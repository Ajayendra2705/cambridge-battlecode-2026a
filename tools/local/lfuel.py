"""Fuel exhaustions of a candidate per map in a local run: python -I tools/local/lfuel.py RUN_DIR CAND [TOP]
For each map: games, exhaustions per game of the candidate's team, split by round (rounds 1-3, 4-100, 101-300, later), and by champion. Sorted by the total."""
import collections, glob, json, os, sys
run, cand = sys.argv[1], sys.argv[2]
top = int(sys.argv[3]) if len(sys.argv) > 3 else 25
M = collections.defaultdict(collections.Counter)
T = collections.Counter()
for f in glob.glob(os.path.join(run, cand + '~*.json')):
    b, o, m, s = os.path.basename(f)[:-5].split('~')
    try:
        j = json.load(open(f, encoding='utf-8'))
    except Exception:
        continue
    us = 'team' + s
    M[m]['n'] += 1
    for e in j['events']:
        if e['kind'] != 'fuelExhausted' or e['owner'].get('team') != us:
            continue
        for x in e['entries']:
            r = x['timestamp']['round']
            b = '1-3' if r <= 3 else '4-100' if r <= 100 else '101-300' if r <= 300 else '300+'
            M[m][b] += 1
            M[m]['all'] += 1
            T[e['owner'].get('name')] += 1
print('map n all/game  r1-3 r4-100 r101-300 r300+ (per game)')
tot = sum(v['all'] for v in M.values()); ng = sum(v['n'] for v in M.values())
print('all', ng, round(tot / max(1, ng), 2), dict(T.most_common(8)))
for m, v in sorted(M.items(), key=lambda z: -z[1]['all'] / max(1, z[1]['n']))[:top]:
    n = max(1, v['n'])
    print(f"{m:24} {n:3} {v['all']/n:6.1f} | {v['1-3']/n:5.1f} {v['4-100']/n:5.1f} {v['101-300']/n:5.1f} {v['300+']/n:5.1f}")
