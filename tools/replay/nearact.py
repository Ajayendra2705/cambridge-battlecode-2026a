"""What champions do with an enemy champion near, early in the game, us vs the rivals.

usage: python -I tools/replay/nearact.py DIR [DIR ...] [--round R] [--upto D]   (defaults: to r150, enemy within 8)

Per alive champion-round with its nearest enemy champion within D, by that distance (1-3, 4-5, 6-8): share hitting a
champion, hitting a camp, stepping closer to the nearest enemy, stepping away, other move, standing; and gold earned and
deaths per 100 such rounds. By numbers within 8 too (we outnumber, even, outnumbered), and per champion type in the 1-3 band.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

args = sys.argv[1:]
R, U = 150, 8
if '--round' in args:
    k = args.index('--round'); R = int(args[k + 1]); del args[k:k + 2]
if '--upto' in args:
    k = args.index('--upto'); U = int(args[k + 1]); del args[k:k + 2]
C = collections.Counter()
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        al = [(i, c) for i, c in enumerate(a['c']) if c['a'] and 'x' in c]
        for i, c in al:
            t = c['t']; p = (c['x'], c['y'])
            es = [(D.dist(p, (o['x'], o['y'])), j) for j, o in al if o['t'] != t]
            if not es: continue
            d, j = min(es)
            w = D.who(t, us)
            if d > U: 
                C[(w, 'far', 'n')] += 1
                nc = b['c'][i]
                if D.camp_hits(a, i): C[(w, 'far', 'camp')] += 1
                if nc['a'] and c['a']: C[(w, 'far', 'gold')] += max(0, D.gold_held(meta, nc) - D.gold_held(meta, c))
                continue
            band = '1-3' if d <= 3 else '4-5' if d <= 5 else '6-8'
            ne = sum(1 for x, o in al if o['t'] != t and D.dist(p, (o['x'], o['y'])) <= 8)
            na = sum(1 for x, o in al if o['t'] == t and D.dist(p, (o['x'], o['y'])) <= 8)
            num = 'outnumber' if na > ne else 'even' if na == ne else 'outnumbered'
            nc = b['c'][i]
            q = (nc['x'], nc['y']) if nc['a'] and 'x' in nc else p
            jc = a['c'][j]; dd = D.dist(q, (jc['x'], jc['y'])) - d
            kind = 'hitc' if D.enemy_hits(a, i, n) else 'camp' if D.camp_hits(a, i) else 'closer' if dd < 0 else 'away' if dd > 0 else 'moved' if q != p else 'still'
            keys = (band, num) + (('1-3 ' + D.NAMES[c['ty']][:8],) if band == '1-3' else ())
            for key in keys:
                C[(w, key, 'n')] += 1; C[(w, key, kind)] += 1
                if not nc['a']: C[(w, key, 'dead')] += 1
                else: C[(w, key, 'gold')] += max(0, D.gold_held(meta, nc) - D.gold_held(meta, c))
types = sorted({k[1] for k in C if k[1].startswith('1-3 ')})
for key in ['1-3', '4-5', '6-8', 'outnumber', 'even', 'outnumbered', 'far'] + types:
    for w in ('us', 'them'):
        m = max(1, C[(w, key, 'n')])
        print(f'{key:12}{w:5} rounds {C[(w, key, "n")]:6} | ' + ' '.join(f'{k} {C[(w, key, k)] / m:.2f}' for k in ('hitc', 'camp', 'closer', 'away', 'moved', 'still')) +
              f' | gold/100r {100 * C[(w, key, "gold")] / m:5.1f} deaths/100r {100 * C[(w, key, "dead")] / m:.2f}')
