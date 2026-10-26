"""Time budget per champion-round to round R, us vs them: python -I tools/replay/budget.py R DIR...
Each alive champion-round goes to the first matching activity: hit champion, hit camp, cast other (ward etc.),
tribute (bag fell to 0 next round while alive, or bag unchanged and standing next to... approximated by bag drop),
capture (standing on a tile of a dead group), at home (within 3 of own start tiles), walking (moved), idle (none).
Also: dead rounds, and walking split by bag (empty / carrying) and by health (90%+ / below)."""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
R = int(sys.argv[1])
A = collections.Counter(); T = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    tile_grp = {t: g for g, ts in gtiles.items() for t in ts}
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    # Tribute channel: rounds in which the bag later drops to zero without a death, counted back while standing still.
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if a['r'] > R: break
        for i in range(n):
            c = a['c'][i]
            w = D.who(c['t'], us)
            T[w] += 1
            if not c['a'] or 'x' not in c: A[(w, 'dead')] += 1; continue
            acts = a['act'][i] if i < len(a['act']) else []
            p = (c['x'], c['y'])
            nb = b['c'][i]
            moved = 'x' in nb and (nb['x'], nb['y']) != p
            if D.enemy_hits(a, i, n): act = 'hit champion'
            elif D.camp_hits(a, i): act = 'hit camp'
            elif nb['a'] and c.get('g', 0) > 0 and nb.get('g', 0) == 0: act = 'tribute done'
            elif not moved and p in tile_grp and all(a['mh'][j] == 0 for j in members[tile_grp[p]]): act = 'on dead group'
            elif min(D.dist(p, q) for q in start[c['t']]) <= 3 and not moved: act = 'home still'
            elif moved:
                act = 'walk ' + ('bag' if c.get('g', 0) >= 20 else 'empty') + (' hurt' if c['hp'] < 0.9 * c['mhp'] else '')
            elif acts: act = 'other action'
            else: act = 'idle away'
            A[(w, act)] += 1
print(f'{ng} games to r{R}: share of champion-rounds (alive or dead), us / them')
keys = sorted({k[1] for k in A}, key=lambda k: -(A[('us', k)] + A[('them', k)]))
for k in keys:
    u, t = A[('us', k)] / T['us'], A[('them', k)] / T['them']
    print(f'  {k:16} {u:.3f} / {t:.3f}  ({u - t:+.3f})')
