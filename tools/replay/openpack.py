"""Opening pack per map, on 5-pick maps: rounds 15-45, per side, mean teammates within 6 per alive champion-round.

usage: python -I tools/replay/openpack.py DIR...   (decoded runs; one line per map, then all maps)
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
A = collections.defaultdict(lambda: [0, 0, 0])  # (map, side): teammates-within-6 sum, champion-rounds, games
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    tm = [c.get('t') for c in rows[0]['c']]
    size = collections.Counter(tm)
    if max(size.values()) < 5: continue
    for side in (0, 1):
        w = D.who(side, us)
        A[mp, w][2] += 1
    for r in rows:
        if r['r'] < 15 or r['r'] > 45: continue
        for side in (0, 1):
            w = D.who(side, us)
            pts = [(c['x'], c['y']) for i, c in enumerate(r['c']) if tm[i] == side and c.get('a') and 'x' in c]
            for p in pts:
                k = sum(1 for q in pts if q != p and D.dist(p, q) <= 6)
                A[mp, w][0] += k; A[mp, w][1] += 1
maps = sorted({m for m, w in A})
print('%-22s %6s %6s' % ('map (5-pick)', 'us', 'them'))
tot = collections.Counter()
for m in maps:
    u, t = A[m, 'us'], A[m, 'them']
    if not u[1] or not t[1]: continue
    print('%-22s %6.2f %6.2f  (%d games)' % (m, u[0] / u[1], t[0] / t[1], u[2]))
    for w, x in (('us', u), ('them', t)): tot[w, 0] += x[0]; tot[w, 1] += x[1]
print('%-22s %6.2f %6.2f' % ('all', tot['us', 0] / tot['us', 1], tot['them', 0] / tot['them', 1]))
