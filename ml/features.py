import math
from multiprocessing import Pool

import numpy as np
import pandas as pd

from actions import engaged
from common import OUT, cooldowns, load_game
from labels import LAM, H, label
from simfight import CHAMPS, alive, stats

MAX_ALLIES, MAX_ENEMIES = 5, 6
UNIT_FEATURES = ["dx", "dy", "dist", "hp", "hp_frac", "log_gems", "str", "focus", "cd0", "cd1", "range"]
GAME_FEATURES = ["round", "score_diff"]


def unit(me, c, cd):
    strength, focus = stats(c)
    dx, dy = c["x"] - me["x"], c["y"] - me["y"]
    return [dx, dy, max(abs(dx), abs(dy)), c["hp"], c["hp"] / c["mhp"], math.log1p(c["g"]), strength, focus, cd[0], cd[1], CHAMPS[c["ty"]]["range"]]


def game_arrays(args):
    game, decisions = args
    _, rounds = load_game(game)
    cds = cooldowns(rounds)
    n = len(decisions)
    F = len(UNIT_FEATURES)
    out = dict(
        self_x=np.zeros((n, F), np.float32), self_t=np.zeros(n, np.int64),
        game_x=np.zeros((n, len(GAME_FEATURES)), np.float32),
        ally_x=np.zeros((n, MAX_ALLIES, F), np.float32), ally_t=np.zeros((n, MAX_ALLIES), np.int64), ally_m=np.zeros((n, MAX_ALLIES), bool),
        enemy_x=np.zeros((n, MAX_ENEMIES, F), np.float32), enemy_t=np.zeros((n, MAX_ENEMIES), np.int64), enemy_m=np.zeros((n, MAX_ENEMIES), bool),
        reach_m=np.zeros((n, MAX_ENEMIES), bool), engaged_m=np.zeros((n, MAX_ENEMIES), bool),
        label=np.zeros(n, np.float32), idx=np.zeros(n, np.int64), champ=np.zeros(n, np.int64),
    )
    for k, ((idx, champ), in_reach) in enumerate(decisions):
        rnd = rounds[idx]
        c, cd = rnd["c"], cds[idx]
        me = c[champ]
        out["self_x"][k] = unit(me, me, cd[champ])
        out["self_t"][k] = me["ty"]
        out["game_x"][k] = [rnd["r"], rnd["sg"][me["t"]] - rnd["sg"][1 - me["t"]]]
        allies = [j for j in rnd["avis"][champ] if alive(c[j])][:MAX_ALLIES]
        for s, j in enumerate(allies):
            out["ally_x"][k, s] = unit(me, c[j], cd[j])
            out["ally_t"][k, s] = c[j]["ty"]
            out["ally_m"][k, s] = True
        hit = engaged(rounds, idx, champ)
        enemies = [j for j in rnd["vis"][champ] if alive(c[j])][:MAX_ENEMIES]
        for s, j in enumerate(enemies):
            out["enemy_x"][k, s] = unit(me, c[j], cd[j])
            out["enemy_t"][k, s] = c[j]["ty"]
            out["enemy_m"][k, s] = True
            out["reach_m"][k, s] = j in in_reach
            out["engaged_m"][k, s] = j in in_reach and j in hit
        out["label"][k] = label(rounds, idx, champ, H, LAM)
        out["idx"][k], out["champ"][k] = idx, champ
    return game, out


def main():
    events = pd.read_parquet(OUT / "events.parquet")
    split = events.groupby("game")["split"].first()
    jobs = [
        (g, [(key, set(e["enemy"])) for key, e in df.groupby(["idx", "champ"])])
        for g, df in events.groupby("game")
    ]
    with Pool(6) as pool:
        results = pool.map(game_arrays, jobs, chunksize=4)
    arrays = {k: np.concatenate([out[k] for _, out in results]) for k in results[0][1]}
    games = np.concatenate([[g] * len(out["label"]) for g, out in results])
    arrays["game"] = games
    arrays["split"] = split.loc[games].to_numpy().astype(str)
    np.savez(OUT / "dataset.npz", **arrays)
    n = len(arrays["label"])
    stay = ~arrays["engaged_m"].any(1)
    print(f"{n} decisions, {arrays['enemy_m'].sum(1).mean():.2f} enemies and {arrays['ally_m'].sum(1).mean():.2f} allies visible on average")
    print(f"engaged {1 - stay.mean():.1%}; label mean {arrays['label'].mean():.2f} std {arrays['label'].std():.2f}")
    print(f"label mean engaged {arrays['label'][~stay].mean():.2f}, stay {arrays['label'][stay].mean():.2f}")


if __name__ == "__main__":
    main()
