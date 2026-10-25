import pandas as pd

from common import OUT, load_game


def label(rounds, idx, champ, H, lam):
    end = min(idx + H, len(rounds) - 1)
    start_rnd, end_rnd = rounds[idx], rounds[end]
    window = rounds[idx : end + 1]

    us = start_rnd["c"][champ]["t"]
    them = 1 - us

    our_carried_start = sum(c["g"] for c in start_rnd["c"] if c["t"] == us)
    our_carried_end = sum(c["g"] for c in end_rnd["c"] if c["t"] == us)
    their_carried_start = sum(c["g"] for c in start_rnd["c"] if c["t"] == them)
    their_carried_end = sum(c["g"] for c in end_rnd["c"] if c["t"] == them)

    our_tributed_start, our_tributed_end = start_rnd["sg"][us], end_rnd["sg"][us]
    their_tributed_start, their_tributed_end = (
        start_rnd["sg"][them],
        end_rnd["sg"][them],
    )

    my_carried_start, my_carried_end = (
        start_rnd["c"][champ]["g"],
        end_rnd["c"][champ]["g"],
    )

    deaths = [0, 0]
    my_deaths = 0
    for prev, cur in zip(window, window[1:]):
        for j, (p, c) in enumerate(zip(prev["c"], cur["c"])):
            if p["a"] and not c["a"]:
                deaths[c["t"]] += 1
                if j == champ:
                    my_deaths += 1
    our_deaths, their_deaths = deaths[us], deaths[them]


def main():
    events = pd.read_parquet(OUT / "events.parquet")
    game = events["game"].iloc[0]
    _, rounds = load_game(game)
    sample = events[events["game"] == game].groupby(["idx", "champ"]).head(1).head(5)
    for idx, champ, enemy in sample[["idx", "champ", "enemy"]].itertuples(index=False):
        print(
            f"round {rounds[idx]['r']} champ {champ} enemy {enemy}: label {label(rounds, idx, champ, H=20, lam=10)}"
        )


if __name__ == "__main__":
    main()
