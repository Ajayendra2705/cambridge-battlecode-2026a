"""Per map: our games against the rivals' in the same decoded runs: python -I tools/replay/mapgold.py DIR [DIR ...] [--min N]

DIR are folders written by tools/replay/decode_run.sh. For each map: games, wins, then us / them at r300 for team gold held (unspent + 30 per shard), deaths to r300,
gems collected to r1000, deaths to r1000, the share of living champion-rounds to r300 with no move and no hit (still), and the first round any champion of a team
hits a camp. Sorted by wins, then gold ratio. A map with low gold and high still points at a bot fault on that map (a freeze), not at a lost fight.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
D.SKIP = []
args = sys.argv[1:]
MIN = 1
if '--min' in args:
    k = args.index('--min'); MIN = int(args[k + 1]); del args[k:k + 2]
A = collections.defaultdict(lambda: collections.Counter())
for us, res, mp, meta, rows in D.games(args):
    a = A[mp]
    a['n'] += 1
    a['w'] += res == 'win'
    n = len(rows[0]['c'])
    fc = {0: None, 1: None}
    prev = None
    for r in rows:
        R = r['r']
        if R > 1000:
            break
        for i, c in enumerate(r['c']):
            w = D.who(c['t'], us)
            if prev is not None:
                pc = prev['c'][i]
                if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0):
                    a['coll_' + w] += c['g'] - pc['g']
                if pc['a'] and not c['a']:
                    a['d1000_' + w] += 1
                    if R <= 300:
                        a['d300_' + w] += 1
            if R <= 300 and c['a']:
                acts = r['act'][i] if i < len(r['act']) else []
                a['live_' + w] += 1
                if not acts:
                    a['still_' + w] += 1
            if fc[c['t']] is None and D.camp_hits(r, i):
                fc[c['t']] = R
        if R == 300:
            for c in r['c']:
                a['gold_' + D.who(c['t'], us)] += D.gold_held(meta, c)
            a['n300'] += 1
        prev = r
    for t, v in fc.items():
        if v is not None:
            a['fc_' + D.who(t, us)] += v
            a['fcn_' + D.who(t, us)] += 1
print('map                      n  win | gold r300 us/them | deaths r300 | collected r1000 | deaths r1000 | still r300 | first camp hit')
rows = []
for mp, a in A.items():
    if a['n'] < MIN:
        continue
    n = a['n']; g = max(1, a['n300'])
    gu, gt = a['gold_us'] / g, a['gold_them'] / g
    rows.append((a['w'] / n, gu / max(1, gt), mp, n, a, gu, gt))
for wr, ratio, mp, n, a, gu, gt in sorted(rows, key=lambda x: (x[0], x[1])):
    print(f"{mp:24} {n:2} {a['w']:3}  | {gu:5.0f}/{gt:5.0f} {ratio:4.2f} | {a['d300_us'] / n:4.1f}/{a['d300_them'] / n:4.1f} | {a['coll_us'] / n:4.0f}/{a['coll_them'] / n:4.0f} | {a['d1000_us'] / n:4.1f}/{a['d1000_them'] / n:4.1f} | "
          f"{a['still_us'] / max(1, a['live_us']):.2f}/{a['still_them'] / max(1, a['live_them']):.2f} | {a['fc_us'] / max(1, a['fcn_us']):3.0f}/{a['fc_them'] / max(1, a['fcn_them']):3.0f}")
