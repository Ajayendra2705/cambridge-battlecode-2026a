"""Which action opens a fight, and casts by type: python -I opener.py RMAX DIR..."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
RM = int(sys.argv[1])
O = collections.Counter(); C = collections.defaultdict(collections.Counter); B = collections.Counter(); G = collections.Counter()
ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    last = -99
    for t in range(n):
        G[(D.who(rows[0]['c'][t]['t'], us), D.NAMES[rows[0]['c'][t]['ty']])] += 1
    for k, a in enumerate(rows):
        if a['r'] > RM:
            break
        evs = []
        for i in range(n):
            for x in (a['act'][i] if i < len(a['act']) else []):
                if x[0] == 'cast':
                    c = a['c'][i]
                    s = C[(D.who(c['t'], us), D.NAMES[c['ty']])]
                    s['cast'] += 1
                    s[x[1] if isinstance(x[1], str) else 'slot' + str(x[1])] += 1
                    if len(x) >= 5 and x[-2] == 'c' and x[-1] < n and a['c'][x[-1]]['t'] != c['t']:
                        s['onE'] += 1
                    if len(x) >= 5 and x[-2] == 'm':
                        s['onM'] += 1
            for x in D.enemy_hits(a, i, n):
                evs.append((i, x))
        if not evs:
            continue
        if k - last >= 15:
            i, x = evs[0]
            c = a['c'][i]
            O[(D.who(c['t'], us), x[0])] += 1
            O[(D.who(c['t'], us), x[0], D.NAMES[c['ty']])] += 1
            B[D.who(c['t'], us)] += 1
        last = k
print(ng, 'games. Opening hit by action:')
for w in ('us', 'them'):
    print(w, B[w] / ng, 'a game; attack', round(O[(w, 'attack')] / max(1, B[w]), 2), 'cast', round(O[(w, 'cast')] / max(1, B[w]), 2))
    print('   ', ' '.join(f"{k[2]}:{k[1][0]}={v/ng:.2f}" for k, v in sorted(O.items(), key=lambda z: -z[1]) if len(k) == 3 and k[0] == w)[:400])
print('Casts a game per champion of the type (with type):')
for key in sorted(C, key=lambda z: (z[1], z[0])):
    s = C[key]; g = max(1, G[key])
    if g < 15:
        continue
    print(f"{key[1]:9} {key[0]:4} games {g:3} casts {s['cast']/g:5.1f} on enemy champion {s['onE']/g:5.1f} on camp {s['onM']/g:5.1f}")
