# Vesper's turn after an enemy champion hit her (attack or cast on her in the round before) with an enemy champion (off
# its spawn) within her range 3 at the round start, to r1000, us vs them. Each turn is classified by its actions:
# shot and dash (in either order), shot only, dash and walk, dash only, walk only, nothing; per health band at the round
# start, with per game counts, P(she dies within 10 rounds) and P(an enemy champion dies within 10 rounds within 6 tiles
# of her start).
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, NAMES
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    for k in range(1, len(rows) - 11):
        a, p = rows[k], rows[k - 1]
        if a['r'] > 1000: break
        for i in range(n):
            v = a['c'][i]
            if NAMES[v['ty']] != 'vesper' or pos(v) is None: continue
            hit = any(x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' and x[-1] == i
                      for j in range(n) if p['c'][j]['t'] != v['t'] for x in (p['act'][j] if j < len(p['act']) else []))
            if not hit: continue
            foes = [j for j in range(n) if a['c'][j]['t'] != v['t'] and pos(a['c'][j]) and pos(a['c'][j]) not in spawn[a['c'][j]['t']]]
            if not any(dist(pos(v), pos(a['c'][j])) <= 3 for j in foes): continue
            acts = a['act'][i] if i < len(a['act']) else []
            shot = any(x[0] == 'attack' and x[-2] == 'c' for x in acts)
            dash = any(x[0] == 'cast' and x[1] == 1 for x in acts)
            walk = any(x[0] == 'move' for x in acts)
            kind = ('shot and dash' if dash else 'shot only') if shot else ('dash and walk' if walk else 'dash only') if dash \
                else 'walk only' if walk else 'nothing'
            hp = v['hp'] / v['mhp']
            band = 'hp 80+' if hp >= 0.8 else 'hp 50-80' if hp >= 0.5 else 'hp <50'
            died = any(not rows[t]['c'][i].get('a') for t in range(k + 1, k + 11))
            near = [j for j in foes if dist(pos(v), pos(a['c'][j])) <= 6]
            kill = any(not rows[t]['c'][j].get('a') for j in near for t in range(k + 1, k + 11))
            w = who(v['t'], us)
            for b in (band, 'all'):
                E[(w, b, kind)] += 1; E[(w, b, kind, 'died')] += died; E[(w, b, kind, 'kill')] += kill
                E[(w, b)] += 1
print(ng, 'games, to r1000: Vesper turns after a hit on her with an enemy champion within 3, per game; P(dies in 10), '
      'P(an enemy within 6 dies in 10)')
for b in ('all', 'hp 80+', 'hp 50-80', 'hp <50'):
    print(f'  {b:9} us {E[("us", b)] / ng:5.1f}/g   them {E[("them", b)] / ng:5.1f}/g')
    for kind in ('shot and dash', 'shot only', 'dash and walk', 'dash only', 'walk only', 'nothing'):
        s = []
        for w in ('us', 'them'):
            c = E[(w, b, kind)]
            s.append(f'{w:4} {c / ng:5.2f}/g {c / max(1, E[(w, b)]):4.2f}  dies {E[(w, b, kind, "died")] / max(1, c):4.2f}'
                     f'  kills {E[(w, b, kind, "kill")] / max(1, c):4.2f}')
        print(f'    {kind:14} ' + '   |   '.join(s))
