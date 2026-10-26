import copy
import sys

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch import nn

from common import OUT
from reinforce_train import ReinforceNet, standardise

KEYS = ["self_x", "self_t", "game_x", "ally_x", "ally_t", "ally_m", "enemy_x", "enemy_t", "enemy_m", "mem_x", "mem_t", "mem_m", "success", "rounds"]
N_GROUP_ONLY = 9
EPOCHS, BATCH, LR, PATIENCE = 30, 8192, 3e-3, 4


class GroupMLP(nn.Module):
    def __init__(self, n_game, n_self, hidden=16):
        super().__init__()
        self.game = nn.Linear(n_game, hidden)
        self.me = nn.Linear(n_self, hidden, bias=False)
        self.ty = nn.Embedding(13, hidden)
        self.out = nn.Linear(hidden, 2)

    def forward(self, b):
        h = torch.relu(self.game(b["game_x"]) + self.me(b["self_x"]) + self.ty(b["self_t"]))
        o = self.out(h)
        return o[:, 0], o[:, 1]


def loss_fn(out, b):
    logit, log_t = out
    bce = nn.functional.binary_cross_entropy_with_logits(logit, b["success"])
    ok = b["success"] > 0
    mse = ((log_t - torch.log(b["rounds"]))[ok] ** 2).mean() if ok.any() else torch.zeros((), device=logit.device)
    return bce + mse, bce, mse


@torch.no_grad()
def evaluate(model, data):
    model.eval()
    outs = [model({k: v[i:i + 65536] for k, v in data.items()}) for i in range(0, len(data["success"]), 65536)]
    model.train()
    logit = torch.cat([o[0] for o in outs])
    log_t = torch.cat([o[1] for o in outs])
    _, bce, mse = loss_fn((logit, log_t), data)
    return bce.item(), mse.item(), torch.sigmoid(logit).cpu().numpy(), log_t.cpu().numpy()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    group_only = mode in ("group_only", "mlp")
    torch.manual_seed(0)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    raw = dict(np.load(OUT / "fpr_dataset.npz"))
    raw["label"] = raw["success"]
    d, stats = standardise(raw, raw["split"] == "train")
    if group_only:
        d["game_x"] = d["game_x"].copy()
        d["game_x"][:, N_GROUP_ONLY:N_GROUP_ONLY + 2] = 0
        for k in ["self_x", "ally_x", "enemy_x", "mem_x"]:
            d[k] = np.zeros_like(d[k])
        for k in ["ally_m", "enemy_m", "mem_m"]:
            d[k] = np.zeros_like(d[k])
    split = {s: {k: torch.as_tensor(d[k][d["split"] == s]).to(device) for k in KEYS} for s in ["train", "val"]}
    if mode == "mlp":
        raw["game_x"][:, -1] = 0
        raw["rounds"] = raw["clear"]
        d["rounds"] = raw["clear"]
        stats["game"] = (raw["game_x"][raw["split"] == "train"].mean(0), raw["game_x"][raw["split"] == "train"].std(0) + 1e-6)
        d["self_x"] = (raw["self_x"] - stats["unit"][0]) / stats["unit"][1]
        d["game_x"] = (raw["game_x"] - stats["game"][0]) / stats["game"][1]
        split = {s_: {k: torch.as_tensor(d[k][d["split"] == s_]).to(device) for k in KEYS} for s_ in ["train", "val"]}
        model = GroupMLP(d["game_x"].shape[1], d["self_x"].shape[1]).to(device)
    else:
        model = ReinforceNet(d["self_x"].shape[1], d["mem_x"].shape[2], d["game_x"].shape[1], hidden=16, shared=True).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    tr, va = split["train"], split["val"]
    best, best_state, bad = float("inf"), None, 0
    for epoch in range(EPOCHS):
        perm = torch.randperm(len(tr["success"]), device=device)
        for i in range(0, len(perm), BATCH):
            b = {k: v[perm[i:i + BATCH]] for k, v in tr.items()}
            loss, _, _ = loss_fn(model(b), b)
            opt.zero_grad()
            loss.backward()
            opt.step()
        bce, mse, _, _ = evaluate(model, va)
        if bce + mse < best:
            best, best_state, bad = bce + mse, copy.deepcopy(model.state_dict()), 0
        else:
            bad += 1
            if bad >= PATIENCE:
                break
    model.load_state_dict(best_state)
    bce, mse, p, log_t = evaluate(model, va)
    y, t = va["success"].cpu().numpy(), va["rounds"].cpu().numpy()
    ok = y > 0
    base_p = np.full_like(y, tr["success"].float().mean().item())
    base_t = np.full(ok.sum(), np.log(tr["rounds"][tr["success"] > 0].cpu().numpy()).mean())
    name = mode
    print(f"[{name}] val: success AUC {roc_auc_score(y, p):.3f}, logloss {bce:.4f} (constant {nn.functional.binary_cross_entropy(torch.tensor(base_p), torch.tensor(y)).item():.4f}); "
          f"log-rounds MSE {mse:.4f} (constant {np.mean((np.log(t[ok]) - base_t) ** 2):.4f}), typical error x{np.exp(np.sqrt(mse)):.2f}")
    torch.save(dict(state=best_state, stats=stats, mode=mode), OUT / f"fpr_{mode}.pt")


if __name__ == "__main__":
    main()
