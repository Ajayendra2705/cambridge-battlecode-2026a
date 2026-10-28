# First shots (as in rh_pursuit.py) on a non-fighting champion, split by: victim type; distance to the shooter at the round
# start (in range already, or came in); the victim's step in the round before relative to the shooter; allies within 3
# of the victim; at a camp (camp hits that round or the one before); the map half (nearer its own spawn or the enemy's).
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, camp_hits, RANGE, NAMES
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
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
                v = a['c'][j]; pj = pos(v); pp = pos(rows[k - 1]['c'][j]); psp = pos(rows[k - 1]['c'][i])
                if pj is None: continue
                w = who(v['t'], us)
                d0 = dist(pj, ps)
                came = 'in range at start' if d0 <= 3 else 'came into range'
                if pp is None or psp is None: prev = 'none'
                else:
                    a0, a1 = dist(pp, psp), dist(pj, psp)
                    prev = 'still' if pp == pj else 'closer' if a1 < a0 else 'level' if a1 == a0 else 'away'
                allies = sum(1 for e in range(n) if e != j and a['c'][e]['t'] == v['t'] and pos(a['c'][e]) and dist(pos(a['c'][e]), pj) <= 3)
                camp = any(camp_hits(rows[t], j) for t in (k - 1, k))
                own = min(dist(pj, s) for s in spawn[v['t']]); opp = min(dist(pj, s) for s in spawn[1 - v['t']])
                half = 'own half' if own < opp else 'their half'
                for key in ('all', 'type ' + NAMES[v['ty']], came, 'prev ' + prev, 'allies %d' % min(allies, 2), 'camp' if camp else 'no camp', half,
                            half + (' camp' if camp else ' no camp') + (' alone' if allies == 0 else ' with ally')):
                    E[(w, key)] += 1
keys = sorted(set(k for (_, k) in E), key=lambda k: (k != 'all', k))
print(ng, 'games, to r1000: first shots on a non-fighting champion per game, by victim side')
for k in keys:
    print(f'  {k:36} us {E[("us", k)] / ng:5.2f}   them {E[("them", k)] / ng:5.2f}')
