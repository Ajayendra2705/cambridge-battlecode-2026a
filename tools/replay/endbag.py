# Bags at the end of lost games, by the losing side (us / them): the loser's tributed total and carried bag at the last
# decoded round, the winner's bag, and the games where the loser held 1000 in hand (tributed plus carried), with how many
# rounds before the end it first did. The result comes from index.txt (the last decoded round is one before the final
# tribute, so its totals do not tell the winner in close games). The 12 closest losses per side are listed.
# usage: python -I tools/replay/endbag.py DIR...
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who
S = collections.defaultdict(list)
for us, res, mp, meta, rows in games(sys.argv[1:]):
    last = rows[-1]
    sg = last['sg']
    lose = us if res == 'loss' else 1 - us
    win = 1 - lose
    bag = [sum(c.get('g', 0) for c in last['c'] if c['a'] and c['t'] == t) for t in (0, 1)]
    hand = [r['sg'][lose] + sum(c.get('g', 0) for c in r['c'] if c['a'] and c['t'] == lose) >= 1000 for r in rows]
    held = len(hand) - max((k + 1 for k, h in enumerate(hand) if not h), default=0)
    first = next((r['r'] for r, h in zip(rows, hand) if h), None)
    S[who(lose, us)].append((mp, last['r'], sg[lose], bag[lose], sg[win], bag[win], held, first))
for w in ('us', 'them'):
    L = S[w]
    if not L: continue
    n = len(L)
    print(f'{w} lost {n}: loser tributed {sum(x[2] for x in L) / n:.0f} bag {sum(x[3] for x in L) / n:.0f}; winner bag'
          f' {sum(x[5] for x in L) / n:.0f}; loser held 1000 in hand at the end {sum(1 for x in L if x[2] + x[3] >= 1000)},'
          f' ever {sum(1 for x in L if x[7] is not None)}; loser bag 100+ at the end {sum(1 for x in L if x[3] >= 100)},'
          f' 50+ {sum(1 for x in L if x[3] >= 50)}')
    for x in sorted(L, key=lambda x: -(x[2] + x[3]))[:12]:
        print(f'    {x[0]:24} end r{x[1]:5} loser {x[2]:4}+{x[3]:4} winner {x[4]:4}+{x[5]:4} held 1000 for the last {x[6]}'
              f' rounds, first r{x[7]}')
