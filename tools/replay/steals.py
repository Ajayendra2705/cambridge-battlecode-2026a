"""Steals (10-30, row cs1): groups one side killed (most camp damage in their last 30 rounds) that the other side captured,
per game to r1000, us vs them, with what the stolen captures paid; at the kill, the killer side's nearest champion and the
stealer's nearest (distance to the group tiles); then, for our kills, where our nearest champion was 3 rounds later.

usage: python -I tools/replay/steals.py DIR [DIR ...]

bb2's 150 pinned games: the rivals stole 1.45 of our kills a game (36 gems, 145 gold), we 0.82 of theirs (21, 94); our
nearest champion stood on the tiles 3 rounds after the kill in 23% of the stolen ones and 65% of the kills we kept.
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
RANGED = {'vesper', 'cassi', 'stellar', 'prism', 'willow', 'tavi'}
C = collections.Counter(); L = collections.defaultdict(list); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    dmg = collections.defaultdict(list); pending = {}
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if b['r'] > 1000: break
        hitters = collections.defaultdict(set)
        for i in range(n):
            for x in D.camp_hits(a, i): hitters[x[-1]].add(D.who(a['c'][i]['t'], us))
        for j, (h0, h1) in enumerate(zip(a['mh'], b['mh'])):
            if j in grp and h1 < h0 and len(hitters.get(j, ())) == 1: dmg[grp[j]].append((b['r'], next(iter(hitters[j])), h0 - h1))
        for g, js in members.items():
            if g not in pending and any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js):
                by = collections.Counter()
                for r0, w, d in dmg.pop(g, []):
                    if r0 > b['r'] - 30: by[w] += d
                near = {}
                for side in ('us', 'them'):
                    best = (99, None, None)
                    for i, c in enumerate(b['c']):
                        if c['a'] and 'x' in c and D.who(c['t'], us) == side:
                            d = min(D.dist((c['x'], c['y']), t) for t in gtiles[g])
                            if d < best[0]: best = (d, D.NAMES[c['ty']], i)
                    near[side] = best
                pending[g] = (b['r'], by.most_common(1)[0][0] if by else 'none', near, k + 1)
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            dead, killer, near, k0 = pending.pop(g)
            w = D.who(c['t'], us)
            if killer not in ('us', 'them'): continue
            kind = 'stolen' if killer != w else 'kept'
            C[(killer, kind)] += 1
            if kind == 'stolen':
                C[(killer, 'gems')] += c['g'] - pc['g']; C[(killer, 'gold')] += c.get('au', 0) - pc.get('au', 0)
                L[(killer, 'kd')].append(near[killer][0]); L[(killer, 'sd')].append(near[w][0]); L[(killer, 'wait')].append(b['r'] - dead)
                C[(killer, 'ranged')] += near[killer][1] in RANGED
            if killer == 'us' and near['us'][2] is not None:
                j = near['us'][2]
                r3 = rows[min(len(rows) - 1, k0 + 3)]['c'][j]
                C[('us', kind, 'on3')] += r3['a'] and 'x' in r3 and (r3['x'], r3['y']) in gtiles[g]
med = lambda key: sorted(L[key])[len(L[key]) // 2] if L[key] else 0
print(f'{ng} games to r1000')
for side in ('us', 'them'):
    s = max(1, C[(side, 'stolen')])
    print(f"  kills by {side:4}: kept {C[(side,'kept')]/ng:5.2f} a game, stolen {C[(side,'stolen')]/ng:5.2f} ({C[(side,'gems')]/ng:5.1f} gems, {C[(side,'gold')]/ng:4.0f} gold a game);"
          f" at the kill nearest killer-side champion {med((side,'kd'))} tiles (ranged {C[(side,'ranged')]/s:.2f}), stealer {med((side,'sd'))}; kill to steal {med((side,'wait'))} rounds")
print(f"  our kills: our nearest champion on the tiles 3 rounds after the kill: kept {C[('us','kept','on3')]/max(1,C[('us','kept')]):.2f}, stolen {C[('us','stolen','on3')]/max(1,C[('us','stolen')]):.2f}")
