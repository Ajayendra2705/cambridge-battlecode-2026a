"""What a champion does with an enemy inside its strike distance: python -I inrange.py RMAX DIR...
Per side and round band: rounds with an enemy in basic-attack range at the start of the round (ranged 3, melee 1), split by the action taken (hit a champion, hit a camp,
tribute or shop or other, move only, nothing). A low share of hits in range means the side gives away first strikes."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
RM = int(sys.argv[1])
MELEE = set()
A = collections.defaultdict(collections.Counter)
ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    prev = None
    for r in rows:
        R = r['r']
        if R > RM:
            break
        if prev is None or prev['r'] != R - 1:
            prev = r
            continue
        for i, c in enumerate(r['c']):
            pc = prev['c'][i]
            if not (pc['a'] and c['a'] and 'x' in pc):
                continue
            p = (pc['x'], pc['y'])
            en = [e for e in prev['c'] if e['t'] != pc['t'] and e['a'] and 'x' in e]
            if not en:
                continue
            d = min(D.dist(p, (e['x'], e['y'])) for e in en)
            if d > 6:
                continue
            acts = r['act'][i] if i < len(r['act']) else []
            kinds = {x[0] for x in acts}
            eh = bool(D.enemy_hits(r, i, n)); ch = bool(D.camp_hits(r, i))
            what = 'hitC' if eh else 'hitM' if ch else 'move' if 'move' in kinds else 'other' if kinds else 'none'
            side = D.who(c['t'], us)
            band = 'r0-100' if R <= 100 else 'r100-300' if R <= 300 else 'r300+'
            s = A[(side, band, d)]
            s['n'] += 1
            s[what] += 1
            A[(side, band, 'ty', c['ty'], 'd<=3' if d <= 3 else 'd>3')]['n'] += 1
            A[(side, band, 'ty', c['ty'], 'd<=3' if d <= 3 else 'd>3')][what] += 1
print(ng, 'games')
for key in sorted(A, key=str):
    s = A[key]
    if len(key) != 3:
        continue
    m = max(1, s['n'])
    print(f"{str(key):26} {s['n']/ng:7.2f} a game | hit champion {s['hitC']/m:.2f} camp {s['hitM']/m:.2f} move {s['move']/m:.2f} other {s['other']/m:.2f} none {s['none']/m:.2f}")
print()
for key in sorted(A, key=str):
    s = A[key]
    if len(key) != 5 or key[4] != 'd<=3' or key[1] == 'r300+':
        continue
    m = max(1, s['n'])
    if s['n'] < 50:
        continue
    print(f"{str(key):44} {s['n']/ng:7.2f} | hit champion {s['hitC']/m:.2f} camp {s['hitM']/m:.2f} move {s['move']/m:.2f} other {s['other']/m:.2f} none {s['none']/m:.2f}")
