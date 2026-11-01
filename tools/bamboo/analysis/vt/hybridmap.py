# hybridmap.py RUNDIR ARM OPP... : per map, ARM's wins / games and gem margin vs each OPP from a fastscreen run's logs (RUNDIR/<ARM>s1-<OPP>/),
# joined with results/db/mapfeatures.json (team = picks, plan, spawnpath, heavy_share, harmless_share); split by picks / plan / spawn path.
import json, os, re, sys, collections
run, arm, opps = sys.argv[1], sys.argv[2], sys.argv[3:]
feat = json.load(open("results/db/mapfeatures.json", encoding="utf-8"))
norm = lambda m: m.replace("-", "_")
fe = {norm(k): v for k, v in feat.items()}
per = collections.defaultdict(lambda: collections.Counter())
for opp in opps:
    d = os.path.join(run, f"{arm}s1-{opp}")
    for f in os.listdir(d):
        t = open(os.path.join(d, f), errors="ignore").read()
        rows = re.findall(r"^\s+([AB])\s+(\S+)\s+(\d+)\s", t, re.M)
        if len(rows) < 2: continue
        g = {n: int(x) for _, n, x in rows[-2:]}
        us = next((v for k, v in g.items() if k.startswith(arm)), None); them = g.get(opp)
        if us is None or them is None: continue
        m = norm(f.split(f"-{arm}s1")[0].split(f"-{opp}")[0])
        c = per[(m, opp)]; c["n"] += 1; c["w"] += us > them; c["m"] += us - them
def bucket(m):
    f = fe.get(m, {})
    sp = f.get("spawnpath", -1)
    return {"picks": f.get("team", "?"), "plan": f.get("plan", "?"), "spawn": "?" if sp < 0 else ("<=30" if sp <= 30 else "31-60" if sp <= 60 else ">60")}
for opp in opps:
    print(f"== {arm} vs {opp}")
    for key in ("picks", "plan", "spawn"):
        agg = collections.defaultdict(lambda: collections.Counter())
        for (m, o), c in per.items():
            if o != opp: continue
            b = bucket(m)[key]; agg[b].update(c); agg[b]["maps"] += 1
        print(f"  by {key}: " + " | ".join(f"{k}: {v['w']}/{v['n']} ({100*v['w']//max(1,v['n'])}%, {v['m']/max(1,v['n']):+.0f}, {v['maps']} maps)" for k, v in sorted(agg.items(), key=lambda kv: str(kv[0]))))
missing = sorted({m for (m, _) in per if m not in fe}); print("maps without features:", missing)
