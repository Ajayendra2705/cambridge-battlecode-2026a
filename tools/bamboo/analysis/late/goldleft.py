# goldleft.py TEAM DIR... : per game, the team's banked gems, gold earned and gold still held at the end, and gold held at r450/r600.
import json, os, sys
TEAM = sys.argv[1]; rows = []
for d in sys.argv[2:]:
    for g in sorted(os.listdir(d)):
        parts = g.split("__")
        if TEAM not in parts[1:3]: continue
        p = os.path.join(d, g, "trace.json")
        if not os.path.isfile(p): continue
        t = json.load(open(p)); us = 0 if parts[1] == TEAM else 1
        f = t["final"]; held = sum(c["gold"] for c in f["ch"] if c["team"] == us); earned = sum(c["earned"] for c in f["ch"] if c["team"] == us)
        def at(r):
            for x in t["rounds"]:
                if x["r"] >= r: return sum(c["gold"] for c in x["ch"] if c["team"] == us)
            return None
        rows.append((parts[0], f["round"], f["bank"][us], f["bank"][1 - us], earned, held, at(300), at(450), at(600)))
for r in rows: print(*r)
n = len(rows)
print(f"{TEAM}: n {n} | end gold held avg {sum(r[5] for r in rows)/n:.0f} of earned {sum(r[4] for r in rows)/n:.0f} | held r300 {sum(r[6] or 0 for r in rows)/n:.0f} r450 {sum(r[7] or 0 for r in rows)/n:.0f} r600 {sum(r[8] or 0 for r in rows)/n:.0f}")
