"""What follows a cast near enemy champions: python -I castfate.py [--r R] DIR...  Per side, champion type and slot: casts with an enemy champion within 6 after the cast, per game; self dies within 10 rounds; enemies within 8 die within 10; number of allies and enemies within 6."""
import collections, os, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
args = sys.argv[1:]
RMAX = 1000
if '--r' in args:
    k = args.index('--r'); RMAX = int(args[k + 1]); del args[k:k + 2]
A = collections.defaultdict(collections.Counter)
G = collections.Counter()
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    types = set()
    for c in rows[0]['c']:
        types.add((D.who(c['t'], us), c['ty']))
    for t in types:
        G[t] += 1
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > RMAX:
            break
        for i, c in enumerate(a['c']):
            if not c['a'] or 'x' not in c or i >= len(a['act']):
                continue
            for x in a['act'][i]:
                if x[0] != 'cast':
                    continue
                b = rows[k + 1]['c'][i]
                p = (b['x'], b['y']) if 'x' in b else (c['x'], c['y'])
                foes = [o for o in a['c'] if o['t'] != c['t'] and o['a'] and 'x' in o and D.dist(p, (o['x'], o['y'])) <= 6]
                if not foes:
                    continue
                al = [o for o in a['c'] if o['t'] == c['t'] and o['a'] and 'x' in o and o is not c and D.dist(p, (o['x'], o['y'])) <= 6]
                key = (D.who(c['t'], us), c['ty'], x[1], 'target' if len(x) > 4 else 'tile')
                s = A[key]
                s['n'] += 1
                s['self'] += any(not rows[k + t]['c'][i]['a'] for t in range(1, 11))
                s['kills'] += sum(1 for j in range(n) if a['c'][j]['t'] != c['t'] and a['c'][j]['a'] and 'x' in a['c'][j] and D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) <= 8 and any(not rows[k + t]['c'][j]['a'] for t in range(1, 11)))
                s['al'] += len(al); s['en'] += len(foes)
                d0 = D.dist((c['x'], c['y']), p)
                s['moved'] += d0 >= 2
for key in sorted(A, key=lambda z: (z[1], z[2], z[3], z[0])):
    s = A[key]; m = max(1, s['n'])
    print(f"{D.NAMES[key[1]][:8]:8} slot {key[2]} {key[3]:6} {key[0]:4} games {G[(key[0], key[1])]:3} casts/game {s['n'] / max(1, G[(key[0], key[1])]):5.1f}  self dies {s['self'] / m:.2f}  enemies die {s['kills'] / m:.2f}  allies {s['al'] / m:.1f} enemies {s['en'] / m:.1f}  jumped {s['moved'] / m:.2f}")
