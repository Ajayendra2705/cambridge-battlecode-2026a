# Fight starts (decoded.py starts: the first hit between two champions after 15 quiet rounds), by the side that struck
# first, to r1000, per game. For each start: the striker's type and kind (basic attack or spell) and distance at the
# round start; whether the victim had the striker within its own basic reach at the start of one of the 3 rounds before
# (and saw it then: `vis`), so that it could have struck first; what the victim did in the round before (hit a camp,
# walked, nothing); and whether the victim dies within 10 rounds.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, RANGE, NAMES
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c']); last_hit = {}
    for k in range(3, len(rows) - 11):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            for x in enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j))
                fresh = k - last_hit.get(key, -99) > 15
                last_hit[key] = k
                if not fresh: continue
                s, v = a['c'][i], a['c'][j]
                ps, pv = pos(s), pos(v)
                if ps is None or pv is None: continue
                w = who(s['t'], us)
                rv = RANGE.get(v['ty'], 1)
                could = any(pos(rows[t]['c'][i]) and pos(rows[t]['c'][j]) and dist(pos(rows[t]['c'][i]), pos(rows[t]['c'][j])) <= rv
                            and i in rows[t]['vis'][j] for t in (k - 1, k - 2, k - 3))
                prev = rows[k - 1]['act'][j] if j < len(rows[k - 1]['act']) else []
                did = 'hit a camp' if any(y[0] in ('attack', 'cast') and len(y) >= 5 and y[-2] == 'm' for y in prev) \
                    else 'walked' if any(y[0] == 'move' for y in prev) else 'other'
                died = any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 11))
                kind = ('spell' if x[0] == 'cast' else 'basic') + (' ranged' if RANGE.get(s['ty'], 1) >= 3 else ' melee')
                d = min(dist(ps, pv), 5)
                for key2 in ('all', 'striker ' + kind, 'distance %d' % d, 'victim could strike first' if could else 'victim could not',
                             'victim ' + did, 'striker ' + NAMES[s['ty']],
                             'from %s: %s %s' % ('4-5' if d >= 4 else '1-3', NAMES[s['ty']], x[0])):
                    E[(w, key2)] += 1; E[(w, key2, 'died')] += died
print(ng, 'games, to r1000: fight starts per game by the striking side, and P(the victim dies within 10 rounds)')
keys = sorted(set(k[1] for k in E if len(k) == 2), key=lambda k: (k != 'all', k))
for k in keys:
    print(f'  {k:32} us {E[("us", k)] / ng:5.2f} (victim dies {E[("us", k, "died")] / max(1, E[("us", k)]):4.2f})'
          f'   them {E[("them", k)] / ng:5.2f} (victim dies {E[("them", k, "died")] / max(1, E[("them", k)]):4.2f})')
