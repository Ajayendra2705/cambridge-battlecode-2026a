# Per map: our and their collected gems at r100/r300/r600 (means over games), wins. usage: mapopen.py RUNDIR CAND
import sys, os, glob, json, collections
RS = (100, 300, 600)
def at(runs, r):
    t = 0; v = 0
    for x in runs:
        if t > r: break
        v = float(x['value']); t += x['duration']
    return v
A = collections.defaultdict(lambda: [0] * 7)
for f in glob.glob(os.path.join(sys.argv[1], sys.argv[2] + '~*.json')):
    _, pool, mp, side = os.path.basename(f)[:-5].split('~')
    j = json.load(open(f, encoding='utf-8'))
    a = A[mp]; a[6] += 1; a[0] += j['match']['outcome'].endswith(side)
    for x in j['championTimelines']:
        if x['metric'] != 'collectedGems': continue
        us = x['owner']['team'][-1] == side
        for i, r in enumerate(RS): a[1 + i] += at(x['runs'], r) * (1 if us else 0)
        for i, r in enumerate(RS[1:]): pass
    for x in j['championTimelines']:
        if x['metric'] != 'collectedGems' or x['owner']['team'][-1] == side: continue
        a[4] += at(x['runs'], 100); a[5] += at(x['runs'], 600)
rows = sorted(A.items(), key=lambda kv: (kv[1][3] - kv[1][5]) / kv[1][6])
for mp, a in rows[:int(sys.argv[3]) if len(sys.argv) > 3 else 25]:
    n = a[6]
    print(f'{mp:24} won {a[0]}/{n}  r100 {a[1]/n:4.0f}:{a[4]/n:4.0f}  r300 {a[2]/n:4.0f}  r600 {a[3]/n:4.0f}:{a[5]/n:4.0f}')
