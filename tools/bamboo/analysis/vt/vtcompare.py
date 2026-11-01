# vtcompare.py DIR : our bot vs a teammate bot from run-batch traces (DIR/<map>__<A|B>/trace.json, side = our side): per game and in
# total - banked gems at r200/400/600/800, end round, captures and gems captured, deaths, gems carried at death, tributes (bank jumps)
# and their mean size, and the round of a monolith-sized capture (>= 150 gems to one team in one round).
import json, os, sys, collections
D = sys.argv[1]; CUTS = [200, 400, 600, 800]
tot = {s: collections.Counter() for s in ("us", "them")}; n = 0; lines = []
for g in sorted(os.listdir(D)):
    p = os.path.join(D, g, "trace.json")
    if not os.path.isfile(p): continue
    mp, side = g.rsplit("__", 1); us = 0 if side == "A" else 1
    t = json.load(open(p, encoding="utf-8")); n += 1
    team = {int(k): v["team"] for k, v in t["champions"].items()}
    rounds = t["rounds"]; byr = {x["r"]: x for x in rounds}
    res = {}
    for who, ti in (("us", us), ("them", 1 - us)):
        c = collections.Counter()
        for cut in CUTS:
            x = next((x for x in rounds if x["r"] >= cut), rounds[-1]); c[f"bank{cut}"] = x["bank"][ti]
        inc = [e for e in t["income"] if team.get(e["id"]) == ti]
        c["caps"] = len({(e["r"], e["input"]) for e in inc}); c["capgems"] = sum(e.get("sub", 0) for e in inc)
        per = collections.Counter()
        for e in inc: per[e["r"]] += e.get("sub", 0)
        mono = [r for r, v in sorted(per.items()) if v >= 150]; c["mono_first"] = mono[0] if mono else 0; c["mono_n"] = len(mono)
        prev = {}; prevbank = 0
        for x in rounds:
            for ch in x["ch"]:
                if ch["team"] != ti: continue
                if prev.get(ch["id"], {}).get("alive") and not ch["alive"]: c["deaths"] += 1; c["gems_lost"] += prev[ch["id"]].get("gems", 0)
                prev[ch["id"]] = ch
            b = x["bank"][ti]
            if b > prevbank: c["tributes"] += 1; c["tribute_gems"] += b - prevbank
            prevbank = b
        c["end"] = t["final"]["round"]; c["final"] = t["final"]["bank"][ti]
        res[who] = c; tot[who].update(c)
    u, h = res["us"], res["them"]
    lines.append(f"{g:24s} end {u['end']:4d} bank us/them r400 {u['bank400']:4d}/{h['bank400']:4d} r800 {u['bank800']:4d}/{h['bank800']:4d} final {u['final']:4d}/{h['final']:4d} | caps {u['caps']:3d}/{h['caps']:3d} deaths {u['deaths']:2d}/{h['deaths']:2d} lost {u['gems_lost']:3d}/{h['gems_lost']:3d} trib {u['tributes']:3d}/{h['tributes']:3d} mono {u['mono_first']:4d}/{h['mono_first']:4d}")
print("\n".join(lines))
for who in ("us", "them"):
    c = tot[who]
    print(f"{who:5s} avg over {n}: bank r200 {c['bank200']/n:.0f} r400 {c['bank400']/n:.0f} r600 {c['bank600']/n:.0f} r800 {c['bank800']/n:.0f} | caps {c['caps']/n:.1f} capgems {c['capgems']/n:.0f} | deaths {c['deaths']/n:.1f} gems lost {c['gems_lost']/n:.0f} | tributes {c['tributes']/n:.1f} size {c['tribute_gems']/max(1,c['tributes']):.1f} | monolith games {sum(1 for _ in [0])}")
