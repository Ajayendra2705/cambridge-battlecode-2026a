# Carried gems by champion type and side to r1000: the mean bag while alive, the mean bag with an enemy champion within
# 4, deaths and gems lost on death per game, per death, and deaths carrying 30+; then the melee line (Heart of Ruin,
# Marcella, Varg, Vendetta, Ryth, Ren, Issac: basic range 1) pooled per side. The mbk1 metric (10-31).
# usage: python -I tools/replay/typebag.py DIR...
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
MELEE = {'heart', 'marcella', 'varg', 'vendetta', 'ryth', 'ren', 'issac'}  # basic range 1 (docs/MECHANICS.md)
A = collections.Counter(); G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    for c in rows[0]['c']: G[(D.who(c['t'], us), D.NAMES[c['ty']])] += 1
    for k, b in enumerate(rows):
        if b['r'] > 1000: break
        for i, c in enumerate(b['c']):
            key = (D.who(c['t'], us), D.NAMES[c['ty']])
            if k and rows[k - 1]['c'][i]['a'] and not c['a']:
                g = rows[k - 1]['c'][i].get('g', 0)
                A[key + ('deaths',)] += 1; A[key + ('lost',)] += g; A[key + ('d30',)] += g >= 30
            if not c['a'] or 'x' not in c: continue
            g = c.get('g', 0); A[key + ('alive',)] += 1; A[key + ('bag',)] += g
            near = min((D.dist((c['x'], c['y']), (o['x'], o['y'])) for o in b['c'] if o['t'] != c['t'] and o['a'] and 'x' in o), default=99)
            if near <= 4: A[key + ('cn',)] += 1; A[key + ('cbag',)] += g
def line(name, keys, g):
    s = lambda f: sum(A[k + (f,)] for k in keys)
    return (f"{name:9} games {g:4}: mean bag {s('bag') / max(1, s('alive')):5.1f}, with an enemy within 4 {s('cbag') / max(1, s('cn')):5.1f} "
            f"({s('cn') / g:5.1f} rounds a game); deaths {s('deaths') / g:4.2f}, gems lost {s('lost') / g:5.1f} a game, "
            f"{s('lost') / max(1, s('deaths')):5.1f} a death, deaths with 30+ {s('d30') / g:4.2f}")
for side in ('us', 'them'):
    for k in sorted(x for x in G if x[0] == side and G[x] >= 10): print(side, line(k[1], [k], G[k]))
    mk = [k for k in G if k[0] == side and k[1] in MELEE]
    if mk: print(side, line('melee', mk, max(G[k] for k in mk)))
