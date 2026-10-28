"""Captures by camp group, us vs them, with the map's own group ids and zones (h3, 10-28).

usage: python -I tools/helper3/h3_groups.py MAPDUMP DIR [DIR ...] [--rounds 300,1000] [--games]

MAPDUMP is the md1 dump of the map (data/maps_txt/<map>.txt); group ids and zones are those of
tools/helper3/h3_layout.py (zone A / B / mid by open walking steps from the spawns; team A = side a = team 0).
A capture event is a round in which champions of one side standing on a group's tiles gain gems or gold without a kill
(the reward is split among those present). Games where we are side b are mirrored through the map's symmetry, so a
group id and its zone column are always seen from our spawn ("own" = our side); the zone totals are from the capturer's
view. Per group and side: captures per game and gems per game to each round. --games prints each game's capture list
(U = us, T = them, group ids as in the table).
"""
import collections, os, statistics, sys

sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]
RS = [300, 1000]
if '--rounds' in args:
    i = args.index('--rounds'); RS = [int(x) for x in args[i + 1].split(',')]; del args[i:i + 2]
show = '--games' in args
args = [a for a in args if a != '--games']
dump, dirs = args[0], args[1:]
CAMP = {'w': 'wolf', 'E': 'elk', 'g': 'gem', '$': 'gold', 'G': 'golem', 'M': 'monolith'}
L = open(dump, encoding='utf-8').read().splitlines()
W, H = int(L[0].split()[2]), int(L[0].split()[3])
g = [list(l) for l in L[1:1 + H]]
tile_grp, groups = {}, []
for y in range(H):
    for x in range(W):
        if g[y][x] in CAMP and (x, y) not in tile_grp:
            st = [(x, y)]; tile_grp[(x, y)] = len(groups); comp = []
            while st:
                cx, cy = st.pop(); comp.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    t = (cx + dx, cy + dy)
                    if 0 <= t[0] < W and 0 <= t[1] < H and g[t[1]][t[0]] in CAMP and t not in tile_grp:
                        tile_grp[t] = len(groups); st.append(t)
            groups.append(comp)
# zone per group from the layout tool's rule (open BFS steps from each spawn, 6+ nearer)
D8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]


def bfs(own, other):
    dist = {}; q = collections.deque()
    for y in range(H):
        for x in range(W):
            if g[y][x] == own: dist[(x, y)] = 0; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in D8:
            t = (x + dx, y + dy)
            if not (0 <= t[0] < W and 0 <= t[1] < H) or t in dist: continue
            c = g[t[1]][t[0]]
            if c in '#oA' or c == other: continue
            dist[t] = dist[(x, y)] + 1; q.append(t)
    return dist


dA, dB = bfs('S', 's'), bfs('s', 'S')


def near(comp, dist):
    return min((dist[(x + dx, y + dy)] for x, y in comp for dx, dy in D8 if (x + dx, y + dy) in dist), default=999)


zoneA = {}
desc = {}
for i, comp in enumerate(groups):
    a, b = near(comp, dA), near(comp, dB)
    zoneA[i] = 'own' if a + 6 <= b else 'enemy' if b + 6 <= a else 'mid'
    k = collections.Counter(CAMP[g[y][x]] for x, y in comp)
    desc[i] = ' '.join(f'{v}{n}' for n, v in sorted(k.items())) + f' x{min(p[0] for p in comp)}-{max(p[0] for p in comp)} y{min(p[1] for p in comp)}-{max(p[1] for p in comp)}'


def zone(i, team):  # zone seen from a team (team 0 = A)
    z = zoneA[i]
    return z if team == 0 or z == 'mid' else ('enemy' if z == 'own' else 'own')


# the map symmetry that sends team A's spawn onto team B's: games where we are side b are mirrored through it, so a
# group id always names the group as seen from our spawn (the table's zone column is then our zone)
SA = {(x, y) for y in range(H) for x in range(W) if g[y][x] == 'S'}
SB = {(x, y) for y in range(H) for x in range(W) if g[y][x] == 's'}
TF = [lambda x, y: (W - 1 - x, H - 1 - y), lambda x, y: (W - 1 - x, y), lambda x, y: (x, H - 1 - y)]
tf = next((f for f in TF if {f(*p) for p in SA} == SB), TF[0])
mirror = {}
for i, comp in enumerate(groups):
    mirror[i] = tile_grp.get(tf(*comp[0]), i)


