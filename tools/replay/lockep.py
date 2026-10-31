# Lock episodes: our hits on one altar (all our champions, gaps <= 10 rounds). Per episode: total hits, hitters, max bag
# of a hitter, whether we tributed at that altar within 20 rounds after, and how the bag of the main hitter ended.
import sys, collections
sys.path.insert(0, r'C:\Users\ajiit\Desktop\Future\Projects\Cambridge Battlecode\tools\replay')
import decoded as D
C = collections.Counter(); ng = 0; H = collections.Counter(); lost = []
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    altars = set(); tr = collections.defaultdict(list)
    for r in rows:
        for i in range(min(n, len(r['act']))):
            for x in r['act'][i]:
                if x[0] == 'tribute':
                    altars.add((x[1], x[2]))
                    if D.who(r['c'][i]['t'], us) == 'us': tr[(x[1], x[2])].append(r['r'])
    eps = collections.defaultdict(list)  # altar -> list of [first, last, hits, hitters set, maxbag]
    for k, r in enumerate(rows):
        for i in range(min(n, len(r['act']))):
            c = r['c'][i]
            if D.who(c['t'], us) != 'us': continue
            for x in r['act'][i]:
                if x[0] == 'attack' and len(x) == 3 and (x[1], x[2]) in altars:
                    L = eps[(x[1], x[2])]
                    if L and r['r'] - L[-1][1] <= 10:
                        e = L[-1]; e[1] = r['r']; e[2] += 1; e[3].add(i); e[4] = max(e[4], c.get('g', 0))
                    else: L.append([r['r'], r['r'], 1, {i}, c.get('g', 0)])
    for a, L in eps.items():
        for f, l, h, hs, bag in L:
            after = any(l <= t <= l + 20 for t in tr[a])
            kind = 'broken' if h >= 5 else 'short'
            C[(kind, 'tributed' if after else 'no tribute')] += 1
            H[min(h, 6)] += 1
            if kind == 'short' and not after: lost.append((mp, f, l, h, len(hs), bag))
print(ng, 'games; lock episodes by hits:', sorted(H.items()))
for k, v in sorted(C.items()): print(' ', k, v, f'{v/ng:.2f}/game')
print('short, no tribute (map, first, last, hits, hitters, max bag):'); [print('  ', x) for x in lost[:40]]
