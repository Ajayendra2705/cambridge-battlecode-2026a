# Contact rounds, to r1000 (or --upto=R): a champion alive with an enemy champion (spawn tiles not excluded) within
# its basic reach + 1 at the round start. What it did that round: hit a champion, hit a camp only, moved closer to the
# nearest enemy, level, away, or nothing; per side, by melee / ranged and per type; per game.
# usage: python -I tools/replay/fs_contact.py [--upto=R] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist, RANGE, NAMES, enemy_hits, camp_hits
UPTO = 1000
args = sys.argv[1:]
if args and args[0].startswith('--upto='): UPTO = int(args[0][7:]); args = args[1:]
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(args):
    ng += 1; n = len(rows[0]['c'])
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if a['r'] > UPTO: break
        for i in range(n):
            c = a['c'][i]
            if not c['a'] or 'x' not in c: continue
            q = (c['x'], c['y']); rg = RANGE.get(c['ty'], 1)
            ens = [(dist(q, (o['x'], o['y'])), j) for j, o in enumerate(a['c']) if o['t'] != c['t'] and o['a'] and 'x' in o]
            if not ens: continue
            d0, j0 = min(ens)
            if d0 > rg + 1: continue
            acts = a['act'][i] if i < len(a['act']) else []
            if enemy_hits(a, i, n): kind = 'hit champion'
            else:
                mv = [x for x in acts if x[0] == 'move']
                nb = b['c'][i]
                if mv and nb['a'] and 'x' in nb:
                    q1 = (mv[-1][3], mv[-1][4])
                    o = a['c'][j0]; d1 = dist(q1, (o['x'], o['y']))
                    kind = 'move closer' if d1 < d0 else 'move away' if d1 > d0 else 'move level'
                elif camp_hits(a, i): kind = 'hit camp only'
                elif any(x[0] in ('cast',) for x in acts): kind = 'cast other'
                else: kind = 'nothing'
            w = who(c['t'], us)
            cls = 'melee' if rg == 1 else 'ranged'
            for key in (cls + ' d' + str(min(d0, rg + 1)), NAMES[c['ty']] + ' d' + str(min(d0, rg + 1))):
                E[(w, key, kind)] += 1; E[(w, key)] += 1
kinds = ('hit champion', 'hit camp only', 'move closer', 'move level', 'move away', 'cast other', 'nothing')
print(f'{ng} games to r{UPTO}: contact rounds (nearest enemy champion within reach + 1 at round start), per game, and shares')
for key in sorted(set(k[1] for k in E if len(k) == 2), key=lambda s: (not s.startswith(('melee', 'ranged')), s)):
    for w in ('us', 'them'):
        t = E[(w, key)]
        if t < ng * 0.5: continue
        print(f'  {key:13} {w:4} {t / ng:6.1f}/g  ' + '  '.join(f'{kd.split()[-1][:6]} {E[(w, key, kd)] / t:.2f}' for kd in kinds))
