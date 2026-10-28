"""Where the gem gap comes from, us vs them, per game to round R (h3, 10-28).

usage: python -I tools/helper3/h3_gemgap.py [--upto R] DIR [DIR ...]    (default R 1000; decoded runs, pooled)

Gems collected (a champion's bag rises while alive) are split by source: a capture (the bag rises without a kill),
by the captured group's strongest camp type (monolith > golem > elk > wolf > clusters only; groups and types from
`decoded.camp_groups` and the meta line), or a kill (the bag rises in a round where the champion's kill count rises),
and by round band (1-300, 301-600, 601-R). Every champion-round (alive or dead) gets one activity, first match:
  fight    hits an enemy champion            farm     hits a camp
  bank     inside a tribute channel (from its start while the bag lasts, standing still)
  capture  standing on a dead group's tile   home     within 3 of its own start tiles
  walk     moved (split by a bag of 20+ and by health under 50%)
  wait     stood still with no action, away from home (respawn waits, waiting for teammates, standing in a bush)
  dead
Then capture gems = alive rounds x share of alive rounds farming or capturing x capture gems per such round, and the
log of our over their capture gems is split over those three factors (a negative share is a factor in our favour).
"""
import collections, math, os, sys

sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]
R = 1000
if '--upto' in args:
    i = args.index('--upto'); R = int(args[i + 1]); del args[i:i + 2]
RANK = {'monolith': 5, 'golem': 4, 'elk': 3, 'wolf': 2, 'gem': 1, 'gold': 1}
BANDS = ((1, 300), (301, 600), (601, R))
G = collections.Counter(); T = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    camps = {int(k): v for k, v in meta.get('camps', {}).items()}
    grp, members, gtiles = D.camp_groups(rows, n)
    tile_grp = {t: g for g, ts in gtiles.items() for t in ts}
    kind = {}
    for g, js in members.items():
        ts = [D.CAMPS.get(camps.get(j), 'gem') for j in js]
        best = max(ts, key=lambda t: RANK.get(t, 0))
        kind[g] = 'clusters' if RANK.get(best, 0) == 1 else best
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    chan_until = {}
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if b['r'] > R: break
        band = next(f'r{lo}-{hi}' for lo, hi in BANDS if lo <= b['r'] <= hi)
        for i in range(n):
            c, nb = a['c'][i], b['c'][i]
            w = 'us' if c['t'] == us else 'them'
            # gems gained this round
            if c['a'] and nb['a'] and nb.get('g', 0) > c.get('g', 0):
                gain = nb['g'] - c.get('g', 0)
                if nb.get('k', 0) > c.get('k', 0): src = 'kill'
                else:
                    p = (nb.get('x'), nb.get('y'))
                    gi = tile_grp.get(p)
                    if gi is None:
                        near = [tile_grp[(p[0] + dx, p[1] + dy)] for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (p[0] + dx, p[1] + dy) in tile_grp] if p[0] is not None else []
                        gi = near[0] if near else None
                    src = kind.get(gi, 'clusters') if gi is not None else 'unknown'
                G[w, 'src', src] += gain; G[w, 'band', band, 'kill' if src == 'kill' else 'capture'] += gain
                G[w, 'collected'] += gain
            # activity
            T[w, 'all'] += 1
            if not c['a'] or 'x' not in c: T[w, 'dead'] += 1; continue
            T[w, 'alive'] += 1
            acts = a['act'][i] if i < len(a['act']) else []
            p = (c['x'], c['y'])
            moved = nb['a'] and 'x' in nb and (nb['x'], nb['y']) != p
            if any(x[0] == 'tribute' for x in acts): chan_until[i] = a['r'] + c.get('g', 0) // 10 + 2
            if D.enemy_hits(a, i, n): act = 'fight'
            elif D.camp_hits(a, i): act = 'farm'
            elif chan_until.get(i, -1) >= a['r'] and c.get('g', 0) > 0 and not moved: act = 'bank'
            elif not moved and p in tile_grp and all(a['mh'][j] == 0 for j in members[tile_grp[p]]): act = 'capture'
            elif min(D.dist(p, q) for q in start[c['t']]) <= 3: act = 'home'
            elif moved:
                act = 'walk' + (' bag20+' if c.get('g', 0) >= 20 else '') + (' hurt' if c['hp'] < 0.5 * c['mhp'] else '')
            elif acts: act = 'other action'
            else: act = 'wait'
            T[w, act] += 1
            T[w, 'act ' + band, act if act in ('farm', 'capture') else 'x'] += 1
