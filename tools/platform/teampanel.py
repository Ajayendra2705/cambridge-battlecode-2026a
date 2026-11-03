"""Read a teammate's panel with no quota: python -I tools/platform/teampanel.py SINCE_ISO [--top] [--min-groups N] [--base HH:MM]

Lists our unranked groups since SINCE_ISO, cuts them into bursts (a gap of over 150 s between groups, or our own gates in results/gate.log, which are left out),
names each burst by the version that was active when it started (from `cambc submissions list --json` activation data is not available, so the version is the newest one
uploaded and compiled about 3 minutes before the burst unless `data/active_times.txt` says otherwise), and prints wins and flips of each burst paired by (rival, map, side)
with the games of earlier bursts. A burst of fewer than --min-groups groups (default 3) counts as other teams' challenges and is skipped. Reads only.
"""
import collections, datetime as dt, json, os, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
args = sys.argv[1:]
mingroups = 3
if '--min-groups' in args:
    k = args.index('--min-groups')
    mingroups = int(args[k + 1])
    del args[k:k + 2]
since = args[0]


def get(a):
    for attempt in range(5):
        out = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
        try:
            return json.loads(out[out.index('{'):])
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise SystemExit('platform read failed')


ms, cur = [], None
while True:
    d = get([C, 'matches', 'list', '--team', OUR, '--kind', 'unranked', '--limit', '100', '--json'] + (['--cursor', cur] if cur else []))
    ms += d['matches']
    cur = d.get('nextCursor')
    if not cur or ms[-1]['createdAt'] < since:
        break
ms = [m for m in ms if m['createdAt'] >= since]
mine = {}
for line in open(os.path.join(ROOT, 'results', 'gate.log'), encoding='utf-8'):
    p = line.split()
    if p and '@' in p[0]:
        for g in p[1:]:
            mine[g] = p[0]
subs = get([C, 'submissions', 'list', '--json'])['submissions']
ups = sorted((s['createdAt'], s['version']) for s in subs if s.get('createdAt'))


def stamp(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


G = collections.OrderedDict()
for m in sorted(ms, key=lambda x: x['createdAt']):
    if m['groupId'] in mine:
        continue
    G.setdefault(m['groupId'], []).append(m)
bursts, last = [], None
for gid, gs in G.items():
    t = stamp(min(x['createdAt'] for x in gs))
    if last is None or (t - last).total_seconds() > 150:
        bursts.append([])
    bursts[-1].append(gs)
    last = t
seen = {}
for b in bursts:
    if len(b) < mingroups:
        continue
    t0 = min(x['createdAt'] for gs in b for x in gs)
    ver = next((v for u, v in reversed(ups) if stamp(u) < stamp(t0) - dt.timedelta(minutes=3)), None)
    res, rivals, maps = {}, collections.Counter(), collections.Counter()
    for gs in b:
        for x in gs:
            me = next(y for y in x['teams'] if y['teamId'] == OUR)
            ot = next(y for y in x['teams'] if y['teamId'] != OUR)
            rivals[ot['name']] += 1
            maps[x['map']] += 1
            if me.get('result') in ('win', 'loss'):
                res[(ot['name'], x['map'], me.get('side'))] = me['result'] == 'win'
    wins = sum(res.values())
    print(f"{t0[11:19]} newest v{ver}: {len(b)} groups, {len(res)} finished, {wins} wins, {len(rivals)} rivals, {len(maps)} maps")
    for name, prev in seen.items():
        keys = [k for k in res if k in prev]
        if len(keys) >= 5:
            print(f"    paired with {name}: {len(keys)} games, {sum(res[k] for k in keys)} against {sum(prev[k] for k in keys)}, flips up {sum(res[k] and not prev[k] for k in keys)}, down {sum(prev[k] and not res[k] for k in keys)}")
    seen[t0[11:16]] = res
