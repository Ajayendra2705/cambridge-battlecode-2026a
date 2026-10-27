# 00ribs champion-round budget per side, r60-1000, champions on average: dead, on the hill (y >= 58), walking down,
# walking up, at home (within 6 of spawn), other; heal trips (leaving the hill alive and reaching home alive) per game
# and health when leaving the hill. Reads every game of the dirs: pass a dir holding 00ribs games only.
# usage: python -I tools/replay/ribsbudget.py DIR...
import gzip, json, os, sys, collections
C = collections.Counter(); trips = collections.defaultdict(list); G = 0
for d in sys.argv[1:]:
    for l in open(os.path.join(d, 'index.txt')):
        if not l.strip(): continue
        mid, mp, side, res = l.split()[:4]
        f = os.path.join(d, mid + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if side == 'a' else 1
        rows = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()]
        rows = [r for r in rows[1:] if r.get('c') and r['r'] <= 1000]
        G += 1
        n = len(rows[0]['c']); spawn = [(c['x'], c['y']) for c in rows[0]['c']]
        hist = collections.defaultdict(list)
        left = {}  # i -> (round, hp frac) when last seen leaving the hill
        for r in rows:
            for i, c in enumerate(r['c']):
                who = 'us' if c['t'] == us else 'them'
                alive = c.get('x') is not None and c.get('hp', 0) > 0
                if not alive:
                    left.pop(i, None)
                    if r['r'] >= 60: C[(who, 'dead')] += 1
                    hist[i] = []; continue
                y = c['y']; h = hist[i]; h.append(y)
                if len(h) > 6: h.pop(0)
                dh = max(abs(c['x'] - spawn[i][0]), abs(c['y'] - spawn[i][1]))
                if y >= 58:
                    st = 'hill'; left[i] = (r['r'], c['hp'] / c['mhp'])
                elif dh <= 6: st = 'home'
                elif len(h) >= 4 and h[-1] - h[0] >= 2: st = 'down'
                elif len(h) >= 4 and h[0] - h[-1] >= 2: st = 'up'
                else: st = 'other'
                if st == 'home' and i in left:
                    r0, fr = left.pop(i); trips[who].append(fr)
                if r['r'] >= 60: C[(who, st)] += 1
print('games', G)
for who in ('us', 'them'):
    tot = sum(v for k, v in C.items() if k[0] == who)
    print(who, ' '.join(f'{s} {C[(who, s)] / G / 940:.2f}' for s in ('dead', 'hill', 'down', 'up', 'home', 'other')), '(champions on average)')
    t = trips[who]
    print('   heal trips per game', round(len(t) / G, 2), 'hp frac leaving hill', round(sum(t) / max(1, len(t)), 2))
