"""Write panel specs: python -I tools/platform/mkpanel.py [--size N] SEED TEAM_ID... > results/panels/specs_NAME.txt

Teams go in blocks of 4. In each block the pool maps (every map in maps/: 40 until 10-26, the platform's 70 since) are
shuffled (seeded) and dealt as two 5-map windows per team, so each team plays 10 different maps and a block covers 40 of
them (the whole pool while it had 40). Our side alternates within each window
(a,b,a,b,a then b,a,b,a,b): each team gets 5 games on each side. Spec format: TEAM:map1,...,map5:side1,...,side5."""
import json, os, random, sys
args = sys.argv[1:]
size = None
if args[0] == '--size': size, args = int(args[1]), args[2:]
seed, teams = int(args[0]), args[1:]
pool = sorted(m[:-7].replace('-', '_') for m in os.listdir(os.path.join(os.path.dirname(__file__), '..', '..', 'maps')) if m.endswith('.map26a'))
specs = []
# --size N: only maps of N champions a side (`data/map_sizes.json`), e.g. a five-a-side panel for a change that acts only
# five a side.
if size:
    sizes = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'map_sizes.json'), encoding='utf-8'))
    pool = [m for m in pool if sizes.get(m) == size]
# A pool too small for a block (under 40 maps, e.g. the 12 three-a-side maps) is shuffled again for every team, so each
# team still gets two full 5-map windows (11-01).
if len(pool) < 40:
    for i, t in enumerate(teams):
        maps = pool[:]
        random.Random(seed * 100 + i).shuffle(maps)
        specs.append(f"{t}:{','.join(maps[0:5])}:a,b,a,b,a")
        specs.append(f"{t}:{','.join(maps[5:10])}:b,a,b,a,b")
    print(' '.join(specs))
    sys.exit()
for b in range(0, len(teams), 4):
    maps = pool[:]
    random.Random(seed * 100 + b).shuffle(maps)
    for i, t in enumerate(teams[b:b + 4]):
        for w in range(2):
            win = maps[(2 * i + w) * 5:(2 * i + w + 1) * 5]
            specs.append(f"{t}:{','.join(win)}:{'a,b,a,b,a' if w == 0 else 'b,a,b,a,b'}")
print(' '.join(specs))
