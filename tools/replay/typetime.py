# Per champion type and side, rounds per game to R: alive, hitting camps, moving, idle (alive, no move, no hit), near a
# teammate (within 3), alone (no teammate within 6); capture rounds (a gem gain without a kill on a group tile) and their
# gems. usage: python -I tools/replay/typetime.py R DIR...   (decoded dirs, e.g. data/fights/main_b30_b30)
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
R = int(sys.argv[1]); A = collections.defaultdict(collections.Counter); G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    n = len(rows[0]['c']); grp, members, gtiles = D.camp_groups(rows, n)
    seen = set()
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        if b['r'] > R: break
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c and 'x' in pc): continue
            key = (D.who(c['t'], us), D.NAMES[c['ty']])
            if (key, id(rows)) not in seen: seen.add((key, id(rows))); G[key] += 1
            x = A[key]; x['alive'] += 1
            hit = bool(D.camp_hits(b, i)); mv = (c['x'], c['y']) != (pc['x'], pc['y'])
            x['camp'] += hit; x['move'] += mv; x['idle'] += not hit and not mv and not D.enemy_hits(b, i, n)
            mates = [o for j, o in enumerate(b['c']) if j != i and o['t'] == c['t'] and o['a'] and 'x' in o]
            dm = min([D.dist((c['x'], c['y']), (o['x'], o['y'])) for o in mates] or [99])
            x['near3'] += dm <= 3; x['alone6'] += dm > 6
            if c.get('g', 0) > pc.get('g', 0) and c.get('k', 0) <= pc.get('k', 0) and any((c['x'], c['y']) in t for t in gtiles.values()):
                x['caps'] += 1; x['capgems'] += c['g'] - pc['g']
print(f'per game to r{R}: rounds alive, hitting camps, moving, idle, a teammate within 3, none within 6; capture rounds and their gems')
for key in sorted(A, key=lambda k: (k[1], k[0])):
    x, g = A[key], max(1, G[key])
    print(f'  {key[1]:9} {key[0]:4} games {g:3} alive {x["alive"]/g:5.0f} camp {x["camp"]/g:4.0f} move {x["move"]/g:4.0f} idle {x["idle"]/g:4.0f}'
          f' near3 {x["near3"]/g:4.0f} alone6 {x["alone6"]/g:4.0f} caps {x["caps"]/g:5.1f} capgems {x["capgems"]/g:5.0f}')
