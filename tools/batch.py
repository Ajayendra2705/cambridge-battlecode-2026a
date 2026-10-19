"""Run bot A vs bot B on every map (both sides) with cambc run-batch and print a results table.

usage: python tools/batch.py BOT_A BOT_B [--maps m1,m2] [--jobs N] [--one-side]
Gem totals come from bot A's "G round ours theirs" stdout lines.
"""
import argparse, glob, os, re, subprocess, sys, time, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')

ap = argparse.ArgumentParser()
ap.add_argument('a'); ap.add_argument('b')
ap.add_argument('--maps', default='')
ap.add_argument('--jobs', type=int, default=6)
ap.add_argument('--one-side', action='store_true')
ap.add_argument('--rounds', type=int, default=0)
args = ap.parse_args()

maps = sorted(os.path.basename(m)[:-7] for m in glob.glob(os.path.join(ROOT, 'maps', '*.map26a')))
if args.maps:
    maps = [m for m in maps if m in args.maps.split(',')]

for bot in {args.a, args.b}:
    r = subprocess.run([CAMBC, 'build', bot, '--release'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-3000:], r.stderr[-3000:]); sys.exit(1)

out_dir = os.path.join(ROOT, 'replays', 'batch-' + time.strftime('%H%M%S'))
os.makedirs(out_dir, exist_ok=True)
lines, jobs = [], []
for m in maps:
    sides = [(args.a, args.b, 'A')] if args.one_side else [(args.a, args.b, 'A'), (args.b, args.a, 'B')]
    for x, y, side in sides:
        rep = f'{m}-{side}.repl26a'
        lines.append(f'"../../bots/{x}" "../../bots/{y}" "../../maps/{m}.map26a" "{rep}"')
        jobs.append((m, side, rep))
manifest = os.path.join(out_dir, 'matches.txt')
with open(manifest, 'w') as f:
    f.write('\n'.join(lines) + '\n')
r = subprocess.run([CAMBC, 'run-batch', manifest, '--jobs', str(args.jobs), '--release'] + (['--rounds', str(args.rounds)] if args.rounds else []), cwd=ROOT, capture_output=True, text=True)
log = r.stdout + r.stderr
with open(os.path.join(out_dir, 'batch.log'), 'w') as f:
    f.write(log)

results = {}
for m in re.finditer(r'\[\+\] TEAM ([AB]) WIN \(([^)]*)\).*?Round (\d+)/\d+\s*\n\s*Replay: .*?([^\\/]+\.repl26a)', log):
    results[m.group(4)] = (m.group(1), int(m.group(3)))

wins = total = margin = 0
win_rounds = []
print(f'{"map":14} side  result  ours  theirs  round')
for m, side, rep in jobs:
    if rep not in results:
        print(f'{m:14} {side}     ???'); continue
    winner, rnd = results[rep]
    won = winner == side
    text = zipfile.ZipFile(os.path.join(out_dir, rep)).read(f'team-{side.lower()}.stdout').decode('latin1')
    gl = re.findall(r'G (\d+) (\d+) (\d+)', text)
    ours, theirs = (int(gl[-1][1]), int(gl[-1][2])) if gl else (-1, -1)
    wins += won; total += 1; margin += ours - theirs
    win_rounds.append(rnd if won else 2000)
    print(f'{m:14} {side}     {"WIN " if won else "loss"}    {ours:4}  {theirs:6}  {rnd}')
print(f'wins {wins}/{total}  avg margin {margin / max(total, 1):.0f}  avg round (loss=2000) '
      f'{sum(win_rounds) / max(len(win_rounds), 1):.0f}  dir {os.path.basename(out_dir)}')
