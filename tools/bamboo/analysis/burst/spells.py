# spells.py LABEL=FOCUS:GLOB ... : spell discipline and focus fire of team FOCUS (burst/extract.ts output), by round band.
#  ready-in-range: champion-rounds with a damaging spell ready (cooldown 0) and an enemy champion within 4 at the round start (not stunned,
#    alive): share that cast it at a champion that round, split by the nearest enemy's health share and whether that enemy died within 5.
#  first cast delay: after a damaging spell became ready-in-range, rounds until it was cast at a champion (cap 10).
#  focus fire: rounds in which 2+ FOCUS champions damaged enemy champions - all on one target vs split; and when split, whether a common
#    target was within reach of both (Chebyshev <= 4 from both at the round start).
#  sync: damaging-spell casts on a champion that land in a round where another FOCUS champion also damages that champion (same round), or
#    within +-1 round; and the share followed by that champion's death within 3 rounds.
#  stun-then-damage: of damaging spell damage on champions, the share dealt to a target stunned at the round start.
import json, sys, glob, collections
sys.path.insert(0, __import__("os").path.dirname(__file__))
from common import Game, cheb, SPELL_MOD, CC

BANDS = [(0, 400, "r<400"), (400, 800, "r400-800"), (800, 9999, "r800+")]


def band(r):
    return next(l for a, b, l in BANDS if a <= r < b)


