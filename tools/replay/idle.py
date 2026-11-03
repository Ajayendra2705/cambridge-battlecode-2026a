"""Wasted turns: python -I tools/replay/idle.py DIR [DIR ...] [--upto R]

Per side and champion type, the share of alive champion-rounds to round R (default 1000) spent hitting (attack or spell), moving,
starting a channel, or doing nothing, split by whether an enemy champion is within 6 tiles. Rounds in a channel and on a camp tile
show as doing nothing, so read the two sides against each other: a gap to the rivals names a bug to read for.
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

args = sys.argv[1:]
upto = 1000
if '--upto' in args:
    k = args.index('--upto')
    upto = int(args[k + 1])
    del args[k:k + 2]
T = collections.defaultdict(collections.Counter)
ALL = collections.defaultdict(collections.Counter)
games = 0
acts = collections.Counter()
for us, res, mp, meta, rows in D.games(args):
    games += 1
    for x in rows:
        if x['r'] > upto:
            break
        for i, c in enumerate(x['c']):
            if not c.get('a') or 'x' not in c:
                continue
            side = 'us' if c['t'] == us else 'them'
            ty = D.NAMES[c['ty']]
            names = [a[0] for a in x['act'][i]] if i < len(x['act']) else []
            acts.update(names)
            if any(n in ('attack', 'cast') for n in names):
                kind = 'hit'
            elif 'move' in names:
                kind = 'move'
            elif names:
                kind = 'other'
            else:
                ne = 99
                for o in x['c']:
                    if o['t'] != c['t'] and o.get('a') and 'x' in o:
                        ne = min(ne, D.dist((o['x'], o['y']), (c['x'], c['y'])))
                kind = 'still_enemy' if ne <= 6 else 'still'
            for d in (T[(side, ty)], ALL[side]):
                d['n'] += 1
                d[kind] += 1
print('games', games, 'actions seen', dict(acts.most_common(12)))
KEYS = ('hit', 'move', 'other', 'still', 'still_enemy')
for side in ('us', 'them'):
    a = ALL[side]
    print(side, ' '.join(k + ' ' + format(a[k] / max(1, a['n']), '.3f') for k in KEYS), 'rounds/game', a['n'] // max(1, games))
for key in sorted(T):
    a = T[key]
    print(' ', key[0], key[1].ljust(9), ' '.join(k + ' ' + format(a[k] / max(1, a['n']), '.3f') for k in KEYS), 'n', a['n'])
