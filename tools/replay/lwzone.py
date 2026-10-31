# 00lost_world: champion-rounds per game in rounds R0-R1 by zone (corridor rows 13-17, our half, their half), us vs them,
# and inside the corridor: x-band (left entrance x<=6, centre pocket 13-23, right entrance x>=29, else).
# usage: lwzone.py DIR [R0 R1]
import sys, collections
sys.path.insert(0, r'C:\Users\ajiit\Desktop\Future\Projects\Cambridge Battlecode\tools\replay')
import decoded as D
r0, r1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (100, 600)
Z = {'us': collections.Counter(), 'them': collections.Counter()}
games = 0
for us, res, mp, meta, rows in D.games([sys.argv[1]]):
    games += 1
    for r in rows:
        if not (r0 <= r['r'] < r1): continue
        for c in r['c']:
            if not c['a'] or 'x' not in c: continue
            side = D.who(c['t'], us)
            x, y = c['x'], c['y']
            # team 0 spawn rows 0-2 (top), team 1 rows 28-30 (bottom); own half = rows nearer own spawn
            own_top = c['t'] == 0
            if 13 <= y <= 17:
                band = 'L' if x <= 6 else 'R' if x >= 29 else 'C' if 13 <= x <= 23 else 'mid'
                Z[side]['corridor_' + band] += 1
            elif (y < 13) == own_top:
                Z[side]['own_half'] += 1
            else:
                Z[side]['their_half'] += 1
            # inside pocket (own side's pocket rows 11-12 or 18-19, x 15-21)
            if 15 <= x <= 21 and (11 <= y <= 12 or 18 <= y <= 19):
                Z[side]['pocket_' + ('own' if (y < 15) == own_top else 'their')] += 1
print(games, 'games, rounds', r0, r1, 'champion-rounds per game')
keys = sorted(set(Z['us']) | set(Z['them']))
for k in keys: print(f'{k:16} us {Z["us"][k] / games:7.1f}  them {Z["them"][k] / games:7.1f}')
