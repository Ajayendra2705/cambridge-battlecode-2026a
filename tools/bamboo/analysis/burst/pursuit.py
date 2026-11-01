# pursuit.py "LABEL=FOCUS[,FOCUS2]|GLOB" ... : how far FOCUS pursues a hurt enemy (burst/extract.ts output). A pursuit starts at the first
# round an enemy champion is under LOW (0.5) of its max health with a FOCUS champion within 4 that damaged it in the last 3 rounds (after
# 20 rounds without such a start for that enemy). It lasts while some FOCUS champion stays within 4 of it; it ends with the enemy's death
# (kill) or the last such round (escape). Per pursuit: rounds, FOCUS chasers (within 4 at some point), the enemy's spawn distance at the
# start and at the end (Chebyshev to its nearest start tile), rounds with no FOCUS damage while pursuing, chasers' health at the end, and
# whether a chaser with a dash ready was within 4 when it ended. R1 env (600) limits the start round.
import sys, glob, os, collections, statistics as stt
sys.path.insert(0, os.path.dirname(__file__))
from common import Game, cheb, DASH

LOW = float(os.environ.get("LOW", 0.5)); R1 = int(os.environ.get("R1", 600))
for arg in sys.argv[1:]:
    lab, rest = arg.split("=", 1); names, pat = rest.split("|")
    P = []; ng = 0; CR = collections.defaultdict(collections.Counter)
    for fp in sorted(glob.glob(pat)):
        for nm in names.split(","):
            g = Game(fp, nm)
            if g.focus is None: continue
            ng += 1; F = g.focus
            die = {}
            for d in g.deaths: die.setdefault(d["v"], []).append(d["r"])
            last_start = collections.defaultdict(lambda: -99)
            busy_until = collections.defaultdict(lambda: -1)
            for r in g.rounds:
                if r >= R1: break
                for e in g.alive(r, 1 - F):
                    if e["hp"] >= LOW * e["mx"] or r <= busy_until[e["id"]] or r - last_start[e["id"]] < 20: continue
                    recent = {a for rr in range(r - 3, r + 1) for a in g.dmg_by[(e["id"], rr)] if g.team[a] == F}
                    near = [c for c in g.near(r, e["p"], F, 4) if c["id"] in recent]
                    if not near: continue
                    last_start[e["id"]] = r
                    chasers = set(c["id"] for c in near); k = r; nodmg = 0; out = "escape"
                    while True:
                        es = g.st(k, e["id"])
                        if not es or not es["al"]:
                            out = "kill" if any(r <= x <= k for x in die.get(e["id"], [])) else "escape"; break
                        nk = g.near(k, es["p"], F, 4)
                        if not nk: break
                        chasers |= {c["id"] for c in nk}
                        if not any(g.team[a] == F for a in g.dmg_by[(e["id"], k)]): nodmg += 1
                        for c in nk:
                            cn = g.cname[c["id"]]; hit = g.dmg_by[(e["id"], k)].get(c["id"], 0) > 0
                            hit_other = any(g.team[int(v)] != F and x > 0 for a in g.acts.get(k, []) if a["id"] == c["id"] for v, x in (a.get("d") or {}).items()) and not hit
                            dr = any((cn, s) in DASH and len(c["cd"]) > s and c["cd"][s] == 0 for s in (0, 1))
                            dashed = any(a["id"] == c["id"] and a["k"] == 6 and (cn, a.get("s")) in DASH and a.get("f") != a.get("a") for a in g.acts.get(k, []))
                            camp = any(a["id"] == c["id"] and a.get("tc") == "m" for a in g.acts.get(k, []))
                            d0 = cheb(c["p"], es["p"])
                            CR[cn]["n"] += 1; CR[cn]["hit"] += hit; CR[cn]["other"] += hit_other; CR[cn]["camp"] += camp
                            CR[cn]["dr"] += dr; CR[cn]["dr_used"] += dr and dashed; CR[cn]["d"] += d0
                            CR[cn]["inreach"] += d0 <= c["rng"]; CR[cn]["inreach_hit"] += d0 <= c["rng"] and hit
                            CR[cn]["out_nohit"] += d0 > c["rng"] and not hit
                        k += 1
                        if k > g.last: break
                    end = k if out == "kill" else k - 1
                    busy_until[e["id"]] = end
                    es0 = g.st(r, e["id"]); esE = g.st(end, e["id"]) if out == "escape" else g.st(end - 1, e["id"]) or g.st(end, e["id"])
                    ch_end = [g.st(end, a) for a in chasers]; ch_end = [c for c in ch_end if c and c["al"]]
                    dash_ready = any(c for c in ch_end if any((g.cname[c["id"]], s) in DASH and len(c["cd"]) > s and c["cd"][s] == 0 for s in (0, 1)))
                    after = g.st(end + 3, e["id"]) or {}
                    P.append(dict(out=out, rounds=end - r + 1, chasers=len(chasers), hp0=es0["hp"] / es0["mx"],
                                  sp0=g.spawn_dist(es0["p"], g.team[e["id"]]), spE=g.spawn_dist(esE["p"], g.team[e["id"]]) if esE and esE.get("p") else -1,
                                  nodmg=nodmg, chp=min((c["hp"] / c["mx"] for c in ch_end), default=0), dash_ready=dash_ready,
                                  recalled=after.get("chn") == 1 or (after.get("p") and g.spawn_dist(after["p"], g.team[e["id"]]) <= 1)))
    K = [p for p in P if p["out"] == "kill"]; X = [p for p in P if p["out"] == "escape"]
    md = lambda xs: f"{stt.median(xs):.1f}" if xs else "-"
    sh = lambda R, f: f"{100 * sum(1 for p in R if f(p)) / max(1, len(R)):.0f}%"
    print(f"== {lab}: team-games {ng}; pursuits of enemies under {LOW:.0%} (start < r{R1}): {len(P)} ({len(P) / max(1, ng):.1f}/game), killed {len(K)} ({sh(P, lambda p: p['out'] == 'kill')})")
    for nm_, R in (("kill", K), ("escape", X)):
        print(f"   {nm_:6s} rounds {md([p['rounds'] for p in R])}  chasers {md([p['chasers'] for p in R])} (2+ {sh(R, lambda p: p['chasers'] >= 2)})  "
              f"hp at start {md([p['hp0'] for p in R])}  spawn dist start {md([p['sp0'] for p in R])} end {md([p['spE'] for p in R])} (end <= 6: {sh(R, lambda p: 0 <= p['spE'] <= 6)})  "
              f"rounds without dmg {md([p['nodmg'] for p in R])}  chaser min hp at end {md([p['chp'] for p in R])}  dash ready at end {sh(R, lambda p: p['dash_ready'])}")
    for cn, c in sorted(CR.items(), key=lambda x: -x[1]["n"]):
        if c["n"] < 20: continue
        print(f"   chaser {cn:8s} rounds {c['n']:4d}: hit the hurt enemy {100 * c['hit'] / c['n']:.0f}% (hit another {100 * c['other'] / c['n']:.0f}%, camp {100 * c['camp'] / c['n']:.0f}%), "
              f"mean distance {c['d'] / c['n']:.1f}, in attack range at round start {100 * c['inreach'] / c['n']:.0f}% (hit then {100 * c['inreach_hit'] / max(1, c['inreach']):.0f}%), "
              f"dash ready {100 * c['dr'] / c['n']:.0f}% of rounds, used when ready {100 * c['dr_used'] / max(1, c['dr']):.0f}%")
    print("   kill share by chasers:", " ".join(f"{k}: {sum(1 for p in K if min(p['chasers'], 3) == k)}/{sum(1 for p in P if min(p['chasers'], 3) == k)}" for k in (1, 2, 3)),
          "| by start spawn dist:", " ".join(f"{l}: {sum(1 for p in K if lo <= p['sp0'] < hi)}/{sum(1 for p in P if lo <= p['sp0'] < hi)}" for l, lo, hi in (("<=6", 0, 7), ("7-12", 7, 13), ("13-20", 13, 21), (">20", 21, 999))))
