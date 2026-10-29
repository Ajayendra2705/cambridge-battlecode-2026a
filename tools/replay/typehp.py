# Per champion type, by round: max health of the living champions, gold held (unspent + 30 per shard owned) and the gold
# of it in health items, us vs them; games with N champions a side only (default 5).
# usage: python -I tools/replay/typehp.py [--size N] [--rounds 200,300,400,600] DIR...
import collections, sys
sys.path.insert(0, 'tools/replay')
from decoded import games, who, gold_held, item_name, NAMES
SIZE, RS, args = 5, (200, 300, 400, 600), sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--size': SIZE = int(args[1])
    elif args[0] == '--rounds': RS = tuple(int(x) for x in args[1].split(','))
    args = args[2:]
E = collections.Counter(); ng = 0
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 2 * SIZE: continue
    ng += 1
    for R in RS:
        row = next((r for r in rows if r['r'] >= R), None)
        if not row: continue
        for c in row['c']:
            if not c.get('a') or not c.get('mhp'): continue
            k = (NAMES[c['ty']], who(c['t'], us), R)
            E[k] += 1; E[k + ('mhp',)] += c['mhp']; E[k + ('held',)] += gold_held(meta, c)
            for it, cnt in c.get('it', []):
                name = item_name(meta, it)
                if '_hp' in name: E[k + ('hp',)] += 30 * cnt * (5 if name.endswith('emblem') else 1)
print(f'{ng} games with {SIZE} a side: per living champion, max health / gold held / gold in health items')
for ty in sorted(set(k[0] for k in E if len(k) == 3)):
    for w in ('us', 'them'):
        if not any(E[(ty, w, R)] for R in RS): continue
        cells = []
        for R in RS:
            k = (ty, w, R); n = E[k]
            cells.append(f'r{R} {E[k + ("mhp",)] / n:5.0f} {E[k + ("held",)] / n:4.0f} {E[k + ("hp",)] / n:4.0f}' if n else f'r{R}     -')
        print(f'  {ty:9} {w:4} ' + '  '.join(cells))
