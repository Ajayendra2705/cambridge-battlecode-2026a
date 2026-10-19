"""Summarise our recent ranked matches: python tools/ranked.py [limit]"""
import json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
limit = sys.argv[1] if len(sys.argv) > 1 else '10'
t = subprocess.run([CAMBC, 'matches', 'list', '--team', OUR, '--kind', 'ranked', '--limit', limit], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
ms = re.findall(r'^(\S{36})\s+finished\s+(\S+)\s*\n\s+(\S{36})\s+(.*?)\s+\[.*?\]\s*\n\s+(\S{36})\s+(.*?)\s+\[', t, re.M)
w = 0
for mid, mp, ta, na, tb, nb in ms:
    p = os.path.join(ROOT, 'ladder_replays', f'{mid}.json')
    if not os.path.exists(p):
        subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding='utf-8'))
    side = 'teamA' if ta == OUR else 'teamB'
    other = 'teamB' if side == 'teamA' else 'teamA'
    g = {x['team']: int(x['submittedGems']) for x in d['teams']}
    won = d['match']['outcome'] == side
    w += won
    deaths = {s: sum(int(c['metrics']['deaths']) for c in d['champions'] if c['team'] == s) for s in (side, other)}
    print(f"{mp:12} {'WIN ' if won else 'loss'} {g[side]:5}-{g[other]:5} r{d['match']['roundsCompleted']:5} deaths {deaths[side]:2}/{deaths[other]:2} vs {nb if side == 'teamA' else na}")
print('wins', w, 'of', len(ms))
