# Positions, bags and hp of every champion every STEP rounds, one game. usage: postrace.py DIR MATCHPREFIX R0 R1 STEP
import glob, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
d, pre, r0, r1, st = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
f = glob.glob(os.path.join(d, pre + '*.jsonl.gz'))[0]
mid = os.path.basename(f).split('.')[0]
idx = {p[0]: p for p in (l.split() for l in open(os.path.join(d, 'index.txt'))) if len(p) >= 4}
_, mp, side, res = idx[mid][:4]
us = 0 if side == 'a' else 1
rows = [r for r in (json.loads(l) for l in gzip.open(f, 'rt')) if r.get('c')]
print(mid, mp, res, 'us team', us)
for r in rows:
    if r['r'] < r0 or r['r'] >= r1 or (r['r'] - r0) % st: continue
    parts = []
    for c in r['c']:
        tag = ('U' if D.who(c['t'], us) == 'us' else 't') + D.NAMES[c['ty']][:3]
        if not c['a'] or 'x' not in c: parts.append(f'{tag}:dead'); continue
        parts.append(f"{tag}({c['x']},{c['y']})g{c.get('g', 0)}")
    print(f"r{r['r']:4} sg{r['sg']} " + ' '.join(parts))
