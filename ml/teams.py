import json

import numpy as np
import pandas as pd

from common import INDEX, OUT


def main():
    ladder = {t["teamId"]: t["rating"] for t in json.load(open(OUT / "ladder.json"))}
    sides = {}
    for line in open(INDEX):
        m = json.loads(line)
        sides[m["matchId"]] = (m["teams"]["a"]["teamId"], m["teams"]["b"]["teamId"])
    events = pd.read_parquet(OUT / "events.parquet")
    dec = events.drop_duplicates(["game", "idx", "champ"]).sort_values(["game", "idx", "champ"])
    d = np.load(OUT / "dataset.npz")
    assert (dec["game"].to_numpy() == d["game"]).all() and (dec["idx"].to_numpy() == d["idx"]).all() and (dec["champ"].to_numpy() == d["champ"]).all()

    own = np.array([sides[g][t] for g, t in zip(dec["game"], dec["team"])])
    opp = np.array([sides[g][1 - t] for g, t in zip(dec["game"], dec["team"])])
    median = float(np.median(list(ladder.values())))
    rating = lambda ids: np.array([ladder.get(i, median) for i in ids], np.float32)
    train = d["split"] == "train"
    counts = pd.Series(own[train]).value_counts()
    known = counts[counts >= 2000].index
    team_index = {t: i + 1 for i, t in enumerate(sorted(known))}
    np.savez(
        OUT / "teams.npz",
        own_rating=rating(own), opp_rating=rating(opp),
        team_id=np.array([team_index.get(t, 0) for t in own], np.int64),
        n_teams=len(team_index) + 1,
        team_keys=np.array(sorted(known)),
    )
    missing = np.mean([i not in ladder for i in own])
    print(f"{len(team_index)} teams with >= 2000 train decisions get their own id (others share id 0)")
    print(f"decisions whose team has no current ladder rating: {missing:.1%}")
    print(f"own rating: mean {rating(own).mean():.0f}, std {rating(own).std():.0f}")


if __name__ == "__main__":
    main()
