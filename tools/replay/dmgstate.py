# All champions, 5-a-side games, to r1000, off spawns, by side: per contact state (enemies within 5: 1, 2, 3+; allies within
# 5: 0, 1, 2+), rounds per game, enemy champion hits received per round, health lost per round (net of heals) as a share of
# max health, and the hits each side lands per round on enemy champions (the champion's own hits).
# usage: python -I tools/replay/dmgstate.py DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist, enemy_hits
args = sys.argv[1:]
R = {w: collections.Counter() for w in ('us', 'them')}; G = collections.Counter()
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 10: continue
    G['g'] += 1
    spawn = {t: set(pos(c) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    for r in range(len(rows) - 1):
        if rows[r]['r'] > 1000: break
        row, nx = rows[r], rows[r + 1]
        hits_on = collections.Counter()
        for k in range(10):
            for x in (row['act'][k] if k < len(row['act']) else []):
                if x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' and x[-1] < 10 and row['c'][x[-1]]['t'] != row['c'][k]['t']: hits_on[x[-1]] += 1
        for i, c in enumerate(row['c']):
            if not c['a'] or 'x' not in c: continue
            p = pos(c)
            if any(dist(p, s) <= 2 for s in spawn[0] | spawn[1]): continue
            en = sum(1 for e in row['c'] if e['a'] and 'x' in e and e['t'] != c['t'] and dist(p, pos(e)) <= 5)
            if not en: continue
            al = sum(1 for j, e in enumerate(row['c']) if j != i and e['a'] and 'x' in e and e['t'] == c['t'] and dist(p, pos(e)) <= 5)
            st = (min(en, 3), min(al, 2)); w = who(c['t'], us); X = R[w]
            X[st] += 1; X[st + ('hits',)] += hits_on[i]; X[st + ('own',)] += bool(enemy_hits(row, i, 10))
            n2 = nx['c'][i]
            if n2['a'] and 'hp' in n2: X[st + ('lost',)] += max(0, c['hp'] - n2['hp']) / max(1, c['mhp']); X[st + ('n2',)] += 1
            else: X[st + ('died',)] += 1
print(f"5-a-side, to r1000, {G['g']} games: per contact state, rounds/game | hits received per round | health share lost per round | own hit share | deaths per 100 rounds")
for en in (1, 2, 3):
    for al in (0, 1, 2):
        st = (en, al); cells = []
        for w in ('us', 'them'):
            X = R[w]; n = max(1, X[st])
            cells.append(f"{w} {X[st] / G['g']:6.1f} | {X[st + ('hits',)] / n:4.2f} | {X[st + ('lost',)] / max(1, X[st + ('n2',)]):.3f} | {X[st + ('own',)] / n:.2f} | {100 * X[st + ('died',)] / n:4.1f}")
        print(f"  e{en}{'+' if en == 3 else ' '} a{al}{'+' if al == 2 else ' '}  " + '    '.join(cells))
