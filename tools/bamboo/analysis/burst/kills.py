# kills.py FOCUS OUT.jsonl GAME.json... : damage episodes of team FOCUS on enemy champions (burst/extract.ts output).
# An episode = rounds in which FOCUS champions damaged one enemy champion, consecutive damage rounds at most GAP (5) apart. Outcome:
# "kill" (the victim died to a FOCUS champion's step within the episode or 3 rounds after its last hit), "monster" (died to a camp step
# then), "escaped" (alive 4+ rounds after the last hit). One JSON line per episode with the window measurements: rounds, attackers and
# their types, damage by autos / spells, casts by slot in the window, dashes that closed distance, victim health at the start, what it
# was doing, nearest ally distance, FOCUS champions within 6 at S-5 / S-3 / S, local numbers, the attackers' spells ready at S, burst
# potential at S vs the victim's health, stuns on the victim, the share of the window's damage dealt in its last 2 rounds.
import json, sys, collections
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import Game, cheb, chains, SPELL_MOD, DASH, CC, RESET

GAP = 5
focus, outp, files = sys.argv[1], sys.argv[2], sys.argv[3:]
out = open(outp, "w")
for f in files:
    g = Game(f, focus)
    if g.focus is None: continue
    F = g.focus
    death_of = collections.defaultdict(list)
    for d in g.deaths:
        death_of[d["v"]].append(d)
    for v, rmap in g.dmg_on.items():
        if g.team[v] == F: continue
        rs = sorted(r for r, x in rmap.items() if x > 0 and any(g.team[a] == F for a in g.dmg_by[(v, r)]))
        for ch in chains(rs, GAP):
            S, L = ch[0], ch[-1]
            dth = next((d for d in death_of[v] if S <= d["r"] <= L + 3), None)
            if dth is None:
                if L + 4 > g.last: continue  # game ended
                outcome = "escaped"
            elif dth["bk"] == 1 and g.team.get(dth["by"]) == F:
                outcome = "kill"
            elif dth["bk"] == 2:
                outcome = "monster"
            else:
                outcome = "other"
            E = dth["r"] if dth else L
            vs = g.st(S, v)
            if not vs or not vs["al"] or not vs.get("p"): continue
            vp = vs["p"]
            attackers = sorted({a for r in ch for a in g.dmg_by[(v, r)] if g.team[a] == F})
            dmg_total = sum(g.dmg_by[(v, r)][a] for r in ch for a in attackers)
            # damage by kind
            auto = spell = 0.0
            casts = collections.Counter(); cast_rounds = []; dash_close = 0; dash_any = 0; dash_rounds = []
            for r in range(S - 2, E + 1):
                for a in g.acts.get(r, []):
                    if a["id"] not in attackers: continue
                    nm = g.cname[a["id"]]
                    dv = (a.get("d") or {}).get(str(v), 0)
                    if S <= r <= E and dv > 0:
                        if a["k"] == 5: auto += dv
                        else: spell += dv
                    if a["k"] == 6:
                        if S <= r <= E:
                            casts[f"{nm}.s{a.get('s')}"] += 1; cast_rounds.append(r)
                        if (nm, a.get("s")) in DASH and a.get("f") and a.get("a") and a["f"] != a["a"]:
                            vpos = (g.st(r, v) or {}).get("p") or vp
                            dash_any += 1
                            if cheb(a["a"], vpos) < cheb(a["f"], vpos): dash_close += 1; dash_rounds.append(r)
            # victim state
            mates = [c for c in g.alive(S, g.team[v]) if c["id"] != v]
            ally_d = min((cheb(c["p"], vp) for c in mates), default=99)
            nf = {k: len(g.near(k, (g.st(k, v) or vs).get("p") or vp, F, 6)) for k in (S - 5, S - 3, S)}
            ne6 = len(g.near(S, vp, g.team[v], 6))  # includes the victim
            att_states = [g.st(S, a) for a in attackers]
            att_states = [c for c in att_states if c and c["al"]]
            att_hp = [c["hp"] / c["mx"] for c in att_states]
            ready_at_S = sum(g.spells_ready(c) for c in att_states)
            dmg_spells_ready = sum(1 for c in att_states for s in (0, 1) if len(c["cd"]) > s and c["cd"][s] == 0 and (g.cname[c["id"]], s) in SPELL_MOD)
            fish6 = g.near(S, vp, F, 6)
            pot6 = sum(g.burst(c) for c in fish6)
            stun_r = sum(1 for r in range(S, E + 1) if (g.st(r, v) or {}).get("stun", 0) > 0)
            per_round = [sum(g.dmg_by[(v, r)][a] for a in attackers) for r in range(S, E + 1)]
            last2 = sum(per_round[-2:]) / max(1, dmg_total)
            maxr = max(per_round) / max(1, vs["hp"])
            minhp = min(((g.st(r, v) or {}).get("hp", 1e9) / vs["mx"]) for r in range(S, L + 2) if (g.st(r, v) or {}).get("al"))
            # opener: the first FOCUS action aimed at the victim in S-3..S (a cast or attack on its tile, or damage)
            opener = None
            for r in range(S - 3, S + 1):
                vpos = (g.st(r, v) or {}).get("p")
                for a in g.acts.get(r, []):
                    if g.team[a["id"]] != F or a["k"] not in (5, 6): continue
                    on_v = (a.get("d") or {}).get(str(v), 0) > 0 or (vpos and a.get("tc") == "c" and a.get("to") and cheb(a["to"], vpos) <= 1)
                    if not on_v: continue
                    nm = g.cname[a["id"]]
                    if a["k"] == 5: kind = "auto"
                    elif (nm, a.get("s")) in DASH and a.get("f") != a.get("a"): kind = "dash"
                    elif (nm, a.get("s")) in CC and (nm, a.get("s")) not in SPELL_MOD: kind = "stun"
                    elif (nm, a.get("s")) in SPELL_MOD: kind = "spell"
                    else: kind = "other"
                    opener = (nm, kind, r); break
                if opener: break
            # peak round and spell timing
            pk = max(range(len(per_round)), key=lambda i: per_round[i]); pr = S + pk
            pk_contrib = len([a for a in attackers if g.dmg_by[(v, pr)].get(a, 0) > 0])
            stun_at_peak = (g.st(pr, v) or {}).get("stun", 0) > 0
            sp_st = sp_all = 0.0; cocast = 0; spell_rounds = collections.defaultdict(set)
            for r in range(S, E + 1):
                vst = (g.st(r, v) or {}).get("stun", 0) > 0
                for a in g.acts.get(r, []):
                    if a["id"] in attackers and a["k"] == 6 and (a.get("d") or {}).get(str(v), 0) > 0:
                        amt = a["d"][str(v)]; sp_all += amt; sp_st += amt if vst else 0; spell_rounds[r].add(a["id"])
            cocast = max((len(x) for x in spell_rounds.values()), default=0)
            gaps = [b - a for a, b in zip(ch, ch[1:])]
            rec = dict(opener=opener, peak_contrib=pk_contrib, peak_frac=round(per_round[pk] / vs["mx"], 2), stun_at_peak=stun_at_peak,
                       spell_dmg_stunned=round(sp_st), spell_dmg=round(sp_all), cocast=cocast, maxgap=max(gaps) if gaps else 0,
                       spell_rounds=len(spell_rounds), game=g.name, gid=g.gid, map=g.map, opp=g.opp_name, v=v, vname=g.cname[v], S=S, L=L, E=E, outcome=outcome,
                       rounds=E - S + 1, nhit=len(ch), attackers=[g.cname[a] for a in attackers], natt=len(attackers),
                       hp0=round(vs["hp"]), mx=vs["mx"], hpf0=round(vs["hp"] / vs["mx"], 3), minhp=round(minhp, 3), dmg=round(dmg_total),
                       auto=round(auto), spell=round(spell), casts=dict(casts), ncast=sum(casts.values()), dash_close=dash_close,
                       dash_any=dash_any, busy=g.busy(v, S), gems=vs["gm"], ally_d=ally_d, nf5=nf[S - 5], nf3=nf[S - 3], nf0=nf[S],
                       ne6=ne6, att_hp=round(sum(att_hp) / max(1, len(att_hp)), 3), ready=ready_at_S, dready=dmg_spells_ready,
                       pot6=round(pot6), pot_ratio=round(pot6 / max(1, vs["hp"]), 2), stun_rounds=stun_r, last2=round(last2, 2),
                       maxround=round(maxr, 2), cast_span=(max(cast_rounds) - min(cast_rounds)) if cast_rounds else None,
                       cast_before_E=[E - r for r in cast_rounds], vdist_spawn=g.spawn_dist(vp, g.team[v]), fdist_spawn=g.spawn_dist(vp, F),
                       killer=g.cname.get(dth["by"]) if dth and dth["bk"] == 1 else None, kk=dth["k"] if dth else None)
            out.write(json.dumps(rec) + "\n")
out.close()
