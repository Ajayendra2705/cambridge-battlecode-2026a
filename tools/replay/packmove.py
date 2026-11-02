"""What a champion does in the 5 rounds after it sights an enemy pack, and how that ends, us vs the rivals.

usage: python -I tools/replay/packmove.py DIR [DIR ...] [--round R] [--foes K]

A sighting is as in packs.py: K or more enemy champions (default 3) within 8 and off their spawn, at most one ally
within 6, after 5 rounds without (2+ enemies resets the quiet count). Over the next 5 rounds the champion's change
of distance to its own spawn (home) and to the nearest of those enemies puts it in one class:
  home     moved 3+ tiles closer to home
  away     moved 2+ tiles away from the nearest sighted enemy (not home)
  toward   moved 2+ tiles closer to the nearest sighted enemy
  hold     anything else (stayed within about a tile)
Per class: sightings per game, share, died within 15 rounds, its hits on champions over those 5 rounds, and allies
within 6 at the sighting. Also split by round (to 300 / after) and by our numbers within 8 of the sighter. Sightings
until round R (default 1000). DIR is a decoded folder (tools/replay/decode_run.sh).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

args = sys.argv[1:]
R, K = 1000, 3
if '--round' in args:
    k = args.index('--round'); R = int(args[k + 1]); del args[k:k + 2]
if '--foes' in args:
    k = args.index('--foes'); K = int(args[k + 1]); del args[k:k + 2]
CLASSES = ('home', 'away', 'toward', 'hold')
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    spawn = {t: [(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c] for t in (0, 1)}
    spawn_set = {t: set(v) for t, v in spawn.items()}
    quiet = collections.Counter()

    def home_d(t, p):
        return min(D.dist(p, s) for s in spawn[t]) if spawn[t] else 0

    for k in range(1, len(rows)):
        a = rows[k - 1]
        if a['r'] > R or k + 16 >= len(rows): break
        for i in range(n):
            q = a['c'][i]
            if not (q['a'] and 'x' in q): quiet[i] = 0; continue
            t = q['t']; pos = (q['x'], q['y'])
            foes = [j for j, o in enumerate(a['c']) if o['a'] and 'x' in o and o['t'] != t and (o['x'], o['y']) not in spawn_set[1 - t]
                    and D.dist(pos, (o['x'], o['y'])) <= 8]
            allies6 = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == t and D.dist(pos, (o['x'], o['y'])) <= 6)
            if len(foes) < 2: quiet[i] += 1; continue
            if len(foes) < K or allies6 > 1: quiet[i] = 0; continue
            fresh = quiet[i] >= 5
            quiet[i] = 0
            if not fresh: continue
            w = D.who(t, us)
            allies8 = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == t and D.dist(pos, (o['x'], o['y'])) <= 8)
            b = rows[k + 4]['c'][i]
            died = any(not rows[kk]['c'][i]['a'] for kk in range(k, k + 15))
            if not (b['a'] and 'x' in b):
                cls = 'hold'  # died within 5 rounds: counted by where it was going is not possible
            else:
                p2 = (b['x'], b['y'])
                dh = home_d(t, pos) - home_d(t, p2)
                def near_foe(p, row):
                    return min((D.dist(p, (row['c'][j]['x'], row['c'][j]['y'])) for j in foes if row['c'][j]['a'] and 'x' in row['c'][j]), default=99)
                de = near_foe(p2, rows[k + 4]) - near_foe(pos, a)
                cls = 'home' if dh >= 3 else 'away' if de >= 2 else 'toward' if de <= -2 else 'hold'
            hitc = sum(1 for kk in range(k - 1, k + 4) if D.enemy_hits(rows[kk], i, n))
            band = 'r<=300' if a['r'] <= 300 else 'r>300'
            for key in ('all', band, f'allies8 {min(allies8, 2)}{"+" if allies8 >= 2 else ""}'):
                C[(w, key, cls)] += 1; C[(w, key, cls, 'died')] += died; C[(w, key, cls, 'hitc')] += hitc
                C[(w, key, cls, 'a6')] += allies6
                C[(w, key)] += 1; C[(w, key, 'died')] += died

print(f'{ng} games to r{R}: sightings of {K}+ enemies within 8 (at most one ally within 6, 5 quiet rounds before)')
for key in ('all', 'r<=300', 'r>300', 'allies8 0', 'allies8 1', 'allies8 2+'):
    print(f'{key}:')
    for w in ('us', 'them'):
        tot = max(1, C[(w, key)])
        parts = []
        for cls in CLASSES:
            m = C[(w, key, cls)]
            if not m: parts.append(f'{cls} -'); continue
            parts.append(f'{cls} {m / tot:.2f} died {C[(w, key, cls, "died")] / m:.2f}')
        print(f'  {w:4} {C[(w, key)] / max(1, ng):4.1f}/game died {C[(w, key, "died")] / tot:.3f} | ' + ' | '.join(parts))
