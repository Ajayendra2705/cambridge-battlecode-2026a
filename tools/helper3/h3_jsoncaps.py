"""Captures of cover-locked groups in a local multi.py run, from the statistics JSONs (no decode needed) (h3, 10-28).

usage: python -I tools/helper3/h3_jsoncaps.py RUNDIR CAND [CAND ...] [--upto R]   (CAND as in the file names: main, exp.h3cv1)

Each game's `CAND~OPP~MAP~SIDE.json` lists `campClear` events (one entry per champion credited with a group capture,
with the round and a tile of the group). A capture is one (round, tile) per team. Groups and the locked set come from
the map's md1 dump and tools/helper3/h3_cover.py (both sides' locked groups). Prints per map and candidate, per game to
round R (default 1000): our captures of locked groups, all our captures, and the opponent's captures of locked groups.
"""
import collections, glob, json, os, sys

args = sys.argv[1:]
R = 1000
if '--upto' in args:
    i = args.index('--upto'); R = int(args[i + 1]); del args[i:i + 2]
run, cands = args[0], args[1:]
src = open(os.path.join('tools', 'helper3', 'h3_cover.py'), encoding='utf-8').read()
ns = {}; exec(src.split('paths = sys.argv[1:]')[0], ns)
CAMP = set('wEg$GM')
cache = {}


def layout(mp):
    if mp not in cache:
        path = os.path.join('data', 'maps_txt', mp + '.txt')
        if not os.path.exists(path): cache[mp] = None; return None
        total, lost, out, nd, gd = ns['analyse'](path)
        blocked = {int(o.split('(')[0]) for o in out}
        L = open(path, encoding='utf-8').read().splitlines(); W, H = int(L[0].split()[2]), int(L[0].split()[3])
        g = [list(l) for l in L[1:1 + H]]
        tile, ng = {}, 0
        for y in range(H):
            for x in range(W):
                if g[y][x] in CAMP and (x, y) not in tile:
                    st = [(x, y)]; tile[(x, y)] = ng
                    while st:
                        cx, cy = st.pop()
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            t = (cx + dx, cy + dy)
                            if 0 <= t[0] < W and 0 <= t[1] < H and g[t[1]][t[0]] in CAMP and t not in tile: tile[t] = ng; st.append(t)
                    ng += 1
        cache[mp] = (blocked, tile)
    return cache[mp]


C = collections.Counter()
for cand in cands:
    for f in sorted(glob.glob(os.path.join(run, cand + '~*.json'))):
        name = os.path.basename(f)[:-5]
        _, opp, mp, side = name.split('~')
        lay = layout(mp)
        if not lay: continue
        blocked, tile = lay
        us = 'teamA' if side == 'A' else 'teamB'
        d = json.load(open(f, encoding='utf-8'))
        seen = set()
        for e in d['events']:
            if e['kind'] != 'campClear': continue
            team = e['owner'].get('team')
            for en in e['entries']:
                rnd = en['timestamp']['round']
                if rnd > R or (team, rnd, en['x'], en['y']) in seen: continue
                seen.add((team, rnd, en['x'], en['y']))
                gi = tile.get((en['x'], en['y']))
                if gi is None:
                    gi = next((tile[(en['x'] + dx, en['y'] + dy)] for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (en['x'] + dx, en['y'] + dy) in tile), None)
                w = 'us' if team == us else 'them'
                for key in (mp, 'total'):
                    C[cand, key, w, 'all'] += 1
                    if gi in blocked: C[cand, key, w, 'locked'] += 1
        for key in (mp, 'total'): C[cand, key, 'games'] += 1
maps = sorted({k[1] for k in C if len(k) == 3 and k[2] == 'games'}, key=lambda m: (m == 'total', m))
print(f'captures per game to r{R}: ours of locked groups / all ours / theirs of locked groups, per candidate')
print(f'{"map":22} ' + ' | '.join(f'{c:>22}' for c in cands))
for mp in maps:
    cells = []
    for c in cands:
        n = max(1, C[c, mp, 'games'])
        cells.append(f'{C[c, mp, "us", "locked"] / n:6.2f} {C[c, mp, "us", "all"] / n:6.1f} {C[c, mp, "them", "locked"] / n:6.2f}')
    print(f'{mp:22} ' + ' | '.join(f'{x:>22}' for x in cells))
