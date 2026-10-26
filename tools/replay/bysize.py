# Per decoded run (python -I tools/replay/bysize.py DIR...): games, wins, our deaths and theirs per game by r1000, by team size (from the decoded rows).
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

for d in sys.argv[1:]:
    C = collections.Counter()
    for us, res, mp, meta, rows in D.games([d]):
        size = len(rows[0]['c']) // 2
        C[(size, 'games')] += 1
        C[(size, 'wins')] += res == 'win'
        prev = None
        for r in rows:
            if r['r'] > 1000: break
            if prev is not None:
                for i, c in enumerate(r['c']):
                    if prev['c'][i]['a'] and not c['a']: C[(size, 'd ' + D.who(c['t'], us))] += 1
            prev = r
    line = f'{d.split("/")[-1]:24}'
    for s in (3, 4, 5):
        g = max(1, C[(s, 'games')])
        line += f'  {s}: {C[(s, "wins")]}/{C[(s, "games")]} deaths {C[(s, "d us")] / g:.2f} vs {C[(s, "d them")] / g:.2f}'
    print(line)
