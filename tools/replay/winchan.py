# Long game-winning tribute channels per side: games where a champion started a tribute with its side's tributed gems
# plus its bag at 1000 or more and a bag of at least MINBAG (default 130, a channel of 13+ rounds), and how many of
# those games that side still lost (the channel broken by a stun, death or lock and the game lost later).
# usage: python -I tools/replay/winchan.py DIR... [--minbag N] [--list]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
args = sys.argv[1:]
minbag = int(args[args.index('--minbag') + 1]) if '--minbag' in args else 130
show = '--list' in args
dirs = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--minbag')]
S = {'us': [0, 0], 'them': [0, 0]}  # games with a long winning channel, games that side lost
for us, res, mp, meta, rows in D.games(dirs):
    for side in (us, 1 - us):
        who = D.who(side, us)
        first = None
        for r in rows:
            for i, c in enumerate(r['c']):
                if c['t'] != side or not c.get('a'): continue
                acts = r['act'][i] if i < len(r['act']) else []
                if any(x[0] == 'tribute' for x in acts) and c.get('g', 0) >= minbag and r['sg'][side] + c.get('g', 0) >= 1000:
                    first = (r['r'], c.get('g', 0)); break
            if first: break
        if not first: continue
        lost = (res == 'win') != (who == 'us')
        S[who][0] += 1; S[who][1] += lost
        if show: print(f"{who:4} {mp:24} r{first[0]} bag {first[1]} -> {'lost' if lost else 'won'} (end r{rows[-1]['r']})")
for who, (n, l) in S.items():
    print(f"{who:4} long winning channels in {n} games, lost {l} of them")
