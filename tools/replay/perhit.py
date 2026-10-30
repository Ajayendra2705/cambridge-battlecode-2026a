# Damage of a lone hit on a champion (one hitter that round, the target alive after it), by champion type, side, action
# (attack or cast) and phase (r0-299, r300-599, r600 to round R): count, mean, median.
# python -I tools/replay/perhit.py SIZE|0 DIR... [--round R]  (SIZE 0 = every team size; R defaults to 1000)
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
args = sys.argv[1:]
R = 1000
if '--round' in args:
    j = args.index('--round'); R = int(args[j + 1]); del args[j:j + 2]
size, dirs = int(args[0]), args[1:]
A = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(dirs):
    n = len(rows[0]['c'])
    if size and n != 2 * size: continue
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        hits = collections.defaultdict(list)
        for i in range(n):
            for x in D.enemy_hits(a, i, n): hits[x[-1]].append((i, x[0]))
        for t, hs in hits.items():
            if len(hs) != 1 or not b['c'][t]['a']: continue
            loss = a['c'][t].get('hp', 0) - b['c'][t].get('hp', 0)
            if loss <= 0: continue
            i, kind = hs[0]
            A[(a['c'][i]['ty'], kind, min(2, a['r'] // 300), D.who(a['c'][i]['t'], us))].append(loss)
phase = ('r0-299', 'r300-599', f'r600-{R}')
for k in sorted(A, key=lambda k: (D.NAMES[k[0]], k[1], k[2], k[3])):
    v = sorted(A[k])
    if len(v) >= 30:
        print(f'{D.NAMES[k[0]]:9} {k[1]:6} {phase[k[2]]:9} {k[3]:4} n {len(v):5}  mean {sum(v) / len(v):6.1f}  median {v[len(v) // 2]:5}')
