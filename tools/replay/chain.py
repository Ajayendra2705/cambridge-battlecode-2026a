# Chain deaths, to r1000: a champion dies within 60 rounds after a teammate died within 8 tiles of the spot. For each
# chain death: where the victim was when the teammate died (distance to that spot), whether it then closed in (its
# distance to the spot fell by 3+ before its own first hit), rounds from the first death to its own, enemies within 6
# at the first death spot then, and our allies alive near. Per side, per game.
# usage: python -I tools/replay/chain.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    deaths = []  # (k, i, pos)
    for k in range(1, len(rows)):
        if rows[k]['r'] > 1000: break
        for i in range(n):
            a, b = rows[k - 1]['c'][i], rows[k]['c'][i]
            if a['a'] and not b['a'] and 'x' in a: deaths.append((k, i, (a['x'], a['y'])))
    for k2, i2, p2 in deaths:
        t = rows[k2 - 1]['c'][i2]['t']; w = D.who(t, us)
        C[(w, 'deaths')] += 1
        first = [(k1, i1, p1) for k1, i1, p1 in deaths if i1 != i2 and rows[k1 - 1]['c'][i1]['t'] == t and 0 < k2 - k1 <= 60 and D.dist(p1, p2) <= 8]
        if not first: continue
        k1, i1, p1 = max(first)
        C[(w, 'chain')] += 1
        c1 = rows[k1]['c'][i2]
        if not (c1['a'] and 'x' in c1): C[(w, 'chain', 'dead or respawning at first')] += 1; continue
        d1 = D.dist((c1['x'], c1['y']), p1)
        # Its first hit by an enemy champion after k1.
        kh = next((kk for kk in range(k1, k2) if any(x[-1] == i2 for j in range(n) for x in D.enemy_hits(rows[kk], j, n))), k2 - 1)
        ch = rows[kh]['c'][i2]
        dh = D.dist((ch['x'], ch['y']), p1) if 'x' in ch else d1
        closed = dh <= d1 - 3
        ens = sum(1 for j in range(n) if rows[k1]['c'][j]['t'] != t and rows[k1]['c'][j]['a'] and 'x' in rows[k1]['c'][j] and D.dist((rows[k1]['c'][j]['x'], rows[k1]['c'][j]['y']), p1) <= 6)
        als = sum(1 for j in range(n) if j != i2 and rows[k1]['c'][j]['t'] == t and rows[k1]['c'][j]['a'] and 'x' in rows[k1]['c'][j] and D.dist((rows[k1]['c'][j]['x'], rows[k1]['c'][j]['y']), (c1['x'], c1['y'])) <= 6)
        db = '0-3' if d1 <= 3 else '4-6' if d1 <= 6 else '7-10' if d1 <= 10 else '11+'
        C[(w, 'chain', 'd1 ' + db)] += 1
        C[(w, 'chain', 'closed in')] += closed
        C[(w, 'chain', 'gap')] += k2 - k1
        C[(w, 'chain', 'gap<=10')] += k2 - k1 <= 10
        C[(w, 'chain', 'ens')] += ens
        C[(w, 'chain', 'als')] += als
        hf = c1.get('hp', 0) / max(1, c1.get('mhp', 1))
        C[(w, 'chain', 'hp80+')] += hf >= 0.8
print(f'{ng} games to r1000: chain deaths (a teammate died within 8 tiles of the spot in the 60 rounds before)')
for w in ('us', 'them'):
    m = max(1, C[(w, 'chain')])
    print(f"  {w:4} deaths {C[(w, 'deaths')] / ng:.2f}/g, chain {C[(w, 'chain')] / ng:.2f}/g ({C[(w, 'chain')] / max(1, C[(w, 'deaths')]):.0%})"
          f"; at the first death: distance to its spot " + ' '.join(f"{b}:{C[(w, 'chain', 'd1 ' + b)] / m:.0%}" for b in ('0-3', '4-6', '7-10', '11+'))
          + f", dead/respawning {C[(w, 'chain', 'dead or respawning at first')] / m:.0%}; 80%+ health {C[(w, 'chain', 'hp80+')] / m:.0%};"
          f" closed in 3+ before its first hit {C[(w, 'chain', 'closed in')] / m:.0%}; rounds between deaths {C[(w, 'chain', 'gap')] / m:.1f}"
          f" (within 10: {C[(w, 'chain', 'gap<=10')] / m:.0%}); enemies within 6 of the spot {C[(w, 'chain', 'ens')] / m:.1f}, its allies within 6 {C[(w, 'chain', 'als')] / m:.1f}")
