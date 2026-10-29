# All champions, 5-a-side games, to r1000, off spawns, rounds where the champion's side has the numbers near it (enemies
# within 5 >= 1 and allies within 5 >= enemies within 5): by the nearest enemy distance (1, 2, 3, 4, 5) and melee / ranged,
# rounds per game, the share hitting an enemy champion, walking closer / level / away, hitting a camp, nothing; by side.
# usage: python -I tools/replay/withnumbers.py DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist, enemy_hits, camp_hits
args = sys.argv[1:]
MELEE = {NAMES.index(x) for x in ('heart', 'marcella', 'vendetta', 'ryth', 'varg', 'ren', 'issac') if x in NAMES}
R = {w: collections.Counter() for w in ('us', 'them')}; G = collections.Counter()
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 10: continue
    G['g'] += 1
    spawn = {t: set(pos(c) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    for r in range(len(rows) - 1):
        if rows[r]['r'] > 1000: break
        row, nx = rows[r], rows[r + 1]
        for i, c in enumerate(row['c']):
            if not c['a'] or 'x' not in c: continue
            p = pos(c)
            if any(dist(p, s) <= 2 for s in spawn[0] | spawn[1]): continue
            ens = [e for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t'] and dist(p, pos(e)) <= 5 and pos(e) not in spawn[e['t']]]
            if not ens: continue
            al = sum(1 for j, e in enumerate(row['c']) if j != i and e['a'] and 'x' in e and e['t'] == c['t'] and dist(p, pos(e)) <= 5)
            if al < len(ens): continue
            e = min(ens, key=lambda e: dist(p, pos(e))); dn = dist(p, pos(e))
            kind = 'melee' if c['ty'] in MELEE else 'ranged'
            if enemy_hits(row, i, 10): what = 'hit champ'
            elif camp_hits(row, i): what = 'hit camp'
            else:
                n2 = nx['c'][i]
                if n2['a'] and 'x' in n2 and pos(n2) != p:
                    dd = dist(pos(n2), pos(e)) - dn
                    what = 'closer' if dd < 0 else 'away' if dd > 0 else 'level'
                else: what = 'nothing'
            X = R[who(c['t'], us)]
            X[(kind, dn)] += 1; X[(kind, dn, what)] += 1
W = ('hit champ', 'closer', 'level', 'away', 'hit camp', 'nothing')
print(f"5-a-side, to r1000, {G['g']} games, champion with the numbers near it: rounds/game and action shares")
print('  kind   d  side   rnd/g  ' + '  '.join(f'{w:>9}' for w in W))
for kind in ('melee', 'ranged'):
    for dn in range(1, 6):
        for w in ('us', 'them'):
            X = R[w]; n = X[(kind, dn)]
            print(f"  {kind:6} {dn}  {w:4}  {n / G['g']:6.1f}  " + '  '.join(f'{X[(kind, dn, a)] / max(1, n):9.2f}' for a in W))
