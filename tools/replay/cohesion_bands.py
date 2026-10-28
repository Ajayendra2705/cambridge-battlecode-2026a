# Opening cohesion: mean teammates within 6 per alive champion off spawn, by round band, us vs them; plus the first
# fight's round for games whose first fight we lost (deaths in 30 rounds ours > theirs), won, or drew.
# usage: python -I tools/replay/cohesion_bands.py [--size N] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
SIZE = None; args = sys.argv[1:]
if args and args[0] == '--size': SIZE = int(args[1]); args = args[2:]
BANDS = [(1, 20), (21, 40), (41, 60), (61, 80), (81, 100), (101, 150), (151, 200), (201, 300)]
C = collections.Counter(); FF = collections.defaultdict(list); ng = 0
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1
    spawn = set((c['x'], c['y']) for c in rows[0]['c'] if 'x' in c)
    for a in rows:
        if a['r'] > 300: break
        b = next((j for j, (lo, hi) in enumerate(BANDS) if lo <= a['r'] <= hi), None)
        if b is None: continue
        for i, c in enumerate(a['c']):
            if not c['a'] or 'x' not in c or (c['x'], c['y']) in spawn: continue
            q = (c['x'], c['y']); w = D.who(c['t'], us)
            m = sum(1 for j, o in enumerate(a['c']) if j != i and o['t'] == c['t'] and o['a'] and 'x' in o and D.dist(q, (o['x'], o['y'])) <= 6)
            C[(w, b)] += m; C[(w, b, 'n')] += 1
    k0 = next((k for k, a in enumerate(rows) for i in range(n) if D.enemy_hits(a, i, n)), None)
    if k0 is None: continue
    du = dt = 0
    for t in range(k0, min(len(rows) - 1, k0 + 30)):
        for i, c in enumerate(rows[t + 1]['c']):
            if rows[t]['c'][i]['a'] and not c['a']:
                if D.who(c['t'], us) == 'us': du += 1
                else: dt += 1
    FF['lost' if du > dt else 'won' if du < dt else 'even'].append(rows[k0]['r'])
print(f'{ng} games: teammates within 6 per alive champion off spawn, by round band (us / them)')
print('  ' + '  '.join(f'r{lo}-{hi} {C[("us", j)] / max(1, C[("us", j, "n")]):.2f}/{C[("them", j)] / max(1, C[("them", j, "n")]):.2f}' for j, (lo, hi) in enumerate(BANDS)))
for k in ('lost', 'even', 'won'):
    L = sorted(FF[k])
    if not L: continue
    print(f'  first fight {k:4}: {len(L)} games, round median {L[len(L) // 2]}, in r1-40 {sum(1 for r in L if r <= 40)}, r41-100 {sum(1 for r in L if 40 < r <= 100)}, r101-200 {sum(1 for r in L if 100 < r <= 200)}, later {sum(1 for r in L if r > 200)}')
