# Bank walks into held altars, to r1000: a champion with 20+ gems, 4-10 tiles from its nearest altar tile, closes on it
# (altar distance down 2+ over 3 rounds) while 2+ enemy champions stand within 3 of that altar. Per episode (one per
# champion per 20 rounds): P(death within 15 rounds), P(tribute within 15), gems lost. Also deaths of 20+ carriers
# within 3 of an altar with 2+ enemies within 3 of it at the death. Us vs them, per game.
# usage: python -I tools/replay/heldaltar.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    altars = {(x[1], x[2]) for b in rows for acts in b['act'][:n] for x in acts if x[0] == 'tribute'}
    if not altars: continue
    nxt = collections.Counter()
    for k in range(3, len(rows) - 16):
        b = rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            c = b['c'][i]
            if not (c['a'] and 'x' in c) or c.get('g', 0) < 20: continue
            p = (c['x'], c['y']); alt = min(altars, key=lambda a: D.dist(p, a)); d = D.dist(p, alt)
            held = sum(1 for o in b['c'] if o['a'] and 'x' in o and o['t'] != c['t'] and D.dist((o['x'], o['y']), alt) <= 3)
            w = D.who(c['t'], us)
            # Death at a held altar.
            if not rows[k + 1]['c'][i]['a'] and d <= 3 and held >= 2: C[(w, 'held death')] += 1; C[(w, 'held death g')] += c['g']
            if k < nxt[i] or not (4 <= d <= 10) or held < 2: continue
            q = rows[k - 3]['c'][i]
            if not (q['a'] and 'x' in q) or D.dist((q['x'], q['y']), alt) - d < 2: continue
            nxt[i] = k + 20
            died = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 16))
            trib = any(x[0] == 'tribute' for kk in range(k, k + 15) for x in (rows[kk]['act'][i] if i < len(rows[kk]['act']) else []))
            C[(w, 'walk')] += 1; C[(w, 'died')] += died; C[(w, 'trib')] += trib; C[(w, 'lost')] += c['g'] if died else 0
for w in ('us', 'them'):
    m = max(1, C[(w, 'walk')])
    print(f"{w:4} walks into a held altar {C[(w, 'walk')] / ng:.2f}/game: died within 15 {C[(w, 'died')] / m:.0%}, tributed within 15 {C[(w, 'trib')] / m:.0%}, "
          f"gems lost {C[(w, 'lost')] / ng:.1f}/game; deaths at a held altar {C[(w, 'held death')] / ng:.2f}/game ({C[(w, 'held death g')] / ng:.1f} gems)")
