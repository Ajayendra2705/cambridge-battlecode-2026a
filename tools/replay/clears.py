# usage: python -I tools/replay/clears.py DIR...
# Per captured group, by the capturing side: distinct own champions that hit its camps during the clear, the group's camp
# health at the first hit, clear rounds, and damage per clear round. python -I clears.py DIR...
import sys, collections, statistics as st
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 1000
V = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    first, hp0, hitters, pending = {}, {}, collections.defaultdict(lambda: collections.defaultdict(set)), {}
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i in range(n):
            for x in D.camp_hits(a, i):
                j = x[-1]
                if j not in grp: continue
                g = grp[j]
                if g not in first:
                    first[g] = a['r']; hp0[g] = sum(a['mh'][k] for k in members[g] if k < len(a['mh']))
                hitters[g][D.who(a['c'][i]['t'], us)].add(i)
        for g, js in members.items():
            if g not in pending and any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js):
                pending[g] = (b['r'], first.pop(g, b['r']), hp0.pop(g, 0), {k: len(v) for k, v in hitters.pop(g, {}).items()})
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            dead, h0, hp, hs = pending.pop(g)
            w = D.who(c['t'], us)
            V[w].append((dead - h0, hp, hs.get(w, 0), hs.get('them' if w == 'us' else 'us', 0), c['g'] - pc['g']))
for w in ('us', 'them'):
    L = V[w]
    if not L: continue
    print(f"{w:4} captures {len(L)}  hitters own {st.mean(x[2] for x in L):.2f} (1: {sum(x[2]==1 for x in L)/len(L):.2f}, 2: {sum(x[2]==2 for x in L)/len(L):.2f}, 3+: {sum(x[2]>=3 for x in L)/len(L):.2f})  other side hit {sum(x[3]>0 for x in L)/len(L):.2f}")
    for lo, hi in ((0, 200), (200, 500), (500, 1000), (1000, 99999)):
        S = [x for x in L if lo <= x[1] < hi]
        if not S: continue
        print(f"     hp {lo:5}-{hi:5}: n {len(S):4}  clear median {st.median(x[0] for x in S):5.1f} mean {st.mean(x[0] for x in S):5.1f}  hitters {st.mean(x[2] for x in S):.2f}  dmg/round {st.mean(x[1]/max(1,x[0]) for x in S):6.1f}  gems {st.mean(x[4] for x in S):5.1f}")
