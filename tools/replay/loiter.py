# Loitering to r1000, us vs them: windows of W rounds (default 40, sliding by W) in which a champion stays alive, makes
# no attack, cast or tribute, and never leaves a box of radius 3 around where it started, off its start tiles. Per game:
# windows, split by whether a dead camp group's tile lies within 2 (respawn waits) and by bag (20+ or less); then the
# maps with the most and examples (map, round, type, tile, bag, enemies within 8 at the start).
# usage: python -I tools/replay/loiter.py DIR... [--w W]
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
args = sys.argv[1:]; W = 40
if '--w' in args: i = args.index('--w'); W = int(args[i + 1]); args = args[:i] + args[i + 2:]
C = collections.Counter(); M = collections.Counter(); ng = 0; ex = []
for us, res, mp, meta, rows in D.games(args):
    ng += 1; n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    tile_g = {t: g for g, ts in gtiles.items() for t in ts}
    start = {i: (rows[0]['c'][i].get('x'), rows[0]['c'][i].get('y')) for i in range(n)}
    R = min(len(rows), 1000)
    for i in range(n):
        for k0 in range(1, R - W, W):
            c0 = rows[k0]['c'][i]
            if not c0['a'] or 'x' not in c0: continue
            p0 = (c0['x'], c0['y'])
            if D.dist(p0, start[i]) <= 3: continue
            ok = True
            for k in range(k0, k0 + W):
                c = rows[k]['c'][i]
                if not c['a'] or 'x' not in c or D.dist((c['x'], c['y']), p0) > 3: ok = False; break
                if any(x[0] in ('attack', 'cast', 'tribute') for x in (rows[k]['act'][i] if i < len(rows[k]['act']) else [])): ok = False; break
            if not ok: continue
            s = D.who(c0['t'], us)
            r0 = rows[k0]
            dead = any(D.dist(p0, t) <= 2 and all(r0['mh'][j] == 0 for j in members[g]) for t, g in tile_g.items())
            bag = c0.get('g', 0)
            key = (s, 'respawn' if dead else 'other', 'bag20' if bag >= 20 else 'bag<20')
            C[key] += 1; M[(s, mp)] += 1
            if s == 'us' and not dead:
                en = sum(1 for o in r0['c'] if o['a'] and 'x' in o and D.who(o['t'], us) != s and D.dist(p0, (o['x'], o['y'])) <= 8)
                ex.append((mp, r0['r'], D.NAMES[c0['ty']], p0, bag, en))
print(f'{ng} games to r1000: {W}-round loiter windows per game')
for kind in ('respawn', 'other'):
    for bag in ('bag20', 'bag<20'):
        print(f"  {kind:8} {bag:6} us {C[('us', kind, bag)] / ng:5.2f}  them {C[('them', kind, bag)] / ng:5.2f}")
print('maps (us / them windows):', ', '.join(f"{mp} {M[('us', mp)]}/{M[('them', mp)]}" for mp in sorted({m for _, m in M}, key=lambda m: -M[('us', m)])[:12]))
print('our non-respawn examples:'); [print('  ', e) for e in ex[:25]]
