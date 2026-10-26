"""Fight episodes by the victim's response, us vs them, to round R: python -I tools/replay/response.py R DIR...
Episode: an enemy champion hits a champion at 50%+ health that no enemy champion hit in the 8 rounds before.
Over the next W rounds (stopping at its death): share of rounds it hit a champion, share it moved away from the nearest
enemy. Response: fought (hit 50%+ of rounds), ran (hit under 20% and moved away 40%+), mixed (else).
Outcome within W rounds: it died; an enemy champion within 6 of it at the start died (a kill for its side)."""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
R, W = int(sys.argv[1]), 12
A = collections.Counter(); ng = 0
def pos(o): return (o['x'], o['y'])
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    last_hit = collections.defaultdict(lambda: -99)
    for k in range(len(rows) - 1):
        a = rows[k]
        if a['r'] > R: break
        victims = {}
        for i in range(n):
            for x in D.enemy_hits(a, i, n): victims.setdefault(x[-1], i)
        for v, att in victims.items():
            fresh = a['r'] - last_hit[v] > 8
            last_hit[v] = a['r']
            c = a['c'][v]
            if not fresh or not c['a'] or 'x' not in c or c['hp'] < 0.5 * c['mhp']: continue
            foes = [j for j, o in enumerate(a['c']) if o['a'] and 'x' in o and o['t'] != c['t'] and D.dist(pos(c), pos(o)) <= 6]
            mates = [j for j, o in enumerate(a['c']) if j != v and o['a'] and 'x' in o and o['t'] == c['t'] and D.dist(pos(c), pos(o)) <= 6]
            hits = away = rounds = 0; died = False; killed = False
            for kk in range(k, min(len(rows) - 1, k + W)):
                r0, r1 = rows[kk], rows[kk + 1]
                me0, me1 = r0['c'][v], r1['c'][v]
                if not me0['a']: break
                rounds += 1
                if D.enemy_hits(r0, v, n): hits += 1
                es = [pos(o) for o in r0['c'] if o['a'] and 'x' in o and o['t'] != c['t']]
                if es and 'x' in me1 and 'x' in me0 and pos(me1) != pos(me0):
                    if min(D.dist(pos(me1), q) for q in es) > min(D.dist(pos(me0), q) for q in es): away += 1
                if not me1['a']: died = True; break
                if any(r0['c'][j]['a'] and not r1['c'][j]['a'] for j in foes): killed = True
            if rounds == 0: continue
            resp = 'fought' if hits >= 0.5 * rounds else 'ran' if hits < 0.2 * rounds and away >= 0.4 * rounds else 'mixed'
            w = D.who(c['t'], us)
            odds = 'outnumbered' if len(foes) > len(mates) + 1 else 'even' if len(foes) == len(mates) + 1 else 'outnumbering'
            for key in (('all', resp), (D.NAMES[c['ty']], resp), (odds, resp)):
                A[(w,) + key + ('n',)] += 1; A[(w,) + key + ('died',)] += died; A[(w,) + key + ('killed',)] += killed
print(f'{ng} games to r{R}: fight episodes on a champion at 50%+ health, per game, by response over {W} rounds: '
      'count (P it died, P an enemy near died)')
groups = ['all', 'even', 'outnumbered', 'outnumbering'] + sorted({k[1] for k in A if k[1] in D.NAMES})
for g in groups:
    line = f'  {g:12}'
    for w in ('us', 'them'):
        line += f'  {w}:'
        for resp in ('fought', 'mixed', 'ran'):
            nn = A[(w, g, resp, 'n')]
            if nn: line += f' {resp} {nn / ng:4.1f} ({A[(w, g, resp, "died")] / nn:.2f}, {A[(w, g, resp, "killed")] / nn:.2f})'
    print(line)
