# 5-a-side games, to r1000: deaths per game of each champion type, us vs them (per game in which that side has the type).
# usage: python -I tools/replay/typedeaths5.py DIR[,DIR...] ...  (each argument is one group of run directories)
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES
for grp in sys.argv[1:]:
    D = collections.Counter(); G = collections.Counter()
    for us, res, mp, meta, rows in games(grp.split(',')):
        if len(rows[0]['c']) != 10: continue
        for c in rows[0]['c']: G[(NAMES[c['ty']], who(c['t'], us))] += 1
        prev = {}
        for r in rows:
            if r['r'] > 1000: break
            for c in r['c']:
                k = (c['t'], c['ty'])
                if prev.get(k) and not c.get('a'): D[(NAMES[c['ty']], who(c['t'], us))] += 1
                prev[k] = c.get('a')
    print(grp)
    for ty in sorted(set(k[0] for k in G)):
        cells = [f'{w} {D[(ty, w)] / G[(ty, w)]:.2f} ({G[(ty, w)]})' if G[(ty, w)] else f'{w}    -' for w in ('us', 'them')]
        print(f'  {ty:9} ' + '   '.join(cells))
