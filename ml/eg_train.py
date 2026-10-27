import copy
import sys

import numpy as np
import torch
from torch import nn

from common import OUT

EPOCHS, BATCH, LR, PATIENCE = 40, 4096, 3e-3, 5


class EnemyGainMLP(nn.Module):
    def __init__(self, n_x, hidden=16):
        super().__init__()
        self.x = nn.Linear(n_x, hidden)
        self.ty = nn.Embedding(13, hidden)
        self.out = nn.Linear(hidden, 2)

    def forward(self, x, ty):
        return self.out(torch.relu(self.x(x) + self.ty(ty)))


def target(label, mode):
    return np.log1p(np.maximum(label, 0)) if mode == "log1p" else label


def loss_fn(out, y, mode):
    if mode == "poisson":
        return nn.functional.poisson_nll_loss(out, y, log_input=True, reduction="none").mean(0)
    return ((out - y) ** 2).mean(0)


def to_gems(out, stats):
    if stats["mode"] == "poisson":
        return np.exp(out)
    out = out * stats["y_std"] + stats["y_mean"]
    return np.expm1(out) if stats["mode"] == "log1p" else out


@torch.no_grad()
def predict(model, x, ty):
    model.eval()
    out = torch.cat([model(x[i:i + 65536], ty[i:i + 65536]) for i in range(0, len(x), 65536)])
    model.train()
    return out


def train(d, mode="raw", seed=0, device="cpu"):
    torch.manual_seed(seed)
    tr = d["split"] == "train"
    mean, std = d["x"][tr].mean(0), d["x"][tr].std(0) + 1e-6
    y = target(d["label"], mode).astype(np.float32)
    y_mean, y_std = y[tr].mean(0), y[tr].std(0) + 1e-6
    if mode != "poisson":
        y = (y - y_mean) / y_std
    t = {s: (torch.as_tensor((d["x"][d["split"] == s] - mean) / std).to(device), torch.as_tensor(d["e_type"][d["split"] == s]).to(device),
             torch.as_tensor(y[d["split"] == s]).to(device)) for s in ["train", "val"]}
    model = EnemyGainMLP(d["x"].shape[1]).to(device)
    (xt, tt, yt), (xv, tv, yv) = t["train"], t["val"]
    if mode == "poisson":
        with torch.no_grad():
            model.out.bias.copy_(torch.log(yt.mean(0)))
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    best, best_state, bad = float("inf"), None, 0
    for epoch in range(EPOCHS):
        perm = torch.randperm(len(yt), device=device)
        for i in range(0, len(perm), BATCH):
            b = perm[i:i + BATCH]
            loss = loss_fn(model(xt[b], tt[b]), yt[b], mode).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
        val = loss_fn(predict(model, xv, tv), yv, mode).mean().item()
        if val < best:
            best, best_state, bad = val, copy.deepcopy(model.state_dict()), 0
        else:
            bad += 1
            if bad >= PATIENCE:
                break
    model.load_state_dict(best_state)
    mse = loss_fn(predict(model, xv, tv), yv, mode).cpu().numpy()
    base = torch.log(yt.mean(0)).expand_as(yv) if mode == "poisson" else yt.mean(0).expand_as(yv)
    const = loss_fn(base, yv, mode).cpu().numpy()
    return model, dict(mean=mean, std=std, y_mean=y_mean, y_std=y_std, mode=mode), mse, const


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "raw"
    d = dict(np.load(OUT / "eg_dataset.npz"))
    if np.isnan(d["label"]).all():
        sys.exit("no labels: write ml/eg_labels.py (enemy_gain and HORIZON), then rerun eg_data.py")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, stats, mse, const = train(d, mode, device=device)
    for k, name in enumerate(["gems", "gold"]):
        print(f"[{mode}] {name}: val loss {mse[k]:.4f} (constant {const[k]:.4f})")
    torch.save(dict(state=model.state_dict(), stats=stats, features=list(d["features"])), OUT / f"eg_{mode}.pt")


if __name__ == "__main__":
    main()
