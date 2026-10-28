"""Per map, to r1000: games, wins, gems collected and tributed and deaths per game, us vs them, sorted by the
collected gap; gap/G is the map's share of the panel's collected gap per game (their minus our collected, summed over
the map's games, over all games). usage: python -I tools/replay/mapgap.py DIR [DIR ...] [--size N]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
args = sys.argv[1:]; SIZE = None
if '--size' in args:
    k = args.index('--size'); SIZE = int(args[k + 1]); args = args[:k] + args[k + 2:]
A = collections.Counter(); tot = collections.Counter()
for us, res, mp, meta, rows in D.games(args):
    s = len(rows[0]['c']) // 2
    if SIZE and s != SIZE: continue
    A[(mp, 'games')] += 1; A[(mp, 'wins')] += res == 'win'; tot['games'] += 1
    last = rows[0]
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        last = b
        for i, c in enumerate(b['c']):
            pc = a['c'][i]; w = D.who(c['t'], us)
            if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): A[(mp, w, 'coll')] += c['g'] - pc['g']
            if pc['a'] and not c['a']: A[(mp, w, 'deaths')] += 1
    for t in (0, 1): A[(mp, D.who(t, us), 'trib')] += last['sg'][t]
maps = sorted({k[0] for k in A}, key=lambda m: (A[(m, 'us', 'coll')] - A[(m, 'them', 'coll')]))
G = tot['games']
print(f'{G} games; per map: games, wins, collected us / them, tributed, deaths; gap share = (their - our collected) summed / games')
for m in maps:
    g = A[(m, 'games')]
    gap = (A[(m, 'them', 'coll')] - A[(m, 'us', 'coll')]) / G
    print(f'  {m:24} {g} {A[(m, "wins")]}  coll {A[(m, "us", "coll")] / g:5.0f} / {A[(m, "them", "coll")] / g:5.0f}  trib {A[(m, "us", "trib")] / g:5.0f} / {A[(m, "them", "trib")] / g:5.0f}  deaths {A[(m, "us", "deaths")] / g:4.1f} / {A[(m, "them", "deaths")] / g:4.1f}  gap/G {gap:+6.1f}')
