# Fight starts on a champion at even numbers within 6 (as fs_attacked.py), to R, by the victim's side, split by whether the
# victim dies within 10: over the 10 rounds after the start, distinct enemy hitters of the victim, enemy hit-rounds on
# the victim, the victim's own hit-rounds on champions, its allies' hit-rounds on champions within 6 of the victim,
# stuns on the victim (stuns.py rules are not reused: a 'cc' cast on it, approximated by cast actions targeting it),
# numbers within 6 of the victim at +3 and +6 (own / opp), and its health at the start.
# usage: python -I tools/replay/fs_attacked2.py [--upto R] [--size N] [--nb even|behind1|ahead] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 150; SIZE = None; NB = 'even'; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--upto': R = int(args[1]); args = args[2:]
    elif args[0] == '--size': SIZE = int(args[1]); args = args[2:]
    elif args[0] == '--nb': NB = args[1]; args = args[2:]
C = collections.Counter(); ng = 0
def p(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1; last = {}
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > R: break
        for i in range(n):
            for x in D.enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j))
                fresh = k - last.get(key, -99) > 15
                last[key] = k
                if not fresh: continue
                v = a['c'][j]; pv = p(v)
                if pv is None or p(a['c'][i]) is None: continue
                cnt = lambda row, q, side_same: sum(1 for o in row['c'] if p(o) and (o['t'] == v['t']) == side_same and D.dist(q, p(o)) <= 6)
                own, opp = cnt(a, pv, True), cnt(a, pv, False)
                nb = 'even' if own == opp else ('ahead' if own > opp else ('behind1' if opp - own == 1 else 'behind2'))
                if nb != NB: continue
                died = any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 11))
                end = next((t for t in range(k + 1, k + 11) if not rows[t]['c'][j].get('a')), k + 11)
                hitters = set(); ehr = 0; vhr = 0; ahr = 0; stn = 0; dmg_in = 0
                for t in range(k, end):
                    row = rows[t]
                    for m in range(n):
                        if row['c'][m]['t'] == v['t']: continue
                        hs = [y for y in D.enemy_hits(row, m, n) if y[-1] == j]
                        if hs: hitters.add(m); ehr += 1
                        acts = row['act'][m] if m < len(row['act']) else []
                        if any(y[0] == 'cast' and len(y) >= 6 and y[-2] == 'c' and y[-1] == j for y in acts): stn += 1
                    if D.enemy_hits(row, j, n): vhr += 1
                    q = p(row['c'][j])
                    for m in range(n):
                        if m == j or row['c'][m]['t'] != v['t'] or not p(row['c'][m]) or not q: continue
                        if D.dist(q, p(row['c'][m])) <= 6 and D.enemy_hits(row, m, n): ahr += 1
                h0 = v.get('hp', 0); h1 = rows[min(end, k + 10)]['c'][j].get('hp', 0) if not died else 0
                q3 = p(rows[k + 3]['c'][j]) or pv; q6 = p(rows[k + 6]['c'][j]) or pv
                w = D.who(v['t'], us); key2 = 'dies' if died else 'lives'
                for kk in ((w, 'all'), (w, key2)):
                    C[kk] += 1; C[kk + ('h',)] += len(hitters); C[kk + ('ehr',)] += ehr; C[kk + ('vhr',)] += vhr; C[kk + ('ahr',)] += ahr
                    C[kk + ('stn',)] += stn; C[kk + ('o3',)] += cnt(rows[k + 3], q3, True); C[kk + ('p3',)] += cnt(rows[k + 3], q3, False)
                    C[kk + ('o6',)] += cnt(rows[k + 6], q6, True); C[kk + ('p6',)] += cnt(rows[k + 6], q6, False)
                    C[kk + ('hp',)] += h0; C[kk + ('mhp',)] += v.get('mhp', 0); C[kk + ('own',)] += own
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r{R}, starts at numbers {NB}: per start, over the 10 rounds after it (to the death)')
for w in ('us', 'them'):
    for key2 in ('all', 'dies', 'lives'):
        kk = (w, key2); c = C[kk]
        if not c: continue
        f = lambda s: C[kk + (s,)] / c
        print(f'  victim {w:4} {key2:5} {c / ng:5.2f}/g: start numbers {f("own"):.1f}v{f("own"):.1f}, hp {f("hp"):.0f}/{f("mhp"):.0f}; enemy hitters {f("h"):.2f}, enemy hit-rounds {f("ehr"):.2f}, '
              f'unit casts on it {f("stn"):.2f}; victim hit-rounds {f("vhr"):.2f}, allies near hit-rounds {f("ahr"):.2f}; numbers +3 {f("o3"):.1f}v{f("p3"):.1f}, +6 {f("o6"):.1f}v{f("p6"):.1f}')
