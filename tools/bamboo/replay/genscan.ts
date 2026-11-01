// ft/genscan.ts @LIST : stress-map health check from replay bundles named MAP__OPP__SIDE.repl26a (SIDE A or B = us).
// Per game: final round, banked gems us/them, our gold, deaths, walking loops (16-round window, alive, moving 10+
// rounds on at most 4 tiles, no enemy within 6), stuck episodes (30+ rounds on one tile away from spawn, no enemy within
// 6, not channelling), never-left-spawn champions after round 60, and turns at the fuel limit. Then the worst maps.
import { ReplayEngine } from "../replay/replay_engine.ts";
import { unzipSync } from "npm:fflate@0.8.2";
const FILES = Deno.readTextFileSync(Deno.args[0].slice(1)).split("\n").map((x) => x.trim()).filter(Boolean);
const eng: any = await ReplayEngine.create();
const cheb = (a: any, b: any) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));
const names: Record<number, string> = { 0: "ryth", 1: "vesp", 2: "vend", 3: "cassi", 4: "issac", 5: "stel", 6: "prism", 7: "marc", 8: "wil", 9: "ren", 10: "varg", 11: "tavi", 12: "hor" };
type Row = { map: string; opp: string; side: string; round: number; us: number; them: number; gold: number; deaths: number; loops: number; loopRounds: number; stuck: number; stuckRounds: number; guard: number; guardRounds: number; homebound: number; fuel: number; notes: string[] };
const rows: Row[] = [];
for (const f of FILES) {
  const base = f.split(/[\\/]/).pop()!.replace(".repl26a", "");
  const [map, opp, side] = base.split("__");
  const us = side === "B" ? 1 : 0;
  let z: Record<string, Uint8Array>;
  try { z = unzipSync(Deno.readFileSync(f)); } catch { console.log(base, "unreadable"); continue; }
  const g = eng.load(z["replay.repl26a"]);
  const row: Row = { map, opp, side, round: 0, us: 0, them: 0, gold: 0, deaths: 0, loops: 0, loopRounds: 0, stuck: 0, stuckRounds: 0, guard: 0, guardRounds: 0, homebound: 0, fuel: 0, notes: [] };
  const start = new Map<number, any>();
  const win = new Map<number, { p: string; moved: boolean; calm: boolean }[]>();
  const inLoop = new Map<number, boolean>();
  const still = new Map<number, { p: string; n: number }>();
  const left = new Map<number, boolean>();
  const prevAlive = new Map<number, boolean>();
  const typeOf = new Map<number, number>();
  let last: any = null, lastRound = -1;
  let campHp = new Map<string, number>(); // camp tile -> health last round (busy test)
  const groupTiles = new Map<number, string[]>();
  const campPos = new Map<string, string>();
  g.walk((h: any, s: any) => {
    if (!s) return;
    last = s;
    if (h.round === lastRound) return;
    lastRound = h.round;
    // camps that lost health this round, groups with a reward up, and groups whose members are all dead (respawning)
    const hurt: any[] = [];
    const nowHp = new Map<string, number>();
    const liveGroup = new Set<number>();
    for (const m of s.camps ?? []) {
      const id = String(m.entity?.index ?? `${m.group}:${m.type}`);
      if (m.position) campPos.set(id, `${m.position.x},${m.position.y}`);
      const k = campPos.get(id);
      const hp = Number(m.health ?? 0);
      nowHp.set(id, hp);
      if (k) {
        if (!groupTiles.has(m.group)) groupTiles.set(m.group, []);
        if (!groupTiles.get(m.group)!.includes(k)) groupTiles.get(m.group)!.push(k);
      }
      if (hp > 0) liveGroup.add(m.group);
      const was = campHp.get(id);
      if (was !== undefined && hp < was && k) { const [x, y] = k.split(",").map(Number); hurt.push({ x, y }); }
    }
    campHp = nowHp;
    const rewardTiles = new Set<string>();
    const deadTiles: any[] = [];
    (s.groups ?? []).forEach((gr: any, gi: number) => {
      if (gr?.rewardAvailable) for (const k of groupTiles.get(gi) ?? []) rewardTiles.add(k);
    });
    for (const [gi, ks] of groupTiles) if (!liveGroup.has(gi)) for (const k of ks) { const [x, y] = k.split(",").map(Number); deadTiles.push({ x, y }); }
    for (const c of s.champions) {
      if (c.team !== us) continue;
      const id = c.entity.index;
      typeOf.set(id, c.type);
      if (prevAlive.get(id) && !c.alive) row.deaths++;
      prevAlive.set(id, c.alive);
      if (!c.alive || !c.position) { win.set(id, []); still.delete(id); continue; }
      if (!start.has(id)) start.set(id, c.position);
      const p = `${c.position.x},${c.position.y}`;
      const busy = hurt.some((q: any) => cheb(q, c.position) <= 4) || rewardTiles.has(p) || Number(c.channelType ?? 0) !== 0;
      const calm = !busy && !s.champions.some((e: any) => e.team !== us && e.alive && e.position && cheb(e.position, c.position) <= 6);
      const w = win.get(id) ?? [];
      const moved = w.length > 0 && w[w.length - 1].p !== p;
      w.push({ p, moved, calm });
      if (w.length > 16) w.shift();
      win.set(id, w);
      const looping = w.length === 16 && w.every((x) => x.calm) && w.filter((x) => x.moved).length >= 10 && new Set(w.map((x) => x.p)).size <= 4;
      if (looping) { row.loopRounds++; if (!inLoop.get(id)) { row.loops++; if (row.notes.length < 6) row.notes.push(`loop ${names[c.type]} r${h.round} at ${p}`); } }
      inLoop.set(id, looping);
      const st = still.get(id);
      const home = cheb(c.position, start.get(id)) <= 3;
      if (!home) left.set(id, true);
      const channel = Number(c.channelType ?? 0) !== 0;
      if (st && st.p === p && calm && !home && !channel) {
        st.n++;
        const guard = deadTiles.some((q: any) => cheb(q, c.position) <= 3);
        if (st.n === 30) { if (guard) row.guard++; else { row.stuck++; if (row.notes.length < 6) row.notes.push(`stuck ${names[c.type]} r${h.round - 30} at ${p}`); } }
        if (st.n >= 30) { if (guard) row.guardRounds++; else row.stuckRounds++; }
      } else still.set(id, { p, n: 0 });
      if (h.round === 60 && !left.get(id)) { row.homebound++; row.notes.push(`home r60 ${names[c.type]}`); }
    }
  }, () => true);
  g.destroy();
  row.round = lastRound;
  const sub = last?.submittedGems;
  const subArr = Array.isArray(sub) ? sub.map(Number) : sub ? [Number(sub[0] ?? sub.teamA ?? 0), Number(sub[1] ?? sub.teamB ?? 0)] : [0, 0];
  row.us = subArr[us]; row.them = subArr[1 - us];
  row.gold = last ? last.champions.filter((c: any) => c.team === us).reduce((a: number, c: any) => a + Number(c.earnedGold ?? 0), 0) : 0;
  const fz = z[us === 0 ? "team-a.fuel" : "team-b.fuel"];
  if (fz) {
    const v = new DataView(fz.buffer, fz.byteOffset, fz.byteLength);
    for (let o = 12 + 64; o + 8 <= fz.length; o += 8) if (Number(v.getBigUint64(o, true)) / 256 >= 99000) row.fuel++;
  }
  rows.push(row);
}
console.log("map      opp    side round   us them  gold dth loops(rnds) stuck(rnds) home fuel99k notes");
for (const r of rows) console.log(`${r.map.padEnd(8)} ${r.opp.padEnd(6)} ${r.side}  ${String(r.round).padStart(5)} ${String(r.us).padStart(4)} ${String(r.them).padStart(4)} ${String(r.gold).padStart(5)} ${String(r.deaths).padStart(3)} ${String(r.loops).padStart(3)}(${String(r.loopRounds).padStart(4)}) ${String(r.stuck).padStart(3)}(${String(r.stuckRounds).padStart(4)}) ${String(r.homebound).padStart(4)} ${String(r.fuel).padStart(6)}  ${r.notes.join("; ")}`);
const sum = (f: (r: Row) => number) => rows.reduce((a, r) => a + f(r), 0);
console.log(`\ngames ${rows.length}: wins ${rows.filter((r) => r.us > r.them).length}, gems ${sum((r) => r.us)} vs ${sum((r) => r.them)}, loops ${sum((r) => r.loops)} (${sum((r) => r.loopRounds)} rounds), stuck ${sum((r) => r.stuck)} (${sum((r) => r.stuckRounds)} rounds), guarding still 30+ ${sum((r) => r.guard)} (${sum((r) => r.guardRounds)} rounds), never left spawn by r60 ${sum((r) => r.homebound)}, fuel-limit turns ${sum((r) => r.fuel)}`);
const byMap = new Map<string, Row[]>();
for (const r of rows) { if (!byMap.has(r.map)) byMap.set(r.map, []); byMap.get(r.map)!.push(r); }
const worst = [...byMap].map(([m, rs]) => ({ m, share: rs.reduce((a, r) => a + r.us, 0) / Math.max(1, rs.reduce((a, r) => a + r.us + r.them, 0)), bad: rs.reduce((a, r) => a + r.loopRounds + r.stuckRounds, 0) })).sort((a, b) => a.share - b.share);
console.log("worst gem share:", worst.slice(0, 10).map((w) => `${w.m} ${(100 * w.share).toFixed(0)}% (loop/stuck rounds ${w.bad})`).join(", "));
console.log("most loop/stuck:", [...worst].sort((a, b) => b.bad - a.bad).slice(0, 10).map((w) => `${w.m} ${w.bad}`).join(", "));
