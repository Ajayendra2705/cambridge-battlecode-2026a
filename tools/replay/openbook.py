"""Opening book by map, from decoded games: python -I tools/replay/openbook.py OUT.json R DIR [DIR ...] [--them-only DIR ...]

For every map: camp tiles and groups (from the hits of all games), the map's symmetry (the transform that carries team 0's start to team 1's and the camp
tiles onto themselves). Every game is read in team 0's frame. f_them[g] is the share of the rivals' games in which their team hit group g by round R, f_us[g]
the same for us. DIRs after --them-only count only for f_them (for example runs of another bot of ours against the same rivals, whose own games must not count
as ours). OUT holds per map: symmetry, representative tile, kind, f_them, f_us and games.
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
D.SKIP = []
out, R = sys.argv[1], int(sys.argv[2])
args = sys.argv[3:]
dirs, them_only = [], []
cur = dirs
for a in args:
    if a == '--them-only':
        cur = them_only
    else:
        cur.append(a)
SIG = json.load(open('data/map_sigs.json', encoding='utf-8'))
NAME = {0: 'wolf', 1: 'elk', 2: 'gemc', 3: 'goldc', 4: 'mono', 5: 'golem'}
POS = collections.defaultdict(dict)
KIND = {}
EV = collections.defaultdict(list)  # map -> (rival team, set of our group hits by team): stored as camp index hits by team
START = {}
def read(ds, us_ok):
    for us, res, mp, meta, rows in D.games(ds):
        n = len(rows[0]['c'])
        KIND[mp] = {int(k): v for k, v in meta['camps'].items()}
        for t in (0, 1):
            s = [(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c]
            if s:
                START.setdefault(mp, {})[t] = s[0]
        hits = {0: collections.Counter(), 1: collections.Counter()}
        for r in rows:
            for i in range(min(n, len(r.get('act', [])))):
                for x in D.camp_hits(r, i):
                    POS[mp][x[-1]] = (x[-4], x[-3])
                    if r['r'] <= R:
                        hits[r['c'][i]['t']][x[-1]] += 1
        EV[mp].append((us, res, hits, us_ok))
read(dirs, True)
if them_only:
    read(them_only, False)
def transforms(w, h):
    yield 'r', lambda x, y: (w - 1 - x, h - 1 - y)
    yield 'x', lambda x, y: (w - 1 - x, y)
    yield 'y', lambda x, y: (x, h - 1 - y)
    if w == h:
        yield 'd', lambda x, y: (y, x)
        yield 'a', lambda x, y: (w - 1 - y, h - 1 - x)
BOOK = {}
for mp, pos in POS.items():
    sig = SIG.get(mp)
    if not sig or mp not in START or len(START[mp]) < 2:
        continue
    w, h = sig[0], sig[1]
    tiles = set(pos.values())
    best = None
    for nm, T in transforms(w, h):
        s0, s1 = START[mp][0], START[mp][1]
        d = D.dist(T(*s0), s1)
        hit = sum(1 for p in tiles if T(*p) in tiles) / max(1, len(tiles))
        sc = hit - 0.02 * d
        if best is None or sc > best[0]:
            best = (sc, nm, T, hit, d)
    sc, nm, T, hit, d = best
    t2c = {p: j for j, p in pos.items()}
    grp = {}
    for j in pos:
        if j in grp:
            continue
        g = min(pos) if False else j
        st = [j]
        comp = []
        while st:
            k = st.pop()
            if k in grp:
                continue
            grp[k] = g
            comp.append(k)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                m = t2c.get((pos[k][0] + dx, pos[k][1] + dy))
                if m is not None and m not in grp:
                    st.append(m)
    mem = collections.defaultdict(list)
    for j, g in grp.items():
        mem[g].append(j)
    # A group of team 1's frame, carried into team 0's frame.
    def to0(j):
        p = T(*pos[j])
        c = t2c.get(p)
        return grp.get(c) if c is not None else None
    F = {'them': collections.Counter(), 'us': collections.Counter()}
    N = collections.Counter()
    for us, res, hits, us_ok in EV[mp]:
        for t in (0, 1):
            w_ = 'us' if t == us else 'them'
            if w_ == 'us' and not us_ok:
                continue
            N[w_] += 1
            seen = set()
            for j, c in hits[t].items():
                if j not in grp:
                    continue
                g = grp[j] if t == 0 else to0(j)
                if g is not None:
                    seen.add(g)
            for g in seen:
                F[w_][g] += 1
    rows_ = []
    for g, js in mem.items():
        ks = [KIND[mp].get(j) for j in js]
        kind = next((NAME[k] for k in (4, 5, 1, 0) if k in ks), 'gemc' if 2 in ks else 'goldc')
        rows_.append({'tile': pos[js[0]], 'tile1': T(*pos[js[0]]), 'kind': kind, 'n': len(js), 'them': F['them'][g] / max(1, N['them']), 'us': F['us'][g] / max(1, N['us'])})
    BOOK[mp] = {'sym': nm, 'symhit': round(hit, 2), 'startd': d, 'start0': START[mp][0], 'nthem': N['them'], 'nus': N['us'], 'groups': rows_}
json.dump(BOOK, open(out, 'w'))
print('maps', len(BOOK))
for mp in sorted(BOOK):
    b = BOOK[mp]
    top = sorted(b['groups'], key=lambda g: -abs(g['them'] - g['us']))[:4]
    print(f"{mp:24} sym {b['sym']} {b['symhit']:.2f} d{b['startd']} n {b['nthem']}/{b['nus']} | " + ' '.join(f"{g['kind']}{g['n']}@{g['tile'][0]},{g['tile'][1]} {g['them']:.2f}/{g['us']:.2f}" for g in top))
