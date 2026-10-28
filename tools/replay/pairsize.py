"""Paired per-game differences (new - base, with standard errors) of collected, tributed, their tributed, deaths and lost
on death to r1000, split by team size (champions per side), for runs paired as in tools/replay/paired.py; several
BASE NEW pairs pool. usage: python -I tools/replay/pairsize.py BASE_RUN NEW_RUN [BASE_RUN NEW_RUN ...]
"""
import sys, os, math, collections, gzip, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paired as P
F = ['us coll', 'us trib', 'them trib', 'us deaths', 'them deaths', 'us lost']
G = collections.defaultdict(list)
args = sys.argv[1:]
for base, new in zip(args[::2], args[1::2]):
    A, B = P.stats(base, 1000), P.stats(new, 1000)
    size = {}
    d = os.path.join(P.ROOT, 'data', 'fights', base.replace('@', '_'))
    for mid, (opp, mp, k) in P.match_map(base).items():
        f = os.path.join(d, mid + '.jsonl.gz')
        if mp in size or not os.path.exists(f): continue
        for l in list(gzip.open(f, 'rt'))[1:]:
            r = json.loads(l)
            if r.get('c'): size[mp] = len(r['c']) // 2; break
    for k in A:
        if k in B: G[size.get(k[1], 0)].append((A[k], B[k])); G['all'].append((A[k], B[k]))
for s in sorted(G, key=str):
    v = G[s]
    cells = []
    for f in F:
        ds = [b[f] - a[f] for a, b in v]
        m = sum(ds) / len(ds); se = math.sqrt(sum((x - m) ** 2 for x in ds) / max(1, len(ds) - 1) / len(ds))
        cells.append(f'{f} {sum(a[f] for a, b in v) / len(v):.1f}{m:+.1f}+-{se:.1f}')
    wins = sum(a['win'] for a, b in v), sum(b['win'] for a, b in v)
    print(f'size {s}: {len(v)} games, wins {wins[0]}->{wins[1]}; ' + ', '.join(cells))
