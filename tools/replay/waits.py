"""Idle waits next to dead camp groups, to r1000: python -I tools/replay/waits.py DIR...
DIRs are decoded runs (data/fights/RUN_PANEL). Counts champion-rounds per game in which a living champion off its own
spawn takes no action within 3 tiles of a group whose camps are all dead (not on its tiles): by the group's region from
that champion's side (own / middle / enemy, as decoded.py lives), and what it does next within 15 rounds (hits that group,
moves first, nothing)."""
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, dist, who, enemy_hits, camp_hits, camp_groups
A = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    grp, members, gtiles = camp_groups(rows, n)
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    region = {}
    for g, ts in gtiles.items():
        do = min(dist(p, q) for p in ts for q in start[us]); de = min(dist(p, q) for p in ts for q in start[1 - us])
        region[g] = 'own' if do < de - 3 else 'enemy' if de < do - 3 else 'middle'
    rows = [r for r in rows if r['r'] <= 1015]
    for t, r in enumerate(rows):
        if r['r'] > 1000: break
        for i in range(n):
            c = r['c'][i]
            if not c['a'] or 'x' not in c: continue
            p = (c['x'], c['y'])
            acts = r['act'][i] if i < len(r['act']) else []
            if acts: continue
            if min(dist(p, q) for q in start[c['t']]) <= 1: continue
            dead = lambda g2: all(r['mh'][j] == 0 for j in members[g2] if j < len(r['mh']))
            near = [g2 for g2, ts in gtiles.items() if min(dist(p, q) for q in ts) <= 3]
            if not near or not all(dead(g2) for g2 in near) or p in {q for g2 in near for q in gtiles[g2]}: continue
            g = min(near, key=lambda g2: min(dist(p, q) for q in gtiles[g2]))
            # owner's view: region relative to the champion's side
            rg = region[g] if c['t'] == us else {'own': 'enemy', 'enemy': 'own', 'middle': 'middle'}[region[g]]
            nxt = 'nothing'
            for r2 in rows[t + 1:t + 16]:
                a2 = r2['act'][i] if i < len(r2['act']) else []
                if any(grp.get(x[-1]) == g for x in camp_hits(r2, i)): nxt = 'hits that group'; break
                if a2 and any(x[0] == 'move' for x in a2): nxt = 'moves first'; break
            w = who(c['t'], us)
            A[(w, rg)] += 1; A[(w, nxt)] += 1
for w in ('us', 'them'):
    print(w, ' '.join(f"{k} {A[(w, k)] / ng:5.0f}" for k in ('own', 'middle', 'enemy', 'hits that group', 'moves first', 'nothing')))
