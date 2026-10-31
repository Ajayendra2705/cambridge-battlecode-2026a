# Local game curves: per side, collected and submitted gems (summed over champions) at given rounds.
# usage: python -I lcurve.py FILE.json...   (multi.py result files CAND~POOL~MAP~SIDE.json)
import sys, json, os
RS = (100, 200, 300, 400, 600, 800, 1000, 1500, 2000)
def at(runs, r):
    t = 0; v = 0
    for x in runs:
        if t > r: break
        v = float(x['value']); t += x['duration']
    return v
for f in sys.argv[1:]:
    j = json.load(open(f, encoding='utf-8')); side = os.path.basename(f)[-6]
    tot = {}
    for x in j['championTimelines']:
        if x['metric'] not in ('collectedGems', 'submittedGems'): continue
        w = 'us' if x['owner']['team'][-1] == side else 'them'
        for r in RS: tot[(w, x['metric'], r)] = tot.get((w, x['metric'], r), 0) + at(x['runs'], r)
    print(os.path.basename(f).split('~', 1)[1], j['match']['outcome'], j['match']['roundsCompleted'])
    for w in ('us', 'them'):
        print(f'  {w:4} coll ' + ' '.join(f"{tot[(w,'collectedGems',r)]:5.0f}" for r in RS) + '  sub ' + ' '.join(f"{tot[(w,'submittedGems',r)]:5.0f}" for r in RS))
