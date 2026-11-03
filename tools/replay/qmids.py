"""Download and decode our ranked games on chosen maps from an ourmaps.py file: python -I tools/replay/qmids.py OURMAPS.json NAME JOBS PREFIX [PREFIX ...]

OURMAPS.json comes from tools/platform/ourmaps.py (it holds match ids, so it reaches further back than qmaps.py's LIMIT newest games). Every game whose map starts
with a PREFIX goes to data/replays/platform/NAME/ with an index.txt (mid map side result opponent), then is decoded into data/fights/NAME/ for decoded.py and the
other readers. A rerun fetches only what is missing.
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
src, name, jobs, prefixes = sys.argv[1], sys.argv[2], int(sys.argv[3]), tuple(sys.argv[4:])
games = [g for g in json.load(open(src, encoding='utf-8')) if g['map'].startswith(prefixes)]
out = os.path.join('data', 'replays', 'platform', name)
fights = os.path.join('data', 'fights', name)
os.makedirs(out, exist_ok=True)
os.makedirs(fights, exist_ok=True)


def fetch(g):
    r = os.path.join(out, g['mid'] + '.repl26a')
    for _ in range(5):
        if os.path.exists(r) and os.path.getsize(r) > 0:
            return r
        subprocess.run([CAMBC, 'matches', 'download', g['mid'], '-o', r], capture_output=True)
    return None


with ThreadPoolExecutor(3) as ex:
    files = [f for f in ex.map(fetch, games) if f]
for p in (out, fights):
    with open(os.path.join(p, 'index.txt'), 'w', encoding='utf-8') as f:
        for g in games:
            f.write(f"{g['mid']} {g['map']} {g['side']} {g['result']} {g['opp']}\n")
print(len(games), 'games,', len(files), 'replays')
subprocess.run([sys.executable, '-I', 'tools/replay/pextract.py', fights, str(jobs)] + files, stdout=subprocess.DEVNULL)
print('decoded', sum(x.endswith('.jsonl.gz') for x in os.listdir(fights)))
