# usage: python -I tools/replay/carriercontact.py FIGHTS_DIR [FIGHTS_DIR ...]   (one map per folder; map dump in data/maps_txt)
# Contacts of carriers near the altar, to r1000, both teams: a champion with 30+ gems within 10 of an altar gets an enemy
# within 4 (first round of contact after 5 quiet rounds). Outcome over the next 25 rounds: tributed (its bag fell below
# 30% of the contact bag while it lived), died (bag lost), or neither (kept it).
# Split by distance to the altar at contact, and by allies within 6.
import sys, os, gzip, json, glob, collections
cheb = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1]))
for D in sys.argv[1:]:
    side = {l.split()[0]: (0 if l.split()[2] == 'a' else 1, l.split()[1]) for l in open(os.path.join(D, 'index.txt'), encoding='utf-8') if len(l.split()) >= 4}
    mp = next(iter(side.values()))[1]
    L = open(f'data/maps_txt/{mp.replace("_", "-")}.txt', encoding='utf-8').read().splitlines()
    Wd, H = int(L[0].split()[2]), int(L[0].split()[3]); g = L[1:1 + H]
    altars = [(x, y) for y in range(H) for x in range(Wd) if g[y][x] == 'A']
    C = collections.Counter(); n = 0
    for f in glob.glob(os.path.join(D, '*.jsonl.gz')):
        mid = os.path.basename(f).split('.')[0]
        if mid not in side: continue
        us, _ = side[mid]; n += 1
        rows = [json.loads(l) for l in gzip.open(f, 'rt')]
        rows = [r for r in rows if r.get('c') and r.get('r', 0) <= 1025]
        quiet = collections.defaultdict(int)
        for k, r in enumerate(rows):
            if r['r'] > 1000: break
            for i, c in enumerate(r['c']):
                if 'x' not in c or not c.get('a', 1): quiet[i] = 0; continue
                t = c['t']; p = (c['x'], c['y'])
                en = [(o['x'], o['y']) for o in r['c'] if o.get('t') == 1 - t and 'x' in o and o.get('a', 1)]
                close = any(cheb(p, e) <= 4 for e in en)
                if not close: quiet[i] += 1; continue
                if quiet[i] < 5: quiet[i] = 0; continue
                quiet[i] = 0
                bag = c.get('g', 0)
                ad = min(cheb(p, a) for a in altars)
                if bag < 30 or ad > 10: continue
                al = sum(1 for j, o in enumerate(r['c']) if j != i and o.get('t') == t and 'x' in o and o.get('a', 1) and cheb(p, (o['x'], o['y'])) <= 6)
                who = 'us' if t == us else 'them'
                out = 'kept'
                for r2 in rows[k + 1:k + 26]:
                    c2 = r2['c'][i]
                    if 'x' not in c2 or not c2.get('a', 1): out = 'died'; break
                    if c2.get('g', 0) < bag * 0.3: out = 'tributed'; break
                band = 'altar 0-3' if ad <= 3 else 'altar 4-10'
                C[(who, band, out)] += 1; C[(who, 'all', out)] += 1
                C[(who, 'ally within 6' if al else 'alone', out)] += 1
    print(f'{D}: {n} games; contacts per game: tributed / died / kept')
    for who in ('us', 'them'):
        for band in ('all', 'altar 0-3', 'altar 4-10', 'alone', 'ally within 6'):
            a, b, c = (C[(who, band, o)] / n for o in ('tributed', 'died', 'kept'))
            print(f'  {who:4} {band:14} {a:5.2f} / {b:5.2f} / {c:5.2f}')
