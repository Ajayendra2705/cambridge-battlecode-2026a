# Fight starts on a champion at even numbers within 6 (as fs_attacked.py), to R, by the victim's side. For each ally of the
# victim within 6 of it at the start (not the victim): its distance to the nearest enemy champion, whether an enemy is
# within its own basic reach (RANGE) at the start, its type, and over the 5 rounds after: hit an enemy champion in any
# round, hit a camp in any round (and no champion), neither. Also its health.
# usage: python -I tools/replay/fs_attacked3.py [--upto R] [--size N] [--nb even] DIR...
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
                own = sum(1 for o in a['c'] if p(o) and o['t'] == v['t'] and D.dist(pv, p(o)) <= 6)
                opp = sum(1 for o in a['c'] if p(o) and o['t'] != v['t'] and D.dist(pv, p(o)) <= 6)
                nb = 'even' if own == opp else ('ahead' if own > opp else ('behind1' if opp - own == 1 else 'behind2'))
                if nb != NB: continue
                w = D.who(v['t'], us)
                C[(w, 'starts')] += 1
                for m, o in enumerate(a['c']):
                    if m == j or o['t'] != v['t'] or not p(o) or D.dist(pv, p(o)) > 6: continue
                    q = p(o)
                    de = min(D.dist(q, p(e)) for e in a['c'] if p(e) and e['t'] != v['t'])
                    rng = D.RANGE.get(o['ty'], 1)
                    inr = de <= rng
                    hc = any(D.enemy_hits(rows[t], m, n) for t in range(k, k + 5))
                    hm = not hc and any(D.camp_hits(rows[t], m) for t in range(k, k + 5))
                    resp = 'hit champ' if hc else 'hit camp' if hm else 'neither'
                    hpf = o.get('hp', 0) / max(1, o.get('mhp', 1))
                    db = 'd1' if de <= 1 else 'd2' if de == 2 else 'd3' if de == 3 else 'd4' if de == 4 else 'd5+'
                    kind = 'melee' if rng <= 1 else 'ranged'
                    for key2 in ('all', db, kind + ' ' + db, 'hp<50' if hpf < 0.5 else 'hp50+', D.NAMES[o['ty']]):
                        C[(w, key2)] += 1; C[(w, key2, resp)] += 1
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r{R}, starts at numbers {NB}: allies of the victim within 6 at the start, and what they do in the next 5 rounds')
for w in ('us', 'them'):
    print(f'  victim {w}: {C[(w, "starts")] / ng:.2f} starts per game')
keys = ['all', 'd1', 'd2', 'd3', 'd4', 'd5+'] + [f'{k} d{d}' for k in ('melee', 'ranged') for d in ('1', '2', '3', '4', '5+')] + ['hp<50', 'hp50+'] + sorted(set(k[1] for k in C if len(k) == 2 and k[1] in D.NAMES))
for key in keys:
    s = []
    for w in ('us', 'them'):
        c = C[(w, key)]
        if not c: s.append(f'{w:4}     -'); continue
        s.append(f'{w:4} {c / max(1, C[(w, "starts")]):4.2f}/start: champ {C[(w, key, "hit champ")] / c:.2f} camp {C[(w, key, "hit camp")] / c:.2f} neither {C[(w, key, "neither")] / c:.2f}')
    print(f'  {key:14} ' + '   '.join(s))
