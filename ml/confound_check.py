import sys

import numpy as np
import torch

from common import OUT
from dataset import load
from features import GAME_FEATURES, UNIT_FEATURES
from model import FightQ


@torch.no_grad()
def predicted_gap(path, device):
    ckpt = torch.load(OUT / path, weights_only=False)
    variant = ckpt.get("variant", "base")
    data, stats = load(device, variant)
    val = data["val"]
    model = FightQ(len(UNIT_FEATURES), val["game_x"].shape[1], n_teams=ckpt.get("n_teams", 0)).to(device)
    model.load_state_dict(ckpt["state"])
    model.eval()
    gaps = []
    for i in range(0, len(val["label"]), 65536):
        b = {k: v[i:i + 65536] for k, v in val.items()}
        q_engage, q_stay = model(b)
        best = q_engage.masked_fill(~b["reach_m"], -1e9).max(1).values
        gaps.append((best - q_stay).cpu().numpy())
    return np.concatenate(gaps) * float(stats["label_std"])


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    raw = np.load(OUT / "dataset.npz")
    val = raw["split"] == "val"
    g, y, eng = raw["game_x"][val], raw["label"][val], raw["engaged_m"][val].any(1)
    col = {f: i for i, f in enumerate(GAME_FEATURES)}
    prey = g[:, col["has_prey"]] == 1
    buckets = {
        "rule says ENGAGE": prey & (g[:, col["rule_engage"]] == 1),
        "rule says stay": prey & (g[:, col["rule_engage"]] == 0),
        "sim: I die": prey & (g[:, col["sim_me_dies"]] == 1),
        "sim: I survive, kill more": prey & (g[:, col["sim_me_dies"]] == 0) & (g[:, col["sim_dead_them"]] > g[:, col["sim_dead_us"]]),
    }
    models = sys.argv[1:] or ["model_s0.pt", "model_rating_s0.pt", "model_team_s0.pt"]
    gaps = {m: predicted_gap(m, device) for m in models}
    print("engage - stay, in gems (val games)")
    print(f"{'situation':28s} {'raw data':>9s}" + "".join(f"{m.replace('model_', '').replace('.pt', ''):>12s}" for m in models))
    for name, m in buckets.items():
        row = f"{name:28s} {y[m & eng].mean() - y[m & ~eng].mean():9.1f}"
        row += "".join(f"{gaps[k][m].mean():12.1f}" for k in models)
        print(row)
    print(f"{'share predicted engage':28s} {eng.mean():9.1%}" + "".join(f"{(gaps[k] > 0).mean():12.1%}" for k in models))


if __name__ == "__main__":
    main()
