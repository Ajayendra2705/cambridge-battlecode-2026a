"""Does stepping away from an enemy in reach work: python -I fleeok.py RMAX DIR...
A round in which a champion took a hit from an enemy champion, with that enemy in range of it or adjacent, and its action next round: hit a champion, or step away (distance from the hitter grows) or other.
Then: damage taken over the next 4 rounds (share of max health), dead within 12 rounds, hits dealt over the next 4 rounds. By side, health band at the decision, melee or ranged hitter."""
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
    cool = {}
    for k in range(len(rows) - 14):
        a = rows[k]
        if a['r'] > RM:
            break
        for h in range(n):
            for x in D.enemy_hits(a, h, n):
                v = x[-1]
                if cool.get(v, -99) > k:
                    continue
                vc, hc = a['c'][v], a['c'][h]
                b = rows[k + 1]
                vb = b['c'][v]; hb = b['c'][h]
                if not (vc['a'] and vb['a'] and hc['a'] and 'x' in vc and 'x' in hc and 'x' in vb and 'x' in hb):
                    continue
                cool[v] = k + 5
                d0 = D.dist((vc['x'], vc['y']), (hc['x'], hc['y']))
                d1 = D.dist((vb['x'], vb['y']), (hc['x'], hc['y']))
                if D.enemy_hits(b, v, n):
                    w = 'hit'
                elif d1 > d0:
                    w = 'away'
                else:
                    w = 'other'
                hb0 = vc.get('hp', 0) / max(1, vc.get('mhp', 1))
                band = 'hp>.5' if hb0 > .5 else 'hp.25-.5' if hb0 > .25 else 'hp<.25'
                hr = 'mel' if D.RANGE[hc['ty']] == 1 else 'rng'
                s = A[(D.who(vc['t'], us), band, hr, w)]
                s['n'] += 1
                c4 = rows[k + 4]['c'][v]
                s['loss'] += (vc.get('hp', 0) - (c4.get('hp', 0) if c4['a'] else 0)) / max(1, vc.get('mhp', 1))
                s['dead'] += any(not rows[k + t]['c'][v]['a'] for t in range(1, 13))
                s['hdead'] += any(not rows[k + t]['c'][h]['a'] for t in range(1, 13))
                s['deal'] += sum(len(D.enemy_hits(rows[k + t], v, n)) for t in range(1, 5))
print(ng, 'games. side, health, hitter, reaction: a game, health lost in 4 rounds, dies in 12, hitter dies in 12, hits dealt in 4')
for key in sorted(A, key=str):
    s = A[key]; m = max(1, s['n'])
    if s['n'] >= 30:
        print(f"{str(key):40} {s['n']/ng:5.2f} | lost {s['loss']/m:.2f} | dies {s['dead']/m:.2f} | hitter dies {s['hdead']/m:.2f} | hits {s['deal']/m:.1f}")
