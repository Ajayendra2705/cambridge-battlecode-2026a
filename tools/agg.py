"""Per-champion averages over a gate run, ours vs opponents': python -I tools/agg.py BOT

Reads the match summaries group.py saved in ladder_replays/ and prints, per champion name and side, games played,
deaths, kills, champion damage done/taken, monster damage done, gems collected and submitted, gold earned.
"""
import collections, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
bot = sys.argv[1]
ids = [l.split()[1:] for l in open(os.path.join(ROOT, 'tools', 'gate.log')) if l.split()[:1] == [bot]][-1]
keys = ['deaths', 'kills', 'championDamageDone', 'championDamageTaken', 'monsterDamageDone', 'collectedGems', 'submittedGems', 'earnedGold']
acc = collections.defaultdict(lambda: collections.Counter())
for gid in ids:
    text = subprocess.run([CAMBC, 'match-groups', 'show', gid], capture_output=True, text=True, encoding='utf-8').stdout
    for mid, ta in re.findall(r'^(\S{36})\s+finished\s+\S+\s*\n\s+(\S{36})', text, re.M):
        p = os.path.join(ROOT, 'ladder_replays', mid + '.json')
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        us = 'teamA' if ta == OUR else 'teamB'
        for c in d['champions']:
            side = 'us' if c['team'] == us else 'them'
            a = acc[(side, c['name'])]
            a['n'] += 1
            for k in keys:
                a[k] += float(c['metrics'][k])
print(f'{"side":5} {"champion":12} {"n":>4} ' + ' '.join(f'{k[:9]:>9}' for k in keys))
for (side, name), a in sorted(acc.items(), key=lambda x: (x[0][0] != 'us', -x[1]['n'])):
    print(f'{side:5} {name:12} {a["n"]:4} ' + ' '.join(f'{a[k] / a["n"]:9.0f}' for k in keys))
