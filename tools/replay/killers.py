"""Who kills whom over a gate run: python -I tools/replay/killers.py BOT  (uses summaries saved in data/summaries/)"""
import collections, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
bot = sys.argv[1]
ids = [l.split()[1:] for l in open(os.path.join(ROOT, 'results', 'gate.log')) if l.split()[:1] == [bot]][-1]
ctx = {'us': collections.Counter(), 'them': collections.Counter()}
killer = {'us': collections.Counter(), 'them': collections.Counter()}
phase = {'us': collections.Counter(), 'them': collections.Counter()}
games = 0
for gid in ids:
    text = subprocess.run([CAMBC, 'match-groups', 'show', gid], capture_output=True, text=True, encoding='utf-8').stdout
    for mid, ta in re.findall(r'^(\S{36})\s+finished\s+\S+\s*\n\s+(\S{36})', text, re.M):
        p = os.path.join(ROOT, 'data', 'summaries', mid + '.json')
        if not os.path.exists(p):
            continue
        games += 1
        d = json.load(open(p, encoding='utf-8'))
        us = 'teamA' if ta == OUR else 'teamB'
        for ev in d['events']:
            if ev['kind'] != 'death':
                continue
            side = 'us' if ev['owner']['team'] == us else 'them'
            for e in ev['entries']:
                t = e.get('target') or {}
                ctx[side][e.get('context')] += 1
                killer[side][(t.get('kind'), t.get('name'))] += 1
                phase[side][e['timestamp']['round'] // 250 * 250] += 1
print('games', games)
for side in ('us', 'them'):
    print(side, 'deaths by context', dict(ctx[side]))
    print(side, 'by round bucket', sorted(phase[side].items()))
    print(side, 'killers', [(f'{k}:{n}', v) for (k, n), v in killer[side].most_common(14)])
