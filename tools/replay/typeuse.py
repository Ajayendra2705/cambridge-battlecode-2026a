"""Where a champion type's rounds go: python -I typeuse.py RMAX DIR...  Per type and side: rounds to RMAX dead, hitting a camp, hitting a champion, moving, still; camp hits by kind unknown; captures (events), gold per capture, enemies in sight share."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
RMAX, dirs = int(sys.argv[1]), sys.argv[2:]
A = collections.defaultdict(collections.Counter)
for us, res, mp, meta, rows in D.games(dirs):
    n = len(rows[0]['c'])
    for i, c0 in enumerate(rows[0]['c']):
        s = A[(D.who(c0['t'], us), D.NAMES[c0['ty']])]
        s['n'] += 1
        prev = None
        for k, r in enumerate(rows):
            if r['r'] > RMAX or k + 1 >= len(rows):
                break
            c = r['c'][i]; nx = rows[k + 1]['c'][i]
            if not c['a']:
                s['dead'] += 1
                continue
            ca = bool(D.camp_hits(r, i))
            acts = r['act'][i] if i < len(r['act']) else []
            ch = any(x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' for x in acts)
            mv = 'x' in c and 'x' in nx and (c['x'], c['y']) != (nx['x'], nx['y'])
            if ca: s['camp'] += 1
            elif ch: s['champ'] += 1
            elif mv: s['move'] += 1
            else: s['still'] += 1
            if nx['a']:
                d = D.gold_held(meta, nx) - D.gold_held(meta, c)
                if d > 0:
                    s['ev'] += 1; s['gold'] += d
print(f'to r{RMAX}: type side n | dead camp champ move still | gold-events gold/event')
for ty in ('vesper', 'marcella', 'vendetta', 'heart', 'willow'):
    for w in ('us', 'them'):
        s = A[(w, ty)]; m = max(1, s['n'])
        if s['n'] < 10:
            continue
        print(f"{ty:9} {w:4} {s['n']:3} | {s['dead']/m:5.1f} {s['camp']/m:5.1f} {s['champ']/m:5.1f} {s['move']/m:5.1f} {s['still']/m:5.1f} | {s['ev']/m:5.1f} {s['gold']/max(1,s['ev']):5.1f}")
