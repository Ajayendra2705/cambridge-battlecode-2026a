# Deaths soon after leaving spawn (to R): for each champion death, the last round the victim stood within 1 of a spawn
# tile of its side (spawn tiles = the side's round-0 champion tiles) and how many rounds before the death that was; at
# that leaving round: enemy champions within 10 of the side's spawn (off their own spawn), and the victim's allies within
# 3 of it. Split by game class (our deaths minus theirs by r1000: massacre 6+, else other). Also per game: walk-outs
# (a champion leaves the spawn area) with 2+ enemies within 10 of our spawn, and P(death within 40 rounds) after them,
# by allies within 3 at leaving.
# usage: python -I tools/replay/fs_walkout.py [--upto R] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 1000; args = sys.argv[1:]
if args and args[0] == '--upto': R = int(args[1]); args = args[2:]
C = collections.Counter(); G = collections.Counter()
def p(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    last = next((k for k, a in enumerate(rows) if a['r'] > R), len(rows) - 1)
    dth = collections.Counter()
    for k in range(last):
        for i, c in enumerate(rows[k + 1]['c']):
            if rows[k]['c'][i]['a'] and not c['a']: dth[D.who(c['t'], us)] += 1
    cls = 'massacre' if dth['us'] - dth['them'] >= 6 else 'other'
    G[cls] += 1
    sp = {t: [(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c] for t in (0, 1)}
    near_sp = lambda q, t: min(D.dist(q, s) for s in sp[t])
    on = [None] * n  # last round index the champion was within 1 of its spawn
    pending = {}
    for k in range(last):
        a = rows[k]
        for i, c in enumerate(a['c']):
            q = p(c)
            if q is None: continue
            t = c['t']
            if near_sp(q, t) <= 1:
                on[i] = k; pending.pop(i, None)
            elif on[i] == k - 1:
                # just left: count enemies within 10 of our spawn and allies within 3
                ens = sum(1 for o in a['c'] if p(o) and o['t'] != t and near_sp(p(o), t) <= 10 and near_sp(p(o), 1 - t) > 1)
                al = sum(1 for j, o in enumerate(a['c']) if j != i and p(o) and o['t'] == t and D.dist(q, p(o)) <= 3)
                pending[i] = (k, ens, al)
                w = D.who(t, us)
                if ens >= 2:
                    ab = 'allies 0' if al == 0 else 'allies 1' if al == 1 else 'allies 2+'
                    C[(cls, w, 'wo')] += 1; C[(cls, w, 'wo', ab)] += 1
                    died = any(not rows[t2]['c'][i]['a'] for t2 in range(k + 1, min(last, k + 41)))
                    C[(cls, w, 'wod')] += died; C[(cls, w, 'wod', ab)] += died
        for i, c in enumerate(rows[k + 1]['c']):
            if a['c'][i]['a'] and not c['a']:
                w = D.who(a['c'][i]['t'], us)
                C[(cls, w, 'deaths')] += 1
                if i in pending:
                    k0, ens, al = pending[i]
                    since = k - k0
                    if since <= 40:
                        C[(cls, w, 'd40')] += 1
                        C[(cls, w, 'd40', 'ens2+' if ens >= 2 else 'ens<2')] += 1
print('games:', dict(G))
for cls in ('massacre', 'other'):
    g = max(1, G[cls])
    for w in ('us', 'them'):
        k = (cls, w)
        print(f'  {cls:8} {w:4}: deaths {C[k + ("deaths",)] / g:5.2f}/g; within 40 rounds of leaving spawn {C[k + ("d40",)] / g:5.2f}'
              f' (2+ enemies within 10 of our spawn at leaving {C[k + ("d40", "ens2+")] / g:5.2f}); walk-outs with 2+ enemies near spawn {C[k + ("wo",)] / g:5.2f}/g,'
              f' P(death in 40) {C[k + ("wod",)] / max(1, C[k + ("wo",)]):.2f}; by allies within 3: '
              + ', '.join(f'{ab} {C[k + ("wo", ab)] / g:.2f}/g {C[k + ("wod", ab)] / max(1, C[k + ("wo", ab)]):.2f}' for ab in ('allies 0', 'allies 1', 'allies 2+')))
