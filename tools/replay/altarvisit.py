# usage: python -I tools/replay/altarvisit.py FIGHTS_DIR [FIGHTS_DIR ...]   (one map per folder; map dump in data/maps_txt)
# Carrier visits to the altar (within 1 of it, the tribute range), to r1000, per team: a visit starts when a champion
# with 30+ gems steps within 1 of an altar and ends when it leaves, dies or its bag drops (tributed). Per visit: rounds
# from arrival to its first 'tribute' action, enemies within 6 at arrival, outcome. Split by enemies within 6 at arrival.
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
        vis = {}
        for l in gzip.open(f, 'rt'):
            r = json.loads(l)
            if not r.get('c') or r.get('r', 0) > 1000: continue
            A = r.get('act') or []
            for i, c in enumerate(r['c']):
                who = 'us' if c.get('t') == us else 'them'
                alive = 'x' in c and c.get('a', 1)
                v = vis.get(i)
                if v is not None:
                    end = None
                    if not alive: end = 'died'
                    elif c.get('g', 0) < v['bag'] * 0.3: end = 'tributed'
                    elif min(cheb((c['x'], c['y']), a) for a in altars) > 1: end = 'left'
                    if end:
                        k = 'none near' if v['en'] == 0 else '1 near' if v['en'] == 1 else '2+ near'
                        for kk in ('all', k):
                            C[(v['who'], kk, end)] += 1; C[(v['who'], kk, 'n')] += 1
                            C[(v['who'], kk, 'wait')] += v['first'] if v['first'] is not None else v['len']
                            C[(v['who'], kk, 'started')] += v['first'] is not None
                        vis.pop(i); v = None
                    else:
                        if v['first'] is None and any(a and a[0] == 'tribute' for a in (A[i] if i < len(A) else [])): v['first'] = v['len']
                        v['len'] += 1
                if v is None and alive and c.get('g', 0) >= 30 and min(cheb((c['x'], c['y']), a) for a in altars) <= 1:
                    en = sum(1 for o in r['c'] if o.get('t') != c['t'] and 'x' in o and o.get('a', 1) and cheb((c['x'], c['y']), (o['x'], o['y'])) <= 6)
                    first = 0 if any(a and a[0] == 'tribute' for a in (A[i] if i < len(A) else [])) else None
                    vis[i] = {'who': who, 'bag': c.get('g', 0), 'en': en, 'first': first, 'len': 1}
    print(f'{D}: {n} games; altar visits with 30+ gems per game: n, tributed / died / left, share started a channel, rounds to the first tribute action')
    for who in ('us', 'them'):
        for kk in ('all', 'none near', '1 near', '2+ near'):
            g2 = lambda s: C[(who, kk, s)]
            nn = max(1, g2('n'))
            print(f'  {who:4} {kk:10} {g2("n") / n:5.2f}: {g2("tributed") / n:4.2f} / {g2("died") / n:4.2f} / {g2("left") / n:4.2f}  started {g2("started") / nn:4.0%}  wait {g2("wait") / nn:4.1f}')
