"""Each champion's first camp group: python -I firstgroups.py DIR...  For each side: the first group hit by each champion, its kind, its distance from the champion's start, its rank among all groups by that distance, its round; and how many champions share each team's first groups."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
# Camp tiles per map, from all games.
games = list(D.games(sys.argv[1:]))
POS = collections.defaultdict(dict)
KIND = {}
for us, res, mp, meta, rows in games:
    n = len(rows[0]['c'])
    KIND[mp] = {int(k): v for k, v in meta['camps'].items()}
    for r in rows:
        for i in range(min(n, len(r.get('act', [])))):
            for x in D.camp_hits(r, i):
                POS[mp][x[-1]] = (x[-4], x[-3])
GR = {}
for mp, pos in POS.items():
    tiles = {p: j for j, p in pos.items()}
    grp = {}
    for j in pos:
        if j in grp:
            continue
        g = len(set(grp.values()))
        st = [j]
        while st:
            k = st.pop()
            if k in grp:
                continue
            grp[k] = g
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                m = tiles.get((pos[k][0] + dx, pos[k][1] + dy))
                if m is not None and m not in grp:
                    st.append(m)
    mem = collections.defaultdict(list)
    for j, g in grp.items():
        mem[g].append(j)
    GR[mp] = (grp, mem)
A = collections.defaultdict(collections.Counter)
NAME = {0: 'wolf', 1: 'elk', 2: 'gemc', 3: 'goldc', 4: 'mono', 5: 'golem'}
def gkind(mp, g):
    grp, mem = GR[mp]
    ks = [KIND[mp].get(j) for j in mem[g]]
    for k in (4, 5, 1, 0):
        if k in ks:
            return NAME[k]
    return 'gemc' if 2 in ks else 'goldc'
for us, res, mp, meta, rows in games:
    n = len(rows[0]['c'])
    grp, mem = GR[mp]
    pos = POS[mp]
    start = {i: (c['x'], c['y']) for i, c in enumerate(rows[0]['c']) if 'x' in c}
    first = {}
    for r in rows:
        if r['r'] > 200:
            break
        for i in range(min(n, len(r.get('act', [])))):
            if i in first:
                continue
            for x in D.camp_hits(r, i):
                if x[-1] in grp:
                    first[i] = (r['r'], grp[x[-1]])
                    break
    sides = collections.defaultdict(list)
    for i, (R, g) in first.items():
        c = rows[0]['c'][i]
        w = D.who(c['t'], us)
        sides[w].append(g)
        if i not in start:
            continue
        s = start[i]
        ds = {h: min(D.dist(s, pos[j]) for j in mem[h]) for h in mem}
        order = sorted(ds, key=lambda h: ds[h])
        a = A[w]
        a['n'] += 1
        a['round'] += R
        a['dist'] += ds[g]
        rank = order.index(g)
        a['rank0'] += rank == 0
        a['rank1'] += rank == 1
        a['rank2+'] += rank >= 2
        a['k_' + gkind(mp, g)] += 1
    for w, gs in sides.items():
        a = A[w]
        a['teams'] += 1
        a['groups'] += len(set(gs))
        a['largest'] += max(collections.Counter(gs).values())
for w in ('us', 'them'):
    a = A[w]; m = max(1, a['n'])
    print(f"{w:4} champions {a['n']}: first hit r{a['round'] / m:.1f}, {a['dist'] / m:.1f} tiles from start; nearest group {a['rank0'] / m:.2f}, second {a['rank1'] / m:.2f}, further {a['rank2+'] / m:.2f}; kinds " + ' '.join(f"{k} {a['k_' + k] / m:.2f}" for k in ('wolf', 'elk', 'gemc', 'goldc', 'golem', 'mono')) + f"; distinct first groups per team {a['groups'] / max(1, a['teams']):.2f}, largest crowd {a['largest'] / max(1, a['teams']):.2f}")
