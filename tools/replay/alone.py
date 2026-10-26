"""Rounds alone against 2+ enemies (no ally within 6, 2+ enemy champions within 6, off their spawn), health 50%+, to r1000:
what the champion does this round (hit champion / hit camp / step away from the nearest enemy / step closer / step level /
stay), split by nearest enemy distance; P(death within 10). python -I tools/replay/alone.py DIR..."""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
A = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    death = {}
    for k in range(1, len(rows)):
        for i in range(n):
            if rows[k - 1]['c'][i]['a'] and not rows[k]['c'][i]['a']: death.setdefault(i, []).append(rows[k]['r'])
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if a['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            if not c['a'] or 'x' not in c or c['hp'] < 0.5 * c['mhp']: continue
            p = (c['x'], c['y'])
            if p in spawn[c['t']]: continue
            es = [(o['x'], o['y']) for o in a['c'] if o['a'] and 'x' in o and o['t'] != c['t'] and (o['x'], o['y']) not in spawn[o['t']]]
            e6 = sum(1 for q in es if D.dist(p, q) <= 6)
            a6 = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == c['t'] and D.dist((o['x'], o['y']), p) <= 6)
            if e6 < 2 or a6 > 0: continue
            de = min(D.dist(p, q) for q in es)
            band = '1-2' if de <= 2 else '3-4' if de <= 4 else '5-6'
            nb = b['c'][i]
            if D.enemy_hits(a, i, n): act = 'hit champ'
            elif D.camp_hits(a, i): act = 'hit camp'
            elif nb['a'] and 'x' in nb and (nb['x'], nb['y']) != p:
                d1 = min(D.dist((nb['x'], nb['y']), q) for q in es)
                act = 'away' if d1 > de else 'closer' if d1 < de else 'level'
            else: act = 'stay'
            w = D.who(c['t'], us)
            dies = any(a['r'] < r <= a['r'] + 10 for r in death.get(i, []))
            A[(w, band, 'n')] += 1; A[(w, band, act)] += 1; A[(w, band, 'dies')] += dies
            A[(w, band, act + ' dies')] += dies
print(f'{ng} games to r1000: rounds alone (no ally within 6) with 2+ enemies within 6, health 50%+; per game, action shares (P death in 10)')
for band in ('1-2', '3-4', '5-6'):
    for w in ('us', 'them'):
        nn = A[(w, band, 'n')]
        if not nn: continue
        acts = '  '.join(f'{x} {A[(w, band, x)] / nn:.2f} ({A[(w, band, x + " dies")] / max(1, A[(w, band, x)]):.2f})'
                         for x in ('hit champ', 'hit camp', 'away', 'level', 'closer', 'stay'))
        print(f'  nearest {band} {w:4} {nn / ng:5.1f}/g  P(dies) {A[(w, band, "dies")] / nn:.3f}  {acts}')
