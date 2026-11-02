"""Fuel left after setup on the first play turn, on every map: python -I tools/local/firstturn.py BOT [OUT.json]

Copies bots/BOT to a temporary probe (never shipped) that prints the fuel left after Bot::init, plays three rounds on each map in maps/ against pool/dh3 and prints each champion's value. The bot
acts on its first turn only when the fuel left is at least the threshold of the line `if (fuel() < 120000) return;` in Bot::play_turn. A value near 100000 means setup ran out of the first turn's
200k and finished on the next. Writes {map: [fuel, ...]} to OUT.json (default data/first_turn_fuel.json).
"""
import glob, json, os, re, shutil, subprocess, sys, tempfile, zipfile
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
bot = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join('data', 'first_turn_fuel.json')
os.chdir(ROOT)
dst = 'bots/exp/ftp_probe'
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree('bots/' + bot, dst, ignore=shutil.ignore_patterns('.cambc'))
p = dst + '/src/bot.cpp'
s = open(p, encoding='utf-8', newline='').read()
m = re.search(r'( *)if \(fuel\(\) < (\d+)\) return;  // big maps: finish setup, act next turn\r?\n', s)
assert m, 'threshold line not found'
s = s.replace(m.group(0), m.group(1) + '{ const auto f0 = fuel(); std::printf("FI %%d %%llu\\n", idx, static_cast<unsigned long long>(f0)); if (f0 < %s) return; }\n' % m.group(2))
s = '#include <cstdio>\n' + s
open(p, 'w', encoding='utf-8', newline='').write(s)
r = subprocess.run([C, 'build', dst, '--release'], capture_output=True, text=True, encoding='utf-8', errors='replace')
assert 'built' in r.stdout + r.stderr, (r.stdout + r.stderr)[-400:]


def one(f):
    mp = os.path.basename(f)[:-7]
    tmp = tempfile.mkdtemp()
    v = None
    try:
        subprocess.run([C, 'run', dst, 'bots/pool/dh3', '--map', mp, '--rounds', '3', '--release', '-o', tmp], capture_output=True, timeout=240)
        b = glob.glob(tmp + '/*.repl26a')
        if b:
            text = zipfile.ZipFile(b[0]).read('team-a.stdout').decode('latin1')
            v = [int(x) for x in re.findall(r'FI \d+ (\d+)', text)]
    except Exception as e:
        print('fail', mp, e)
    shutil.rmtree(tmp, ignore_errors=True)
    return mp, v


with ThreadPoolExecutor(8) as ex:
    res = dict(ex.map(one, sorted(glob.glob('maps/*.map26a'))))
shutil.rmtree(dst, ignore_errors=True)
json.dump(res, open(out, 'w'))
vals = [x for v in res.values() if v for x in v]
print(len(res), 'maps;', sum(1 for v in res.values() if not v), 'without a reading')
print('champions with fuel left >= 120000:', sum(x >= 120000 for x in vals), 'of', len(vals))
for lo, hi in ((0, 2000), (2000, 20000), (20000, 50000), (50000, 80000), (80000, 120000), (120000, 200000)):
    print(f'  {lo}-{hi}: {sum(lo <= x < hi for x in vals)}')
for k, v in sorted(res.items(), key=lambda kv: min(kv[1]) if kv[1] else 1 << 30):
    print(k, v)
