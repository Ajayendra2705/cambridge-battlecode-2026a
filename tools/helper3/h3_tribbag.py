"""Bag at tribute start and bag at death, per side, from decoded games (h3, 10-28).

usage: python -I tools/helper3/h3_tribbag.py [--upto R] DIR [DIR ...]   (default R 1000; decoded runs, pooled)

A tribute start is a 'tribute' action in a champion's round (the channel's first turn); its bag is the champion's
gems that round. Prints per side: tribute starts per game, the bag's quartiles and mean, the share of starts over 40,
60 and 100 gems; deaths with a bag per game and their bag's quartiles; and the gems lost on death per game.
"""
import collections, os, statistics, sys

sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]
R = 1000
if '--upto' in args:
    i = args.index('--upto'); R = int(args[i + 1]); del args[i:i + 2]
T = collections.defaultdict(list); Dd = collections.defaultdict(list); ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if b['r'] > R: break
        for i in range(n):
            c = a['c'][i]
            w = 'us' if c['t'] == us else 'them'
            acts = a['act'][i] if i < len(a['act']) else []
            if c['a'] and c.get('g', 0) > 0 and any(x[0] == 'tribute' for x in acts): T[w].append(c['g'])
            if c['a'] and not b['c'][i]['a'] and c.get('g', 0) > 0: Dd[w].append(c['g'])


def q(v):
    if len(v) < 4: return 'n/a'
    qs = statistics.quantiles(v, n=4)
    return f'q1 {qs[0]:.0f} median {qs[1]:.0f} q3 {qs[2]:.0f} mean {statistics.mean(v):.0f}'


print(f'{ng} games to r{R}: ' + ', '.join(args))
for w in ('us', 'them'):
    t = T[w]
    print(f'  {w:4} tribute starts {len(t) / ng:5.1f}/game  bag {q(t)}  over 40 {sum(x > 40 for x in t) / max(1, len(t)):.0%},'
          f' over 60 {sum(x > 60 for x in t) / max(1, len(t)):.0%}, over 100 {sum(x > 100 for x in t) / max(1, len(t)):.0%}')
    print(f'       deaths with a bag {len(Dd[w]) / ng:4.2f}/game  bag {q(Dd[w])}  lost {sum(Dd[w]) / ng:.0f} gems/game')
