"""Does staying together pay in the opening? python -I tools/replay/packness.py RMAX DIR [DIR ...]

For each game and side: packness = mean, over rounds 10 to RMAX and living champions, of the share of living allies within 4 tiles. Prints each side's mean, then groups the games by size and by how much more packed the
rival is than we are (four bands), with games, wins, gold at r300 and r600 (us/them), and deaths to r300. A second table does the same over all sides: gold at r300 by that side's packness band, whoever played it.
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

R, dirs = int(sys.argv[1]), sys.argv[2:]
rowsout = []
for us, res, mp, meta, rows in D.games(dirs):
    n = len(rows[0]['c'])
    size = n // 2
    S = {0: [0.0, 0], 1: [0.0, 0]}
    G = {}
    dead = {0: 0, 1: 0}
    prev = None
    for x in rows:
        r = x['r']
        if r in (300, 600):
            for t in (0, 1):
                G[(r, t)] = sum(D.gold_held(meta, c) for c in x['c'] if c['t'] == t)
        if r > 600:
            break
        if prev is not None and r <= 300:
            for i in range(n):
                if prev['c'][i]['a'] and not x['c'][i]['a']:
                    dead[x['c'][i]['t']] += 1
        prev = x
        if r < 10 or r > R:
            continue
        for t in (0, 1):
            al = [c for c in x['c'] if c['t'] == t and c['a']]
            if len(al) < 2:
                continue
            for c in al:
                near = sum(1 for o in al if o is not c and max(abs(o['x'] - c['x']), abs(o['y'] - c['y'])) <= 4)
                S[t][0] += near / (len(al) - 1)
                S[t][1] += 1
    if (300, 0) not in G:
        continue
    pu = S[us][0] / max(1, S[us][1])
    pt = S[1 - us][0] / max(1, S[1 - us][1])
    rowsout.append(dict(size=size, win=res == 'win', pu=pu, pt=pt, gu3=G[(300, us)], gt3=G[(300, 1 - us)], gu6=G.get((600, us), 0), gt6=G.get((600, 1 - us), 0), du=dead[us], dt=dead[1 - us], mp=mp))
print(f'{len(rowsout)} games')
for s in (3, 4, 5, 0):
    rr = [x for x in rowsout if s == 0 or x['size'] == s]
    if not rr:
        continue
    k = len(rr)
    print(f"size {s or 'all'}: games {k}, wins {sum(x['win'] for x in rr)}, packness us {sum(x['pu'] for x in rr) / k:.3f} them {sum(x['pt'] for x in rr) / k:.3f}")
    for lo, hi in ((-9, -0.08), (-0.08, 0.0), (0.0, 0.08), (0.08, 0.16), (0.16, 9)):
        b = [x for x in rr if lo <= x['pt'] - x['pu'] < hi]
        if not b:
            continue
        m = len(b)
        print(f"   them minus us {lo:+.2f}..{hi:+.2f}: {m:4d} games, win {sum(x['win'] for x in b) / m:.2f}, gold r300 {sum(x['gu3'] for x in b) / m:5.0f}/{sum(x['gt3'] for x in b) / m:5.0f}, r600 {sum(x['gu6'] for x in b) / m:5.0f}/{sum(x['gt6'] for x in b) / m:5.0f}, deaths r300 {sum(x['du'] for x in b) / m:.1f}/{sum(x['dt'] for x in b) / m:.1f}")
print('all sides by their own packness: gold at r300 and r600 of that side, its rival, deaths to r300')
A = []
for x in rowsout:
    A.append((x['size'], x['pu'], x['gu3'], x['gt3'], x['gu6'], x['gt6'], x['du'], x['dt']))
    A.append((x['size'], x['pt'], x['gt3'], x['gu3'], x['gt6'], x['gu6'], x['dt'], x['du']))
for s in (3, 4, 5):
    rr = sorted((a for a in A if a[0] == s), key=lambda a: a[1])
    if not rr:
        continue
    q = max(1, len(rr) // 4)
    for j in range(4):
        b = rr[j * q:(j + 1) * q if j < 3 else len(rr)]
        m = len(b)
        print(f"  size {s} q{j + 1} packness {sum(a[1] for a in b) / m:.2f}: {m:4d} sides, gold r300 {sum(a[2] for a in b) / m:5.0f}/{sum(a[3] for a in b) / m:5.0f}, r600 {sum(a[4] for a in b) / m:5.0f}/{sum(a[5] for a in b) / m:5.0f}, deaths {sum(a[6] for a in b) / m:.1f}/{sum(a[7] for a in b) / m:.1f}")
