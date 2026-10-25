from multiprocessing import Pool

import pandas as pd

from common import OUT, load_game, load_games

EVERY = 50


def game_snapshots(args):
    game, winner = args
    _, rounds = load_game(game)
    rows = []
    for rnd in rounds[::EVERY]:
        team = [[c for c in rnd["c"] if c["t"] == t] for t in (0, 1)]
        tributed = rnd["sg"]
        carried = [sum(c["g"] for c in team[t]) for t in (0, 1)]
        alive = [sum(c["a"] for c in team[t]) for t in (0, 1)]
        rows.append((game, rnd["r"], tributed[0] - tributed[1], carried[0] - carried[1], alive[0] - alive[1], int(winner == 0)))
    return rows


def main():
    games = load_games()
    games = games[games["winner"] >= 0]
    with Pool(6) as pool:
        chunks = pool.map(game_snapshots, list(zip(games["game"], games["winner"])), chunksize=8)
    snaps = pd.DataFrame(
        [r for c in chunks for r in c],
        columns=["game", "r", "d_tributed", "d_carried", "d_alive", "a_wins"],
    )
    snaps = snaps.merge(games[["game", "split"]], on="game")
    snaps.to_parquet(OUT / "snapshots.parquet")
    print(f"{len(snaps)} snapshots from {snaps['game'].nunique()} games")
    print(snaps.describe().round(1).to_string())


if __name__ == "__main__":
    main()
