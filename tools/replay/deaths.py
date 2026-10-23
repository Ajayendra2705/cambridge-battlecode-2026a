"""Download our stdout from every match of a gate run and tally death contexts: python -I tools/replay/deaths.py BOT"""
import collections, os, re, subprocess, sys, zipfile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
bot = sys.argv[1]
ids = [l.split()[1:] for l in open(os.path.join(ROOT, 'results', 'gate.log')) if l.split()[:1] == [bot]][-1]
acts = collections.Counter()
for gid in ids:
    text = subprocess.run([CAMBC, 'match-groups', 'show', gid], capture_output=True, text=True, encoding='utf-8').stdout
    for mid, mp, ta in re.findall(r'^(\S{36})\s+finished\s+(\S+)\s*\n\s+(\S{36})', text, re.M):
        path = os.path.join(ROOT, 'data', 'runs', 'plat', mid[:8] + '.repl26a')
        if not os.path.exists(path):
            subprocess.run([CAMBC, 'matches', 'download', mid, '-o', path], capture_output=True)
        if not os.path.exists(path):
            print(f'{mp:12} download failed {mid}')
            continue
        z = zipfile.ZipFile(path)
        name = [n for n in z.namelist() if n.endswith('.stdout')][0]
        for line in z.read(name).decode('latin1').split('\n'):
            line = line.strip()
            if re.match(r'D\d+ s\d', line):
                print(f'{mp:12} {line[:170]}')
                m = re.match(r'D\d+ s\d+ r\d+ hp=\S+ (\S+)', line)
                if m:
                    acts[m.group(1)] += 1
print('deaths by last activity:', dict(acts.most_common()))
