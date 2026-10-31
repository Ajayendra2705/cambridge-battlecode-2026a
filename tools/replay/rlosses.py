# Recent ranked games, classified: per game map, size, result, our/their collected, tributed, deaths. usage: rlosses.py LIMIT
import json, os, re, subprocess, sys, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'C:\Users\ajiit\Desktop\Future\Projects\Cambridge Battlecode'
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
t = subprocess.run([CAMBC, 'matches', 'list', '--team', OUR, '--kind', 'ranked', '--limit', sys.argv[1]], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
ms = re.findall(r'^(\S{36})\s+finished\s+(\S+)\s*\n\s+(\S{36})\s+(.*?)\s+\[.*?\]\s*\n\s+(\S{36})\s+(.*?)\s+\[', t, re.M)
K = collections.Counter(); rows = []
for mid, mp, ta, na, tb, nb in ms:
    p = os.path.join(ROOT, 'data', 'summaries', f'{mid}.json')
    if not os.path.exists(p): subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
    if not os.path.exists(p): continue
    d = json.load(open(p, encoding='utf-8'))
    s = 'teamA' if ta == OUR else 'teamB'; o = 'teamB' if s == 'teamA' else 'teamA'
    won = d['match']['outcome'] == s
    f = lambda tm, k: sum(int(float(c['metrics'][k])) for c in d['champions'] if c['team'] == tm)
    n = sum(1 for c in d['champions'] if c['team'] == s)
    us = {k: f(s, k) for k in ('collectedGems', 'submittedGems', 'deaths')}; th = {k: f(o, k) for k in ('collectedGems', 'submittedGems', 'deaths')}
    cls = 'win' if won else ('massacre' if us['deaths'] - th['deaths'] >= 6 else ('bank' if us['collectedGems'] >= 0.9 * th['collectedGems'] else 'econ'))
    K[cls] += 1
    rows.append((cls, mp, n, us, th, nb if s == 'teamA' else na, d['match']['roundsCompleted']))
for r in rows:
    if r[0] != 'win': print(f"{r[0]:8} {r[1]:22} n{r[2]} coll {r[3]['collectedGems']:5}/{r[4]['collectedGems']:5} trib {r[3]['submittedGems']:5}/{r[4]['submittedGems']:5} deaths {r[3]['deaths']:2}/{r[4]['deaths']:2} r{r[6]:5} vs {r[5]}")
print(dict(K), 'of', len(rows))
