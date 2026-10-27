"""Deaths to enemy packs and what champions do on sighting one, us vs the rivals, to a round (default 1000).

usage: python -I tools/replay/packs.py DIR [DIR ...] [--round R]

Deaths: per game by enemies minus allies within 6 of the victim at its last alive round (victim excluded), and the
"outnumbered" total (2 or more). Sightings: a champion with at most one ally within 6 gets 2+ enemy champions within 8
(off their spawn) after 5+ rounds without; over the next 5 rounds its rounds hitting champions and camps, and whether
it dies within 15 rounds. Big sightings are those with 3+ enemies within 8. DIR is a decoded folder
(tools/replay/decode_run.sh). Judged pa1 (10-27).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

args = sys.argv[1:]
R = 1000
if '--round' in args:
    k = args.index('--round'); R = int(args[k + 1]); del args[k:k + 2]
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    quiet = collections.Counter()
    for k in range(1, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > R: break
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if not pc['a'] or c['a'] or 'x' not in pc: continue
            t = pc['t']; w = D.who(t, us); p = (pc['x'], pc['y'])
            e6 = sum(1 for o in a['c'] if o['a'] and 'x' in o and o['t'] != t and D.dist((o['x'], o['y']), p) <= 6)
            a6 = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == t and D.dist((o['x'], o['y']), p) <= 6)
            d = e6 - a6
            C[(w, 'deaths')] += 1
            C[(w, 'no enemy' if e6 == 0 else '-1 or less' if d <= -1 else '0' if d == 0 else '+1' if d == 1 else '+2' if d == 2 else '+3 or more')] += 1
            C[(w, 'outnumbered')] += d >= 2
        if k + 16 >= len(rows): continue
        for i in range(n):
            q = a['c'][i]
            if not (q['a'] and 'x' in q): quiet[i] = 0; continue
            t = q['t']; pos = (q['x'], q['y'])
            foes = sum(1 for o in a['c'] if o['a'] and 'x' in o and o['t'] != t and (o['x'], o['y']) not in spawn[1 - t]
                       and D.dist(pos, (o['x'], o['y'])) <= 8)
            allies = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == t and D.dist(pos, (o['x'], o['y'])) <= 6)
            if foes < 2 or allies > 1:
                if foes < 2: quiet[i] += 1
                continue
            fresh = quiet[i] >= 5
            quiet[i] = 0
            if not fresh: continue
            w = D.who(t, us)
            hitc = sum(1 for kk in range(k - 1, k + 4) if D.enemy_hits(rows[kk], i, n))
            hitm = sum(1 for kk in range(k - 1, k + 4) if D.camp_hits(rows[kk], i))
            died = any(not rows[kk]['c'][i]['a'] for kk in range(k, k + 15))
            for key in ('seen', 'seen 3+') if foes >= 3 else ('seen',):
                C[(w, key)] += 1; C[(w, key + ' hitc')] += hitc; C[(w, key + ' hitm')] += hitm; C[(w, key + ' died')] += died

print(f'{ng} games to r{R}: deaths per game by enemies minus allies within 6 at the death')
for key in ('deaths', 'no enemy', '-1 or less', '0', '+1', '+2', '+3 or more', 'outnumbered'):
    print(f'  {key:12} us {C[("us", key)] / max(1, ng):5.2f}  them {C[("them", key)] / max(1, ng):5.2f}')
print('pack sightings (2+ enemies within 8, at most one ally within 6, after 5 quiet rounds): per game, next 5 rounds '
      'hitting champions / camps, died within 15')
for key in ('seen', 'seen 3+'):
    for w in ('us', 'them'):
        m = max(1, C[(w, key)])
        print(f'  {key:8} {w:4} {C[(w, key)] / max(1, ng):5.1f}  hit champions {C[(w, key + " hitc")] / m:.2f}  camps '
              f'{C[(w, key + " hitm")] / m:.2f}  died {C[(w, key + " died")] / m:.3f}')
