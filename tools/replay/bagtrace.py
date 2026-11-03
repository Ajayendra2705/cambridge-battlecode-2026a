"""What did the carrier do with a winning bag? python -I tools/replay/bagtrace.py DIR [MAXGAMES] [--skip MAP]

For lost games that once held a bag lifting our tributed gems to 1000: from the first such round to the end, one line a
round for the carrier: position, health, bag, its actions, the nearest altar tile distance (from `altars` in
data/map_info.json), the nearest enemy, and whether it channels. Ends with a count of the rounds by what the carrier did.
"""
import collections, json, os, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

args = sys.argv[1:]
skip = []
while '--skip' in args:
    k = args.index('--skip')
    skip.append(args[k + 1])
    del args[k:k + 2]
d = args[0]
maxg = int(args[1]) if len(args) > 1 else 12
info = json.load(open('data/map_info.json', encoding='utf-8')) if os.path.exists('data/map_info.json') else {}
TOT = collections.Counter()
shown = 0
games = 0
for us, res, mp, meta, rows in D.games([d]):
    if res == 'win' or any(s in mp for s in skip):
        continue
    first = None
    for k, x in enumerate(rows):
        su = x['sg'][us]
        for i, c in enumerate(x['c']):
            if c['t'] == us and c.get('a') and c.get('g', 0) > 0 and su + c.get('g', 0) >= 1000:
                first = (k, i)
                break
        if first:
            break
    if not first:
        continue
    games += 1
    k0, i0 = first
    altars = (info.get(mp) or {}).get('A') or []
    if shown < maxg:
        print(f"\n{mp} side {'ab'[us]} first winning bag r{rows[k0]['r']} tributed {rows[k0]['sg'][us]} bag {rows[k0]['c'][i0].get('g', 0)} {D.NAMES[rows[k0]['c'][i0]['ty']]}; end r{rows[-1]['r']} final {rows[-1]['sg'][us]} / {rows[-1]['sg'][1 - us]}")
    for x in rows[k0:]:
        c = x['c'][i0]
        if not c.get('a') or 'x' not in c:
            TOT['dead'] += 1
            if shown < maxg:
                print(f"  r{x['r']} dead")
                break
            continue
        pos = (c['x'], c['y'])
        acts = x['act'][i0] if i0 < len(x['act']) else []
        names = [a[0] for a in acts]
        ne = 99
        for o in x['c']:
            if o['t'] != us and o.get('a') and 'x' in o:
                ne = min(ne, D.dist((o['x'], o['y']), pos))
        da = min((D.dist(pos, tuple(a)) for a in altars), default=-1)
        kind = 'tribute' if 'submit' in names or 'tribute' in names else 'hit' if ('attack' in names or 'cast' in names) else 'move' if 'move' in names else 'idle'
        TOT[kind] += 1
        if shown < maxg and x['r'] - rows[k0]['r'] < 45:
            print(f"  r{x['r']} {pos} hp {c['hp']}/{c['mhp']} bag {c.get('g', 0)} altar {da} enemy {ne} {names}")
    shown += 1
print('\ngames', games, 'carrier rounds by kind', dict(TOT))
