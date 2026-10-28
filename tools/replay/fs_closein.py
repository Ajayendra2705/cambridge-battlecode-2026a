# Fight starts (as in fs_firsthit.py) struck by a melee champion that has a dash (Heart of Ruin, Vendetta), from 3 or
# more tiles at the round start: the striker's actions that turn in order (move, cast, attack), and P(the victim dies)
# and P(the striker dies) within 10 rounds, per game, to r1000, by the striking side.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, NAMES
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c']); last_hit = {}
    for k in range(1, len(rows) - 11):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            for x in enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j))
                fresh = k - last_hit.get(key, -99) > 15
                last_hit[key] = k
                s = a['c'][i]
                if not fresh or NAMES[s['ty']] not in ('heart', 'vendetta'): continue
                ps, pv = pos(s), pos(a['c'][j])
                if ps is None or pv is None or dist(ps, pv) < 3: continue
                acts = a['act'][i] if i < len(a['act']) else []
                seq = []
                for y in acts:
                    t = y[0] if y[0] != 'cast' else 'cast%d' % y[1]
                    if t in ('move', 'attack') or t.startswith('cast'):
                        if not seq or seq[-1] != t: seq.append(t)
                w = who(s['t'], us)
                vd = any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 11))
                sd = any(not rows[t]['c'][i].get('a') for t in range(k + 1, k + 11))
                for key2 in ('%s from %d' % (NAMES[s['ty']], min(dist(ps, pv), 5)), '%s %s' % (NAMES[s['ty']], ' '.join(seq))):
                    E[(w, key2)] += 1; E[(w, key2, 'v')] += vd; E[(w, key2, 's')] += sd
print(ng, 'games, to r1000: fight starts by Heart of Ruin / Vendetta from 3+ tiles, per game; P(victim dies), P(striker dies) in 10')
for k in sorted(set(k[1] for k in E if len(k) == 2)):
    line = []
    for w in ('us', 'them'):
        c = E[(w, k)]
        line.append(f'{w:4} {c / ng:5.2f} (v {E[(w, k, "v")] / max(1, c):4.2f} s {E[(w, k, "s")] / max(1, c):4.2f})')
    print(f'  {k:34} ' + '   '.join(line))
