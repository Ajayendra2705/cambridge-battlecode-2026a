import numpy as np
import torch
from sklearn.linear_model import LinearRegression

from fpr_data import CAMP_TYPES
from fpr_train import evaluate
from common import OUT
from reinforce_train import ReinforceNet, standardise
from simfight import CHAMPS, AOE, DAMAGE, RESET

CAMP_STR = {"wolf": 20, "elk": 60, "gem_cluster": 0, "gold_cluster": 0, "golem": 120, "monolith": 200}
CAMP_RANGE = {"wolf": 3, "elk": 4, "gem_cluster": 3, "gold_cluster": 3, "golem": 4, "monolith": 5}


def formula_time(self_x, self_t, game_x):
    hp, strength, focus = self_x[3], self_x[6], self_x[7]
    dps = strength
    for kind, mod in CHAMPS[int(self_t)]["slots"]:
        if kind in (DAMAGE, AOE):
            dps += mod * focus / 8
        if kind == RESET:
            dps += strength / 8
    counts = dict(zip(CAMP_TYPES, game_x[:len(CAMP_TYPES)]))
    camps = [t for t in CAMP_TYPES for _ in range(int(counts[t]))]
    g_hp = game_x[len(CAMP_TYPES)]
    g_str = sum(CAMP_STR[t] for t in camps)
    hardest = max((CAMP_STR[t] for t in camps), default=0)
    rng = max((CAMP_RANGE[t] for t in camps), default=3)
    n = 1 + int(game_x[9])
    home = game_x[11]
    t_fight = g_hp / max(1.0, dps * n)
    damage = t_fight * g_str * (0.7 if len(camps) > 1 else 1.0)
    usable = hp - (rng + 1) * hardest - 40.0
    if usable <= 50.0:
        return 1e3
    trips = max(0.0, damage / (usable * n) - 1.0)
    return game_x[17] + t_fight + trips * (6.0 + home) / n + 5.0


def main():
    raw = dict(np.load(OUT / "fpr_dataset.npz"))
    val = raw["split"] == "val"
    ok = val & (raw["success"] > 0)
    pred = np.array([formula_time(sx, st, gx) for sx, st, gx in zip(raw["self_x"][ok], raw["self_t"][ok], raw["game_x"][ok])])
    y = np.log(raw["rounds"][ok])
    lp = np.log(np.clip(pred, 1, 1e3))
    raw_mse = np.mean((lp - y) ** 2)
    fit = LinearRegression().fit(lp[:, None], y)
    cal_mse = np.mean((fit.predict(lp[:, None]) - y) ** 2)
    print(f"bot formula travel + clear_time + 5: log-rounds MSE {raw_mse:.4f} raw, {cal_mse:.4f} after fitting scale/offset on val itself "
          f"(slope {fit.coef_[0]:.2f}); constant {np.var(y):.4f}")

    ckpt = torch.load(OUT / "fpr_full.pt", weights_only=False)
    raw["label"] = raw["success"]
    d, _ = standardise(raw, raw["split"] == "train")
    keys = ["self_x", "self_t", "game_x", "ally_x", "ally_t", "ally_m", "enemy_x", "enemy_t", "enemy_m", "mem_x", "mem_t", "mem_m", "success", "rounds"]
    data = {k: torch.as_tensor(d[k][val]) for k in keys}
    model = ReinforceNet(d["self_x"].shape[1], d["mem_x"].shape[2], d["game_x"].shape[1], hidden=16, shared=True)
    model.load_state_dict(ckpt["state"])
    _, mse, _, _ = evaluate(model, data)
    print(f"model (full): log-rounds MSE {mse:.4f}")


if __name__ == "__main__":
    main()
