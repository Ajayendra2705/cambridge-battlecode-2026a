"""Do we convert leads? python -I tools/replay/leads.py DIR [DIR ...]

At r300, r600, r1000 and r1500, for games still running: who leads in gems in hand (tributed plus bags) and in team gold, how often the leader wins, and the same for the rival's leads. If our leads are overturned
more often than theirs, the game is lost late; if we rarely lead at r300, it is lost early. Also prints wins by how the game ended (r2000 or earlier) and the mean round of the end.
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

dirs = sys.argv[1:]
CP = (300, 600, 1000, 1500)
T = collections.defaultdict(collections.Counter)
E = collections.Counter()
for us, res, mp, meta, rows in D.games(dirs):
    win = res == 'win'
    end = rows[-1]['r']
    E['n'] += 1
    E['w'] += win
    b = 'r2000' if end >= 1999 else 'early'
    E[b + '_n'] += 1
    E[b + '_w'] += win
    E['endsum'] += end
    k = 0
    last = None
    for x in rows:
        while k < len(CP) and x['r'] >= CP[k]:
            r = CP[k]
            hand = lambda t: x['sg'][t] + sum(c.get('g', 0) for c in x['c'] if c['t'] == t)
            gold = lambda t: sum(D.gold_held(meta, c) for c in x['c'] if c['t'] == t)
            alive = lambda t: sum(c['a'] for c in x['c'] if c['t'] == t)
            hu, ht = hand(us), hand(1 - us)
            gu, gt = gold(us), gold(1 - us)
            t = T[r]
            t['n'] += 1
            t['w'] += win
            for name, a, c in (('hand', hu, ht), ('gold', gu, gt)):
                if a > c * 1.05:
                    t[name + '_us'] += 1
                    t[name + '_us_w'] += win
                elif c > a * 1.05:
                    t[name + '_them'] += 1
                    t[name + '_them_w'] += win
                else:
                    t[name + '_even'] += 1
                    t[name + '_even_w'] += win
            t['hu'] += hu
            t['ht'] += ht
            t['gu'] += gu
            t['gt'] += gt
            k += 1
print(f"{E['n']} games, {E['w']} wins; ended at r2000 {E['r2000_n']} (wins {E['r2000_w']}), earlier {E['early_n']} (wins {E['early_w']}); mean end r{E['endsum'] / max(1, E['n']):.0f}")
print('round games wins | gems in hand us/them | we lead n, win% | even n, win% | they lead n, win% || gold us/them | we lead n, win% | they lead n, win%')
for r in CP:
    t = T[r]
    n = max(1, t['n'])
    pc = lambda a, b: f"{t[a]:4d} {100 * t[b] / max(1, t[a]):3.0f}%"
    print(f"r{r:<5d}{t['n']:4d} {t['w']:4d} | {t['hu'] / n:5.0f}/{t['ht'] / n:5.0f} | {pc('hand_us', 'hand_us_w')} | {pc('hand_even', 'hand_even_w')} | {pc('hand_them', 'hand_them_w')} || {t['gu'] / n:6.0f}/{t['gt'] / n:6.0f} | {pc('gold_us', 'gold_us_w')} | {pc('gold_them', 'gold_them_w')}")
