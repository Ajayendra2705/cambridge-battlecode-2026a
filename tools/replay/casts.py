"""Ability casts per body to a round, us vs them, from decoded games (data/fights/<run>/).
usage: python -I tools/replay/casts.py [--round 1000] [--six] DIR...

Prints, per side and champion type, the games it played, casts of slot 0 and slot 1 per game, attacks per game and rounds alive,
so a body that never casts stands out. --six keeps only teams that field six bodies (Cassi and Issac on a five-pick map).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

args = sys.argv[1:]
last = 1000
if '--round' in args:
    k = args.index('--round')
    last = int(args[k + 1])
    del args[k:k + 2]
six = '--six' in args
if six:
    args.remove('--six')
T = {w: collections.defaultdict(collections.Counter) for w in ('us', 'them')}
ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    size = collections.Counter(c['t'] for c in rows[0]['c'])
    for k in range(1, len(rows)):
        r = rows[k]
        if r['r'] > last:
            break
        for e in range(n):
            me = r['c'][e]
            if six and size[me['t']] != 6:
                continue
            c = T[D.who(me['t'], us)][D.NAMES[me['ty']]]
            if k == 1:
                c['games'] += 1
            if me['a']:
                c['alive'] += 1
            for x in (r['act'][e] if e < len(r['act']) else []):
                if x[0] == 'cast':
                    c[f'slot{x[1]}'] += 1
                elif x[0] == 'attack':
                    c['attack'] += 1
print(ng, 'games, to round', last)
for w in ('us', 'them'):
    print(w)
    for name, c in sorted(T[w].items()):
        g = max(1, c['games'])
        print(f"  {name:10} {c['games']:4} bodies  slot0 {c['slot0'] / g:6.1f}  slot1 {c['slot1'] / g:6.1f}  attacks {c['attack'] / g:7.1f}  alive {c['alive'] / g:7.1f}")
