# show.py FOCUS GAME.json VICTIM_ID R0 R1 : round by round, the victim and every champion within 8 of it: tile, health, cooldowns, stun,
# channel, and their actions that round (m move, A attack -> target tile [c champion / m camp] with damage, C cast slot, D dash).
import sys, collections
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import Game, cheb, DASH

focus, path, v, R0, R1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
g = Game(path, focus)
print(g.name, "focus team", g.focus, "victim", v, g.cname[v])
for r in range(R0, R1 + 1):
    vs = g.st(r, v)
    if not vs: continue
    print(f"r{r}")
    rows = [c for c in g.byr[r].values() if c["al"] and c.get("p") and vs.get("p") and cheb(c["p"], vs["p"]) <= 8] if vs["al"] else [vs]
    for c in sorted(rows, key=lambda c: (c["t"] != g.focus, c["id"])):
        acts = []
        for a in g.acts.get(r, []):
            if a["id"] != c["id"]: continue
            dd = ",".join(f"{g.cname[int(k)]}{int(k)}:{x:.0f}" for k, x in (a.get("d") or {}).items())
            if a["k"] == 4: acts.append("m")
            elif a["k"] == 5: acts.append(f"A{a.get('tc') or ''}[{dd}]")
            elif a["k"] == 6:
                dash = (g.cname[c["id"]], a.get("s")) in DASH and a.get("f") != a.get("a")
                acts.append(f"{'D' if dash else 'C'}{a.get('s')}{a.get('tc') or ''}[{dd}]")
            elif a["k"] == 14: acts.append("ward")
        side = "F" if c["t"] == g.focus else "E"
        dist = cheb(c["p"], vs["p"]) if vs.get("p") and c.get("p") else -1
        print(f"   {side} {g.cname[c['id']]:8s}{c['id']:2d} ({c['p']['x']:2d},{c['p']['y']:2d}) d{dist} hp {c['hp']:6.0f}/{c['mx']:5d} cd{c['cd']} "
              f"{'stun ' if c['stun'] else ''}{'chn' + str(c['chn']) + ' ' if c['chn'] else ''}gm{c['gm']} st{c['st']} fo{c['fo']} | {' '.join(acts)}"
              + (f" mon-{g.mdmg[(c['id'], r)]:.0f}" if g.mdmg.get((c['id'], r)) else ""))
