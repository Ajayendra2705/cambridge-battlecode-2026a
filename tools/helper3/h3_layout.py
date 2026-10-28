"""Map layout from an md1 dump (data/maps_txt/<map>.txt, made by bots/probe/md1): camp groups, altars, walking distances.

usage: python -I tools/helper3/h3_layout.py data/maps_txt/01yellow-brick-road.txt [--map]

Groups are camps that touch cardinally (docs/MECHANICS.md section 7), with the engine's camp numbers (gems, gold,
health, respawn). Walking distances are 8-neighbour BFS steps from the nearest spawn tile of team A ('S') and team B
('s'); walls, holes, altars and the other team's spawn block. 'open' treats every camp as dead (tiles free), 'shut'
treats live camps as blocking. A group's distance is to the nearest free tile next to (Chebyshev 1) one of its camps.
zone: A or B when nearer that spawn by 6+ open steps, else mid. --map prints the grid with group ids (base 36).
"""
import sys, collections

CAMP = {'w': ('wolf', 4, 40, 1350, 40), 'E': ('elk', 15, 90, 2400, 60), 'g': ('gem', 7, 0, 120, 50),
        '$': ('gold', 0, 20, 120, 50), 'G': ('golem', 36, 160, 5000, 80), 'M': ('monolith', 200, 300, 20000, 150)}
lines = open(sys.argv[1], encoding='utf-8').read().splitlines()
name, W, H, sym = lines[0].split()[1:5]
W, H = int(W), int(H)
g = [list(l) for l in lines[1:1 + H]]
cell = lambda x, y: g[y][x]
inside = lambda x, y: 0 <= x < W and 0 <= y < H
D8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]


def bfs(team, shut):
    own, other = ('S', 's') if team == 'A' else ('s', 'S')
    dist = {}
    q = collections.deque()
    for y in range(H):
        for x in range(W):
            if g[y][x] == own: dist[(x, y)] = 0; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in D8:
            nx, ny = x + dx, y + dy
            if not inside(nx, ny) or (nx, ny) in dist: continue
            c = g[ny][nx]
            if c in '#oA' or c == other or (shut and c in CAMP): continue
            dist[(nx, ny)] = dist[(x, y)] + 1; q.append((nx, ny))
    return dist


dA, dB = bfs('A', False), bfs('B', False)
sA, sB = bfs('A', True), bfs('B', True)
# camp groups
seen, groups = {}, []
for y in range(H):
    for x in range(W):
        if g[y][x] in CAMP and (x, y) not in seen:
            comp, st = [], [(x, y)]
            seen[(x, y)] = len(groups)
            while st:
                cx, cy = st.pop(); comp.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if inside(nx, ny) and g[ny][nx] in CAMP and (nx, ny) not in seen:
                        seen[(nx, ny)] = len(groups); st.append((nx, ny))
            groups.append(comp)


def near(comp, dist):
    best = None
    for (x, y) in comp:
        for dx, dy in D8:
            t = (x + dx, y + dy)
            if t in dist and (best is None or dist[t] < best): best = dist[t]
    return best if best is not None else -1


tA = min((dB[(x, y)] for y in range(H) for x in range(W) if g[y][x] == 'S' and (x, y) in dB), default=-1)
spawnA = [(x, y) for y in range(H) for x in range(W) if g[y][x] == 'S']
spawnB = [(x, y) for y in range(H) for x in range(W) if g[y][x] == 's']
adjA = min((dB.get((x + dx, y + dy), 999) for (x, y) in spawnA for dx, dy in D8), default=-1)
adjAs = min((sB.get((x + dx, y + dy), 999) for (x, y) in spawnA for dx, dy in D8), default=-1)
print(f'{name} {W}x{H} {sym}; spawn A x{min(p[0] for p in spawnA)}-{max(p[0] for p in spawnA)} y{min(p[1] for p in spawnA)}-{max(p[1] for p in spawnA)},'
      f' spawn B x{min(p[0] for p in spawnB)}-{max(p[0] for p in spawnB)} y{min(p[1] for p in spawnB)}-{max(p[1] for p in spawnB)};'
      f' spawn to spawn {adjA + 1} steps open, {adjAs + 1} shut')
alt = [(x, y) for y in range(H) for x in range(W) if g[y][x] == 'A']


def adjd(p, dist):
    return min((dist[(p[0] + dx, p[1] + dy)] for dx, dy in D8 if (p[0] + dx, p[1] + dy) in dist), default=-1)


print('altars (x,y: steps from A open/shut, from B open/shut):',
      '; '.join(f'({x},{y}) A{adjd((x, y), dA)}/{adjd((x, y), sA)} B{adjd((x, y), dB)}/{adjd((x, y), sB)}' for x, y in alt))
print('grp kinds                       gems gold    hp  rsp  tiles(x,y)        A-open/shut B-open/shut zone')
tot = collections.Counter()
for i, comp in enumerate(groups):
    k = collections.Counter(CAMP[g[y][x]][0] for x, y in comp)
    gems = sum(CAMP[g[y][x]][1] for x, y in comp); gold = sum(CAMP[g[y][x]][2] for x, y in comp)
    hp = sum(CAMP[g[y][x]][3] for x, y in comp); rsp = max(CAMP[g[y][x]][4] for x, y in comp)
    a, b = near(comp, dA), near(comp, dB)
    zone = 'A' if a + 6 <= b else 'B' if b + 6 <= a else 'mid'
    xs = [p[0] for p in comp]; ys = [p[1] for p in comp]
    kinds = ' '.join(f'{v}{n}' for n, v in sorted(k.items()))
    tot[zone, 'gems'] += gems; tot[zone, 'n'] += 1
    print(f'{i:3} {kinds:30} {gems:4} {gold:4} {hp:5} {rsp:4}  x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)}'.ljust(70)
          + f' {a:3}/{near(comp, sA):3}   {b:3}/{near(comp, sB):3}  {zone}')
print('gems per full clear by zone:', ', '.join(f'{z} {tot[z, "gems"]} in {tot[z, "n"]} groups' for z in ('A', 'mid', 'B')))
if '--map' in sys.argv:
    ids = '0123456789abcdefghijklmnopqrstuvwxyz'
    for y in range(H):
        print(''.join(ids[seen[(x, y)] % 36] if (x, y) in seen else g[y][x] for x in range(W)))
