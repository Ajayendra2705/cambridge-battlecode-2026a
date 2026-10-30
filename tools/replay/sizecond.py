"""A size-conditional variant from two decoded runs on the same pinned panels, without a gate.

usage: python -I tools/replay/sizecond.py SIZES BASE NEW [BASE NEW ...]   (SIZES e.g. 5 or 4,5; runs as in results/gate.log)

A variant that plays as NEW on maps of the listed team sizes (`data/map_sizes.json`) and as BASE elsewhere replays, game
by game, NEW's game on those maps and BASE's game on the others: platform games are deterministic and pinned panels keep
the opponents' bots (main_b24p@b24p at 00:21 IST 10-31 replayed bb2_b24@b24 from 20:16 exactly). Prints the pooled paired
differences against BASE over all games (as pooled.py) and over the listed sizes only.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paired as P
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sizes = {int(x) for x in sys.argv[1].split(',')}
runs = sys.argv[2:]
size_of = json.load(open(os.path.join(ROOT, 'data', 'map_sizes.json'), encoding='utf-8'))
F = P.FIELDS + ['margin', 'win']
allp, inp = [], []
for b, n in zip(runs[::2], runs[1::2]):
    A, B = P.stats(b, 1000), P.stats(n, 1000)
    ks = [k for k in A if k in B]
    unknown = sorted({k[1] for k in ks if k[1] not in size_of})
    print(f'  {b} -> {n}: {len(ks)} paired games' + (f'; maps without a size (played as BASE): {unknown}' if unknown else ''))
    for k in ks:
        for X in (A[k], B[k]): X['margin'] = X['us trib'] - X['them trib']
        hit = size_of.get(k[1]) in sizes
        pair = (A[k], B[k] if hit else A[k])
        allp.append(pair)
        if hit: inp.append(pair)
for label, ps in (('all games', allp), (f'size {sorted(sizes)} only', inp)):
    N = len(ps)
    if not N: continue
    print(f'{N} paired games, {label} (to r1000): base -> size-conditional, diff +- se')
    for f in F:
        a = sum(x[0][f] for x in ps) / N; c = sum(x[1][f] for x in ps) / N
        ds = [x[1][f] - x[0][f] for x in ps]; m = sum(ds) / N
        se = math.sqrt(sum((d - m) ** 2 for d in ds) / max(1, N - 1) / N)
        print(f'  {f:12} {a:8.2f} -> {c:8.2f}   {m:+8.2f} +- {se:6.2f}')
