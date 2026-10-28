# What a champion was doing when it walked into a shooter's range and took a first shot (rh_camein.py, "victim walked
# in", the shooter seen at the round start). Its step is split as in rh_camein.py's breakdown: toward its nearest enemy
# that is the shooter, toward its nearest enemy that is another enemy, or not toward its nearest enemy. Each is split by
# context, first match: tributed within 5 rounds (banking), bag of 30+ (carrying), hit a camp in the 3 rounds before or
# the round after (farming), under half health and stepping toward its own spawn (going home), any other step toward its
# own spawn, other. Per game, to r1000, us vs them.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, enemy_hits, RANGE
from rangedhits import pos
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    spawn = {t: [(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c] for t in (0, 1)}
    fought = [set(i for i in range(n) if enemy_hits(r, i, n)) for r in rows]
    lasthit = {}
    for k in range(4, len(rows) - 6):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            sh = a['c'][i]; ps = pos(sh)
            if ps is None or RANGE.get(sh['ty'], 1) < 3: continue
            for x in a['act'][i]:
                if x[0] != 'attack' or x[-2] != 'c': continue
                j = x[-1]
                if a['c'][j]['t'] == sh['t']: continue
                first = k - lasthit.get((i, j), -99) > 8
                lasthit[(i, j)] = k
                if not first or j in fought[k] or j in fought[k - 1]: continue
                pj = pos(a['c'][j]); q = (x[1], x[2])
                if pj is None or dist(pj, ps) <= 3 or q == pj or i not in a['vis'][j]: continue
                v = a['c'][j]
                foes = [e for e in range(n) if a['c'][e]['t'] != v['t'] and pos(a['c'][e]) and pos(a['c'][e]) not in spawn[a['c'][e]['t']]]
                near = min(foes, key=lambda e: dist(pj, pos(a['c'][e])))
                if near == i: step = 'toward nearest = the shooter'
                elif dist(q, pos(a['c'][near])) < dist(pj, pos(a['c'][near])): step = 'toward nearest = another enemy'
                else: step = 'not toward its nearest enemy'
                home = min(dist(pj, s) for s in spawn[v['t']]) > min(dist(q, s) for s in spawn[v['t']])
                acts = lambda t: rows[t]['act'][j] if j < len(rows[t]['act']) else []
                if any(y[0] == 'tribute' for t in range(k, k + 6) for y in acts(t)): ctx = 'banking (tribute within 5)'
                elif v.get('g', 0) >= 30: ctx = 'carrying 30+'
                elif any(y[0] == 'attack' and y[-2] == 'm' for t in (k - 3, k - 2, k - 1, k, k + 1) for y in acts(t)): ctx = 'farming (camp hits)'
                elif v['hp'] < 0.5 * v['mhp'] and home: ctx = 'going home hurt'
                elif home: ctx = 'toward own spawn'
                else: ctx = 'other'
                w = who(v['t'], us)
                E[(w, step, '')] += 1; E[(w, step, ctx)] += 1
print(ng, 'games, to r1000: first shots after the victim walked into a seen shooter\'s range, per game')
for step in ('toward nearest = the shooter', 'toward nearest = another enemy', 'not toward its nearest enemy'):
    print(f'  {step:44} us {E[("us", step, "")] / ng:5.2f}   them {E[("them", step, "")] / ng:5.2f}')
    for ctx in ('banking (tribute within 5)', 'carrying 30+', 'farming (camp hits)', 'going home hurt', 'toward own spawn', 'other'):
        print(f'    {ctx:42} us {E[("us", step, ctx)] / ng:5.2f}   them {E[("them", step, ctx)] / ng:5.2f}')
