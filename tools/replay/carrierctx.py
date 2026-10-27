# Deaths with a bag of 30+ to r1000 by context: channelling (a tribute action in the last 3 rounds, or standing within 1
# of an altar tile with no move in the last 2 rounds), near an altar (within 3 tiles), hitting camps in the last 5
# rounds, else elsewhere. Gems lost per game in each. Us vs them. Altar tiles = tiles tributes were made from.
# usage: python -I tools/replay/carrierctx.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    altars = {(x[1], x[2]) for b in rows for acts in b['act'][:n] for x in acts if x[0] == 'tribute'}
    for k in range(6, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if not (pc['a'] and not c['a'] and 'x' in pc) or pc.get('g', 0) < 30: continue
            w = D.who(pc['t'], us); p = (pc['x'], pc['y']); g = pc['g']
            ad = min((D.dist(p, x) for x in altars), default=99)
            trib = any(x[0] == 'tribute' for kk in range(k - 3, k) for x in (rows[kk]['act'][i] if i < len(rows[kk]['act']) else []))
            still = all(not any(x[0] == 'move' for x in (rows[kk]['act'][i] if i < len(rows[kk]['act']) else [])) for kk in range(k - 3, k))
            camp = any(D.camp_hits(rows[kk], i) for kk in range(k - 5, k))
            ctx = 'channel' if trib or (ad <= 1 and still) else 'near altar' if ad <= 3 else 'camp fight' if camp else 'elsewhere'
            C[(w, ctx)] += 1; C[(w, ctx, 'g')] += g; C[(w, 'all')] += 1; C[(w, 'all', 'g')] += g
print(f'{ng} games to r1000: deaths with 30+ gems per game (gems lost per game) by context')
for ctx in ('all', 'channel', 'near altar', 'camp fight', 'elsewhere'):
    print(f'  {ctx:11} us {C[("us", ctx)] / ng:.2f} ({C[("us", ctx, "g")] / ng:5.1f})   them {C[("them", ctx)] / ng:.2f} ({C[("them", ctx, "g")] / ng:5.1f})')
