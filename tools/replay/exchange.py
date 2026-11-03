"""Damage exchange in contact by numbers: python -I tools/replay/exchange.py RMIN RMAX DIR...
A round counts when at least one champion of each side stands within 3 of an enemy at the start of the round. Bodies in contact per side give the bucket (us - them). Per bucket: rounds per game, health each side loses per
round (damage from camps too), basic hits and casts on champions per body-round in contact, and deaths per 100 rounds."""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
D.SKIP = []
r0, r1 = int(sys.argv[1]), int(sys.argv[2])
A = collections.defaultdict(collections.Counter)
ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[3:]):
    ng += 1
    n = len(rows[0]['c'])
    for k in range(1, len(rows)):
        r = rows[k]; p = rows[k - 1]
        if r['r'] > r1:
            break
        if r['r'] < r0 or p['r'] != r['r'] - 1:
            continue
        live = [(i, c) for i, c in enumerate(p['c']) if c['a'] and 'x' in c]
        cont = {'us': [], 'them': []}
        for i, c in live:
            w = D.who(c['t'], us)
            if any(e['t'] != c['t'] and D.dist((c['x'], c['y']), (e['x'], e['y'])) <= 3 for _, e in live):
                cont[w].append(i)
        if not cont['us'] or not cont['them']:
            continue
        d = len(cont['us']) - len(cont['them'])
        b = 'us+2' if d >= 2 else 'them+2' if d <= -2 else f'{d:+d}'
        s = A[b]
        s['rounds'] += 1
        for w in ('us', 'them'):
            s['bodies_' + w] += len(cont[w])
            for i in cont[w]:
                c0, c1 = p['c'][i], r['c'][i]
                if c1['a']:
                    s['loss_' + w] += max(0, c0.get('hp', 0) - c1.get('hp', 0))
                else:
                    s['loss_' + w] += c0.get('hp', 0)
                    s['dead_' + w] += 1
                acts = D.enemy_hits(r, i, n)
                s['atk_' + w] += sum(1 for x in acts if x[0] == 'attack')
                s['cast_' + w] += sum(1 for x in acts if x[0] == 'cast')
print(ng, 'games; bucket bodies us-them | rounds a game | bodies us/them | health lost a round us/them | basic hits per body-round us/them | casts on champions per body-round us/them | deaths per 100 rounds us/them')
for b in ('them+2', '-1', '+0', '+1', 'us+2'):
    s = A[b]; m = max(1, s['rounds'])
    print(f"{b:7} {s['rounds']/ng:6.1f} | {s['bodies_us']/m:.1f}/{s['bodies_them']/m:.1f} | {s['loss_us']/m:5.0f}/{s['loss_them']/m:5.0f} | {s['atk_us']/max(1,s['bodies_us']):.2f}/{s['atk_them']/max(1,s['bodies_them']):.2f} | {s['cast_us']/max(1,s['bodies_us']):.3f}/{s['cast_them']/max(1,s['bodies_them']):.3f} | {100*s['dead_us']/m:.1f}/{100*s['dead_them']/m:.1f}")
