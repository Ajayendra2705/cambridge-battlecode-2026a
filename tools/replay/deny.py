# The rivals' winning channel in games we lost before r2000: the carrier, channel length, and our nearest living
# champion's distance at the channel start and its minimum during the channel; also how far our nearest was while the
# carrier walked with its winning bag. python -I deny.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
H = collections.Counter(); seen = set(); W = []
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    key = (mp, meta['rounds'], tuple(meta['submittedGems']))
    if key in seen or res != 'loss' or meta['rounds'] >= 2000: continue
    seen.add(key)
    th = 1 - us
    # the last tribute start of a rival whose bag alone wins
    start = None
    for k, r in enumerate(rows):
        for i, c in enumerate(r['c']):
            if c['t'] != th or not c.get('a'): continue
            acts = r['act'][i] if i < len(r['act']) else []
            if any(x[0] == 'tribute' for x in acts) and r['sg'][th] + c.get('g', 0) >= 1000: start = (k, i)
    if not start: H['no winning channel found'] += 1; continue
    k, i = start
    car = rows[k]['c'][i]
    def near(r):
        c = r['c'][i]
        ds = [max(abs(o['x'] - c['x']), abs(o['y'] - c['y'])) for o in r['c'] if o['t'] == us and o.get('a') and 'x' in o and 'x' in c]
        return min(ds) if ds else 99
    d0 = near(rows[k]); dmin = min(near(r) for r in rows[k:])
    # walk phase: from the first round with a winning bag
    k0 = next(j for j, r in enumerate(rows) if r['c'][i].get('a') and r['sg'][th] + r['c'][i].get('g', 0) >= 1000 and r['sg'][th] < 1000) if True else k
    dwalk = min(near(r) for r in rows[k0:k + 1])
    H['games'] += 1
    for lim in (2, 4, 6, 8):
        if d0 <= lim: H[f'start within {lim}'] += 1
        if dmin <= lim: H[f'channel within {lim}'] += 1
        if dwalk <= lim: H[f'walk+channel within {lim}'] += 1
    W.append((mp, rows[k]['r'], car.get('g'), len(rows) - k, d0, dmin, dwalk))
print(dict(H))
for w in W[:40]: print('  %s r%d bag %s rounds-left %d nearest at start %d, min in channel %d, min from winning bag %d' % w)
