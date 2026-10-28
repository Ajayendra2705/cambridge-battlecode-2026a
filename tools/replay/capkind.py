"""Captures per game to r1000 by group kind (the set of camp types in the group, e.g. gem, gold, wolf+gold, elk+gem) and
region (own half / middle / enemy half, from the capturer's side, by distance to each side's start tiles), us vs them,
with the capturer's gems and gold per game and the capture rounds' quartiles; then captures per kind over all regions.

usage: python -I tools/replay/capkind.py DIR [DIR ...] [--size N] [--map SUBSTR] [--permap KIND:REGION|KIND:all]
       [--skip MAPSUBSTR,...]
--size keeps games with N champions per side; --map keeps maps whose name contains SUBSTR; --permap adds captures per
game by map for one kind and region (or all regions), sorted by their lead. A capture is the first champion whose bag
or gold rises on a tile of the group after its last camp died; a split reward counts that champion's share only.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
args = sys.argv[1:]
if '--skip' in args:
    k = args.index('--skip'); D.SKIP = args[k + 1].split(','); args = args[:k] + args[k + 2:]
SIZE = None
if '--size' in args:  # only games with this many champions per side
    k = args.index('--size'); SIZE = int(args[k + 1]); args = args[:k] + args[k + 2:]
ONLY = None
if '--map' in args:  # only games on maps whose name contains this
    k = args.index('--map'); ONLY = args[k + 1]; args = args[:k] + args[k + 2:]
PERMAP = None
if '--permap' in args:  # also captures per game by map for one kind and region, e.g. gem:middle
    k = args.index('--permap'); PERMAP = tuple(args[k + 1].split(':')); args = args[:k] + args[k + 2:]
M = collections.Counter()
N = collections.Counter(); ng = 0; RND = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n // 2 != SIZE: continue
    if ONLY and ONLY not in mp: continue
    ng += 1; M[(mp, 'games')] += 1
    grp, members, gtiles = D.camp_groups(rows, n)
    ctype = {int(k): v for k, v in (meta.get('camps') or {}).items()}
    kind = {}
    for g, js in members.items():
        ts = sorted({ctype.get(j, -1) for j in js})
        kind[g] = '+'.join(D.CAMPS.get(t, '?') for t in ts)
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    pending = set()
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        for g, js in members.items():
            if any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js): pending.add(g)
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            pending.discard(g)
            w = D.who(c['t'], us)
            do = min(D.dist(p, q) for q in start[c['t']]); de = min(D.dist(p, q) for q in start[1 - c['t']])
            region = 'own' if do < de - 3 else 'enemy' if de < do - 3 else 'middle'
            K = kind[g]
            N[(w, K, region)] += 1; N[(w, K, region, 'g')] += c['g'] - pc['g']; N[(w, K, region, 'au')] += c.get('au', 0) - pc.get('au', 0)
            RND[(w, K, region)].append(b['r'])
            if PERMAP in ((K, region), (K, 'all')): M[(mp, w)] += 1
kinds = collections.Counter()
for (w, K, region, *rest) in N:
    if not rest: kinds[K] += N[(w, K, region)]
print(f'{ng} games to r1000: captures per game (gems, gold) by group kind and region, us | them')
for K, _ in kinds.most_common(12):
    for region in ('own', 'middle', 'enemy'):
        cells = []
        for w in ('us', 'them'):
            m = N[(w, K, region)]
            q = sorted(RND[(w, K, region)])
            cells.append(f'{m / ng:5.2f} ({N[(w, K, region, "g")] / ng:5.1f} g, {N[(w, K, region, "au")] / ng:5.1f} au; r{q[len(q) // 4] if q else 0}-{q[3 * len(q) // 4] if q else 0})')
        print(f'  {K:22} {region:6} ' + ' | '.join(cells))
print('all regions: captures per game by kind, us | them')
for K, _ in kinds.most_common(12):
    print(f'  {K:22} ' + ' | '.join(f'{sum(N[(w, K, r)] for r in ("own", "middle", "enemy")) / ng:5.2f}' for w in ('us', 'them')))
if PERMAP:
    print(f'{PERMAP[0]} {PERMAP[1]} captures per game by map, us | them')
    for mp in sorted({k[0] for k in M}, key=lambda m: -(M[(m, 'them')] - M[(m, 'us')]) / M[(m, 'games')]):
        g = M[(mp, 'games')]
        print(f'  {mp:26} {g:2} games  {M[(mp, "us")] / g:5.2f} | {M[(mp, "them")] / g:5.2f}')
