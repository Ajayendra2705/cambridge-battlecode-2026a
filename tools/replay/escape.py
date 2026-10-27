# What happens to a hurt champion in contact, to r1000: the first round a champion (off spawn) is at under 50% health
# with an enemy champion within 4, after 10 rounds without that. Over the next 15 rounds: died, escaped (reached its
# spawn, or 7+ tiles from every enemy champion, alive at the end), or neither. Also how far it was from its spawn, the
# enemies and allies within 6, whether it moved away from the nearest enemy in the next round, and whether it was
# hit in the next 3 rounds.
# Then the chasers: champions within 4 of an enemy that just dropped under half health, whether they hit it within 3
# rounds, by health, distance, type and bag; and what those 2-4 tiles away that did not hit did instead.
# usage: python -I tools/replay/escape.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    quiet = [99] * n
    for k in range(len(rows) - 16):
        a = rows[k]
        if a['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            low = off(c) and c.get('hp', 0) < 0.5 * max(1, c.get('mhp', 1))
            p = (c['x'], c['y']) if 'x' in c else None
            ens = [(D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])), j) for j in range(n) if p and a['c'][j]['t'] != c['t'] and off(a['c'][j])] if low else []
            if not (low and ens and min(ens)[0] <= 4):
                quiet[i] += 1; continue
            fresh = quiet[i] >= 10; quiet[i] = 0
            if not fresh: continue
            t = c['t']; w = D.who(t, us)
            home = min(D.dist(p, q) for q in start[t])
            out = 'neither'
            for kk in range(k + 1, k + 16):
                o = rows[kk]['c'][i]
                if not o['a']: out = 'died'; break
            if out != 'died':
                for kk in range(k + 1, k + 16):
                    o = rows[kk]['c'][i]
                    q = (o['x'], o['y'])
                    if min(D.dist(q, s) for s in start[t]) <= 1: out = 'escaped'; break
                    e2 = [D.dist(q, (rows[kk]['c'][j]['x'], rows[kk]['c'][j]['y'])) for j in range(n) if rows[kk]['c'][j]['t'] != t and off(rows[kk]['c'][j])]
                    if not e2 or min(e2) >= 7: out = 'escaped'; break
            d0, j0 = min(ens)
            b = rows[k + 1]['c'][i]
            away = b['a'] and 'x' in b and D.dist((b['x'], b['y']), (a['c'][j0]['x'], a['c'][j0]['y'])) > d0
            hit3 = any(i == x[-1] for kk in range(k, k + 3) for j in range(n) for x in D.enemy_hits(rows[kk], j, n))
            e6 = sum(1 for d, j in ens if d <= 6)
            al = sum(1 for j in range(n) if j != i and a['c'][j]['t'] == t and off(a['c'][j]) and D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) <= 6)
            hb = 'home<=8' if home <= 8 else 'home9-16' if home <= 16 else 'home17+'
            for d, j in ens:
                if d > 4: continue
                cj = a['c'][j]; cw = D.who(cj['t'], us)
                hj = any(x[-1] == i for kk in range(k, k + 3) for x in D.enemy_hits(rows[kk], j, n))
                b2 = rows[k + 2]['c'][j]; b2i = rows[k + 2]['c'][i]
                closer = b2['a'] and 'x' in b2 and b2i['a'] and 'x' in b2i and D.dist((b2['x'], b2['y']), (b2i['x'], b2i['y'])) < d
                hfj = cj.get('hp', 0) / max(1, cj.get('mhp', 1))
                hk = 'hp80+' if hfj >= 0.8 else 'hp50-80' if hfj >= 0.5 else 'hp<50'
                if d >= 2 and not hj:
                    hc = D.enemy_hits(a, j, n); hm = D.camp_hits(a, j)
                    b1 = rows[k + 1]['c'][j]; b1i = rows[k + 1]['c'][i]
                    d1 = D.dist((b1['x'], b1['y']), (b1i['x'], b1i['y'])) if b1['a'] and 'x' in b1 and b1i['a'] and 'x' in b1i else d
                    mv = b1['a'] and 'x' in b1 and (b1['x'], b1['y']) != (cj['x'], cj['y'])
                    what = 'hit another champion' if hc else 'hit a camp' if hm else ('moved, farther' if d1 > d else 'moved, nearer' if d1 < d else 'moved, same') if mv else 'stayed'
                    melee = D.RANGE.get(cj['ty'], 1) <= 1
                    e6j = sum(1 for jj in range(n) if a['c'][jj]['t'] != cj['t'] and off(a['c'][jj]) and D.dist((cj['x'], cj['y']), (a['c'][jj]['x'], a['c'][jj]['y'])) <= 6)
                    a6j = 1 + sum(1 for jj in range(n) if jj != j and a['c'][jj]['t'] == cj['t'] and off(a['c'][jj]) and D.dist((cj['x'], cj['y']), (a['c'][jj]['x'], a['c'][jj]['y'])) <= 6)
                    nb = 'ahead' if a6j > e6j else 'even' if a6j == e6j else 'behind'
                    for key3 in ((cw, 'miss', 'melee' if melee else 'ranged', what), (cw, 'miss', 'melee' if melee else 'ranged', 'all'), (cw, 'missnb', 'melee' if melee else 'ranged', nb)):
                        C[key3] += 1
                for key2 in ((cw, 'chaser', 'all'), (cw, 'chaser', hk), (cw, 'chaser', 'd%d' % d), (cw, 'chaser', D.NAMES[cj['ty']] + (' d1' if d == 1 else ' d2-4')), (cw, 'chaser', ('bag30+' if cj.get('g', 0) >= 30 else 'bag<30') + (' d1' if d == 1 else ' d2-4'))):
                    C[key2] += 1; C[key2 + ('hit',)] += hj; C[key2 + ('closer',)] += closer; C[key2 + ('kill',)] += out == 'died'
            for key in ((w, 'all'), (w, hb)):
                C[key] += 1; C[key + (out,)] += 1; C[key + ('away',)] += away; C[key + ('hit3',)] += hit3
                C[key + ('e6',)] += e6; C[key + ('al',)] += al; C[key + ('home',)] += home
                C[key + ('hpf',)] += c.get('hp', 0) / max(1, c.get('mhp', 1))
