"""Her first capture events: python -I vesfirst.py TYPE DIR...  median round, base gold band, gems, walk from start tile, teammates within 6, helpers (hit a camp within 4 tiles in the 25 rounds before)."""
import collections, os, sys, statistics as st
sys.path.insert(0, 'tools/replay')
import decoded as D
want, dirs = sys.argv[1], sys.argv[2:]
E = collections.defaultdict(list)
Nn = collections.Counter()
for us, res, mp, meta, rows in D.games(dirs):
    n = len(rows[0]['c'])
    for i, c0 in enumerate(rows[0]['c']):
        if D.NAMES[c0['ty']] != want:
            continue
        w = D.who(c0['t'], us)
        Nn[w] += 1
        start = (c0.get('x', 0), c0.get('y', 0))
        for r1 in rows[1:6]:
            if 'x' in r1['c'][i]:
                start = (r1['c'][i]['x'], r1['c'][i]['y']); break
        cnt = 0
        for kb in range(1, min(len(rows), 400)):
            a, b = rows[kb - 1], rows[kb]
            p, c = a['c'][i], b['c'][i]
            if not (p['a'] and c['a']) or any(a['c'][j]['a'] and not b['c'][j]['a'] for j in range(n)):
                continue
            d = D.gold_held(meta, c) - D.gold_held(meta, p); dg = c.get('g', 0) - p.get('g', 0)
            if not (d > 0 or dg > 0) or 'x' not in c:
                continue
            base = max(0, d) / (1.33 if want == 'vesper' else 1.0)
            near = sum(1 for j, o in enumerate(b['c']) if j != i and o['a'] and 'x' in o and o['t'] == c['t'] and D.dist((o['x'], o['y']), (c['x'], c['y'])) <= 6)
            helpers = set()
            for rr in rows[max(0, kb - 25):kb]:
                for j in range(n):
                    o = rr['c'][j]
                    if j != i and o['t'] == c['t'] and 'x' in o and D.camp_hits(rr, j) and D.dist((o['x'], o['y']), (c['x'], c['y'])) <= 4:
                        helpers.add(j)
            E[(w, cnt)].append((b['r'], base, dg, D.dist(start, (c['x'], c['y'])), near, len(helpers)))
            cnt += 1
            if cnt >= 4:
                break
for w in ('us', 'them'):
    print(w, 'champion-games', Nn[w])
    for k in range(4):
        v = E[(w, k)]
        if not v:
            continue
        rr = [x[0] for x in v]
        print(f"  capture {k+1}: reached {len(v)/max(1,Nn[w]):.2f}  round med {st.median(rr):.0f}  base gold {sum(x[1] for x in v)/len(v):.0f} (0: {sum(x[1]<1 for x in v)/len(v):.2f}, <=25: {sum(0<x[1]<=25 for x in v)/len(v):.2f}, 26-59: {sum(25<x[1]<60 for x in v)/len(v):.2f}, 60+: {sum(x[1]>=60 for x in v)/len(v):.2f})  gems {sum(x[2] for x in v)/len(v):.1f}  walk {st.median(x[3] for x in v):.0f}  near {sum(x[4] for x in v)/len(v):.1f}  helpers {sum(x[5] for x in v)/len(v):.1f}")
