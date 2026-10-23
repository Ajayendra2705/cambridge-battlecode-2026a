"""Fit the death-hazard model: P(champion dies within the next H rounds | features) as a logistic regression.

usage: python -I tools/replay/hazard.py DIR [DIR...] [--horizon 20]
Reads our team's stdout from every replay in the directories (F feature lines every 10 rounds, D death lines),
fits on a random 70% of the maps and reports AUC / log-loss on the held-out maps, then refits on everything
and prints C++ coefficients (applied to the raw features, standardisation folded in).
F line: F round slot gems hp% n_enemies nearest_enemy since_seen altar_d home_d enemy_field n_allies enemy_burst max_hp
"""
import glob, os, re, sys, zipfile
import numpy as np

args = [a for a in sys.argv[1:] if not a.startswith('--')]
H = int(sys.argv[sys.argv.index('--horizon') + 1]) if '--horizon' in sys.argv else 20
NAMES = ['hp', 'n_enemies', 'near_inv', 'seen_recent', 'altar_d', 'home_d', 'enemy_side', 'n_allies',
         'burst_ratio', 'round']


def features(f):
    rnd, slot, gems, hp, ne, nd, since, altar, home, ef, na, burst, mhp = f
    near = min(nd, 12)
    return [hp / 100, min(ne, 5), 1.0 / max(near, 1), float(since <= 20),
            min(altar, 60) / 30, min(home, 80) / 40, (home - ef) / 40 if ef < 900 and home < 900 else 0.0,
            min(na, 5), min(burst / max(mhp, 1), 3.0), rnd / 2000]


rows = []  # (map, features, label)
for d in args:
    for path in glob.glob(os.path.join(d, '*.repl26a')):
        base = os.path.basename(path)
        m = re.match(r'(.+?)~(.+?)~(.+?)~([AB])\.repl26a', base)
        if m:
            mp, side = m[3], m[4].lower()
        else:  # platform replay: our stdout is the only one
            mp, side = base[:8], None
        try:
            z = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            continue
        name = f'team-{side}.stdout' if side else [n for n in z.namelist() if n.endswith('.stdout')][0]
        text = z.read(name).decode('latin1')
        deaths = {}
        for dm in re.finditer(r'^D(\d+) s(\d)', text, re.M):
            deaths.setdefault(int(dm[2]), []).append(int(dm[1]))
        for fm in re.finditer(r'^F ((?:-?\d+ ){12}-?\d+)', text, re.M):
            f = [int(x) for x in fm[1].split()]
            rnd, slot = f[0], f[1]
            label = any(rnd < t <= rnd + H for t in deaths.get(slot, []))
            rows.append((mp, features(f), float(label)))
print('samples', len(rows), 'positives', int(sum(r[2] for r in rows)), 'maps', len({r[0] for r in rows}))
X = np.array([r[1] for r in rows]); y = np.array([r[2] for r in rows]); maps = np.array([r[0] for r in rows])


def fit(X, y, l2=1.0, iters=60):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.hstack([np.ones((len(X), 1)), (X - mu) / sd])
    w = np.zeros(Z.shape[1])
    for _ in range(iters):  # Newton steps
        p = 1 / (1 + np.exp(-Z @ w))
        g = Z.T @ (p - y) + l2 * np.r_[0, w[1:]]
        Hm = (Z * (p * (1 - p))[:, None]).T @ Z + l2 * np.diag(np.r_[0, np.ones(len(w) - 1)])
        w -= np.linalg.solve(Hm, g)
    return w, mu, sd


def predict(model, X):
    w, mu, sd = model
    Z = np.hstack([np.ones((len(X), 1)), (X - mu) / sd])
    return 1 / (1 + np.exp(-Z @ w))


def auc(p, y):
    order = np.argsort(p); r = np.empty(len(p)); r[order] = np.arange(1, len(p) + 1)
    pos = y == 1
    return (r[pos].sum() - pos.sum() * (pos.sum() + 1) / 2) / max(pos.sum() * (~pos).sum(), 1)


rng = np.random.default_rng(0)
umaps = sorted(set(maps)); aucs = []
for rep in range(5):
    test = set(rng.choice(umaps, size=max(1, len(umaps) * 3 // 10), replace=False))
    tr = np.array([m not in test for m in maps])
    model = fit(X[tr], y[tr])
    p = predict(model, X[~tr])
    ll = -np.mean(y[~tr] * np.log(p + 1e-9) + (1 - y[~tr]) * np.log(1 - p + 1e-9))
    base = y[tr].mean(); ll0 = -np.mean(y[~tr] * np.log(base) + (1 - y[~tr]) * np.log(1 - base))
    aucs.append(auc(p, y[~tr]))
    print(f'held-out maps {len(test)}: AUC {aucs[-1]:.3f}  logloss {ll:.4f} (base {ll0:.4f})')
w, mu, sd = fit(X, y)
raw = w[1:] / sd
b = w[0] - (raw * mu).sum()
print('mean held-out AUC', round(float(np.mean(aucs)), 3))
for n, c in zip(NAMES, raw): print(f'  {n:12} {c:+.4f}')
print('C++: bias', f'{b:.5f}f', 'coef {' + ', '.join(f'{c:.5f}f' for c in raw) + '}')
