"""Per-map gains of screened variants against one base: python -I tools/local/armscan.py OUT.json BASE CAND@RUN_DIR [CAND@RUN_DIR ...]

RUN_DIR holds the candidate's games and hard links to the base's (tools/local/screen.sh). For each map and candidate: games, base gold at r300, gain, wins base / candidate, margin difference. Writes the table to OUT.json and prints
the entries with gain at least +100 and at least 8% of the base and wins not below the base's.
"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lgold2 import at
out, base = sys.argv[1], sys.argv[2]
T = collections.defaultdict(dict)


def load(path, R=300):
    b, o, m, s = os.path.basename(path)[:-5].split('~')
    j = json.load(open(path, encoding='utf-8'))
    us = 'team' + s
    gold = sum(at(t['runs'], R) for t in j['championTimelines'] if t['metric'] == 'earnedGold' and t['owner'].get('team') == us)
    sub = {t['team']: int(t['submittedGems']) for t in j['teams']}
    return (o, m, s), (gold, float(j['match']['outcome'] == us), sum(v if k == us else -v for k, v in sub.items()))


for spec in sys.argv[3:]:
    cand, run = spec.split('@')
    B, C = {}, {}
    for f in glob.glob(os.path.join(run, '*.json')):
        n = os.path.basename(f).split('~')[0]
        if n not in (base, cand):
            continue
        try:
            k, v = load(f)
        except Exception:
            continue
        (B if n == base else C)[k] = v
    M = collections.defaultdict(list)
    for k, v in C.items():
        if k in B:
            M[k[1]].append((B[k], v))
    for mp, xs in M.items():
        n = len(xs)
        T[mp][cand] = dict(n=n, base=round(sum(x[0][0] for x in xs) / n), gain=round(sum(x[1][0] - x[0][0] for x in xs) / n, 1), wb=sum(x[0][1] for x in xs), wc=sum(x[1][1] for x in xs),
                           margin=round(sum(x[1][2] - x[0][2] for x in xs) / n, 1))
json.dump(T, open(out, 'w', encoding='utf-8'))
for mp, row in sorted(T.items()):
    good = [(c, v) for c, v in row.items() if v['gain'] >= 100 and v['gain'] >= 0.08 * v['base'] and v['wc'] >= v['wb']]
    if good:
        print(mp, 'base', list(row.values())[0]['base'], ' '.join(f"{c}:{v['gain']:+.0f},{v['wb']:.0f}/{v['wc']:.0f},{v['margin']:+.0f}" for c, v in sorted(good, key=lambda z: -z[1]['gain'])))
