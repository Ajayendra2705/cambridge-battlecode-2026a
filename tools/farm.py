"""Farming benchmark: bot vs starter for N rounds on every map; prints gems banked at the end of each game."""
import glob, os, re, subprocess, sys, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
bot = sys.argv[1]
rounds = sys.argv[2] if len(sys.argv) > 2 else '400'
out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'batch.py'), bot, 'starter-cpp', '--jobs', '10',
                      '--one-side', '--rounds', rounds], capture_output=True, text=True).stdout
d = re.search(r'dir (batch-\d+)', out).group(1)
total = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'replays', d, '*-A.repl26a'))):
    text = zipfile.ZipFile(f).read('team-a.stdout').decode('latin1')
    g = re.findall(r'G (\d+) (\d+) (\d+)', text)
    ours = int(g[-1][1]) if g else 0
    total += ours
    print(f'{os.path.basename(f)[:-10]:14} {ours:5}')
print('total', total)
