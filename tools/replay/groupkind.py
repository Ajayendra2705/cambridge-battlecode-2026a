"""Captures per game by group composition and region, us vs them, to round R.
usage: python -I tools/replay/groupkind.py R DIR... """
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
R = int(sys.argv[1])
N = collections.Counter(); G = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    camps = {int(k): v for k, v in meta.get('camps', {}).items()}
    grp, members, gtiles = D.camp_groups(rows, n)
    kind = {}
    for g, js in members.items():
        c = collections.Counter(D.CAMPS.get(camps.get(j), '?') for j in js)
        big = [t for t in ('monolith', 'golem', 'elk', 'wolf') if c[t]]
        kind[g] = big[0] if big else 'clusters'
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    pending = set()
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for g, js in members.items():
            if g not in pending and any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js): pending.add(g)
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            pending.discard(g)
            w = D.who(c['t'], us)
            # Region from the capturing side's view.
            do = min(D.dist(p, q) for q in start[c['t']]); de = min(D.dist(p, q) for q in start[1 - c['t']])
            region = 'own' if do < de - 3 else 'enemy' if de < do - 3 else 'middle'
            N[(w, kind[g], region)] += 1; G[(w, kind[g], region)] += c['g'] - pc['g']
print(f'{ng} games to r{R}: captures per game (gems per game) by the group\'s biggest camp type and region (capturer\'s view)')
for k in ('monolith', 'golem', 'elk', 'wolf', 'clusters'):
    for region in ('own', 'middle', 'enemy'):
        u, t = N[('us', k, region)] / ng, N[('them', k, region)] / ng
        if u + t < 0.05: continue
        print(f'  {k:9} {region:6}  us {u:5.2f} ({G[("us", k, region)] / ng:5.1f})   them {t:5.2f} ({G[("them", k, region)] / ng:5.1f})   gap gems {(G[("us", k, region)] - G[("them", k, region)]) / ng:+6.1f}')
