# Contacts of one type (default vesper) while short, 5-a-side, to r1000: a round that ends with an enemy champion next
# to her when none was the round before, with more enemy champions within 6 of her than her allies within 6 plus one.
# Per game, by how it began (her own move ended next to an enemy; she moved and an enemy came; she shot and an enemy
# came; she stood and an enemy came) and the nearest enemy's distance the round before; then the share with her dash
# (slot 1) used more than 8 rounds before, the rounds the contact lasts, and P(she dies within 10).
# usage: python -I tools/replay/contacts.py [--type NAME] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist
TY = 'vesper'; args = sys.argv[1:]
if args and args[0] == '--type': TY = args[1]; args = args[2:]
T = NAMES.index(TY)
HOW = ('walked in', 'moved, enemy came', 'shot, enemy came', 'stood, enemy came')
C = collections.Counter(); G = collections.Counter()
def pos(c): return (c['x'], c['y'])
def nearest(row, c):
    return min((dist(pos(c), pos(e)) for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t']), default=99)
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 10: continue
    for k, c0 in enumerate(rows[0]['c']):
        if c0['ty'] != T: continue
        w = who(c0['t'], us); G[w] += 1
        last_dash = -100
        for r in range(1, len(rows) - 1):
            if rows[r]['r'] > 1000: break
            prev, row = rows[r - 1], rows[r]
            acts0 = prev['act'][k] if k < len(prev['act']) else []
            if any(x[0] == 'cast' and x[1] == 1 for x in acts0): last_dash = prev['r']
            c, cp = row['c'][k], prev['c'][k]
            if not c['a'] or 'x' not in c or not cp['a'] or 'x' not in cp: continue
            if nearest(row, c) > 1 or nearest(prev, cp) <= 1: continue
            en6 = sum(1 for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t'] and dist(pos(c), pos(e)) <= 6)
            al6 = sum(1 for j, e in enumerate(row['c']) if j != k and e['a'] and 'x' in e and e['t'] == c['t'] and dist(pos(c), pos(e)) <= 6)
            if en6 <= al6 + 1: continue
            moved = pos(c) != pos(cp)
            own = moved and min((dist(pos(c), pos(e)) for e in prev['c'] if e['a'] and 'x' in e and e['t'] != c['t']), default=99) <= 1
            how = HOW[0] if own else HOW[1] if moved else HOW[2] if any(x[0] == 'attack' for x in acts0) else HOW[3]
            q = r
            while q < len(rows) - 1 and rows[q]['c'][k]['a'] and 'x' in rows[q]['c'][k] and nearest(rows[q], rows[q]['c'][k]) <= 1: q += 1
            die = any(not rows[z]['c'][k]['a'] for z in range(r + 1, min(len(rows), r + 11)))
            for h in ('all', how):
                C[(w, h)] += 1; C[(w, h, min(nearest(prev, cp), 4))] += 1; C[(w, h, 'die')] += die
            C[(w, 'ready')] += prev['r'] - last_dash > 8; C[(w, 'len')] += q - r
print(f"{TY} contacts begun while short, 5-a-side, to r1000; games us {G['us']} them {G['them']}")
for w in ('us', 'them'):
    g = max(1, G[w]); n = max(1, C[(w, 'all')])
    print(f"  {w:4} all {C[(w, 'all')] / g:.2f}/g  dash ready {C[(w, 'ready')] / n:.2f}  lasts {C[(w, 'len')] / n:.2f} rounds  P(she dies 10) {C[(w, 'all', 'die')] / n:.2f}")
    for h in HOW:
        m = max(1, C[(w, h)])
        print(f"    {h:18} {C[(w, h)] / g:.2f}/g  from d=2 {C[(w, h, 2)] / g:.2f} d=3 {C[(w, h, 3)] / g:.2f} d>=4 {C[(w, h, 4)] / g:.2f}  P(she dies 10) {C[(w, h, 'die')] / m:.2f}")
