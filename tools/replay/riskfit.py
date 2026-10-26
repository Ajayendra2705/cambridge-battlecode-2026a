"""Fit P(death within 10 rounds) for a champion in contact (enemy champion within 6) on what the bot sees each turn:
s = log2 of the hp share (own hp plus allies within 5, over enemies within 6), own hp fraction f, enemies within 4 (n4),
and whether it hit an enemy champion this round (e). Per side, logistic; then a grid of predictions.
python tools/replay/riskfit.py DIR... (from the repo root; needs numpy, so not with -I). The fit gave the risk model of
rk1's fight step (`bot.cpp`, `docs/experiments.md`): refit after a patch or a large change of fighting."""
import collections, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D

H = 10
X = collections.defaultdict(list); Y = collections.defaultdict(list); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    end = next((k for k, r in enumerate(rows) if r['r'] > 1000), len(rows))
    for k in range(min(end, len(rows) - H)):
        cs = rows[k]['c']
        for i in range(n):
            c = cs[i]
            if not c['a'] or 'x' not in c: continue
            p = (c['x'], c['y'])
            ed = [(D.dist(p, (o['x'], o['y'])), o) for o in cs if o['a'] and 'x' in o and o['t'] != c['t']]
            e6 = [o for d, o in ed if d <= 6]
            if not e6: continue
            a5 = [o for j, o in enumerate(cs) if j != i and o['a'] and 'x' in o and o['t'] == c['t'] and D.dist(p, (o['x'], o['y'])) <= 5]
            share = (c['hp'] + sum(o['hp'] for o in a5)) / max(1, sum(o['hp'] for o in e6))
            died = any(not rows[jj]['c'][i]['a'] for jj in range(k + 1, k + H + 1))
            s = D.who(c['t'], us)
            X[s].append((np.clip(np.log2(max(share, 1e-3)), -3, 3), c['hp'] / max(1, c['mhp']), sum(1 for d, o in ed if d <= 4),
                         1 if D.enemy_hits(rows[k], i, n) else 0, c.get('g', 0)))
            Y[s].append(died)


def fit(Z, y):
    Z = np.column_stack([np.ones(len(Z)), Z]); w = np.zeros(Z.shape[1])
    for _ in range(30):
        pr = 1 / (1 + np.exp(-np.clip(Z @ w, -30, 30)))
        Hm = (Z * (pr * (1 - pr))[:, None]).T @ Z + 1e-6 * np.eye(len(w))
        w += np.linalg.solve(Hm, Z.T @ (y - pr))
    return w


print(ng, 'games; P(death within', H, 'rounds) in contact = sigmoid(b0 + b1*log2(share) + b2*hpfrac + b3*enemies4 + b4*engaged)')
for side in ('us', 'them'):
    x = np.array(X[side], float); y = np.array(Y[side], float)
    w = fit(x[:, :4], y)
    print(f'  {side:4} ({len(x) / ng:.0f} rounds/game, base {y.mean():.3f}): b0 {w[0]:+.3f} share {w[1]:+.3f} hpfrac {w[2]:+.3f} enemies4 {w[3]:+.3f} engaged {w[4]:+.3f}')
    m = x[:, 4] >= 30
    w2 = fit(x[m][:, :4], y[m])
    print(f'       carriers 30+ ({m.sum() / ng:.0f} rounds/game, base {y[m].mean():.3f}): b0 {w2[0]:+.3f} share {w2[1]:+.3f} hpfrac {w2[2]:+.3f} enemies4 {w2[3]:+.3f} engaged {w2[4]:+.3f}')
    # Calibration: predicted vs observed by decile.
    Z = np.column_stack([np.ones(len(x)), x[:, :4]]); pr = 1 / (1 + np.exp(-Z @ w))
    qs = np.quantile(pr, np.linspace(0, 1, 6))
    print('       calibration (pred/obs by quintile): ' + '  '.join(f'{pr[(pr >= a) & (pr <= b)].mean():.3f}/{y[(pr >= a) & (pr <= b)].mean():.3f}' for a, b in zip(qs[:-1], qs[1:])))
    for f in (1.0, 0.7, 0.4):
        print(f'       hp {f:.1f}, 1 enemy within 4, not hitting: ' + '  '.join(
            f'share {sh:g} {1 / (1 + np.exp(-(w[0] + w[1] * np.log2(sh) + w[2] * f + w[3]))):.3f}' for sh in (0.33, 0.5, 0.7, 1, 1.4, 2, 3)))
