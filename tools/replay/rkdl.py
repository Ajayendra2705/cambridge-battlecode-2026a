"""Download our ranked games of chosen maps listed by tools/platform/ourmaps.py: python -I tools/replay/rkdl.py NAME OURMAPS.json MAX_PER_MAP MAP [MAP ...]

Newest games first, at most MAX_PER_MAP a map, into data/replays/platform/NAME/ with an index.txt (mid map side result), for tools/replay/pextract.py. Summaries go to
data/summaries/ as usual. Ranked sets are played against teams near our rank, so this shows what holds the rating back on a map.
"""
import collections, json, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
name, src, mx, maps = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:]
games = json.load(open(src, encoding='utf-8'))
out = os.path.join('data', 'replays', 'platform', name)
os.makedirs(out, exist_ok=True)
seen = collections.Counter()
idx = []
for g in games:
    mp = g['map']
    if mp not in maps or seen[mp] >= mx:
        continue
    seen[mp] += 1
    mid = g['mid']
    p = os.path.join('data', 'summaries', f'{mid}.json')
    if not os.path.exists(p):
        subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
    r = os.path.join(out, f'{mid}.repl26a')
    if not os.path.exists(r):
        subprocess.run([CAMBC, 'matches', 'download', mid, '-o', r], capture_output=True)
    res = 'win' if g['result'] == 'win' else 'loss'
    idx.append(f"{mid} {mp} {g['side']} {res}")
open(os.path.join(out, 'index.txt'), 'w').write('\n'.join(idx) + '\n')
print(len(idx), 'games', dict(seen))
