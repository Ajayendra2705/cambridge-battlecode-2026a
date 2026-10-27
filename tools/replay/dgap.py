# How often our danger map is empty beside a pack: per our champion-round (to r1000, off spawn) with 2+ enemy champions
# within 8 (off their spawn), compute each enemy's one-round burst as knowledge.h does (str + max(str if reset, cast x
# focus) + str, Heart of Ruin scaled by missing health; stats from type base + items held) and whether it passes the
# danger filter (burst >= 30% of our current health; 15% for Cassi and Issac). Reports the share of such rounds with
# no enemy passing, the combined burst over our health, and P(death within 10 rounds) split by that.
# usage: python -I tools/replay/dgap.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
# base hp, hp growth, base str, str growth, base focus, focus growth, has attack reset, best cast x focus
T = {'ryth': (1200, 100, 45, 4.5, 100, 10, 1, 1.0), 'vesper': (1000, 100, 45, 5, 100, 10, 1, 0),
     'vendetta': (1000, 100, 70, 6, 100, 10, 1, 0), 'cassi': (600, 65, 30, 3, 100, 13, 0, 2.0),
     'issac': (900, 80, 45, 3, 100, 10, 1, 0), 'stellar': (650, 65, 30, 3.5, 70, 8.5, 0, 2.0),
     'prism': (700, 65, 35, 2.5, 80, 8, 0, 1.5), 'marcella': (1200, 100, 45, 4.5, 60, 14, 1, 2.0),
     'willow': (700, 50, 55, 3, 140, 5, 1, 0), 'ren': (900, 100, 35, 5, 100, 9, 0, 1.1),
     'varg': (1000, 100, 45, 5, 100, 10, 1, 0), 'tavi': (900, 75, 45, 5, 110, 10, 1, 1.6),
     'heart': (1000, 100, 30, 3, 100, 10, 0, 1.5)}
NAMES = D.ITEMS['v2_0_0']
def stats(o):
    b = T[D.NAMES[o['ty']]]
    g = {'str': 0.0, 'focus': 0.0, 'hp': 0.0}
    for idx, cnt in o.get('it', []):
        fs, kind = NAMES[idx].split(' ')
        fam, st = fs.split('_')
        if kind == 'shard': g[st] += cnt
        elif fam == 'power': g[st] += 6 * cnt
        elif fam == 'greed': g[st] += 35 * cnt
        elif fam == 'bruiser':
            for s in g: g[s] += (5 if s == st else 1) * cnt
        else: g[st] += 5 * cnt
    s = b[2] + b[3] * g['str']
    if D.NAMES[o['ty']] == 'ryth': s += 0.01 * b[1] * g['hp']
    return s, b[4] + b[5] * g['focus'], b[6], b[7]
def burst(o):
    s, f, reset, cast = stats(o)
    sc = 1.0 + 0.5 * (1 - o['hp'] / max(1, o['mhp'])) if D.NAMES[o['ty']] == 'heart' else 1.0
    return (s + max(s if reset else 0, cast * f) + s) * sc
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            if not off(c): continue
            w = D.who(c['t'], us)
            p = (c['x'], c['y'])
            ens = [a['c'][j] for j in range(n) if a['c'][j]['t'] != c['t'] and off(a['c'][j]) and D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) <= 8]
            if len(ens) < 2: continue
            hp = c['hp']; hf = hp / max(1, c['mhp'])
            frag = D.NAMES[c['ty']] in ('cassi', 'issac')
            bs = [burst(e) for e in ens]
            npass = sum(1 for x in bs if x >= hp * (0.15 if frag else 0.3))
            tot = sum(bs) / max(1, hp)
            dies = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 11))
            hb = 'hp80+' if hf >= 0.8 else 'hp50-80' if hf >= 0.5 else 'hp<50'
            nb = '3+' if len(ens) >= 3 else '2'
            for key in ((w, 'all'), (w, hb), (w, nb), (w, hb, nb)):
                C[key] += 1; C[key + ('empty',)] += npass == 0; C[key + ('dies',)] += dies
                C[key + ('empty', 'dies')] += dies and npass == 0
                C[key + ('tot',)] += tot
                C[key + ('emptybig',)] += npass == 0 and tot >= 0.3
print(f'{ng} games, our/their champion-rounds to r1000 with 2+ enemies within 8 (off spawn)')
for w in ('us', 'them'):
    for key in [(w, 'all'), (w, 'hp80+'), (w, 'hp50-80'), (w, 'hp<50'), (w, '2'), (w, '3+'), (w, 'hp80+', '3+'), (w, 'hp50-80', '3+')]:
        m = C[key]
        if not m: continue
        e = C[key + ('empty',)]
        print(f"  {' '.join(key):18} rounds/g {m / ng:6.1f}  no enemy passes {e / m:5.1%}  (with combined burst >= 30% hp {C[key + ('emptybig',)] / m:5.1%})"
              f"  combined burst/hp {C[key + ('tot',)] / m:4.2f}  P(dead10) empty {C[key + ('empty', 'dies')] / max(1, e):.3f} vs passing {(C[key + ('dies',)] - C[key + ('empty', 'dies')]) / max(1, m - e):.3f}")
