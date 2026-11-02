"""Which drafts win on which map on the ladder: python -I tools/platform/mapdrafts.py LADGAMES.json LADDER.json [SINCE_ISO] [--top N] [--size K] [--min N] [--map NAME]

Input from ladgames.py and `cambc ladder --json` (data/ladgames*.json, data/ladder*.json). For each game side with both teams on the ladder file, the residual is
the result (1 win, 0.5 draw, 0 loss) minus the Elo expectation from the current ratings (400 scale). A draft is the set of picks. --top N keeps sides of the
top N teams only (their opponents may be anyone on the file).

Prints, per team size: each draft with its games, wins, mean residual per 100 games (+- se) and the teams that use it most; then per map the commonest drafts with the same
numbers (--min games, default 8). Current ratings are used for games of the last days, so a team that climbed fast shows a small negative bias, and a team's draft
carries the rest of its bot: a residual compares teams at their own strength, it does not say what the draft would do in another bot.
"""
import collections, json, math, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
N = 'Ryth Vesp Vend C+I Stel Pris Marc Will Ren Varg Tavi Hrt'.split()
args = sys.argv[1:]


def opt(name, default=None, cast=str):
    if name in args:
        j = args.index(name)
        v = cast(args[j + 1])
        del args[j:j + 2]
        return v
    return default


top = opt('--top', 0, int)
size = opt('--size', 0, int)
minn = opt('--min', 8, int)
only = opt('--map')
games, lad = json.load(open(args[0], encoding='utf-8')), json.load(open(args[1], encoding='utf-8'))
since = args[2] if len(args) > 2 else '2026-11-01'
rat = {r['name']: r['rating'] for r in lad}
rank = {r['name']: r.get('rank', 999) for r in lad}
D = collections.defaultdict(list)
M = collections.defaultdict(lambda: collections.defaultdict(list))
T = collections.defaultdict(collections.Counter)
for g in games.values():
    if g['created'] < since or len(g['teams']) != 2:
        continue
    a, b = g['teams']
    if a['name'] not in rat or b['name'] not in rat or not a['picks'] or len(a['picks']) != len(b['picks']):
        continue
    k = len(a['picks'])
    if size and k != size:
        continue
    for x, y in ((a, b), (b, a)):
        if top and rank[x['name']] > top:
            continue
        e = 1 / (1 + 10 ** ((rat[y['name']] - rat[x['name']]) / 400))
        r = 1.0 if x['result'] == 'win' else 0.5 if x['result'] == 'draw' else 0.0
        d = ' '.join(sorted(N[p] for p in x['picks']))
        D[(k, d)].append((r, r - e))
        M[g['map']][(k, d)].append((r, r - e))
        T[(k, d)][x['name']] += 1


def stat(v):
    n = len(v)
    w = sum(1 for r, _ in v if r == 1.0)
    m = sum(x for _, x in v) / n
    s = math.sqrt(sum((x - m) ** 2 for _, x in v) / max(1, n - 1) / n)
    return n, w, 100 * m, 100 * s


if not only:
    for k in sorted({k for k, _ in D}):
        print(f'--- {k} picks')
        for (kk, d), v in sorted(D.items(), key=lambda it: -len(it[1])):
            if kk != k or len(v) < minn:
                continue
            n, w, m, s = stat(v)
            teams = ', '.join(f'{t} {c}' for t, c in T[(kk, d)].most_common(3))
            print(f'{d:30} n {n:4} w {w:4} {100 * w / n:3.0f}% residual {m:+5.1f} +- {s:4.1f} | {teams}')
for mp in sorted(M):
    if only and mp != only:
        continue
    rows = sorted(M[mp].items(), key=lambda it: -len(it[1]))
    rows = [(kd, stat(v)) for kd, v in rows if len(v) >= minn]
    if not rows:
        continue
    print(mp + ': ' + '; '.join(f'{kd[1]} {st[1]}/{st[0]} {st[2]:+.0f}' for kd, st in rows[:6]))
