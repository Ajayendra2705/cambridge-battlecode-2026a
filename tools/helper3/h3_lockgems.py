"""Gems captured from groups our bot can never pick (tools/helper3/h3_cover.py), us vs them, per decoded run (h3, 10-28).

usage: python -I tools/helper3/h3_lockgems.py DIR [DIR ...]

For every game whose map has blocked groups (md1 dump in data/maps_txt, map name with hyphens), sums the gems each
side captured from those groups to r1000 (capture = bag rises without a kill while standing on or next to a group
tile; games on side b mirrored through the dump's symmetry, so the blocked ids are ours). Prints per game and the total
per game over all games of the run (lock maps or not), with the run's whole collected gap for scale.
"""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'helper3'))
import decoded as D
src = open(os.path.join('tools', 'helper3', 'h3_cover.py'), encoding='utf-8').read()
ns = {}; exec(src.split('paths = sys.argv[1:]')[0], ns)
CAMP = set('wEg$GM')
cache = {}
def layout(mp):
    if mp in cache: return cache[mp]
    path = os.path.join('data', 'maps_txt', mp.replace('_', '-') + '.txt')
    if not os.path.exists(path): path = os.path.join('data', 'maps_txt', mp + '.txt')
    if not os.path.exists(path): cache[mp] = None; return None
    total, lost, out, nd, gd = ns['analyse'](path)
    blocked = {int(o.split('(')[0]) for o in out}
    L = open(path, encoding='utf-8').read().splitlines(); W, H = int(L[0].split()[2]), int(L[0].split()[3])
    g = [list(l) for l in L[1:1 + H]]
    tile, groups = {}, []
    for y in range(H):
        for x in range(W):
            if g[y][x] in CAMP and (x, y) not in tile:
                st = [(x, y)]; tile[(x, y)] = len(groups); comp = []
                while st:
                    cx, cy = st.pop(); comp.append((cx, cy))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        t = (cx + dx, cy + dy)
                        if 0 <= t[0] < W and 0 <= t[1] < H and g[t[1]][t[0]] in CAMP and t not in tile: tile[t] = len(groups); st.append(t)
                groups.append(comp)
    TF = {'rotational180': lambda x, y: (W - 1 - x, H - 1 - y), 'horizontal': lambda x, y: (W - 1 - x, y), 'vertical': lambda x, y: (x, H - 1 - y)}
    tf = TF.get(L[0].split()[4], TF['rotational180'])
    cache[mp] = (blocked, tile, tf); return cache[mp]
tot = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        for i in range(n):
            c, nb = a['c'][i], b['c'][i]
            if c['a'] and nb['a'] and nb.get('g', 0) > c.get('g', 0):
                tot['us' if c['t'] == us else 'them', 'all'] += nb['g'] - c['g']
    lay = layout(mp)
    if not lay or not lay[0]: continue
    blocked, tile, tf = lay
    got = collections.Counter()
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        for i in range(n):
            c, nb = a['c'][i], b['c'][i]
            if not (c['a'] and nb['a']) or nb.get('k', 0) > c.get('k', 0) or nb.get('g', 0) <= c.get('g', 0) or 'x' not in nb: continue
            p = (nb['x'], nb['y'])
            cand = [tile.get((p[0] + dx, p[1] + dy)) for dx in (0, -1, 1) for dy in (0, -1, 1)]
            gi = next((x for x in cand if x is not None), None)
            if gi is None: continue
            if us == 1: gi = tile.get(tf(*next(t for t, v in tile.items() if v == gi)), gi)
            if gi in blocked: got['us' if c['t'] == us else 'them'] += nb['g'] - c['g']
    tot['us', 'lock'] += got['us']; tot['them', 'lock'] += got['them']
    print(f'  {meta["file"][:8]} {mp:22} {res:4} blocked-group gems us {got["us"]:4} them {got["them"]:4}')
print(f'{ng} games: gems from blocked groups per game us {tot["us", "lock"] / ng:.1f} them {tot["them", "lock"] / ng:.1f}'
      f' (gap {(tot["us", "lock"] - tot["them", "lock"]) / ng:+.1f}); all collected us {tot["us", "all"] / ng:.0f} them {tot["them", "all"] / ng:.0f}'
      f' (gap {(tot["us", "all"] - tot["them", "all"]) / ng:+.0f})')
