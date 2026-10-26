import json
from multiprocessing import Pool

import numpy as np
import pandas as pd

import reinforce_data as rd
from common import INDEX, OUT, load_game, load_games
from simfight import alive, dist

TEAM = "Velvet Tributers"
WINDOW = 30
NEAR = 4


def side_groups():
    rating = {t["teamId"]: t["rating"] for t in json.load(open(OUT / "ladder.json"))}
    ours = next(t["rating"] for t in json.load(open(OUT / "ladder.json")) if t["name"] == TEAM)
    sides = {}
    for line in open(INDEX):
        m = json.loads(line)
        for t, s in ((0, "a"), (1, "b")):
            team = m["teams"][s]
            r = rating.get(team["teamId"])
            if team["name"] == TEAM:
                g = "ours"
            elif r is None:
                g = "unrated"
            elif r > ours + 75:
                g = "higher"
            elif r < ours - 75:
                g = "lower"
            else:
                g = "similar"
            sides[(m["matchId"], t)] = g
    return sides


def move_away(rounds, i, ch):
    me, nxt = rounds[i]["c"][ch], rounds[i + 1]["c"][ch]
    vis = [j for j in rounds[i]["vis"][ch] if alive(rounds[i]["c"][j])]
    if not vis or not alive(nxt):
        return None, None
    j = min(vis, key=lambda j: dist(me, rounds[i]["c"][j]))
    d0 = dist(me, rounds[i]["c"][j])
    return dist(nxt, rounds[i]["c"][j]) > d0, d0


def analyse(args):
    game, map_name, groups = args
    _, rounds = load_game(game)
    spawn = rd.spawn_tiles(rounds)
    alt = rd.altars(map_name)
    deaths, flees = [], []
    n = len(rounds)
    for d in range(1, n):
        for ch, (p, c) in enumerate(zip(rounds[d - 1]["c"], rounds[d]["c"])):
            if not p["a"] or c["a"]:
                continue
            t = p["t"]
            last = d - 1
            me = rounds[last]["c"][ch]
            if "x" not in me:
                continue
            killers = [j for j, e in enumerate(rounds[last]["c"]) if e["t"] != t and alive(e) and dist(me, e) <= NEAR]
            first_seen, ally_saw_first = [], []
            for j in killers:
                seen_me = next((k for k in range(max(0, last - WINDOW), last + 1) if j in rounds[k]["vis"][ch]), None)
                seen_ally = next((k for k in range(max(0, last - WINDOW), last + 1)
                                  if any(j in rounds[k]["vis"][a] for a, ca in enumerate(rounds[k]["c"]) if ca["t"] == t and a != ch)), None)
                first_seen.append(last - seen_me if seen_me is not None else None)
                ally_saw_first.append(seen_ally is not None and (seen_me is None or seen_ally < seen_me))
            hp = lambda k: rounds[k]["c"][ch]["hp"] / rounds[k]["c"][ch]["mhp"] if k >= 0 and alive(rounds[k]["c"][ch]) else np.nan
            run, turn_hp = 0, np.nan
            for k in range(last - 1, max(0, last - 20), -1):
                away, _ = move_away(rounds, k, ch)
                if away is None or not away:
                    break
                run += 1
                turn_hp = hp(k)
            bleed = 0
            for k in range(last, max(0, last - 40), -1):
                if hp(k) >= 0.9:
                    break
                bleed += 1
            ctx = rounds[max(0, last - 10)]["c"][ch]
            deaths.append(dict(
                game=game, group=groups[(game, t)], map=map_name, round=rounds[d]["r"], gems=me["g"], hp_m10=hp(last - 10), hp_m5=hp(last - 5),
                bleed=bleed, flee_run=run, turn_hp=turn_hp, n_killers=len(killers),
                killer_seen_ago=np.nanmean([x if x is not None else np.nan for x in first_seen]) if killers else np.nan,
                killer_unseen=np.mean([x is None for x in first_seen]) if killers else np.nan,
                killer_seen_late=np.mean([x is not None and x <= 7 for x in first_seen]) if killers else np.nan,
                ally_saw_first=np.mean(ally_saw_first) if killers else np.nan,
                d_own=rd.nearest(ctx, spawn[t]) if "x" in ctx else np.nan, d_enemy=rd.nearest(ctx, spawn[1 - t]) if "x" in ctx else np.nan,
                d_altar=rd.nearest(ctx, alt) if "x" in ctx else np.nan,
            ))
    for i in range(1, n - 12, 2):
        for ch, me in enumerate(rounds[i]["c"]):
            if not alive(me):
                continue
            away, d0 = move_away(rounds, i, ch)
            prev, _ = move_away(rounds, i - 1, ch) if alive(rounds[i - 1]["c"][ch]) else (None, None)
            if not away or prev or d0 is None or d0 > NEAR:
                continue
            vis = [j for j in rounds[i]["vis"][ch] if alive(rounds[i]["c"][j])]
            died = any(not rounds[k]["c"][ch]["a"] for k in range(i + 1, i + 11))
            flees.append(dict(group=groups[(game, me["t"])], hp=me["hp"] / me["mhp"], gems=me["g"],
                              near_e=sum(dist(me, rounds[i]["c"][j]) <= 6 for j in vis),
                              near_a=sum(dist(me, rounds[i]["c"][j]) <= 5 for j in rounds[i]["avis"][ch] if alive(rounds[i]["c"][j])),
                              died=died))
    return deaths, flees


