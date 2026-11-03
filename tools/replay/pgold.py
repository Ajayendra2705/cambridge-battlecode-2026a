"""Earned gold and gems by round from platform match summaries, paired: python -I tools/replay/pgold.py BASE_RUN NEW_RUN [NEW_RUN ...]

Runs are names in results/gate.log (RUN@PANEL). Pairs games by group order and position within the group, so both runs must play the same panel in the same order. Prints, as new minus base per game with its standard error:
team gold earned, Vesper's gold earned (over games where both have her), tributed gems, collected gems and deaths by r150, r300, r600, r1000, plus the same for the rival's team gold. Needs no replay decoding: only downloads summaries
(data/summaries/), so a gate can be judged without loading the laptop.
"""
import collections, json, math, os, re, subprocess, sys, time

CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
ROUNDS = (150, 300, 600, 1000)


def at(runs, r):
    t, v = 0, 0.0
    for x in runs:
        if t >= r:
            break
        v = float(x['value'])
        t += x['duration']
    return v


def read(run):
    ids = [l.split()[1:] for l in open('results/gate.log', encoding='utf-8') if l.split()[:1] == [run]][-1]
    out = []
    for gid in ids:
        found = []
        for attempt in range(6):
            text = subprocess.run([CAMBC, 'match-groups', 'show', gid], capture_output=True, text=True, encoding='utf-8').stdout
            found = re.findall(r'^(\S{36})\s+finished\s+\S+\s*\n\s+(\S{36})', text, re.M)
            if found:
                break
            time.sleep(5 * (attempt + 1))
        rows = []
        for mid, ta in found:
            p = f'data/summaries/{mid}.json'
            if not os.path.exists(p):
                subprocess.run([CAMBC, 'matches', 'summary', mid, '--json', '-o', p], capture_output=True)
            if not os.path.exists(p):
                rows.append(None)
                continue
            d = json.load(open(p, encoding='utf-8'))
            us = 'teamA' if ta == OUR else 'teamB'
            m = collections.Counter()
            for t in d['championTimelines']:
                o = t['owner']
                if t['metric'] in ('earnedGold', 'collectedGems', 'deaths'):
                    for r in ROUNDS:
                        side = 'us' if o.get('team') == us else 'them'
                        m[(t['metric'], side, r)] += at(t['runs'], r)
                        if t['metric'] == 'earnedGold' and o.get('name') == 'Vesper Vale' and side == 'us':
                            m[('vesper', 'us', r)] += at(t['runs'], r)
                            m['has_vesper'] = 1
            for t in d['teamTimelines']:
                if t['metric'] == 'submittedGems':
                    o = t['owner']
                    side = 'us' if (o if isinstance(o, str) else o.get('team')) == us else 'them'
                    for r in ROUNDS:
                        m[('tributed', side, r)] = at(t['runs'], r)
            rows.append(m)
        out.append(rows)
    return out


base = read(sys.argv[1])
print(sys.argv[1], sum(1 for g in base for m in g if m), 'games')
for run in sys.argv[2:]:
    new = read(run)
    print(run, sum(1 for g in new for m in g if m), 'games; new minus base per game (+- se)')
    for label, key, only in (('team gold', ('earnedGold', 'us'), False), ('Vesper gold', ('vesper', 'us'), True), ('their gold', ('earnedGold', 'them'), False), ('collected', ('collectedGems', 'us'), False),
                             ('tributed', ('tributed', 'us'), False), ('their tributed', ('tributed', 'them'), False), ('deaths', ('deaths', 'us'), False), ('their deaths', ('deaths', 'them'), False)):
        line = f'  {label:15s}'
        for r in ROUNDS:
            ds, bs = [], []
            for gb, gn in zip(base, new):
                for mb, mn in zip(gb, gn):
                    if not mb or not mn or (only and not (mb['has_vesper'] and mn['has_vesper'])):
                        continue
                    ds.append(mn[key + (r,)] - mb[key + (r,)])
                    bs.append(mb[key + (r,)])
            if ds:
                mean = sum(ds) / len(ds)
                sd = math.sqrt(sum((x - mean) ** 2 for x in ds) / max(1, len(ds) - 1))
                line += f' | r{r} {mean:+7.1f} +- {sd / math.sqrt(len(ds)):5.1f} ({sum(bs) / len(bs):5.0f})'
        print(line)
