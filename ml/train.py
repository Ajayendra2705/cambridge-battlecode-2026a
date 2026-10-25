import copy
import sys
import time

import torch

from common import OUT
from dataset import batches, load
from features import GAME_FEATURES, UNIT_FEATURES
from model import FightQ, q_loss

EPOCHS = 20
BATCH = 8192
LR = 3e-3
PATIENCE = 3


@torch.no_grad()
def evaluate(model, data):
    model.eval()
    total, n = 0.0, 0
    for b in batches(data, 65536, shuffle=False):
        q_engage, q_stay = model(b)
        k = len(b["label"])
        total += q_loss(q_engage, q_stay, b).item() * k
        n += k
    model.train()
    return total / n


def constant_baseline(train, data):
    stay_tr = ~train["engaged_m"].any(1)
    m_engage, m_stay = train["label"][~stay_tr].mean(), train["label"][stay_tr].mean()
    stay = ~data["engaged_m"].any(1)
    y = data["label"]
    return dict(
        global_mean=((y - train["label"].mean()) ** 2).mean().item(),
        per_action_mean=torch.where(stay, (y - m_stay) ** 2, (y - m_engage) ** 2).mean().item(),
    )


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data, stats = load(device)
    model = FightQ(len(UNIT_FEATURES), len(GAME_FEATURES)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    print(f"{sum(p.numel() for p in model.parameters())} parameters, train {len(data['train']['label'])} val {len(data['val']['label'])}")
    print("val baselines (MSE, label in std units):", {k: round(v, 4) for k, v in constant_baseline(data["train"], data["val"]).items()})

    best, best_state, bad = float("inf"), None, 0
    for epoch in range(EPOCHS):
        t, total, n = time.time(), 0.0, 0
        for b in batches(data["train"], BATCH, shuffle=True):
            q_engage, q_stay = model(b)
            loss = q_loss(q_engage, q_stay, b)
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * len(b["label"])
            n += len(b["label"])
        val = evaluate(model, data["val"])
        print(f"epoch {epoch:2d}  train {total / n:.4f}  val {val:.4f}  {time.time() - t:.1f}s")
        if val < best:
            best, best_state, bad = val, copy.deepcopy(model.state_dict()), 0
        else:
            bad += 1
            if bad >= PATIENCE:
                break

    torch.save(dict(state=best_state, stats=stats, unit_features=UNIT_FEATURES, game_features=GAME_FEATURES), OUT / f"model_s{seed}.pt")
    print(f"seed {seed} best val {best:.4f}")


if __name__ == "__main__":
    main()
