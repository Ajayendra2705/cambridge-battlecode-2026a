# engage.py FOCUS OUT.jsonl GAME.json... : contact episodes of team FOCUS's champions (burst/extract.ts output). A contact = champion f of
# FOCUS and enemy champion e within CONTACT (3, Chebyshev) at a round start after 8+ rounds without (both alive). Response over the first
# RESP (3) rounds (S..S+RESP-1); env CONTACT / RESP override (CONTACT=6 RESP=4 = sightings and the decision to close in): "commit" if f dealt damage to any enemy champion (or cast at one), else "hold". Features at S: the enemy's health
# share / busy / gems, f's health share, spells ready (cooldown 0), dash ready, local numbers (FOCUS champions within 6 of e vs e's team
# within 6 of e, both counting the two), the burst potential of FOCUS within 6 / e's health, who drew first blood (e's team damaged a FOCUS
# champion within 6 in S-3..S-1), f on its own half, rounds. Outcomes: e killed within 15 rounds, f died within 15 rounds.
import json, sys, collections
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import Game, cheb, SPELL_MOD, DASH

import os
CONTACT, QUIET, RESP, LOOK = int(os.environ.get("CONTACT", 3)), 8, int(os.environ.get("RESP", 3)), 15
focus, outp, files = sys.argv[1], sys.argv[2], sys.argv[3:]
out = open(outp, "w")
for fpath in files:
    g = Game(fpath, focus)
    if g.focus is None: continue
    F = g.focus
    die = collections.defaultdict(list)
    for d in g.deaths: die[d["v"]].append(d["r"])
    last_contact = {}
    for r in g.rounds:
        if r < 15: continue
        mine = g.alive(r, F); theirs = g.alive(r, 1 - F)
        for f in mine:
            for e in theirs:
                d = cheb(f["p"], e["p"])
                key = (f["id"], e["id"])
                if d > CONTACT: continue
                prev = last_contact.get(key, -99); last_contact[key] = r
                if r - prev <= QUIET: continue
                # response
                commit = False; first_hit = None; cast_any = 0
                for rr in range(r, r + RESP):
                    for a in g.acts.get(rr, []):
                        if a["id"] != f["id"]: continue
                        dd = a.get("d") or {}
                        if any(amt > 0 and g.team[int(v)] != F for v, amt in dd.items()) or (a["k"] == 6 and a.get("tc") == "c"):
                            commit = True; first_hit = rr if first_hit is None else first_hit
                    if commit: break
                hit_e = any(g.dmg_by[(e["id"], rr)].get(f["id"], 0) > 0 for rr in range(r, r + RESP))
                camp = any(a["id"] == f["id"] and a.get("tc") == "m" for rr in range(r, r + RESP) for a in g.acts.get(rr, []))
                nf = g.near(r, e["p"], F, 6); ne = g.near(r, e["p"], 1 - F, 6)
                nf_f = g.near(r, f["p"], F, 6); ne_f = g.near(r, f["p"], 1 - F, 6)
                pot = sum(g.burst(c) for c in nf)
                pot_e = sum(g.burst(c) for c in ne)  # their burst on us
                fhp_sum = sum(c["hp"] for c in nf); ehp_sum = sum(c["hp"] for c in ne)
                fn = g.cname[f["id"]]
                ready = [s for s in (0, 1) if len(f["cd"]) > s and f["cd"][s] == 0]
                first_blood = any(g.dmg_by[(c["id"], rr)].get(x, 0) > 0 for rr in range(r - 3, r) for c in nf for x in g.dmg_by[(c["id"], rr)] if g.team[x] != F)
                own_half = g.spawn_dist(f["p"], F) < g.spawn_dist(f["p"], 1 - F)
                ekill = any(r <= x <= r + LOOK for x in die[e["id"]]) and any(g.dmg_by[(e["id"], rr)] and any(g.team[a] == F for a in g.dmg_by[(e["id"], rr)]) for rr in range(r, r + LOOK))
                fdie = any(r <= x <= r + LOOK for x in die[f["id"]])
                out.write(json.dumps(dict(game=g.name, gid=g.gid, r=r, f=fn, e=g.cname[e["id"]], d=d, commit=commit, hit_e=hit_e, camp=camp,
                    ehp=round(e["hp"] / e["mx"], 3), ehp_abs=round(e["hp"]), fhp=round(f["hp"] / f["mx"], 3), ebusy=g.busy(e["id"], r), egems=e["gm"],
                    fgems=f["gm"], ready=len(ready), dmg_ready=sum(1 for s in ready if (fn, s) in SPELL_MOD), dash_ready=any((fn, s) in DASH for s in ready),
                    nf=len(nf), ne=len(ne), nf_f=len(nf_f), ne_f=len(ne_f), pot=round(pot), pot_ratio=round(pot / max(1, e["hp"]), 2),
                    pot_e=round(pot_e), hp_ratio=round(fhp_sum / max(1, ehp_sum), 2), first_blood=first_blood, own_half=own_half,
                    ekill=ekill, fdie=fdie, estr=e["st"], fstr=f["st"], emx=e["mx"], fmx=f["mx"])) + "\n")
out.close()
