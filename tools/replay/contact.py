# Contact episodes to r1000: the first round an enemy champion (off its spawn) is within 4 of a champion after 10 rounds
# with none within 4. Per side, by numbers at that round (allies within 6 incl. self vs enemies within 6) and health
# (80%+, 50-80%, under 50%): episodes per game, P(death within 15 rounds), P(an enemy within 6 at the start dies within
# 15), and the champion's next 5 rounds: share hitting a champion, share moving away from the nearest enemy.
# usage: python -I tools/replay/contact.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    last_near = [-99] * n
    for k in range(len(rows) - 16):
        b = rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            c = b['c'][i]
            if not off(c): continue
            p = (c['x'], c['y']); t = c['t']
            en4 = [j for j in range(n) if b['c'][j]['t'] != t and off(b['c'][j]) and D.dist(p, (b['c'][j]['x'], b['c'][j]['y'])) <= 4]
            if not en4: continue
            fresh = k - last_near[i] > 10; last_near[i] = k
            if not fresh: continue
            en6 = [j for j in range(n) if b['c'][j]['t'] != t and off(b['c'][j]) and D.dist(p, (b['c'][j]['x'], b['c'][j]['y'])) <= 6]
            al6 = sum(1 for j in range(n) if b['c'][j]['t'] == t and off(b['c'][j]) and D.dist(p, (b['c'][j]['x'], b['c'][j]['y'])) <= 6)
            diff = max(-2, min(1, al6 - len(en6)))
            hf = c.get('hp', 0) / max(1, c.get('mhp', 1))
            hb = '80+' if hf >= 0.8 else '50-80' if hf >= 0.5 else '<50'
            w = D.who(t, us)
            dies = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 16))
            kills = any(not rows[kk]['c'][j]['a'] for j in en6 for kk in range(k + 1, k + 16))
            hit = away = steps = 0
            for kk in range(k, k + 5):
                r0, r1 = rows[kk], rows[kk + 1]
                if not (r0['c'][i]['a'] and r1['c'][i]['a'] and 'x' in r1['c'][i]): break
                steps += 1
                hit += bool(D.enemy_hits(r0, i, n))
                q0 = (r0['c'][i]['x'], r0['c'][i]['y']); q1 = (r1['c'][i]['x'], r1['c'][i]['y'])
                ens = [(r0['c'][j]['x'], r0['c'][j]['y']) for j in range(n) if r0['c'][j]['t'] != t and off(r0['c'][j])]
                if ens and q1 != q0 and min(D.dist(q1, e) for e in ens) > min(D.dist(q0, e) for e in ens): away += 1
            for key in ((w, diff, hb), (w, diff, 'all'), (w, 'all', 'all')):
                C[key] += 1; C[key + ('d',)] += dies; C[key + ('k',)] += kills; C[key + ('h',)] += hit; C[key + ('a',)] += away; C[key + ('s',)] += steps
print(f'{ng} games to r1000: contact episodes (enemy within 4 after 10 quiet rounds) by numbers (allies incl. self - enemies, within 6) and health')
print('  cell             us: per game  P(die15) P(kill15) hit away   |  them: per game  P(die15) P(kill15) hit away')
cells = [('all', 'all')] + [(d, 'all') for d in (1, 0, -1, -2)] + [(d, h) for d in (1, 0, -1, -2) for h in ('80+', '50-80', '<50')]
for d, h in cells:
    out = []
    for w in ('us', 'them'):
        key = (w, d, h); m = max(1, C[key]); s = max(1, C[key + ('s',)])
        out.append(f"{C[key] / ng:5.2f}  {C[key + ('d',)] / m:.3f}  {C[key + ('k',)] / m:.3f}  {C[key + ('h',)] / s:.2f} {C[key + ('a',)] / s:.2f}")
    lab = f"{'+' if d != 'all' and d > 0 else ''}{d}{'' if d != -2 else '-'} {h}"
    print(f'  {lab:14}  ' + '   |   '.join(out))
