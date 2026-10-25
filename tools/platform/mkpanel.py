"""Write panel specs: python -I tools/platform/mkpanel.py SEED TEAM_ID... > results/panels/specs_NAME.txt

Teams go in blocks of 4. In each block the pool maps (every map in maps/: 40 until 10-26, the platform's 70 since) are
shuffled (seeded) and dealt as two 5-map windows per team, so each team plays 10 different maps and a block covers 40 of
them (the whole pool while it had 40). Our side alternates within each window
(a,b,a,b,a then b,a,b,a,b): each team gets 5 games on each side. Spec format: TEAM:map1,...,map5:side1,...,side5."""
import os, random, sys
seed, teams = int(sys.argv[1]), sys.argv[2:]
pool = sorted(m[:-7].replace('-', '_') for m in os.listdir(os.path.join(os.path.dirname(__file__), '..', '..', 'maps')) if m.endswith('.map26a'))
specs = []
for b in range(0, len(teams), 4):
    maps = pool[:]
    random.Random(seed * 100 + b).shuffle(maps)
    for i, t in enumerate(teams[b:b + 4]):
        for w in range(2):
            win = maps[(2 * i + w) * 5:(2 * i + w + 1) * 5]
            specs.append(f"{t}:{','.join(win)}:{'a,b,a,b,a' if w == 0 else 'b,a,b,a,b'}")
print(' '.join(specs))
