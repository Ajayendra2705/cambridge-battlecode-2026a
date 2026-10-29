# Paired comparison pooled over several panels: each BASE NEW pair of runs is paired game by game as in paired.py
# (paired.stats), and the per-game differences of all pairs are pooled exactly, with their standard error. With
# --type the counts are of that champion type only (as in paired.py) and each side's max health of it at r600 is added.
# usage: python -I tools/replay/pooled.py [--type NAME] [--round R] BASE NEW [BASE NEW ...]   (runs as in
#        results/gate.log, all decoded first)
import sys, math, collections
sys.path.insert(0, 'tools/replay')
import paired as P
import decoded as D
args = sys.argv[1:]; ty = None; R = 1000
while args and args[0].startswith('--'):
    if args[0] == '--type': ty = D.NAMES.index(args[1])
    elif args[0] == '--round': R = int(args[1])
    args = args[2:]
F = P.FIELDS + (['us mhp600', 'them mhp600'] if ty is not None else []) + ['margin', 'win']
pairs = []
for b, n in zip(args[::2], args[1::2]):
    A, B = P.stats(b, R, ty), P.stats(n, R, ty)
    ks = [k for k in A if k in B]
    print(f'  {b} -> {n}: {len(ks)} paired games')
    for k in ks:
        for X in (A[k], B[k]): X['margin'] = X['us trib'] - X['them trib']
        pairs.append((A[k], B[k]))
N = len(pairs)
print(f'{N} paired games pooled (to r{R}{", type " + D.NAMES[ty] if ty is not None else ""}): base -> new, diff +- se')
for f in F:
    a = sum(x[0][f] for x in pairs) / N; b = sum(x[1][f] for x in pairs) / N
    ds = [x[1][f] - x[0][f] for x in pairs]; m = sum(ds) / N
    se = math.sqrt(sum((d - m) ** 2 for d in ds) / max(1, N - 1) / N)
    print(f'  {f:12} {a:8.2f} -> {b:8.2f}   {m:+8.2f} +- {se:6.2f}')
