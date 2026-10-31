# Two-tile oscillation runs to r1000, us vs them: a living champion alternates between the same two tiles for 6+ rounds
# (A,B,A,B,...) with no attack or cast in the run (moves and wards only). Per game: runs and champion-rounds, split by
# bag (20+ gems or less) and by whether an enemy champion stood within 6 at the run's start; then the longest examples
# (map, round, length, type, tiles, bag, nearest altar distance). Found the step_field ping-pong of bb2 (10-31): at a
# dead end of the walking field (a live camp on the way) the local search steps back and the next turn's field step
# returns, so 02guardians carriers rocked beside the altar's live guard and gave up banking.
# usage: python -I tools/replay/osc.py DIR... [--min N]
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
args = sys.argv[1:]; MIN = 6
if '--min' in args: i = args.index('--min'); MIN = int(args[i + 1]); args = args[:i] + args[i + 2:]
C = collections.Counter(); L = collections.Counter(); ng = 0; ex = []
for us, res, mp, meta, rows in D.games(args):
    ng += 1; n = len(rows[0]['c'])
    altars = set()
    for r in rows:
        for i in range(min(n, len(r['act']))):
            for x in r['act'][i]:
                if x[0] == 'tribute': altars.add((x[1], x[2]))
    R = min(len(rows), 1000)
    for i in range(n):
        k = 1
        while k < R:
            c0 = rows[k]['c'][i]
            if not c0['a'] or 'x' not in c0: k += 1; continue
            a = (c0['x'], c0['y']); b = None; j = k + 1
            while j < R:
                c = rows[j]['c'][i]
                if not c['a'] or 'x' not in c: break
                p = (c['x'], c['y'])
                acts = rows[j]['act'][i] if i < len(rows[j]['act']) else []
                if any(x[0] in ('attack', 'cast', 'tribute') for x in acts): break
                want = a if (j - k) % 2 == 0 else b
                if b is None and (j - k) == 1 and p != a: b = p; j += 1; continue
                if p != want: break
                j += 1
            ln = j - k
            if b is not None and ln >= MIN:
                s = D.who(c0['t'], us)
                en = any(o['a'] and 'x' in o and D.who(o['t'], us) != s and D.dist(a, (o['x'], o['y'])) <= 6 for o in rows[k]['c'])
                bag = c0.get('g', 0)
                key = (s, 'bag20' if bag >= 20 else 'bag<20', 'enemy6' if en else 'quiet')
                C[key] += 1; L[key] += ln
                ad = min(D.dist(a, al) for al in altars) if altars else 99
                ex.append((ln, s, mp, rows[k]['r'], D.NAMES[c0['ty']], a, b, bag, ad))
                k = j
            else:
                k += 1
print(f'{ng} games, two-tile runs of {MIN}+ rounds without attack or cast, per game (champion-rounds per game)')
for bag in ('bag20', 'bag<20'):
    for en in ('quiet', 'enemy6'):
        print(f"  {bag:6} {en:6}  us {C[('us', bag, en)] / ng:5.2f} ({L[('us', bag, en)] / ng:5.1f})   them {C[('them', bag, en)] / ng:5.2f} ({L[('them', bag, en)] / ng:5.1f})")
print('longest (length, side, map, round, type, tile A, tile B, bag, altar distance):')
for e in sorted(ex, reverse=True)[:30]: print('  ', e)
