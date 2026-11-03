"""Team gold at a round per map, us against the rival, from ranked game summaries: python -I tools/replay/rkgold.py OURMAPS.json [--round 600] [--since ISO] [--fetch N]

OURMAPS.json comes from tools/platform/ourmaps.py. Reads data/summaries/<match>.json (or .json.gz); --fetch N downloads up to N missing ones, newest first.
Prints per map, worst ratio first: games, wins, median gold of each side at the round, their share of the map's games with us under half their gold, and our deaths.
A map where we earn a small part of the rival's gold in most games is a blind spot of the bot on that map, not a lost fight.
"""
import collections, gzip, json, os, statistics, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
args = sys.argv[1:]


def opt(name, default):
    if name in args:
        k = args.index(name)
        v = args[k + 1]
        del args[k:k + 2]
        return v
    return default


rnd = int(opt('--round', '600'))
since = opt('--since', '')
fetch = int(opt('--fetch', '0'))
ms = [m for m in json.load(open(args[0], encoding='utf-8')) if m['created'] >= since]


def path(mid):
    return os.path.join(ROOT, 'data', 'summaries', mid + '.json')


def load(mid):
    p = path(mid)
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    if os.path.exists(p + '.gz'):
        return json.load(gzip.open(p + '.gz', 'rt', encoding='utf-8'))
    return None


def at(runs, r):
    k = 0
    for x in runs:
        k += x['duration']
        if r < k:
            return float(x['value'])
    return float(runs[-1]['value']) if runs else 0.0


T = collections.defaultdict(list)
miss = 0
for m in sorted(ms, key=lambda x: x['created'], reverse=True):
    d = load(m['mid'])
    if d is None and fetch > 0:
        fetch -= 1
        subprocess.run([CAMBC, 'matches', 'summary', m['mid'], '--json', '-o', path(m['mid'])], capture_output=True)
        d = load(m['mid'])
    if d is None:
        miss += 1
        continue
    us = 'team' + m['side'].upper()
    g = collections.Counter()
    dth = 0
    for t in d['championTimelines']:
        o = t['owner'].get('team')
        if t['metric'] == 'earnedGold':
            g[o] += at(t['runs'], rnd)
        elif t['metric'] == 'deaths' and o == us:
            dth += at(t['runs'], rnd)
    T[m['map']].append((m['result'] == 'win', g[us], sum(v for k, v in g.items() if k != us), dth, m['opp']))
print(f'{len(ms)} games, {miss} without a summary; gold at r{rnd}')
print('map                       games wins  us  them  ratio  under half  deaths')
rows = []
for mp, x in T.items():
    a = statistics.median(v[1] for v in x)
    b = statistics.median(v[2] for v in x)
    rows.append((a / max(1, b), mp, x, a, b))
for r, mp, x, a, b in sorted(rows, key=lambda v: v[0]):
    under = sum(v[1] < 0.5 * v[2] for v in x)
    print(f'{mp:25} {len(x):4} {sum(v[0] for v in x):4} {a:5.0f} {b:5.0f} {r:5.2f} {under:6} {sum(v[3] for v in x) / len(x):8.1f}')
