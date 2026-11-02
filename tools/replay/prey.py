"""Hurt enemies near healthy champions: do they get chased and killed, us as hunters vs the rivals as hunters.

usage: python -I tools/replay/prey.py DIR [DIR ...] [--round R] [--frac F]   (defaults: to r1000, prey under 50% health)

An episode starts when a living champion (off its spawn) is under F of its max health with a healthy (50%+) enemy champion within 6, after 15
rounds of that not holding. Per episode, for the hunters (healthy enemies within 6 at the start): whether the nearest hunter closes in over
the next 4 rounds (closer / same / away from the prey's new place), hits on the prey in the next 10 rounds, the prey's death within 15 rounds
(any cause), and who else died. Split by hunters' numbers (1, 2, 3+), by distance (1-3, 4-6), by the prey's health band, and by round band.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

args = sys.argv[1:]
R, F = 1000, 0.5
if '--round' in args:
    k = args.index('--round'); R = int(args[k + 1]); del args[k:k + 2]
if '--frac' in args:
    k = args.index('--frac'); F = float(args[k + 1]); del args[k:k + 2]
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    spawn = {t: {(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c} for t in (0, 1)}
    quiet = collections.Counter()
    for k in range(len(rows) - 16):
        a = rows[k]
        if a['r'] > R: break
        for i in range(n):
            q = a['c'][i]
            if not (q['a'] and 'x' in q) or (q['x'], q['y']) in spawn[q['t']]: quiet[i] += 1; continue
            p = (q['x'], q['y'])
            hunters = [j for j, o in enumerate(a['c']) if o['a'] and 'x' in o and o['t'] != q['t'] and o['hp'] >= 0.5 * o['mhp'] and D.dist(p, (o['x'], o['y'])) <= 6]
            if not (hunters and q['hp'] < F * q['mhp']): quiet[i] += 1; continue
            fresh = quiet[i] >= 15
            quiet[i] = 0
            if not fresh: continue
            w = D.who(1 - q['t'], us)   # the hunters' side
            d0 = min(D.dist(p, (a['c'][j]['x'], a['c'][j]['y'])) for j in hunters)
            b = rows[k + 4]['c'][i]
            died = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 16))
            hits = 0
            for kk in range(k, k + 10):
                row = rows[kk]
                for j in range(n):
                    if row['c'][j]['t'] == q['t']: continue
                    hits += sum(1 for x in D.enemy_hits(row, j, n) if x[-1] == i)
            cls = 'dead'
            if b['a'] and 'x' in b:
                ds = [D.dist((b['x'], b['y']), (rows[k + 4]['c'][j]['x'], rows[k + 4]['c'][j]['y'])) for j in hunters if rows[k + 4]['c'][j]['a'] and 'x' in rows[k + 4]['c'][j]]
                d4 = min(ds) if ds else 99
                cls = 'closer' if d4 < d0 else 'same' if d4 == d0 else 'away'
            lost = sum(1 for j in hunters if any(not rows[kk]['c'][j]['a'] for kk in range(k + 1, k + 16)))
            frac = q['hp'] / q['mhp']
            keys = ['all', f'hunters {min(len(hunters), 3)}', f'dist {"1-3" if d0 <= 3 else "4-6"}', f'hp {"<25" if frac < .25 else "25-50"}',
                    f'round {"<=300" if a["r"] <= 300 else "<=600" if a["r"] <= 600 else ">600"}', f'prey {D.NAMES[q["ty"]]}']
            for key in keys:
                C[(w, key, 'n')] += 1; C[(w, key, 'died')] += died; C[(w, key, cls)] += 1; C[(w, key, 'hits')] += hits; C[(w, key, 'lost')] += lost
                C[(w, key, cls, 'died')] += died
print(f'{ng} games to r{R}, prey under {F:.0%} with a healthy enemy within 6: as hunters, episodes/game, kills, hunter gap after 4 rounds and kill rate in each')
keys = sorted({k[1] for k in C}, key=str)
for key in keys:
    for w in ('us', 'them'):
        m = C[(w, key, 'n')]
        if not m: continue
        parts = ' '.join(f'{c} {C[(w, key, c)] / m:.2f} (kill {C[(w, key, c, "died")] / max(1, C[(w, key, c)]):.2f})' for c in ('closer', 'same', 'away'))
        print(f'{key:16}{w:5} {m / ng:5.2f}/g kill {C[(w, key, "died")] / m:.3f} hits {C[(w, key, "hits")] / m:4.2f} hunters lost {C[(w, key, "lost")] / m:.2f} | {parts}')
