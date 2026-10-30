# usage: python -I tools/replay/early2.py DIR...
# Deaths by round band, us vs them, and win share by our early deaths minus theirs (to r300). python -I early2.py DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
B = (0, 100, 200, 300, 500, 1001)
dz = collections.Counter(); ng = 0; by = collections.defaultdict(lambda: [0, 0])
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c']); e = collections.Counter()
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        for i in range(min(n, len(b['c']))):
            if a['c'][i]['a'] and not b['c'][i]['a']:
                w = D.who(b['c'][i]['t'], us)
                band = next(k for k in range(len(B) - 1) if B[k] <= b['r'] < B[k + 1])
                dz[(w, band)] += 1
                if b['r'] < 300: e[w] += 1
    k = max(-3, min(3, e['us'] - e['them']))
    by[k][0] += res == 'win'; by[k][1] += 1
print(ng, 'games; deaths per game by band', ' '.join(f'r{B[k]}-{B[k+1]}: {dz[("us", k)]/ng:.2f}/{dz[("them", k)]/ng:.2f}' for k in range(len(B) - 1)))
print('our deaths minus theirs to r300 -> wins/games:', ' '.join(f'{k:+d}: {by[k][0]}/{by[k][1]}' for k in sorted(by)))
