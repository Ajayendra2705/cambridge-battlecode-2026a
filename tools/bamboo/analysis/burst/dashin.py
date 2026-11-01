# dashin.py "LABEL=FOCUS[,FOCUS2]|GLOB" ... : dash-ins of team FOCUS (burst/extract.ts output): a dash (Vendetta / HoR / Vesper / Issac /
# Ren dash slot, tile changed) that ends nearer an enemy champion and within its attack reach of it (melee 1, ranged 3). Per dash-in:
# the target's health share at the round start, the dasher's, FOCUS within 6 of the target (incl. the dasher) vs the target's team within
# 6 (incl.), burst potential of FOCUS within 6 / target health, the target busy / stunned, damage the target took that round from FOCUS,
# and outcomes: target dead within 8 rounds, dasher dead within 8. Printed by dasher type and by buckets; R0/R1 env limit the rounds.
import sys, glob, os, collections
sys.path.insert(0, os.path.dirname(__file__))
from common import Game, cheb, DASH

R0, R1 = int(os.environ.get("R0", 0)), int(os.environ.get("R1", 9999))
for arg in sys.argv[1:]:
    lab, rest = arg.split("=", 1)
    names, pat = rest.split("|")
    rows = []; ng = 0
    for fp in sorted(glob.glob(pat)):
        for nm in names.split(","):
            g = Game(fp, nm)
            if g.focus is None: continue
            ng += 1; F = g.focus
            die = collections.defaultdict(list)
            for d in g.deaths: die[d["v"]].append(d)
            for r in g.rounds:
                if not (R0 <= r < R1): continue
                for a in g.acts.get(r, []):
                    if g.team[a["id"]] != F or a["k"] != 6: continue
                    cn = g.cname[a["id"]]
                    if (cn, a.get("s")) not in DASH or not a.get("f") or not a.get("a") or a["f"] == a["a"]: continue
                    me = g.st(r, a["id"])
                    if not me: continue
                    reach = 3 if me["rng"] >= 3 else 1
                    en = [e for e in g.alive(r, 1 - F) if cheb(e["p"], a["a"]) <= reach + 1 and cheb(e["p"], a["a"]) < cheb(e["p"], a["f"])]
                    if not en: continue
                    t = min(en, key=lambda e: (cheb(e["p"], a["a"]), e["hp"]))
                    nf = g.near(r, t["p"], F, 6); ne = g.near(r, t["p"], 1 - F, 6)
                    pot = sum(g.burst(c) for c in nf)
                    tdead = any(r <= d["r"] <= r + 8 for d in die[t["id"]])
                    ddead = any(r <= d["r"] <= r + 8 for d in die[a["id"]])
                    hitters = {x for rr in range(r, r + 4) for x in g.dmg_by[(t["id"], rr)] if g.team[x] == F}
                    fol_dmg = sum(x for rr in range(r, r + 4) for o, x in g.dmg_by[(t["id"], rr)].items() if g.team[o] == F) / t["mx"]
                    idle = [c for c in nf if c["id"] not in hitters and c["id"] != a["id"]]
                    rows.append(dict(hitters=len(hitters), fol=fol_dmg, idle=len(idle), cn=cn, thp=t["hp"] / t["mx"], dhp=me["hp"] / me["mx"], nf=len(nf), ne=len(ne), pr=pot / max(1, t["hp"]),
                                     busy=g.busy(t["id"], r), stun=t["stun"] > 0, dmg=g.dmg_on[t["id"]].get(r, 0) / t["mx"], tdead=tdead, ddead=ddead,
                                     game=g.gid, r=r))
    print(f"== {lab}: team-games {ng}, dash-ins {len(rows)} ({len(rows) / max(1, ng):.1f}/game, rounds {R0}-{R1})")

    def summ(R):
        n = len(R)
        if not n: return "-"
        f = lambda p: f"{100 * sum(1 for x in R if p(x)) / n:3.0f}%"
        return (f"n{n:4d} kill8 {f(lambda x: x['tdead'])} dasher-dies8 {f(lambda x: x['ddead'])} | target hp<50 {f(lambda x: x['thp'] < .5)} "
                f">=85 {f(lambda x: x['thp'] >= .85)} | nf>ne {f(lambda x: x['nf'] > x['ne'])} nf<ne {f(lambda x: x['nf'] < x['ne'])} | pot>=hp {f(lambda x: x['pr'] >= 1)} "
                f"pot>=.6 {f(lambda x: x['pr'] >= .6)} | stunned {f(lambda x: x['stun'])} | dasher hp>=70 {f(lambda x: x['dhp'] >= .7)} | target busy camp/recall {f(lambda x: x['busy'] in ('camp', 'recall', 'tribute'))}")
    print("  all     ", summ(rows))
    mn = lambda R, k: f"{sum(x[k] for x in R) / max(1, len(R)):.2f}"
    print(f"  follow-up r..r+3: FOCUS hitters on the target {mn(rows, 'hitters')}, damage {mn(rows, 'fol')} of its max, FOCUS within 6 that did not hit it {mn(rows, 'idle')}; "
          f"target >=85%: hitters {mn([x for x in rows if x['thp'] >= .85], 'hitters')} dmg {mn([x for x in rows if x['thp'] >= .85], 'fol')}")
    for cn in sorted({x["cn"] for x in rows}):
        print(f"  {cn:8s}", summ([x for x in rows if x["cn"] == cn]))
    print("  kill8 by target hp:", " ".join(f"{l}: {summ_k}" for l, summ_k in (
        (l, f"{sum(1 for x in rows if lo <= x['thp'] < hi and x['tdead'])}/{sum(1 for x in rows if lo <= x['thp'] < hi)}") for l, lo, hi in (("<35", 0, .35), ("35-60", .35, .6), ("60-85", .6, .85), (">=85", .85, 9)))))
    print("  kill8 by nf-ne:", " ".join(f"{k}: {sum(1 for x in rows if max(-2, min(2, x['nf'] - x['ne'])) == k and x['tdead'])}/{sum(1 for x in rows if max(-2, min(2, x['nf'] - x['ne'])) == k)}" for k in (-2, -1, 0, 1, 2)))
    print("  kill8 by pot/hp:", " ".join(f"{l}: {sum(1 for x in rows if lo <= x['pr'] < hi and x['tdead'])}/{sum(1 for x in rows if lo <= x['pr'] < hi)}" for l, lo, hi in (("<.35", 0, .35), (".35-.6", .35, .6), (".6-1", .6, 1), (">=1", 1, 99))))
