# Local losses by map and opponent: python -I lmaps.py RUNDIR...  (multi.py run folders; files CAND~POOL~MAP~SIDE.json)
import sys, os, glob, json, collections
L = collections.Counter(); N = collections.Counter(); O = collections.Counter(); D = collections.Counter(); M = collections.Counter()
for d in sys.argv[1:]:
    for f in glob.glob(os.path.join(d, (os.environ.get('CAND', '') + '*') if os.environ.get('CAND') else '*.json')):
        if not f.endswith('.json'): continue
        cand, pool, mp, side = os.path.basename(f)[:-5].split('~')
        j = json.load(open(f, encoding='utf-8'))
        out = j['match']['outcome']
        win = out.endswith(side) if isinstance(out, str) else False
        N[mp] += 1
        g = {t['team'][-1]: int(t['submittedGems']) for t in j['teams']}
        M[mp] += g.get(side, 0) - sum(v for k, v in g.items() if k != side)
        D[mp] += sum(float(c['metrics']['deaths']) for c in j['champions'] if c['team'][-1] == side)
        if not win: L[mp] += 1; O[(mp, pool)] += 1
tot = sum(N.values())
print(f'{tot} games, {sum(L.values())} losses')
for mp, n in sorted(N.items(), key=lambda x: -L[x[0]]):
    if not L[mp]: continue
    print(f'{mp:26} lost {L[mp]:3}/{n:3}  margin/g {M[mp]/n:+7.0f}  deaths/g {D[mp]/n:5.1f}  by ' + ' '.join(f'{p.split(".")[-1]}:{O[(mp,p)]}' for (m, p) in O if m == mp))
