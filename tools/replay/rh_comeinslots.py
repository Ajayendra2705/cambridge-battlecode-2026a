# Verify the "shooter came into range" hits: victim shot at its round-start tile, shooter over 3 tiles away at the round
# start. Print the shooter's action list that round (in order) and tally the action kinds that precede the attack.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, RANGE, NAMES
from rangedhits import pos
P = collections.Counter(); ng = 0; shown = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    fought = [set(i for i in range(n) if enemy_hits(r, i, n)) for r in rows]
    for k in range(1, len(rows) - 4):
        a, b = rows[k], rows[k + 1]
        if a['r'] > 1000: break
        for i in range(n):
            sh = a['c'][i]; ps = pos(sh)
            if ps is None or RANGE.get(sh['ty'], 1) < 3: continue
            acts = a['act'][i]
            for q, x in enumerate(acts):
                if x[0] != 'attack' or x[-2] != 'c': continue
                j = x[-1]
                if a['c'][j]['t'] == sh['t'] or j in fought[k] or j in fought[k - 1]: continue
                pk = pos(a['c'][j])
                if pk is None or dist(pk, ps) <= 3 or (x[1], x[2]) != pk: continue
                w = who(a['c'][j]['t'], us)
                before = tuple(y[0] if y[0] != 'cast' else 'cast' for y in acts[:q])
                P[(w, before)] += 1
                if shown < 6 and w == 'us':
                    shown += 1
                    print(mp, 'r', a['r'], NAMES[sh['ty']], 'start', ps, 'next', pos(b['c'][i]), 'victim', pk, 'acts', acts)
print(ng, 'games; actions before the attack, per game:')
for (w, bf), c in sorted(P.items(), key=lambda t: -t[1]):
    print(f'  victim {w:4} {c / ng:5.2f}  {bf}')