near2 = collections.defaultdict(set)  # tile -> groups with a tile within Chebyshev 2
for i, comp in enumerate(groups):
    for x, y in comp:
        for dx in range(-2, 3):
            for dy in range(-2, 3): near2[x + dx, y + dy].add(i)
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(dirs):
    ng += 1
    n = len(rows[0]['c'])
    ev = collections.defaultdict(lambda: [0, 0])  # (round, side, group) -> [gems, gold]
    for a, b in zip(rows, rows[1:]):
        for i in range(n):
            c, pc = b['c'][i], a['c'][i]
            if not (c['a'] and pc['a']) or c.get('k', 0) > pc.get('k', 0): continue
            dg, dau = c.get('g', 0) - pc.get('g', 0), c.get('au', 0) - pc.get('au', 0)
            if dg <= 0 and dau <= 0: continue
            if c.get('g', 0) < pc.get('g', 0): continue  # a tribute or death round, not a capture
            grp = tile_grp.get((c.get('x'), c.get('y')))
            if grp is None: grp = tile_grp.get((pc.get('x'), pc.get('y')))
            if grp is None: continue
            e = ev[b['r'], c['t'], grp]; e[0] += max(0, dg); e[1] += max(0, dau)
        if b['r'] <= RS[-1]:  # camp hits on the group's tiles and alive champion-rounds within 2 of it
            for i in range(n):
                c = b['c'][i]
                w = 'us' if c['t'] == us else 'them'
                for x in D.camp_hits(b, i):
                    gh = tile_grp.get((x[-4], x[-3]))
                    if gh is not None: C[w, 'hits', mirror[gh] if us == 1 else gh] += 1
                if c['a'] and 'x' in c:
                    for gn in near2.get((c['x'], c['y']), ()): C[w, 'near', mirror[gn] if us == 1 else gn] += 1
    caps = sorted(((r, t, mirror[grp] if us == 1 else grp), v) for (r, t, grp), v in ev.items())
    for (r, t, grp), (gm, au) in caps:
        if au == 0 and gm == 0: continue
        w = 'us' if t == us else 'them'
        zn = zone(grp, 0 if w == 'us' else 1)  # grp is already seen from our spawn (as team A)
        for R in RS:
            if r <= R:
                C[w, R, grp, 'n'] += 1; C[w, R, grp, 'gems'] += gm
                C[w, R, zn, 'zn'] += 1; C[w, R, zn, 'zgems'] += gm
    if show:
        print(f'{meta.get("file", "")[:8]} {res} us={"ab"[us]}: ' + ' '.join(
            f'{r}{"U" if t == us else "T"}{grp}:{gm}' for (r, t, grp), (gm, au) in caps if r <= 1000))
print(f'{ng} games; captures per game (gems per game) by group, to ' + ', '.join(f'r{R}' for R in RS))
print('grp zone(A) kinds                                ' + ''.join(f'| r{R} us n gems  them n gems ' for R in RS))
for i in range(len(groups)):
    if not any(C[w, R, i, 'n'] for w in ('us', 'them') for R in RS): continue
    print(f'{i:3} {zoneA[i]:6} {desc[i]:40} ' + ''.join(
        f'| {C["us", R, i, "n"] / ng:5.2f} {C["us", R, i, "gems"] / ng:5.1f}  {C["them", R, i, "n"] / ng:5.2f} {C["them", R, i, "gems"] / ng:5.1f} '
        for R in RS))
print(f'to r{RS[-1]}, per game: camp hits on the group, alive champion-rounds within 2 of it (us / them)')
for i in range(len(groups)):
    if not any(C[w, k, i] for w in ('us', 'them') for k in ('hits', 'near')): continue
    print(f'{i:3} {zoneA[i]:6} {desc[i]:40} hits {C["us", "hits", i] / ng:6.1f} / {C["them", "hits", i] / ng:6.1f}'
          f'   near {C["us", "near", i] / ng:6.0f} / {C["them", "near", i] / ng:6.0f}')
for R in RS:
    print(f'r{R} by zone from the capturer: ' + '  |  '.join(w + ' ' + ', '.join(
        f'{z} {C[w, R, z, "zn"] / ng:.2f} caps {C[w, R, z, "zgems"] / ng:.0f} gems' for z in ('own', 'mid', 'enemy')) for w in ('us', 'them')))
