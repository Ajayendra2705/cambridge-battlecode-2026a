# Per decoded run (python -I tools/replay/bysize.py DIR...): games, wins, and per game by r1000 our deaths and theirs, gems
# collected and tributed, by team size (from the decoded rows).
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
                    pc = prev['c'][i]; w = D.who(c['t'], us)
                    if pc['a'] and not c['a']: C[(size, 'd ' + w)] += 1
                    if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): C[(size, 'c ' + w)] += c['g'] - pc['g']
            prev = r
        for t in (0, 1): C[(size, 't ' + D.who(t, us))] += prev['sg'][t]
    line = f'{d.split("/")[-1]:24}'
    for s in (3, 4, 5):
        g = max(1, C[(s, 'games')])
        line += (f'  {s}: {C[(s, "wins")]}/{C[(s, "games")]} deaths {C[(s, "d us")] / g:.2f} vs {C[(s, "d them")] / g:.2f}'
                 f' coll {C[(s, "c us")] / g:.0f} vs {C[(s, "c them")] / g:.0f} trib {C[(s, "t us")] / g:.0f} vs {C[(s, "t them")] / g:.0f}')
    print(line)
