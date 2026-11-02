"""Earned gold by round in a local multi.py run, each candidate paired game by game with a base candidate.

usage: python -I tools/local/lgold2.py RUN_DIR BASE_CAND [TYPE]   (e.g. data/runs/multi-221500 pool.v1503 "Vesper Vale")

Reads every game JSON of the run (`championTimelines`, metric earnedGold: one sample a round, run-length encoded) and
pairs each candidate's game with the base's game on the same (opponent, map, side). Prints per candidate the paired
mean difference (new - base, +- standard error) of our team's earned gold at r150, r300 and r600, and of the gold
of the champion type TYPE (default Vesper Vale) at r150 and r300, over the games where both have that champion.
"""
import collections, glob, json, math, os, sys

ROUNDS = (150, 300, 600)


def at(runs, r):
    k = 0
    for x in runs:
        k += x['duration']
        if r < k: return float(x['value'])
    return float(runs[-1]['value']) if runs else 0.0


def load(path):
    b, o, m, s = os.path.basename(path)[:-5].split('~')
    d = json.load(open(path, encoding='utf-8'))
    team = 'team' + s
    out = collections.Counter()
    for t in d['championTimelines']:
        if t['metric'] != 'earnedGold' or t['owner'].get('team') != team: continue
        for r in ROUNDS:
            out[('team', r)] += at(t['runs'], r)
            out[(t['owner'].get('name'), r)] += at(t['runs'], r)
        out[(t['owner'].get('name'), 'n')] += 1
    return b, (o, m, s), out


def mse(xs):
    if len(xs) < 2: return 0.0, 0.0
    m = sum(xs) / len(xs)
    v = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(v / len(xs))


def main():
    run, base = sys.argv[1], sys.argv[2]
    ty = sys.argv[3] if len(sys.argv) > 3 else 'Vesper Vale'
    games = collections.defaultdict(dict)
    for f in glob.glob(os.path.join(run, '*.json')):
        try:
            b, key, out = load(f)
        except Exception:
            continue
        games[b][key] = out
    if base not in games: raise SystemExit(f'no games of {base} in {run}')
    print(f'{run}: earned gold, new - base per game (+- se), paired on (opponent, map, side) with {base}')
    for b in sorted(games):
        if b == base: continue
        keys = [k for k in games[b] if k in games[base]]
        cols = []
        for r in ROUNDS:
            m, se = mse([games[b][k][('team', r)] - games[base][k][('team', r)] for k in keys])
            mb = sum(games[base][k][('team', r)] for k in keys) / max(1, len(keys))
            cols.append(f'team r{r} {m:+6.1f} +- {se:5.1f} (base {mb:5.0f})')
        tk = [k for k in keys if games[b][k][(ty, 'n')] and games[base][k][(ty, 'n')]]
        for r in ROUNDS[:2]:
            m, se = mse([games[b][k][(ty, r)] - games[base][k][(ty, r)] for k in tk])
            mb = sum(games[base][k][(ty, r)] for k in tk) / max(1, len(tk))
            cols.append(f'{ty} r{r} {m:+6.1f} +- {se:5.1f} (base {mb:4.0f})')
        print(f'  {b:14} n={len(keys):4} ({ty} in {len(tk)}) | ' + ' | '.join(cols))


if __name__ == '__main__':
    main()
