# Idle fight rounds: after a fight starts on a champion at half health or more (as `decoded.py defend`), its rounds with no action off a dead group's tile; share with an enemy cast on it (targeted, or a ground cast landing within 1) that round or the round before, with an enemy in its basic reach, and by type. python -I tools/replay/stillstun.py SIZE DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
size = int(sys.argv[1])
A = collections.defaultdict(collections.Counter)
def cast_on(row, j, n, pos, team):
    for i in range(n):
        ci = row['c'][i]
        if ci['t'] == team: continue
        for y in (row['act'][i] if i < len(row['act']) else []):
            if y[0] != 'cast': continue
            if len(y) >= 6 and y[-2] == 'c' and y[-1] == j: return True
            if len(y) == 4 and max(abs(y[2] - pos[0]), abs(y[3] - pos[1])) <= 1: return True
    return False
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    n = len(rows[0]['c'])
    if n != 2 * size: continue
    grp, members, gtiles = D.camp_groups(rows, n)
    last_hit = {}
    for k, a in enumerate(rows):
        if a['r'] > 1000 or k + 11 >= len(rows) or k < 1: continue
        for i in range(n):
            for x in D.enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j)); fresh = k - last_hit.get(key, -99) > 15; last_hit[key] = k
                dc = a['c'][j]
                if not fresh or 'x' not in dc or dc.get('hp', 0) < 0.5 * max(1, dc.get('mhp', 1)): continue
                w = D.who(dc['t'], us)
                for s in range(k, k + 6):
                    r0 = rows[s]; v0 = r0['c'][j]
                    if not v0['a'] or 'x' not in v0: break
                    acts = r0['act'][j] if j < len(r0['act']) else []
                    if acts: continue
                    p = (v0['x'], v0['y'])
                    if any(p in gtiles[g] and all(r0['mh'][m] == 0 for m in members[g] if m < len(r0['mh'])) for g in gtiles): continue
                    A[w]['nothing'] += 1
                    if cast_on(rows[s - 1], j, n, p, dc['t']) or cast_on(r0, j, n, p, dc['t']): A[w]['cast on it'] += 1
                    foes = [o for o in r0['c'] if o['t'] != dc['t'] and o['a'] and 'x' in o]
                    rng = D.RANGE.get(v0['ty'], 1)
                    if any(D.dist(p, (o['x'], o['y'])) <= rng for o in foes): A[w]['enemy in reach'] += 1
                    A[w]['type ' + D.NAMES[v0['ty']]] += 1
for w in ('us', 'them'):
    C = A[w]; m = max(1, C['nothing'])
    print(w, C['nothing'], 'nothing rounds;', ' '.join(f'{k} {v / m:.2f}' for k, v in sorted(C.items()) if k != 'nothing'))
