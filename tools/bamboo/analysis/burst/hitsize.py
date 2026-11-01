# hitsize.py "LABEL=FOCUS[,FOCUS2]|GLOB" ... : damage per hit on enemy champions by champion type, slot (A = basic attack, s0 / s1 casts) and
# round band (r<300, 300-600, 600+), as mean damage and as a share of the target's max health; also the attacker's mean strength / focus.
import sys, glob, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import Game
B = [(0, 300), (300, 600), (600, 9999)]
for arg in sys.argv[1:]:
    lab, rest = arg.split("=", 1); names, pat = rest.split("|")
    T = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0])
    for fp in sorted(glob.glob(pat)):
        for nm in names.split(","):
            g = Game(fp, nm)
            if g.focus is None: continue
            for (r, a, v, amt, k, s) in g.pvp:
                if g.team[a] != g.focus: continue
                b = next(i for i, (lo, hi) in enumerate(B) if lo <= r < hi)
                key = (g.cname[a], "A" if k == 5 else f"s{s}", b)
                vs = g.st(r, v) or {}; me = g.st(r, a) or {}
                t = T[key]; t[0] += 1; t[1] += amt; t[2] += amt / max(1, vs.get("mx", 1)); t[3] += me.get("st", 0); t[4] += me.get("fo", 0)
    print(f"== {lab}")
    for cn in sorted({k[0] for k in T}):
        parts = []
        for sl in ("A", "s0", "s1"):
            cells = []
            for b in range(3):
                t = T.get((cn, sl, b))
                cells.append(f"{t[1] / t[0]:4.0f}/{100 * t[2] / t[0]:2.0f}%" if t and t[0] >= 5 else "    -    ")
            parts.append(f"{sl}: " + " ".join(cells))
        st = [T.get((cn, "A", b)) for b in range(3)]
        print(f"  {cn:8s} " + " | ".join(parts) + "   str/foc " + " ".join(f"{t[3] / t[0]:.0f}/{t[4] / t[0]:.0f}" if t and t[0] else "-" for t in st))
