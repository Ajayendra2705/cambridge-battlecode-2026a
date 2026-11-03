"""How losses end: python -I tools/replay/lastrace.py DIR [DIR ...]

For each lost game, our tributed gems at the end and our gems in hand (tributed plus bags). Prints losses by how near we
were (behind by under 50, 100, 200, 400 tributed; held enough in hand to have won), the rivals' last channel (its bag, how
long it ran, the distance from it to our nearest living champion when it started), and the same for wins with the sides
swapped. A last-channel fix (altar lock, stun) can only flip a loss where we were close, so this sizes it before any code.
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

dirs = sys.argv[1:]
N = collections.Counter()
BAG = collections.Counter()
near = collections.Counter()
rows_out = []
held = []
for us, res, mp, meta, rows in D.games(dirs):
    N['games'] += 1
    last = rows[-1]
    end = last['r']
    su, st = last['sg'][us], last['sg'][1 - us]
    hand_u = su + sum(c.get('g', 0) for c in last['c'] if c['t'] == us)
    win = res == 'win'
    N['win' if win else 'loss'] += 1
    if end >= 1999:
        N['r2000_win' if win else 'r2000_loss'] += 1
    if win:
        continue
    gap = max(st, 1000) - su
    for cut in (50, 100, 200, 400):
        if gap < cut:
            N[f'loss_gap<{cut}'] += 1
    if hand_u >= 1000:
        N['loss_held_1000_in_hand'] += 1
    # Gems in hand: the first round we held 1000, how long before the end, and our biggest bag then.
    for x in rows:
        h = x['sg'][us] + sum(c.get('g', 0) for c in x['c'] if c['t'] == us)
        if h >= 1000:
            bags = sorted((c.get('g', 0) for c in x['c'] if c['t'] == us), reverse=True)
            held.append((end - x['r'], mp, x['r'], end, x['sg'][us], bags[:3], last['sg'][us], last['sg'][1 - us]))
            break
    if end >= 1999:
        continue
    # The rivals' last channel: walk back from the end while their winning champion stays channelling.
    bag = 0
    who_i = None
    for i, c in enumerate(rows[-2]['c'] if len(rows) > 1 else last['c']):
        if c['t'] == 1 - us and c.get('g', 0) > bag:
            bag = c.get('g', 0)
            who_i = i
    BAG['n'] += 1
    b = '<10' if bag < 10 else '<30' if bag < 30 else '<60' if bag < 60 else '<120' if bag < 120 else '120+'
    BAG[b] += 1
    if who_i is None:
        continue
    # Channel start: the first round of the final run in which that champion stayed within 1 of its last tile.
    pos = (rows[-2]['c'][who_i]['x'], rows[-2]['c'][who_i]['y'])
    start = len(rows) - 2
    while start > 0:
        q = (rows[start - 1]['c'][who_i]['x'], rows[start - 1]['c'][who_i]['y'])
        if q != pos:
            break
        start -= 1
    x = rows[start]
    dn = 99
    for c in x['c']:
        if c['t'] == us and c.get('a'):
            dn = min(dn, D.dist((c['x'], c['y']), pos))
    k = '<=2' if dn <= 2 else '<=4' if dn <= 4 else '<=6' if dn <= 6 else '<=8' if dn <= 8 else '>8'
    near[k] += 1
    near['len_sum'] += len(rows) - 1 - start
    near['n'] += 1
    rows_out.append((gap, mp, bag, dn, len(rows) - 1 - start, su, st, end))

print(f"games {N['games']}, wins {N['win']}, losses {N['loss']}; ended at r2000: wins {N['r2000_win']}, losses {N['r2000_loss']}")
print('losses by final tributed gap:', {k: N[k] for k in sorted(N) if k.startswith('loss_gap')})
print('losses with 1000 in hand at the end:', N['loss_held_1000_in_hand'])
print("rivals' last bag (losses before r2000):", {k: BAG[k] for k in ('<10', '<30', '<60', '<120', '120+')}, 'of', BAG['n'])
if near['n']:
    print('our nearest champion when that channel started:', {k: near[k] for k in ('<=2', '<=4', '<=6', '<=8', '>8')}, 'mean channel rounds', round(near['len_sum'] / near['n'], 1))
held.sort(reverse=True)
print('losses that once held 1000 in hand:', len(held))
print('  rounds from then to the end, map, round, end, tributed then, biggest bags then, final ours, final theirs:')
for r in held[:40]:
    print('   ', r)
rows_out.sort()
print('closest losses (gap, map, last bag, our nearest, channel rounds, ours, theirs, end):')
for r in rows_out[:25]:
    print(' ', r)
