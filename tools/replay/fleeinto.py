# Flee steps into other enemies: per champion-round to r1000 where a champion under 50% health (off spawn) has an
# enemy champion within 3 and moves, classify the step against the round-start enemy positions: 'into' = the new tile
# is within 2 of an enemy that was farther than 2 from the old tile; 'away' = the nearest enemy is farther after the
# step and no enemy came within 2; 'closer' = the nearest enemy distance fell. Reports shares and P(death within 10).
# usage: python -I tools/replay/fleeinto.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    for k in range(len(rows) - 11):
        a, b = rows[k], rows[k + 1]
        if b['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            if not off(c) or c['hp'] >= 0.5 * c['mhp']: continue
            p = (c['x'], c['y'])
            ens = [(a['c'][j]['x'], a['c'][j]['y']) for j in range(n) if a['c'][j]['t'] != c['t'] and off(a['c'][j])]
            if not ens or min(D.dist(p, e) for e in ens) > 3: continue
            o = b['c'][i]
            if not (o['a'] and 'x' in o): continue
            q = (o['x'], o['y'])
            w = D.who(c['t'], us)
            C[(w, 'rounds')] += 1
            if q == p: continue
            d0 = min(D.dist(p, e) for e in ens); d1 = min(D.dist(q, e) for e in ens)
            into = any(D.dist(q, e) <= 2 < D.dist(p, e) for e in ens)
            cls = 'into' if into else 'away' if d1 > d0 else 'closer' if d1 < d0 else 'level'
            dies = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 11))
            for key in ((w, 'moves'), (w, cls)):
                C[key] += 1; C[key + ('dies',)] += dies
print(f'{ng} games to r1000: champion under 50% health with an enemy within 3, steps classified')
for w in ('us', 'them'):
    m = C[(w, 'moves')]
    line = f"  {w:4} rounds/g {C[(w, 'rounds')] / ng:5.1f}, moves/g {m / ng:5.1f} (P dead10 {C[(w, 'moves', 'dies')] / max(1, m):.3f})"
    for cls in ('away', 'level', 'closer', 'into'):
        x = C[(w, cls)]
        line += f" | {cls} {x / max(1, m):.0%} P {C[(w, cls, 'dies')] / max(1, x):.3f}"
    print(line)
