"""Team cohesion, us vs the rivals, by team size and round band (to round 1000).

usage: python -I tools/replay/cohesion.py DIR [DIR ...]

Per alive champion-round: allies within 6 (mean) and the share with none ("alone"). Per camp-hit champion-round: the
share in which a teammate hits the same group in that round ("shared"). Groups are decoded.py's camp_groups (camps that
touch cardinally, from the camps hit in the game). DIR is a decoded folder (tools/replay/decode_run.sh,
tools/local/local_decode.sh).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

BANDS = ((0, 150), (150, 300), (300, 600), (600, 1000))
C = collections.Counter()
G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    size = n // 2
    G[size] += 1
    grp, members, tiles = D.camp_groups(rows, n)
    for r in rows:
        if r['r'] >= 1000: break
        band = next(b for b in BANDS if b[0] <= r['r'] < b[1])
        for i in range(n):
            p = r['c'][i]
            if not p['a'] or 'x' not in p: continue
            w = D.who(p['t'], us)
            al = sum(1 for o in r['c'] if o['a'] and 'x' in o and o['t'] == p['t'] and o is not p
                     and D.dist((p['x'], p['y']), (o['x'], o['y'])) <= 6)
            C[(size, band, w, 'n')] += 1
            C[(size, band, w, 'allies')] += al
            C[(size, band, w, 'alone')] += al == 0
        hitters = collections.defaultdict(set)
        for i in range(min(n, len(r['act']))):
            for x in D.camp_hits(r, i):
                if x[-1] in grp: hitters[(r['c'][i]['t'], grp[x[-1]])].add(i)
        for (t, g), s in hitters.items():
            w = D.who(t, us)
            C[(size, band, w, 'hits')] += len(s)
            C[(size, band, w, 'shared')] += len(s) if len(s) >= 2 else 0
print('per alive champion-round: allies within 6, share alone; per camp-hit round: share with a teammate on the group'
      ' (us / them)')
for size in sorted(G):
    for band in BANDS + ('all',):
        bs = BANDS if band == 'all' else (band,)
        f = lambda w, k, d: sum(C[(size, b, w, k)] for b in bs) / max(1, sum(C[(size, b, w, d)] for b in bs))
        name = 'r0-1000' if band == 'all' else f'r{band[0]}-{band[1]}'
        print(f"  size {size} ({G[size]:3} games) {name:9}  allies {f('us', 'allies', 'n'):.2f}/{f('them', 'allies', 'n'):.2f}"
              f"  alone {f('us', 'alone', 'n'):.2f}/{f('them', 'alone', 'n'):.2f}  shared {f('us', 'shared', 'hits'):.2f}/{f('them', 'shared', 'hits'):.2f}")
