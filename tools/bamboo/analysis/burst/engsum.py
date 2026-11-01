# engsum.py LABEL=EN.jsonl ... : commit rates of engage.py contacts by feature bucket, side by side; then two-feature grids.
import json, sys, collections

sets = [(a.split("=", 1)[0], [json.loads(l) for l in open(a.split("=", 1)[1])]) for a in sys.argv[1:]]


def b(x, edges):
    for lo, hi, lab in edges:
        if lo <= x < hi: return lab
    return "?"


SPECS = [
    ("champion f", lambda e: e["f"]),
    ("enemy hp share", lambda e: b(e["ehp"], [(0, .35, "a<35"), (.35, .6, "b35-60"), (.6, .85, "c60-85"), (.85, 9, "d>=85")])),
    ("f hp share", lambda e: b(e["fhp"], [(0, .35, "a<35"), (.35, .6, "b35-60"), (.6, .85, "c60-85"), (.85, 9, "d>=85")])),
    ("numbers nf-ne (around e)", lambda e: max(-2, min(2, e["nf"] - e["ne"]))),
    ("numbers around f", lambda e: max(-2, min(2, e["nf_f"] - e["ne_f"]))),
    ("pot / enemy hp", lambda e: b(e["pot_ratio"], [(0, .35, "a<.35"), (.35, .6, "b.35-.6"), (.6, 1, "c.6-1"), (1, 99, "d>=1")])),
    ("hp sum ratio (6 of e)", lambda e: b(e["hp_ratio"], [(0, .67, "a<.67"), (.67, 1, "b.67-1"), (1, 1.5, "c1-1.5"), (1.5, 99, "d>=1.5")])),
    ("f spells ready", lambda e: e["ready"]),
    ("f dmg spell ready", lambda e: e["dmg_ready"]),
    ("enemy busy", lambda e: e["ebusy"]),
    ("enemy carries gems", lambda e: "gems>0" if e["egems"] > 0 else "none"),
    ("first blood by them", lambda e: e["first_blood"]),
    ("f on own half", lambda e: e["own_half"]),
    ("round", lambda e: b(e["r"], [(0, 150, "a<150"), (150, 400, "b150-400"), (400, 800, "c400-800"), (800, 9999, "d800+")])),
    ("distance", lambda e: e["d"]),
]


def line(E):
    n = len(E); c = sum(1 for e in E if e["commit"])
    k = sum(1 for e in E if e["commit"] and e["ekill"]); dd = sum(1 for e in E if e["commit"] and e["fdie"])
    return f"{c:4d}/{n:4d} {100 * c / max(1, n):3.0f}% k{100 * k / max(1, c):3.0f}% d{100 * dd / max(1, c):3.0f}%"


for lab, E in sets:
    n = len(E); c = sum(1 for e in E if e["commit"])
    print(f"== {lab}: contacts {n}, commit {100 * c / n:.0f}%; after commit e killed {100 * sum(1 for e in E if e['commit'] and e['ekill']) / max(1, c):.0f}%, "
          f"f died {100 * sum(1 for e in E if e['commit'] and e['fdie']) / max(1, c):.0f}%; after hold e killed {100 * sum(1 for e in E if not e['commit'] and e['ekill']) / max(1, n - c):.0f}%, "
          f"f died {100 * sum(1 for e in E if not e['commit'] and e['fdie']) / max(1, n - c):.0f}%; hold->camp {100 * sum(1 for e in E if not e['commit'] and e['camp']) / max(1, n - c):.0f}%")
print("(cells: commits/contacts commit% | k = enemy killed within 15 after a commit | d = f died within 15 after a commit)")
for name, fn in SPECS:
    print(f"  {name}")
    keys = sorted({fn(e) for _, E in sets for e in E}, key=str)
    for k in keys:
        print(f"    {str(k):10s}" + "".join(f"  {lab}: {line([e for e in E if fn(e) == k])}" for lab, E in sets))
# grids
print("\nGRID numbers around e (rows) x enemy hp share (cols): commit%  (n)")
rows = [-2, -1, 0, 1, 2]
cols = ["a<35", "b35-60", "c60-85", "d>=85"]
for lab, E in sets:
    print(f"  {lab}")
    print("        " + "".join(f"{c:>14s}" for c in cols))
    for rw in rows:
        s = f"    {rw:3d} "
        for cl in cols:
            EE = [e for e in E if max(-2, min(2, e["nf"] - e["ne"])) == rw and SPECS[1][1](e) == cl]
            c = sum(1 for e in EE if e["commit"])
            s += f"{(100 * c / len(EE)) if EE else 0:8.0f}%({len(EE):3d})"
        print(s)
print("\nGRID pot/enemy hp (rows) x f hp (cols): commit% (n)")
for lab, E in sets:
    print(f"  {lab}")
    for rw in ["a<.35", "b.35-.6", "c.6-1", "d>=1"]:
        s = f"    {rw:8s} "
        for cl in cols:
            EE = [e for e in E if SPECS[5][1](e) == rw and SPECS[2][1](e) == cl]
            c = sum(1 for e in EE if e["commit"])
            s += f"{(100 * c / len(EE)) if EE else 0:8.0f}%({len(EE):3d})"
        print(s)
