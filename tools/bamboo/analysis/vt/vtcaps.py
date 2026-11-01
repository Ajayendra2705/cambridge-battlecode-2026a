# vtcaps.py DIR : captures by kind (from the summed reward of one capture: gems / gold) and by phase, us vs them; plus how many of a
# team's champions were capturing in parallel (distinct capture events within the same 10-round window).
import json, os, sys, collections
D = sys.argv[1]; PH = [(0, 300), (300, 600), (600, 900), (900, 2001)]
def kind(gm, gd):
    if gd == 0 and gm <= 9: return "gem cluster(s) small"
    if gm == 0: return "gold only"
    if gm <= 6 and gd <= 60: return "wolf-ish"
    if gm <= 40: return "elk / mixed"
    return "big (golem/monolith)"
tot = {s: collections.Counter() for s in ("us", "them")}; ph = {s: collections.Counter() for s in ("us", "them")}; par = {s: [] for s in ("us", "them")}; n = 0
for g in sorted(os.listdir(D)):
    p = os.path.join(D, g, "trace.json")
    if not os.path.isfile(p): continue
    us = 0 if g.endswith("__A") else 1; t = json.load(open(p, encoding="utf-8")); n += 1
    team = {int(k): v["team"] for k, v in t["champions"].items()}
    for who, ti in (("us", us), ("them", 1 - us)):
        caps = collections.defaultdict(lambda: [0, 0, 0])
        for e in t["income"]:
            if team.get(e["id"]) != ti: continue
            c = caps[(e["r"], e["input"])]; c[0] += e.get("sub", 0); c[1] += e.get("gold", 0); c[2] = e["r"]
        for (r, _), (gm, gd, _) in caps.items():
            tot[who][kind(gm, gd)] += 1
            ph[who][next(f"r{a}-{b}" for a, b in PH if a <= r < b)] += 1
        rs = sorted(r for (r, _) in caps); 
        for i, r in enumerate(rs): par[who].append(sum(1 for q in rs if r <= q < r + 10))
for who in ("us", "them"):
    print(who, "per game:", {k: round(v / n, 1) for k, v in sorted(tot[who].items())})
    print("   by phase:", {k: round(v / n, 1) for k, v in sorted(ph[who].items())}, "| captures within the same 10 rounds (mean):", round(sum(par[who]) / max(1, len(par[who])), 2))
