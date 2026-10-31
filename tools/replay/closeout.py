# Close-out of won positions: per side, games where its tributed gems plus its champions' bags first reach 1000 ("win in
# hand"), the rounds from then to the game end, and how many of those games it lost. Per game with --list.
# usage: python -I tools/replay/closeout.py DIR... [--list]
import os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
show = '--list' in sys.argv
dirs = [a for a in sys.argv[1:] if a != '--list']
S = {'us': [], 'them': []}  # (result for that side, rounds from win in hand to the end)
for us, res, mp, meta, rows in D.games(dirs):
    for side in (us, 1 - us):
        who = D.who(side, us)
        for r in rows:
            bags = sum(c.get('g', 0) for c in r['c'] if c['t'] == side and c['a'])
            if r['sg'][side] < 1000 <= r['sg'][side] + bags:
                won = (res == 'win') == (who == 'us')
                S[who].append((won, rows[-1]['r'] - r['r']))
                if show and not won: print(f"{who:4} {mp:24} lost, win in hand at r{r['r']} (trib {r['sg'][side]} + bags {bags}), "
                                           f"game end r{rows[-1]['r']}, rivals {r['sg'][1 - side]} then")
                break
for who, v in S.items():
    lost = [t for w, t in v if not w]
    print(f"{who:4} win in hand in {len(v)} games, lost {len(lost)}; rounds to the end median "
          f"{statistics.median([t for _, t in v]) if v else '-'}")
