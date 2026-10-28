"""Our newest ranked games on chosen maps, beyond the 100 that tools/replay/qmaps.py can see (h3, 10-28).

usage:
  python -I tools/helper3/h3_qmaps.py list PAGES OUT.json
      Pages through our ranked matches (100 a page, newest first, engine 2.0.0, finished) and writes one record per
      game (mid, map, side, result, opp, created, ours, theirs) to OUT.json. One API call per page, retried on errors.
  python -I tools/helper3/h3_qmaps.py get LIST.json NAME N MAP [MAP ...]
      Takes the newest N games of each MAP (exact platform names, underscores) from LIST.json, downloads their replays
      one at a time into data/replays/platform/NAME/ (backing off on failures such as HTTP 429), and writes index.txt
      (mid map side result, the format of qmaps.py, for pextract.py and decoded.py) and meta.tsv (also opponent,
      creation time and the bot version that was live then, from data/helper3/h3_subs*.json if present).

`cambc matches list --limit` accepts at most 100, so qmaps.py only reaches the last ~2.5 hours of ranked games.
"""
import json, os, subprocess, sys, time, glob

C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
SIZES = {62557: 'go1', 62258: 'cr3', 60976: 'cw1'}  # zip sizes of the main bots' submissions
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def run(args, tries=6):
    for k in range(tries):
        r = subprocess.run([C] + args, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode == 0: return r
        wait = 10 * 2 ** k
        print(f'  retry in {wait}s: {(r.stderr or r.stdout).strip()[:120]}', flush=True)
        time.sleep(wait)
    return r


def cmd_list(pages, out_path):
    ms, cur = [], None
    for page in range(pages):
        r = run(['matches', 'list', '--team', OUR, '--kind', 'ranked', '--limit', '100', '--json'] + (['--cursor', cur] if cur else []))
        t = r.stdout
        d = json.loads(t[t.find('{'):])
        ms += d['matches']; cur = d.get('nextCursor')
        print(f'page {page}: {len(d["matches"])} matches, oldest {d["matches"][-1]["createdAt"] if d["matches"] else "-"}', flush=True)
        if not cur: break
        time.sleep(2)
    out = []
    for m in ms:
        if m['status'] != 'finished': continue
        side = next((x for x in m['teams'] if x['teamId'] == OUR), None)
        if not side or side.get('engineVersion') != '2.0.0': continue
        opp = next((x for x in m['teams'] if x['teamId'] != OUR), {})
        out.append({'mid': m['matchId'], 'map': m['map'], 'side': side['side'], 'result': side['result'],
                    'opp': opp.get('teamName') or opp.get('name'), 'created': m.get('createdAt'),
                    'ours': side.get('draftPicks'), 'theirs': opp.get('draftPicks')})
    json.dump(out, open(out_path, 'w', encoding='utf-8'))
    print(len(out), 'games written to', out_path)


def versions():
    """(activation time, version, label) from saved `cambc submissions list --json` pages, oldest first."""
    subs = {}
    for f in glob.glob(os.path.join('data', 'helper3', 'h3_subs*.json')):
        t = open(f, encoding='utf-8').read()
        for s in json.loads(t[t.find('{'):])['submissions']: subs[s['version']] = s
    live = sorted((s for s in subs.values() if s['status'] != 'cancelled'), key=lambda s: s['createdAt'])
    act = []
    for i, s in enumerate(live):
        start = live[i - 1]['statusAt'] if i else s['createdAt']  # live from the moment the previous one went inactive
        act.append((max(start, s['createdAt']), s['version'], SIZES.get(s['size'], f'var{s["size"]}')))
    return act


def live_at(act, t):
    best = None
    for start, v, label in act:
        if start <= t: best = (v, label)
    return best if best else (None, 'old')


def cmd_get(list_path, name, n, maps):
    games = json.load(open(list_path, encoding='utf-8'))
    act = versions()
    out = os.path.join('data', 'replays', 'platform', name); os.makedirs(out, exist_ok=True)
    idx, meta = [], []
    for mp in maps:
        for g in [g for g in games if g['map'] == mp][:n]:
            r = os.path.join(out, g['mid'] + '.repl26a')
            if not (os.path.exists(r) and os.path.getsize(r) > 0):
                res = run(['matches', 'download', g['mid'], '-o', r])
                if res.returncode != 0 or not os.path.exists(r):
                    print('FAIL', g['mid'], flush=True); continue
                time.sleep(1)
            v, label = live_at(act, g['created'])
            idx.append(f"{g['mid']} {g['map']} {g['side']} {g['result']}")
            meta.append(f"{g['mid']}\t{g['map']}\t{g['side']}\t{g['result']}\t{g['opp']}\t{g['created']}\tv{v}\t{label}")
            print(meta[-1], flush=True)
    with open(os.path.join(out, 'index.txt'), 'w', newline='') as f: f.write('\n'.join(idx) + '\n')
    with open(os.path.join(out, 'meta.tsv'), 'w', encoding='utf-8', newline='') as f: f.write('\n'.join(meta) + '\n')
    print(len(idx), 'games in', out)


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'list': cmd_list(int(sys.argv[2]), sys.argv[3])
    elif len(sys.argv) >= 6 and sys.argv[1] == 'get': cmd_get(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5:])
    else: print(__doc__)
