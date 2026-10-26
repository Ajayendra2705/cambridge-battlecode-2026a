"""Games where we feed deaths: python -I tools/replay/massacre.py DIR... [--min 12]   (run from the repo root)

A massacre is a game with at least MIN of our deaths (default 12) and at least 2.5 times the enemy's. Per massacre: map,
result, deaths us/them, deaths per 250-round band, zone of each death (own half / middle / enemy half, by walking
distance from the two spawns), the mean enemies and allies within 6 at the death, the share of deaths with no ally
within 6, and the share at a repeat spot (within 6 tiles of one of our deaths in the 150 rounds before). Then the same
shares over all our deaths in the other games, for comparison.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
args = sys.argv[1:]
MIN = 12
if '--min' in args:
    j = args.index('--min'); MIN = int(args[j + 1]); args = args[:j] + args[j + 2:]
agg = {'massacre': collections.Counter(), 'other': collections.Counter()}
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    deaths = []; theirs = 0
    for k in range(1, len(rows)):
        a, b = rows[k - 1], rows[k]
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if not pc['a'] or c['a'] or 'x' not in pc: continue
            if pc['t'] != us: theirs += 1; continue
            p = (pc['x'], pc['y'])
            e6 = sum(1 for o in a['c'] if o['a'] and 'x' in o and o['t'] != us and D.dist((o['x'], o['y']), p) <= 6)
            a6 = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == us and D.dist((o['x'], o['y']), p) <= 6)
            do = min(D.dist(p, q) for q in start[us]); de = min(D.dist(p, q) for q in start[1 - us])
            zone = 'own' if do < de - 3 else 'enemy' if de < do - 3 else 'middle'
            repeat = any(b['r'] - r0 <= 150 and D.dist(p, q) <= 6 for r0, q in ((d[0], d[1]) for d in deaths))
            deaths.append((b['r'], p, zone, e6, a6, repeat, D.NAMES[pc['ty']]))
    kind = 'massacre' if len(deaths) >= MIN and len(deaths) >= 2.5 * max(1, theirs) else 'other'
    A = agg[kind]
    A['games'] += 1; A['deaths'] += len(deaths); A['their deaths'] += theirs
    for r, p, zone, e6, a6, repeat, ty in deaths:
        A[zone] += 1; A['e6'] += e6; A['a6'] += a6; A['alone'] += a6 == 0; A['repeat'] += repeat
    if kind == 'massacre':
        bands = collections.Counter(min(3, r // 250) for r, *_ in deaths)
        z = collections.Counter(d[2] for d in deaths)
        nd = len(deaths)
        print(f'{mp:24} {res:4} deaths {nd:2}/{theirs:<2} first r{deaths[0][0]:<4} by band r0-249/250-499/500-749/750+: '
              f'{bands[0]}/{bands[1]}/{bands[2]}/{bands[3]}  zone own/mid/enemy {z["own"]}/{z["middle"]}/{z["enemy"]}  '
              f'e6 {sum(d[3] for d in deaths) / nd:.1f} a6 {sum(d[4] for d in deaths) / nd:.1f}  alone {sum(d[4] == 0 for d in deaths) / nd:.0%}  '
              f'repeat {sum(d[5] for d in deaths) / nd:.0%}  types ' + ','.join(f'{t[:4]}{c}' for t, c in collections.Counter(d[6] for d in deaths).most_common()))
for kind, A in agg.items():
    nd = max(1, A['deaths'])
    print(f'{kind:8}: {A["games"]} games, our deaths {A["deaths"] / max(1, A["games"]):.1f} per game (theirs {A["their deaths"] / max(1, A["games"]):.1f}); '
          f'zone own/mid/enemy {A["own"] / nd:.0%}/{A["middle"] / nd:.0%}/{A["enemy"] / nd:.0%}; enemies within 6 {A["e6"] / nd:.1f}, allies {A["a6"] / nd:.1f}; '
          f'alone {A["alone"] / nd:.0%}; repeat spot {A["repeat"] / nd:.0%}')
