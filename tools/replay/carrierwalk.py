# Deaths with a bag of 30+ to r1000 away from altars (over 3 tiles) and not channelling: whether the carrier was heading
# to an altar (altar distance down 3+ over its last 8 alive rounds), heading home (spawn distance down 3+), or neither;
# how long it had carried 30+ (this life), the altar distance at death, enemies / allies within 6, and its health 8
# rounds before. Us vs them, per game.
# usage: python -I tools/replay/carrierwalk.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    altars = {(x[1], x[2]) for b in rows for acts in b['act'][:n] for x in acts if x[0] == 'tribute'}
    start = {i: (rows[0]['c'][i].get('x'), rows[0]['c'][i].get('y')) for i in range(n)}
    since = {}
    for k in range(9, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if pc['a'] and pc.get('g', 0) >= 30 and i not in since: since[i] = k - 1
            if pc['a'] and pc.get('g', 0) < 30: since.pop(i, None)
            if not (pc['a'] and not c['a'] and 'x' in pc): continue
            s0 = since.pop(i, None)
            if pc.get('g', 0) < 30 or not altars: continue
            w = D.who(pc['t'], us); p = (pc['x'], pc['y'])
            ad = min(D.dist(p, x) for x in altars)
            trib = any(x[0] == 'tribute' for kk in range(k - 3, k) for x in (rows[kk]['act'][i] if i < len(rows[kk]['act']) else []))
            if ad <= 3 or trib: continue
            o = rows[k - 9]['c'][i]
            if not (o['a'] and 'x' in o): continue
            q = (o['x'], o['y'])
            to_altar = min(D.dist(q, x) for x in altars) - ad >= 3
            to_home = start[i][0] is not None and D.dist(q, start[i]) - D.dist(p, start[i]) >= 3
            kind = 'to altar' if to_altar else 'to home' if to_home else 'other'
            e6 = sum(1 for x in a['c'] if x['a'] and 'x' in x and x['t'] != pc['t'] and D.dist((x['x'], x['y']), p) <= 6)
            a6 = sum(1 for j, x in enumerate(a['c']) if j != i and x['a'] and 'x' in x and x['t'] == pc['t'] and D.dist((x['x'], x['y']), p) <= 6)
            for key in ('all', kind):
                C[(w, key)] += 1; C[(w, key, 'g')] += pc['g']; C[(w, key, 'held')] += (k - 1 - s0) if s0 is not None else 0
                C[(w, key, 'ad')] += ad; C[(w, key, 'e6')] += e6; C[(w, key, 'a6')] += a6; C[(w, key, 'hp8')] += o['hp'] / o['mhp']
print(f'{ng} games to r1000: carrier (30+) deaths away from altars, per game (gems), held rounds, altar dist, e6/a6, hp 8 rounds before')
for key in ('all', 'to altar', 'to home', 'other'):
    for w in ('us', 'them'):
        m = max(1, C[(w, key)])
        print(f"  {key:8} {w:4} {C[(w, key)] / ng:.2f} ({C[(w, key, 'g')] / ng:4.1f})  held {C[(w, key, 'held')] / m:4.0f}  altar {C[(w, key, 'ad')] / m:4.1f}"
              f"  e6 {C[(w, key, 'e6')] / m:.1f} a6 {C[(w, key, 'a6')] / m:.1f}  hp8 {C[(w, key, 'hp8')] / m:.2f}")
