# Per champion type, to R (default 600): rounds dead, hitting camps, hitting champions, moving, idle, with a teammate
# within 3, gems gained (captures), gold earned (au rises), per game, us vs them.
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
R = int(os.environ.get('R', '600'))
A = collections.defaultdict(collections.Counter); G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    for c in rows[0]['c']: G[(D.who(c['t'], us), D.NAMES[c['ty']])] += 1
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i in range(n):
            c = a['c'][i]; k = (D.who(c['t'], us), D.NAMES[c['ty']]); X = A[k]
            if not c['a'] or 'x' not in c: X['dead'] += 1; continue
            acts = a['act'][i] if i < len(a['act']) else []
            hitc = any(x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'm' for x in acts)
            hitch = any(x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' for x in acts)
            mv = any(x[0] == 'move' for x in acts)
            X['camp'] += hitc; X['champ'] += hitch and not hitc; X['move'] += mv and not hitc and not hitch
            X['idle'] += not acts
            p = (c['x'], c['y'])
            X['mate3'] += any(o is not c and o['t'] == c['t'] and o['a'] and 'x' in o and D.dist(p, (o['x'], o['y'])) <= 3 for o in a['c'])
            nc = b['c'][i]
            if nc['a'] and nc.get('g', 0) > c.get('g', 0): X['gems'] += nc['g'] - c['g']; X['gains'] += 1
            if nc['a'] and nc.get('au', 0) > c.get('au', 0): X['gold+'] += nc['au'] - c['au']
for k in sorted(A, key=lambda k: (k[1], k[0])):
    g = G[k]
    if g < 10: continue
    X = A[k]
    print(f"{k[1]:9} {k[0]:4} n {g:3} " + ' '.join(f"{f} {X[f] / g:6.1f}" for f in ('dead', 'camp', 'champ', 'move', 'idle', 'mate3', 'gems', 'gains', 'gold+')))
