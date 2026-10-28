# First fight of each game (the first enemy champion hit, either side), outcome by deaths in the next 30 rounds
# (lost / even / won for us), split by how many of ours and theirs stand within 8 of the victim at that round, and by
# the round. Also the game result per first-fight outcome.
# usage: python -I tools/replay/fs_ffcomp.py [--size N] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
SIZE = None; args = sys.argv[1:]
if args and args[0] == '--size': SIZE = int(args[1]); args = args[2:]
C = collections.Counter(); ng = 0
def p(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1
    k0 = s = v = None
    for k, a in enumerate(rows):
        for i in range(n):
            h = D.enemy_hits(a, i, n)
            if h: k0, s, v = k, i, h[0][-1]; break
        if k0 is not None: break
    if k0 is None: continue
    du = dt = 0
    for t in range(k0, min(len(rows) - 1, k0 + 30)):
        for i, c in enumerate(rows[t + 1]['c']):
            if rows[t]['c'][i]['a'] and not c['a']:
                if D.who(c['t'], us) == 'us': du += 1
                else: dt += 1
    out = 'lost' if du > dt else 'won' if du < dt else 'even'
    a = rows[k0]; q = p(a['c'][v])
    nu = sum(1 for c in a['c'] if p(c) and D.who(c['t'], us) == 'us' and D.dist(q, p(c)) <= 8)
    nt = sum(1 for c in a['c'] if p(c) and D.who(c['t'], us) == 'them' and D.dist(q, p(c)) <= 8)
    diff = nu - nt
    db = 'ours more' if diff > 0 else 'level' if diff == 0 else 'theirs more'
    ub = f'ours within 8: {min(nu, 5)}'
    rb = 'r<=40' if a['r'] <= 40 else 'r41-80' if a['r'] <= 80 else 'r81+'
    win = res == 'win'
    for key in ('all', db, ub, rb):
        C[(key, out)] += 1; C[(key, out, 'w')] += win; C[(key, 'n')] += 1
print(f'{ng} games: first fight outcome (deaths in 30 rounds) by numbers within 8 of the victim; [game wins]')
for key in ['all', 'ours more', 'level', 'theirs more'] + [f'ours within 8: {k}' for k in range(1, 6)] + ['r<=40', 'r41-80', 'r81+']:
    nn = C[(key, 'n')]
    if not nn: continue
    print(f'  {key:18} n {nn:3}: ' + '  '.join(f'{o} {C[(key, o)] / nn:.2f} [{C[(key, o, "w")]}/{C[(key, o)]}]' for o in ('lost', 'even', 'won')))
