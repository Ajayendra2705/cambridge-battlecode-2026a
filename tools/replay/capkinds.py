"""What each side captures, by kind of group: python -I tools/replay/capkinds.py RMAX [--maps m1,m2] DIR [DIR ...]

To round RMAX, per game: reward rises (a champion's gold held or bag rises with no kill, on a tile within 3 of a group in data/map_info.json) by the group's kind (gold, gem, wolf, elk, golem, monolith; the hardest camp
names it) and by the half it lies on (own: closer to that side's spawn), with the gold earned from them, gems earned, and the share of the group's reward the champion took. Then the same by champion type. Shows which
groups a richer rival takes that we leave.
"""
import collections, json, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

args = sys.argv[1:]
maps = None
if '--maps' in args:
    k = args.index('--maps')
    maps = set(args[k + 1].split(','))
    del args[k:k + 2]
R, dirs = int(args[0]), args[1:]
MI = json.load(open('data/map_info.json', encoding='utf-8'))
KIND = {0: 'wolf', 1: 'elk', 2: 'gem', 3: 'gold', 4: 'mono', 5: 'golem'}
ORDER = {'mono': 5, 'golem': 4, 'elk': 3, 'wolf': 2, 'gem': 1, 'gold': 0}
T = collections.defaultdict(collections.Counter)
Y = collections.defaultdict(collections.Counter)
games = 0
for us, res, mp, meta, rows in D.games(dirs):
    if maps is not None and mp not in maps:
        continue
    info = MI.get(mp)
    if not info:
        continue
    games += 1
    tiles = {}
    for g in info['G']:
        kinds = [KIND[c[0]] for c in g['camps']]
        kind = max(kinds, key=lambda x: ORDER[x]) if kinds else 'gold'
        for c in g['camps']:
            tiles[(c[1], c[2])] = (g, kind)
    n = len(rows[0]['c'])
    held = [0] * n
    prev = None
    for x in rows:
        if x['r'] > R:
            break
        for i in range(n):
            c = x['c'][i]
            g = D.gold_held(meta, c)
            if prev is not None:
                p = prev['c'][i]
                dgold = g - held[i]
                dgem = c.get('g', 0) - p.get('g', 0)
                if (dgold > 0 or dgem > 0) and c['a'] and p['a'] and c.get('k', 0) == p.get('k', 0):
                    best, bd = None, 4
                    for (tx, ty), v in tiles.items():
                        d = max(abs(tx - c['x']), abs(ty - c['y']))
                        if d < bd:
                            best, bd = v, d
                    if best is not None:
                        grp, kind = best
                        w = D.who(c['t'], us)
                        # team 0 is the map_info's view: sd = walk from team 0's spawn, ed = from the other.
                        own = (grp['sd'] <= grp['ed']) if c['t'] == 0 else (grp['ed'] <= grp['sd'])
                        k = (kind, 'own' if own else 'far')
                        t = T[w]
                        t[k + ('n',)] += 1
                        t[k + ('gold',)] += max(0, dgold)
                        t[k + ('gems',)] += max(0, dgem)
                        y = Y[(D.NAMES[c['ty']], w)]
                        y[kind] += 1
                        y[kind + '_gold'] += max(0, dgold)
            held[i] = g
        prev = x
k = max(1, games)
print(f'{games} games to r{R}; per game, us then them: rises, gold, gems')
for kind in ('gold', 'gem', 'wolf', 'elk', 'golem', 'mono'):
    for half in ('own', 'far'):
        u, t = T['us'], T['them']
        a = (kind, half)
        if u[a + ('n',)] + t[a + ('n',)] == 0:
            continue
        print(f"  {kind:6s}{half:4s} {u[a + ('n',)] / k:5.1f} /{t[a + ('n',)] / k:5.1f}   gold {u[a + ('gold',)] / k:5.0f} /{t[a + ('gold',)] / k:5.0f}   gems {u[a + ('gems',)] / k:5.0f} /{t[a + ('gems',)] / k:5.0f}")
print('by type, gold from each kind a game (us then them)')
for ty in D.NAMES:
    for w in ('us', 'them'):
        y = Y.get((ty, w))
        if not y:
            continue
        print(f"  {ty:9s}{w:5s}" + ' '.join(f"{kind} {y[kind + '_gold'] / k:4.0f}" for kind in ('gold', 'gem', 'wolf', 'elk', 'golem', 'mono')))
