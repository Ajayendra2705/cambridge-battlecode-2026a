# Games split by the death difference to r1000 (ours minus theirs): count, wins, tribute margin share.
# usage: python -I tools/replay/massgames.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
G = []
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c']); dead = collections.Counter(); last = rows[0]; first = {}
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        last = b
        for i in range(n):
            if a['c'][i]['a'] and not b['c'][i]['a']:
                w = D.who(a['c'][i]['t'], us); dead[w] += 1
                if dead[w] == 3 and w not in first: first[w] = b['r']
    G.append((dead['us'] - dead['them'], res == 'win', last['sg'][us] - last['sg'][1 - us], mp, dead['us'], dead['them'], first.get('us', 9999)))
tot = sum(g[2] for g in G)
for lo, hi in ((-99, -1), (0, 2), (3, 5), (6, 9), (10, 99)):
    s = [g for g in G if lo <= g[0] <= hi]
    if not s: continue
    print(f"death diff {lo:3}..{hi:3}: {len(s):3} games, {sum(g[1] for g in s):3} wins, margin/game {sum(g[2] for g in s)/len(s):6.0f}, share of total margin {sum(g[2] for g in s)/tot:5.0%}")
print(f"all {len(G)} games, margin/game {tot/len(G):.0f}")
