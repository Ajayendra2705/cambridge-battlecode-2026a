"""Deaths per 1000 alive champion-rounds by bag class (0, 1-29, 30-59, 60+), us vs them, to r1000; and the share of
those rounds with an enemy champion within 8. python -I tools/replay/bagrate.py DIR... (from the repo root)"""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
R = collections.Counter(); ng = 0
cls = lambda g: '0' if g == 0 else '1-29' if g < 30 else '30-59' if g < 60 else '60+'
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    end = next((k for k, r in enumerate(rows) if r['r'] > 1000), len(rows))
    for k in range(1, end):
        a, b = rows[k - 1], rows[k]
        for i in range(n):
            pc = a['c'][i]
            if not pc['a'] or 'x' not in pc: continue
            w = D.who(pc['t'], us); c = cls(pc.get('g', 0)); p = (pc['x'], pc['y'])
            R[(w, c)] += 1
            if any(o['a'] and 'x' in o and o['t'] != pc['t'] and D.dist((o['x'], o['y']), p) <= 8 for o in a['c']): R[(w, c, 'e8')] += 1
            if not b['c'][i]['a']: R[(w, c, 'd')] += 1
print(ng, 'games: deaths per 1000 alive rounds by bag (share of rounds with an enemy within 8)')
for c in ('0', '1-29', '30-59', '60+'):
    print(f'  bag {c:6}', ' | '.join(f'{w} {1000 * R[(w, c, "d")] / max(1, R[(w, c)]):5.2f} ({R[(w, c, "e8")] / max(1, R[(w, c)]):.2f}, {R[(w, c)] / ng:4.0f} rounds)' for w in ('us', 'them')))
