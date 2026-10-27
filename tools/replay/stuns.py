"""Stuns on champions, us vs them, to r1000. Reads decoded runs (data/fights/<run>/).
usage: python -I tools/replay/stuns.py DIR...

Stun sources (docs/MECHANICS.md): unit casts Tavi slot 1, Prism slot 0, Cassi slot 1, Ren slot 0 on an enemy champion;
area casts Heart of Ruin slot 1 (dash landing) and Ryth slot 0, on the ground or on a unit, stunning enemies within 1 of
the cast tile (in the row before or the row of the cast); Marcella's first basic attack on an enemy champion after her
slot 0 cast. Marcella is stun-immune. Prints per side (the stunning side):
- stuns per game, the share on a target the side already stunned that round, the share followed by another stun of the
  side on the same target within 2 rounds, P(target dead within 3 and within 6 rounds), stuns per game by stunner type;
- the side's own deaths with a stun on the victim in its last 6 rounds;
- for stunned targets: the share and P(dead within 6) by enemies within 3, allies within 3 and health at the stun;
- deaths per game (stunned in brackets) by game group: our team size, and whether the rivals field an extra stunner
  (Ryth, Tavi, Prism, Cassi or Ren; 'plain' = only Heart of Ruin and Marcella).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

N = D.NAMES.index
UNIT = {(N('tavi'), 1), (N('prism'), 0), (N('cassi'), 1), (N('ren'), 0)}
AREA = {(N('heart'), 1), (N('ryth'), 0)}
EXTRA = {N('ryth'), N('tavi'), N('prism'), N('cassi'), N('ren')}
MARC = N('marcella')
def pos(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
def died(rows, j, k, lim): return any(kk + 1 < len(rows) and rows[kk]['c'][j]['a'] and not rows[kk + 1]['c'][j]['a'] for kk in range(k, k + lim))

def main(dirs):
    T = {w: collections.Counter() for w in ('us', 'them')}
    TY = {w: collections.Counter() for w in ('us', 'them')}
    TG = {w: collections.Counter() for w in ('us', 'them')}
    CTX, SP = collections.Counter(), collections.Counter()
    ng = 0
    for us, res, mp, meta, rows in D.games(dirs):
        ng += 1; n = len(rows[0]['c'])
        for c in rows[0]['c']: TG[D.who(c['t'], us)][c['ty']] += 1
        grp = ('extra' if any(c['ty'] in EXTRA for c in rows[0]['c'] if c['t'] != us) else 'plain') + str(sum(c['t'] == us for c in rows[0]['c']))
        SP[(grp, 'g')] += 1
        enh = [False] * n
        stuns = collections.defaultdict(list)   # row index -> [(stunning side, target, stunner type)]
        for k in range(1, len(rows)):
            r = rows[k]
            if r['r'] > 1000: break
            for e in range(n):
                me = r['c'][e]; te = me['ty']
                for x in (r['act'][e] if e < len(r['act']) else []):
                    hit = []
                    if x[0] == 'cast':
                        if te == MARC and x[1] == 0: enh[e] = True
                        if len(x) == 6 and x[4] == 'c' and (te, x[1]) in UNIT and x[5] < n and r['c'][x[5]]['t'] != me['t']: hit = [x[5]]
                        if len(x) in (4, 6) and (te, x[1]) in AREA:
                            land = (x[2], x[3])
                            hit = [j for j in range(n) if r['c'][j]['t'] != me['t']
                                   and any(q and D.dist(land, q) <= 1 for q in (pos(rows[k - 1]['c'][j]), pos(r['c'][j])))]
                    elif x[0] == 'attack' and te == MARC and enh[e]:
                        enh[e] = False
                        if len(x) == 5 and x[3] == 'c' and x[4] < n and r['c'][x[4]]['t'] != me['t']: hit = [x[4]]
                    for j in hit:
                        if r['c'][j]['ty'] != MARC and r['c'][j]['a']: stuns[k].append((D.who(me['t'], us), j, te))
        for k, lst in stuns.items():
            seen = collections.Counter()
            for w, j, te in lst:
                C = T[w]; C['stuns'] += 1; TY[w][te] += 1
                if seen[(w, j)]: C['overlap'] += 1
                seen[(w, j)] += 1
                if seen[(w, j)] > 1: continue
                C['first'] += 1
                C['chain'] += any((w, j) == (w2, j2) for kk in (k + 1, k + 2) for w2, j2, _ in stuns.get(kk, []))
                C['d3'] += died(rows, j, k, 3); d6 = died(rows, j, k, 6); C['d6'] += d6
                tr = rows[k - 1]['c'][j]; tp = pos(tr)
                if not tp: continue
                na = sum(1 for o in rows[k - 1]['c'] if pos(o) and o['t'] != tr['t'] and D.dist(tp, pos(o)) <= 3)
                nl = sum(1 for jj, o in enumerate(rows[k - 1]['c']) if jj != j and pos(o) and o['t'] == tr['t'] and D.dist(tp, pos(o)) <= 3)
                hf = tr['hp'] / max(1, tr['mhp'])
                for tag in ('enemies %d' % min(na, 4), 'allies %d' % min(nl, 2), 'health ' + ('<50' if hf < .5 else '50-80' if hf < .8 else '80+')):
                    CTX[(w, tag)] += 1; CTX[(w, tag, 'd')] += d6
                CTX[(w, 'n')] += 1
        for k in range(1, len(rows)):
            if rows[k]['r'] > 1000: break
            for i in range(n):
                if rows[k - 1]['c'][i]['a'] and not rows[k]['c'][i]['a']:
                    w = D.who(rows[k - 1]['c'][i]['t'], us); other = 'them' if w == 'us' else 'us'
                    st = any((other, i) == (w2, j2) for kk in range(k - 6, k + 1) for w2, j2, _ in stuns.get(kk, []))
                    T[w]['deaths'] += 1; T[w]['dstun'] += st; SP[(grp, w, 'd')] += 1; SP[(grp, w, 'ds')] += st
    for w in ('us', 'them'):
        C = T[w]; f = max(1, C['first']); tgt = 'them' if w == 'us' else 'us'
        print(f"{w:4} stunning: {C['stuns']/ng:.1f} stuns on champions per game, overlap {C['overlap']/max(1,C['stuns']):.0%}, chained {C['chain']/f:.0%}, "
              f"target dead within 3 {C['d3']/f:.0%}, within 6 {C['d6']/f:.0%}")
        print('      by stunner (per game of that type): ' + ', '.join(f"{D.NAMES[t]} {v/max(1,TG[w][t]):.1f} ({TG[w][t]} games)" for t, v in TY[w].most_common()))
        print(f"      targets ({tgt}): " + ' | '.join(f"{t} {CTX[(w,t)]/max(1,CTX[(w,'n')]):.0%} -> {CTX[(w,t,'d')]/max(1,CTX[(w,t)]):.2f}" for t in
              ('enemies 0', 'enemies 1', 'enemies 2', 'enemies 3', 'enemies 4', 'allies 0', 'allies 1', 'allies 2', 'health <50', 'health 50-80', 'health 80+')))
        print(f"      own deaths {C['deaths']/ng:.2f} per game, {C['dstun']/max(1,C['deaths']):.0%} with a stun on the victim in its last 6 rounds")
    for grp in sorted({k[0] for k in SP}):
        g = SP[(grp, 'g')]
        print(f"{grp:7} {g:3} games: deaths us {SP[(grp,'us','d')]/g:.2f} (stunned {SP[(grp,'us','ds')]/g:.2f}), them {SP[(grp,'them','d')]/g:.2f} (stunned {SP[(grp,'them','ds')]/g:.2f})")
    print(f"games: {ng}")

if __name__ == '__main__':
    main(sys.argv[1:])
