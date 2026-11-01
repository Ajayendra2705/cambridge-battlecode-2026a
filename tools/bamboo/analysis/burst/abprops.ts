// abprops.ts DIR... : each champion type's abilityProps (type, cooldown, range, radius, modifier, duration) at round 50 - the burst model's
// spell table.
import { ReplayEngine } from "../../replay/replay_engine.ts";
const NAMES = ["Ryth", "Vesper", "Vendetta", "Cassi", "Issac", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi", "HoR"];
const eng: any = await ReplayEngine.create();
const seen = new Set<string>();
for (const dir of Deno.args) {
  const g = eng.load(Deno.readFileSync(dir + "/replay.repl26a"));
  g.walk((h: any, s: any) => {
    if (!s) return;
    for (const c of s.champions) { if (seen.has(NAMES[c.type])) continue; seen.add(NAMES[c.type]);
      console.log(NAMES[c.type], "hp", c.maxHealth, "str", c.strength.effective, "foc", c.focus.effective, "rng", c.attackRange, JSON.stringify(c.abilityProps)); }
  }, (h: any) => h.round === 50);
  g.destroy();
}
