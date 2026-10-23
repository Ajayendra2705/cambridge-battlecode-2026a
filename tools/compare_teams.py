"""Compare us vs opponents over gate runs: python -I tools/compare_teams.py RUN [RUN...] (names in tools/gate.log)."""
import collections, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
M = collections.defaultdict(collections.Counter); EV = collections.defaultdict(collections.Counter)
draft = {'U': collections.Counter(), 'T': collections.Counter()}; items = {'U': collections.Counter(), 'T': collections.Counter()}
curve = {'U': collections.defaultdict(list), 'T': collections.defaultdict(list)}
n = 0
for run in sys.argv[1:]:
    ids = [l.split()[1:] for l in open('tools/gate.log') if l.split()[:1] == [run]][-1]
    for gid in ids:
        text = subprocess.run([CAMBC, 'match-groups', 'show', gid], capture_output=True, text=True, encoding='utf-8').stdout
        for mid, ta in re.findall(r'^(\S{36})\s+finished\s+\S+\s*\n\s+(\S{36})', text, re.M):
            p = f'ladder_replays/{mid}.json'
            if not os.path.exists(p): subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
            if not os.path.exists(p): continue
            d = json.load(open(p, encoding='utf-8')); us = 'teamA' if ta == OUR else 'teamB'; n += 1
            for c in d['champions']:
                s = 'U' if c['team'] == us else 'T'
                draft[s][c['name']] += 1
                for k, v in c['metrics'].items():
                    try: M[s][k] += float(v)
                    except ValueError: pass
            for e in d['events']:
                s = 'U' if e['owner'].get('team') == us else 'T'
                EV[s][e['kind']] += len(e['entries'])
                if e['kind'] in ('buyItem', 'buyConsumable'):
                    for x in e['entries']: items[s][(e['kind'], x.get('context'), x.get('value'))] += 1
            for t in d['teamTimelines']:
                if t['metric'] != 'submittedGems': continue
                s = 'U' if t['owner'] == us else 'T'
                r = 0; pts = []
                for run_ in t['runs']: pts.append((r, int(run_['value']))); r += run_['duration']
                for at in (200, 400, 600, 800, 1000):
                    curve[s][at].append(max([v for rr, v in pts if rr <= at] or [0]))
print('games', n)
keys = sorted(set(M['U']) | set(M['T']))
print(f'{"metric":24} {"us/game":>10} {"them/game":>10} {"ratio":>6}')
for k in keys: print(f'{k:24} {M["U"][k]/n:10.0f} {M["T"][k]/n:10.0f} {M["T"][k]/max(M["U"][k],1):6.2f}')
print('events per game'); 
for k in sorted(set(EV['U']) | set(EV['T'])): print(f'  {k:20} {EV["U"][k]/n:8.1f} {EV["T"][k]/n:8.1f}')
print('submitted gems by round (median us / them):')
for at in (200, 400, 600, 800, 1000):
    u = sorted(curve['U'][at]); t = sorted(curve['T'][at])
    print(f'  r{at}: {u[len(u)//2]} / {t[len(t)//2]}')
print('their draft:', draft['T'].most_common(10))
print('our draft:', draft['U'].most_common(6))
print('their purchases (kind, context, value) top:', items['T'].most_common(14))
print('our purchases top:', items['U'].most_common(8))
