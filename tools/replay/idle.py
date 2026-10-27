"""Idle champion-rounds by kind, us vs the rivals, per 100 alive champion-rounds to round 1000.

usage: python -I tools/replay/idle.py DIR [DIR ...] [--maps]

A champion is idle in a round when it is alive, ends on the same tile and logged no action, outside 3 tiles of its
start tile. Kinds, in order: chan (inside a tribute channel: bag / 10 rounds after the tribute action while the bag
holds), wait (on or next to a dead camp: respawn waits and holds), cool (next to a live camp: between hits), foe (an
enemy champion within 4), other (none of these: walking nowhere, waiting for teammates, stuck). Camp tiles are those
some champion hit in the game. --maps prints one line per map, largest gap in "other" first. DIR is a decoded folder
(tools/replay/decode_run.sh, tools/local/local_decode.sh).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

KINDS = ('chan', 'wait', 'cool', 'foe', 'other')
permap = '--maps' in sys.argv
A = collections.defaultdict(collections.Counter)
seen = set()
for us, res, mp, meta, rows in D.games([a for a in sys.argv[1:] if not a.startswith('--')]):
    if meta['file'] in seen: continue
    seen.add(meta['file'])
    n = len(rows[0]['c'])
    cpos = {}
    for r in rows:
        for i in range(min(n, len(r.get('act', [])))):
            for x in D.camp_hits(r, i): cpos[(x[-4], x[-3])] = x[-1]
    start = {i: (rows[0]['c'][i].get('x'), rows[0]['c'][i].get('y')) for i in range(n)}
    C = A[mp if permap else 'all']
    C['games'] += 1
    chan = collections.Counter()
    for k in range(1, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            p, c = a['c'][i], b['c'][i]
            acts = a['act'][i] if i < len(a['act']) else []
            if not (p['a'] and c['a'] and 'x' in p and 'x' in c):
                chan[i] = 0
                continue
            w = D.who(p['t'], us)
            C[w + ' alive'] += 1
            if any(x[0] == 'tribute' for x in acts) and p.get('g', 0) > 0: chan[i] = -(-p['g'] // 10) + 1
            if chan[i] > 0:
                chan[i] -= 1
                if c.get('g', 0) == p.get('g', 0):
                    C[w + ' chan'] += 1
                    continue
                chan[i] = 0
            if (p['x'], p['y']) != (c['x'], c['y']) or acts: continue
            if abs(p['x'] - start[i][0]) <= 3 and abs(p['y'] - start[i][1]) <= 3: continue
            near = [cpos[(p['x'] + dx, p['y'] + dy)] for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (p['x'] + dx, p['y'] + dy) in cpos]
            foe = any(o['a'] and 'x' in o and o['t'] != p['t'] and D.dist((p['x'], p['y']), (o['x'], o['y'])) <= 4 for o in a['c'])
            if any(j < len(a['mh']) and a['mh'][j] == 0 for j in near): kind = 'wait'
            elif near: kind = 'cool'
            elif foe: kind = 'foe'
            else: kind = 'other'
            C[w + ' ' + kind] += 1
print('idle per 100 alive champion-rounds to r1000, us / them')
out = []
for key, C in A.items():
    f = lambda w, k: 100 * C[w + ' ' + k] / max(1, C[w + ' alive'])
    out.append((f('us', 'other') - f('them', 'other'), key, C, f))
for d, key, C, f in sorted(out, key=lambda t: -t[0]):
    print(f"  {key:24} {C['games']:3} games  " + '  '.join(f"{k} {f('us', k):4.1f}/{f('them', k):4.1f}" for k in KINDS))
