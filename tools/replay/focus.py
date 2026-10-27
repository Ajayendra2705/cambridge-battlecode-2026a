# Focus fire, to r1000: in rounds where 2+ champions of a side hit enemy champions, the share where all of them hit
# one target; per hit, whether the target was the lowest-health (fraction) enemy champion within the hitter's reach;
# and the share of hit targets dying within 10 rounds.
# usage: python -I tools/replay/focus.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > 1000: break
        for t in (0, 1):
            w = D.who(t, us)
            hits = {}
            for i in range(n):
                if a['c'][i]['t'] != t: continue
                tg = {x[-1] for x in D.enemy_hits(a, i, n)}
                if tg and 'x' in a['c'][i]: hits[i] = tg
            for i, tg in hits.items():
                c = a['c'][i]; p = (c['x'], c['y']); rng = D.RANGE.get(c['ty'], 1)
                cand = [j for j in range(n) if a['c'][j]['t'] != t and a['c'][j]['a'] and 'x' in a['c'][j] and D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) <= max(rng, 1)]
                if len(cand) >= 2:
                    low = min(cand, key=lambda j: a['c'][j].get('hp', 0) / max(1, a['c'][j].get('mhp', 1)))
                    C[(w, 'choice')] += 1; C[(w, 'lowest')] += low in tg
                for j in tg:
                    C[(w, 'hits')] += 1
                    C[(w, 'hit dies10')] += any(not rows[kk]['c'][j]['a'] for kk in range(k + 1, k + 11))
            if len(hits) >= 2:
                C[(w, 'multi')] += 1
                C[(w, 'same')] += len(set.union(*hits.values())) == 1
print(f'{ng} games to r1000')
for w in ('us', 'them'):
    print(f"  {w:4} rounds with 2+ hitters {C[(w, 'multi')] / ng:5.1f}/g, all on one target {C[(w, 'same')] / max(1, C[(w, 'multi')]):.2f};"
          f" hits with 2+ enemies in reach on the lowest-health one {C[(w, 'lowest')] / max(1, C[(w, 'choice')]):.2f} ({C[(w, 'choice')] / ng:.1f}/g);"
          f" hit targets dying within 10 {C[(w, 'hit dies10')] / max(1, C[(w, 'hits')]):.3f}")
