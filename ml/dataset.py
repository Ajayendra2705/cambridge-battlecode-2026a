import numpy as np
import torch

from common import OUT

TENSORS = ["self_x", "self_t", "game_x", "ally_x", "ally_t", "ally_m", "enemy_x", "enemy_t", "enemy_m", "reach_m", "engaged_m", "label"]


def norm_stats(d, train):
    units = np.concatenate([
        d["self_x"][train],
        d["ally_x"][train][d["ally_m"][train]],
        d["enemy_x"][train][d["enemy_m"][train]],
    ])
    return dict(
        unit_mean=units.mean(0), unit_std=units.std(0) + 1e-6,
        game_mean=d["game_x"][train].mean(0), game_std=d["game_x"][train].std(0) + 1e-6,
        label_mean=d["label"][train].mean(), label_std=d["label"][train].std(),
    )


def normalise(d, stats):
    out = dict(d)
    for k in ["self_x", "ally_x", "enemy_x"]:
        out[k] = (d[k] - stats["unit_mean"]) / stats["unit_std"]
    out["ally_x"] = out["ally_x"] * d["ally_m"][..., None]
    out["enemy_x"] = out["enemy_x"] * d["enemy_m"][..., None]
    out["game_x"] = (d["game_x"] - stats["game_mean"]) / stats["game_std"]
    out["label"] = (d["label"] - stats["label_mean"]) / stats["label_std"]
    return out


def load(device):
    d = dict(np.load(OUT / "dataset.npz"))
    stats = norm_stats(d, d["split"] == "train")
    d = normalise(d, stats)
    splits = {}
    for name in ["train", "val", "test"]:
        m = d["split"] == name
        splits[name] = {k: torch.as_tensor(d[k][m].astype(np.float32) if d[k].dtype == np.float64 else d[k][m]).to(device) for k in TENSORS}
    return splits, stats


def batches(data, size, shuffle):
    n = len(data["label"])
    order = torch.randperm(n, device=data["label"].device) if shuffle else torch.arange(n, device=data["label"].device)
    for i in range(0, n, size):
        idx = order[i:i + size]
        yield {k: v[idx] for k, v in data.items()}
