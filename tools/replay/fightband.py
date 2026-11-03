"""Fight outcomes by round band and by health edge: python -I fightband.py DIR...
A fight: the first enemy champion hit on a champion after 15 quiet rounds for that pair of teams within 8 tiles. Within the next 12 rounds count kills each way.
Bands by round, numbers within 6 of the hit champion, and max-health ratio of the two sides within 6."""
import collections, os, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
A = collections.defaultdict(collections.Counter)
ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    last = -99
    k = 0
    while k < len(rows) - 13:
        a = rows[k]
        if a['r'] > 1000:
            break
        victims = []
        for i in range(n):
            for x in D.enemy_hits(a, i, n):
                victims.append((x[-1], i))
        if not victims or k - last < 15:
            if victims:
                last = k
            k += 1
            continue
        last = k
        v, h = victims[0]
        vc = a['c'][v]
        if 'x' not in vc:
            k += 1
            continue
        p = (vc['x'], vc['y'])
        side = D.who(vc['t'], us)  # the side hit first
        near = lambda t: [c for c in a['c'] if c['t'] == t and c['a'] and 'x' in c and D.dist(p, (c['x'], c['y'])) <= 6]
        mine, foes = near(vc['t']), near(1 - vc['t'])
        kills_of = collections.Counter()
        for j in range(n):
            c = a['c'][j]
            if c['a'] and 'x' in c and D.dist(p, (c['x'], c['y'])) <= 8 and any(not rows[k + t]['c'][j]['a'] for t in range(1, 13)):
                kills_of[D.who(c['t'], us)] += 1  # who lost a champion
        R = a['r']
        band = 'r0-60' if R <= 60 else 'r60-150' if R <= 150 else 'r150-400' if R <= 400 else 'r400-1000'
        mh = sum(c.get('mhp', 0) for c in mine); fh = sum(c.get('mhp', 0) for c in foes)
        num = 'ahead' if len(mine) > len(foes) else 'even' if len(mine) == len(foes) else 'behind'
        hp = 'hp+' if mh > 1.15 * fh else 'hp=' if mh * 1.15 >= fh else 'hp-'
        for key in ((side, band), (side, num), (side, hp), (side, band, num)):
            s = A[key]
            s['n'] += 1
            s['victims_lost'] += kills_of[side]
            s['hitters_lost'] += kills_of['us' if side == 'them' else 'them']
            s['mh'] += mh; s['fh'] += fh; s['nm'] += len(mine); s['nf'] += len(foes)
print(ng, 'games. The side hit first; per fight: its losses, the hitters losses within 12 rounds; bodies and max health within 6')
for key in sorted(A, key=str):
    s = A[key]; m = max(1, s['n'])
    print(f"{str(key):40} {s['n'] / ng:5.2f}/game  hit side loses {s['victims_lost'] / m:.2f}  hitters lose {s['hitters_lost'] / m:.2f}  bodies {s['nm'] / m:.1f} v {s['nf'] / m:.1f}  mhp {s['mh'] / m:5.0f} v {s['fh'] / m:5.0f}")
