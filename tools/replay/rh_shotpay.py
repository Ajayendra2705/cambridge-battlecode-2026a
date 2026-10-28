# Came-in shots: an enemy ranged champion over 3 tiles from a non-fighting victim at the round start hits it at its
# round-start tile (after a walk and a reset, or a dash). One event per shooter, victim and round. Over that round and
# the next 6: hits by the shooter's team on the victim, hits by the victim's team on the shooter, deaths, and whether
# the victim hit any enemy within 3 rounds (its later hits then count as "in a fight" in rangedhits).
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, RANGE
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    fought = [set(i for i in range(n) if enemy_hits(r, i, n)) for r in rows]
    for k in range(1, len(rows) - 9):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            sh = a['c'][i]; ps = pos(sh)
            if ps is None or RANGE.get(sh['ty'], 1) < 3: continue
            seen = set()
            for x in a['act'][i]:
                if x[0] != 'attack' or x[-2] != 'c': continue
                j = x[-1]
                if j in seen or a['c'][j]['t'] == sh['t'] or j in fought[k] or j in fought[k - 1]: continue
                pk = pos(a['c'][j])
                if pk is None or dist(pk, ps) <= 3 or (x[1], x[2]) != pk: continue
                seen.add(j)
                w = who(a['c'][j]['t'], us)
                mates = [e for e in range(n) if a['c'][e]['t'] == sh['t']]
                foes = [e for e in range(n) if a['c'][e]['t'] == a['c'][j]['t']]
                E[(w, 'n')] += 1
                E[(w, 'team')] += sum(1 for t in range(k, k + 7) for e in mates for y in enemy_hits(rows[t], e, n) if y[-1] == j)
                E[(w, 'back')] += sum(1 for t in range(k, k + 7) for e in foes for y in enemy_hits(rows[t], e, n) if y[-1] == i)
                E[(w, 'vd')] += any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 8))
                E[(w, 'sd')] += any(not rows[t]['c'][i].get('a') for t in range(k + 1, k + 8))
                E[(w, 'fight')] += any(j in fought[t] for t in range(k, k + 3))
print(ng, 'games, to r1000: came-in shots on non-fighting victims; that round and the next 6, per event')
for w in ('them', 'us'):
    m = max(1, E[(w, 'n')])
    print(f"  victim {w:4} {E[(w, 'n')] / ng:5.2f}/game  shooter's team hits on victim {E[(w, 'team')] / m:4.2f}  hits back on shooter {E[(w, 'back')] / m:4.2f}  victim died {E[(w, 'vd')] / m:4.2f}  shooter died {E[(w, 'sd')] / m:4.2f}  victim fought within 3 {E[(w, 'fight')] / m:4.2f}")
