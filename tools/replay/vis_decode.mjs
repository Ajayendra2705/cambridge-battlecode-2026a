// Headless replay decoder. The official visualiser engine (WASM) replays the match deterministically, and the
// visualiser's own snapshot decoder (PanelChrome module) turns each state snapshot into objects. Assets are fetched
// from a local `cambc view` server by tools/replay/vis_assets.sh into data/vis/ (gitignored). Minified export names
// change between cambc versions, so decoders are found by behaviour, not by name.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const assets = path.join(root, 'data', 'vis');
const find = (re) => fs.existsSync(assets) && fs.readdirSync(assets).find((f) => re.test(f));

export function replayBytes(file) {
  const head = fs.readFileSync(file).subarray(0, 2).toString('latin1');
  if (head === 'PK') return execFileSync('unzip', ['-p', file, 'replay.repl26a'], { maxBuffer: 1 << 28 });
  return fs.readFileSync(file);
}

export const engineVersion = (bytes) => `v${bytes[8]}_${bytes[9]}_${bytes[10]}`;

const engines = new Map();
export async function openEngine(version) {
  if (engines.has(version)) return engines.get(version);
  const wasmFile = find(new RegExp(`^${version}-.*\\.wasm$`));
  const pcFile = find(/^PanelChrome-.*\.js$/);
  if (!wasmFile || !pcFile) throw new Error(`missing visualiser assets for ${version}: run tools/replay/vis_assets.sh`);
  const { WASI } = await import('node:wasi');
  const PC = await import(pathToFileURL(path.join(assets, pcFile)).href);
  const wasi = new WASI({ version: 'preview1', args: [], env: {}, returnOnExit: true });
  const mod = await WebAssembly.compile(fs.readFileSync(path.join(assets, wasmFile)));
  const inst = await WebAssembly.instantiate(mod, { wasi_snapshot_preview1: wasi.wasiImport });
  wasi.initialize(inst);
  const X = inst.exports;
  const view = () => new DataView(X.memory.buffer);
  const outBuf = X.Engine_Malloc(64), args = X.Engine_Malloc(128);
  const cstr = (p) => { const b = new Uint8Array(X.memory.buffer); let e = p; while (b[e]) e++; return Buffer.from(b.subarray(p, e)).toString(); };
  const check = (rc) => { if (rc !== 0) throw new Error(`engine error ${rc}: ${cstr(X.GetLastErrorMsg())}`); };
  const vals = Object.values(PC);
  const spectator = vals.find((v) => v && typeof v === 'object' && v.team === 2 && v.champion === 0xffffffff);
  const analytics = vals.find((v) => typeof v === 'function' && String(v).includes('Invalid analytics snapshot count'));
  const headers = vals.filter((v) => typeof v === 'function' && v.length === 2);
  if (!spectator || !analytics) throw new Error('visualiser decoder layout changed');
  const E = { X, view, outBuf, args, check, spectator, analytics, headers };
  engines.set(version, E);
  return E;
}

export async function openReplay(file) {
  const bytes = replayBytes(file);
  const E = await openEngine(engineVersion(bytes));
  const { X, view, outBuf, args, check, spectator, analytics } = E;
  const p = X.Engine_Malloc(bytes.length);
  new Uint8Array(X.memory.buffer, p, bytes.length).set(bytes);
  check(X.Game_FromReplayFileBytes(p, bytes.length, outBuf));
  X.Engine_Free(p);
  const handle = view().getBigUint64(outBuf, true);
  const snap = X.Engine_Malloc(X.Game_Visualiser_SnapshotSize());
  check(X.Game_Runner_SetCheckpointsEnabled(handle, 1));
  check(X.Game_Visualiser_Timeline_GetMain(handle, outBuf));
  const main = view().getBigUint64(outBuf, true);
  check(X.Game_Visualiser_Timeline_Info(handle, main, args, args + 8, args + 16));
  const size = view().getUint32(args, true);
  const header = () => {
    for (const h of E.headers) {
      try {
        const r = h(view(), snap);
        if (r && typeof r.round === 'number' && Array.isArray(r.drafts)) { E.headers = [h]; return r; }
      } catch {}
    }
    throw new Error('no header decoder matched the snapshot');
  };
  const read = (team, champion) => {
    const t = args + 48, v = view();
    v.setUint32(t, team >>> 0, true);
    v.setUint32(t + 4, champion >>> 0, true);
    check(X.Game_Visualiser_ReadState(handle, t, snap));
    return analytics(view(), snap, header());
  };
  return {
    size,
    seek(pos) { check(X.Game_Visualiser_Timeline_Seek(handle, main, pos, 0)); },
    state() { return read(spectator.team, spectator.champion); },
    stateAs(team, champion) { return read(team, champion); },
    close() { X.Engine_Free(snap); X.Game_Destroy(handle); },
  };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const R = await openReplay(process.argv[2]);
  const pos = Number(process.argv[3] ?? 200);
  R.seek(pos);
  const s = R.state();
  console.log('timeline size', R.size);
  console.log(JSON.stringify(s, (k, v) => (typeof v === 'bigint' ? Number(v) : v)).slice(0, Number(process.argv[4] ?? 4000)));
  R.close();
}
