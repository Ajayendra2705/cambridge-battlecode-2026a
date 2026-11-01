// Headless access to CAMBC replays through the visualiser's own engine build.
//
// The cambc CLI unpacks its visualiser under %LOCALAPPDATA%/cambc/assets/<hash>/;
// we load the engine WebAssembly and the snapshot decoders from there, so the
// numbers we read are exactly what the visualiser shows.
//
// Every file in those folders carries a 1980 timestamp, so the newest install
// is the folder with the newest directory time (CAMBC_ASSETS overrides it). A
// visualiser ships one engine per game version (v0_0_1, v0_0_2 after the
// Oct 16 patch): each replay goes to the newest engine that accepts it. The
// decoders' export names change between builds, so they are found by what
// they return (CAMBC_DECODERS="header,state" overrides).
import { expandGlob } from "jsr:@std/fs@1/expand-glob";
import { toFileUrl } from "jsr:@std/path@1/to-file-url";
import { unzipSync } from "npm:fflate@0.8.2";

const OMNISCIENT = { team: 2, champion: 0xffffffff };

async function assetDir(): Promise<string> {
  const override = Deno.env.get("CAMBC_ASSETS");
  if (override) return override;
  const root = `${Deno.env.get("LOCALAPPDATA")}/cambc/assets`;
  let best: { path: string; time: number } | undefined;
  for await (const entry of Deno.readDir(root)) {
    if (!entry.isDirectory) continue;
    const dir = `${root}/${entry.name}/visualiser/assets`;
    try {
      await Deno.stat(dir);
    } catch {
      continue;
    }
    const time = (await Deno.stat(`${root}/${entry.name}`)).mtime?.getTime() ?? 0;
    if (!best || time > best.time) best = { path: dir, time };
  }
  if (best) return best.path;
  throw new Error("cambc visualiser assets not found (run `cambc view` once)");
}

async function assets(dir: string, pattern: string): Promise<string[]> {
  const out: string[] = [];
  for await (const entry of expandGlob(`${dir}/${pattern}`)) out.push(entry.path);
  return out.sort();
}

// deno-lint-ignore no-explicit-any
type Decoders = any;
// deno-lint-ignore no-explicit-any
type Decode = (view: DataView, ptr: number) => any;

// One engine build (one game version).
class Core {
  exports!: Record<string, CallableFunction> & { memory: WebAssembly.Memory };
  outBuf = 0;
  args = 0;
  snapshot = 0;

  static async create(wasmPath: string): Promise<Core> {
    const core = new Core();
    let memory: WebAssembly.Memory;
    const view = () => new DataView(memory.buffer);
    const wasi = {
      environ_get: () => 0,
      environ_sizes_get: (count: number, size: number) => {
        view().setUint32(count, 0, true);
        view().setUint32(size, 0, true);
        return 0;
      },
      fd_close: () => 0,
      fd_fdstat_get: () => 0,
      fd_prestat_get: () => 8, // EBADF: no preopened directories
      fd_prestat_dir_name: () => 8,
      fd_read: () => 0,
      fd_seek: () => 0,
      fd_write: (_fd: number, iovs: number, count: number, written: number) => {
        let total = 0;
        for (let i = 0; i < count; i++) total += view().getUint32(iovs + i * 8 + 4, true);
        view().setUint32(written, total, true);
        return 0;
      },
      random_get: (ptr: number, len: number) => {
        new Uint8Array(memory.buffer, ptr, len).fill(0);
        return 0;
      },
      proc_exit: (code: number) => {
        throw new Error(`engine exited with ${code}`);
      },
    };
    const { instance } = await WebAssembly.instantiate(await Deno.readFile(wasmPath), {
      wasi_snapshot_preview1: wasi,
      deep_wasm: { on_assert_fail_impl: () => 1 },
    });
    core.exports = instance.exports as typeof core.exports;
    memory = core.exports.memory;
    core.exports._initialize();
    core.outBuf = core.exports.Engine_Malloc(32) as number;
    core.args = core.exports.Engine_Malloc(128) as number;
    core.snapshot = core.exports.Engine_Malloc(core.exports.Game_Visualiser_SnapshotSize() as number) as number;
    return core;
  }

  get view(): DataView {
    return new DataView(this.exports.memory.buffer);
  }
}

export class ReplayEngine {
  private cores: Core[] = [];
  private decoders!: Decoders;
  header?: Decode;
  state?: Decode;

  static async create(): Promise<ReplayEngine> {
    const engine = new ReplayEngine();
    const dir = await assetDir();
    const chrome = await assets(dir, "PanelChrome-*.js");
    if (!chrome.length) throw new Error(`no PanelChrome decoder in ${dir}`);
    engine.decoders = await import(toFileUrl(chrome[0]).href);
    // Newest game version first.
    for (const wasm of (await assets(dir, "v[0-9]*_*.wasm")).reverse()) engine.cores.push(await Core.create(wasm));
    const names = Deno.env.get("CAMBC_DECODERS");
    if (names) {
      const [h, s] = names.split(",");
      engine.header = engine.decoders[h];
      engine.state = engine.decoders[s];
    }
    return engine;
  }

