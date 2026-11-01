// extract.ts OUTDIR DIR... : per-step champion damage attribution for the burst study (Nov 1, "copy how Fish bursts a champion").
// Writes OUTDIR/<basename of DIR>.json (nothing is written into the replay directories):
//   champions {id: {team, name}}
//   rounds [{r, ch: [{id, t, p, hp, mx, al, cd:[s0,s1], ab:[type0,type1], rng, stun, sh, chn, gm, gd, st, fo}]}]  (state at the round's first step)
//   acts   [{r, id, k, s (slot), f (actor tile before), a (actor tile after), to, tc (target: 'c' champion / 'm' camp member / null),
//            d {victimId: health lost to this step}}]  - phase-10 steps of champion actors, kinds 4 move, 5 attack, 6 cast, 14, 23 and any
//            step that changed a champion's health (negative d = healed)
//   mdmg   [{r, v, amt}] champion health lost in monster steps (phase 9, camp actor), per round and victim
//   deaths [{r, v, by (actor id of the killing step or -1), bk (actor kind: 1 champion, 2 camp, 0 other), k (step kind)}]
// Ability types (abilityProps.type): 1 attack reset / enhanced auto, 2 damage, 3 area damage, 4 damage+stun, 5 heal, 6 dash, 7 buff.
import { ReplayEngine } from "../../replay/replay_engine.ts";
const NAMES = ["Ryth", "Vesper", "Vendetta", "Cassi", "Issac", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi", "HoR"];
const eng: any = await ReplayEngine.create();
const OUT = Deno.args[0];
Deno.mkdirSync(OUT, { recursive: true });
for (const dir of Deno.args.slice(1)) {
  const t0 = Date.now();
  let g: any;
  try { g = eng.load(Deno.readFileSync(dir + "/replay.repl26a")); } catch (e) { console.error(dir, "load failed", e); continue; }
  const out: any = { champions: {}, rounds: [], acts: [], mdmg: [], deaths: [] };
  let prev: any = null, round = -1, lastKey = "";
  const mAcc = new Map<string, number>();
  try {
    g.walk((h: any, s: any) => {
      const key = `${h.inputPosition}:${h.round}:${h.step.substep}`; if (key === lastKey) return; lastKey = key;
      if (!s?.champions?.length) { prev = s; return; }
      for (const c of s.champions) if (!out.champions[c.entity.index]) out.champions[c.entity.index] = { team: c.team, name: NAMES[c.type] };
      if (h.round !== round) {
        round = h.round;
        out.rounds.push({ r: round, ch: s.champions.map((c: any) => {
          const stun = (c.buffs ?? []).find((b: any) => b.type === 1), sh = (c.buffs ?? []).find((b: any) => b.type === 0);
          return { id: c.entity.index, t: c.team, p: c.position, hp: Math.round(c.health * 10) / 10, mx: c.maxHealth, al: c.alive,
            cd: (c.cooldowns ?? []).map(Number), ab: (c.abilityProps ?? []).map((p: any) => p?.type ?? -1), rng: c.attackRange,
            stun: stun ? Number(stun.timer) + 1 : 0, sh: sh ? Math.round(Number(sh.magnitude)) : 0, chn: c.channelType, gm: Number(c.gems),
            gd: Number(c.gold), st: Math.round(c.strength.effective), fo: Math.round(c.focus.effective) };
        }) });
      }
      const st = h.step;
      if (prev?.champions?.length) {
        const d: Record<number, number> = {};
        let any = false;
        for (const c of s.champions) {
          const o = prev.champions.find((x: any) => x.entity.index === c.entity.index);
          if (!o) continue;
          const loss = (o.alive ? o.health : 0) - (c.alive ? c.health : 0);
          if (Math.abs(loss) > 0.01 && o.alive) { d[c.entity.index] = Math.round(loss * 10) / 10; any = true; }
          if (o.alive && !c.alive) out.deaths.push({ r: h.round, v: c.entity.index, by: st.actor?.kind === 1 || st.actor?.kind === 2 ? st.actor.index : -1, bk: st.actor?.kind ?? 0, k: st.kind, ph: st.phase });
        }
        if (st.phase === 10 && st.actor?.kind === 1) {
          if ([4, 5, 6, 14, 23].includes(st.kind) || any) {
            const me = s.champions.find((x: any) => x.entity.index === st.actor.index), mo = prev.champions.find((x: any) => x.entity.index === st.actor.index);
            let tc: string | null = null;
            if (st.kind === 5 || st.kind === 6) {
              if (prev.champions.some((x: any) => x.alive && x.position && x.position.x === st.to.x && x.position.y === st.to.y && x.entity.index !== st.actor.index)) tc = "c";
              else if ((prev.camps ?? []).some((x: any) => x.health > 0 && x.position && x.position.x === st.to.x && x.position.y === st.to.y)) tc = "m";
            }
            out.acts.push({ r: h.round, id: st.actor.index, k: st.kind, s: st.abilitySlot, f: mo?.position, a: me?.position, to: st.to, tc, d: any ? d : undefined });
          }
        } else if (st.phase === 9 && st.actor?.kind === 2 && any) {
          for (const [v, amt] of Object.entries(d)) if (amt > 0) { const k = `${h.round}:${v}`; mAcc.set(k, (mAcc.get(k) ?? 0) + amt); }
        }
      }
      prev = s;
    }, () => true);
  } catch (e) { console.error(dir, "walk stopped", String(e).slice(0, 200)); }
  g.destroy();
  for (const [k, amt] of mAcc) { const [r, v] = k.split(":").map(Number); out.mdmg.push({ r, v, amt: Math.round(amt * 10) / 10 }); }
  Deno.writeTextFileSync(`${OUT}/${dir.replace(/[\\/]+$/, "").split(/[\\/]/).pop()}.json`, JSON.stringify(out));
  console.log(JSON.stringify({ dir: dir.split(/[\\/]/).pop(), rounds: out.rounds.length, acts: out.acts.length, deaths: out.deaths.length, sec: (Date.now() - t0) / 1000 }));
}
