# killsum.py LABEL=EP.jsonl ... : side-by-side summary of kills.py episodes (kills vs escapes) for each labelled file.
import json, sys, collections, statistics as stt


def load(p):
    return [json.loads(l) for l in open(p)]


sets = [(a.split("=", 1)[0], load(a.split("=", 1)[1])) for a in sys.argv[1:]]
games = {lab: len({e["gid"] for e in E}) for lab, E in sets}


def med(xs):
    xs = [x for x in xs if x is not None]
    return f"{stt.median(xs):.2f}" if xs else "-"


def share(xs, pred):
    xs = list(xs)
    return f"{100 * sum(1 for x in xs if pred(x)) / max(1, len(xs)):.0f}%"


def bucket(x, edges):
    for lo, hi, lab in edges:
        if lo <= x < hi: return lab
    return "?"


def row(name, fn):
    print(f"{name:42s}" + "".join(f"{fn(E):>16s}" for E in cols))


for lab, E in sets:
    K = [e for e in E if e["outcome"] == "kill"]
    X = [e for e in E if e["outcome"] == "escaped"]
    print(f"== {lab}: games {games[lab]}  kills {len(K)} ({len(K) / games[lab]:.1f}/game)  escapes {len(X)}  kill share of episodes {100 * len(K) / max(1, len(K) + len(X)):.0f}%")
cols = []
for lab, E in sets:
    cols.append([e for e in E if e["outcome"] == "kill"])
    cols.append([e for e in E if e["outcome"] == "escaped"])
print(f"{'':42s}" + "".join(f"{lab + ' ' + k:>16s}" for lab, _ in sets for k in ("kill", "esc")))
row("episodes", lambda E: str(len(E)))
row("rounds S..E median", lambda E: med([e["rounds"] for e in E]))
row("rounds <=2", lambda E: share(E, lambda e: e["rounds"] <= 2))
row("rounds 3-5", lambda E: share(E, lambda e: 3 <= e["rounds"] <= 5))
row("rounds 6-10", lambda E: share(E, lambda e: 6 <= e["rounds"] <= 10))
row("rounds >10", lambda E: share(E, lambda e: e["rounds"] > 10))
row("attackers mean", lambda E: f"{sum(e['natt'] for e in E) / max(1, len(E)):.2f}")
row("attackers 1 / 2 / 3+", lambda E: "/".join(share(E, lambda e, k=k: (e['natt'] == k if k < 3 else e['natt'] >= 3)) for k in (1, 2, 3)))
row("victim hp/max at S median", lambda E: med([e["hpf0"] for e in E]))
row("victim hp at S <35%", lambda E: share(E, lambda e: e["hpf0"] < 0.35))
row("victim hp at S 35-70%", lambda E: share(E, lambda e: 0.35 <= e["hpf0"] < 0.7))
row("victim hp at S >=70%", lambda E: share(E, lambda e: e["hpf0"] >= 0.7))
row("victim min hp in window median", lambda E: med([e["minhp"] for e in E]))
row("dmg dealt / victim hp at S median", lambda E: med([e["dmg"] / max(1, e["hp0"]) for e in E]))
row("spell share of damage", lambda E: f"{100 * sum(e['spell'] for e in E) / max(1, sum(e['spell'] + e['auto'] for e in E)):.0f}%")
row("casts per episode", lambda E: f"{sum(e['ncast'] for e in E) / max(1, len(E)):.2f}")
row("closing dash in S-2..E", lambda E: share(E, lambda e: e["dash_close"] > 0))
row("stunned >=1 round in window", lambda E: share(E, lambda e: e["stun_rounds"] > 0))
row("dmg share in last 2 rounds", lambda E: med([e["last2"] for e in E]))
row("max 1-round dmg / hp at S", lambda E: med([e["maxround"] for e in E]))
row("victim ally dist median", lambda E: med([min(e["ally_d"], 30) for e in E]))
row("victim ally dist >=6", lambda E: share(E, lambda e: e["ally_d"] >= 6))
row("victim ally dist <=2", lambda E: share(E, lambda e: e["ally_d"] <= 2))
row("focus within 6 at S-5 mean", lambda E: f"{sum(e['nf5'] for e in E) / max(1, len(E)):.2f}")
row("focus within 6 at S-3 mean", lambda E: f"{sum(e['nf3'] for e in E) / max(1, len(E)):.2f}")
row("focus within 6 at S mean", lambda E: f"{sum(e['nf0'] for e in E) / max(1, len(E)):.2f}")
row("focus within 6 at S >=2", lambda E: share(E, lambda e: e["nf0"] >= 2))
row("victim side within 6 (incl) mean", lambda E: f"{sum(e['ne6'] for e in E) / max(1, len(E)):.2f}")
row("numbers nf0 > ne6", lambda E: share(E, lambda e: e["nf0"] > e["ne6"]))
row("numbers nf0 == ne6", lambda E: share(E, lambda e: e["nf0"] == e["ne6"]))
row("numbers nf0 < ne6", lambda E: share(E, lambda e: e["nf0"] < e["ne6"]))
row("burst pot(6)/victim hp median", lambda E: med([e["pot_ratio"] for e in E]))
row("burst pot(6)/victim hp >= 1", lambda E: share(E, lambda e: e["pot_ratio"] >= 1))
row("attackers' hp share at S", lambda E: med([e["att_hp"] for e in E]))
row("attackers' dmg spells ready at S", lambda E: f"{sum(e['dready'] for e in E) / max(1, len(E)):.2f}")
row("victim carrying gems >0", lambda E: share(E, lambda e: e["gems"] > 0))
row("victim gems mean", lambda E: f"{sum(e['gems'] for e in E) / max(1, len(E)):.1f}")
for b in ("recall", "tribute", "crystal", "camp", "fighting", "walking", "idle"):
    row(f"victim busy: {b}", lambda E, b=b: share(E, lambda e: e["busy"] == b))
