# Five a side to R (default 600): champion-rounds with 1-3 enemy champions within 6 and health at half or more, by
# enemies within 6 / allies within 6: share of actions (hit a champion, hit a camp, step away from the nearest enemy,
# step closer, other move, idle) and P(death within 10 rounds) after each. By side.
# Usage: python -I tools/replay/stateact.py DIR... [--round R]
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 600
args = [a for a in sys.argv[1:]]
if '--round' in args: k = args.index('--round'); R = int(args[k + 1]); del args[k:k + 2]
T = collections.Counter()
ACTS = ('hit champ', 'hit camp', 'away', 'closer', 'move', 'idle')
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if n != 10: continue
    death = [[None] * n for _ in rows]
    nxt = [10 ** 9] * n
    for k in range(len(rows) - 1, -1, -1):
        for i in range(n):
            if not rows[k]['c'][i]['a'] and (k == 0 or rows[k - 1]['c'][i]['a']): nxt[i] = k
            death[k][i] = nxt[i]
    for k, r in enumerate(rows[:-1]):
        if r['r'] > R: break
        for i, c in enumerate(r['c']):
            if not c['a'] or 'x' not in c or c.get('hp', 0) < 0.5 * max(1, c.get('mhp', 1)): continue
            q = (c['x'], c['y'])
            en = [(D.dist(q, (o['x'], o['y'])), j) for j, o in enumerate(r['c']) if o['t'] != c['t'] and o['a'] and 'x' in o]
            e6 = sum(1 for d, j in en if d <= 6)
            if not 1 <= e6 <= 3: continue
            a6 = min(2, sum(1 for j, o in enumerate(r['c']) if j != i and o['t'] == c['t'] and o['a'] and 'x' in o and D.dist(q, (o['x'], o['y'])) <= 6))
            side = D.who(c['t'], us)
            acts = r['act'][i] if i < len(r.get('act', [])) else []
            if D.enemy_hits(r, i, n): a = 'hit champ'
            elif D.camp_hits(r, i): a = 'hit camp'
            elif any(x[0] == 'move' for x in acts):
                nx = rows[k + 1]['c'][i]
                if 'x' in nx:
                    dn, j = min(en)
                    o = rows[k + 1]['c'][j]
                    d1 = D.dist((nx['x'], nx['y']), (o['x'], o['y'])) if 'x' in o else dn
                    d0 = D.dist(q, (o['x'], o['y'])) if 'x' in o else dn
                    a = 'away' if d1 > d0 else 'closer' if d1 < d0 else 'move'
                else: a = 'move'
            else: a = 'idle'
            dies = death[k][i] - k <= 10
            key = (side, e6, a6)
            T[key + ('n',)] += 1; T[key + (a,)] += 1; T[key + (a, 'd')] += dies
for e6 in (1, 2, 3):
    for a6 in (0, 1, 2):
        for side in ('us', 'them'):
            key = (side, e6, a6); m = T[key + ('n',)]
            if m < 50: continue
            print(f"e{e6} a{a6} {side:4} n {m:6}: " + '  '.join(f"{a} {T[key + (a,)] / m:.2f} ({T[key + (a, 'd')] / max(1, T[key + (a,)]):.3f})" for a in ACTS))
