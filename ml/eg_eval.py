import numpy as np
import torch

from common import OUT
from eg_train import EnemyGainMLP, predict, to_gems

SEGMENTS = [(0, 0), (1, 10), (11, 50), (51, 1e9)]
NEAR = 4
BOOT = 1000


def model_preds(name, d, m):
    ck = torch.load(OUT / f"eg_{name}.pt", weights_only=False)
    s = ck["stats"]
    model = EnemyGainMLP(d["x"].shape[1])
    model.load_state_dict(ck["state"])
    x = torch.as_tensor((d["x"][m] - s["mean"]) / s["std"])
    return to_gems(predict(model, x, torch.as_tensor(d["e_type"][m])).numpy(), s)[:, 0]


def deviance(y, p):
    p = np.maximum(p, 1e-6)
    return 2 * np.mean(np.where(y > 0, y * np.log(np.maximum(y, 1e-12) / p), 0) - (y - p))


def main():
    d = dict(np.load(OUT / "eg_dataset.npz"))
    f = list(d["features"])
    col = lambda n: d["x"][:, f.index(n)]
    tr = d["split"] == "train"
    y_all = d["label"][:, 0]
    cap = col("capturing") > 0
    type_mean = {t: y_all[tr & (d["e_type"] == t)].mean() for t in np.unique(d["e_type"][tr])}
    table = {(t, c): y_all[tr & (d["e_type"] == t) & (cap == c)].mean() for t in type_mean for c in (False, True)
             if (tr & (d["e_type"] == t) & (cap == c)).any()}
    for subset, m in [("decision rows (one of ours within 4)", (d["split"] == "val") & (col("dist_our_nearest") <= NEAR)),
                      ("all val rows", d["split"] == "val")]:
        y, games = y_all[m], d["game"][m]
        ty, c = d["e_type"][m], cap[m]
        preds = {
            "constant": np.full(len(y), y_all[tr].mean()),
            "rule: capturing ? group gems : type mean": np.where(c, col("g0_gems")[m], [type_mean[t] for t in ty]),
            "rule: mean by (type, capturing)": np.array([table.get((t, cc), type_mean[t]) for t, cc in zip(ty, c)]),
            **{f"model {n}": model_preds(n, d, m) for n in ["raw", "log1p", "poisson"]},
        }
        print(f"\n== {subset}: {m.sum()} rows, {len(np.unique(games))} games, mean label {y.mean():.2f}")
        print(f"{'predictor':42}{'MSE':>9}{'deviance':>10}{'mean pred':>10}" + "".join(f"{f'seg {a}-{int(b) if b < 1e9 else 'up'}':>16}" for a, b in SEGMENTS))
        for name, p in preds.items():
            seg = []
            for a, b in SEGMENTS:
                s = (y >= a) & (y <= b)
                seg.append(f"{p[s].mean():7.1f}/{y[s].mean():6.1f}")
            print(f"{name:42}{np.mean((p - y) ** 2):9.1f}{deviance(y, p):10.3f}{p.mean():10.2f}" + "".join(f"{x:>16}" for x in seg))
        ug = np.unique(games)
        gi = {g: np.where(games == g)[0] for g in ug}
        rng = np.random.default_rng(0)
        base = preds["rule: mean by (type, capturing)"]
        print(f"bootstrap over games ({BOOT}x), deviance difference vs 'mean by (type, capturing)' (negative = model better), 95% interval:")
        for n in ["raw", "log1p", "poisson"]:
            p, diffs = preds[f"model {n}"], []
            for _ in range(BOOT):
                idx = np.concatenate([gi[g] for g in rng.choice(ug, len(ug))])
                diffs.append(deviance(y[idx], p[idx]) - deviance(y[idx], base[idx]))
            lo, hi = np.percentile(diffs, [2.5, 97.5])
            print(f"  model {n:8} {np.mean(diffs):+.3f}  [{lo:+.3f}, {hi:+.3f}]")


if __name__ == "__main__":
    main()
