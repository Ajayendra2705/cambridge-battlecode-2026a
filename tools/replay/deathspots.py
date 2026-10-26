"""Our deaths on one map: python -I tools/replay/deathspots.py MAP DIR...
Per death: round, champion type, position, health 10 rounds before, enemies and allies within 5 at death, where it was
10 rounds before and how far from our spawn, whether it was hit by an enemy champion in its last 5 rounds.
"""
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

MAP = sys.argv[1]
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    if MAP not in mp: continue
    n = len(rows[0]['c'])
    start = [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == us]
    print(f'== {mp} {res} rounds {rows[-1]["r"]}')
    for k in range(1, len(rows)):
        a, b = rows[k - 1], rows[k]
        for i in range(n):
            c, pc = b['c'][i], a['c'][i]
            if c['t'] != us or not pc['a'] or c['a'] or 'x' not in pc: continue
            p = (pc['x'], pc['y'])
            e5 = sum(1 for o in a['c'] if o['a'] and 'x' in o and o['t'] != us and D.dist((o['x'], o['y']), p) <= 5)
            a5 = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == us and D.dist((o['x'], o['y']), p) <= 5)
            back = rows[max(0, k - 10)]['c'][i]
            bp = (back['x'], back['y']) if back['a'] and 'x' in back else None
            hits = sum(1 for r in rows[max(0, k - 5):k] for e in range(n) for x in D.enemy_hits(r, e, n) if x[-1] == i)
            print(f'  r{b["r"]:4} {D.NAMES[c["ty"]]:8} at {p} home {min(D.dist(p, q) for q in start):2}  '
                  f'enemies<=5 {e5} allies<=5 {a5}  10 before {bp} hp {int(100 * back["hp"] / max(1, back["mhp"])) if bp else "-"}%  hits taken 5r {hits}')
