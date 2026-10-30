# usage: python -I tools/replay/handoff2.py DIR...
# Per capture to r1000, by the capturing side: rounds from the group's last camp death to the capture (claim), whether the
# capturer hit the group during its clear, and the capturer's distance to the group's tiles when the last camp died.
import sys, collections, statistics as st
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 1000
V = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    hitters = collections.defaultdict(set); pending = {}
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i in range(n):
            for x in D.camp_hits(a, i):
                if x[-1] in grp: hitters[grp[x[-1]]].add(i)
        for g, js in members.items():
            if g not in pending and any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js):
                pos = {i: (c['x'], c['y']) for i, c in enumerate(b['c']) if c['a'] and 'x' in c}
                pending[g] = (b['r'], hitters.pop(g, set()), pos)
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            dead, hs, pos = pending.pop(g)
            w = D.who(c['t'], us)
            d0 = min(max(abs(pos[i][0] - t[0]), abs(pos[i][1] - t[1])) for t in gtiles[g]) if i in pos else 99
            V[w].append((b['r'] - dead, i in hs, d0, c['g'] - pc['g'] + (c.get('au', 0) - pc.get('au', 0)) / 4))
for w in ('us', 'them'):
    L = V[w]
    if not L: continue
    far = [x for x in L if x[2] >= 3]
    print(f"{w:4} captures {len(L)}: claim mean {st.mean(x[0] for x in L):.1f}, over 10 rounds {sum(x[0] > 10 for x in L) / len(L):.2f}; "
          f"capturer hit the group {sum(x[1] for x in L) / len(L):.2f}; capturer 3+ tiles off at the last kill {len(far) / len(L):.2f} "
          f"(claim {st.mean(x[0] for x in far) if far else 0:.1f}, value {st.mean(x[3] for x in far) if far else 0:.1f} against {st.mean(x[3] for x in L):.1f})")
