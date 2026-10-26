"""Repeat deaths per side: python -I tools/replay/repeat.py DIR... (repo root). A repeat death is within 6 tiles and 150 rounds of an
earlier death of the same side. Split: same champion (it came back after respawn) or a teammate; rounds since that
champion left its spawn; what it did in its last 10 rounds (hit a camp, hit a champion); bag at death."""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
A = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    spawn = {t: set((c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    left = {}  # champion -> round it was last on its spawn
    deaths = {0: [], 1: []}
    for k in range(1, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            c = a['c'][i]
            if c['a'] and 'x' in c and (c['x'], c['y']) in spawn[c['t']]: left[i] = a['r']
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if not pc['a'] or c['a'] or 'x' not in pc: continue
            t = pc['t']; w = D.who(t, us); p = (pc['x'], pc['y'])
            prev = [(r0, j) for r0, q, j in deaths[t] if b['r'] - r0 <= 150 and D.dist(p, q) <= 6]
            A[(w, 'deaths')] += 1
            since = b['r'] - left.get(i, 0)
            sb = '0-20' if since <= 20 else '21-50' if since <= 50 else '51+'
            lo = max(0, k - 10)
            camp = any(D.camp_hits(rows[kk], i) for kk in range(lo, k))
            champ = any(D.enemy_hits(rows[kk], i, n) for kk in range(lo, k))
            if prev:
                A[(w, 'repeat')] += 1
                A[(w, 'repeat self' if any(j == i for _, j in prev) else 'repeat mate')] += 1
                gap = b['r'] - max(r0 for r0, _ in prev)
                A[(w, 'repeat gap ' + ('0-10' if gap <= 10 else '11-30' if gap <= 30 else '31-60' if gap <= 60 else '61-150'))] += 1
                e6 = sum(1 for o in a['c'] if o['a'] and 'x' in o and o['t'] != t and D.dist((o['x'], o['y']), p) <= 6)
                a6 = sum(1 for j, o in enumerate(a['c']) if j != i and o['a'] and 'x' in o and o['t'] == t and D.dist((o['x'], o['y']), p) <= 6)
                if gap > 10: A[(w, 'repeat gap>10 e6-a6 ' + ('<=0' if e6 - a6 <= 0 else '1' if e6 - a6 == 1 else '2+'))] += 1
                A[(w, 'repeat since ' + sb)] += 1
                A[(w, 'repeat ' + ('hit champ' if champ else 'hit camp only' if camp else 'no hit'))] += 1
            else:
                A[(w, 'first since ' + sb)] += 1
            deaths[t].append((b['r'], p, i))
print(f'{ng} games to r1000, per game us / them')
keys = sorted({k[1] for k in A})
for key in keys:
    print(f'  {key:24} {A[("us", key)] / ng:5.2f} / {A[("them", key)] / ng:5.2f}')
