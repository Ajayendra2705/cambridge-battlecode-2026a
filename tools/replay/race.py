"""Middle-group race detail, to round R: python -I tools/replay/race.py R DIR... [--kind KIND] [--region own|middle|enemy]
For every captured middle life (decoded.py lives' definition), at the round the group came up: each side's nearest live
champion (Chebyshev distance to the group's tiles) and how many champions each side had within 10; whether our side ever
hit it during that life; and, when the enemy hit first, the first thing our nearest champion did in the next 40 rounds
(fought, hit camps of another group nearer / farther than this one, went home, tributed, hit this group late, died).
Splits by who hit first, by opening (life starting at the first round) or respawn, and by who was nearer at the start.
--kind keeps groups of one kind (camp types joined by +, as tools/replay/capkind.py names them, e.g. gem); --region
looks at the groups of another region (from our side) instead of the middle.
"""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

args = sys.argv[1:]; KIND = None; REG = 'middle'
if '--kind' in args:
    k = args.index('--kind'); KIND = args[k + 1]; args = args[:k] + args[k + 2:]
if '--region' in args:
    k = args.index('--region'); REG = args[k + 1]; args = args[:k] + args[k + 2:]
R = int(args[0])
A = collections.Counter(); V = collections.defaultdict(list); ng = 0
for us, res, mp, meta, rows in D.games(args[1:]):
    ng += 1
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    region = {}
    for g, ts in gtiles.items():
        do = min(D.dist(p, q) for p in ts for q in start[us]); de = min(D.dist(p, q) for p in ts for q in start[1 - us])
        region[g] = 'own' if do < de - 3 else 'enemy' if de < do - 3 else 'middle'
    rix = {r['r']: k for k, r in enumerate(rows)}
    ctype = {int(k): v for k, v in (meta.get('camps') or {}).items()}
    if KIND:
        members = {g: js for g, js in members.items() if '+'.join(D.CAMPS.get(t, '?') for t in sorted({ctype.get(j, -1) for j in js})) == KIND}

    def near(row, g, side):
        ds = [min(D.dist((c['x'], c['y']), q) for q in gtiles[g]) for c in row['c'] if c['a'] and 'x' in c and D.who(c['t'], us) == side]
        return (min(ds) if ds else 99), sum(1 for d in ds if d <= 10), ds

    # life: [up round, first hitter, first hit round, hitters set, start snapshot]
    def new_life(k, g):
        row = rows[k]
        return [row['r'], None, None, set(), (near(row, g, 'us'), near(row, g, 'them'))]
    life = {g: new_life(0, g) for g in members}
    dead, claimed = set(), set()
    for k, (a, b) in enumerate(zip(rows, rows[1:])):
        if b['r'] > R: break
        for i in range(n):
            for x in D.camp_hits(a, i):
                g = grp.get(x[-1])
                if g is None or g not in life or g in dead or g in claimed: continue
                w = D.who(a['c'][i]['t'], us)
                life[g][3].add(w)
                if life[g][1] is None: life[g][1] = w; life[g][2] = a['r']
        for g, js in members.items():
            if g not in dead and g not in claimed and any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js): dead.add(g)
            if (g in dead or g in claimed) and all(b['mh'][j] > 0 for j in js) and any(a['mh'][j] == 0 for j in js):
                dead.discard(g); claimed.discard(g); life[g] = new_life(k + 1, g)
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            g = next((g for g in dead if (c['x'], c['y']) in gtiles[g]), None)
            if g is None: continue
            up, first, fr, hitters, ((du, nu, _), (dt, nt, _)) = life[g]
            w = D.who(c['t'], us)
            dead.discard(g); claimed.add(g)
            if region[g] != REG or not first: continue
            kind = 'open' if up == rows[0]['r'] else 'resp'
            nearer = 'us nearer' if du < dt - 1 else 'them nearer' if dt < du - 1 else 'even'
            A[('n', first)] += 1; A[('n', first, kind)] += 1; A[('n', first, nearer)] += 1
            A[('cap', first, w)] += 1
            if first == 'them' and 'us' in hitters: A[('them first, we hit too')] += 1
            V[('du', first)].append(du); V[('dt', first)].append(dt); V[('delay', first)].append(fr - up)
            A[('nu', first)] += nu; A[('nt', first)] += nt
            if first == 'them':
                # What our nearest champion at the start did from up to the first hit.
                k0 = rix.get(up); k1 = rix.get(fr)
                if k0 is None or k1 is None: continue
                ds = [(min(D.dist((cc['x'], cc['y']), q) for q in gtiles[g]), j) for j, cc in enumerate(rows[k0]['c'])
                      if cc['a'] and 'x' in cc and cc['t'] == us]
                if not ds: A[('next', 'all dead')] += 1; continue
                d0, j = min(ds)
                where = 'other'
                for r in rows[k0:k0 + 40]:
                    cc = r['c'][j]
                    if not cc['a'] or 'x' not in cc: where = 'died'; break
                    acts = r['act'][j] if j < len(r['act']) else []
                    if any(x[0] == 'tribute' for x in acts): where = 'tribute'; break
                    if min(D.dist((cc['x'], cc['y']), q) for q in start[us]) <= 2 and min(D.dist((rows[k0]['c'][j]['x'], rows[k0]['c'][j]['y']), q) for q in start[us]) > 2:
                        where = 'home'; break
                    hits = [grp.get(x[-1]) for x in D.camp_hits(r, j)]
                    hits = [h for h in hits if h is not None]
                    if hits:
                        h = hits[0]
                        if h == g: where = 'this group'; break
                        p0 = (rows[k0]['c'][j]['x'], rows[k0]['c'][j]['y'])
                        dh = min(D.dist(p0, q) for q in gtiles[h])
                        where = f'camps {region[h]} ' + ('nearer' if dh < d0 - 1 else 'farther' if dh > d0 + 1 else 'same')
                        break
                    if any(x[0] in ('attack', 'cast') for x in acts): where = 'fight'; break
                A[('next', where)] += 1
                V['d0'].append(d0)
print(f'{ng} games to r{R}: captured {REG} lives' + (f' of {KIND} groups' if KIND else '') + ' with a first hit, per game')
med = lambda v: sorted(v)[len(v) // 2] if v else '-'
for s in ('us', 'them'):
    m = A[('n', s)]
    print(f'  first hit {s:4} {m / ng:4.1f} (opening {A[("n", s, "open")] / ng:.1f}, respawn {A[("n", s, "resp")] / ng:.1f}); at the start our nearest '
          f'median {med(V[("du", s)])}, theirs {med(V[("dt", s)])}; within 10 us {A[("nu", s)] / max(1, m):.2f} them {A[("nt", s)] / max(1, m):.2f}; '
          f'us nearer {A[("n", s, "us nearer")] / ng:.1f}, even {A[("n", s, "even")] / ng:.1f}, them nearer {A[("n", s, "them nearer")] / ng:.1f}; '
          f'captured by us {A[("cap", s, "us")] / ng:.1f} them {A[("cap", s, "them")] / ng:.1f}; delay median {med(V[("delay", s)])}')
print(f'  them first: our nearest champion at the start (median {med(V["d0"])} tiles), what it did next within 40 rounds: '
      + ', '.join(f'{k[1]} {v / ng:.2f}' for k, v in sorted(A.items(), key=lambda kv: -kv[1]) if k[0] == 'next'))