for arg in sys.argv[1:]:
    lab, spec = arg.split("=", 1)
    focus, pat = spec.split(":", 1)
    files = sorted(glob.glob(pat))
    names = focus.split(",")
    S = collections.defaultdict(collections.Counter)
    ngames = 0
    for fp in files:
        for nm_team in names:
            g = Game(fp, nm_team)
            if g.focus is None: continue
            ngames += 1
            F = g.focus
            die = collections.defaultdict(list)
            for d in g.deaths: die[d["v"]].append(d["r"])
            pending = {}  # (cid, slot) -> round it became ready-in-range
            for r in g.rounds:
                if r < 15: continue
                b = band(r)
                en = g.alive(r, 1 - F)
                for c in g.alive(r, F):
                    if c["stun"]: continue
                    nm = g.cname[c["id"]]
                    near = [e for e in en if cheb(e["p"], c["p"]) <= 4]
                    for s in (0, 1):
                        if (nm, s) not in SPELL_MOD: continue
                        ready = len(c["cd"]) > s and c["cd"][s] == 0
                        key = (c["id"], s)
                        if not (ready and near):
                            pending.pop(key, None); continue
                        cast = any(a["id"] == c["id"] and a["k"] == 6 and a.get("s") == s and (a.get("tc") == "c" or any(x > 0 and g.team[int(k)] != F for k, x in (a.get("d") or {}).items())) for a in g.acts.get(r, []))
                        tgt = min(near, key=lambda e: e["hp"] / e["mx"])
                        hb = "low<50" if tgt["hp"] / tgt["mx"] < 0.5 else "high>=50"
                        dies = any(r <= x <= r + 5 for x in die[tgt["id"]])
                        S[b]["rr"] += 1; S[b]["rr_cast"] += cast
                        S[b]["rr_" + hb] += 1; S[b]["rr_cast_" + hb] += cast
                        S[b]["rr_dies" if dies else "rr_lives"] += 1; S[b]["rr_cast_dies" if dies else "rr_cast_lives"] += cast
                        if key not in pending: pending[key] = r
                        if cast:
                            S[b]["delay_n"] += 1; S[b]["delay_sum"] += min(10, r - pending[key]); S[b]["delay0"] += (r == pending[key])
                            pending.pop(key, None)
                # focus fire
                att = collections.defaultdict(set)
                for a in g.acts.get(r, []):
                    if g.team[a["id"]] != F: continue
                    for k, x in (a.get("d") or {}).items():
                        if x > 0 and g.team[int(k)] != F: att[a["id"]].add(int(k))
                if len(att) >= 2:
                    S[b]["ff_rounds"] += 1
                    tg = set().union(*att.values())
                    if len(tg) == 1: S[b]["ff_one"] += 1
                    else:
                        S[b]["ff_split"] += 1
                        # could they have shared a target?
                        pos = {c["id"]: c["p"] for c in g.alive(r, F)}
                        common = [e for e in en if all(cheb(e["p"], pos[a]) <= 4 for a in att if a in pos)]
                        S[b]["ff_split_common"] += bool(common)
                # spell sync on champion targets
                for a in g.acts.get(r, []):
                    if g.team[a["id"]] != F or a["k"] != 6: continue
                    for k, x in (a.get("d") or {}).items():
                        v = int(k)
                        if x <= 0 or g.team[v] == F: continue
                        S[b]["sp_casts"] += 1; S[b]["sp_dmg"] += x
                        others = [o for o in g.dmg_by[(v, r)] if o != a["id"] and g.team[o] == F]
                        others1 = [o for rr in (r - 1, r, r + 1) for o in g.dmg_by[(v, rr)] if o != a["id"] and g.team[o] == F]
                        S[b]["sp_same_round"] += bool(others); S[b]["sp_pm1"] += bool(others1)
                        S[b]["sp_kill3"] += any(r <= y <= r + 3 for y in die[v])
                        vs = g.st(r, v) or {}
                        if vs.get("stun"): S[b]["sp_dmg_stunned"] += x
                        S[b]["sp_hpfrac"] += x / max(1, vs.get("mx", 1))
                # all champion damage while stunned
                for a in g.acts.get(r, []):
                    if g.team[a["id"]] != F: continue
                    for k, x in (a.get("d") or {}).items():
                        v = int(k)
                        if x > 0 and g.team[v] != F:
                            S[b]["all_dmg"] += x
                            if (g.st(r, v) or {}).get("stun"): S[b]["all_dmg_stunned"] += x
    print(f"== {lab} ({focus}): team-games {ngames}")
    for _, _, b in BANDS:
        c = S[b]
        if not c["rr"]: continue
        pc = lambda a, n: f"{100 * c[a] / max(1, c[n]):.0f}%"
        print(f"  {b}: dmg-spell ready with enemy within 4: {c['rr']} champion-rounds, cast at a champion {pc('rr_cast', 'rr')} "
              f"(nearest-low target <50%: {pc('rr_cast_low<50', 'rr_low<50')}, >=50%: {pc('rr_cast_high>=50', 'rr_high>=50')}; target dies in 5: {pc('rr_cast_dies', 'rr_dies')}, lives: {pc('rr_cast_lives', 'rr_lives')}); "
              f"first-cast delay {c['delay_sum'] / max(1, c['delay_n']):.2f} rounds, cast in the first ready round {pc('delay0', 'delay_n')}")
        print(f"     focus fire: rounds with 2+ hitters {c['ff_rounds']} ({c['ff_rounds'] / ngames:.1f}/game), one target {pc('ff_one', 'ff_rounds')}, split {pc('ff_split', 'ff_rounds')} "
              f"(split although a common target was within 4 of all: {pc('ff_split_common', 'ff_split')})")
        print(f"     spell hits on champions {c['sp_casts']} ({c['sp_casts'] / ngames:.1f}/game, mean {c['sp_dmg'] / max(1, c['sp_casts']):.0f} dmg = {100 * c['sp_hpfrac'] / max(1, c['sp_casts']):.0f}% of target max): "
              f"another teammate hit the same target that round {pc('sp_same_round', 'sp_casts')}, within +-1 {pc('sp_pm1', 'sp_casts')}; target died within 3 {pc('sp_kill3', 'sp_casts')}; "
              f"spell dmg on stunned targets {100 * c['sp_dmg_stunned'] / max(1, c['sp_dmg']):.0f}%, all dmg on stunned {100 * c['all_dmg_stunned'] / max(1, c['all_dmg']):.0f}%")
