import gzip, json, sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data/fights/ranked"
OUT = ROOT / "data/ml"


def load_game(path):
    with gzip.open(path, "rt") as f:
        lines = [json.loads(l) for l in f]
    return lines[0], lines[1:]


def pair_gaps(rounds):
    pass


def main():
    n_games = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    files = sorted(DATA.glob("*.jsonl.gz"))[:n_games]
    gaps = Counter()
    for path in files:
        _, rounds = load_game(path)
        gaps.update(pair_gaps(rounds))

    print(f"{sum(gaps.values())} gaps from {len(files)} games")
    for length, count in sorted(gaps.items())[:30]:
        print(f"{length:5d} {count:7d}")

    OUT.mkdir(parents=True, exist_ok=True)
    lengths = sorted(gaps)
    plt.figure(figsize=(9, 4))
    plt.bar(lengths, [gaps[l] for l in lengths], width=1.0)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("rounds out of view before reappearing")
    plt.ylabel("number of gaps")
    plt.title(f"Vision gap lengths, {len(files)} games")
    plt.tight_layout()
    plt.savefig(OUT / "vis_gaps.png", dpi=120)
    print("saved", OUT / "vis_gaps.png")


if __name__ == "__main__":
    main()
