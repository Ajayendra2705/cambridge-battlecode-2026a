# Deaths per game to r1000 by team size (champions a side), us vs them, with wins; per run directory group.
# usage: python -I tools/replay/sizedeaths.py DIR[,DIR...] ...  (each argument is one group of run directories)
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who
for grp in sys.argv[1:]:
    E = collections.Counter()
    for us, res, mp, meta, rows in games(grp.split(',')):
        n = len(rows[0]['c']) // 2
        E[(n, 'g')] += 1; E[(n, 'w')] += res == 'win'
        prev = {}
        for r in rows:
            if r['r'] > 1000: break
            for c in r['c']:
                k = c.get('id', (c['t'], c['ty']))
                if prev.get(k) and not c.get('a'): E[(n, who(c['t'], us))] += 1
                prev[k] = c.get('a')
    print(grp)
    for n in sorted(set(k[0] for k in E)):
        g = E[(n, 'g')]
        print(f'  size {n}: {g:3} games, wins {E[(n, "w")]:3}, deaths us {E[(n, "us")] / g:.2f} them {E[(n, "them")] / g:.2f}')
