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
                if not toward or RANGE.get(a['c'][j]['ty'], 1) > 1 or k + 8 >= len(rows): continue
                eng = any(pos(a['c'][e]) and a['c'][e]['t'] == a['c'][j]['t'] and e != j and dist(pos(a['c'][e]), pi) <= 2 for e in range(n))
                taken = sum(1 for t in range(k, k + 7) for y in rows[t]['act'][i] if y[0] == 'attack' and y[-2] == 'c' and y[-1] == j)
                dealt = sum(1 for t in range(k, k + 7) for y in enemy_hits(rows[t], j, n) if y[-1] == i)
                sdead = any(not rows[t]['c'][i].get('a') for t in range(k + 1, k + 8))
                jdead = any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 8))
                anyd = sum(len(enemy_hits(rows[t], j, n)) for t in range(k, k + 7))
                en = [e for e in range(n) if a['c'][e]['t'] != a['c'][j]['t'] and pos(a['c'][e])]
                near = min(en, key=lambda e: dist(pj, pos(a['c'][e]))) == i
                E[(w, 'any')] += anyd
                if eng: continue
                for key in ('not engaged, nearest=shooter' if near else 'not engaged, nearest=other',):
                    E[(w, key, 'any')] += anyd
                    E[(w, key)] += 1; E[(w, key, 'taken')] += taken; E[(w, key, 'dealt')] += dealt; E[(w, key, 'sd')] += sdead; E[(w, key, 'jd')] += jdead
print(ng, 'games, to r1000: melee walk-ins toward an enemy shooter outside fights; next 7 rounds per event')
for key in ('not engaged, nearest=shooter', 'not engaged, nearest=other'):
    for w in ('us', 'them'):
        m = max(1, E[(w, key)])
        print(f"  {key:28} {w:4} {E[(w, key)] / ng:5.1f}/game  shots taken from it {E[(w, key, 'taken')] / m:4.2f}  hits on it {E[(w, key, 'dealt')] / m:4.2f}  it died {E[(w, key, 'sd')] / m:4.2f}  walker died {E[(w, key, 'jd')] / m:4.2f}  its hits on any enemy {E[(w, key, 'any')] / m:4.2f}")
