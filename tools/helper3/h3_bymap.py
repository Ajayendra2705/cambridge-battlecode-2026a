"""Per map and in total, to round R: gems collected, tributed, lost on death and deaths, us vs them (h3, 10-28).

usage: python -I tools/helper3/h3_bymap.py [--upto R] DIR [DIR ...]      (default R 1000)

The numbers of `decoded.py gems` (collected = a champion's bag rises while alive; tributed at the last round to R;
lost on death = bag at death), split by the map of each game. Several DIRs pool; to compare two candidates, run it
once per candidate's folder.
"""
import collections, os, sys

sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]
R = 1000
if '--upto' in args:
    i = args.index('--upto'); R = int(args[i + 1]); del args[i:i + 2]
A = collections.defaultdict(collections.Counter)
for us, res, mp, meta, rows in D.games(args):
    for key in (mp, 'total'):
        A[key]['games'] += 1; A[key]['wins'] += res == 'win'
    last = rows[0]
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        last = b
        for i, c in enumerate(b['c']):
            pc = a['c'][i]; w = 'us' if c['t'] == us else 'them'
            for key in (mp, 'total'):
                if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): A[key][w, 'collected'] += c['g'] - pc['g']
                if pc['a'] and not c['a']: A[key][w, 'lost'] += pc.get('g', 0); A[key][w, 'deaths'] += 1
    for key in (mp, 'total'):
        A[key]['us', 'tributed'] += last['sg'][us]; A[key]['them', 'tributed'] += last['sg'][1 - us]
print(f'to r{R}, per game, us / them: ' + ', '.join(args))
print(f'{"map":22} games wins | collected     | tributed      | lost on death | deaths')
for key in sorted(A, key=lambda k: (k == 'total', k)):
    a = A[key]; n = max(1, a['games'])
    print(f'{key:22} {a["games"]:5} {a["wins"]:4} | ' + ' | '.join(
        f'{a["us", k] / n:6.0f} {a["them", k] / n:6.0f}' if k != 'deaths' else f'{a["us", k] / n:5.1f} {a["them", k] / n:5.1f}'
        for k in ('collected', 'tributed', 'lost', 'deaths')))
