# How ranged champions spend their attack reset: per game and side, turns with a reset cast followed by an attack,
# split by what came before the reset in that turn: an attack (double shot), a walk (walk-in shot), nothing.
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, RANGE, NAMES
RESET = {('vesper', 0), ('tavi', 0), ('willow', 1)}
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    for r in rows:
        if r['r'] > 1000: break
        for i in range(n):
            ty = NAMES[r['c'][i]['ty']]
            acts = r['act'][i] if i < len(r['act']) else []
            for q, x in enumerate(acts):
                if x[0] != 'cast' or (ty, x[1]) not in RESET: continue
                after = any(y[0] == 'attack' for y in acts[q + 1:])
                before = [y[0] for y in acts[:q] if y[0] in ('attack', 'move')]
                kind = 'after an attack (double shot)' if 'attack' in before else 'after a walk (walk-in shot)' if 'move' in before else 'first action'
                E[(who(r['c'][i]['t'], us), kind + (', then a shot' if after else ', no shot'))] += 1
print(ng, 'games, to r1000: attack resets cast by ranged champions, per game')
for k in sorted(set(k for (_, k) in E)):
    print(f'  {k:46} us {E[("us", k)] / ng:5.2f}   them {E[("them", k)] / ng:5.2f}')
