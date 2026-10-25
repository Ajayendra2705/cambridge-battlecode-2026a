from multiprocessing import Pool

import pandas as pd

from actions import engaged
from common import OUT, cooldowns, load_game
from simfight import dist, engage_decision


def bucket(d, rnd, champ):
    if d["prey"] is None:
        near = min(dist(rnd["c"][champ], rnd["c"][j]) for j in rnd["vis"][champ])
        return "no prey, enemy <=6" if near <= 6 else "no prey, enemy 7+"
    s = d["sim"]
    margin = s["dead"][1] - s["dead"][0]
    if margin > 0:
        return "sim: we kill more"
    if margin < 0:
        return "sim: they kill more"
    return "sim: even, hp ahead" if s["hp_frac"][0] > s["hp_frac"][1] + 0.2 else "sim: even, not ahead"


def game_rows(args):
    game, decisions = args
    _, rounds = load_game(game)
    cds = cooldowns(rounds)
    rows = []
    for (idx, champ), enemies in decisions:
        rnd = rounds[idx]
        d = engage_decision(rnd, cds[idx], champ)
        rows.append((game, idx, champ, bucket(d, rnd, champ), d["engage"], bool(engaged(rounds, idx, champ) & enemies)))
    return rows


def main():
    events = pd.read_parquet(OUT / "events.parquet")
    jobs = [
        (g, [(key, set(e["enemy"])) for key, e in df.groupby(["idx", "champ"])])
        for g, df in events.groupby("game")
    ]
    with Pool(6) as pool:
        chunks = pool.map(game_rows, jobs, chunksize=4)
    cov = pd.DataFrame([r for c in chunks for r in c], columns=["game", "idx", "champ", "bucket", "bot_engage", "engaged"])
    cov.to_parquet(OUT / "coverage.parquet")
    table = cov.groupby("bucket").agg(n=("engaged", "size"), engaged=("engaged", "mean"), bot_engage=("bot_engage", "mean"))
    table["n_engaged"] = (table["n"] * table["engaged"]).round().astype(int)
    table["n_not"] = table["n"] - table["n_engaged"]
    print(f"{len(cov)} decisions, engaged {cov['engaged'].mean():.1%}")
    print(table.sort_values("n", ascending=False).to_string(float_format=lambda x: f"{x:.1%}"))


if __name__ == "__main__":
    main()
