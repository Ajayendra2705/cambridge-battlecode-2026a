"""Does acting first pay, by distance? Natural experiment on pairs whose order flips within a game.

usage: python -I tools/replay/firstpay.py ORDERS_DIR FIGHTS_DIR
For each round (1-1000) and each pair (our X, their Y), both alive, Chebyshev distance d at the round start (1..9):
who acted first, and hits between them this round and the next (attack or cast with the other as target).
Only pairs that occur with both orders at that distance in the game are used (controls for the champion types).
"""
import collections, gzip, json, os, sys

orders, fights = sys.argv[1], sys.argv[2]
side, opp_kind = {}, {}
for line in open(os.path.join(fights, 'index.txt'), encoding='utf-8'):
    p = line.split()
    if len(p) >= 3: side[p[0]] = 0 if p[2] == 'a' else 1

def hits_of(r):
    out = collections.Counter()
    for i, acts in enumerate(r.get('act') or []):
        for a in acts:
            if a[0] == 'attack' and len(a) >= 5 and a[3] == 'c': out[i, a[4], 'a'] += 1
            elif a[0] == 'cast' and len(a) >= 6 and a[4] == 'c': out[i, a[5], 'c'] += 1
    return out

T = collections.defaultdict(collections.Counter)
for stem, us in side.items():
    fo, ff = os.path.join(orders, stem + '.json'), os.path.join(fights, stem + '.jsonl.gz')
    if not (os.path.exists(fo) and os.path.exists(ff)): continue
    g = json.load(open(fo))
    teams, rounds = g['teams'], g['rounds']
    reord = len({tuple(i for i in o if teams[i] != us) for _, o, _ in rounds}) >= 4
    F = {}
    for x in gzip.open(ff, 'rt'):
        if not x.strip(): continue
        r = json.loads(x)
        if 'r' in r and r['r'] <= 1001: F[r['r']] = hits_of(r)
    recs = collections.defaultdict(list)   # (X, Y, d) -> [(first, xy_now, yx_now, xy_next, yx_next)]
    for r, o, s in rounds:
        if r > 1000: break
        pos = {i: k for k, i in enumerate(o)}
        h0, h1 = F.get(r, {}), F.get(r + 1, {})
        for X in range(len(teams)):
            if teams[X] != us or not s[X][4] or X not in pos: continue
            for Y in range(len(teams)):
                if teams[Y] == us or not s[Y][4] or Y not in pos: continue
                d = max(abs(s[X][0] - s[Y][0]), abs(s[X][1] - s[Y][1]))
                if d > 9: continue
                xy = h0.get((X, Y, 'a'), 0) + h0.get((X, Y, 'c'), 0)
                yx = h0.get((Y, X, 'a'), 0) + h0.get((Y, X, 'c'), 0)
                xy1 = h1.get((X, Y, 'a'), 0) + h1.get((X, Y, 'c'), 0)
                yx1 = h1.get((Y, X, 'a'), 0) + h1.get((Y, X, 'c'), 0)
                yc = h0.get((Y, X, 'c'), 0)
                xc = h0.get((X, Y, 'c'), 0)
                recs[X, Y, d].append((pos[X] < pos[Y], xy, yx, xy1, yx1, xc, yc))
    for (X, Y, d), L in recs.items():
        if len({f for f, *_ in L}) < 2: continue
        for f, xy, yx, xy1, yx1, xc, yc in L:
            for grp in ('all', 'reorders' if reord else 'draft order'):
                c = T[grp, d, f]
                c['n'] += 1; c['xy'] += xy; c['yx'] += yx; c['xy1'] += xy1; c['yx1'] += yx1; c['xc'] += xc; c['yc'] += yc

for grp in ('all', 'draft order', 'reorders'):
    print(grp, ': per 100 pair-rounds, ours first / theirs first; "now" = this round, "+1" = next round')
    print('   d      n(F/L)      we hit now      they hit now     net now        net now+next   our casts  their casts')
    for d in range(1, 10):
        a, b = T[grp, d, True], T[grp, d, False]
        if not a['n'] or not b['n']: continue
        f = lambda c, k: 100.0 * c[k] / c['n']
        net = lambda c: f(c, 'xy') - f(c, 'yx')
        net2 = lambda c: f(c, 'xy') + f(c, 'xy1') - f(c, 'yx') - f(c, 'yx1')
        print('   %d %6d/%-6d %5.1f / %-5.1f   %5.1f / %-5.1f   %+5.1f / %+5.1f   %+5.1f / %+5.1f   %4.1f/%-4.1f  %4.1f/%-4.1f' % (
            d, a['n'], b['n'], f(a, 'xy'), f(b, 'xy'), f(a, 'yx'), f(b, 'yx'), net(a), net(b), net2(a), net2(b),
            f(a, 'xc'), f(b, 'xc'), f(a, 'yc'), f(b, 'yc')))
