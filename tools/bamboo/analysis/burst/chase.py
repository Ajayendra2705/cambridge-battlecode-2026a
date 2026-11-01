# chase.py "LABEL=FOCUS|EP.jsonl|GLOB" ... : what ends FOCUS's damage episodes (kills.py output joined with burst/extract.ts games).
# For every episode where the victim fell below LOW (0.5) of its max health: the outcome, and after the last hit L the attackers' pursuit
# (rounds any attacker stays within 4 of the victim), the victim's reaction (genuine recall within L..L+6, back at its spawn within
# L+10), reinforcements (victim's team within 6 of the victim at L vs S), the attackers at L (lowest health share, damaging spells /
# dashes ready), and the victim's distance to its own spawn and to FOCUS's at L. Stop reason, first that applies: recall / home /
# attackers hurt (<35%) / outnumbered (victim side within 6 > FOCUS within 6) / outran (no attacker within 4 at L+3) / other.
import json, sys, glob, os, collections, statistics as stt
sys.path.insert(0, os.path.dirname(__file__))
from common import Game, cheb, SPELL_MOD, DASH

LOW = float(os.environ.get("LOW", "0.5"))
R1 = int(os.environ.get("R1", "600"))
for arg in sys.argv[1:]:
    lab, rest = arg.split("=", 1)
    focus, epf, pat = rest.split("|")
    focus_names = focus.split(",")
    E = [json.loads(l) for l in open(epf)]
    E = [e for e in E if e["minhp"] < LOW and e["outcome"] in ("kill", "escaped") and e["S"] < R1]
    games = {}
    for fp in glob.glob(pat):
        games[os.path.basename(fp)[:-5]] = fp
    C = collections.defaultdict(collections.Counter); P = collections.defaultdict(list)
    cache = {}
    for e in E:
        fp = games.get(e["game"])
        if not fp: continue
        # which focus team in this game
        key = (fp, e["opp"])
        if key not in cache:
            g = None
            for nm in focus_names:
                gg = Game(fp, nm)
                if gg.focus is not None and gg.opp_name == e["opp"]: g = gg; break
            cache[key] = g
        g = cache[key]
        if g is None: continue
        F, v, S, L = g.focus, e["v"], e["S"], e["L"]
        att = [a for a in g.ch if g.team[a] == F and any(g.dmg_by[(v, r)].get(a, 0) > 0 for r in range(S, L + 1))]
        out = e["outcome"]
        vL = g.st(L, v) or {}
        # pursuit after L
        pursue = 0
        for k in range(1, 16):
            vs = g.st(L + k, v)
            if not vs or not vs["al"] or not vs.get("p"): break
            if any((g.st(L + k, a) or {}).get("al") and (g.st(L + k, a) or {}).get("p") and cheb(g.st(L + k, a)["p"], vs["p"]) <= 4 for a in att): pursue += 1
            else: break
        recall = any((g.st(r, v) or {}).get("chn") == 1 and not any(a["id"] == v and a["k"] in (4, 5, 6) for a in g.acts.get(r, [])) for r in range(L, L + 7))
        home = any((g.st(r, v) or {}).get("p") and g.spawn_dist(g.st(r, v)["p"], g.team[v]) <= 2 for r in range(L, L + 11))
        nfL = len(g.near(L, vL.get("p") or {"x": -99, "y": -99}, F, 6)) if vL.get("p") else 0
        neL = len(g.near(L, vL["p"], g.team[v], 6)) if vL.get("p") else 0
        neS = e["ne6"]
        ast = [g.st(L, a) for a in att]; ast = [c for c in ast if c and c["al"]]
        amin = min((c["hp"] / c["mx"] for c in ast), default=0)
        dready = sum(1 for c in ast for s in (0, 1) if len(c["cd"]) > s and c["cd"][s] == 0 and (g.cname[c["id"]], s) in SPELL_MOD)
        dashr = sum(1 for c in ast for s in (0, 1) if len(c["cd"]) > s and c["cd"][s] == 0 and (g.cname[c["id"]], s) in DASH)
        att_dead = sum(1 for a in att if not (g.st(L + 2, a) or {}).get("al", True))
        p3 = g.st(L + 3, v) or {}
        near3 = any((g.st(L + 3, a) or {}).get("al") and p3.get("p") and (g.st(L + 3, a) or {}).get("p") and cheb(g.st(L + 3, a)["p"], p3["p"]) <= 4 for a in att)
        if out == "kill": reason = "killed"
        elif recall: reason = "recall"
        elif home: reason = "home"
        elif att_dead: reason = "attacker died"
        elif amin < 0.35: reason = "attackers hurt"
        elif neL > nfL: reason = "outnumbered"
        elif not near3: reason = "outran/let go"
        else: reason = "other"
        C["reason"][reason] += 1
        C["n"][out] += 1
        P[out + "_pursue"].append(pursue)
        P[out + "_minhp"].append(e["minhp"])
        if out == "escaped":
            P["esc_vspawn"].append(e["vdist_spawn"]); P["esc_dready"].append(dready); P["esc_dash"].append(dashr)
            P["esc_reinf"].append(neL - neS); P["esc_nfL"].append(nfL); P["esc_neL"].append(neL); P["esc_rounds"].append(e["rounds"])
            P["esc_vspawnL"].append(g.spawn_dist(vL["p"], g.team[v]) if vL.get("p") else 99)
            P["esc_fspawnL"].append(g.spawn_dist(vL["p"], F) if vL.get("p") else 99)
            C["esc_low30"]["low<30" if e["minhp"] < 0.3 else "30-50"] += 1
        else:
            P["kill_rounds"].append(e["rounds"])
            P["kill_vspawnL"].append(g.spawn_dist(vL["p"], g.team[v]) if vL.get("p") else 99)
        C["low30"][out] += e["minhp"] < 0.3
    n = sum(C["n"].values())
    print(f"== {lab}: episodes with victim under {LOW:.0%} (S < {R1}): {n}; killed {C['n']['kill']} ({100 * C['n']['kill'] / max(1, n):.0f}%), "
          f"of those under 30%: killed {C['low30']['kill']} / {C['low30']['kill'] + C['low30']['escaped']}")
    print("   end:", ", ".join(f"{k} {v} ({100 * v / max(1, n):.0f}%)" for k, v in C["reason"].most_common()))
    md = lambda xs: f"{stt.median(xs):.1f}" if xs else "-"
    mn = lambda xs: f"{sum(xs) / len(xs):.2f}" if xs else "-"
    print(f"   escapes: pursuit rounds after the last hit median {md(P['escaped_pursue'])} mean {mn(P['escaped_pursue'])}; window rounds {md(P['esc_rounds'])}; "
          f"victim spawn dist at L {md(P['esc_vspawnL'])} (focus spawn {md(P['esc_fspawnL'])}); FOCUS within 6 at L {mn(P['esc_nfL'])} vs theirs {mn(P['esc_neL'])}; "
          f"reinforcement S->L {mn(P['esc_reinf'])}; attackers' dmg spells ready at L {mn(P['esc_dready'])}, dashes ready {mn(P['esc_dash'])}")
    print(f"   kills: window rounds {md(P['kill_rounds'])}; victim spawn dist at last hit {md(P['kill_vspawnL'])}")
