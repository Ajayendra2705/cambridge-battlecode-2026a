# Per champion type and first emblem family: champion-games, gems collected and deaths to r1000, and the round of that
# first emblem (us and the rivals).
# usage: python -I tools/replay/firstemb.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
A = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c']); first = [None] * n; got = [0] * n; dead = [0] * n; when = [0] * n
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if pc['a'] and not c['a']: dead[i] += 1
            if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): got[i] += c['g'] - pc['g']
            if first[i] is None:
                for it, cnt in c.get('it', []):
                    nm = D.item_name(meta, it)
                    if nm.endswith('emblem') and cnt > 0: first[i] = nm.split('_')[0]; when[i] = b['r']
    for i in range(n):
        ty = D.NAMES[rows[0]['c'][i]['ty']]
        A[(D.who(rows[0]['c'][i]['t'], us), ty, first[i] or 'none')].append((got[i], dead[i], when[i]))
for k in sorted(A):
    v = A[k]
    if len(v) < 5: continue
    print(f"{k[0]:4} {k[1]:9} {k[2]:11} n {len(v):3}  gems {sum(x[0] for x in v)/len(v):5.0f}  deaths {sum(x[1] for x in v)/len(v):4.2f}  first at r{sum(x[2] for x in v)/len(v):4.0f}")
