"""Per map, the first 150 rounds, us against the rivals: python -I openmap.py OUT.json DIR...
Team gold at r50, r100, r150; first and third reward rounds; hits on camps by kind to r100; bodies within 6 of the first camp-hitter; deaths to r100."""
import collections, json, os, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
D.SKIP = []
out, dirs = sys.argv[1], sys.argv[2:]
A = collections.defaultdict(collections.Counter)
for us, res, mp, meta, rows in D.games(dirs):
    a = A[mp]
    a['n'] += 1
    a['w'] += res == 'win'
    camps = {int(k): v for k, v in meta['camps'].items()}
    ev = {'us': [], 'them': []}
    prev = {}
    for k, r in enumerate(rows):
        R = r['r']
        if R > 150:
            break
        for i, c in enumerate(r['c']):
            w = D.who(c['t'], us)
            tot = c.get('g', 0) + D.gold_held(meta, c)
            if tot > prev.get(i, 0) and c.get('k', 0) == prev.get((i, 'k'), 0) and R > 1:
                ev[w].append(R)
            prev[i] = tot
            prev[i, 'k'] = c.get('k', 0)
            if R <= 100:
                for x in D.camp_hits(r, i):
                    kind = camps.get(x[-1], -1)
                    a[f'hit{kind}_{w}'] += 1
                if k + 1 < len(rows) and c['a'] and not rows[k + 1]['c'][i]['a']:
                    a[f'd100_{w}'] += 1
        if R in (50, 100, 150):
            for c in r['c']:
                a[f'gold{R}_' + D.who(c['t'], us)] += D.gold_held(meta, c)
    for w in ev:
        e = sorted(ev[w])
        a[f'first_{w}'] += e[0] if e else 151
        a[f'third_{w}'] += e[2] if len(e) > 2 else 151
json.dump(A, open(out, 'w'))
print('map                      n win | gold r50 | r100 | r150 | first | third | hits to r100: wolf elk gemc goldc golem | deaths r100')
rows = sorted(A.items(), key=lambda kv: kv[1]['gold150_us'] / max(1, kv[1]['gold150_them']))
for mp, a in rows:
    n = a['n']
    f = lambda k: a[k] / n
    print(f"{mp:24} {n:3} {a['w']:3} | {f('gold50_us'):4.0f}/{f('gold50_them'):4.0f} | {f('gold100_us'):4.0f}/{f('gold100_them'):4.0f} | {f('gold150_us'):4.0f}/{f('gold150_them'):4.0f} | {f('first_us'):3.0f}/{f('first_them'):3.0f} | {f('third_us'):3.0f}/{f('third_them'):3.0f} | "
          + ' '.join(f"{f('hit%d_us' % k):3.0f}/{f('hit%d_them' % k):3.0f}" for k in (0, 1, 2, 3, 5)) + f" | {f('d100_us'):3.1f}/{f('d100_them'):3.1f}")