print(f'{ng} games to r1000: a champion under 50% health with an enemy within 4 (after 10 rounds without), next 15 rounds')
for w in ('us', 'them'):
    for hb in ('all', 'home<=8', 'home9-16', 'home17+'):
        m = C[(w, hb)]
        if not m: continue
        print(f"  {w:4} {hb:9} {m / ng:5.2f}/g  died {C[(w, hb, 'died')] / m:.2f} escaped {C[(w, hb, 'escaped')] / m:.2f} neither {C[(w, hb, 'neither')] / m:.2f}"
              f" | health {C[(w, hb, 'hpf')] / m:.2f}, home {C[(w, hb, 'home')] / m:4.1f}, enemies6 {C[(w, hb, 'e6')] / m:.1f}, allies6 {C[(w, hb, 'al')] / m:.1f}, stepped away {C[(w, hb, 'away')] / m:.2f}, hit in 3 {C[(w, hb, 'hit3')] / m:.2f}")
print('chasers: champions within 4 of an enemy that just dropped under 50% health (above): hit it within 3 rounds, nearer to it 2 rounds later, it died within 15')
for w in ('us', 'them'):
    for hk in sorted({k[2] for k in C if len(k) == 3 and k[1] == 'chaser' and k[0] == w}):
        m = C[(w, 'chaser', hk)]
        if not m: continue
        print(f"  {w:4} {hk:8} {m / ng:5.2f}/g  hit {C[(w, 'chaser', hk, 'hit')] / m:.2f}  nearer {C[(w, 'chaser', hk, 'closer')] / m:.2f}  target died {C[(w, 'chaser', hk, 'kill')] / m:.2f}")
print('chasers 2-4 tiles away that did not hit the hurt enemy within 3 rounds: first-round action, and numbers (them incl. self vs enemies within 6)')
for w in ('us', 'them'):
    for kind in ('melee', 'ranged'):
        m = C[(w, 'miss', kind, 'all')]
        if not m: continue
        acts = sorted({k[3] for k in C if len(k) == 4 and k[:3] == (w, 'miss', kind) and k[3] != 'all'}, key=lambda x: -C[(w, 'miss', kind, x)])
        print(f"  {w:4} {kind:6} {m / ng:5.2f}/g  " + '  '.join(f"{x} {C[(w, 'miss', kind, x)] / m:.0%}" for x in acts)
              + ' | ' + ' '.join(f"{nb} {C[(w, 'missnb', kind, nb)] / m:.0%}" for nb in ('ahead', 'even', 'behind')))
