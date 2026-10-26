"""What a champion does when an enemy champion comes into sight, by the bag it carries: python -I tools/replay/carrier.py DIR...

An encounter is a round (to r1000) where an enemy champion is within 8 tiles of a living champion and none was in the
previous 5 rounds. Per side ("us" is the index's team) and bag (0, 1-29, 30+) and enemies within 8 (1, 2+), per game:
encounters, then over the next rounds: P(died within 15), P(tribute started within 15), P(hit an enemy champion within
10), mean change of the distance to the nearest enemy after 5 rounds (+ = moved away), the mean distance to the nearest
altar at the encounter and its change after 10 rounds (- = towards; altars are the tiles tributes were made from), and
the bag lost per game in those deaths. Use it to compare how carriers of both teams react (b10 mw1: our carriers die
2.25x as often per carrying round).
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D


def bag_class(g):
    return '0' if g == 0 else '1-29' if g < 30 else '30+'


A = collections.defaultdict(lambda: collections.defaultdict(float)); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    altars = {(x[1], x[2]) for b in rows for acts in b['act'][:n] for x in acts if x[0] == 'tribute'}
    last_seen = collections.defaultdict(lambda: -99)
    end = next((k for k, r in enumerate(rows) if r['r'] > 1000), len(rows))
    for k in range(end):
        b = rows[k]
        for i in range(n):
            c = b['c'][i]
            if not c['a'] or 'x' not in c: continue
            p = (c['x'], c['y'])
            foes = [(o['x'], o['y']) for o in b['c'] if o['a'] and 'x' in o and o['t'] != c['t'] and D.dist((o['x'], o['y']), p) <= 8]
            if not foes: continue
            fresh = b['r'] - last_seen[i] > 5
            last_seen[i] = b['r']
            if not fresh: continue
            key = (D.who(c['t'], us), bag_class(c.get('g', 0)), '1' if len(foes) == 1 else '2+')
            S = A[key]
            S['n'] += 1
            if altars: S['altar0'] += min(D.dist(p, a) for a in altars)
            died = trib = hit = False
            for j in range(k + 1, min(len(rows), k + 16)):
                cj = rows[j]['c'][i]
                if any(x[0] == 'tribute' for x in rows[j]['act'][i]): trib = True
                if j <= k + 10 and D.enemy_hits(rows[j], i, n): hit = True
                if not cj['a']:
                    died = True; S['lost'] += rows[j - 1]['c'][i].get('g', 0); break
            S['died'] += died; S['trib'] += trib; S['hit'] += hit
            j5 = min(len(rows) - 1, k + 5); c5 = rows[j5]['c'][i]
            if c5['a'] and 'x' in c5:
                q = (c5['x'], c5['y'])
                now = min(D.dist(p, f) for f in foes)
                later = min((D.dist(q, (o['x'], o['y'])) for o in rows[j5]['c'] if o['a'] and 'x' in o and o['t'] != c['t']), default=now)
                S['away'] += later - now; S['away n'] += 1
            j10 = min(len(rows) - 1, k + 10); c10 = rows[j10]['c'][i]
            if altars and c10['a'] and 'x' in c10:
                S['altar'] += min(D.dist((c10['x'], c10['y']), a) for a in altars) - min(D.dist(p, a) for a in altars); S['altar n'] += 1
print(f'{ng} games to r1000. Per game: encounters (bag, enemies within 8), then P(died 15) P(tribute 15) P(hit 10), '
      f'distance change to the nearest enemy after 5 (+ away), altar distance then and its change after 10 (- towards), bag lost')
for bag in ('0', '1-29', '30+'):
    for ec in ('1', '2+'):
        line = []
        for w in ('us', 'them'):
            S = A[(w, bag, ec)]
            if not S['n']: line.append(f'{w} -'); continue
            line.append(f"{w} {S['n'] / ng:5.2f}: died {S['died'] / S['n']:.2f} trib {S['trib'] / S['n']:.2f} hit {S['hit'] / S['n']:.2f}"
                        f" away {S['away'] / max(1, S['away n']):+.1f} altar {S['altar0'] / S['n']:.0f}{S['altar'] / max(1, S['altar n']):+.1f} lost {S['lost'] / ng:5.1f}")
        print(f'  bag {bag:4} e{ec:2} | ' + ' | '.join(line))
