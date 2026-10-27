# Pack sightings to r1000 (2+ enemy champions within 8 off their spawn, at most one ally within 6, after 5+ rounds
# without), split by what the champion did in the 5 rounds before: hit a champion ('champ'), else hit a camp ('camp'),
# else moved in 3+ of them ('walk'), else 'still'. For each: per game, death within 15 rounds, own net steps towards the
# pack's centre over the next 5 rounds, rounds hitting champions / camps in the next 5, distance to the nearest of the
# pack at the sighting and its change after 5 rounds (both sides' steps), bag 20+, health 75%+.
# usage: python -I tools/replay/packwalk.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    quiet = collections.Counter()
    for k in range(5, len(rows) - 16):
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
            prev = rows[k - 5:k]
            if any(D.enemy_hits(q, i, n) for q in prev): kind = 'champ'
            elif any(D.camp_hits(q, i) for q in prev): kind = 'camp'
            else:
                moved = sum(1 for a, b in zip(prev, prev[1:] + [r]) if a['c'][i]['a'] and b['c'][i]['a'] and 'x' in a['c'][i] and 'x' in b['c'][i]
                            and (a['c'][i]['x'], a['c'][i]['y']) != (b['c'][i]['x'], b['c'][i]['y']))
                kind = 'walk' if moved >= 3 else 'still'
            cx = sum(r['c'][j]['x'] for j in foes) / len(foes); cy = sum(r['c'][j]['y'] for j in foes) / len(foes)
            d0 = max(abs(pos[0] - cx), abs(pos[1] - cy))
            near0 = min(D.dist(pos, (r['c'][j]['x'], r['c'][j]['y'])) for j in foes)
            q = rows[k + 5]['c'][i]
            alive5 = q['a'] and 'x' in q
            toward = d0 - max(abs(q['x'] - cx), abs(q['y'] - cy)) if alive5 else 0
            near5 = min([D.dist((q['x'], q['y']), (rows[k + 5]['c'][j]['x'], rows[k + 5]['c'][j]['y'])) for j in foes
                         if rows[k + 5]['c'][j]['a'] and 'x' in rows[k + 5]['c'][j]] or [99]) if alive5 else 0
            hitc = sum(1 for kk in range(k, k + 5) if D.enemy_hits(rows[kk], i, n))
            hitm = sum(1 for kk in range(k, k + 5) if D.camp_hits(rows[kk], i))
            died = any(not rows[kk]['c'][i]['a'] for kk in range(k, k + 16))
            for key in (kind, 'all'):
                for f, v in (('n', 1), ('died', died), ('toward', toward), ('hitc', hitc), ('hitm', hitm), ('near0', near0),
                             ('dnear', (near5 - near0) if alive5 and near5 < 99 else 0), ('a5', alive5 and near5 < 99),
                             ('bag', p.get('g', 0) >= 20), ('hi', p['hp'] >= 0.75 * p['mhp'])):
                    C[(w, key, f)] += v
print(f'{ng} games to r1000: pack sightings by activity in the 5 rounds before; per game, died<=15, own steps toward, hit rounds champ/camp (next 5), nearest foe at sighting and its change after 5 rounds, bag 20+, hp 75%+')
for key in ('all', 'walk', 'camp', 'champ', 'still'):
    for w in ('us', 'them'):
        nn = max(1, C[(w, key, 'n')])
        print(f"  {key:5} {w:4} {C[(w, key, 'n')] / ng:5.1f}/g  died {C[(w, key, 'died')] / nn:.3f}  toward {C[(w, key, 'toward')] / nn:+.2f}"
              f"  hit c/m {C[(w, key, 'hitc')] / nn:.2f}/{C[(w, key, 'hitm')] / nn:.2f}  near {C[(w, key, 'near0')] / nn:.1f}"
              f" ({C[(w, key, 'dnear')] / max(1, C[(w, key, 'a5')]):+.2f})  bag {C[(w, key, 'bag')] / nn:.2f}  hi {C[(w, key, 'hi')] / nn:.2f}")
