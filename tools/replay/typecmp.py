"""What each champion type does, us against them: python -I tools/replay/typecmp.py RMAX DIR [DIR ...]

Per team-game of a type, to round RMAX: alive rounds, casts of slot 0 and slot 1 per 100 alive rounds, hits on champions and camps per 100 alive rounds, gems gained, deaths, kills, and gold held and
maximum health at the end of the window. Gems gained counts rises of the bag outside tribute. Shows a type we play worse than the rivals do (a healer that seldom casts, a carry that never hits).
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

R, dirs = int(sys.argv[1]), sys.argv[2:]
C = collections.defaultdict(collections.Counter)
for us, res, mp, meta, rows in D.games(dirs):
    n = len(rows[0]['c'])
    types = {i: D.NAMES[rows[0]['c'][i]['ty']] for i in range(n)}
    seen = set()
    last = None
    prev = None
    for x in rows:
        if x['r'] > R:
            break
        last = x
        for i in range(n):
            c = x['c'][i]
            w = D.who(c['t'], us)
            k = (types[i], w)
            if (i,) not in seen:
                seen.add((i,))
                C[k]['games'] += 1
            if c['a']:
                C[k]['alive'] += 1
            for a in (x['act'][i] if i < len(x['act']) else []):
                if a[0] == 'cast':
                    C[k]['cast%d' % a[1]] += 1
                elif a[0] == 'attack' and len(a) > 3:
                    C[k]['hit_' + ('champ' if a[3] == 'c' else 'camp' if a[3] == 'm' else 'other')] += 1
            if prev is not None:
                p = prev['c'][i]
                if p['a'] and not c['a']:
                    C[k]['deaths'] += 1
                if p['a'] and c['a'] and c.get('g', 0) > p.get('g', 0):
                    C[k]['gems'] += c.get('g', 0) - p.get('g', 0)
                if c.get('k', 0) > p.get('k', 0):
                    C[k]['kills'] += c.get('k', 0) - p.get('k', 0)
        prev = x
    if last is not None:
        for i in range(n):
            c = last['c'][i]
            k = (types[i], D.who(c['t'], us))
            C[k]['gold'] += D.gold_held(meta, c)
            C[k]['mhp'] += c.get('mhp', 0)
            C[k]['alive_end'] += c['a']
print(f'to r{R}, per team-game; us then them on each line')
print('type       games alive | cast0/100 cast1/100 | champ/100 camp/100 | gems deaths kills | gold maxhp(alive at end)')
for ty in D.NAMES:
    for w in ('us', 'them'):
        t = C.get((ty, w))
        if not t or t['games'] < 3:
            continue
        g = t['games']
        al = max(1, t['alive'])
        print(f"{ty:9s} {w:4s} {g:4d} {t['alive'] / g:5.0f} | {100 * t['cast0'] / al:5.1f} {100 * t['cast1'] / al:5.1f} | {100 * t['hit_champ'] / al:5.1f} {100 * t['hit_camp'] / al:5.1f} | {t['gems'] / g:5.0f} {t['deaths'] / g:4.1f} {t['kills'] / g:4.1f} | {t['gold'] / g:6.0f} {t['mhp'] / max(1, t['alive_end']):6.0f}")
