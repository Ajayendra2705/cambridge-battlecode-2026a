"""Earned gold at any rounds in a local multi.py run, paired with a base candidate: python -I tools/local/lgold3.py RUN_DIR BASE_CAND TYPE ROUND [ROUND ...]
Like lgold2.py, which stops at r600 for the team and r300 for a type: prints team gold and the gold of champion type TYPE (e.g. "Vesper Vale") at each ROUND.
"""
import collections, glob, json, math, os, sys


def at(runs, r):
    k = 0
    for x in runs:
        k += x['duration']
        if r < k: return float(x['value'])
    return float(runs[-1]['value']) if runs else 0.0


def load(path, rounds):
    b, o, m, s = os.path.basename(path)[:-5].split('~')
    d = json.load(open(path, encoding='utf-8'))
    team = 'team' + s
    out = collections.Counter()
    for t in d['championTimelines']:
        if t['metric'] != 'earnedGold' or t['owner'].get('team') != team: continue
        for r in rounds:
            out[('team', r)] += at(t['runs'], r)
            out[(t['owner'].get('name'), r)] += at(t['runs'], r)
        out[(t['owner'].get('name'), 'n')] += 1
    return b, (o, m, s), out


def mse(xs):
    if len(xs) < 2: return 0.0, 0.0
    m = sum(xs) / len(xs)
    return m, math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1) / len(xs))


run, base, ty = sys.argv[1:4]
rounds = [int(x) for x in sys.argv[4:]]
games = collections.defaultdict(dict)
for f in glob.glob(os.path.join(run, '*.json')):
    try:
        b, key, out = load(f, rounds)
    except Exception:
        continue
    games[b][key] = out
if base not in games: raise SystemExit(f'no games of {base} in {run}')
for b in sorted(games):
    if b == base: continue
    keys = [k for k in games[b] if k in games[base]]
    tk = [k for k in keys if games[b][k][(ty, 'n')] and games[base][k][(ty, 'n')]]
    print(f'{b} n={len(keys)} ({ty} in {len(tk)}), new - base per game (+- se)')
    for r in rounds:
        m, se = mse([games[b][k][('team', r)] - games[base][k][('team', r)] for k in keys])
        mb = sum(games[base][k][('team', r)] for k in keys) / max(1, len(keys))
        m2, se2 = mse([games[b][k][(ty, r)] - games[base][k][(ty, r)] for k in tk])
        mb2 = sum(games[base][k][(ty, r)] for k in tk) / max(1, len(tk))
        print(f'  r{r}: team {m:+7.1f} +- {se:5.1f} (base {mb:5.0f}) | {ty} {m2:+7.1f} +- {se2:5.1f} (base {mb2:5.0f})')
