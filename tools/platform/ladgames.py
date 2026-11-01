# Ranked games of every team on a ladder file: python -I ladgames.py LADDER.json OUT.json [PAGES]  (from the repo root)
# One record per match (deduplicated): map, created, and per team: name, side, result, draft picks.
import json, os, subprocess, sys, time
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
lad, out = json.load(open(sys.argv[1], encoding='utf-8')), sys.argv[2]
pages = int(sys.argv[3]) if len(sys.argv) > 3 else 1
seen = {}
for i, r in enumerate(lad):
    cur = None
    for p in range(pages):
        a = [C, 'matches', 'list', '--team', r['teamId'], '--kind', 'ranked', '--limit', '100', '--json'] + (['--cursor', cur] if cur else [])
        for attempt in range(5):
            t = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if t.returncode == 0: break
            time.sleep(5 * (attempt + 1))
        try: d = json.loads(t.stdout[t.stdout.find('{'):])
        except Exception: break
        for m in d.get('matches', []):
            if m.get('status') != 'finished' or m['matchId'] in seen: continue
            seen[m['matchId']] = {'map': m['map'], 'created': m['createdAt'],
                                  'teams': [{'name': x['name'], 'side': x['side'], 'result': x['result'],
                                             'picks': x.get('draftPicks', []), 'engine': x.get('engineVersion')} for x in m['teams']]}
        cur = d.get('nextCursor')
        if not cur: break
    print(i + 1, len(seen), flush=True)
json.dump(seen, open(out, 'w', encoding='utf-8'))
