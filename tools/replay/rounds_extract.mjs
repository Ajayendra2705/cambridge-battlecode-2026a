// Per-round dataset from replays: champion state at the start of every round, what each champion could see
// (fog of war, per champion), and what each champion did during the round (moves, attacks and casts with the
// entity they hit). One gzipped JSON line per round in <outdir>/<replay name>.jsonl.gz.
// usage: node tools/replay/rounds_extract.mjs <outdir> <replay>...
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { openReplay } from './vis_decode.mjs';

// Step kinds, inferred from state changes (the state at a timeline position is after that step): 4 move one tile,
// 5 basic attack, 6 ability cast (dashes move 2), 12 tribute start, 14 ward placement, 13 shop, 3 end of turn.
const KIND = { 4: 'move', 5: 'attack', 6: 'cast', 12: 'tribute', 14: 'ward' };
const dist = (a, b) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));

function entityAt(s, pos) {
  for (const c of s.champions) if (c.alive && c.position && c.position.x === pos.x && c.position.y === pos.y) return ['c', c.entity.index];
  for (const c of s.camps) if (c.position && c.health > 0 && c.position.x === pos.x && c.position.y === pos.y) return ['m', c.entity.index];
  return null;
}

function snapshot(R, s) {
  const champs = s.champions.map((c) => {
    const row = { t: c.team, ty: c.type, a: c.alive ? 1 : 0, g: c.gems ?? 0, au: c.gold ?? 0, k: c.kills ?? 0 };
    if (c.position) Object.assign(row, { x: c.position.x, y: c.position.y, hp: Math.round(c.health), mhp: Math.round(c.maxHealth) });
    const items = [];
    (c.items || []).forEach((n, i) => { if (n) items.push([i, n]); });
    if (items.length) row.it = items;
    return row;
  });
  const vis = s.champions.map((me) => {
    if (!me.alive || !me.position) return [];
    const v = R.stateAs(me.team, me.entity.index);
    const seen = [];
    v.champions.forEach((c, i) => { if (c.team !== me.team && c.position) seen.push(i); });
    return seen;
  });
  // mh: every camp's health this round (index = camp entity index, types in the meta line).
  return { r: s.round, sg: s.submittedGems.map(Number), c: champs, vis, mh: s.camps.map((c) => Math.round(c.health)) };
}

export function extract(file, out) {
  return openReplay(file).then((R) => {
    const lines = [];
    let cur = null, acts = null, prev = null;
    for (let p = 0; p < R.size; p++) {
      R.seek(p);
      const s = R.state();
      if (s.phase !== 10 && s.round === 0) continue;
      if (!cur || s.round !== cur.r) {
        if (cur) lines.push(JSON.stringify({ ...cur, act: acts }));
        cur = snapshot(R, s);
        acts = s.champions.map(() => []);
      }
      const st = s.step, kind = KIND[st.kind];
      if (kind && st.actor.kind === 1) {
        const i = st.actor.index;
        if (kind === 'move') acts[i].push([kind, st.from.x, st.from.y, st.to.x, st.to.y]);
        else if (kind === 'tribute' || kind === 'ward') acts[i].push([kind, st.to.x, st.to.y]);
        else {
          const hit = prev ? entityAt(prev, st.to) : null;
          acts[i].push(kind === 'cast' ? [kind, st.abilitySlot ?? -1, st.to.x, st.to.y, ...(hit || [])] : [kind, st.to.x, st.to.y, ...(hit || [])]);
        }
      }
      prev = s;
    }
    if (cur) lines.push(JSON.stringify({ ...cur, act: acts }));
    const meta = { file: path.basename(file), engine: R.version, drafts: prev?.drafts, outcome: prev?.outcome, submittedGems: prev?.submittedGems.map(Number), rounds: prev?.round,
      camps: Object.fromEntries((prev?.camps ?? []).map((c) => [c.entity.index, c.type])) };
    fs.writeFileSync(out, zlib.gzipSync(JSON.stringify(meta) + '\n' + lines.join('\n') + '\n'));
    R.close();
    return meta;
  });
}

if (process.argv[1] && import.meta.url.endsWith(path.basename(process.argv[1]))) {
  const [outdir, ...files] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  for (const f of files) {
    const out = path.join(outdir, path.basename(f).replace(/\.(repl26a|zip)$/, '') + '.jsonl.gz');
    if (fs.existsSync(out)) continue;
    const t = Date.now();
    try {
      const m = await extract(f, out);
      console.log(`ok ${path.basename(f)} rounds=${m.rounds} ${((Date.now() - t) / 1000).toFixed(1)}s`);
    } catch (e) {
      console.log(`fail ${path.basename(f)}: ${e.message}`);
    }
  }
}
