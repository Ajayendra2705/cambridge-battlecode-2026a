"""List ladder teams whose latest ranked matches use the current map pool (so they have an eligible bot).
usage: python -I tools/platform/eligible.py LADDER_JSONL RANKS (e.g. 1-40,45-300:5)"""
import json, re, subprocess, sys, os, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
POOL = {m[:-7] for m in os.listdir(os.path.join(os.path.dirname(__file__), '..', '..', 'maps')) if m.endswith('.map26a')}
POOL |= {m.replace('-', '_') for m in POOL}
teams = {}
for l in open(sys.argv[1], encoding='utf-8'):
    if l.strip():
        for t in json.loads(l)['teams']: teams[t['rank']] = t
ranks = []
for part in sys.argv[2].split(','):
    span, _, step = part.partition(':')
    a, _, b = span.partition('-')
    ranks += range(int(a), int(b or a) + 1, int(step or 1))
for r in ranks:
    t = teams.get(r)
    if not t: continue
    for _ in range(6):  # the listing comes back empty under HTTP 429
        out = subprocess.run([CAMBC, 'matches', 'list', '--team', t['teamId'], '--kind', 'ranked', '--limit', '3'],
                             capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
        maps = re.findall(r'^\S{36}\s+\S+\s+(\S+)\s*$', out, re.M)
        if maps: break
        time.sleep(10)
    ok = all(m in POOL for m in maps) and bool(maps)
    print(f"{r:4} {t['rating']:7.1f} {t['teamId']} {'NEW' if ok else 'old'} {','.join(maps)} {t['name']}", flush=True)
