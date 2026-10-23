"""Local round robin of ladder bots: every unique pair on every map, both sides.
usage: python -I tools/rr.py BOT1,BOT2,... [--maps m1,m2] [--jobs 6] [--out FILE]
Prints a win matrix (row's wins vs column, out of 2 x maps), each bot's total, and consecutive-pair results
(in the order given: does each bot beat the one before it?). Replays are deleted; JSON summaries are kept."""
import argparse, collections, itertools, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')
ap = argparse.ArgumentParser()
ap.add_argument('bots')
ap.add_argument('--maps', default=open(os.path.join(ROOT, 'tools', 'allmaps.txt')).read().strip())
ap.add_argument('--jobs', type=int, default=6)
ap.add_argument('--dir', help='aggregate an existing run directory instead of playing')
args = ap.parse_args()
bots, maps = args.bots.split(','), args.maps.split(',')

if args.dir:
    out = args.dir
else:
    def build(bot):
        r = subprocess.run([CAMBC, 'build', bot, '--release'], cwd=ROOT, capture_output=True, text=True)
        return bot, r.returncode, r.stdout[-800:] + r.stderr[-800:]
    with ThreadPoolExecutor(4) as ex:
        for bot, rc, log in ex.map(build, bots):
            if rc: print('build failed', bot, log); sys.exit(1)
    out = os.path.join(ROOT, 'replays', 'rr-' + time.strftime('%H%M%S'))
    os.makedirs(out, exist_ok=True)
    rows = []
    for x, y in itertools.combinations(bots, 2):
        for m in maps:
            for a, b in ((x, y), (y, x)):
                name = f'{a}~{b}~{m}'
                rows.append(f'"../../bots/{a}" "../../bots/{b}" "../../maps/{m}.map26a" "{name}.repl26a" --statistics "{name}.json" --json')
    open(os.path.join(out, 'matches.txt'), 'w').write('\n'.join(rows) + '\n')
    print(len(rows), 'games in', out, flush=True)
    subprocess.run([CAMBC, 'run-batch', os.path.join(out, 'matches.txt'), '--jobs', str(args.jobs), '--release'], cwd=ROOT,
                   capture_output=True, text=True)

win = collections.Counter()   # (row, col) -> row wins
games = collections.Counter()
margin = collections.Counter()
for f in os.listdir(out):
    if f.endswith('.repl26a'):
        os.remove(os.path.join(out, f))
        continue
    if not f.endswith('.json'): continue
    a, b, m = f[:-5].split('~')
    d = json.load(open(os.path.join(out, f), encoding='utf-8'))
    o = d['match']['outcome']
    gems = {t['team']: int(t['submittedGems']) for t in d['teams']}
    w = a if o == 'teamA' else b if o == 'teamB' else None
    games[a, b] += 1; games[b, a] += 1
    if w: win[w, b if w == a else a] += 1
    margin[a, b] += gems['teamA'] - gems['teamB']; margin[b, a] += gems['teamB'] - gems['teamA']

w = max(len(x) for x in bots)
print(' ' * w, ' '.join(f'{x[:5]:>5}' for x in bots), '  total')
for r in bots:
    cells = [f'{win[r, c]:>2}/{games[r, c]:<2}' if r != c else '  -  ' for c in bots]
    tw, tg = sum(win[r, c] for c in bots), sum(games[r, c] for c in bots)
    print(f'{r:{w}}', ' '.join(cells), f'  {tw}/{tg} ({100 * tw / max(1, tg):.0f}%)')
print('\nconsecutive (new vs previous):')
for prev, new in zip(bots, bots[1:]):
    n = games[new, prev]
    print(f'  {new} vs {prev}: {win[new, prev]}/{n} wins, gem margin {margin[new, prev] / max(1, n):+.0f}/game')
print('dir', out)
