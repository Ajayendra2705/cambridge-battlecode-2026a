"""What a champion does with an enemy champion in reach: python -I tools/replay/inreach.py RMIN RMAX DIR...

Per champion-round (alive, off its own turn's stun is not known) with an enemy champion within reach at the start of the round: melee types within 2 (a step and a hit),
ranged types within their range. Shares by side of: hit a champion, hit a camp, other cast, move toward the nearest enemy, move away, no action; split by the champion's
health and by numbers within 6 (itself and allies against enemies). Rounds per game show how much time each state takes.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
D.SKIP = []
RANGED = {'vesper': 3, 'cassi': 3, 'willow': 3, 'tavi': 3, 'prism': 3, 'stellar': 3}
r0, r1 = int(sys.argv[1]), int(sys.argv[2])
A = collections.defaultdict(collections.Counter)
ng = 0
KINDS = ['hit', 'camp', 'cast', 'toward', 'away', 'still', 'other']
for us, res, mp, meta, rows in D.games(sys.argv[3:]):
    ng += 1
    n = len(rows[0]['c'])
    for row in rows:
        R = row['r']
        if R < r0:
            continue
        if R > r1:
            break
        cs = row['c']
        for i, c in enumerate(cs):
            if not c['a'] or 'x' not in c:
                continue
            name = D.NAMES[c['ty']]
            reach = RANGED.get(name, 2)
            en = [e for e in cs if e['t'] != c['t'] and e['a'] and 'x' in e]
            if not en:
                continue
            p = (c['x'], c['y'])
            ds = [max(abs(e['x'] - p[0]), abs(e['y'] - p[1])) for e in en]
            dn = min(ds)
            if dn > reach:
                continue
            acts = row['act'][i] if i < len(row['act']) else []
            if D.enemy_hits(row, i, n):
                k = 'hit'
            elif D.camp_hits(row, i):
                k = 'camp'
            elif any(x[0] == 'cast' for x in acts):
                k = 'cast'
            else:
                mv = [x for x in acts if x[0] == 'move']
                if mv:
                    q = (mv[-1][3], mv[-1][4])
                    d2 = min(max(abs(e['x'] - q[0]), abs(e['y'] - q[1])) for e in en)
                    k = 'toward' if d2 < dn else 'away' if d2 > dn else 'other'
                elif not acts:
                    k = 'still'
                else:
                    k = 'other'
            w = D.who(c['t'], us)
            hp = c['hp'] / max(1, c['mhp'])
            band = 'hp>.7' if hp > .7 else 'hp.4-.7' if hp > .4 else 'hp<.4'
            al = sum(1 for o in cs if o['t'] == c['t'] and o['a'] and 'x' in o and max(abs(o['x'] - p[0]), abs(o['y'] - p[1])) <= 6)
            em = sum(1 for d in ds if d <= 6)
            num = 'ahead' if al > em else 'even' if al == em else 'behind'
            for key in ('all', band, num, ('melee' if name not in RANGED else 'ranged'), name):
                A[(w, key)][k] += 1
                A[(w, key)]['n'] += 1
print(f'{ng} games, r{r0}-{r1}: rounds a game with an enemy in reach, then shares us / them')
keys = ['all', 'hp>.7', 'hp.4-.7', 'hp<.4', 'ahead', 'even', 'behind', 'melee', 'ranged', 'heart', 'marcella', 'vendetta', 'vesper', 'willow']
for key in keys:
    a, b = A[('us', key)], A[('them', key)]
    if not a['n'] and not b['n']:
        continue
    print(f"{key:9} {a['n'] / ng:6.1f}/{b['n'] / ng:6.1f} | " + ' '.join(f"{k} {a[k] / max(1, a['n']):.2f}/{b[k] / max(1, b['n']):.2f}" for k in KINDS))
