import sys
import zipfile
from pathlib import Path

import numpy as np
import torch

from common import OUT, cooldowns, load_game
from features import UNIT_FEATURES, unit
from simfight import alive


def main():
    bundle, extracted = Path(sys.argv[1]), Path(sys.argv[2])
    ckpt = torch.load(OUT / "model.pt", weights_only=False)
    s = ckpt["stats"]
    _, rounds = load_game(extracted)
    by_round = {rnd["r"]: i for i, rnd in enumerate(rounds)}
    cds = cooldowns(rounds)

    with zipfile.ZipFile(bundle) as z:
        text = z.read("team-a.stdout").decode(errors="replace").replace("\0", "")
    diffs = {f: [] for f in UNIT_FEATURES}
    game_diffs, n = [], 0
    for line in text.splitlines():
        if not line.startswith("FQ "):
            continue
        head, game_part, *units = line[3:].split(" | ")
        nums = head.split("|")[0].split()
        r, x, y = int(nums[0]), int(nums[1]), int(nums[2])
        bot_game = [float(v) for v in game_part.split()]
        bot_units = [[float(v) for v in u.split()] for u in units]
        idx = by_round.get(r)
        if idx is None:
            continue
        rnd = rounds[idx]
        c = rnd["c"]
        champ = next((i for i, ch in enumerate(c) if ch["t"] == 0 and alive(ch) and ch["x"] == x and ch["y"] == y), None)
        if champ is None:
            continue
        me = c[champ]
        py_units = [(me["ty"], unit(me, me, cds[idx][champ]))]
        py_units += [(c[j]["ty"], unit(me, c[j], cds[idx][j])) for j in rnd["avis"][champ] if alive(c[j])]
        py_units += [(c[j]["ty"], unit(me, c[j], cds[idx][j])) for j in rnd["vis"][champ] if alive(c[j])]
        raw_bot = [(int(u[0]), np.array(u[1:]) * s["unit_std"] + s["unit_mean"]) for u in bot_units]
        n += 1
        for t, bu in raw_bot:
            match = min((pu for pu in py_units if pu[0] == t), key=lambda pu: np.abs(np.array(pu[1][:2]) - bu[:2]).sum(), default=None)
            if match is None:
                continue
            for k, f in enumerate(UNIT_FEATURES):
                diffs[f].append(bu[k] - match[1][k])
        py_game = (np.array([rnd["r"], rnd["sg"][0] - rnd["sg"][1]]) - s["game_mean"]) / s["game_std"]
        game_diffs.append(np.array(bot_game) - py_game)
    print(f"{n} logged decisions matched")
    print(f"{'feature':10s} {'exact':>7s} {'mean diff':>10s} {'max |diff|':>10s}")
    for f, d in diffs.items():
        d = np.array(d)
        print(f"{f:10s} {np.mean(np.abs(d) < 1e-3):7.1%} {d.mean():10.3f} {np.abs(d).max():10.3f}")
    g = np.array(game_diffs) * s["game_std"]
    print("game diffs (raw units): mean", g.mean(0).round(3), "max", np.abs(g).max(0).round(3))


if __name__ == "__main__":
    main()
