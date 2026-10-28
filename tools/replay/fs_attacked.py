# Fight starts on a champion (first enemy champion hit on it after 15 quiet rounds), to R, by the victim's side:
# P(victim dies within 10) split by numbers within 6 of the victim at the round start (its side incl. itself vs the
# striker's side), the victim's health, and the victim's response over the next 3 rounds: 'hit back' (it hits an enemy
# champion in one of them), 'ran' (it ends farther from the striker than it started, without hitting), 'other'.
# usage: python -I tools/replay/fs_attacked.py [--upto R] [--size N] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 150; SIZE = None; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--upto': R = int(args[1]); args = args[2:]
    elif args[0] == '--size': SIZE = int(args[1]); args = args[2:]
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
                v = a['c'][j]; pv = p(v); ps = p(a['c'][i])
                if pv is None or ps is None: continue
                own = sum(1 for o in a['c'] if p(o) and o['t'] == v['t'] and D.dist(pv, p(o)) <= 6)
                opp = sum(1 for o in a['c'] if p(o) and o['t'] != v['t'] and D.dist(pv, p(o)) <= 6)
                nb = 'even' if own == opp else ('ahead' if own > opp else ('behind 1' if opp - own == 1 else 'behind 2+'))
                hpf = v.get('hp', 0) / max(1, v.get('mhp', 1))
                hb = 'hp80+' if hpf >= 0.8 else 'hp50-80' if hpf >= 0.5 else 'hp<50'
                hit = any(D.enemy_hits(rows[t], j, n) for t in range(k, k + 3))
                end = p(rows[k + 3]['c'][j]); pe = p(rows[k + 3]['c'][i]) or ps
                ran = not hit and end is not None and D.dist(end, pe) > D.dist(pv, ps)
                resp = 'hit back' if hit else 'ran' if ran else 'other'
                died = any(not rows[t]['c'][j].get('a') for t in range(k + 1, k + 11))
                w = D.who(v['t'], us)
                for key2 in ('all', nb, hb, resp, nb + ' ' + resp):
                    C[(w, key2)] += 1; C[(w, key2, 'd')] += died
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r{R}: fight starts on a champion of the side, per game, and P(the victim dies within 10)')
keys = ['all', 'ahead', 'even', 'behind 1', 'behind 2+', 'hp80+', 'hp50-80', 'hp<50', 'hit back', 'ran', 'other'] + \
       [f'{nb} {r}' for nb in ('ahead', 'even', 'behind 1', 'behind 2+') for r in ('hit back', 'ran', 'other')]
for key in keys:
    s = []
    for w in ('us', 'them'):
        c = C[(w, key)]
        s.append(f'{w:4} {c / ng:5.2f} (dies {C[(w, key, "d")] / max(1, c):.2f})')
    print(f'  {key:20} ' + '   '.join(s))
