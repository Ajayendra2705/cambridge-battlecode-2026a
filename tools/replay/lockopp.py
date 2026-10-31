# Altar-lock denial, both sides, to r1000: (1) the rival tribute channels (bag >= MIN, default 30) by how near one of
# the side's champions came to the channel's altar while it ran (<=2: a lock can go down at once; 3-4; 5-6; far), with
# the gems in them and the share that still completed; (2) each side's broken channels (bag > 50) by cause: died,
# lock (the channeler hits an enemy altar lock afterwards), cast (an enemy cast on it), moved (it walked: a walk-off
# or an unseen cause), other. The lx1 metric (10-31).
# usage: [MIN=30] python -I tools/replay/lockopp.py DIR...
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
MIN = int(os.environ.get('MIN', '30'))
C = collections.Counter(); B = collections.Counter(); G = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    G += 1; n = len(rows[0]['c'])
    for k, b in enumerate(rows):
        if b['r'] > 1000: break
        for i, acts in enumerate(b['act'][:n]):
            tr = [x for x in acts if x[0] == 'tribute']
            c = b['c'][i]; g = c.get('g', 0)
            if not tr or g < min(MIN, 51): continue
            turns = max(1, -(-g // 10))
            if k + turns + 2 >= len(rows): continue
            ch = D.who(c['t'], us); altar = (tr[0][1], tr[0][2])
            ok = rows[k + turns + 2]['sg'][c['t']] - b['sg'][c['t']] >= g * 0.9
            if g >= MIN:
                best = 99
                for r in rows[k:k + turns]:
                    for o in r['c']:
                        if o['t'] != c['t'] and o['a'] and 'x' in o: best = min(best, D.dist(altar, (o['x'], o['y'])))
                band = '<=2' if best <= 2 else '3-4' if best <= 4 else '5-6' if best <= 6 else 'far'
                opp = 'them' if ch == 'us' else 'us'
                C[(opp, band, 'n')] += 1; C[(opp, band, 'g')] += g; C[(opp, band, 'ok')] += ok
            if g <= 50 or ok or b['sg'][c['t']] + g >= 1000: continue
            cause = 'other'
            for r in rows[k + 1:k + turns + 3]:
                if not r['c'][i]['a']: cause = 'died'; break
                ha = r['act'][i] if i < len(r['act']) else []
                if any(x[0] == 'attack' and len(x) == 3 for x in ha): cause = 'lock'; break
                if any(x[0] == 'cast' and x[-1] == i for e in range(n) for x in D.enemy_hits(r, e, n)): cause = 'cast'; break
                if any(x[0] == 'move' for x in ha): cause = 'moved'; break
            B[(ch, cause)] += 1; B[(ch, cause, 'g')] += g
print(f'{G} games')
for side in ('us', 'them'):
    print(f'{side}: rival channels (bag >= {MIN}) by our nearest distance to their altar, per game:')
    for band in ('<=2', '3-4', '5-6', 'far'):
        m = C[(side, band, 'n')]
        if m: print(f'   {band:4} channels {m / G:5.2f}  gems {C[(side, band, "g")] / G:6.1f}  completed {100 * C[(side, band, "ok")] / m:3.0f}%')
for side in ('us', 'them'):
    print(f'{side}: own broken channels (bag > 50) by cause, per game (channels, gems): ' +
          ', '.join(f'{c} {B[(side, c)] / G:.2f} ({B[(side, c, "g")] / G:.1f})' for c in ('lock', 'cast', 'died', 'moved', 'other')))
