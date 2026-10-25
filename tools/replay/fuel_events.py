"""Platform fuel exhaustion and bot faults of our team per gate run: python -I tools/replay/fuel_events.py RUN [RUN...]

RUN is a run name as in results/gate.log (e.g. cand6_b3456@b3456). Reads the match summaries (fetched into
data/summaries/ when missing) and prints per run: games, botFault events, fuelExhausted events per game for us and
for the opponents, ours by round (1-3 = the setup spilling over, 4-30, 31 on), by map size and by champion.
"""
import json, os, re, subprocess, sys, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
for run in sys.argv[1:]:
    ids = [l.split()[1:] for l in open('results/gate.log') if l.split()[:1] == [run]][-1]
    rounds = collections.Counter(); maps = collections.Counter(); champs = collections.Counter(); faults = 0; n = 0; them = 0
    for gid in ids:
        text = subprocess.run([CAMBC, 'match-groups', 'show', gid], capture_output=True, text=True, encoding='utf-8').stdout
        for mid, ta in re.findall(r'^(\S{36})\s+finished\s+\S+\s*\n\s+(\S{36})', text, re.M):
            p = f'data/summaries/{mid}.json'
            if not os.path.exists(p):
                subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
            if not os.path.exists(p): continue
            d = json.load(open(p, encoding='utf-8')); us = 'teamA' if ta == OUR else 'teamB'; n += 1
            m = d['match']
            mname = f"{m.get('width')}x{m.get('height')}"
            for e in d['events']:
                if e['kind'] == 'botFault' and e['owner'].get('team') == us: faults += len(e['entries'])
                if e['kind'] != 'fuelExhausted': continue
                if e['owner'].get('team') != us:
                    them += len(e['entries']); continue
                for x in e['entries']:
                    r = x['timestamp']['round']
                    rounds['r1-3' if r <= 3 else 'r4-30' if r <= 30 else 'r31+'] += 1
                    maps[mname] += 1
                    champs[e['owner'].get('name')] += 1
    print(f'== {run}: games {n}, botFault {faults}, fuelExhausted us {sum(rounds.values())/max(n,1):.1f}/game them {them/max(n,1):.1f}/game, by round {dict(rounds)}')
    print('   maps', maps.most_common(8))
    print('   champions', champs.most_common(8))
