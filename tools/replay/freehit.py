"""Free hits left by melee champions: python -I tools/replay/freehit.py RMAX DIR...
A melee champion may walk and attack in one turn. Counted per game by side and type: turns that end with a walk and no attack although an enemy champion stands within 1 of the end tile both at the start of the round and at the start of the next, and the
same with a camp in reach as the only unused target left out. Also turns that start beside an enemy, walk away and deal no hit. Compared with the turns that walk and hit a champion."""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
D.SKIP = []
RM = int(sys.argv[1])
A = collections.defaultdict(collections.Counter)
G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    n = len(rows[0]['c'])
    seen = collections.Counter()
    for c in rows[0]['c']:
        G[(D.who(c['t'], us), D.NAMES[c['ty']])] += 1
        G[(D.who(c['t'], us), 'all')] += 1
    for k in range(len(rows) - 1):
        r = rows[k]; b = rows[k + 1]
        if r['r'] > RM:
            break
        for i, c in enumerate(r['c']):
            if not c['a'] or 'x' not in c or D.RANGE[c['ty']] != 1:
                continue
            acts = r['act'][i] if i < len(r['act']) else []
            mv = [x for x in acts if x[0] == 'move']
            if not mv:
                continue
            q = (mv[-1][3], mv[-1][4])
            hit = bool(D.enemy_hits(r, i, n))
            attacked = any(x[0] == 'attack' for x in acts)
            near_end = False
            for j, e in enumerate(r['c']):
                if e['t'] == c['t'] or not e['a'] or 'x' not in e:
                    continue
                e2 = b['c'][j]
                if not e2['a'] or 'x' not in e2:
                    continue
                if D.dist(q, (e['x'], e['y'])) <= 1 and D.dist(q, (e2['x'], e2['y'])) <= 1:
                    near_end = True
            start_near = any(e['t'] != c['t'] and e['a'] and 'x' in e and D.dist((c['x'], c['y']), (e['x'], e['y'])) <= 1 for e in r['c'])
            w = D.who(c['t'], us); ty = D.NAMES[c['ty']]
            for key in ((w, 'all'), (w, ty)):
                s = A[key]
                s['walkhit'] += hit
                s['free'] += near_end and not attacked
                s['left'] += start_near and not hit and not near_end
print('side type | walk+hit champion | walk ending beside an enemy, no attack | started beside an enemy, walked off, no hit (per champion-game)')
for key in sorted(A, key=lambda z: (z[1] != 'all', z[1], z[0])):
    s = A[key]; g = max(1, G[key])
    if g < 15:
        continue
    print(f"{key[1]:9} {key[0]:4} {g:4} | {s['walkhit']/g:5.1f} | {s['free']/g:5.2f} | {s['left']/g:5.2f}")
