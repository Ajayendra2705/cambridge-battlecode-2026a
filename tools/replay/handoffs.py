"""Capture hand-offs per champion type, us vs them (10-30, row vw1): for each capture to a round (default 600), the teammate
that hit the group most since it came up against the champion that captured it.

usage: python -I tools/replay/handoffs.py DIR [DIR ...] [--round R]

Per type and game: captures (with the capturer's gold), groups it hit most, how many of those a teammate captured ("handed",
with that gold), and captures of groups a teammate hit most ("took"). Per-game means divide by all games, so a type the
rivals pick in fewer games reads low (divide by its share of games). bb2's 150 pinned games: our Vesper handed 3.7 a game.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
R = 600
if '--round' in sys.argv:
    k = sys.argv.index('--round'); R = int(sys.argv[k + 1]); del sys.argv[k:k + 2]
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    hits = collections.defaultdict(collections.Counter)  # group -> champion index -> hits since up
    pending = set()
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i in range(n):
            for x in D.camp_hits(a, i):
                g = grp.get(x[-1])
                if g is not None: hits[g][i] += 1
        for g, js in members.items():
            if any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js): pending.add(g)
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            pending.discard(g)
            w = D.who(c['t'], us); ty = D.NAMES[c['ty']]
            au = c.get('au', 0) - pc.get('au', 0)
            same = {k: v for k, v in hits[g].items() if rows[0]['c'][k]['t'] == c['t']}
            top = max(same, key=same.get) if same else None
            tty = D.NAMES[rows[0]['c'][top]['ty']] if top is not None else '?'
            C[(w, ty, 'caps')] += 1; C[(w, ty, 'au')] += au
            C[(w, tty, 'topped')] += 1
            if top is not None and top != i:
                C[(w, tty, 'handed')] += 1; C[(w, tty, 'handed_au')] += au
                C[(w, ty, 'took')] += 1; C[(w, ty, 'took_au')] += au
            hits[g].clear()
print(f'{ng} games to r{R}; per game: captures (gold), groups it hit most, of those captured by a teammate (gold), captures of groups a teammate hit most (gold)')
for w in ('us', 'them'):
    for ty in ('vesper', 'marcella', 'heart', 'vendetta', 'varg', 'ryth', 'prism', 'tavi'):
        if C[(w, ty, 'caps')] + C[(w, ty, 'topped')] == 0: continue
        print(f"  {w:4} {ty:9} caps {C[(w,ty,'caps')]/ng:5.2f} ({C[(w,ty,'au')]/ng:5.0f})  topped {C[(w,ty,'topped')]/ng:5.2f}  handed {C[(w,ty,'handed')]/ng:5.2f} ({C[(w,ty,'handed_au')]/ng:4.0f})  took {C[(w,ty,'took')]/ng:5.2f} ({C[(w,ty,'took_au')]/ng:4.0f})")
