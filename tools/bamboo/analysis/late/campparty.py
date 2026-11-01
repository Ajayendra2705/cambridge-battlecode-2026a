# campparty.py TEAM DIR... : camp-fight episodes (a team's damage on one group, gaps <= 12 rounds) with >= MIN damage: champions that hit
# it, rounds taken, damage per round, by phase; and the team's champion-rounds busy on camps vs all alive champion-rounds.
import json, os, sys, collections
TEAM = sys.argv[1]; MIN = int(os.environ.get("MIN", "1300")); PH = [(0, 300), (300, 600), (600, 900), (900, 2001)]
st = {p: collections.Counter() for p in PH}; parties = {p: collections.Counter() for p in PH}; n = 0
for d in sys.argv[2:]:
    for g in sorted(os.listdir(d)):
        parts = g.split("__")
        if TEAM not in parts[1:3]: continue
        p = os.path.join(d, g, "trace.json")
        if not os.path.isfile(p): continue
        t = json.load(open(p)); n += 1; us = 0 if parts[1] == TEAM else 1
        team = {int(k): v["team"] for k, v in t["champions"].items()}
        ev = collections.defaultdict(list)
        for e in t["damage"]:
            if e.get("group") is None or team.get(e.get("actor")) != us: continue
            ev[e["group"]].append(e)
        for gid, es in ev.items():
            es.sort(key=lambda e: e["r"]); cur = []
            def flush(cur):
                if not cur: return
                dmg = sum(e["amount"] for e in cur)
                if dmg < MIN: return
                r0, r1 = cur[0]["r"], cur[-1]["r"]; actors = {e["actor"] for e in cur}
                ph = next(x for x in PH if x[0] <= r0 < x[1])
                c = st[ph]; c["eps"] += 1; c["actors"] += len(actors); c["rounds"] += r1 - r0 + 1; c["dmg"] += dmg; c["chr"] += len(actors) * (r1 - r0 + 1)
                parties[ph][min(len(actors), 4)] += 1
            for e in es:
                if cur and e["r"] - cur[-1]["r"] > 12: flush(cur); cur = []
                cur.append(e)
            flush(cur)
print(f"{TEAM}: {n} games (episodes with >= {MIN} damage)")
for ph in PH:
    c = st[ph]; e = max(1, c["eps"]); tot = sum(parties[ph].values()) or 1
    print(f"  r{ph[0]}-{ph[1]}: eps/game {c['eps']/max(1,n):.1f} | champs {c['actors']/e:.2f} | rounds {c['rounds']/e:.1f} | dmg/round {c['dmg']/max(1,c['rounds']):.0f} | champ-rounds/ep {c['chr']/e:.1f} | dmg/champ-round {c['dmg']/max(1,c['chr']):.0f} | party 1/2/3/4+: " + "/".join(f"{100*parties[ph][k]/tot:.0f}" for k in (1, 2, 3, 4)) + "%")
