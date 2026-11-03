"""Our newest unranked match groups: python -I tools/platform/recentgroups.py [N] [--out FILE]

Lists the newest N groups (default 24), oldest first: time, status counts, our version, opponent and maps. Shows whether a teammate's test is running before we queue our own, and which panel it plays. A match group plays the
team's active version, so two tests at once play each other's bot. With --out, writes the raw matches of those groups to FILE for later use.
"""
import collections, json, os, subprocess, sys

C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
args = sys.argv[1:]
out = None
if '--out' in args:
    k = args.index('--out')
    out = args[k + 1]
    del args[k:k + 2]
n = int(args[0]) if args else 24
ms, cur = [], None
while len(ms) < n * 5 + 10:
    a = [C, 'matches', 'list', '--team', OUR, '--kind', 'unranked', '--limit', '100', '--json'] + (['--cursor', cur] if cur else [])
    d = json.loads(subprocess.run(a, capture_output=True, text=True, encoding='utf-8').stdout)
    ms += d['matches']
    cur = d.get('nextCursor')
    if not cur:
        break
if out:
    json.dump(ms, open(out, 'w', encoding='utf-8'))
G = collections.OrderedDict()
for m in ms:
    G.setdefault(m.get('matchGroupId') or m.get('groupId') or m.get('group') or m.get('id'), []).append(m)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if ms:
    print('fields', sorted(ms[0].keys()))
rows = list(G.items())[:n]
for gid, gs in reversed(rows):
    st = collections.Counter(m.get('status') for m in gs)
    t = min(m.get('createdAt') or m.get('created') or '' for m in gs)
    print(str(t)[:16], str(gid)[:8], dict(st), len(gs))
