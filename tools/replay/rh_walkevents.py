# Walk-in events: a champion hitting no enemy champion in rounds k-1 and k, over 3 tiles from an enemy ranged champion
# (alive, off its spawn) at round k start and within its basic range at round k+1 start, having moved itself. Split by
# whether the victim's step was toward that shooter; share shot by that shooter in round k or k+1.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, RANGE
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    fought = [set(i for i in range(n) if enemy_hits(r, i, n)) for r in rows]
    for k in range(1, len(rows) - 2):
        a, b = rows[k], rows[k + 1]
        if a['r'] > 1000: break
        for j in range(n):
            pj, qj = pos(a['c'][j]), pos(b['c'][j])
            if pj is None or qj is None or pj == qj or j in fought[k] or j in fought[k - 1]: continue
            w = who(a['c'][j]['t'], us)
            for i in range(n):
                pi, qi = pos(a['c'][i]), pos(b['c'][i])
                if pi is None or qi is None or a['c'][i]['t'] == a['c'][j]['t'] or RANGE.get(a['c'][i]['ty'], 1) < 3 or pi in spawn[a['c'][i]['t']]: continue
                if dist(pj, pi) <= 3 or dist(qj, qi) > 3: continue
                toward = dist(qj, pi) < dist(pj, pi)
                saw = i in a['vis'][j]
                shot = any(y[0] == 'attack' and y[-2] == 'c' and y[-1] == j for t in (k, k + 1) for y in rows[t]['act'][i])
                for key in ('all', 'toward the shooter' if toward else 'not toward it', 'saw it' if saw else 'did not see it'):
                    E[(w, key)] += 1; E[(w, key, 's')] += shot
print(ng, 'games, to r1000: walk-in events per game (share shot by that shooter that round or the next)')
for key in ('all', 'toward the shooter', 'not toward it', 'saw it', 'did not see it'):
    print(f'  {key:20} ' + '   '.join(f"{w} {E[(w, key)] / ng:5.1f} ({E[(w, key, 's')] / max(1, E[(w, key)]):.2f})" for w in ('us', 'them')))
