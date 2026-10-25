"""Fetch the official visualiser assets (engine WASM + decoder JS) of the installed cambc for vis_decode.mjs.
usage: python -I tools/replay/vis_assets.py REPLAY   (starts `cambc view` on port 7099, crawls its assets, stops it)
The assets go to data/vis/<newest engine they ship>/ (for example data/vis/v1_1_0/), and vis_decode.mjs reads replays of
that engine with them; replays of older engines keep the flat data/vis/ (cambc 3.0.5, engines up to 1.0.3)."""
import os, re, shutil, subprocess, sys, time, urllib.request

CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
OUT = os.path.join(ROOT, 'data', 'vis', 'new')
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
server = subprocess.Popen([CAMBC, 'view', '--port', '7099', sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(5)
    seen, todo = set(), ['index.html']
    while todo:
        p = todo.pop()
        if p in seen: continue
        seen.add(p)
        try: data = urllib.request.urlopen('http://127.0.0.1:7099/' + p).read()
        except Exception: continue
        open(os.path.join(OUT, os.path.basename(p)), 'wb').write(data)
        if p.endswith(('.js', '.html')):
            for n in set(re.findall(r'([\w\-]+(?:\.[\w\-]+)*\.(?:js|wasm))', data.decode('utf-8', 'replace'))):
                if 'assets/' + n not in seen: todo.append('assets/' + n)
finally:
    server.kill()
engines = [m for f in os.listdir(OUT) if (m := re.match(r'v(\d+)_(\d+)_(\d+)-.*\.wasm$', f))]
if not engines: sys.exit(f'no engine WASM fetched (is cambc view running elsewhere on port 7099?); see {OUT}')
newest = max(engines, key=lambda m: tuple(map(int, m.groups())))
final = os.path.join(ROOT, 'data', 'vis', 'v{}_{}_{}'.format(*newest.groups()))
shutil.rmtree(final, ignore_errors=True)
os.rename(OUT, final)
print(len(os.listdir(final)), 'files in', final)
