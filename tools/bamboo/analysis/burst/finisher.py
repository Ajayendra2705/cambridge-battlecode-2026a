# finisher.py "LABEL=FOCUS[,FOCUS2]|GLOB" ... : per champion type, rounds with an enemy under LOW (0.3) health within 4 while the champion's
# damaging spell is ready (cooldown 0, not stunned): share that cast the spell at it, cast it elsewhere, auto-attacked it, or did neither;
# split by distance (<=2 / 3-4). The "finish with the ready nuke" check. R1 env limits rounds. The enemy's tile is taken at the moment the
# champion acts: teams alternate (A = team 0 first in odd rounds), so when the enemy's team acted first this round its post-move tile counts.
import sys, glob, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import Game, cheb, SPELL_MOD
LOW = float(os.environ.get("LOW", 0.3)); R1 = int(os.environ.get("R1", 9999))
for arg in sys.argv[1:]:
    lab, rest = arg.split("=", 1); names, pat = rest.split("|")
    T = collections.defaultdict(collections.Counter)
    for fp in sorted(glob.glob(pat)):
        for nm in names.split(","):
            g = Game(fp, nm)
            if g.focus is None: continue
            F = g.focus
            for r in g.rounds:
                if r >= R1: break
                lows = [e for e in g.alive(r, 1 - F) if e["hp"] < LOW * e["mx"]]
                if not lows: continue
                for c in g.alive(r, F):
                    if c["stun"]: continue
                    cn = g.cname[c["id"]]
                    slots = [s for s in (0, 1) if (cn, s) in SPELL_MOD and len(c["cd"]) > s and c["cd"][s] == 0]
                    if not slots: continue
                    def pos_now(e):
                        if (r % 2 == 1) == (e["t"] == 0):  # the enemy's team acted first this round
                            mv = [a for a in g.acts.get(r, []) if a["id"] == e["id"] and a.get("a")]
                            if mv: return mv[-1]["a"]
                        return e["p"]
                    near = [dict(e, p=pos_now(e)) for e in lows]
                    near = [e for e in near if cheb(e["p"], c["p"]) <= 4]
                    if not near: continue
                    e = min(near, key=lambda x: cheb(x["p"], c["p"]))
                    band = "d<=2" if cheb(e["p"], c["p"]) <= 2 else "d3-4"
                    acts = [a for a in g.acts.get(r, []) if a["id"] == c["id"]]
                    cast_it = any(a["k"] == 6 and a.get("s") in slots and any((a.get("d") or {}).get(str(x["id"]), 0) > 0 for x in near) for a in acts)
                    cast_else = any(a["k"] == 6 and a.get("s") in slots for a in acts) and not cast_it
                    auto_it = any(a["k"] == 5 and any((a.get("d") or {}).get(str(x["id"]), 0) > 0 for x in near) for a in acts)
                    what = "cast at it" if cast_it else "cast elsewhere" if cast_else else "auto it" if auto_it else "neither"
                    for k in (band, "all"):
                        T[(cn, k)]["n"] += 1; T[(cn, k)][what] += 1
    print(f"== {lab}")
    for (cn, k), t in sorted(T.items()):
        if t["n"] < 8: continue
        print(f"   {cn:8s} {k:5s} n{t['n']:4d}: " + ", ".join(f"{w} {100 * t[w] / t['n']:.0f}%" for w in ("cast at it", "cast elsewhere", "auto it", "neither")))
