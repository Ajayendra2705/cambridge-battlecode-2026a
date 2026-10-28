# The first fight of each game: the first round any champion hits an enemy champion; champions of each side within 8 of
# the victim then (and the most within 8 over the next 20 rounds); deaths per side in the 30 rounds from it; which side
# struck first; and the game result. Grouped by the first fight's death difference (ours minus theirs).
# usage: python -I tools/replay/fs_firstfight.py [--size N] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
SIZE = None; args = sys.argv[1:]
if args and args[0] == '--size': SIZE = int(args[1]); args = args[2:]
G = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    k0 = None
    for k, a in enumerate(rows):
        for i in range(n):
            h = D.enemy_hits(a, i, n)
            if h: k0, striker, victim = k, i, h[0][-1]; break
        if k0 is not None: break
    if k0 is None: continue
    a = rows[k0]; v = a['c'][victim]; q = (v['x'], v['y'])
    def near(row, side):
        return sum(1 for c in row['c'] if c['a'] and 'x' in c and D.who(c['t'], us) == side and D.dist(q, (c['x'], c['y'])) <= 8)
    nu, nt = near(a, 'us'), near(a, 'them')
    mu = max(near(rows[t], 'us') for t in range(k0, min(len(rows), k0 + 20)))
    mt = max(near(rows[t], 'them') for t in range(k0, min(len(rows), k0 + 20)))
    du = dt = 0
    for t in range(k0, min(len(rows) - 1, k0 + 30)):
        for i, c in enumerate(rows[t + 1]['c']):
            if rows[t]['c'][i]['a'] and not c['a']:
                if D.who(c['t'], us) == 'us': du += 1
                else: dt += 1
    first = D.who(a['c'][striker]['t'], us)
    G[max(-2, min(2, du - dt))].append((a['r'], nu, nt, mu, mt, du, dt, first, res, mp))
print('first fight per game; by its death difference in 30 rounds (ours minus theirs, clipped at +-2)')
for d in sorted(G):
    L = G[d]; m = len(L)
    f = lambda j: sum(x[j] for x in L) / m
    print(f'  diff {d:+d}: {m:3} games, wins {sum(x[8] == "win" for x in L) / m:.2f}; round {f(0):5.0f}; within 8 at the first hit us {f(1):.1f} them {f(2):.1f}, most in 20 rounds {f(3):.1f} vs {f(4):.1f};'
          f' deaths {f(5):.2f} vs {f(6):.2f}; we struck first {sum(x[7] == "us" for x in L) / m:.2f}')
L = [x for d in G for x in G[d]]
print(f'  all: {len(L)} games; first fight lost (diff>0) {sum(1 for x in L if x[5] > x[6]) / len(L):.2f}, won {sum(1 for x in L if x[5] < x[6]) / len(L):.2f}')
