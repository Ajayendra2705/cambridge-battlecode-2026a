# timesplit.py TEAM DIR... : TEAM's champion-rounds in R0-R1 by activity: dead, home (<= 4 of its spawn), channel (recall / gather), camp
# (hit a camp this round), pvp (hit an enemy champion), walk (moved), still (none of these). Env R0 R1 (default 300 600).
import json, os, sys, collections
TEAM = sys.argv[1]; R0 = int(os.environ.get("R0", "300")); R1 = int(os.environ.get("R1", "600"))
acc = collections.Counter(); stillwhere = collections.Counter(); n = 0
for d in sys.argv[2:]:
    for g in sorted(os.listdir(d)):
        parts = g.split("__")
        if TEAM not in parts[1:3]: continue
        p = os.path.join(d, g, "trace.json")
        if not os.path.isfile(p): continue
        t = json.load(open(p)); us = 0 if parts[1] == TEAM else 1
        champs = {int(k): v for k, v in t["champions"].items()}; team = {k: v["team"] for k, v in champs.items()}
        if t["final"]["round"] < R1: continue
        n += 1
        camp = collections.defaultdict(set)
        for e in t["damage"]:
            if R0 <= e["r"] < R1 and team.get(e.get("actor")) == us:
                camp[e["r"]].add(e["actor"]) if e.get("group") is not None else None
        pvp = collections.defaultdict(set)
        epos = {}
        rounds = {x["r"]: x for x in t["rounds"]}
        for e in t["damage"]:
            if R0 <= e["r"] < R1 and e.get("group") is None and team.get(e.get("actor")) == us: pvp[e["r"]].add(e["actor"])
        prev = {}
        for r in range(R0, R1):
            x = rounds.get(r)
            if x is None: continue
            for c in x["ch"]:
                if c["team"] != us: continue
                i = c["id"]; sp = champs[i]["spawn"]; pos = (c["p"]["x"], c["p"]["y"]) if "p" in c else None
                if not c["alive"]: k = "dead"
                elif i in camp[r]: k = "camp"
                elif i in pvp[r]: k = "pvp"
                elif pos is not None and max(abs(pos[0] - sp["x"]), abs(pos[1] - sp["y"])) <= 4: k = "home"
                elif prev.get(i) is not None and prev[i] != pos: k = "walk"
                elif c.get("channel", 0): k = "channel"
                else: k = "still"
                acc[k] += 1; prev[i] = pos
tot = sum(acc.values()) or 1
print(f"{TEAM} r{R0}-{R1} ({n} games): " + " ".join(f"{k} {100*acc[k]/tot:.1f}%" for k in ("camp", "pvp", "walk", "still", "home", "channel", "dead")))
