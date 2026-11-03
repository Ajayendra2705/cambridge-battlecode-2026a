"""Our ranked games by map family, team size and draft: python -I tools/platform/rkmaps.py OURMAPS.json [--since ISO]

OURMAPS.json comes from tools/platform/ourmaps.py. Prints win rates by map prefix (00, 01, 02, 03, adgato), by team size (picks of our draft), and all maps at 40% or worse with
at least 5 games, the worst first, so a neighbour-level panel can be chosen. Ranked sets are played against teams within about 15 ranks of us, so these maps are the ones that
hold the rating back, whatever the panels against the top 20 say.
"""
import collections, json, sys
args = sys.argv[1:]
since = None
if '--since' in args:
    k = args.index('--since')
    since = args[k + 1]
    del args[k:k + 2]
d = json.load(open(args[0], encoding='utf-8'))
if since:
    d = [g for g in d if g['created'] >= since]
P = collections.defaultdict(lambda: [0, 0])
S = collections.defaultdict(lambda: [0, 0])
M = collections.defaultdict(lambda: [0, 0])
for g in d:
    w = g['result'] == 'win'
    m = g['map']
    pre = 'adgato' if m.startswith('adgato') else m[:2]
    n = len(g['ours'])
    for T, key in ((P, pre), (S, n), (M, m)):
        T[key][0] += w
        T[key][1] += 1
print(len(d), 'games', sum(g['result'] == 'win' for g in d), 'wins', d[-1]['created'][:16], 'to', d[0]['created'][:16])
print('by family:', ' '.join(f'{k} {v[0]}/{v[1]} {v[0] / v[1]:.2f}' for k, v in sorted(P.items())))
print('by size:', ' '.join(f'{k} {v[0]}/{v[1]} {v[0] / v[1]:.2f}' for k, v in sorted(S.items())))
rows = [(v[0] / v[1], m, v) for m, v in M.items() if v[1] >= 5 and v[0] / v[1] <= 0.4]
print('maps at 40% or worse:', ' '.join(f'{m} {v[0]}/{v[1]}' for r, m, v in sorted(rows)))
