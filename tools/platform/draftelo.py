# Ladder games: which picks beat their Elo expectation, per team size.
#   python -I draftelo.py LADGAMES.json LADDER.json [SINCE_ISO]   (from the repo root)
# Per game side with both teams on the ladder file: residual = result (1 win, 0.5 draw, 0 loss) - Elo expectation from
# the current ratings (400 scale). Per size and champion: games where exactly one side drafted it, mean residual of
# that side (se over games). Then the most common full drafts with their mean residual.
import collections, json, math, sys
N = 'Ryth Vesp Vend C+I Stel Pris Marc Will Ren Varg Tavi Hrt'.split()
games, lad = json.load(open(sys.argv[1], encoding='utf-8')), json.load(open(sys.argv[2], encoding='utf-8'))
since = sys.argv[3] if len(sys.argv) > 3 else '2026-10-30'
rat = {r['name']: r['rating'] for r in lad}
by = collections.defaultdict(list)  # (size, champ) -> residuals
comp = collections.defaultdict(list)
tot = collections.Counter()
for g in games.values():
    if g['created'] < since or len(g['teams']) != 2: continue
    a, b = g['teams']
    if a['name'] not in rat or b['name'] not in rat or not a['picks'] or len(a['picks']) != len(b['picks']): continue
    k = len(a['picks']); tot[k] += 1
    for x, y in ((a, b), (b, a)):
        e = 1 / (1 + 10 ** ((rat[y['name']] - rat[x['name']]) / 400))
        res = {'win': 1, 'loss': 0}.get(x['result'], 0.5) - e
        comp[(k, ' '.join(N[i] for i in sorted(x['picks'])))].append(res)
        for c in set(x['picks']) - set(y['picks']):
            by[(k, c)].append(res)
def ms(v):
    m = sum(v) / len(v)
    return m, (math.sqrt(sum((t - m) ** 2 for t in v) / (len(v) - 1) / len(v)) if len(v) > 1 else 0)
print('games per size', dict(tot))
for k in (3, 4, 5):
    print(f'-- {k} a side: champion drafted by one side only: games, mean residual of that side')
    rows = sorted(((ms(v), c, len(v)) for (kk, c), v in by.items() if kk == k and len(v) >= 20), reverse=True)
    for (m, se), c, n in rows: print(f'   {N[c]:5} {n:5} {m:+.3f} +- {se:.3f}')
    print(f'   drafts (20+ sides):')
    rows = sorted(((ms(v), d, len(v)) for (kk, d), v in comp.items() if kk == k and len(v) >= 20), reverse=True)
    for (m, se), d, n in rows: print(f'   {d:28} {n:5} {m:+.3f} +- {se:.3f}')
