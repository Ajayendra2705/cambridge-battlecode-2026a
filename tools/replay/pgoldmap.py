"""pgold.py split by map: python -I tools/replay/pgoldmap.py BASE_RUN NEW_RUN [BASE_RUN NEW_RUN ...]

Runs are names in results/gate.log (RUN@PANEL), each pair on one pinned panel; the maps come from results/panels/specs_PANEL.txt in group and position order.
Prints, per map over all pairs, the paired difference (new minus base) of team gold at r300, r600 and r1000, their gold at r1000, our and their deaths at r1000, and wins of both runs.
Uses the summaries in data/summaries/ and fetches what is missing.
"""
import collections, json, math, os, re, subprocess, sys, time

CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
ROUNDS = (300, 600, 1000)


def at(runs, r):
    t, v = 0, 0.0
    for x in runs:
        if t >= r:
            break
        v = float(x['value'])
        t += x['duration']
    return v


def read(run):
    panel = run.split('@')[1]
    ids = [l.split()[1:] for l in open('results/gate.log', encoding='utf-8') if l.split()[:1] == [run]][-1]
    specs = open(f'results/panels/specs_{panel}.txt', encoding='utf-8').read().split()
    out = {}
    for gi, gid in enumerate(ids):
        maps = specs[gi].split(':')[1].split(',')
        found = []
        for attempt in range(6):
            text = subprocess.run([CAMBC, 'match-groups', 'show', gid], capture_output=True, text=True, encoding='utf-8').stdout
            found = re.findall(r'^(\S{36})\s+finished\s+\S+\s*\n\s+(\S{36})', text, re.M)
            if found:
                break
            time.sleep(5 * (attempt + 1))
        for pos, (mid, ta) in enumerate(found):
            p = f'data/summaries/{mid}.json'
            if not os.path.exists(p):
                subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
            if not os.path.exists(p):
                continue
            d = json.load(open(p, encoding='utf-8'))
            us = 'teamA' if ta == OUR else 'teamB'
            m = collections.Counter()
            for t in d['championTimelines']:
                o = t['owner']
                if t['metric'] in ('earnedGold', 'deaths'):
                    side = 'us' if o.get('team') == us else 'them'
                    for r in ROUNDS:
                        m[(t['metric'], side, r)] += at(t['runs'], r)
            final = {}
            for t in d['teamTimelines']:
                if t['metric'] == 'submittedGems':
                    o = t['owner']
                    side = 'us' if (o if isinstance(o, str) else o.get('team')) == us else 'them'
                    tot = 0
                    for x in t['runs']:
                        tot = float(x['value'])
                    final[side] = tot
            m['win'] = final.get('us', 0) > final.get('them', 0)
            out[(gi, pos)] = (maps[pos] if pos < len(maps) else '?', m)
    return out


D = collections.defaultdict(lambda: collections.defaultdict(list))
W = collections.defaultdict(lambda: [0, 0, 0])
args = sys.argv[1:]
for base, new in zip(args[::2], args[1::2]):
    B, N = read(base), read(new)
    for k in B:
        if k not in N:
            continue
        mp, b = B[k]
        _, n = N[k]
        W[mp][0] += b['win']
        W[mp][1] += n['win']
        W[mp][2] += 1
        for name, key in (('gold300', ('earnedGold', 'us', 300)), ('gold600', ('earnedGold', 'us', 600)), ('gold1000', ('earnedGold', 'us', 1000)), ('their1000', ('earnedGold', 'them', 1000)), ('deaths', ('deaths', 'us', 1000)), ('tdeaths', ('deaths', 'them', 1000))):
            D[mp][name].append(n[key] - b[key])
            D['ALL'][name].append(n[key] - b[key])


def ms(v):
    n = len(v)
    if n < 2:
        return 0, 0
    a = sum(v) / n
    return a, math.sqrt(sum((x - a) ** 2 for x in v) / (n - 1) / n)


print(f"{'map':22} {'n':>3} {'wins':>7} | {'gold r300':>13} {'gold r600':>14} {'gold r1000':>14} {'their r1000':>14} {'deaths':>11} {'their deaths':>11}")
for mp in sorted(D, key=lambda x: (x == 'ALL', -(sum(D[x]['gold1000']) / max(1, len(D[x]['gold1000']))))):
    w = W[mp] if mp != 'ALL' else [sum(W[m][0] for m in W), sum(W[m][1] for m in W), sum(W[m][2] for m in W)]
    cells = ' '.join(f"{ms(D[mp][c])[0]:+7.0f}+-{ms(D[mp][c])[1]:<5.0f}" for c in ('gold300', 'gold600', 'gold1000', 'their1000'))
    d = ' '.join(f"{ms(D[mp][c])[0]:+5.1f}+-{ms(D[mp][c])[1]:<4.1f}" for c in ('deaths', 'tdeaths'))
    print(f'{mp:22} {w[2]:3} {w[0]:3}>{w[1]:<3} | {cells} {d}')