row("victim nearer own spawn than focus's", lambda E: share(E, lambda e: e["vdist_spawn"] < e["fdist_spawn"]))
print()
for lab, E in sets:
    K = [e for e in E if e["outcome"] == "kill"]
    print(f"-- {lab} kills: victim types", dict(collections.Counter(e["vname"] for e in K).most_common()))
    print(f"   attacker types (share of kills involving)", {k: f"{100 * v / len(K):.0f}%" for k, v in collections.Counter(n for e in K for n in set(e["attackers"])).most_common()})
    print(f"   killing blow", dict(collections.Counter(e["killer"] for e in K).most_common()))
    print(f"   killing-blow step kind (5 auto, 6 cast)", dict(collections.Counter(e["kk"] for e in K)))
    print(f"   casts in kill windows", dict(collections.Counter(k for e in K for k, v in e["casts"].items() for _ in range(v)).most_common()))
    print(f"   attacker combos", dict(collections.Counter("+".join(sorted(e["attackers"])) for e in K).most_common(12)))
    cb = [x for e in K for x in e["cast_before_E"]]
    print(f"   cast timing (rounds before death) 0:{share(cb, lambda x: x == 0)} 1:{share(cb, lambda x: x == 1)} 2:{share(cb, lambda x: x == 2)} 3-5:{share(cb, lambda x: 3 <= x <= 5)} 6+:{share(cb, lambda x: x >= 6)} (n {len(cb)})")
    print()
# conversion by bucket
print("conversion (kill / (kill + escaped)) by bucket")
specs = [
    ("focus within 6 at S", lambda e: min(e["nf0"], 4)),
    ("numbers nf0 - ne6", lambda e: max(-2, min(2, e["nf0"] - e["ne6"]))),
    ("victim hp at S", lambda e: bucket(e["hpf0"], [(0, .35, "<35"), (.35, .7, "35-70"), (.7, 9, ">=70")])),
    ("pot ratio", lambda e: bucket(e["pot_ratio"], [(0, .5, "<0.5"), (.5, 1, "0.5-1"), (1, 2, "1-2"), (2, 99, ">=2")])),
    ("victim busy", lambda e: e["busy"]),
    ("victim ally dist", lambda e: bucket(e["ally_d"], [(0, 3, "<=2"), (3, 6, "3-5"), (6, 999, ">=6")])),
    ("attackers", lambda e: min(e["natt"], 3)),
]
for name, fn in specs:
    print(f"  {name}")
    keys = sorted({fn(e) for _, E in sets for e in E}, key=str)
    for k in keys:
        line = f"    {str(k):10s}"
        for lab, E in sets:
            EE = [e for e in E if e["outcome"] in ("kill", "escaped") and fn(e) == k]
            nk = sum(1 for e in EE if e["outcome"] == "kill")
            line += f"  {lab}: {nk:4d}/{len(EE):4d} {100 * nk / max(1, len(EE)):3.0f}%"
        print(line)
