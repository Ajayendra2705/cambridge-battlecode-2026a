"""Earned gold per map, one candidate against a base: python -I tools/local/lgoldmap.py RUN_DIR BASE_CAND CAND [ROUND] [TYPE]

Reads a multi.py run like lgold2.py. For each map: mean team gold of the base, the paired difference at ROUND (default 150), the difference of the gold of champion
type TYPE when given, and the games. Sorted by the difference. The last line gives the same split by map size of spawn walk (data/map_features.json `sd`, near under 61).
"""
import collections, glob, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lgold2 import at
run, base, cand = sys.argv[1], sys.argv[2], sys.argv[3]
R = int(sys.argv[4]) if len(sys.argv) > 4 else 150
TY = sys.argv[5] if len(sys.argv) > 5 else None


def load(path):
    b, o, m, s = os.path.basename(path)[:-5].split('~')
    d = json.load(open(path, encoding='utf-8'))
    team = 'team' + s
    t0 = 0.0
    t1 = 0.0
    for t in d['championTimelines']:
        if t['metric'] != 'earnedGold' or t['owner'].get('team') != team:
            continue
        v = at(t['runs'], R)
        t0 += v
        if TY and t['owner'].get('name') == TY:
            t1 += v
    return b, (o, m, s), (t0, t1)


G = collections.defaultdict(dict)
for f in glob.glob(os.path.join(run, '*.json')):
    if os.path.basename(f).split('~')[0] not in (base, cand):
        continue
    try:
        b, k, v = load(f)
    except Exception:
        continue
    G[b][k] = v
M = collections.defaultdict(list)
for k, v in G[cand].items():
    if k in G[base]:
        M[k[1]].append((G[base][k][0], v[0] - G[base][k][0], v[1] - G[base][k][1]))
rows = []
for mp, xs in M.items():
    n = len(xs)
    rows.append((sum(x[1] for x in xs) / n, mp, n, sum(x[0] for x in xs) / n, sum(x[2] for x in xs) / n))
print(f'{cand} - {base}: team gold at r{R} per map')
for d, mp, n, b, t in sorted(rows):
    print(f'{mp:24} n{n:2} base {b:6.0f} diff {d:+7.1f}' + (f' {TY[:6]} {t:+6.1f}' if TY else ''))
feat = {(x.get('name') or x.get('map')).replace('-', '_'): x for x in json.load(open('data/map_features.json', encoding='utf-8'))}
for label, f in (('near', lambda sd: 0 <= sd < 61), ('far', lambda sd: sd >= 61)):
    xs = [x[1] for mp, v in M.items() if f(feat.get(mp.replace('-', '_'), {}).get('sd', -1)) for x in v]
    if xs:
        m = sum(xs) / len(xs)
        print(f'{label}: {len(xs)} games, {m:+.1f} +- {math.sqrt(sum((x - m) ** 2 for x in xs) / max(1, len(xs) - 1) / len(xs)):.1f}')
