# Whose captures a type's camp hits feed, to R (600): each camp-hit round of a TYPE champion is credited to the group's next
# capture (the first champion whose gems or gold rise on the group's tiles after its last camp died): by self, a
# teammate, an enemy, or none before R. Per game, us vs them.
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
R = int(os.environ.get('R', '600')); TYPE = os.environ.get('TYPE', 'vesper')
C = collections.Counter(); G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    vi = [i for i, c in enumerate(rows[0]['c']) if D.NAMES[c['ty']] == TYPE]
    for i in vi: G[D.who(rows[0]['c'][i]['t'], us)] += 1
    open_hits = collections.defaultdict(list)  # group -> [(slot)]
    pending = set()
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        for i in vi:
            if not a['c'][i]['a']: continue
            gs = {grp[x[-1]] for x in D.camp_hits(a, i) if x[-1] in grp}
            for g in gs: open_hits[g].append(i)
        for g, js in members.items():
            if any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js): pending.add(g)
        for k, c in enumerate(b['c']):
            pc = a['c'][k]
            if not (c['a'] and pc['a'] and 'x' in c) or c.get('k', 0) > pc.get('k', 0): continue
            if c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            pending.discard(g)
            for i in open_hits.pop(g, []):
                w = D.who(rows[0]['c'][i]['t'], us)
                out = 'self' if k == i else 'mate' if c['t'] == rows[0]['c'][i]['t'] else 'enemy'
                C[(w, out)] += 1
    for g, hs in open_hits.items():
        for i in hs: C[(D.who(rows[0]['c'][i]['t'], us), 'none')] += 1
for w in ('us', 'them'):
    tot = sum(C[(w, o)] for o in ('self', 'mate', 'enemy', 'none'))
    print(f"{w:4} {TYPE} n {G[w]}: camp-hit rounds per game {tot / max(1, G[w]):.1f}: " + ', '.join(f"{o} {C[(w, o)] / max(1, G[w]):.1f} ({100 * C[(w, o)] / max(1, tot):.0f}%)" for o in ('self', 'mate', 'enemy', 'none')))
