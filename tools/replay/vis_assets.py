"""Fetch the official visualiser assets (engine WASM + decoder JS) into data/vis/ for vis_decode.mjs.
usage: python -I tools/replay/vis_assets.py REPLAY   (starts `cambc view` on port 7099, crawls its assets, stops it)"""
import os, re, subprocess, sys, time, urllib.request

CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
OUT = os.path.join(ROOT, 'data', 'vis')
os.makedirs(OUT, exist_ok=True)
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
    print(len(os.listdir(OUT)), 'files in', OUT)
finally:
    server.kill()
