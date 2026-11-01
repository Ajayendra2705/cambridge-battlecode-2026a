# phaseinc.py TEAM DIR... : capture income (gems 'sub', gold) per phase for TEAM vs its opponents; phases by round; also the game end round.
import json, os, sys, collections
TEAM = sys.argv[1]; PH = [0, 150, 300, 450, 600, 10**9]
acc = {s: collections.defaultdict(lambda: [0, 0, 0]) for s in ("us", "them")}
ends = []; n = 0
for d in sys.argv[2:]:
    for g in sorted(os.listdir(d)):
        parts = g.split("__")
        if TEAM not in parts[1:3]: continue
        p = os.path.join(d, g, "trace.json")
        if not os.path.isfile(p): continue
        t = json.load(open(p)); n += 1
        us = 0 if parts[1] == TEAM else 1
        team = {int(k): v["team"] for k, v in t["champions"].items()}
        ends.append(t["final"]["round"])
        for e in t["income"]:
            side = "us" if team.get(e["id"]) == us else "them"
            ph = next(i for i in range(len(PH) - 1) if PH[i] <= e["r"] < PH[i + 1])
            a = acc[side][ph]; a[0] += e.get("sub", 0); a[1] += e.get("gold", 0); a[2] += 1
print(f"{TEAM}: {n} games, end round median {sorted(ends)[len(ends)//2] if ends else 0}")
for side in ("us", "them"):
    print(" ", side, " | ".join(f"r{PH[i]}-{PH[i+1] if PH[i+1] < 10**9 else 'end'}: gems {a[0]/max(1,n):.0f} gold {a[1]/max(1,n):.0f} caps {a[2]/max(1,n):.1f} g/gem {a[1]/max(1,a[0]):.2f}" for i in range(len(PH) - 1) for a in [acc[side][i]]))
