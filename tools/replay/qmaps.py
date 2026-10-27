# Download our recent ranked games on maps matching any of MAPS into data/replays/platform/NAME and write index.txt
# (mid map side result) for tools/replay/pextract.py. usage: python -I tools/replay/qmaps.py NAME LIMIT MAP [MAP ...]
import os, re, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
name, limit, maps = sys.argv[1], sys.argv[2], sys.argv[3:]
t = subprocess.run([CAMBC, 'matches', 'list', '--team', OUR, '--kind', 'ranked', '--limit', limit], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
ms = re.findall(r'^(\S{36})\s+finished\s+(\S+)\s*\n\s+(\S{36})\s+(.*?)\s+\[.*?\]\s*\n\s+(\S{36})\s+(.*?)\s+\[', t, re.M)
out = os.path.join('data', 'replays', 'platform', name); os.makedirs(out, exist_ok=True)
idx = []
for mid, mp, ta, na, tb, nb in ms:
    if not any(m in mp for m in maps): continue
    side = 'a' if ta == OUR else 'b'
    p = os.path.join('data', 'summaries', f'{mid}.json')
    if not os.path.exists(p): subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
    d = json.load(open(p, encoding='utf-8'))
    res = 'win' if d['match']['outcome'] == ('teamA' if side == 'a' else 'teamB') else 'loss'
    r = os.path.join(out, f'{mid}.repl26a')
    if not os.path.exists(r): subprocess.run([CAMBC, 'matches', 'download', mid, '-o', r], capture_output=True)
    idx.append(f'{mid} {mp} {side} {res}')
    print(idx[-1], nb if side == 'a' else na)
open(os.path.join(out, 'index.txt'), 'w').write('\n'.join(idx) + '\n')
