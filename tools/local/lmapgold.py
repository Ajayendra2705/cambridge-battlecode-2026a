"""Per-map paired gold in a local multi.py run: python -I tools/local/lmapgold.py RUN_DIR BASE_CAND NEW_CAND [--round 1000]

Pairs games on (opponent, map, side). Per map, largest gain first: team gold at the round, new minus base with its standard error, both candidates' wins, margin difference with its
standard error, their gold difference. Used to choose maps for a per-map router: on the 8 maps of `nr2` the local gold gain tracks the platform's (results/analysis/rule_route2.md).
"""
import collections, glob, json, math, os, sys

args = sys.argv[1:]
rnd = 1000
if '--round' in args:
    k = args.index('--round')
    rnd = int(args[k + 1])
    del args[k:k + 2]
run, base, new = args


def at(runs, r):
    k = 0
    for x in runs:
        k += x['duration']
        if r < k:
            return float(x['value'])
    return float(runs[-1]['value']) if runs else 0.0


def load(cand):
    out = {}
    for p in glob.glob(os.path.join(run, cand + '~*.json')):
        _, o, m, s = os.path.basename(p)[:-5].split('~')
        d = json.load(open(p, encoding='utf-8'))
        team = 'team' + s
        g = {'us': 0.0, 'them': 0.0}
        for t in d['championTimelines']:
            if t['metric'] == 'earnedGold':
                g['us' if t['owner'].get('team') == team else 'them'] += at(t['runs'], rnd)
        sub = {}
        for t in d['teamTimelines']:
            if t['metric'] == 'submittedGems':
                w = t['owner'] if isinstance(t['owner'], str) else t['owner'].get('team')
                sub[w] = float(t['runs'][-1]['value']) if t['runs'] else 0.0
        other = 'teamB' if s == 'A' else 'teamA'
        out[(o, m, s)] = (g['us'], g['them'], sub.get(team, 0) - sub.get(other, 0))
    return out


def ms(v):
    n = len(v)
    a = sum(v) / n
    return a, math.sqrt(sum((x - a) ** 2 for x in v) / max(1, n - 1) / n)


B, N = load(base), load(new)
M = collections.defaultdict(list)
for k in B:
    if k in N:
        M[k[1]].append((B[k], N[k]))
rows = []
for m, v in M.items():
    a, se = ms([n[0] - b[0] for b, n in v])
    t, tse = ms([n[1] - b[1] for b, n in v])
    mg, mse = ms([n[2] - b[2] for b, n in v])
    rows.append((a, se, m, len(v), sum(b[2] > 0 for b, _ in v), sum(n[2] > 0 for _, n in v), mg, mse, t, tse, sum(b[0] for b, _ in v) / len(v)))
rows.sort(reverse=True)
print(f"{'map':24} n base gold  gain  (se)  wins  margin (se)  their gold (se)")
for a, se, m, n, wb, wn, mg, mse, t, tse, g in rows:
    print(f'{m:24} {n} {g:6.0f} {a:+7.0f} ({se:4.0f}) {wb}>{wn} {mg:+6.0f} ({mse:4.0f}) {t:+6.0f} ({tse:4.0f})')
