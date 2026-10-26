import numpy as np
import torch

from common import OUT
from dataset import normalise
from features import GAME_FEATURES, UNIT_FEATURES
from model import FightQ

SEEDS = [0, 1, 2, 3, 4]
KEYS = ["self_x", "self_t", "game_x", "ally_x", "ally_t", "ally_m", "enemy_x", "enemy_t", "enemy_m"]


@torch.no_grad()
def gaps(ckpt, d, device):
    model = FightQ(len(UNIT_FEATURES), len(GAME_FEATURES)).to(device)
    model.load_state_dict(ckpt["state"])
    model.eval()
    reach = torch.as_tensor(d["reach_m"], device=device)
    out = []
    for i in range(0, len(d["label"]), 65536):
        b = {k: torch.as_tensor(d[k][i:i + 65536], device=device) for k in KEYS}
        q_engage, q_stay = model(b)
        best = q_engage.masked_fill(~reach[i:i + 65536], -1e9).max(1).values
        out.append((best - q_stay).cpu().numpy())
    return np.concatenate(out)


def commit(gap, same_run, delta):
    choice = np.zeros(len(gap), bool)
    for i in range(len(gap)):
        prev = choice[i - 1] if i > 0 and same_run[i] else False
        choice[i] = gap[i] > (-delta if prev else delta)
    return choice


def flip_rate(choice, same_run):
    return (choice[1:] != choice[:-1])[same_run[1:]].mean()


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    raw = dict(np.load(OUT / "dataset.npz"))
    val = raw["split"] == "val"
    ckpts = [torch.load(OUT / f"model_s{s}.pt", weights_only=False) for s in SEEDS]
    d = normalise({k: v[val] for k, v in raw.items()}, ckpts[0]["stats"])
    order = np.lexsort((d["idx"], d["champ"], d["game"]))
    d = {k: v[order] for k, v in d.items()}
    same_run = np.zeros(len(order), bool)
    same_run[1:] = (d["game"][1:] == d["game"][:-1]) & (d["champ"][1:] == d["champ"][:-1]) & (d["idx"][1:] == d["idx"][:-1] + 1)

    G = np.stack([gaps(c, d, device) for c in ckpts])
    g0, gmean = G[0], G.mean(0)
    rmse = np.sqrt(0.73)
    print(f"{len(g0)} val decisions, {same_run.mean():.0%} continue the previous round's decision run")
    print(f"\nCheck 1: |Q(engage) - Q(stay)| vs model error (RMSE ~ {rmse:.2f}, label std units)")
    for q in [50, 75, 90, 99]:
        print(f"  {q}th percentile |gap|: {np.percentile(np.abs(g0), q):.3f}")
    print(f"  seed-to-seed std of the gap: {G.std(0).mean():.3f}")

    agree = (np.sign(G) == np.sign(G[0])).all(0)
    print(f"\nEnsemble: all 5 agree on {agree.mean():.1%} of decisions")
    print(f"  engage rate: model0 {np.mean(g0 > 0):.1%}, ensemble-agreed engage {np.mean(agree & (gmean > 0)):.1%}, agreed stay {np.mean(agree & (gmean < 0)):.1%}")

    print("\nCheck 2: flip rate between consecutive rounds (same champion)")
    print(f"  model0 plain:            {flip_rate(g0 > 0, same_run):.1%}")
    for delta in [0.05, 0.1, 0.2]:
        print(f"  model0 commit delta={delta}: {flip_rate(commit(g0, same_run, delta), same_run):.1%}")
    print(f"  ensemble mean plain:     {flip_rate(gmean > 0, same_run):.1%}")
    actual = d["engaged_m"].any(1)
    print(f"  logged players:          {flip_rate(actual, same_run):.1%}")


if __name__ == "__main__":
    main()
