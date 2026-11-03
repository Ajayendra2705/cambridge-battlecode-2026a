"""Where gold comes from, us against them: python -I tools/replay/goldsrc.py RMAX DIR [DIR ...]

Per team-game to round RMAX, from rises of a champion's gold held (unspent plus 30 per shard): gold in rises on a round with a kill credited to that champion, on a round its bag fell (tribute: Marcella's +2 a gem,
others nothing), and all other rises (camp rewards), with the number of those reward rises and the gold per rise. A second table splits the rewards by type. Purchases keep the value about the same at 30 a shard, and a
falling value is ignored, so the sums are close to the gold earned. Shows whether a richer rival gets its gold from kills, from more rewards, or from bigger shares of each reward.
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

R, dirs = int(sys.argv[1]), sys.argv[2:]
T = collections.defaultdict(collections.Counter)
Y = collections.defaultdict(collections.Counter)
games = 0
for us, res, mp, meta, rows in D.games(dirs):
    games += 1
    n = len(rows[0]['c'])
    prev = None
    held = [0] * n
    for i in range(n):
        Y[(D.NAMES[rows[0]['c'][i]['ty']], D.who(rows[0]['c'][i]['t'], us))]['games'] += 1
    for x in rows:
        if x['r'] > R:
            break
        for i in range(n):
            c = x['c'][i]
            g = D.gold_held(meta, c)
            if prev is not None:
                p = prev['c'][i]
                d = g - held[i]
                if d > 0:
                    w = D.who(c['t'], us)
                    ty = D.NAMES[c['ty']]
                    if c.get('k', 0) > p.get('k', 0):
                        src = 'kill'
                    elif c.get('g', 0) < p.get('g', 0) and p['a'] and c['a']:
                        src = 'tribute'
                    else:
                        src = 'reward'
                    T[w][src] += d
                    T[w][src + '_n'] += 1
                    Y[(ty, w)][src] += d
                    Y[(ty, w)][src + '_n'] += 1
            held[i] = g
        prev = x
k = max(1, games)
print(f'{games} games to r{R}; team gold a game, us / them')
for s in ('reward', 'kill', 'tribute'):
    u, t = T['us'], T['them']
    print(f"  {s:8s} {u[s] / k:6.0f} / {t[s] / k:6.0f}   rises {u[s + '_n'] / k:5.1f} / {t[s + '_n'] / k:5.1f}   gold a rise {u[s] / max(1, u[s + '_n']):5.1f} / {t[s] / max(1, t[s + '_n']):5.1f}")
print('type      side games | reward rises a-rise | kill | tribute (per team-game of that type)')
for ty in D.NAMES:
    for w in ('us', 'them'):
        c = Y.get((ty, w))
        if not c or c['games'] < 3:
            continue
        g = c['games']
        print(f"{ty:9s} {w:4s} {g:4d} | {c['reward'] / g:6.0f} {c['reward_n'] / g:5.1f} {c['reward'] / max(1, c['reward_n']):5.1f} | {c['kill'] / g:5.0f} | {c['tribute'] / g:5.0f}")
