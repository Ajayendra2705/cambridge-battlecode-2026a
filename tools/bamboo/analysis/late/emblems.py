# emblems.py TEAM DIR... : average emblems (odd item ids) and shards (even ids, /5) per living champion of TEAM at a few rounds.
import json, os, sys
TEAM = sys.argv[1]; R = [150, 300, 450, 600, 800, 1000]; acc = {r: [0.0, 0.0, 0] for r in R}
for d in sys.argv[2:]:
    for g in sorted(os.listdir(d)):
        parts = g.split("__")
        if TEAM not in parts[1:3]: continue
        p = os.path.join(d, g, "trace.json")
        if not os.path.isfile(p): continue
        t = json.load(open(p)); us = 0 if parts[1] == TEAM else 1; rounds = t["rounds"]
        for r in R:
            x = next((x for x in rounds if x["r"] >= r), None)
            if x is None: continue
            for c in x["ch"]:
                if c["team"] != us: continue
                it = c["items"]; acc[r][0] += sum(it[i] for i in range(1, len(it), 2)); acc[r][1] += sum(it[i] for i in range(0, len(it), 2)) / 5; acc[r][2] += 1
print(TEAM, " | ".join(f"r{r}: emb {a[0]/max(1,a[2]):.2f} +shards {a[1]/max(1,a[2]):.2f}" for r, a in acc.items()))
