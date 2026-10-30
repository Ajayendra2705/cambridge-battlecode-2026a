# Gems a side gains on camp-group tiles by group class, to round R: clusters only (gem clusters, by region: own half,
# middle, enemy half, from the gainer's distance to each side's start tiles with a 6-tile margin), clusters of both kinds,
# mixed (wolves or elks), big (golem or monolith), and gains off any group (kills). Per game: gems and gains.
# python -I tools/replay/gclass.py R SIZE|0 DIR...  (SIZE 0 = every team size)
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R, size = int(sys.argv[1]), int(sys.argv[2])
G = collections.Counter(); N = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[3:]):
    n = len(rows[0]['c'])
    if size and n != 2 * size: continue
    ng += 1
    camps = {int(k): v for k, v in meta.get('camps', {}).items()}
    grp, members, tiles = D.camp_groups(rows, n)
    spawn = {t: [(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c] for t in (0, 1)}
    cls = {}
    for g, js in members.items():
        ts = {D.CAMPS.get(camps.get(j), '?') for j in js}
        cls[g] = 'gem only' if ts == {'gem'} else 'clusters' if ts <= {'gem', 'gold'} else 'big' if ts & {'golem', 'monolith'} else 'mixed'
    tile_g = {t: g for g, ts in tiles.items() for t in ts}
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i, c in enumerate(b['c']):
            if not (c['a'] and a['c'][i]['a'] and 'x' in c) or c.get('g', 0) <= a['c'][i].get('g', 0): continue
            q = (c['x'], c['y']); g = tile_g.get(q)
            k = cls.get(g, 'off group') if g is not None else 'off group'
            if k == 'gem only':
                dm = min(D.dist(q, s) for s in spawn[c['t']]); dt = min(D.dist(q, s) for s in spawn[1 - c['t']])
                k += ' own' if dm < dt - 6 else ' enemy' if dt < dm - 6 else ' middle'
            w = D.who(c['t'], us)
            G[(w, k)] += c['g'] - a['c'][i]['g']; N[(w, k)] += 1
print(f'{ng} games to r{R}: gems a game (gains a game) on group tiles by group class')
for k in sorted({k[1] for k in G}):
    print(f'  {k:16}', '   '.join(f'{w} {G[(w, k)] / max(1, ng):6.1f} ({N[(w, k)] / max(1, ng):4.1f})' for w in ('us', 'them')))
