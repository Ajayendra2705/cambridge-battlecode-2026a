# After a first shot: an enemy shooter's basic hit on a champion that hit no enemy champion that round or the one before,
# and that this shooter had not hit in the 8 rounds before. Over the next 8 rounds: further hits by that shooter, the
# shooter's steps toward the victim (its round-start distance fell), the victim's steps away from the shooter, and the
# state at round k+8: dead, back on its spawn, hit the shooter, more than 5 tiles from the shooter, or still within 5.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, RANGE
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    fought = [set(i for i in range(n) if enemy_hits(r, i, n)) for r in rows]
    lasthit = {}
    for k in range(1, len(rows) - 10):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            sh = a['c'][i]
            if pos(sh) is None or RANGE.get(sh['ty'], 1) < 3: continue
            for x in a['act'][i]:
                if x[0] != 'attack' or x[-2] != 'c': continue
                j = x[-1]
                if a['c'][j]['t'] == sh['t']: continue
                first = k - lasthit.get((i, j), -99) > 8
                lasthit[(i, j)] = k
                if not first or j in fought[k] or j in fought[k - 1]: continue
                w = who(a['c'][j]['t'], us)
                more = sum(1 for t in range(k + 1, k + 9) for y in rows[t]['act'][i] if y[0] == 'attack' and y[-2] == 'c' and y[-1] == j)
                follow = flee = 0
                for t in range(k + 1, k + 9):
                    p0i, p1i, p0j, p1j = pos(rows[t]['c'][i]), pos(rows[t + 1]['c'][i]), pos(rows[t]['c'][j]), pos(rows[t + 1]['c'][j])
                    if None in (p0i, p1i, p0j, p1j): break
                    follow += dist(p1i, p0j) < dist(p0i, p0j)
                    flee += dist(p1j, p0i) > dist(p0j, p0i)
                back = any(y[-1] == i for t in range(k + 1, k + 9) for y in enemy_hits(rows[t], j, n))
                cj, ci = rows[k + 8]['c'][j], rows[k + 8]['c'][i]
                died = any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 9))
                if died: end = 'dead'
                elif back: end = 'hit back'
                elif pos(cj) in spawn[cj['t']]: end = 'home'
                elif pos(ci) is None or dist(pos(cj), pos(ci)) > 5: end = 'apart'
                else: end = 'near'
                E[(w, 'n')] += 1; E[(w, 'more')] += more; E[(w, 'follow')] += follow; E[(w, 'flee')] += flee
                E[(w, 'more2')] += more >= 2; E[(w, end)] += 1; E[(w, end, 'more')] += more
print(ng, 'games, to r1000: first shots on a non-fighting champion, per game; the next 8 rounds')
for w in ('us', 'them'):
    m = max(1, E[(w, 'n')])
    print(f"  victim {w:4} {E[(w, 'n')] / ng:5.1f}/game  more hits by that shooter {E[(w, 'more')] / m:4.2f} (2+ in {E[(w, 'more2')] / m:.2f})  "
          f"shooter steps toward {E[(w, 'follow')] / m:4.2f}  victim steps away {E[(w, 'flee')] / m:4.2f}")
    print('      end: ' + '  '.join(f"{e} {E[(w, e)] / m:.2f} ({E[(w, e, 'more')] / max(1, E[(w, e)]):.1f} hits)" for e in ('dead', 'hit back', 'home', 'apart', 'near')))
