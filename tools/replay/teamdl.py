# python -I tools/replay/teamdl.py NAME PER_TEAM ENGINE TEAM_ID...
#   -> data/replays/platform/NAME/{mid}.repl26a + index.txt (mid map side result), side and result of the listed team
# Scouting: the newest PER_TEAM ranked matches of each team on engine ENGINE (e.g. 2.0.0). A match between two listed
# teams is kept once, from the first team's side. Decode with rounds_extract.mjs like decode_run.sh does.
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
name, per, engine, teams = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4:]
out = f'data/replays/platform/{name}'; os.makedirs(out, exist_ok=True)
rows, seen = [], set()
for team in teams:
    t = subprocess.run([C, 'matches', 'list', '--team', team, '--kind', 'ranked', '--limit', str(4 * per), '--json'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
    try: ms = json.loads(t[t.find('{'):])['matches']
    except Exception: print('no listing for', team); continue
    n = 0
    for m in ms:
        if n >= per: break
        if m['status'] != 'finished' or m['matchId'] in seen: continue
        side = next((x for x in m['teams'] if x['teamId'] == team), None)
        if not side or side.get('engineVersion') != engine: continue
        seen.add(m['matchId']); n += 1
        rows.append((m['matchId'], m['map'], side['side'], side['result']))
open(out + '/index.txt', 'w').write('\n'.join(' '.join(r) for r in rows))
def get(r):
    p = f'{out}/{r[0]}.repl26a'
    for a in range(8):  # downloads fail now and then (see gdl.py)
        if os.path.exists(p): return
        subprocess.run([C, 'matches', 'download', r[0], '-o', p], capture_output=True)
        if not os.path.exists(p): time.sleep(10 * (a + 1))
with ThreadPoolExecutor(2) as ex: list(ex.map(get, rows))
print(name, len(rows), 'matches,', len(os.listdir(out)) - 1, 'replays')