print(f'{ng} games to r{R}: ' + ', '.join(args))
print('gems collected per game by source (us / them, gap)')
srcs = ['monolith', 'golem', 'elk', 'wolf', 'clusters', 'unknown', 'kill']
for s in srcs:
    u, t = G['us', 'src', s] / ng, G['them', 'src', s] / ng
    if u or t: print(f'  {s:9} {u:6.1f} / {t:6.1f}  ({u - t:+6.1f})')
u, t = G['us', 'collected'] / ng, G['them', 'collected'] / ng
print(f'  {"total":9} {u:6.1f} / {t:6.1f}  ({u - t:+6.1f})')
print('by round band: captures | kills (us / them, gap)')
for lo, hi in BANDS:
    bd = f'r{lo}-{hi}'
    cu, ct = G['us', 'band', bd, 'capture'] / ng, G['them', 'band', bd, 'capture'] / ng
    ku, kt = G['us', 'band', bd, 'kill'] / ng, G['them', 'band', bd, 'kill'] / ng
    print(f'  {bd:10} captures {cu:6.1f} / {ct:6.1f} ({cu - ct:+6.1f})   kills {ku:5.1f} / {kt:5.1f} ({ku - kt:+6.1f})')
print('champion-rounds per game by activity (us / them, gap); share of alive rounds in brackets')
acts = sorted({k[1] for k in T if len(k) == 2 and k[1] not in ('all', 'alive')}, key=lambda a: -(T['us', a] + T['them', a]))
for a in ['alive'] + acts:
    u, t = T['us', a] / ng, T['them', a] / ng
    su = '' if a in ('alive', 'dead') else f'  [{T["us", a] / max(1, T["us", "alive"]):.3f} / {T["them", a] / max(1, T["them", "alive"]):.3f}]'
    print(f'  {a:18} {u:7.1f} / {t:7.1f}  ({u - t:+7.1f}){su}')
# decomposition of capture gems
cap = {w: sum(G[w, 'src', s] for s in srcs if s != 'kill') / ng for w in ('us', 'them')}
alive = {w: T[w, 'alive'] / ng for w in ('us', 'them')}
fr = {w: (T[w, 'farm'] + T[w, 'capture']) / max(1, T[w, 'alive']) for w in ('us', 'them')}
eff = {w: cap[w] / max(1e-9, alive[w] * fr[w]) for w in ('us', 'them')}
tot = math.log(cap['us'] / cap['them']) if cap['us'] and cap['them'] else 0
print(f'capture gems {cap["us"]:.0f} / {cap["them"]:.0f} = alive rounds {alive["us"]:.0f} / {alive["them"]:.0f}'
      f' x farm+capture share {fr["us"]:.3f} / {fr["them"]:.3f} x gems per farm+capture round {eff["us"]:.3f} / {eff["them"]:.3f}')
if tot:
    parts = {'alive rounds': math.log(alive['us'] / alive['them']), 'farm share': math.log(fr['us'] / fr['them']),
             'gems per farm round': math.log(eff['us'] / eff['them'])}
    print('share of the log gap: ' + ', '.join(f'{k} {v / tot:.0%}' for k, v in parts.items()))
for lo, hi in BANDS:
    bd = f'r{lo}-{hi}'
    fu = T['us', 'act ' + bd, 'farm'] + T['us', 'act ' + bd, 'capture']; ft = T['them', 'act ' + bd, 'farm'] + T['them', 'act ' + bd, 'capture']
    print(f'  {bd:10} farm+capture rounds per game {fu / ng:6.1f} / {ft / ng:6.1f}; capture gems per such round'
          f' {G["us", "band", bd, "capture"] / max(1, fu):.3f} / {G["them", "band", bd, "capture"] / max(1, ft):.3f}')
