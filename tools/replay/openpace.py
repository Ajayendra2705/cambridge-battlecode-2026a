"""Opening pace: how far each team has come from its start by a round, on decoded games: python -I tools/replay/openpace.py DIR...

For rounds 4, 8, 12, 16, 24, 32 and 40: mean Chebyshev distance of a living champion from its own position at the first round in the data, and the share of champions who moved in the last
round, us against them, with the team spread (largest Chebyshev distance between two teammates) and allies within 6. Maps with spawns closer than 10 tiles are left out.
"""
import collections, sys

sys.path.insert(0, 'tools/replay')
import decoded as D

D.SKIP = []
ROUNDS = (4, 8, 12, 16, 24, 32, 40)
S = collections.defaultdict(lambda: collections.Counter())
n = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    first = {}
    last = {}
    use = False
    for r in rows:
        if r['r'] > 40:
            break
        pts = {0: [], 1: []}
        for i, c in enumerate(r['c']):
            if not c.get('a') or 'x' not in c:
                continue
            first.setdefault(i, (c['x'], c['y']))
            pts[c['t']].append((i, c['x'], c['y']))
        if not use:
            # spawn gap at the first row
            a, b = pts[0], pts[1]
            if a and b and max(max(abs(x[1] - y[1]), abs(x[2] - y[2])) for x in a for y in b) >= 10:
                use = True
                n += 1
            else:
                break
        if r['r'] in ROUNDS:
            for t, ps in pts.items():
                side = 'us' if t == us else 'them'
                for i, x, y in ps:
                    fx, fy = first[i]
                    S[(r['r'], side)]['dist'] += max(abs(x - fx), abs(y - fy))
                    S[(r['r'], side)]['n'] += 1
                    S[(r['r'], side)]['moved'] += last.get(i) != (x, y)
                    S[(r['r'], side)]['near'] += sum(1 for j, u, v in ps if j != i and max(abs(u - x), abs(v - y)) <= 6)
                if ps:
                    S[(r['r'], side)]['spread'] += max(max(abs(a[1] - b[1]), abs(a[2] - b[2])) for a in ps for b in ps)
                    S[(r['r'], side)]['teams'] += 1
        for t, ps in pts.items():
            for i, x, y in ps:
                last[i] = (x, y)
print(f'{n} games')
print('round | dist from start us/them | moved share us/them | spread us/them | allies within 6 us/them')
for R in ROUNDS:
    a, b = S[(R, 'us')], S[(R, 'them')]
    if not a['n'] or not b['n']:
        continue
    print(f"r{R:<4} | {a['dist'] / a['n']:5.1f} {b['dist'] / b['n']:5.1f} | {a['moved'] / a['n']:.2f} {b['moved'] / b['n']:.2f} | {a['spread'] / a['teams']:5.1f} {b['spread'] / b['teams']:5.1f} | {a['near'] / a['n']:.2f} {b['near'] / b['n']:.2f}")
