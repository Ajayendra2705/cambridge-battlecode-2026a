"""Judge candidates run between two runs of the same base: python -I tools/platform/sandwich.py BASE1 BASE2 NEW [NEW ...]

Games are deterministic, so the two base runs give the same score in every game unless the opponent changed its bot
in between. Opponents with any game that differs between BASE1 and BASE2 are dropped from every comparison; on the
rest each NEW run is compared with BASE1 (wins, L->W, W->L, margin) and with every earlier NEW run, so a variant
built on another candidate is also compared with its parent. Results come from rcmp.py's cache (data/cache), which
rcmp.py fills: run `python -I tools/platform/rcmp.py BASE1 BASE2 NEW...` first.
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load(run):
    path = os.path.join(ROOT, 'data', 'cache', 'res_' + run.replace('@', '_') + '.json')
    if not os.path.exists(path):
        sys.exit(f'no cache for {run}: run rcmp.py with it first')
    return {tuple(k.split('|')): v for k, v in json.load(open(path)).items()}


b1, b2, news = sys.argv[1], sys.argv[2], sys.argv[3:]
B1, B2 = load(b1), load(b2)
drifted = sorted({k[0] for k in B1 if k in B2 and B1[k][1] != B2[k][1]})
missing = sorted({k[0] for k in B1 if k not in B2} | {k[0] for k in B2 if k not in B1})
print(f'{b1} vs {b2}: {sum(k in B2 for k in B1)} shared games; opponents that changed bots: {len(drifted)}')
for o in drifted:
    ks = [k for k in B1 if k[0] == o and k in B2]
    diff = sum(B1[k][1] != B2[k][1] for k in ks)
    print(f'  drop {o[:40]}: {diff} of {len(ks)} games differ, wins {sum(B1[k][0] for k in ks)} -> {sum(B2[k][0] for k in ks)}')
if missing: print('  games missing from one base run for:', ', '.join(o[:30] for o in missing))
runs = [(b1, B1)] + [(n, load(n)) for n in news]
keep = [k for k in B1 if k in B2 and k[0] not in drifted and all(k in R for _, R in runs)]
print(f'kept {len(keep)} games against {len({k[0] for k in keep})} opponents')
for name, R in runs:
    print(f'  {name:28s} wins {sum(R[k][0] for k in keep):3d}  margin {sum(R[k][1] for k in keep) / max(1, len(keep)):+8.0f}/game')
for i in range(1, len(runs)):
    for j in range(i):
        (na, A), (nb, B) = runs[j], runs[i]
        up = sum(B[k][0] and not A[k][0] for k in keep)
        down = sum(A[k][0] and not B[k][0] for k in keep)
        print(f'{nb} vs {na}: {sum(B[k][0] for k in keep) - sum(A[k][0] for k in keep):+d} wins (L->W {up}, W->L {down})')
