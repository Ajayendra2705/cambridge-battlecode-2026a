"""Map signatures for a per-map router: python -I tools/local/mapsig.py [OUT.json]   (default data/map_sigs.json)

Plays the probe bots/exp/sigp (it prints "SIG width height walls holes altars bushes" and ends its turns) on every map in maps/ for two rounds and
writes {map: [w, h, walls, holes, altars, bushes]}, with a warning for any two maps with the same signature. A router reads the same six numbers
from the SDK before the draft (cheap, and the same for both sides on these symmetric maps), so it needs no walking search and no map names.
"""
import glob, json, os, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
C = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'data', 'map_sigs.json')
tmp = tempfile.mkdtemp(prefix='sig')
sigs = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'maps', '*.map26a'))):
    mp = os.path.basename(f)[:-7]
    for old in glob.glob(os.path.join(tmp, '*')): os.remove(old)
    subprocess.run([C, 'run', 'bots/exp/sigp', 'bots/exp/sigp', '--map', mp, '--rounds', '2', '--release', '-o', tmp], cwd=ROOT, capture_output=True)
    b = glob.glob(os.path.join(tmp, '*.repl26a'))
    if not b:
        print('no bundle', mp); continue
    text = zipfile.ZipFile(b[0]).read('team-a.stdout').decode('latin1')
    line = next((l for l in text.replace('\x00', '\n').split('\n') if l.startswith('SIG ')), None)
    if not line:
        print('no line', mp); continue
    sigs[mp.replace('-', '_')] = [int(x) for x in line.split()[1:]]
shutil.rmtree(tmp, ignore_errors=True)
json.dump(sigs, open(out, 'w', encoding='utf-8'), indent=0)
seen = {}
for mp, s in sigs.items():
    k = tuple(s)
    if k in seen: print('SAME SIGNATURE', seen[k], mp, s)
    seen[k] = mp
print(len(sigs), 'maps,', len(seen), 'signatures ->', out)
