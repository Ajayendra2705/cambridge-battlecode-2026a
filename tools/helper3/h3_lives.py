"""Where our farming rounds go: camp hits per group life by who captured it, us vs them, to round R (h3, 10-28).

usage: python -I tools/helper3/h3_lives.py [--upto R] DIR [DIR ...]   (default R 1000; decoded runs, pooled)

Groups are `decoded.camp_groups` (camps that touch cardinally, from the camps hit in the game), typed by their
strongest camp. A capture is a round in which champions of one side standing on (or next to) a group's tiles gain gems
or gold without a kill; it ends that group's life. Each champion's camp-hit round (attack or cast on a camp) is
charged to the life it hit: captured by its own side ("own"), by the other side ("lost": we woke or wore it down, they
took it), or not captured by R ("open"). Per side and group type: hit rounds per game in each class, own captures
per game, gems per own capture, hit rounds per own capture, and gems per hit round over all hits.
"""
import bisect, collections, os, sys

sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]
R = 1000
if '--upto' in args:
    i = args.index('--upto'); R = int(args[i + 1]); del args[i:i + 2]
RANK = {'monolith': 5, 'golem': 4, 'elk': 3, 'wolf': 2, 'gem': 1, 'gold': 1}
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    camps = {int(k): v for k, v in meta.get('camps', {}).items()}
    grp, members, gtiles = D.camp_groups(rows, n)
    tile_grp = {t: g for g, ts in gtiles.items() for t in ts}
    kind = {}
    for g, js in members.items():
        best = max((D.CAMPS.get(camps.get(j), 'gem') for j in js), key=lambda t: RANK.get(t, 0))
        kind[g] = 'clusters' if RANK.get(best, 0) == 1 else best
    caps = collections.defaultdict(dict)  # group -> {round: [side, gems]}
    hits = []  # (round, side, group)
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if b['r'] > R: break
        for i in range(n):
            c, nb = a['c'][i], b['c'][i]
            for x in D.camp_hits(a, i):
                g = grp.get(x[-1])
                if g is not None: hits.append((a['r'], c['t'], g))
            if not (c['a'] and nb['a']) or nb.get('k', 0) > c.get('k', 0): continue
            dg, dau = nb.get('g', 0) - c.get('g', 0), nb.get('au', 0) - c.get('au', 0)
            if dg < 0 or (dg == 0 and dau <= 0) or 'x' not in nb: continue
            p = (nb['x'], nb['y'])
            g = tile_grp.get(p)
            if g is None:
                near = [tile_grp[(p[0] + dx, p[1] + dy)] for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (p[0] + dx, p[1] + dy) in tile_grp]
                g = near[0] if near else None
            if g is None: continue
            e = caps[g].setdefault(b['r'], [c['t'], 0]); e[1] += max(0, dg)
    ends = {g: sorted(v) for g, v in caps.items()}
    for r, t, g in hits:
        w = 'us' if t == us else 'them'
        lst = ends.get(g, [])
        j = bisect.bisect_left(lst, r + 1)  # the first capture after this hit ends its life
        if j >= len(lst): cls = 'open'
        else: cls = 'own' if caps[g][lst[j]][0] == t else 'lost'
        C[w, kind.get(g, '?'), cls] += 1; C[w, 'all', cls] += 1
    for g, v in caps.items():
        for r, (t, gm) in v.items():
            w = 'us' if t == us else 'them'
            C[w, kind.get(g, '?'), 'caps'] += 1; C[w, kind.get(g, '?'), 'gems'] += gm
            C[w, 'all', 'caps'] += 1; C[w, 'all', 'gems'] += gm
print(f'{ng} games to r{R}: ' + ', '.join(args))
print('per game: camp-hit rounds on lives captured by own side / by the other side / open; own captures, gems per'
      ' capture, own-life hit rounds per capture; gems per hit round (all hits)')
for kd in ('all', 'monolith', 'golem', 'elk', 'wolf', 'clusters'):
    for w in ('us', 'them'):
        h = {c: C[w, kd, c] / ng for c in ('own', 'lost', 'open')}
        tot = sum(h.values())
        if not tot and not C[w, kd, 'caps']: continue
        cp = C[w, kd, 'caps'] / ng
        print(f'  {kd:9} {w:4} hits own {h["own"]:6.1f} lost {h["lost"]:5.1f} ({h["lost"] / max(1e-9, tot):4.0%}) open {h["open"]:5.1f}'
              f' | caps {cp:5.2f} gems/cap {C[w, kd, "gems"] / max(1, C[w, kd, "caps"]):5.1f}'
              f' own hits/cap {h["own"] / max(1e-9, cp):5.1f} | gems/hit {C[w, kd, "gems"] / max(1, C[w, kd, "own"] + C[w, kd, "lost"] + C[w, kd, "open"]):.3f}')
