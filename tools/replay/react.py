"""Reaction to a first hit and focus fire: python -I react.py RMAX DIR...
Fight start: a champion hits an enemy champion after 15 rounds with no such hit between the teams. For the side hit first, over the next 6 rounds: the victim's hits on champions, the victim's
step away from the hitter (distance change), whether it died within 12 rounds, the number of its allies within 6 at the start and hitting within 6 rounds, and the same for the hitter's side.
Focus: rounds with at least two hits by one side: the share where all hits land on one champion, and the health share of the target compared with the other enemies in range."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
RM = int(sys.argv[1])
A = collections.defaultdict(collections.Counter)
ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    last = -99
    for k, a in enumerate(rows[:-13]):
        if a['r'] > RM:
            break
        hits = [(x[-1], i) for i in range(n) for x in D.enemy_hits(a, i, n)]
        # Focus
        for t in (0, 1):
            ht = [v for v, i in hits if a['c'][i]['t'] == t]
            if len(ht) >= 2:
                s = A[('focus', D.who(t, us))]
                s['n'] += 1
                s['one'] += len(set(ht)) == 1
                s['hits'] += len(ht); s['dist'] += len(set(ht))
        if not hits:
            continue
        if k - last < 15:
            last = k
            continue
        last = k
        v, h = hits[0]
        vc, hc = a['c'][v], a['c'][h]
        if 'x' not in vc or 'x' not in hc:
            continue
        side = D.who(vc['t'], us)
        R = a['r']
        band = 'r0-100' if R <= 100 else 'r100-300' if R <= 300 else 'r300+'
        s = A[('start', side, band)]
        s['n'] += 1
        d0 = D.dist((vc['x'], vc['y']), (hc['x'], hc['y']))
        s['d0'] += d0
        p0 = (vc['x'], vc['y'])
        allies = [j for j in range(n) if a['c'][j]['t'] == vc['t'] and j != v and a['c'][j]['a'] and 'x' in a['c'][j] and D.dist(p0, (a['c'][j]['x'], a['c'][j]['y'])) <= 6]
        foes = [j for j in range(n) if a['c'][j]['t'] == hc['t'] and a['c'][j]['a'] and 'x' in a['c'][j] and D.dist(p0, (a['c'][j]['x'], a['c'][j]['y'])) <= 6]
        s['allies'] += len(allies); s['foes'] += len(foes)
        vh = fh = ah = 0; first = None
        for t in range(1, 7):
            r = rows[k + t]
            nv = len(D.enemy_hits(r, v, n))
            if nv and first is None:
                first = t
            vh += nv
            ah += sum(len(D.enemy_hits(r, j, n)) for j in allies)
            fh += sum(len(D.enemy_hits(r, j, n)) for j in foes)
        s['vhit'] += vh; s['ahit'] += ah; s['fhit'] += fh
        s['backN'] += first is not None; s['backT'] += first or 0
        r6 = rows[k + 6]
        vc6, hc6 = r6['c'][v], r6['c'][h]
        if vc6['a'] and hc6['a'] and 'x' in vc6 and 'x' in hc6:
            s['n6'] += 1
            s['d6'] += D.dist((vc6['x'], vc6['y']), (hc6['x'], hc6['y']))
        s['vdead'] += any(not rows[k + t]['c'][v]['a'] for t in range(1, 13))
        s['hdead'] += any(not rows[k + t]['c'][h]['a'] for t in range(1, 13))
print(ng, 'games')
for key in sorted(A, key=str):
    s = A[key]; m = max(1, s['n'])
    if key[0] == 'focus':
        print(f"{str(key):22} rounds {s['n']/ng:6.1f} a game | all on one {s['one']/m:.2f} | hits {s['hits']/m:.2f} targets {s['dist']/m:.2f}")
    else:
        print(f"{str(key):34} {s['n']/ng:5.1f} | d {s['d0']/m:.1f} to {s['d6']/max(1,s['n6']):.1f} | near {s['allies']/m:.1f} allies {s['foes']/m:.1f} foes | hits in 6: victim {s['vhit']/m:.1f} allies {s['ahit']/m:.1f} foes {s['fhit']/m:.1f} | hits back {s['backN']/m:.2f} at {s['backT']/max(1,s['backN']):.1f} | victim dies {s['vdead']/m:.2f} hitter dies {s['hdead']/m:.2f}")
