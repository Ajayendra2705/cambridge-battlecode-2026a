# Round-by-round trace of our deaths by round UPTO in one decoded game: the victim (position, hp, home distance,
# actions) and every enemy champion within 8 (type, distance, hp, whom it hit), from 25 rounds before the death.
# usage: python -I tools/replay/trace.py FIGHTDIR MATCH_ID_PREFIX [UPTO] [MAXDEATHS]
import sys, os, gzip, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
d, pre = sys.argv[1], sys.argv[2]
UPTO = int(sys.argv[3]) if len(sys.argv) > 3 else 300
MAXD = int(sys.argv[4]) if len(sys.argv) > 4 else 3
side = {}
for line in open(os.path.join(d, 'index.txt'), encoding='utf-8'):
    p = line.split()
    if len(p) >= 4: side[p[0]] = (0 if p[2] == 'a' else 1, p[1], p[3])
f = next(x for x in glob.glob(os.path.join(d, '*.jsonl.gz')) if os.path.basename(x).startswith(pre))
mid = os.path.basename(f).split('.')[0]
us, mp, res = side[mid]
lines = [json.loads(l) for l in gzip.open(f, 'rt')]
rows = [r for r in lines[1:] if r.get('c')]
n = max(len(r['c']) for r in rows); rows = [r for r in rows if len(r['c']) == n]
start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
home = lambda t, q: min(D.dist(q, s) for s in start[t])
print(f'{mp} {res} us=team{us} drafts {lines[0].get("drafts")}')
shown = 0
for k in range(len(rows) - 1):
    if rows[k + 1]['r'] > UPTO or shown >= MAXD: break
    for i in range(n):
        c = rows[k]['c'][i]
        if c['t'] != us or not (c['a'] and not rows[k + 1]['c'][i]['a']): continue
        shown += 1
        print(f"\n== {D.NAMES[c['ty']]} (#{i}) dies at r{rows[k + 1]['r']}, bag {c.get('g', 0)}")
        for kk in range(max(0, k - 25), k + 1):
            r = rows[kk]; me = r['c'][i]
            if not (me['a'] and 'x' in me): continue
            q = (me['x'], me['y'])
            acts = ' '.join(x[0][0] + ('C' if x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' else 'm' if x[0] in ('attack', 'cast') else '') for x in (r['act'][i] if i < len(r['act']) else []))
            ens = []
            for j in range(n):
                o = r['c'][j]
                if o['t'] == us or not (o['a'] and 'x' in o) or D.dist(q, (o['x'], o['y'])) > 8: continue
                hit = 'X' if any(x[-1] == i for x in D.enemy_hits(r, j, n)) else ''
                ens.append(f"{D.NAMES[o['ty']][:4]}@{D.dist(q, (o['x'], o['y']))}{hit}")
            als = sum(1 for j in range(n) if j != i and r['c'][j]['t'] == us and r['c'][j]['a'] and 'x' in r['c'][j] and D.dist(q, (r['c'][j]['x'], r['c'][j]['y'])) <= 6)
            print(f"  r{r['r']:4} ({q[0]:2},{q[1]:2}) home {home(us, q):2} hp {me.get('hp', 0):5.0f}/{me.get('mhp', 0):4} al6 {als}  [{acts:10}]  " + ' '.join(ens))
