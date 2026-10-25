import copy
import sys

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression, PoissonRegressor
from sklearn.metrics import roc_auc_score
from torch import nn

from common import OUT
from model import N_TYPES

KEYS = ["self_x", "self_t", "game_x", "ally_x", "ally_t", "ally_m", "enemy_x", "enemy_t", "enemy_m", "mem_x", "mem_t", "mem_m", "label", "ally_label"]
EPOCHS, BATCH, LR, PATIENCE = 20, 8192, 3e-3, 3


class ReinforceNet(nn.Module):
    def __init__(self, n_unit, n_mem, n_game, width=16, hidden=16, shared=False):
        super().__init__()
        self.unit_x, self.unit_t = nn.Linear(n_unit, width), nn.Embedding(N_TYPES, width)
        self.mem_x, self.mem_t = nn.Linear(n_mem, width), nn.Embedding(N_TYPES, width)
        self.shared = shared
        if shared:
            self.head = nn.Sequential(nn.Linear(4 * width + n_game, hidden), nn.ReLU(), nn.Linear(hidden, 2))
        else:
            self.head_e = nn.Sequential(nn.Linear(4 * width + n_game, hidden), nn.ReLU(), nn.Linear(hidden, 1))
            self.head_a = nn.Sequential(nn.Linear(4 * width + n_game, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, b):
        unit = lambda x, t: torch.relu(self.unit_x(x) + self.unit_t(t))
        me = unit(b["self_x"], b["self_t"])
        allies = (unit(b["ally_x"], b["ally_t"]) * b["ally_m"][..., None]).sum(1)
        enemies = (unit(b["enemy_x"], b["enemy_t"]) * b["enemy_m"][..., None]).sum(1)
        mem = (torch.relu(self.mem_x(b["mem_x"]) + self.mem_t(b["mem_t"])) * b["mem_m"][..., None]).sum(1)
        x = torch.cat([me, allies, enemies, mem, b["game_x"]], -1)
        if self.shared:
            out = self.head(x)
            return out[:, 0], out[:, 1]
        return self.head_e(x).squeeze(-1), self.head_a(x).squeeze(-1)


def standardise(d, train):
    stats = {}
    units = np.concatenate([d["self_x"][train], d["ally_x"][train][d["ally_m"][train]], d["enemy_x"][train][d["enemy_m"][train]]])
    stats["unit"] = (units.mean(0), units.std(0) + 1e-6)
    mem = d["mem_x"][train][d["mem_m"][train]]
    stats["mem"] = (mem.mean(0), mem.std(0) + 1e-6)
    stats["game"] = (d["game_x"][train].mean(0), d["game_x"][train].std(0) + 1e-6)
    out = dict(d)
    for k, s in [("self_x", "unit"), ("ally_x", "unit"), ("enemy_x", "unit"), ("mem_x", "mem"), ("game_x", "game")]:
        out[k] = (d[k] - stats[s][0]) / stats[s][1]
    for k in ["ally", "enemy", "mem"]:
        out[f"{k}_x"] = out[f"{k}_x"] * d[f"{k}_m"][..., None]
    return out, stats


@torch.no_grad()
def predict(model, data):
    model.eval()
    out = [torch.stack(model({k: v[i:i + 65536] for k, v in data.items()}), 1).exp() for i in range(0, len(data["label"]), 65536)]
    model.train()
    return torch.cat(out)


def poisson_dev(y, mu):
    y, mu = np.asarray(y, np.float64), np.clip(np.asarray(mu, np.float64), 1e-6, None)
    return 2 * np.mean(np.where(y > 0, y * np.log(y / mu), 0) - (y - mu))


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    small = len(sys.argv) > 2 and sys.argv[2] == "small"
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    raw = dict(np.load(OUT / "rf_dataset.npz"))
    d, stats = standardise(raw, raw["split"] == "train")
    split = {s: {k: torch.as_tensor(d[k][d["split"] == s]).to(device) for k in KEYS} for s in ["train", "val"]}
    model = ReinforceNet(d["self_x"].shape[1], d["mem_x"].shape[2], d["game_x"].shape[1], hidden=8 if small else 16, shared=small).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.PoissonNLLLoss(log_input=True)
    tr, va = split["train"], split["val"]
    best, best_state, bad = float("inf"), None, 0
    for epoch in range(EPOCHS):
        perm = torch.randperm(len(tr["label"]), device=device)
        for i in range(0, len(perm), BATCH):
            b = {k: v[perm[i:i + BATCH]] for k, v in tr.items()}
            log_e, log_a = model(b)
            loss = loss_fn(log_e, b["label"]) + loss_fn(log_a, b["ally_label"])
            opt.zero_grad()
            loss.backward()
            opt.step()
        mu = predict(model, va).cpu()
        dev_e, dev_a = poisson_dev(va["label"].cpu(), mu[:, 0]), poisson_dev(va["ally_label"].cpu(), mu[:, 1])
        dev = dev_e + dev_a
        print(f"epoch {epoch:2d} val deviance enemy {dev_e:.4f} ally {dev_a:.4f}")
        if dev < best:
            best, best_state, bad = dev, copy.deepcopy(model.state_dict()), 0
        else:
            bad += 1
            if bad >= PATIENCE:
                break
    model.load_state_dict(best_state)
    torch.save(dict(state=best_state, stats=stats, small=small), OUT / (f"rf_small_s{seed}.pt" if small else f"rf_model_s{seed}.pt"))

    val = raw["split"] == "val"
    y, died = raw["label"][val], raw["died"][val]
    mu_both = predict(model, va).cpu().numpy()
    mu, mu_a = mu_both[:, 0], mu_both[:, 1]
    ya = raw["ally_label"][val]
    Xa = lambda m: np.stack([raw["ally_m"][m].sum(1), raw["enemy_m"][m].sum(1)], 1)
    base_a = PoissonRegressor(alpha=0).fit(Xa(raw["split"] == "train"), raw["ally_label"][raw["split"] == "train"]).predict(Xa(val))
    print(f"ally arrivals: deviance baseline(n_allies, n_enemies) {poisson_dev(ya, base_a):.4f} model {poisson_dev(ya, mu_a):.4f}; AUC baseline {roc_auc_score(ya > 0, base_a):.3f} model {roc_auc_score(ya > 0, mu_a):.3f}")
    trm = raw["split"] == "train"
    X = lambda m: np.stack([raw["mem_m"][m].sum(1), raw["enemy_m"][m].sum(1)], 1)
    const = np.full(len(y), raw["label"][trm].mean())
    base = PoissonRegressor(alpha=0).fit(X(trm), raw["label"][trm]).predict(X(val))
    print(f"\nval Poisson deviance: constant {poisson_dev(y, const):.4f}  baseline(n_memory, n_visible) {poisson_dev(y, base):.4f}  model {poisson_dev(y, mu):.4f}")
    print(f"AUC for any arrival: baseline {roc_auc_score(y > 0, base):.3f}  model {roc_auc_score(y > 0, mu):.3f}")
    near = (raw["enemy_m"][val] & (raw["enemy_x"][val][:, :, 2] <= 6)).sum(1)
    for name, feats in [("enemies near now", [near]), ("+ baseline arrivals", [near, base]), ("+ model arrivals", [near, mu]), ("+ model enemy and ally arrivals", [near, mu, mu_a]), ("+ TRUE arrivals (oracle)", [near, y]), ("+ TRUE enemy and ally (oracle)", [near, y, ya])]:
        Xd = np.stack(feats, 1)
        p = LogisticRegression().fit(Xd, died).predict_proba(Xd)[:, 1]
        print(f"AUC for death in the 9 rounds after: {name:26s} {roc_auc_score(died, p):.3f}")


if __name__ == "__main__":
    main()
