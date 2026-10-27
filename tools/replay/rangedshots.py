# A ranged champion's contact rounds (TY=type index, default 1 = Vesper) by the nearest enemy champion's distance and whether a target in her reach cannot answer
# (distance over its basic range), to r1000: share hitting a champion, moving (step or dash), staying; P(dead in 10).
# Also splits rounds by whether the weakest enemy within 4 (absolute health: prey4; health fraction: tgt4) stands at 4 tiles.
# usage: [TY=1] python -I tools/replay/rangedshots.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
TY = int(os.environ.get('TY', 1))
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    for k in range(1, len(rows) - 11):
        a, b = rows[k], rows[k + 1]
        if b['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            if c['ty'] != TY or not off(c): continue
            p = (c['x'], c['y'])
            ens = [(D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])), j) for j in range(n) if a['c'][j]['t'] != c['t'] and off(a['c'][j])]
            if not ens: continue
            d = min(ens)[0]
            if d > 3: continue
            safe = any(dd > D.RANGE[a['c'][j]['ty']] for dd, j in ens if dd <= 3)
            hitprev = any(i == x[-1] for j in range(n) for x in D.enemy_hits(rows[k - 1], j, n))
            hf = c.get('hp', 0) / max(1, c.get('mhp', 1))
            hb = '80+' if hf >= 0.8 else '50-80' if hf >= 0.5 else '<50'
            hit = bool(D.enemy_hits(a, i, n))
            q = (b['c'][i]['x'], b['c'][i]['y']) if b['c'][i]['a'] and 'x' in b['c'][i] else p
            mv = D.dist(p, q)
            act = 'hit' if hit else 'move' if mv else 'stay'
            dies = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 11))
            w = D.who(c['t'], us)
            e4 = [(a['c'][j].get('hp', 0), dd, j) for dd, j in ens if dd <= 4]
            pr = min(e4)[1] if e4 else 9
            e4f = [(a['c'][j].get('hp', 0) / max(1, a['c'][j].get('mhp', 1)), dd, j) for dd, j in ens if dd <= 4]
            tf = min(e4f)[1] if e4f else 9
            pk = 'prey4' if pr == 4 else 'preyin'
            tk = 'tgt4' if tf == 4 else 'tgtin'
            for key in ((w, hb, 'any', pk), (w, hb, 'any', tk), (w, 'all', 'any', pk), (w, 'all', 'any', tk)):
                C[key] += 1; C[key + (act,)] += 1; C[key + ('d',)] += dies
                if not hit and mv: C[key + ('dash',)] += mv >= 2
            for key in ((w, hb, 'hp' if not hitprev else 'hit', d, safe), (w, 'all', d, safe), (w, hb, 'any', 'all')):
                C[key] += 1; C[key + (act,)] += 1; C[key + ('d',)] += dies
                if hit: C[key + ('hitmove',)] += mv > 0
                if not hit and mv: C[key + ('dash',)] += mv >= 2
print(f'{ng} games to r1000, {D.NAMES[TY]} with the nearest enemy champion within 3 (off spawns). safe = a target in her reach cannot answer')
for w in ('us', 'them'):
    for key in [(w, 'all', d, s) for d in (1, 2, 3) for s in (True, False)] + [(w, hb, 'any', k) for hb in ('all', '80+', '50-80', '<50') for k in ('prey4', 'preyin', 'tgt4', 'tgtin')]:
        m = C[key]
        if m < 20: continue
        print(f"  {w:4} {' '.join(str(x) for x in key[1:]):22} {m / ng:5.1f}/g  hit {C[key + ('hit',)] / m:.2f}  move {C[key + ('move',)] / m:.2f} (dash {C[key + ('dash',)] / max(1, C[key + ('move',)]):.2f})  stay {C[key + ('stay',)] / m:.2f}  P(dead10) {C[key + ('d',)] / m:.3f}")
