# First shots (rh_pursuit.py) on a non-fighting champion that was over 3 tiles from the shooter at the round start: who
# moved (the victim walked in before the shot, or the shooter came in), whether the victim saw the shooter at that round
# start (its own fog view, `vis`), and the distance then.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, RANGE, NAMES
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    fought = [set(i for i in range(n) if enemy_hits(r, i, n)) for r in rows]
    lasthit = {}
    for k in range(2, len(rows) - 2):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            sh = a['c'][i]; ps = pos(sh)
            if ps is None or RANGE.get(sh['ty'], 1) < 3: continue
            for x in a['act'][i]:
                if x[0] != 'attack' or x[-2] != 'c': continue
                j = x[-1]
                if a['c'][j]['t'] == sh['t']: continue
                first = k - lasthit.get((i, j), -99) > 8
                lasthit[(i, j)] = k
                if not first or j in fought[k] or j in fought[k - 1]: continue
                pj = pos(a['c'][j])
                if pj is None or dist(pj, ps) <= 3: continue
                w = who(a['c'][j]['t'], us)
                mover = 'victim walked in' if (x[1], x[2]) != pj else 'shooter came in'
                seen = 'saw it' if i in a['vis'][j] else 'did not see it'
                d0 = dist(pj, ps)
                for key in ('all', mover, mover + ', ' + seen, mover + ', d=%d' % min(d0, 6)):
                    E[(w, key)] += 1
print(ng, 'games, to r1000: first shots on a non-fighting champion that started the round over 3 tiles from the shooter, per game')
for k in sorted(set(k for (_, k) in E), key=lambda k: (k != 'all', k)):
    print(f'  {k:40} us {E[("us", k)] / ng:5.2f}   them {E[("them", k)] / ng:5.2f}')
