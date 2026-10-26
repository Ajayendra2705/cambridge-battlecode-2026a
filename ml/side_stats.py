from multiprocessing import Pool

import numpy as np
import pandas as pd

import reinforce_data as rd
from actions import hits
from common import OUT, load_game, load_games
from death_analysis import side_groups
from simfight import CHAMPS, alive, dist

PHASES = [(0, 300), (300, 600), (600, 1000), (1000, 2001)]


def phase_of(r):
    return next(i for i, (a, b) in enumerate(PHASES) if a <= r < b)


def side_stats(args):
    game, map_name, groups = args
    _, rounds = load_game(game)
    spawn = rd.spawn_tiles(rounds)
    out = []
    for t in (0, 1):
        s = dict(game=game, team=t, group=groups[(game, t)], map=map_name, rounds=rounds[-1]["r"])
        for p in range(len(PHASES)):
            s[f"contact_p{p}"] = s[f"alive_p{p}"] = s[f"enemy_half_p{p}"] = s[f"allies_near_p{p}"] = 0
        champ_hits = camp_hits = wards = tributes = 0
        seen_bags, big_bag_seen = [], 0
        dmg_dealt = 0.0
        for i, rnd in enumerate(rounds[:-1]):
            c, nxt = rnd["c"], rounds[i + 1]["c"]
            ph = phase_of(rnd["r"])
            for ch, me in enumerate(c):
                if me["t"] != t or not alive(me):
                    continue
                s[f"alive_p{ph}"] += 1
                if rd.nearest(me, spawn[1 - t]) < rd.nearest(me, spawn[t]):
                    s[f"enemy_half_p{ph}"] += 1
                s[f"allies_near_p{ph}"] += sum(dist(me, c[a]) <= 5 for a in rnd["avis"][ch] if alive(c[a]))
                vis = [j for j in rnd["vis"][ch] if alive(c[j])]
                if any(dist(me, c[j]) <= max(CHAMPS[me["ty"]]["range"], 4) for j in vis):
                    s[f"contact_p{ph}"] += 1
                for j in vis:
                    seen_bags.append(c[j]["g"])
                    big_bag_seen += c[j]["g"] >= 30
                for act in rnd["act"][ch]:
                    h = hits(act)
                    if act[0] == "ward":
                        wards += 1
                    elif act[0] == "tribute":
                        tributes += 1
                    elif h and h[0] == "c" and c[h[1]]["t"] != t:
                        champ_hits += 1
                    elif h and h[0] == "m":
                        camp_hits += 1
            for e, ce in enumerate(c):
                if ce["t"] != t and alive(ce) and "hp" in nxt[e] and nxt[e]["a"]:
                    if any(alive(c[a]) and c[a]["t"] == t and dist(c[a], ce) <= 4 for a in range(len(c))):
                        dmg_dealt += max(0.0, ce["hp"] - nxt[e]["hp"])
        sg = [r["sg"][t] for r in rounds]
        deposits = [b - a for a, b in zip(sg, sg[1:]) if b > a]
        contact = sum(s[f"contact_p{p}"] for p in range(len(PHASES)))
        s.update(champ_hits=champ_hits, camp_hits=camp_hits, wards=wards, tribute_acts=tributes,
                 deposits=len(deposits), gems_per_deposit=np.mean(deposits) if deposits else np.nan,
                 enemy_bag_seen_mean=np.mean(seen_bags) if seen_bags else np.nan, big_bags_seen=big_bag_seen,
                 dmg_near_enemies=dmg_dealt, hits_per_contact=champ_hits / contact if contact else np.nan,
                 dmg_per_contact=dmg_dealt / contact if contact else np.nan, contact=contact,
                 tributed=rounds[-1]["sg"][t], opp_tributed=rounds[-1]["sg"][1 - t],
                 kills=sum(x["k"] for x in rounds[-1]["c"] if x["t"] == t),
                 win=rounds[-1]["sg"][t] > rounds[-1]["sg"][1 - t])
        out.append(s)
    return out


def main():
    groups = side_groups()
    games = load_games()
    with Pool(6) as pool:
        rows = [r for rs in pool.map(side_stats, [(g, m, groups) for g, m in zip(games["game"], games["map"])], chunksize=4) for r in rs]
    df = pd.DataFrame(rows)
    df.to_parquet(OUT / "side_stats.parquet")
    print(f"{len(df)} team-sides")


if __name__ == "__main__":
    main()
