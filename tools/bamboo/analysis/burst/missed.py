# missed.py "LABEL=FOCUS[,FOCUS2]|GLOB" ... : finishing chances on low enemies (burst/extract.ts output). A chance = an enemy champion
# under LOW (0.3) of its max health at a round start, alive, with a FOCUS champion (not stunned) that could reach it this turn: basic attack
# reach = attack range (ranged) or range + 1 (melee: step then hit), + 2 more with a dash ready (melee dashers), 4 with a damaging spell
# ready. Taken = a FOCUS champion damaged it that round. Per team: chance rounds, share taken, kills within 3 rounds, and per champion
# type: rounds it had the low enemy in its reach and what it did (hit it / hit another champion / hit a camp / moved only / nothing).
# Vision is not modelled (walls, bushes): a "missed" round can be a target out of sight. R1 env limits rounds.
import sys, glob, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import Game, cheb, SPELL_MOD, DASH

LOW = float(os.environ.get("LOW", 0.3)); R1 = int(os.environ.get("R1", 9999))
for arg in sys.argv[1:]:
    lab, rest = arg.split("=", 1); names, pat = rest.split("|")
    C = collections.Counter(); T = collections.defaultdict(collections.Counter); ng = 0; ex = []
    for fp in sorted(glob.glob(pat)):
        for nm in names.split(","):
            g = Game(fp, nm)
            if g.focus is None: continue
            ng += 1; F = g.focus
            die = collections.defaultdict(list)
            for d in g.deaths: die[d["v"]].append(d["r"])
            for r in g.rounds:
                if r >= R1: break
                for e in g.alive(r, 1 - F):
                    if e["hp"] >= LOW * e["mx"]: continue
                    able = []
                    for c in g.alive(r, F):
                        if c["stun"]: continue
                        cn = g.cname[c["id"]]; d = cheb(c["p"], e["p"])
                        melee = c["rng"] <= 1
                        reach = c["rng"] + (1 if melee else 0)
                        if melee and any((cn, s) in DASH and len(c["cd"]) > s and c["cd"][s] == 0 for s in (0, 1)): reach += 2
                        if any((cn, s) in SPELL_MOD and len(c["cd"]) > s and c["cd"][s] == 0 for s in (0, 1)): reach = max(reach, 4)
                        if d <= reach: able.append(c)
                    if not able: continue
                    taken = any(g.team[a] == F for a in g.dmg_by[(e["id"], r)])
                    C["chance"] += 1; C["taken"] += taken
                    C["kill3"] += any(r <= x <= r + 3 for x in die[e["id"]])
                    if not taken and len(ex) < 12 and r < 900: ex.append((g.gid, g.map, r, g.cname[e["id"]], e["id"], round(e["hp"]), [g.cname[c["id"]] for c in able]))
                    for c in able:
                        cn = g.cname[c["id"]]
                        acts = [a for a in g.acts.get(r, []) if a["id"] == c["id"]]
                        hit_e = g.dmg_by[(e["id"], r)].get(c["id"], 0) > 0
                        hit_o = any(x > 0 and g.team[int(v)] != F for a in acts for v, x in (a.get("d") or {}).items())
                        camp = any(a.get("tc") == "m" for a in acts)
                        moved = any(a["k"] == 4 for a in acts)
                        what = "hit it" if hit_e else "hit other champ" if hit_o else "camp" if camp else "moved only" if moved else "nothing"
                        T[cn]["n"] += 1; T[cn][what] += 1
    print(f"== {lab}: team-games {ng}; chance rounds on enemies under {LOW:.0%}: {C['chance']} ({C['chance'] / max(1, ng):.1f}/game), "
          f"taken {100 * C['taken'] / max(1, C['chance']):.0f}%, target dead within 3 rounds {100 * C['kill3'] / max(1, C['chance']):.0f}%")
    for cn, t in sorted(T.items(), key=lambda x: -x[1]["n"]):
        if t["n"] < 15: continue
        print(f"   {cn:8s} {t['n']:4d}: " + ", ".join(f"{k} {100 * t[k] / t['n']:.0f}%" for k in ("hit it", "hit other champ", "camp", "moved only", "nothing")))
    for x in ex[:6]: print("   missed e.g.", x)
