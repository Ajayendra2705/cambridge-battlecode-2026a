# Walk-ins of one type (default vendetta): a 'move' that ends next to an enemy champion it was not next to before the
# move, 5-a-side, to r1000, by side and the margin at the destination (enemies within 3 minus her and allies within 3):
# per game, P(she dies within 10), P(a target dies within 10).
# usage: python -I tools/replay/walkins.py [--type NAME] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist
TY = 'vendetta'; args = sys.argv[1:]
if args and args[0] == '--type': TY = args[1]; args = args[2:]
T = NAMES.index(TY)
R = {w: collections.Counter() for w in ('us', 'them')}; G = collections.Counter()
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 10: continue
    for c0 in rows[0]['c']:
        if c0['ty'] == T: G[who(c0['t'], us)] += 1
    deaths = {k: [r for r in range(1, len(rows)) if not rows[r]['c'][k]['a'] and rows[r - 1]['c'][k]['a']] for k in range(10)}
    for r in range(len(rows)):
        if rows[r]['r'] > 1000: break
        row = rows[r]
        for i, c in enumerate(row['c']):
            if c['ty'] != T or not c['a'] or 'x' not in c or i >= len(row['act']): continue
            for x in row['act'][i]:
                if x[0] != 'move' or len(x) < 5: continue
                a, b = (x[1], x[2]), (x[3], x[4])
                near = [k for k, e in enumerate(row['c']) if e['a'] and 'x' in e and e['t'] != c['t'] and dist(b, pos(e)) <= 1 and dist(a, pos(e)) > 1]
                if not near: continue
                en3 = sum(1 for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t'] and dist(b, pos(e)) <= 3)
                al3 = sum(1 for j, e in enumerate(row['c']) if j != i and e['a'] and 'x' in e and e['t'] == c['t'] and dist(b, pos(e)) <= 3)
                dd = en3 - al3 - 1; key = 'd<=-1' if dd <= -1 else 'd=0' if dd == 0 else 'd>=1'
                X = R[who(c['t'], us)]
                for k2 in ('all', key):
                    X[k2] += 1; X[(k2, 'die')] += any(0 < dr - r <= 10 for dr in deaths[i])
                    X[(k2, 'kill')] += any(any(0 < dr - r <= 10 for dr in deaths[k]) for k in near)
                break
print(f"{TY} walk-ins next to an enemy champion, 5-a-side, to r1000; games us {G['us']} them {G['them']}")
for key in ('all', 'd<=-1', 'd=0', 'd>=1'):
    for w in ('us', 'them'):
        X = R[w]; n = max(1, X[key])
        print(f"  {key:6} {w:4} {X[key] / max(1, G[w]):5.2f}/g  P(she dies 10) {X[(key, 'die')] / n:.2f}  P(a target dies 10) {X[(key, 'kill')] / n:.2f}")
