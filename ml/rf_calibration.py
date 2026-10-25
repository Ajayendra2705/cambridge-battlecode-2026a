import sys
from multiprocessing import Pool

import numpy as np
import torch
from sklearn.metrics import roc_auc_score

import reinforce_data as rd
from common import OUT, ROOT, load_game
from reinforce_train import ReinforceNet, poisson_dev

BINS = [0, 0.2, 0.4, 0.69, 1.0, 1.5, np.inf]


def local_rows(path):
    _, rounds = load_game(path)
    rd.load_game = lambda _: (None, rounds)
    return rd.game_arrays((path.name, path.name.split("~")[2]))[1]


def to_arrays(rows):
    a = dict(
        self_x=np.array([r["self_x"] for r in rows], np.float32), self_t=np.array([r["self_t"] for r in rows], np.int64),
        game_x=np.array([r["game_x"] for r in rows], np.float32),
        label=np.array([r["label"] for r in rows], np.float32), ally_label=np.array([r["ally_label"] for r in rows], np.float32),
    )
    for name, width, n_feat in [("ally", rd.MAX_ALLIES, 11), ("enemy", rd.MAX_ENEMIES, 11), ("mem", rd.MAX_MEMORY, len(rd.MEMORY_FEATURES))]:
        a[f"{name}_x"], a[f"{name}_m"] = rd.pad(rows, f"{name}_x", width, n_feat)
        a[f"{name}_t"], _ = rd.pad(rows, f"{name}_t", width, 0, np.int64)
    return a


@torch.no_grad()
def predict(ckpt, a):
    st = ckpt["stats"]
    small = ckpt.get("small", False)
    model = ReinforceNet(a["self_x"].shape[1], a["mem_x"].shape[2], a["game_x"].shape[1], hidden=8 if small else 16, shared=small)
    model.load_state_dict(ckpt["state"])
    model.eval()
    b = dict(a)
    for k, s in [("self_x", "unit"), ("ally_x", "unit"), ("enemy_x", "unit"), ("mem_x", "mem"), ("game_x", "game")]:
        b[k] = ((a[k] - st[s][0]) / st[s][1]).astype(np.float32)
    for k in ["ally", "enemy", "mem"]:
        b[f"{k}_x"] = b[f"{k}_x"] * a[f"{k}_m"][..., None]
    out = []
    for i in range(0, len(a["label"]), 65536):
        e, al = model({k: torch.as_tensor(v[i:i + 65536]) for k, v in b.items() if k not in ("label", "ally_label")})
        out.append(torch.stack([e, al], 1).exp().numpy())
    return np.concatenate(out)


def report(name, y, mu):
    print(f"  {name:8s} mean predicted {mu.mean():.3f}  actual {y.mean():.3f}  deviance {poisson_dev(y, mu):.3f}  AUC(any) {roc_auc_score(y > 0, mu):.3f}")
    idx = np.digitize(mu, BINS) - 1
    cells = [f"{BINS[b]:g}-{BINS[b + 1]:g}: {mu[idx == b].mean():.2f}/{y[idx == b].mean():.2f} (n={int((idx == b).sum())})" for b in range(len(BINS) - 1) if (idx == b).any()]
    print("           pred/actual by bin: " + "; ".join(cells))


def main():
    ckpt_name = sys.argv[1] if len(sys.argv) > 1 else "rf_model_s0"
    ckpt = torch.load(OUT / f"{ckpt_name}.pt", weights_only=False)
    files = sorted((ROOT / "data/fights/local_calib").glob("*.jsonl.gz"))
    with Pool(6) as pool:
        rows = [r for rs in pool.map(local_rows, files) for r in rs]
    local = to_arrays(rows)
    plat = dict(np.load(OUT / "rf_dataset.npz"))
    val = plat["split"] == "val"
    plat = {k: v[val] for k, v in plat.items() if k in local}
    for name, a in [("platform val", plat), ("local games", local)]:
        mu = predict(ckpt, a)
        print(f"{name}: {len(a['label'])} samples")
        report("enemies", a["label"], mu[:, 0])
        report("allies", a["ally_label"], mu[:, 1])
        print(f"  share of decisions where the ln 2 rule fires: enemies {(mu[:, 0] > np.log(2)).mean():.1%}, allies {(mu[:, 1] > np.log(2)).mean():.1%}")


if __name__ == "__main__":
    main()
