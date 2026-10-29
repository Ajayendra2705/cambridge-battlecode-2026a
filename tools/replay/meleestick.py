# Melee champions adjacent to an enemy champion (off its spawn) at a round start, 5-a-side, to r1000, by side and by numbers
# near (allies within 5 minus enemies within 5: <0, 0, >0): P(still adjacent to that enemy at the next round start), the
# share of rounds it hit a champion, and when that enemy stepped away (its distance from the melee's old tile grew), the
# share the melee followed (adjacent again) and P(that enemy dies within 10 rounds).
# usage: python -I tools/replay/meleestick.py DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist, enemy_hits
args = sys.argv[1:]
MELEE = {NAMES.index(x) for x in ('heart', 'marcella', 'vendetta', 'ryth', 'varg', 'ren', 'issac') if x in NAMES}
R = {w: collections.Counter() for w in ('us', 'them')}; G = collections.Counter()
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 10: continue
    G['g'] += 1
    spawn = {t: set(pos(c) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    deaths = {k: [r for r in range(1, len(rows)) if not rows[r]['c'][k]['a'] and rows[r - 1]['c'][k]['a']] for k in range(10)}
    for r in range(len(rows) - 1):
        if rows[r]['r'] > 1000: break
        row, nx = rows[r], rows[r + 1]
        for i, c in enumerate(row['c']):
            if c['ty'] not in MELEE or not c['a'] or 'x' not in c: continue
            p = pos(c)
            adj = [k for k, e in enumerate(row['c']) if e['a'] and 'x' in e and e['t'] != c['t'] and dist(p, pos(e)) <= 1 and pos(e) not in spawn[e['t']]]
            if not adj: continue
            k = min(adj, key=lambda k: row['c'][k]['hp'])
            en = sum(1 for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t'] and dist(p, pos(e)) <= 5)
            al = sum(1 for j, e in enumerate(row['c']) if j != i and e['a'] and 'x' in e and e['t'] == c['t'] and dist(p, pos(e)) <= 5)
            num = 'down' if al + 1 < en else 'even' if al + 1 == en else 'up'
            X = R[who(c['t'], us)]
            X[num] += 1; X[(num, 'hit')] += bool(enemy_hits(row, i, 10))
            m2, e2 = nx['c'][i], nx['c'][k]
            if not m2['a'] or 'x' not in m2 or not e2['a'] or 'x' not in e2: continue
            X[(num, 'n2')] += 1; X[(num, 'still')] += dist(pos(m2), pos(e2)) <= 1
            if dist(p, pos(e2)) > 1:
                X[(num, 'stepped')] += 1; X[(num, 'followed')] += dist(pos(m2), pos(e2)) <= 1
                X[(num, 'stepped dies')] += any(0 < dr - r <= 10 for dr in deaths[k])
print(f"melee adjacent to an enemy champion, 5-a-side, to r1000, {G['g']} games, by numbers near (allies+1 vs enemies within 5)")
for num in ('down', 'even', 'up'):
    for w in ('us', 'them'):
        X = R[w]
        print(f"  {num:4} {w:4} rounds/g {X[num] / G['g']:5.1f}  hit {X[(num, 'hit')] / max(1, X[num]):.2f}  still adjacent {X[(num, 'still')] / max(1, X[(num, 'n2')]):.2f}"
              f"  enemy stepped away {X[(num, 'stepped')] / G['g']:5.2f}/g: followed {X[(num, 'followed')] / max(1, X[(num, 'stepped')]):.2f}, it died in 10 {X[(num, 'stepped dies')] / max(1, X[(num, 'stepped')]):.2f}")
