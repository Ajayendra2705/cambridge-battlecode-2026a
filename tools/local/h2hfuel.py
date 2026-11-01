# Head to head of CAND against OPP at one team size, pooled over runs at several fuel values (multi.py --fuel):
#   python -I tools/local/h2hfuel.py SIZE CAND OPP DEFAULT_RUN DEFAULT_CAND RUN [RUN...]   (from the repo root)
# Names as in the file names (exp.b10n, main, bamboo458sf). Each RUN (a folder name under data/runs) holds
# CAND~OPP~MAP~SIDE games. DEFAULT_RUN/DEFAULT_CAND adds games played the other way round, DEFAULT_CAND~CAND~MAP~SIDE,
# with the result flipped (pass DEFAULT_CAND none when the default games are already CAND~OPP and list their run as a
# RUN). Only maps of SIZE count. Prints CAND's win share with its standard error over (map, side) clusters: each
# cluster's mean over its fuel values is one observation, since a map's advantage repeats across fuel values.
# Used for results/analysis/h2h_fuel_1101.md.
import collections, glob, json, math, os, sys

sz = json.load(open('data/map_sizes.json'))
size, cand, opp, drun, dcand, runs = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6:]
cl = collections.defaultdict(list)  # (map, b10n's side) -> b10n wins
for f in glob.glob(os.path.join('data', 'runs', drun, f'{dcand}~{cand}~*.json')):
    _, _, mp, side = os.path.basename(f)[:-5].split('~')
    if sz.get(mp.replace('-', '_')) != size:
        continue
    out = json.load(open(f, encoding='utf-8'))['match']['outcome']
    them = 'team' + side
    cl[(mp, 'B' if side == 'A' else 'A')].append(int(out != them and out != 'draw'))
for r in runs:
    for f in glob.glob(os.path.join('data', 'runs', r, f'{cand}~{opp}~*.json')):
        _, _, mp, side = os.path.basename(f)[:-5].split('~')
        if sz.get(mp.replace('-', '_')) != size:
            continue
        out = json.load(open(f, encoding='utf-8'))['match']['outcome']
        cl[(mp, side)].append(int(out == 'team' + side))
means = [sum(v) / len(v) for v in cl.values()]
n = sum(len(v) for v in cl.values())
mu = sum(means) / len(means)
se = math.sqrt(sum((x - mu) ** 2 for x in means) / (len(means) - 1) / len(means))
print(f'{cand} against {opp}, {size} a side: {sum(sum(v) for v in cl.values())} of {n} games, {len(cl)} clusters, '
      f'share {mu:.3f} +- {se:.3f} (clustered by map and side); games per cluster {sorted(collections.Counter(len(v) for v in cl.values()).items())}')
