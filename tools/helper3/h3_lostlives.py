"""Strong-camp lives one side hit but the other side captured, to round 1000 (h3, 10-28).

usage: python -I tools/helper3/h3_lostlives.py DIR [DIR ...]   (decoded runs, pooled)

A life is a group's run of camp hits up to a capture (as tools/helper3/h3_lives.py), for groups whose strongest camp
is an elk, golem or monolith. For lives captured by side X that side Y also hit ("lost" by Y): the group's health
left at Y's last hit (share of the life's starting health, from `mh`), rounds from that hit to the capture, Y's
champions within 6 of the group at the round X first hits it after Y's last hit (0 = Y had left; 1+ = contested),
and whether a Y champion within 6 then died before the capture. Per side Y: lost lives per game and those shares.
"""
import bisect, collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
RANK = {'monolith': 5, 'golem': 4, 'elk': 3, 'wolf': 2, 'gem': 1, 'gold': 1}
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    camps = {int(k): v for k, v in meta.get('camps', {}).items()}
    grp, members, gtiles = D.camp_groups(rows, n)
    tile_grp = {t: g for g, ts in gtiles.items() for t in ts}
    kind = {g: max((D.CAMPS.get(camps.get(j), 'gem') for j in js), key=lambda t: RANK.get(t, 0)) for g, js in members.items()}
    strong = {g for g, k in kind.items() if k in ('elk', 'golem', 'monolith')}
    caps = collections.defaultdict(dict); hits = collections.defaultdict(list)  # group -> {round: side}; group -> [(round, side, k)]
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if b['r'] > 1000: break
        for i in range(n):
            c, nb = a['c'][i], b['c'][i]
            for x in D.camp_hits(a, i):
                g = grp.get(x[-1])
                if g in strong: hits[g].append((a['r'], c['t'], k))
            if not (c['a'] and nb['a']) or nb.get('k', 0) > c.get('k', 0) or 'x' not in nb: continue
            if nb.get('g', 0) - c.get('g', 0) < 0 or (nb.get('g', 0) == c.get('g', 0) and nb.get('au', 0) <= c.get('au', 0)): continue
            p = (nb['x'], nb['y'])
            g = next((tile_grp[(p[0] + dx, p[1] + dy)] for dx in (0, -1, 1) for dy in (0, -1, 1) if (p[0] + dx, p[1] + dy) in tile_grp), None)
            if g in strong: caps[g].setdefault(b['r'], c['t'])
    for g, cv in caps.items():
        ends = sorted(cv); prev = -1
        for e in ends:
            life = [h for h in hits[g] if prev < h[0] <= e]
            prev = e
            X = cv[e]
            for Y in (0, 1):
                if Y == X: continue
                yh = [h for h in life if h[1] == Y]
                if not yh: continue
                w = 'us' if Y == us else 'them'
                last = max(yh)
                k0 = min(h[2] for h in life)
                start_hp = sum(rows[k0]['mh'][j] for j in members[g] if j < len(rows[k0]['mh'])) or 1
                left = sum(rows[last[2]]['mh'][j] for j in members[g] if j < len(rows[last[2]]['mh'])) / start_hp
                xh = [h for h in life if h[1] == X and h[0] > last[0]]
                C[w, 'n'] += 1; C[w, 'gap'] += e - last[0]
                C[w, 'left<30' if left < 0.3 else 'left30-60' if left < 0.6 else 'left60+'] += 1
                if xh:
                    kx = min(xh)[2]; row = rows[kx]
                    tiles = gtiles[g]
                    near = [i for i in range(n) if row['c'][i]['t'] == Y and row['c'][i]['a'] and 'x' in row['c'][i]
                            and min(D.dist((row['c'][i]['x'], row['c'][i]['y']), t) for t in tiles) <= 6]
                    C[w, 'present' if near else 'left'] += 1
                    died = any(not rows[kk]['c'][i]['a'] for i in near for kk in range(kx, min(len(rows), kx + (e - min(xh)[0]) + 1)))
                    if near and died: C[w, 'present died'] += 1
                else: C[w, 'X finished earlier'] += 1
print(f'{ng} games: strong-camp lives (elk, golem, monolith) hit by a side but captured by the other, to r1000')
for w in ('us', 'them'):
    N = max(1, C[w, 'n'])
    print(f'  {w:4} lost {C[w, "n"] / ng:.2f}/game | health left at its last hit <30% {C[w, "left<30"] / N:.0%}, 30-60% {C[w, "left30-60"] / N:.0%},'
          f' 60%+ {C[w, "left60+"] / N:.0%} | rounds to the capture {C[w, "gap"] / N:.0f} | when the taker resumed: it had left'
          f' {C[w, "left"] / N:.0%}, still within 6 {C[w, "present"] / N:.0%} (one of them died before the capture {C[w, "present died"] / N:.0%})')
