# Carriers (bag 20+) under 35% health to r1000, split by "quiet" (no enemy champion within 8 of the champion in the
# last 30 rounds, our proxy for the bot's enemy_seen_round) and by whether it moved homewards / was hit by a camp this
# round; deaths per 100 rounds in each. Us vs them.
# usage: python -I tools/replay/lowquiet.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    start = {i: (rows[0]['c'][i].get('x'), rows[0]['c'][i].get('y')) for i in range(n)}
    seen = collections.defaultdict(lambda: -100)
    for k in range(len(rows) - 1):
        r, nx = rows[k], rows[k + 1]
        if r['r'] > 1000: break
        for i in range(n):
            p = r['c'][i]
            if not (p['a'] and 'x' in p): continue
            pos = (p['x'], p['y'])
            if any(e['a'] and 'x' in e and e['t'] != p['t'] and D.dist(pos, (e['x'], e['y'])) <= 8 for e in r['c']): seen[i] = k
            if p.get('g', 0) < 20 or p['hp'] >= 0.35 * p['mhp']: continue
            w = D.who(p['t'], us)
            q = 'quiet' if k - seen[i] > 30 else 'seen'
            c2 = nx['c'][i]
            home = c2['a'] and 'x' in c2 and D.dist((c2['x'], c2['y']), start[i]) < D.dist(pos, start[i])
            C[(w, q, 'r')] += 1; C[(w, q, 'd')] += not c2['a']; C[(w, q, 'home')] += home
print(f'{ng} games to r1000: carriers under 35% health, rounds per game / homeward share / deaths per 100 rounds')
for w in ('us', 'them'):
    print(f'  {w:4} ' + '   '.join(f"{q}: {C[(w, q, 'r')] / ng:5.1f} / {C[(w, q, 'home')] / max(1, C[(w, q, 'r')]):.2f} / {100 * C[(w, q, 'd')] / max(1, C[(w, q, 'r')]):.2f}" for q in ('quiet', 'seen')))
