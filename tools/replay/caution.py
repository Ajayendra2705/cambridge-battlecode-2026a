"""Games where our team dies fast, against the rest, to r1000: python -I tools/replay/caution.py [--early] DIR...
DIRs are decoded runs (data/fights/RUN_PANEL). A game counts as a caution game once our deaths reach 3 + one per 100
rounds after r200 (ow1's trigger; with --early 2 + one per 100 after r100, ow4's) at some round to r1000. Prints, per group:
games, wins, and per game our and their deaths, collected and tributed gems to r1000, and our deaths after the trigger."""
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
args = sys.argv[1:]
early = '--early' in args
dirs = [a for a in args if a != '--early']
bar = (lambda r: 2 + max(0, (r - 100) // 100)) if early else (lambda r: 3 + max(0, (r - 200) // 100))
A = collections.defaultdict(collections.Counter)
for us, res, mp, meta, rows in D.games(dirs):
    dd = collections.Counter(); col = collections.Counter(); fire = None; after = 0; last = rows[0]
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        last = b
        for i, c in enumerate(b['c']):
            pc = a['c'][i]; w = D.who(c['t'], us)
            if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): col[w] += c['g'] - pc['g']
            if pc['a'] and not c['a']:
                dd[w] += 1
                if w == 'us' and fire is not None: after += 1
        if fire is None and dd['us'] >= bar(b['r']): fire = b['r']
    k = 'caution' if fire is not None else 'rest'
    A[k]['games'] += 1; A[k]['won'] += res == 'win'; A[k]['after'] += after
    for w in ('us', 'them'):
        A[k][w + ' deaths'] += dd[w]; A[k][w + ' coll'] += col[w]
    for t in (0, 1): A[k][D.who(t, us) + ' trib'] += last['sg'][t]
for k in ('caution', 'rest'):
    g = max(1, A[k]['games'])
    print(f"{k:8} games {A[k]['games']:3} won {A[k]['won']:3} | " + ' '.join(f"{x} {A[k][x] / g:.2f}" for x in
          ('us deaths', 'them deaths', 'us coll', 'them coll', 'us trib', 'them trib')) + f" | our deaths after the trigger {A[k]['after'] / g:.2f}")
