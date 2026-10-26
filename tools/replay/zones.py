"""Champion-round shares by zone (own half, middle, enemy half: by distance to each side's start tiles, as decoded.py
lives), per side, in round windows: python -I zones.py DIR..."""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
W = [(1, 150), (150, 300), (300, 600), (600, 1000)]
A = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    for r in rows:
        if r['r'] >= 1000: break
        w = next(k for k, (a, b) in enumerate(W) if a <= r['r'] < b)
        for c in r['c']:
            s = D.who(c['t'], us)
            if not c['a'] or 'x' not in c: A[(s, w, 'dead')] += 1; continue
            p = (c['x'], c['y'])
            dm = min(D.dist(p, q) for q in start[c['t']]); de = min(D.dist(p, q) for q in start[1 - c['t']])
            A[(s, w, 'own' if dm < de - 3 else 'enemy' if de < dm - 3 else 'middle')] += 1
print(f'{ng} games: share of champion-rounds by zone (own half / middle / enemy half / dead), each side from its own view')
for w, (a, b) in enumerate(W):
    out = []
    for s in ('us', 'them'):
        t = sum(A[(s, w, z)] for z in ('own', 'middle', 'enemy', 'dead'))
        out.append(f'{s} ' + ' / '.join(f'{A[(s, w, z)] / max(1, t):.2f}' for z in ('own', 'middle', 'enemy', 'dead')))
    print(f'  r{a}-{b}: ' + '   '.join(out))
