"""Groups our bot can never pick because of the `covered` rule, per map (h3, 10-28).

usage: python -I tools/helper3/h3_cover.py [MAPDUMP ...]     (default: every data/maps_txt/*.txt)

Replays the rule of bots/main (go1): knowledge.h fills W.covered_by[g] with every other group that has a camp of
reach above 3 (elk 4, golem 4, monolith 5) within reach of one of g's tiles; pick_group (targets.h, "covered") skips g
while such a group is alive and either (a) is not strong (its strongest camp under 100: an elk group) and g has a camp
with strength (not clusters only), or (b) woke within the last 10 rounds. Rule (a) does not need the coverer awake, so
an elk group blocks its neighbours until it dies, and two elk groups that cover each other block each other for good.

Fixed point from a full map: a group is pickable once all its type-(a) coverers are pickable (we take them first).
The rest is never picked by us unless the enemy kills a coverer. Prints per map the blocked groups (layout ids of
tools/helper3/h3_layout.py, with the side nearer by open steps), their gems per clear, and the share of the map's gems.
"""
import collections, glob, os, sys

CAMP = {'w': (20, 3, 4), 'E': (60, 4, 15), 'g': (0, 3, 7), '$': (0, 3, 0), 'G': (120, 4, 36), 'M': (200, 5, 200)}  # strength, reach, gems
D8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]


def analyse(path):
    L = open(path, encoding='utf-8').read().splitlines()
    W, H = int(L[0].split()[2]), int(L[0].split()[3])
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
                        if 0 <= t[0] < W and 0 <= t[1] < H and g[t[1]][t[0]] in CAMP and t not in tile:
                            tile[t] = len(groups); st.append(t)
                groups.append(comp)
    strong = [max(CAMP[g[y][x]][0] for x, y in c) >= 100 for c in groups]
    cluster = [max(CAMP[g[y][x]][0] for x, y in c) <= 0 for c in groups]
    gems = [sum(CAMP[g[y][x]][2] for x, y in c) for c in groups]
    cov = [set() for _ in groups]
    for b, comp in enumerate(groups):
        for x, y in comp:
            r = CAMP[g[y][x]][1]
            if r <= 3: continue
            for gi, c2 in enumerate(groups):
                if gi != b and any(max(abs(x - u), abs(y - v)) <= r for u, v in c2): cov[gi].add(b)
    perm = [{b for b in cov[i] if not strong[b] and not cluster[i]} for i in range(len(groups))]  # rule (a)
    ok = set(i for i in range(len(groups)) if not perm[i])
    while True:
        more = {i for i in range(len(groups)) if i not in ok and perm[i] <= ok}
        if not more: break
        ok |= more

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
    near = lambda comp, d: min((d[(x + dx, y + dy)] for x, y in comp for dx, dy in D8 if (x + dx, y + dy) in d), default=999)
    blocked = [i for i in range(len(groups)) if i not in ok]
    delayed = [i for i in ok if perm[i]]
    total = sum(gems)
    out = []
    for i in blocked:
        a, b = near(groups[i], dA), near(groups[i], dB)
        xs = [p[0] for p in groups[i]]; ys = [p[1] for p in groups[i]]
        out.append(f'{i}({gems[i]}g x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)} A{a}/B{b} by {sorted(perm[i])})')
    return total, sum(gems[i] for i in blocked), out, len(delayed), sum(gems[i] for i in delayed)


paths = sys.argv[1:] or sorted(glob.glob(os.path.join('data', 'maps_txt', '*.txt')))
rows = []
for p in paths:
    total, lost, out, nd, gd = analyse(p)
    rows.append((lost / max(1, total), os.path.basename(p)[:-4], total, lost, out, nd, gd))
for share, name, total, lost, out, nd, gd in sorted(rows, reverse=True):
    if lost or len(paths) == 1:
        print(f'{name:24} blocked {lost:4} of {total:4} gems per clear ({share:4.0%}); delayed {nd} groups ({gd} gems): ' + '; '.join(out))
print(f'{sum(1 for r in rows if r[3])} of {len(rows)} maps have groups our bot never picks while both covers live')