  // Load a .repl26a bundle (zip) or a bare replay file; returns the game handle.
  load(bytes: Uint8Array): Game {
    let replay = bytes;
    if (bytes[0] === 0x50 && bytes[1] === 0x4b) {
      const files = unzipSync(bytes);
      const name = Object.keys(files).find((n) => n.endsWith(".repl26a"));
      if (!name) throw new Error("zip has no replay.repl26a");
      replay = files[name];
    }
    let last = 0;
    for (const core of this.cores) {
      const ptr = core.exports.Engine_Malloc(replay.byteLength) as number;
      try {
        new Uint8Array(core.exports.memory.buffer, ptr, replay.byteLength).set(replay);
        last = core.exports.Game_FromReplayFileBytes(ptr, replay.byteLength, core.outBuf) as number;
        if (last === 0) return new Game(this, core, core.view.getBigUint64(core.outBuf, true));
      } finally {
        core.exports.Engine_Free(ptr);
      }
    }
    throw new Error(`engine error ${last} (no installed engine version accepts this replay)`);
  }

  // Find the header and full-state decoders by their output, on a snapshot
  // just read: the header is the smallest output with the timeline position,
  // the state the richest with champions, camps and groups (v0_0_2 builds
  // also export a smaller analytics decoder, and their state decoder takes a
  // third argument and returns the header fields too).
  findDecoders(view: DataView, ptr: number) {
    if (this.header && this.state) return;
    let header: { fn: Decode; keys: number } | undefined, state: { fn: Decode; keys: number } | undefined;
    for (const fn of Object.values(this.decoders)) {
      if (typeof fn !== "function" || (fn.length !== 2 && fn.length !== 3)) continue;
      let out;
      try {
        out = (fn as Decode)(view, ptr);
      } catch {
        continue;
      }
      if (!out || typeof out !== "object") continue;
      const keys = Object.keys(out).length;
      if ("inputPosition" in out && out.step && "substep" in out.step && (!header || keys < header.keys)) header = { fn: fn as Decode, keys };
      if (Array.isArray(out.champions) && Array.isArray(out.camps) && Array.isArray(out.groups) && (!state || keys > state.keys)) state = { fn: fn as Decode, keys };
    }
    this.header ??= header?.fn;
    this.state ??= state?.fn;
    if (!this.header || !this.state) throw new Error("snapshot decoders not found (set CAMBC_DECODERS=header,state)");
  }
}

export class Game {
  readonly timeline: bigint;
  readonly length: number;

  constructor(private engine: ReplayEngine, private core: Core, readonly handle: bigint) {
    const c = core;
    if ((c.exports.Game_Visualiser_Timeline_GetMain(handle, c.outBuf) as number) !== 0) throw new Error("no timeline");
    this.timeline = c.view.getBigUint64(c.outBuf, true);
    c.exports.Game_Visualiser_Timeline_Info(handle, this.timeline, c.args, c.args + 8, c.args + 16);
    this.length = c.view.getUint32(c.args, true);
  }

  private perspective(): number {
    const p = this.core.args + 48;
    this.core.view.setUint32(p, OMNISCIENT.team, true);
    this.core.view.setUint32(p + 4, OMNISCIENT.champion, true);
    return p;
  }

  private read() {
    const c = this.core;
    if ((c.exports.Game_Visualiser_ReadState(this.handle, this.perspective(), c.snapshot) as number) !== 0) {
      throw new Error("read state failed");
    }
    this.engine.findDecoders(c.view, c.snapshot);
  }

  // Full state after timeline step `position` (0 .. length-1).
  // deno-lint-ignore no-explicit-any
  stateAt(position: number): any {
    const c = this.core;
    if ((c.exports.Game_Visualiser_Timeline_Seek(this.handle, this.timeline, position, 0) as number) !== 0) {
      throw new Error(`seek ${position} failed`);
    }
    this.read();
    const header = this.engine.header!(c.view, c.snapshot);
    return { header, ...this.engine.state!(c.view, c.snapshot) };
  }

  // Walk the whole game once, front to back (seeking is linear in the
  // position, so per-step seeks would be quadratic). `wantFull(header)` says
  // whether to decode the full state for that step; `visit` gets the header
  // and, when requested, the full state.
  walk(
    // deno-lint-ignore no-explicit-any
    visit: (header: any, state?: any) => void,
    // deno-lint-ignore no-explicit-any
    wantFull: (header: any) => boolean = () => false,
  ) {
    const c = this.core;
    if ((c.exports.Game_Visualiser_Timeline_Seek(this.handle, this.timeline, 0, 0) as number) !== 0) throw new Error("seek failed");
    let previous = -1, previousSub = -1, previousRound = -1;
    for (;;) {
      this.read();
      const header = this.engine.header!(c.view, c.snapshot);
      // The recorded inputs run out a little before the game resolves; stop
      // once stepping makes no further progress.
      if (header.inputPosition === previous && header.step.substep === previousSub && header.round === previousRound) break;
      previous = header.inputPosition;
      previousSub = header.step.substep;
      previousRound = header.round;
      visit(header, wantFull(header) ? { header, ...this.engine.state!(c.view, c.snapshot) } : undefined);
      if (header.outcome) break;
      if ((c.exports.Game_Visualiser_Timeline_ReplayNext(this.handle, 1) as number) !== 0) break;
    }
  }

  destroy() {
    this.core.exports.Game_Destroy(this.handle);
  }
}
