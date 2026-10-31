# Dashes per champion type and side to r1000 (slot-1 casts of Vesper, Vendetta, Issac, Ren and Heart of Ruin), split by
# the nearest enemy champion at the dash (within 4, 5-8, none within 8: a travel dash), per game of that type; and the
# dash rounds per alive round. The tl1 metric (10-31).
# usage: python -I tools/replay/dashes.py DIR...
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
DASH = {'vesper', 'vendetta', 'issac', 'ren', 'heart'}
C = collections.Counter(); G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    for c in rows[0]['c']: G[(D.who(c['t'], us), D.NAMES[c['ty']])] += 1
    for b in rows:
        if b['r'] > 1000: break
        for i, acts in enumerate(b['act'][:n]):
            c = b['c'][i]; ty = D.NAMES[c['ty']]
            if ty not in DASH or not c['a']: continue
            k = (D.who(c['t'], us), ty); C[k + ('alive',)] += 1
            if not any(x[0] == 'cast' and x[1] == 1 for x in acts): continue
            near = min((D.dist((c['x'], c['y']), (o['x'], o['y'])) for o in b['c'] if o['t'] != c['t'] and o['a'] and 'x' in o), default=99)
            C[k + ('<=4' if near <= 4 else '5-8' if near <= 8 else 'travel',)] += 1
for k in sorted(G):
    if k[1] not in DASH: continue
    g = G[k]; a = C[k + ('alive',)]
    tot = sum(C[k + (b,)] for b in ('<=4', '5-8', 'travel'))
    print(f"{k[1]:9} {k[0]:4} games {g:3}: dashes {tot / g:6.1f} a game (enemy within 4 {C[k + ('<=4',)] / g:5.1f}, 5-8 {C[k + ('5-8',)] / g:5.1f}, "
          f"none within 8 {C[k + ('travel',)] / g:5.1f}); per 100 alive rounds {100 * tot / max(1, a):4.1f}")
