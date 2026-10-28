# Melee turns that hit an enemy champion with a basic attack (Heart of Ruin, Vendetta, Marcella, Varg, Ryth and the other
# melee types), to r1000, us vs them: whether the champion walked after its last attack that turn, and where to (away
# from the target it hit, level, closer), with P(the target dies) and P(the hitter dies) within 10 rounds, per game.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, RANGE, NAMES
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    for k in range(1, len(rows) - 11):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            if pos(c) is None or RANGE.get(c['ty'], 1) > 1: continue
            acts = a['act'][i] if i < len(a['act']) else []
            last = max((q for q, x in enumerate(acts) if x[0] == 'attack' and x[-2] == 'c' and a['c'][x[-1]]['t'] != c['t']), default=-1)
            if last < 0: continue
            j = acts[last][-1]
            tp = (acts[last][1], acts[last][2])  # the target's tile when hit
            mv = [x for x in acts[last + 1:] if x[0] == 'move']
            if not mv: kind = 'no walk after the hit'
            else:
                end = (mv[-1][3], mv[-1][4])
                before = (mv[0][1], mv[0][2])
                d0, d1 = dist(before, tp), dist(end, tp)
                kind = 'walked away' if d1 > d0 else 'walked closer' if d1 < d0 else 'walked level'
            vd = any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 11))
            sd = any(not rows[t]['c'][i].get('a') for t in range(k + 1, k + 11))
            w = who(c['t'], us)
            for key in ('all ' + kind, NAMES[c['ty']] + ' ' + kind):
                E[(w, key)] += 1; E[(w, key, 'v')] += vd; E[(w, key, 's')] += sd
print(ng, 'games, to r1000: melee turns with a basic attack on an enemy champion, per game; P(target dies), P(hitter dies) in 10')
for key in sorted(set(k[1] for k in E if len(k) == 2), key=lambda k: (not k.startswith('all'), k)):
    line = []
    for w in ('us', 'them'):
        c = E[(w, key)]
        line.append(f'{w:4} {c / ng:6.2f} (t {E[(w, key, "v")] / max(1, c):4.2f} h {E[(w, key, "s")] / max(1, c):4.2f})')
    print(f'  {key:34} ' + '   '.join(line))
