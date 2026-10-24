import gzip, json, random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FIGHTS = ROOT / "data/fights/ranked"
INDEX = ROOT / "data/replays/ranked/index.jsonl"
OUT = ROOT / "data/ml"

COOLDOWN = 8
VENDETTA = 2


def load_game(game):
    path = game if isinstance(game, Path) else FIGHTS / f"{game}.jsonl.gz"
    with gzip.open(path, "rt") as f:
        lines = [json.loads(l) for l in f]
    return lines[0], [r for r in lines[1:] if r["c"]]


def build_games(seed=0, val=0.15, test=0.15):
    rows = []
    for line in open(INDEX):
        m = json.loads(line)
        a, b = m["teams"]["a"], m["teams"]["b"]
        if not (FIGHTS / f"{m['matchId']}.jsonl.gz").exists() or a["engine"] != "1.0.3":
            continue
        rows.append({
            "game": m["matchId"], "map": m["map"],
            "team_a": a["name"], "team_b": b["name"], "rank_a": a["rank"], "rank_b": b["rank"],
            "winner": 0 if a["result"] == "win" else 1 if b["result"] == "win" else -1,
        })
    games = pd.DataFrame(rows).sort_values("game").reset_index(drop=True)
    ids = list(games["game"])
    random.Random(seed).shuffle(ids)
    n_val, n_test = int(len(ids) * val), int(len(ids) * test)
    split = {g: "test" for g in ids[:n_test]} | {g: "val" for g in ids[n_test:n_test + n_val]}
    games["split"] = games["game"].map(lambda g: split.get(g, "train"))
    return games


def load_games():
    return pd.read_parquet(OUT / "games.parquet")


def cooldowns(rounds):
    n = len(rounds[0]["c"])
    last = [[None, None] for _ in range(n)]
    kills = [0] * n
    out = []
    for rnd in rounds:
        r = rnd["r"]
        cds = []
        for i, c in enumerate(rnd["c"]):
            if c["ty"] == VENDETTA and c["k"] > kills[i]:
                last[i] = [None, None]
            kills[i] = c["k"]
            cds.append([0 if t is None else max(0, COOLDOWN - (r - t)) for t in last[i]])
        out.append(cds)
        for i, acts in enumerate(rnd["act"]):
            for a in acts:
                if a[0] == "cast" and a[1] in (0, 1):
                    last[i][a[1]] = r
    return out


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    games = build_games()
    games.to_parquet(OUT / "games.parquet")
    print(games["split"].value_counts().to_string())
    print(games["winner"].value_counts().to_string())
