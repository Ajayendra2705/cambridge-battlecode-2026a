# Alive rounds per game to r1000 by bag (0, 1-19, 20+) and health band, us vs them, with deaths per 100 rounds, and the
# share of those rounds with an enemy champion within 8.
# usage: python -I tools/replay/hpbag.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
HB = lambda f: '<35' if f < 0.35 else '35-50' if f < 0.5 else '50-75' if f < 0.75 else '75+'
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    for k in range(1, len(rows)):
        q, r = rows[k - 1], rows[k]
        if r['r'] > 1000: break
        for i in range(n):
            p = q['c'][i]
            if not (p['a'] and 'x' in p): continue
            g = p.get('g', 0)
            b = '0' if g == 0 else '1-19' if g < 20 else '20+'
            h = HB(p['hp'] / max(1, p['mhp']))
            seen = any(e['a'] and 'x' in e and e['t'] != p['t'] and D.dist((p['x'], p['y']), (e['x'], e['y'])) <= 8 for e in q['c'])
            w = D.who(p['t'], us)
            C[(w, b, h, 'r')] += 1; C[(w, b, h, 'd')] += not r['c'][i]['a']; C[(w, b, h, 's')] += seen
print(f'{ng} games to r1000: alive rounds per game / deaths per 100 rounds / share with an enemy within 8')
for b in ('0', '1-19', '20+'):
    for h in ('<35', '35-50', '50-75', '75+'):
        print(f'  bag {b:4} hp {h:5} ' + '   '.join(f"{w} {C[(w, b, h, 'r')] / ng:5.0f}/{100 * C[(w, b, h, 'd')] / max(1, C[(w, b, h, 'r')]):5.2f}/{C[(w, b, h, 's')] / max(1, C[(w, b, h, 'r')]):.2f}" for w in ('us', 'them')))
