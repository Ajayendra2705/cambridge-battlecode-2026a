# vtsplit.py DIR : champion-rounds by activity (dead, camp = hit a camp this round, pvp = hit a champion, home = within 4 of its spawn,
# walk = moved, still) for us vs them in run-batch traces, rounds 0-900; plus the mean champions hitting the same camp in a round.
import json, os, sys, collections
D = sys.argv[1]; R1 = int(os.environ.get("R1", "900"))
acc = {s: collections.Counter() for s in ("us", "them")}; party = {s: [] for s in ("us", "them")}
for g in sorted(os.listdir(D)):
    p = os.path.join(D, g, "trace.json")
    if not os.path.isfile(p): continue
    us = 0 if g.endswith("__A") else 1; t = json.load(open(p, encoding="utf-8"))
    champs = {int(k): v for k, v in t["champions"].items()}; team = {k: v["team"] for k, v in champs.items()}
    camp = collections.defaultdict(set); grp = collections.defaultdict(lambda: collections.defaultdict(set)); pvp = collections.defaultdict(set)
    for e in t["damage"]:
        if e["r"] >= R1: continue
        if e.get("group") is not None: camp[e["r"]].add(e["actor"]); grp[e["r"]][e["group"]].add(e["actor"])
        else: pvp[e["r"]].add(e["actor"])
    prev = {}
    for x in t["rounds"]:
        r = x["r"]
        if r >= R1: break
        for c in x["ch"]:
            who = "us" if c["team"] == us else "them"; i = c["id"]; sp = champs[i]["spawn"]; pos = (c["p"]["x"], c["p"]["y"]) if "p" in c else None
            if not c["alive"]: k = "dead"
            elif i in camp[r]: k = "camp"
            elif i in pvp[r]: k = "pvp"
            elif pos and max(abs(pos[0] - sp["x"]), abs(pos[1] - sp["y"])) <= 4: k = "home"
            elif prev.get(i) is not None and prev[i] != pos: k = "walk"
            else: k = "still"
            acc[who][k] += 1; prev[i] = pos
        for gid, actors in grp[r].items():
            for who, ti in (("us", us), ("them", 1 - us)):
                n = sum(1 for a in actors if team.get(a) == ti)
                if n: party[who].append(n)
for who in ("us", "them"):
    tot = sum(acc[who].values()) or 1
    print(f"{who:5s} " + " ".join(f"{k} {100*acc[who][k]/tot:.1f}%" for k in ("camp", "pvp", "walk", "still", "home", "dead")) + f" | champions on one camp per hit-round {sum(party[who])/max(1,len(party[who])):.2f}")
