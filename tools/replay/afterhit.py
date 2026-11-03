"""What a champion does in the round after it is hit, in detail: python -I afterhit.py RMAX DIR..."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
RM = int(sys.argv[1])
A = collections.defaultdict(collections.Counter)
ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    for k in range(len(rows) - 2):
        a = rows[k]
        if a['r'] > RM:
            break
        victims = {}
        for h in range(n):
            for x in D.enemy_hits(a, h, n):
                victims.setdefault(x[-1], h)
        for v, h in victims.items():
            vc, hc = a['c'][v], a['c'][h]
            b = rows[k + 1]
            vb = b['c'][v]
            if not (vc['a'] and vb['a'] and hc['a'] and 'x' in vc and 'x' in hc and 'x' in vb):
                continue
            d0 = D.dist((vc['x'], vc['y']), (hc['x'], hc['y']))
            d1 = D.dist((vb['x'], vb['y']), (hc['x'], hc['y']))
            acts = b['act'][v] if v < len(b['act']) else []
            kinds = {x[0] for x in acts}
            if D.enemy_hits(b, v, n):
                w = 'hit champion'
            elif D.camp_hits(b, v):
                w = 'hit camp'
            elif 'move' in kinds:
                w = 'away' if d1 > d0 else 'closer' if d1 < d0 else 'beside'
            elif kinds:
                w = 'cast or other'
            else:
                w = 'still'
            side = D.who(vc['t'], us)
            ty = D.NAMES[vc['ty']]
            R = D.RANGE[hc['ty']]
            A[(side, 'all', 'mel' if R == 1 else 'rng')][w] += 1
            A[(side, 'all', 'mel' if R == 1 else 'rng')]['n'] += 1
            A[(side, ty, 'mel' if R == 1 else 'rng')][w] += 1
            A[(side, ty, 'mel' if R == 1 else 'rng')]['n'] += 1
W = ['hit champion', 'hit camp', 'away', 'closer', 'beside', 'cast or other', 'still']
print(ng, 'games:', ' | '.join(W))
for key in sorted(A, key=lambda k: (k[1] != 'all', k[1], k[2], k[0])):
    s = A[key]; m = max(1, s['n'])
    if s['n'] < 150:
        continue
    print(f"{key[1]:9} {key[2]} {key[0]:4} {s['n']/ng:6.1f} " + ' '.join(f"{s[w]/m:.2f}" for w in W))
