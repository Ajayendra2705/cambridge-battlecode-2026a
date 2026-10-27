# Deaths to r1000 by bag carried (the killer takes it): count and gems per game by bag bucket, us vs them; for bags of
# 20+, the share heading to an altar (3+ tiles closer over the last 6 rounds), at an altar (within 2), channelling a
# tribute in the last 3 rounds, enemies and allies within 6 at the last alive round, health 6 rounds before, and
# rounds since the bag first reached 20 (how long it was carried).
# usage: python -I tools/replay/bagdeath.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
B = lambda g: '0' if g == 0 else '1-9' if g < 10 else '10-19' if g < 20 else '20-39' if g < 40 else '40-79' if g < 80 else '80+'
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    altars = set()
    for r in rows:
        for acts in r['act'][:n]:
            for x in acts:
                if x[0] == 'tribute' and len(x) >= 3: altars.add((x[1], x[2]))
    if not altars: continue
    da = lambda p: min(D.dist(p, a) for a in altars)
    since20 = {}
    for k in range(7, len(rows)):
        r, q = rows[k], rows[k - 1]
        if r['r'] > 1000: break
        for i in range(n):
            c, p = r['c'][i], q['c'][i]
            if p['a'] and p.get('g', 0) >= 20 and i not in since20: since20[i] = k
            if p['a'] and p.get('g', 0) < 20: since20.pop(i, None)
            if not (p['a'] and not c['a'] and 'x' in p): continue
            w = D.who(p['t'], us); g = p.get('g', 0); b = B(g)
            C[(w, b, 'n')] += 1; C[(w, b, 'g')] += g
            if g < 20: continue
            o = rows[k - 7]['c'][i]
            pos = (p['x'], p['y'])
            toward = o['a'] and 'x' in o and da((o['x'], o['y'])) - da(pos) >= 3
            at = da(pos) <= 2
            chan = any(x[0] == 'tribute' for kk in range(k - 3, k) for x in (rows[kk]['act'][i] if i < len(rows[kk]['act']) else []))
            foes = sum(1 for e in q['c'] if e['a'] and 'x' in e and e['t'] != p['t'] and D.dist(pos, (e['x'], e['y'])) <= 6)
            al = sum(1 for e in q['c'] if e is not p and e['a'] and 'x' in e and e['t'] == p['t'] and D.dist(pos, (e['x'], e['y'])) <= 6)
            for key, v in (('toward', toward), ('at', at), ('chan', chan), ('foes', foes), ('allies', al),
                           ('hp6', o['hp'] / max(1, o['mhp']) if o['a'] else 0), ('carried', k - since20.get(i, k)),
                           ('daltar', da(pos))):
                C[(w, 'big', key)] += v
            C[(w, 'big', 'n')] += 1; C[(w, 'big', 'g')] += g
print(f'{ng} games, deaths to r1000 per game by bag at death (count / gems)')
for w in ('us', 'them'):
    print(f'  {w:4} ' + '  '.join(f"{b}: {C[(w, b, 'n')] / ng:.2f}/{C[(w, b, 'g')] / ng:.0f}" for b in ('0', '1-9', '10-19', '20-39', '40-79', '80+')))
for w in ('us', 'them'):
    nn = max(1, C[(w, 'big', 'n')])
    print(f"  {w:4} bag 20+: {C[(w, 'big', 'n')] / ng:.2f}/game; heading to altar {C[(w, 'big', 'toward')] / nn:.2f}, at altar {C[(w, 'big', 'at')] / nn:.2f}, "
          f"channelling {C[(w, 'big', 'chan')] / nn:.2f}, altar dist {C[(w, 'big', 'daltar')] / nn:.1f}, foes6 {C[(w, 'big', 'foes')] / nn:.2f}, allies6 {C[(w, 'big', 'allies')] / nn:.2f}, "
          f"hp 6 before {C[(w, 'big', 'hp6')] / nn:.2f}, rounds carried 20+ {C[(w, 'big', 'carried')] / nn:.0f}")
