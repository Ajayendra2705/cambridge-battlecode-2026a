from multiprocessing import Pool

import pandas as pd

from common import OUT, load_game, load_games
from simfight import CHAMPS, alive, dist


def reach(c):
    return max(CHAMPS[c["ty"]]["range"], 4)


def find_decisions(game):
    _, rounds = load_game(game)
    rows = []
    for idx, rnd in enumerate(rounds):
        c = rnd["c"]
        for champ, enemies in enumerate(rnd["vis"]):
            if not alive(c[champ]):
                continue
            for enemy in enemies:
                if alive(c[enemy]) and (d := dist(c[champ], c[enemy])) <= reach(c[champ]):
                    rows.append((game, idx, rnd["r"], champ, enemy, c[champ]["t"], d))
    return rows


def main():
    games = load_games()
    games = games[~games["map"].str.contains("boss_battle")]
    with Pool(6) as pool:
        chunks = pool.map(find_decisions, games["game"], chunksize=8)
    events = pd.DataFrame(
        [row for chunk in chunks for row in chunk],
        columns=["game", "idx", "r", "champ", "enemy", "team", "dist"],
    )
    events = events.merge(games[["game", "split"]], on="game")
    events.to_parquet(OUT / "events.parquet")
    decisions = events.groupby(["game", "idx", "champ"]).size()
    print(f"{len(events)} (champion, enemy) rows, {len(decisions)} decisions, {events['game'].nunique()} games")
    print(f"enemies in reach per decision: {decisions.value_counts().sort_index().to_dict()}")
    print(events["split"].value_counts().to_string())


if __name__ == "__main__":
    main()
