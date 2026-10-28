// Turn order per round from replays: the champion indices in the order their end-of-turn steps appear, and each
// champion's state at the round start. One JSON file per replay in OUTDIR:
//   {teams, types, rounds: [[round, order, [[x, y, hp, maxHp, alive, gems] per champion]], ...]} for rounds 1-1000.
// usage: node tools/replay/orderdump.mjs OUTDIR REPLAY...   (skips replays whose output exists; about 5 s each)
import fs from 'node:fs';
import path from 'node:path';
import { openReplay } from './vis_decode.mjs';

const [outdir, ...files] = process.argv.slice(2);
fs.mkdirSync(outdir, { recursive: true });
for (const f of files) {
  const out = path.join(outdir, path.basename(f).replace(/\.(repl26a|zip)$/, '') + '.json');
  if (fs.existsSync(out)) continue;
  try {
    const R = await openReplay(f);
    let round = -1, order = [], snap = null, teams = null, types = null;
    const rounds = [];
    for (let p = 0; p < R.size; p++) {
      R.seek(p);
      const s = R.state();
      if (!teams && s.champions && s.champions.length) { teams = s.champions.map((c) => c.team); types = s.champions.map((c) => c.type); }
      if (s.round !== round) {
        if (order.length && round >= 1 && round <= 1000) rounds.push([round, order, snap]);
        order = []; round = s.round;
        snap = s.champions.map((c) => (c.position ? [c.position.x, c.position.y, Math.round(c.health), Math.round(c.maxHealth), c.alive ? 1 : 0, c.gems ?? 0] : [-1, -1, 0, 0, 0, 0]));
      }
      const st = s.step;
      if (st && st.kind === 3 && st.actor && st.actor.kind === 1) order.push(st.actor.index);
    }
    if (order.length && round >= 1 && round <= 1000) rounds.push([round, order, snap]);
    R.close();
    fs.writeFileSync(out, JSON.stringify({ teams, types, rounds }));
    console.log('ok', path.basename(f));
  } catch (e) {
    console.log('fail', path.basename(f), e.message);
  }
}
