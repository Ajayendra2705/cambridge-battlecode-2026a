"""Use of a ready ranged spell with an enemy champion in its range: python -I nukeuse.py TYPE SLOT RANGE DIR...
Rounds in which an enemy champion stood within RANGE at the start of the round and the slot was ready (last cast at least 8 rounds ago), split by what the champion did."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
T, SL, RG = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
A = collections.defaultdict(collections.Counter)
G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[4:]):
    n = len(rows[0]['c'])
    for i, c0 in enumerate(rows[0]['c']):
        if D.NAMES[c0['ty']] != T:
            continue
        side = D.who(c0['t'], us)
        G[side] += 1
        last = -99
        prev = None
        for r in rows:
            R = r['r']
            if R > 600:
                break
            c = r['c'][i]
            acts = r['act'][i] if i < len(r['act']) else []
            casts = [x for x in acts if x[0] == 'cast' and x[1] == SL]
            if prev is not None and c['a'] and prev['c'][i]['a'] and 'x' in prev['c'][i]:
                pc = prev['c'][i]
                en = [e for e in prev['c'] if e['t'] != pc['t'] and e['a'] and 'x' in e]
                d = min([D.dist((pc['x'], pc['y']), (e['x'], e['y'])) for e in en] or [99])
                if d <= RG and R - last >= 8:
                    band = 'r0-100' if R <= 100 else 'r100-300' if R <= 300 else 'r300-600'
                    s = A[(side, band)]
                    s['n'] += 1
                    kinds = {x[0] for x in acts}
                    if casts and casts[0][-2] == 'c':
                        w = 'nukeC'
                    elif casts:
                        w = 'nukeM'
                    elif D.enemy_hits(r, i, n):
                        w = 'hitC'
                    elif D.camp_hits(r, i):
                        w = 'hitM'
                    elif 'move' in kinds:
                        w = 'move'
                    else:
                        w = 'none'
                    s[w] += 1
                    s['hp'] += pc.get('hp', 0) / max(1, pc.get('mhp', 1))
            if casts:
                last = R
            prev = r
print(T, 'games', dict(G))
for key in sorted(A):
    s = A[key]; m = max(1, s['n'])
    print(f"{str(key):22} {s['n']/max(1,G[key[0]]):5.1f} a game | spell on champion {s['nukeC']/m:.2f} on camp {s['nukeM']/m:.2f} | basic on champion {s['hitC']/m:.2f} on camp {s['hitM']/m:.2f} | move {s['move']/m:.2f} none {s['none']/m:.2f} | hp {s['hp']/m:.2f}")
