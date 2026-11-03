"""Who takes the big gold captures in the opening: python -I capwho.py R MINGOLD DIR...  Teams with a Vesper only. Per champion type: events a game, health share at the event,
and for events not taken by Vesper: her distance to the capture, how often she is within 6, within 12, dead."""
import collections, os, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
R, MING, dirs = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3:]
C = collections.Counter(); H = collections.defaultdict(list); DV = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(dirs):
    n = len(rows[0]['c'])
    for t in (0, 1):
        idx = [i for i, c in enumerate(rows[0]['c']) if c['t'] == t]
        ves = [i for i in idx if D.NAMES[rows[0]['c'][i]['ty']] == 'vesper']
        if not ves:
            continue
        w = D.who(t, us)
        C[(w, 'games')] += 1
        v = ves[0]
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R:
                break
            if any(a['c'][j]['a'] and not b['c'][j]['a'] for j in range(n)):
                continue
            for i in idx:
                p, c = a['c'][i], b['c'][i]
                if not (p['a'] and c['a']):
                    continue
                d = D.gold_held(meta, c) - D.gold_held(meta, p)
                base = d / (1.33 if i == v else 1.0)
                if base < MING:
                    continue
                ty = D.NAMES[c['ty']]
                C[(w, 'ev', ty)] += 1
                C[(w, 'gold', ty)] += d
                if c.get('mhp'):
                    H[(w, ty)].append(c['hp'] / c['mhp'])
                if i != v:
                    vc = b['c'][v]
                    if not vc['a']:
                        DV[w].append(999)
                    elif 'x' in vc and 'x' in c:
                        DV[w].append(D.dist((vc['x'], vc['y']), (c['x'], c['y'])))
for w in ('us', 'them'):
    g = max(1, C[(w, 'games')])
    print(w, 'games', g)
    for k in sorted({k[2] for k in C if k[0] == w and k[1] == 'ev'}, key=lambda t: -C[(w, 'ev', t)]):
        h = H.get((w, k), [])
        print(f"   {k:10} events {C[(w,'ev',k)]/g:5.2f}  gold {C[(w,'gold',k)]/g:6.1f}" + (f"  health {sum(h)/len(h):.2f} under.45 {sum(x<.45 for x in h)/len(h):.2f}" if h else ''))
    dv = DV[w]
    if dv:
        s = sorted(dv)
        print(f"   not Vesper: {len(dv)/g:.2f} a game; she is dead {sum(x==999 for x in dv)/len(dv):.2f}, within 6 {sum(x<=6 for x in dv)/len(dv):.2f}, within 12 {sum(x<=12 for x in dv)/len(dv):.2f}, median {s[len(s)//2]}")
