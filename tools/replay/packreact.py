# Pack sightings to r1000: a champion with at most one ally within 6 gets 2+ enemy champions within 8 (off their
# spawn tiles) after 5+ rounds without. Over the next 5 rounds: the champion's own steps towards the pack's centroid
# at the start (net tiles), its hits on champions and camps, standing still; enemies within 6 after 5 rounds; death
# within 15 rounds. Split by the champion's health (75%+ or not) and bag (20+ or not). Us vs them.
# usage: python -I tools/replay/packreact.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    quiet = collections.Counter()
    for k in range(len(rows) - 16):
        r = rows[k]
        if r['r'] > 1000: break
        for i in range(n):
            p = r['c'][i]
            if not (p['a'] and 'x' in p): quiet[i] = 0; continue
            t = p['t']; pos = (p['x'], p['y'])
            foes = [j for j in range(n) if r['c'][j]['a'] and 'x' in r['c'][j] and r['c'][j]['t'] != t
                    and (r['c'][j]['x'], r['c'][j]['y']) not in spawn[1 - t] and D.dist(pos, (r['c'][j]['x'], r['c'][j]['y'])) <= 8]
            al = sum(1 for j in range(n) if j != i and r['c'][j]['a'] and 'x' in r['c'][j] and r['c'][j]['t'] == t and D.dist(pos, (r['c'][j]['x'], r['c'][j]['y'])) <= 6)
            if len(foes) < 2 or al > 1: quiet[i] += 1 if len(foes) < 2 else 0; continue
            start = quiet[i] >= 5
            quiet[i] = 0
            if not start: continue
            w = D.who(t, us)
            cx = sum(r['c'][j]['x'] for j in foes) / len(foes); cy = sum(r['c'][j]['y'] for j in foes) / len(foes)
            d0 = max(abs(pos[0] - cx), abs(pos[1] - cy))
            q = rows[k + 5]['c'][i]
            if not (q['a'] and 'x' in q): toward = 0
            else: toward = d0 - max(abs(q['x'] - cx), abs(q['y'] - cy))
            hitc = sum(1 for kk in range(k, k + 5) if D.enemy_hits(rows[kk], i, n))
            hitm = sum(1 for kk in range(k, k + 5) if D.camp_hits(rows[kk], i))
            still = sum(1 for kk in range(k, k + 5) if rows[kk]['c'][i]['a'] and rows[kk + 1]['c'][i]['a'] and 'x' in rows[kk + 1]['c'][i]
                        and (rows[kk]['c'][i].get('x'), rows[kk]['c'][i].get('y')) == (rows[kk + 1]['c'][i]['x'], rows[kk + 1]['c'][i]['y']))
            e6 = sum(1 for o in rows[k + 5]['c'] if q['a'] and 'x' in q and o['a'] and 'x' in o and o['t'] != t and D.dist((q['x'], q['y']), (o['x'], o['y'])) <= 6)
            died = any(not rows[kk]['c'][i]['a'] for kk in range(k, k + 16))
            hi = p['hp'] >= 0.75 * p['mhp']; bag = p.get('g', 0) >= 20
            for key in ('all', f"hp {'hi' if hi else 'lo'}", f"bag {'20+' if bag else '<20'}", f"foes {min(len(foes), 3)}"):
                for f, v in (('n', 1), ('toward', toward), ('hitc', hitc), ('hitm', hitm), ('still', still), ('e6', e6), ('died', died), ('d0', d0)):
                    C[(w, key, f)] += v
print(f'{ng} games to r1000: pack sightings (2+ enemies within 8, at most one ally within 6, after 5+ rounds without)')
for key in ('all', 'hp hi', 'hp lo', 'bag <20', 'bag 20+', 'foes 2', 'foes 3'):
    for w in ('us', 'them'):
        nn = max(1, C[(w, key, 'n')])
        print(f"  {key:8} {w:4} {C[(w, key, 'n')] / ng:5.1f}/game  dist {C[(w, key, 'd0')] / nn:.1f}  own steps toward (5 rounds) {C[(w, key, 'toward')] / nn:+.2f}"
              f"  champ-hit rounds {C[(w, key, 'hitc')] / nn:.2f} camp-hit {C[(w, key, 'hitm')] / nn:.2f} still {C[(w, key, 'still')] / nn:.2f}"
              f"  e6 after {C[(w, key, 'e6')] / nn:.2f}  died<=15 {C[(w, key, 'died')] / nn:.3f}")
