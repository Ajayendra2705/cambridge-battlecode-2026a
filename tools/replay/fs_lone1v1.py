# Lone first strikes, to R: a champion opens a fight (its first hit on that enemy after 15 quiet rounds between the
# pair) with no ally within 5 and that enemy the only enemy champion within 6 at the round start; split by where
# (clearly our side: own spawn 7+ tiles nearer than theirs, Chebyshev, else 'middle/theirs') and the striker's health.
# Outcome within 15 rounds: P(striker dies), P(victim dies), and the most enemies within 6 of the striker in 10 rounds.
# usage: python -I tools/replay/fs_lone1v1.py [--upto R] [--size N] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 1000; SIZE = None; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--upto': R = int(args[1]); args = args[2:]
    elif args[0] == '--size': SIZE = int(args[1]); args = args[2:]
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1
    sp = {t: [(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c] for t in (0, 1)}
    last = {}
    for k in range(len(rows) - 16):
        a = rows[k]
        if a['r'] > R: break
        for i in range(n):
            for x in D.enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j))
                fresh = k - last.get(key, -99) > 15
                last[key] = k
                if not fresh: continue
                s = a['c'][i]
                if 'x' not in s: continue
                q = (s['x'], s['y'])
                allies = sum(1 for m, o in enumerate(a['c']) if m != i and o['t'] == s['t'] and o['a'] and 'x' in o and D.dist(q, (o['x'], o['y'])) <= 5)
                ens = [m for m, o in enumerate(a['c']) if o['t'] != s['t'] and o['a'] and 'x' in o and D.dist(q, (o['x'], o['y'])) <= 6]
                if allies or ens != [j]: continue
                own = min(D.dist(q, p) for p in sp[s['t']]); their = min(D.dist(q, p) for p in sp[1 - s['t']])
                where = 'own side' if own + 7 <= their else 'middle/theirs'
                hp = 'hp80+' if s.get('hp', 0) >= 0.8 * s.get('mhp', 1) else 'hp50-80' if s.get('hp', 0) >= 0.5 * s.get('mhp', 1) else 'hp<50'
                sd = any(not rows[t]['c'][i]['a'] for t in range(k + 1, k + 16))
                vd = any(not rows[t]['c'][j]['a'] for t in range(k + 1, k + 16))
                mx = 0
                for t in range(k, k + 11):
                    c2 = rows[t]['c'][i]
                    if not c2['a'] or 'x' not in c2: break
                    q2 = (c2['x'], c2['y'])
                    mx = max(mx, sum(1 for o in rows[t]['c'] if o['t'] != s['t'] and o['a'] and 'x' in o and D.dist(q2, (o['x'], o['y'])) <= 6))
                w = D.who(s['t'], us)
                for key2 in (('all',), (where,), (where, hp)):
                    C[(w,) + key2] += 1; C[(w,) + key2 + ('sd',)] += sd; C[(w,) + key2 + ('vd',)] += vd; C[(w,) + key2 + ('mx',)] += mx
                    C[(w,) + key2 + ('mx2',)] += mx >= 2
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r{R}: lone first strikes (no ally within 5, the victim the only enemy within 6)')
keys = [('all',), ('own side',), ('middle/theirs',)] + [(w, h) for w in ('own side', 'middle/theirs') for h in ('hp80+', 'hp50-80', 'hp<50')]
for key in keys:
    line = []
    for w in ('us', 'them'):
        c = C[(w,) + key]
        if not c: line.append(f'{w:4}   -'); continue
        line.append(f'{w:4} {c / ng:5.2f}/g striker dies {C[(w,) + key + ("sd",)] / c:.2f} victim dies {C[(w,) + key + ("vd",)] / c:.2f} 2+ enemies come {C[(w,) + key + ("mx2",)] / c:.2f}')
    print(f'  {" ".join(key):24} ' + '   '.join(line))
