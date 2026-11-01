// probe.ts DIR R0 R1 : print phase-10 (champion action) steps between rounds R0..R1 with champion health changes per step
// (field discovery for burst/extract.ts).
import { ReplayEngine } from "../../replay/replay_engine.ts";
const eng: any = await ReplayEngine.create();
const g = eng.load(Deno.readFileSync(Deno.args[0] + "/replay.repl26a"));
const R0 = +Deno.args[1], R1 = +Deno.args[2];
let prev: any = null;
g.walk((h: any, s: any) => {
  if (!s) return;
  const st = h.step;
  const d: string[] = [];
  if (prev) for (const c of s.champions) { const o = prev.champions.find((x: any) => x.entity.index === c.entity.index); if (o && o.health !== c.health) d.push(`${c.entity.index}:${(c.health - o.health).toFixed(1)}`); if (o && JSON.stringify(o.cooldowns)!==JSON.stringify(c.cooldowns) && st.phase===10) d.push(`cd${c.entity.index}:${c.cooldowns}`); if (o && JSON.stringify(o.buffs)!==JSON.stringify(c.buffs)) d.push(`buf${c.entity.index}:${JSON.stringify(c.buffs)}`);}
  if (st.phase !== 9 || d.length) console.log(`r${h.round} ph${st.phase} k${st.kind} a${st.actor.kind}.${st.actor.index} ${st.from.x},${st.from.y}->${st.to.x},${st.to.y} slot${st.abilitySlot} sub${st.substep} ${d.join(" ")}`);
  prev = s;
}, (h: any) => h.round >= R0 && h.round <= R1);
g.destroy();
