# Step-ins by melee champions, to r1000: a round where a melee champion (off spawn) 2-3 tiles from its nearest enemy
# champion ends within 1 tile of an enemy's round-start tile, nearer to it than it started (its own step or dash in).
# Per type and side: step-ins per game, share that hit that round, numbers at the start (itself + allies within 6 vs
# enemies within 6: ahead / even / behind), health, start distance, and P(death within 10); the last line pools the
# step-ins made behind in numbers per game over all types.
# usage: python -I tools/replay/closein.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0; G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    for c in rows[0]['c']: G[(D.who(c['t'], us), c['ty'])] += 1
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    for k in range(len(rows) - 11):
        a, b = rows[k], rows[k + 1]
        if b['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            if D.RANGE.get(c['ty'], 1) > 1 or not off(c): continue
            p = (c['x'], c['y'])
            ens = [(D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])), j) for j in range(n) if a['c'][j]['t'] != c['t'] and off(a['c'][j])]
            if not ens: continue
            d0 = min(ens)[0]
            if d0 not in (2, 3): continue
            o = b['c'][i]
            if not (o['a'] and 'x' in o): continue
            q = (o['x'], o['y'])
            adj = any(D.dist(q, (a['c'][j]['x'], a['c'][j]['y'])) <= 1 < D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) for d, j in ens if d <= 3)
            w = D.who(c['t'], us); ty = D.NAMES[c['ty']]
            C[(w, ty, 'rounds23')] += 1
            if not adj or q == p: continue
            e6 = sum(1 for d, j in ens if d <= 6)
            al = 1 + sum(1 for j in range(n) if j != i and a['c'][j]['t'] == c['t'] and off(a['c'][j]) and D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) <= 6)
            nb = 'ahead' if al > e6 else 'even' if al == e6 else 'behind'
            hit = bool(D.enemy_hits(a, i, n))
            dies = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 11))
            hf = c.get('hp', 0) / max(1, c.get('mhp', 1))
            hb = 'hp80+' if hf >= 0.8 else 'hp50-80' if hf >= 0.5 else 'hp<50'
            for key in ((w, ty, 'all'), (w, ty, nb), (w, ty, hb), (w, ty, 'd%d' % d0), (w, 'pooled', nb)):
                C[key] += 1; C[key + ('hit',)] += hit; C[key + ('dies',)] += dies
print(f'{ng} games to r1000: melee step-ins (2-3 tiles from the nearest enemy, then within 1 of an enemy by its own move), per champion-game')
for ty in sorted({k[1] for k in C if k[1] != 'pooled'}):
    for w in ('us', 'them'):
        g = G[(w, D.NAMES.index(ty))]
        if g < 15 or not C[(w, ty, 'all')]: continue
        line = f"  {ty:9} {w:4} n={g:3} rounds at 2-3 tiles {C[(w, ty, 'rounds23')] / g:5.1f}, step-ins {C[(w, ty, 'all')] / g:4.1f} (hit {C[(w, ty, 'all', 'hit')] / C[(w, ty, 'all')]:.2f}, P(dead10) {C[(w, ty, 'all', 'dies')] / C[(w, ty, 'all')]:.3f})"
        for k in ('ahead', 'even', 'behind', 'hp80+', 'hp50-80', 'hp<50', 'd2', 'd3'):
            m = C[(w, ty, k)]
            if m: line += f" | {k} {m / C[(w, ty, 'all')]:.0%} P {C[(w, ty, k, 'dies')] / m:.3f}"
        print(line)
for w in ('us', 'them'):
    m = C[(w, 'pooled', 'behind')]
    print(f"  {w:4} all melee: step-ins behind in numbers {m / max(1, ng):.2f} per game, P(death within 10) {C[(w, 'pooled', 'behind', 'dies')] / max(1, m):.3f}")
