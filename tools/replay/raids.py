"""Raids on home-half groups, to r1000: python -I tools/replay/raids.py DIR...
DIRs are decoded runs (data/fights/RUN_PANEL). For each side's home-half groups (region as decoded.py lives), how many group
lives a game the owner hits first and how many the other side hits first, the median rounds the group was up before that
hit, and the owner's nearest champion to the group when it came up and at the hit (median, share within 8)."""
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, camp_groups, camp_hits, dist, who
R = 1000
S = collections.defaultdict(list); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    grp, members, gtiles = camp_groups(rows, n)
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    owner = {}
    for g, ts in gtiles.items():
        do = min(dist(p, q) for p in ts for q in start[us]); de = min(dist(p, q) for p in ts for q in start[1 - us])
        owner[g] = us if do < de - 3 else (1 - us) if de < do - 3 else None
    def near(row, team, g):
        ds = [min(dist((c['x'], c['y']), q) for q in gtiles[g]) for c in row['c'] if c['t'] == team and c['a'] and 'x' in c]
        return min(ds) if ds else 99
    up = {g: rows[0] for g in members}; hit = {g: None for g in members}
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i in range(n):
            for x in camp_hits(a, i):
                g = grp.get(x[-1])
                if g is None or hit[g] is not None or owner.get(g) is None: continue
                hit[g] = a['c'][i]['t']
                o = owner[g]; side = who(o, us)
                kind = 'raid' if hit[g] != o else 'home'
                S[(side, kind, 'wait')].append(a['r'] - up[g]['r'])
                S[(side, kind, 'own_near_up')].append(near(up[g], o, g))
                S[(side, kind, 'own_near_hit')].append(near(a, o, g))
        for g, js in members.items():
            if all(b['mh'][j] > 0 for j in js) and any(a['mh'][j] == 0 for j in js):
                up[g] = b; hit[g] = None
med = lambda v: sorted(v)[len(v) // 2] if v else -1
for side in ('us', 'them'):
    for kind in ('home', 'raid'):
        w = S[(side, kind, 'wait')]
        nu = S[(side, kind, 'own_near_up')]; nh = S[(side, kind, 'own_near_hit')]
        frac = lambda v, k: sum(1 for x in v if x <= k) / max(1, len(v))
        print(f"{side:4} groups on {side}'s half, first hit by {'owner' if kind == 'home' else 'other side'}: {len(w)/ng:5.1f}/game  "
              f"rounds up before the hit median {med(w)}  owner's nearest champion when it came up median {med(nu)} (<=8: {frac(nu, 8):.2f})  "
              f"at the hit median {med(nh)} (<=8: {frac(nh, 8):.2f})")
