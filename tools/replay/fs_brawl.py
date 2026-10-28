# Brawls: the first fight of each game (first enemy champion hit) with 4+ of each side within 8 of the victim. Over the
# next W rounds (default 20), per side and per brawl: champion hit-rounds (a champion hitting an enemy champion), damage
# dealt to champions (hp loss split over hitters, as decoded.py types), casts on enemy champions (unit target), ground
# casts, rounds a champion stands within 3 of an enemy without hitting one, retreat steps (a move that ends farther from
# the nearest enemy, with an enemy within 3 at the start), deaths, the first death's side and type; per type hit share
# while an enemy is in basic reach.
# usage: python -I tools/replay/fs_brawl.py [--size N] [--w W] [--min M] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
SIZE = None; W = 20; M = 4; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--size': SIZE = int(args[1]); args = args[2:]
    elif args[0] == '--w': W = int(args[1]); args = args[2:]
    elif args[0] == '--min': M = int(args[1]); args = args[2:]
C = collections.Counter(); T = collections.Counter(); nb = 0; FD = collections.Counter()
def p(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    k0 = v = None
    for k, a in enumerate(rows):
        for i in range(n):
            h = D.enemy_hits(a, i, n)
            if h: k0, v = k, h[0][-1]; break
        if k0 is not None: break
    if k0 is None or k0 + W + 1 >= len(rows): continue
    a = rows[k0]; q = p(a['c'][v])
    nu = sum(1 for c in a['c'] if p(c) and D.who(c['t'], us) == 'us' and D.dist(q, p(c)) <= 8)
    nt = sum(1 for c in a['c'] if p(c) and D.who(c['t'], us) == 'them' and D.dist(q, p(c)) <= 8)
    if nu < M or nt < M: continue
    nb += 1; first = None
    for t in range(k0, k0 + W):
        r0, r1 = rows[t], rows[t + 1]
        tg = collections.defaultdict(list)
        for i in range(n):
            for x in D.enemy_hits(r0, i, n): tg[x[-1]].append(i)
        for j, hs in tg.items():
            loss = max(0, r0['c'][j].get('hp', 0) - (r1['c'][j].get('hp', 0) if r1['c'][j]['a'] else 0))
            for i in hs: C[(D.who(r0['c'][i]['t'], us), 'dmg')] += loss / len(hs)
        for i, c in enumerate(r0['c']):
            if not p(c): continue
            w = D.who(c['t'], us); qi = p(c)
            ens = [p(o) for o in r0['c'] if p(o) and o['t'] != c['t']]
            if not ens: continue
            de = min(D.dist(qi, e) for e in ens)
            hit = bool(D.enemy_hits(r0, i, n))
            acts = r0['act'][i] if i < len(r0['act']) else []
            C[(w, 'hit')] += hit
            C[(w, 'ucast')] += sum(1 for y in acts if y[0] == 'cast' and len(y) >= 6 and y[-2] == 'c' and r0['c'][y[-1]]['t'] != c['t'])
            C[(w, 'gcast')] += sum(1 for y in acts if y[0] == 'cast' and len(y) < 6)
            if de <= 3 and not hit: C[(w, 'idle3')] += 1
            if de <= 3: C[(w, 'in3')] += 1
            rng = D.RANGE.get(c['ty'], 1)
            if de <= rng: T[(w, D.NAMES[c['ty']], 'inr')] += 1; T[(w, D.NAMES[c['ty']], 'inrhit')] += hit
            mv = [y for y in acts if y[0] == 'move']
            if mv and de <= 3:
                end = (mv[-1][3], mv[-1][4])
                de2 = min(D.dist(end, e) for e in ens)
                if de2 > de: C[(w, 'retreat')] += 1
            if not r1['c'][i]['a']:
                C[(w, 'deaths')] += 1
                if first is None: first = (w, D.NAMES[c['ty']], t - k0)
    if first: FD[(first[0], first[1])] += 1; FD[(first[0],)] += 1
print(f'{nb} brawls (first fight, {M}+ of each side within 8 of the victim), next {W} rounds, per brawl:')
for w in ('us', 'them'):
    print(f'  {w:4}: hit-rounds {C[(w, "hit")] / nb:5.1f}  champion dmg {C[(w, "dmg")] / nb:6.0f}  unit casts on champions {C[(w, "ucast")] / nb:4.1f}  ground casts {C[(w, "gcast")] / nb:4.1f}'
          f'  rounds within 3 of an enemy {C[(w, "in3")] / nb:5.1f} (not hitting {C[(w, "idle3")] / max(1, C[(w, "in3")]):.2f})  retreat steps {C[(w, "retreat")] / nb:4.1f}  deaths {C[(w, "deaths")] / nb:.2f}  first death {FD[(w,)]}')
print('  first death by type:', ', '.join(f'{k[0]} {k[1]} {v}' for k, v in sorted(FD.items()) if len(k) == 2))
print('  hit share with an enemy in basic reach, by type:')
for ty in sorted(set(k[1] for k in T)):
    s = []
    for w in ('us', 'them'):
        c = T[(w, ty, 'inr')]
        s.append(f'{w} {T[(w, ty, "inrhit")] / c:.2f} ({c / nb:.1f}/brawl)' if c else f'{w} -')
    print(f'    {ty:9} ' + '  '.join(s))
