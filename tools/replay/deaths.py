"""Deaths to enemy champions in detail, us vs them, to round R: the situation K rounds before the death.
usage: python -I tools/replay/deaths.py R DIR...  (env TYPE=heart: only that champion type's deaths, both sides)
Per death: health share K rounds before, enemies / allies within 6 then, zone, bag, the dead champion's hits on
champions and its moves away from the nearest enemy over the last K rounds, and the killer side's count within 6 at death."""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
R, K = int(sys.argv[1]), 10
TYPE = os.environ.get('TYPE')
A = collections.Counter(); ng = 0; tot = collections.Counter()
def near(row, i, team, d=6):
    c = row['c'][i]
    if 'x' not in c: return 0
    return sum(1 for j, o in enumerate(row['c']) if j != i and o['a'] and 'x' in o and o['t'] == team and D.dist((c['x'], c['y']), (o['x'], o['y'])) <= d)
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    hitby = collections.defaultdict(lambda: -99)  # last round champion i was hit by an enemy champion
    for k in range(1, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > R: break
        for i in range(n):
            for x in D.enemy_hits(a, i, n): hitby[x[-1]] = a['r']
        for i in range(n):
            if not (a['c'][i]['a'] and not b['c'][i]['a']): continue
            if a['r'] - hitby[i] > 3: continue  # not a champion kill
            c0 = rows[max(0, k - 1 - K)]
            me = c0['c'][i]
            if not me['a'] or 'x' not in me: continue
            if TYPE and D.NAMES[me['ty']] != TYPE: continue
            w = D.who(me['t'], us)
            tot[w] += 1
            hp = me['hp'] / me['mhp']
            e = near(c0, i, 1 - me['t']); al = near(c0, i, me['t'])
            p = (me['x'], me['y'])
            do = min(D.dist(p, q) for q in start[me['t']]); de = min(D.dist(p, q) for q in start[1 - me['t']])
            zone = 'own' if do < de - 3 else 'enemy' if de < do - 3 else 'middle'
            hits = sum(1 for kk in range(max(0, k - 1 - K), k) if D.enemy_hits(rows[kk], i, n))
            away = 0
            for kk in range(max(1, k - K), k):
                r0, r1 = rows[kk - 1], rows[kk]
                c, nc = r0['c'][i], r1['c'][i]
                if 'x' not in c or 'x' not in nc or (c['x'], c['y']) == (nc['x'], nc['y']): continue
                es = [(o['x'], o['y']) for o in r0['c'] if o['a'] and 'x' in o and o['t'] != me['t']]
                if not es: continue
                d0 = min(D.dist((c['x'], c['y']), q) for q in es); d1 = min(D.dist((nc['x'], nc['y']), q) for q in es)
                if d1 > d0: away += 1
            A[(w, 'hp', 'full' if hp >= 0.9 else 'hi' if hp >= 0.5 else 'lo')] += 1
            A[(w, 'num', f'e{min(e, 3)} a{min(al, 2)}')] += 1
            A[(w, 'zone', zone)] += 1
            A[(w, 'bag', '30+' if me['g'] >= 30 else '1-29' if me['g'] else '0')] += 1
            A[(w, 'hits', '0' if hits == 0 else '1-3' if hits <= 3 else '4+')] += 1
            A[(w, 'away', '0' if away == 0 else '1-3' if away <= 3 else '4+')] += 1
            A[(w, 'type', D.NAMES[me['ty']])] += 1
print(f'{ng} games to r{R}: deaths to champions per game, us {tot["us"] / ng:.2f}, them {tot["them"] / ng:.2f}; situation {K} rounds before (per game)')
for cat in ('hp', 'num', 'zone', 'bag', 'hits', 'away', 'type'):
    keys = sorted({k[2] for k in A if k[1] == cat})
    print(f'  {cat:5} ' + '  '.join(f'{v}: {A[("us", cat, v)] / ng:.2f}/{A[("them", cat, v)] / ng:.2f}' for v in keys))
