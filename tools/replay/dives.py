# Dives of one type (default vendetta): slot 1 casts (dash) whose landing has an enemy champion within 1, to r1000,
# 5-a-side games, by side: per game; at the landing, enemies within 3 and allies within 3; her health share; whether she
# hit a champion that round; P(she dies within 10), P(an enemy within 1 of the landing dies within 10). Split by the
# margin at the landing: enemy champions within 3 minus (allies within 3 + her), <= -1, 0, 1, >= 2; then by the margin
# and the weakest adjacent target's health (40% or less: low), and the dives rz12 refuses (level against a high target,
# or short) against the rest.
# usage: python -I tools/replay/dives.py [--type NAME] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist, enemy_hits
TY = 'vendetta'; args = sys.argv[1:]
if args and args[0] == '--type': TY = args[1]; args = args[2:]
T = NAMES.index(TY)
R = {w: collections.Counter() for w in ('us', 'them')}; G = collections.Counter()
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 10: continue
    for i, c0 in enumerate(rows[0]['c']):
        if c0['ty'] == T: G[who(c0['t'], us)] += 1
    deaths = {k: [r for r in range(1, len(rows)) if not rows[r]['c'][k]['a'] and rows[r - 1]['c'][k]['a']] for k in range(10)}
    for r in range(len(rows)):
        if rows[r]['r'] > 1000: break
        row = rows[r]
        for i, c in enumerate(row['c']):
            if c['ty'] != T or not c['a'] or 'x' not in c or i >= len(row['act']): continue
            for x in row['act'][i]:
                if x[0] != 'cast' or x[1] != 1 or len(x) < 4: continue
                land = (x[2], x[3])
                near1 = [k for k, e in enumerate(row['c']) if e['a'] and 'x' in e and e['t'] != c['t'] and dist(land, pos(e)) <= 1]
                if not near1: continue
                en3 = sum(1 for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t'] and dist(land, pos(e)) <= 3)
                al3 = sum(1 for j, e in enumerate(row['c']) if j != i and e['a'] and 'x' in e and e['t'] == c['t'] and dist(land, pos(e)) <= 3)
                w = who(c['t'], us); X = R[w]
                dd = en3 - (al3 + 1); key = 'd<=-1' if dd <= -1 else 'd=0' if dd == 0 else 'd=1' if dd == 1 else 'd>=2'
                low = min(row['c'][k]['hp'] / max(1, row['c'][k]['mhp']) for k in near1) <= 0.4
                hk = ('d<=-1' if dd <= -1 else 'd=0' if dd == 0 else 'd>=1') + (' low' if low else ' high')
                rk = 'refused' if dd >= 1 or (dd == 0 and not low) else 'kept'
                for k2 in ('all', key, hk, rk):
                    X[k2] += 1
                    X[(k2, 'hit')] += bool(enemy_hits(row, i, 10))
                    X[(k2, 'hp')] += c['hp'] / max(1, c['mhp'])
                    X[(k2, 'die')] += any(0 < dr - r <= 10 for dr in deaths[i])
                    X[(k2, 'kill')] += any(any(0 < dr - r <= 10 for dr in deaths[k]) for k in near1)
                break
print(f"{TY} dives (dash landing next to an enemy champion), 5-a-side, to r1000; games us {G['us']} them {G['them']}")
for key in ('all', 'd<=-1', 'd=0', 'd=1', 'd>=2', 'd<=-1 low', 'd<=-1 high', 'd=0 low', 'd=0 high', 'd>=1 low', 'd>=1 high', 'kept', 'refused'):
    for w in ('us', 'them'):
        X = R[w]; n = max(1, X[key])
        print(f"  {key:11} {w:4} {X[key] / max(1, G[w]):5.2f}/g  hit {X[(key, 'hit')] / n:.2f}  hp {X[(key, 'hp')] / n:.2f}  P(she dies 10) {X[(key, 'die')] / n:.2f}  P(a target dies 10) {X[(key, 'kill')] / n:.2f}")
