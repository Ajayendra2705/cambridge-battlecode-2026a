"""Download recent finished ranked replays of the teams in a ladder rank range (both sides of every match are data).
usage: python -I tools/replay/fetch_ranked.py RANKS [--per-team N] [--out data/replays/ranked]   e.g. RANKS = 40-90
Needs `cambc login`. Writes <out>/<match id>.repl26a and appends one JSON line per match to <out>/index.jsonl."""
import argparse, json, os, re, shutil, subprocess, time
from concurrent.futures import ThreadPoolExecutor

CAMBC = shutil.which('cambc') or os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
ap = argparse.ArgumentParser()
ap.add_argument('ranks')
ap.add_argument('--per-team', type=int, default=25)
ap.add_argument('--out', default='data/replays/ranked')
ap.add_argument('--jobs', type=int, default=2)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

def cli_json(*a):
    for attempt in range(8):
        r = subprocess.run([CAMBC, *a, '--json'], capture_output=True, text=True)
        if r.returncode == 0: return json.loads(r.stdout)
        wait = re.search(r'retry after (\d+)', r.stderr)
        time.sleep((int(wait.group(1)) if wait else 5) * (attempt + 1))
    raise subprocess.CalledProcessError(r.returncode, a, r.stdout, r.stderr)

lo, _, hi = args.ranks.partition('-')
lo, hi = int(lo), int(hi or lo)
teams, page = [], 1
while True:
    rows = cli_json('ladder', '--page', str(page), '--limit', '100')['teams']
    teams += [t for t in rows if lo <= t['rank'] <= hi]
    if not rows or rows[-1]['rank'] >= hi: break
    page += 1
rank_of = {t['teamId']: t['rank'] for t in teams}
print(f'{len(teams)} teams in ranks {lo}-{hi}', flush=True)

index_path = os.path.join(args.out, 'index.jsonl')
seen = {json.loads(l)['matchId'] for l in open(index_path)} if os.path.exists(index_path) else set()
new = []
for t in teams:
    try:
        ms = cli_json('matches', 'list', '--team', t['teamId'], '--kind', 'ranked', '--limit', str(args.per_team))['matches']
    except subprocess.CalledProcessError as e:
        print('list failed', t['name'], e.stderr[:200], flush=True)
        continue
    for m in ms:
        if m['status'] == 'finished' and m['matchId'] not in seen:
            seen.add(m['matchId'])
            new.append(m)
print(f'{len(new)} new finished matches', flush=True)

def get(m):
    p = os.path.join(args.out, m['matchId'] + '.repl26a')
    for attempt in range(6):
        if os.path.exists(p) and os.path.getsize(p) > 0: return True
        subprocess.run([CAMBC, 'matches', 'download', m['matchId'], '-o', p], capture_output=True)
        if not (os.path.exists(p) and os.path.getsize(p) > 0): time.sleep(5 * (attempt + 1))
    return os.path.exists(p) and os.path.getsize(p) > 0

done = 0
with ThreadPoolExecutor(args.jobs) as ex, open(index_path, 'a') as f:
    for m, ok in zip(new, ex.map(get, new)):
        if not ok: continue
        sides = {s['side']: s for s in m['teams']}
        f.write(json.dumps({'matchId': m['matchId'], 'map': m['map'], 'finishedAt': m.get('finishedAt'),
                            'teams': {k: {'name': s['name'], 'teamId': s['teamId'], 'rank': rank_of.get(s['teamId']),
                                          'result': s['result'], 'engine': s['engineVersion']} for k, s in sides.items()}}) + '\n')
        f.flush()
        done += 1
        if done % 25 == 0: print(f'downloaded {done}/{len(new)}', flush=True)
print(f'downloaded {done} of {len(new)}', flush=True)
