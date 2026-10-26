# Order of emblem completions per champion type (first four emblems, to r1000): share of each emblem at each position,
# and the mean round of completion. Us vs them. Usage: python -I tools/replay/emblemorder.py TYPE DIR...
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
T = sys.argv[1]
P = collections.defaultdict(collections.Counter); RD = collections.defaultdict(list); NG = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    n = len(rows[0]['c'])
    seen = [set() for _ in range(n)]
    order = [[] for _ in range(n)]
    for r in rows:
        if r['r'] > 1000: break
        for i, c in enumerate(r['c']):
            for it, cnt in c.get('it', []):
                name = D.item_name(meta, it)
                if name.endswith('emblem') and it not in seen[i] and cnt > 0:
                    seen[i].add(it); order[i].append((r['r'], name.replace(' emblem', '')))
    for i, c in enumerate(rows[0]['c']):
        if D.NAMES[c['ty']] != T: continue
        side = D.who(c['t'], us); NG[side] += 1
        for k, (rd, name) in enumerate(order[i][:4]):
            P[(side, k)][name] += 1; RD[(side, k)].append(rd)
for side in ('us', 'them'):
    print(f'{T} {side} ({NG[side]} champion-games)')
    for k in range(4):
        tot = sum(P[(side, k)].values())
        if not tot: continue
        top = ', '.join(f'{nm} {v / NG[side]:.0%}' for nm, v in P[(side, k)].most_common(5))
        print(f'  emblem {k + 1}: mean round {sum(RD[(side, k)]) / tot:5.0f}, held by {tot / NG[side]:.0%}: {top}')
