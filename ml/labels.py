import pandas as pd

from common import OUT, load_game


def label(rounds, idx, champ, H, lam):
    pass


def main():
    events = pd.read_parquet(OUT / "events.parquet")
    game = events["game"].iloc[0]
    _, rounds = load_game(game)
    sample = events[events["game"] == game].drop_duplicates(["idx", "champ"]).head(5)
    for idx, champ, enemy in sample[["idx", "champ", "enemy"]].itertuples(index=False):
        print(
            f"round {rounds[idx]['r']} champ {champ} enemy {enemy}: label {label(rounds, idx, champ, H=20, lam=10)}"
        )


if __name__ == "__main__":
    main()
