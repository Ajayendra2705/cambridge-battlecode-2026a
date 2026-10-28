"""Our ranked games per map (engine 2.0.0), newest first, 100 a page: python -I tools/platform/ourmaps.py PAGES OUT.json

Writes one record per finished game (match id, map, our side, result, opponent, creation time, both drafts) to OUT.json
and prints wins per map, worst first. Retries a page that fails (HTTP 429).
"""
import json, subprocess, os, sys, collections, time
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
ms, cur = [], None
for page in range(int(sys.argv[1])):
    a = [C, 'matches', 'list', '--team', OUR, '--kind', 'ranked', '--limit', '100', '--json'] + (['--cursor', cur] if cur else [])
    for attempt in range(4):
        r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode == 0: break
        time.sleep(5 * (attempt + 1))
    t = r.stdout
    d = json.loads(t[t.find('{'):])
    ms += d['matches']; cur = d.get('nextCursor')
    if not cur: break
out = []
for m in ms:
    if m['status'] != 'finished': continue
    side = next((x for x in m['teams'] if x['teamId'] == OUR), None)
    if not side or side.get('engineVersion') != '2.0.0': continue
    opp = next((x for x in m['teams'] if x['teamId'] != OUR), {})
    out.append({'mid': m['matchId'], 'map': m['map'], 'side': side['side'], 'result': side['result'], 'opp': opp.get('teamName') or opp.get('name'), 'created': m.get('createdAt'), 'ours': side.get('draftPicks'), 'theirs': opp.get('draftPicks')})
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'))
W = collections.Counter(); N = collections.Counter()
for o in out: N[o['map']] += 1; W[o['map']] += o['result'] == 'win'
print(len(out), 'games', sum(W.values()), 'wins')
for mp in sorted(N, key=lambda m: W[m] / N[m]): print(f'{mp:28} {W[mp]:3}/{N[mp]:3} {W[mp] / N[mp]:.2f}')
