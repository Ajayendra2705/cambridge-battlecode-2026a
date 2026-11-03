"""Second sample of per-map opening arms: python -I tools/local/armtable2.py BASE_LOG BASE_CAND ARM:CAND:LOG [ARM:CAND:LOG ...] [--first data/armtable_r300.json --names L=vlc1,L3=vlc3,...]

BASE_LOG and each LOG are multi.py logs (they hold the `dir` line). For each arm and map: games, the base's team gold at r300, the paired gain at r300, wins base / arm, margin difference, and the gain in the
first table. The last column applies the table rule of results/analysis/rule_arms.md: gain at least +100 and at least 8% of the base, wins not below the base's. A final list gives the best passing arm of each map
by the mean of the two samples, as a JSON spec for mk_rt.py.
"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lgold2 import at
args = sys.argv[1:]
first, names = {}, {}
if '--first' in args:
    k = args.index('--first'); first = json.load(open(args[k + 1], encoding='utf-8')); del args[k:k + 2]
if '--names' in args:
    k = args.index('--names'); names = dict(x.split('=') for x in args[k + 1].split(',')); del args[k:k + 2]
base_log, base = args[0], args[1]


def run_dir(log):
    for line in open(log, encoding='utf-8', errors='replace'):
        if line.startswith('dir '):
            return line[4:].strip()
    sys.exit('no dir line in ' + log)


def load(path, R=300):
    b, o, m, s = os.path.basename(path)[:-5].split('~')
    j = json.load(open(path, encoding='utf-8'))
    team = 'team' + s
    gold = sum(at(t['runs'], R) for t in j['championTimelines'] if t['metric'] == 'earnedGold' and t['owner'].get('team') == team)
    us = 'team' + s
    win = float(j['match']['outcome'] == us)
    sub = {t['team']: int(t['submittedGems']) for t in j['teams']}
    return b, (o, m, s), (gold, win, sum(v if k == us else -v for k, v in sub.items()))


B = {}
for f in glob.glob(os.path.join(run_dir(base_log), base + '~*.json')):
    try:
        b, k, v = load(f)
        B[k] = v
    except Exception:
        pass
best = {}
for spec in args[2:]:
    arm, cand, log = spec.split(':')
    M = collections.defaultdict(list)
    for f in glob.glob(os.path.join(run_dir(log), cand + '~*.json')):
        try:
            b, k, v = load(f)
        except Exception:
            continue
        if k in B:
            M[k[1]].append((B[k], v))
    print(f'== {arm} ({cand})')
    for mp, xs in sorted(M.items(), key=lambda z: -sum(x[1][0] - x[0][0] for x in z[1]) / len(z[1])):
        n = len(xs)
        bg = sum(x[0][0] for x in xs) / n
        g = sum(x[1][0] - x[0][0] for x in xs) / n
        wb, wa = sum(x[0][1] for x in xs), sum(x[1][1] for x in xs)
        mg = sum(x[1][2] - x[0][2] for x in xs) / n
        g1 = first.get(mp, {}).get(names.get(arm, ''), None)
        ok = g >= 100 and g >= 0.08 * bg and wa >= wb
        print(f'{mp:24} n{n:2} base {bg:6.0f} gain {g:+7.1f} wins {wb:.0f}/{wa:.0f} margin {mg:+7.1f} first {"-" if g1 is None else round(g1):>6} {"PASS" if ok else ""}')
        if ok:
            mean = (g + g1) / 2 if g1 is not None else g
            if mp not in best or mean > best[mp][0]:
                best[mp] = (mean, arm)
print(json.dumps({m.replace('-', '_'): v[1] for m, v in sorted(best.items())}))
