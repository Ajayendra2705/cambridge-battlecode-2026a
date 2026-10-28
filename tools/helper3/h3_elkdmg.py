"""Elk hits taken per game, us vs them, to round R, split by whether the victim was farming that elk's group (h3, 10-28).

usage: python -I tools/helper3/h3_elkdmg.py [--upto R] DIR [DIR ...]      (default R 1000; decoded runs, pooled)

Inferred, as tools/replay/tankalone.py does (the replays do not list camp attacks): groups are `decoded.camp_groups`;
a group counts as awake in a round if any of its camps was hit in that round or the two before (a hit wakes the whole
group, and a camp sleeps 2 rounds after nobody is in reach). Each live elk of an awake group hits the nearest
champion within 4 tiles (rounds where the nearest of both teams tie are skipped) for 60, before Jungle. A hit is
"farming" when the victim hit a camp of that group in the last 3 rounds, else "bystander" (an elk of a group the
victim was not hitting, e.g. a neighbour group woken beside the one it farms). Prints hits and damage per game, the
bystander share, and deaths within 3 rounds of a bystander elk hit.
"""
import collections, os, sys

sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]
R = 1000
if '--upto' in args:
    i = args.index('--upto'); R = int(args[i + 1]); del args[i:i + 2]
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    camps = {int(k): v for k, v in meta.get('camps', {}).items()}
    pos = {}
    for r in rows:
        for i in range(n):
            for x in D.camp_hits(r, i): pos[x[-1]] = (x[-4], x[-3])
    grp, members, gtiles = D.camp_groups(rows, n)
    elks = [j for j in pos if D.CAMPS.get(camps.get(j)) == 'elk']
    last_hit = {}  # group -> last round any camp of it was hit
    mine = {}      # (champion, group) -> last round that champion hit the group
    bys = collections.defaultdict(list)  # champion -> rounds of bystander elk hits
    for k, r in enumerate(rows):
        if r['r'] > R: break
        for i in range(n):
            for x in D.camp_hits(r, i):
                g = grp.get(x[-1])
                if g is not None: last_hit[g] = r['r']; mine[i, g] = r['r']
        for j in elks:
            g = grp.get(j)
            if g is None or r['r'] - last_hit.get(g, -99) > 2 or j >= len(r['mh']) or r['mh'][j] <= 0: continue
            best, who = 99, []
            for i, c in enumerate(r['c']):
                if not c['a'] or 'x' not in c: continue
                d = D.dist(pos[j], (c['x'], c['y']))
                if d > 4: continue
                if d < best: best, who = d, [i]
                elif d == best: who.append(i)
            if not who or len({r['c'][i]['t'] for i in who}) > 1: continue
            i = who[0]; w = 'us' if r['c'][i]['t'] == us else 'them'
            kind = 'farming' if r['r'] - mine.get((i, g), -99) <= 3 else 'bystander'
            C[w, kind] += 1
            if kind == 'bystander': bys[i].append(r['r'])
    for k in range(1, len(rows)):
        q, r = rows[k - 1], rows[k]
        if r['r'] > R: break
        for i in range(n):
            if q['c'][i]['a'] and not r['c'][i]['a'] and any(0 <= r['r'] - t <= 3 for t in bys.get(i, ())):
                C['us' if q['c'][i]['t'] == us else 'them', 'died'] += 1
print(f'{ng} games to r{R}: elk hits taken per game (x60 damage, before Jungle): ' + ', '.join(args))
for w in ('us', 'them'):
    f, b = C[w, 'farming'] / ng, C[w, 'bystander'] / ng
    print(f'  {w:4} all {f + b:6.1f} ({(f + b) * 60:6.0f} dmg)  farming {f:6.1f}  bystander {b:5.1f} ({b / max(1e-9, f + b):4.0%})'
          f'  deaths within 3 rounds of a bystander hit {C[w, "died"] / ng:.2f}')
