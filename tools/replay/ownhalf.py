# Our deaths in our own half (death spot within 20 open steps of our spawn) on one map, to round R: one line per death
# (round, spot at first contact, home distance there, static or moving over the 8 rounds before contact, camp hits and
# moves in those rounds, nearest camp tile, allies within 6 and 12 at contact, enemies within 9 five rounds before
# contact, health, bag, contact length, and the D-line activity at death from the replay stdout), then per-game totals.
# First contact = the first round of the final approach with an enemy within 4. Map dump from data/maps_txt (hyphens).
# usage: python -I tools/replay/ownhalf.py FIGHTS_DIR REPLAY_DIR R   (e.g. data/fights/cov1_bwmp_bwmp_00interlock
#        data/replays/platform/cov1_bwmp_bwmp 1000; REPLAY_DIR may lack the replays, the activity is then ?)
import sys, os, gzip, json, glob, collections, zipfile, re
D, RD, R = sys.argv[1], sys.argv[2], int(sys.argv[3])
cheb = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1]))
side = {l.split()[0]: (l.split()[2], l.split()[1]) for l in open(os.path.join(D, 'index.txt'), encoding='utf-8') if len(l.split()) >= 4}
mp = next(iter(side.values()))[1]
L = open(f'data/maps_txt/{mp.replace("_", "-")}.txt', encoding='utf-8').read().splitlines()
Wd, H = int(L[0].split()[2]), int(L[0].split()[3]); g = L[1:1 + H]
def bfs(src):
    q = [(x, y) for y in range(H) for x in range(Wd) if g[y][x] == src]; d = {p: 0 for p in q}
    for p in q:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                t = (p[0] + dx, p[1] + dy)
                if 0 <= t[0] < Wd and 0 <= t[1] < H and t not in d and g[t[1]][t[0]] not in '#o': d[t] = d[p] + 1; q.append(t)
    return d
fd = {0: bfs('S'), 1: bfs('s')}
CAMP = set('wEg$GM')
camps = [(x, y) for y in range(H) for x in range(Wd) if g[y][x] in CAMP]
C = collections.Counter(); n = 0
for f in sorted(glob.glob(os.path.join(D, '*.jsonl.gz'))):
    mid = os.path.basename(f).split('.')[0]
    if mid not in side: continue
    sd, _ = side[mid]; us = 0 if sd == 'a' else 1; n += 1
    dl = {}
    rp = os.path.join(RD, mid + '.repl26a')
    if os.path.exists(rp):
        st = zipfile.ZipFile(rp).read(f'team-{sd}.stdout').decode('utf8', 'replace').replace('\0', '')
        for m in re.finditer(r'^D(\d+) s(\d) r\d+ hp=(\S+) (\S+)(.*)$', st, re.M): dl[int(m.group(1))] = (m.group(4), m.group(5)[:60])
    hist = collections.defaultdict(list)
    for l in gzip.open(f, 'rt'):
        r = json.loads(l)
        if not r.get('c') or r.get('r', 0) > R: continue
        A = r.get('act') or []
        for i, c in enumerate(r['c']):
            t = c.get('t')
            if t != us: continue
            if 'x' in c and c.get('a', 1):
                en = [(o['x'], o['y']) for o in r['c'] if o.get('t') == 1 - t and 'x' in o and o.get('a', 1)]
                al = [(o['x'], o['y']) for j, o in enumerate(r['c']) if j != i and o.get('t') == t and 'x' in o and o.get('a', 1)]
                acts = A[i] if i < len(A) else []
                hits = any(a and a[0] == 'attack' and len(a) > 3 and a[3] == 'm' for a in acts)
                mv = any(a and a[0] == 'move' for a in acts)
                hist[i].append((r['r'], (c['x'], c['y']), en, al, hits, mv, c['hp'], c['mhp'], c.get('g', 0)))
            elif hist[i]:
                h = hist[i]; hist[i] = []
                last = h[-1]
                if fd[t].get(last[1], 999) > 20: continue
                j = len(h) - 1
                while j > 0 and any(cheb(h[j - 1][1], e) <= 4 for e in h[j - 1][2]): j -= 1
                k = h[j]; w = h[max(0, j - 8):j]
                static = j >= 8 and abs(fd[t].get(h[j - 8][1], 999) - fd[t].get(k[1], 999)) < 3
                hits = sum(q[4] for q in w); mvs = sum(q[5] for q in w)
                e5 = sum(1 for e in h[max(0, j - 5)][2] if cheb(h[max(0, j - 5)][1], e) <= 9)
                a6 = sum(1 for a in k[3] if cheb(k[1], a) <= 6); a12 = sum(1 for a in k[3] if cheb(k[1], a) <= 12)
                cd = min(cheb(k[1], c) for c in camps)
                act = dl.get(r['r'] - 1) or dl.get(r['r']) or dl.get(r['r'] - 2) or ('?', '')
                print(f'{mid[:8]} r{last[0]:4} spot {k[1]} home {fd[t].get(k[1])} {"static" if static else "moving"} '
                      f'hits {hits}/8 moves {mvs}/8 camp {cd} allies6 {a6} allies12 {a12} enemies9@-5 {e5} '
                      f'hp {k[6]}/{k[7]} bag {k[8]} contact {last[0] - k[0]}r  D: {act[0]}')
                C['deaths'] += 1; C['static' if static else 'moving'] += 1
                C['alone (no ally within 12)' if a12 == 0 else 'ally within 12, none within 6' if a6 == 0 else 'ally within 6'] += 1
print(f'{n} games, per game: ' + ', '.join(f'{k} {v / n:.2f}' for k, v in C.items()))
