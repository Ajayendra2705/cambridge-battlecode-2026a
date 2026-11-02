"""Per map: Bamboo line against the bot_10 line within the same opponent, from data/draftline.json (run draftline.py first).

usage: python -I tools/platform/mapstrat.py [--min-w W]

For each (map, opponent) played by both lines, the difference of win rates, weighted by the harmonic mean of the two game counts; per map the
weighted mean difference and its standard error (binomial, with a floor on each rate so that 0 of 5 does not count as certain). Maps are sorted by the difference
divided by its error. Ranked and unranked games are pooled. Picks: the size of the draft. The last lines give the sum over maps by near and far (data/map_features.json, sd >= 61).
"""
import collections, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data = json.load(open(os.path.join(ROOT, 'data', 'draftline.json'), encoding='utf-8'))
feat = json.load(open(os.path.join(ROOT, 'data', 'map_features.json'), encoding='utf-8'))
feat = {(x.get('name') or x.get('map')).replace('-', '_'): x for x in feat}
minw = float(sys.argv[sys.argv.index('--min-w') + 1]) if '--min-w' in sys.argv else 8.0
T = collections.defaultdict(lambda: collections.defaultdict(lambda: {'bamboo': [0, 0], 'b10': [0, 0]}))
size = {}
for kind, ms in data.items():
    for m in ms:
        us = [x for x in m['teams'] if x['name'] == 'Velvet Tributers']
        if not us or us[0]['result'] is None: continue
        us = us[0]
        op = [x for x in m['teams'] if x is not us][0]['name']
        p = us['draftPicks']
        line = 'bamboo' if 0 in p else 'b10' if 11 in p else None
        if not line: continue
        c = T[m['map']][op][line]
        c[0] += us['result'] == 'win'; c[1] += 1
        size[m['map']] = len(p)
rows = []
for mp, ops in T.items():
    W = D = V = 0.0
    bw = bn = vw = vn = nops = 0
    for op, c in ops.items():
        a, b = c['bamboo'], c['b10']
        if not a[1] or not b[1]: continue
        w = 2 * a[1] * b[1] / (a[1] + b[1])
        ra, rb = a[0] / a[1], b[0] / b[1]
        # Shrunk rates for the variance: a rate of 0 or 1 on few games is not certain.
        sa, sb = (a[0] + 1) / (a[1] + 2), (b[0] + 1) / (b[1] + 2)
        v = sa * (1 - sa) / a[1] + sb * (1 - sb) / b[1]
        W += w; D += w * (ra - rb); V += w * w * v
        bw += a[0]; bn += a[1]; vw += b[0]; vn += b[1]; nops += 1
    if W <= 0: continue
    d, se = D / W, math.sqrt(V) / W
    f = feat.get(mp) or {}
    rows.append((d / se if se else 0, mp, d, se, W, nops, bw, bn, vw, vn, f.get('sd', -1)))
print('map                      picks walk | bamboo-b10 within opponent (+- se)   z    weight opponents | bamboo    b10')
near = [0.0, 0.0, 0.0]; far = [0.0, 0.0, 0.0]
for z, mp, d, se, W, nops, bw, bn, vw, vn, sd in sorted(rows, reverse=True):
    print(f'{mp:24} {size[mp]:3} {sd:6} | {100 * d:+5.0f}% +- {100 * se:3.0f}% {z:+5.1f} {W:7.1f} {nops:3} | {bw:3}/{bn:<3} {vw:3}/{vn:<3}' + ('' if W >= minw else '  (thin)'))
    t = far if sd >= 61 else near
    t[0] += W * d; t[1] += W; t[2] += (W * se) ** 2
for name, t in (('near', near), ('far', far)):
    if t[1]: print(f'{name}: {100 * t[0] / t[1]:+.1f}% +- {100 * math.sqrt(t[2]) / t[1]:.1f}% (weight {t[1]:.0f})')