def main():
    groups = side_groups()
    games = load_games()
    jobs = [(g, m, groups) for g, m in zip(games["game"], games["map"])]
    with Pool(6) as pool:
        res = pool.map(analyse, jobs, chunksize=4)
    D = pd.DataFrame([x for d, _ in res for x in d])
    F = pd.DataFrame([x for _, f in res for x in f])
    D.to_parquet(OUT / "deaths_all.parquet")
    F.to_parquet(OUT / "flees_all.parquet")
    side_games = pd.Series(groups).reset_index().rename(columns={0: "group"}).groupby("group").size()
    order = ["ours", "higher", "similar", "lower", "unrated"]
    pd.set_option("display.width", 200)

    print("A/B/D. Deaths by team group (means per death)")
    t = D.groupby("group").agg(deaths=("round", "size"), hp_m10=("hp_m10", "mean"), bleed=("bleed", "median"), flee_run=("flee_run", "mean"),
                               turn_hp=("turn_hp", "median"), killers=("n_killers", "mean"), killer_unseen=("killer_unseen", "mean"),
                               killer_seen_late=("killer_seen_late", "mean"), ally_saw_first=("ally_saw_first", "mean"),
                               gems=("gems", "median"), d_own=("d_own", "median"), d_enemy=("d_enemy", "median"), round=("round", "median"))
    t["per_game"] = t["deaths"] / side_games.reindex(t.index)
    print(t.reindex(order).round(2).to_string())

    print("\nC. Flee starts within 4 tiles of an enemy: P(dead within 10 rounds) by hp at the turn")
    F["hp_bin"] = pd.cut(F["hp"], [0, 0.3, 0.5, 0.7, 0.9, 1.01])
    c = F.groupby(["group", "hp_bin"], observed=True)["died"].agg(["mean", "size"]).unstack("hp_bin")
    print(c["mean"].reindex(order).round(3).to_string())
    print("counts:")
    print(c["size"].reindex(order).to_string())
    print("\nC2. Flee starts: average situation")
    print(F.groupby("group")[["hp", "near_e", "near_a", "gems"]].mean().reindex(order).round(2).to_string())

    ours = D[D["group"] == "ours"]
    print("\nD. Our deaths by map (top 8):", ours["map"].value_counts().head(8).to_dict())
    print("D. Our deaths by game phase:", pd.cut(ours["round"], [0, 300, 600, 1000, 1500, 2000]).value_counts().sort_index().to_dict())


if __name__ == "__main__":
    main()
