import math
import re
from multiprocessing import Pool

import numpy as np

import reinforce_data as rd
from actions import hits
from common import OUT, cooldowns, load_game, load_games
from features import unit
from simfight import alive

QUIET = 15
WINDOW = 60
AT_GROUP = 3
CAMP_TYPES = ["wolf", "elk", "gem_cluster", "gold_cluster", "golem", "monolith"]
CAMP_HP = {"wolf": 1350, "elk": 2400, "gem_cluster": 120, "gold_cluster": 120, "golem": 5000, "monolith": 20000}
GROUP_FEATURES = [f"n_{t}" for t in CAMP_TYPES] + ["camp_hp", "gems", "gold", "allies_near_group", "enemies_near_group",
                                                     "dist_own_spawn", "dist_enemy_spawn", "dist_altar", "round", "score_diff", "my_gems_log", "dist_group"]


def map_groups(map_name):
    groups = []
    for line in open(rd.MAP_DUMPS / f"{map_name.replace('_', '-')}.txt"):
        if line.startswith("GROUP "):
            camps = [(t, int(x), int(y)) for t, x, y in re.findall(r"(\w+)@(\d+),(\d+)", line)]
            groups.append(dict(gems=int(re.search(r"gems=(\d+)", line)[1]), gold=int(re.search(r"gold=(\d+)", line)[1]), camps=camps,
                               tiles=[dict(x=x, y=y) for _, x, y in camps]))
    return groups


def outcome(rounds, i, ch, g):
    team = rounds[i]["c"][ch]["t"]
    for k in range(i, min(i + WINDOW, len(rounds) - 1)):
        for a, (p, q) in enumerate(zip(rounds[k]["c"], rounds[k + 1]["c"])):
            if p["t"] != team or not p["a"] or not alive(q) or rd.nearest(q, g["tiles"]) > AT_GROUP:
                continue
            if (q["g"] > p["g"] or q["au"] > p["au"]) and q["k"] == p["k"] and not any(x[0] == "tribute" for x in rounds[k]["act"][a]):
                return 1, k + 1 - i
    return 0, WINDOW


DECIDE = 8
LOOKBACK = 30


def features_at(rounds, j, ch, g, memory, cds, spawn, alt):
    rnd = rounds[j]
    c, me = rnd["c"], rnd["c"][ch]
    vis = [k for k in rnd["vis"][ch] if alive(c[k])]
    allies = [k for k in rnd["avis"][ch] if alive(c[k])]
    mem = sorted([(k, m) for k, m in memory.items() if k not in vis and rnd["r"] - m["r"] <= rd.MEMORY], key=lambda km: -km[1]["r"])
    types = [t for t, _, _ in g["camps"]]
    return dict(
        self_x=unit(me, me, cds[j][ch]), self_t=me["ty"],
        ally_x=[unit(me, c[k], cds[j][k]) for k in allies[:rd.MAX_ALLIES]], ally_t=[c[k]["ty"] for k in allies[:rd.MAX_ALLIES]],
        enemy_x=[unit(me, c[k], cds[j][k]) for k in vis[:rd.MAX_ENEMIES]], enemy_t=[c[k]["ty"] for k in vis[:rd.MAX_ENEMIES]],
        mem_x=[[m["x"] - me["x"], m["y"] - me["y"], max(abs(m["x"] - me["x"]), abs(m["y"] - me["y"])), rnd["r"] - m["r"], m["hp_frac"], math.log1p(m["g"])]
               for _, m in mem[:rd.MAX_MEMORY]],
        mem_t=[c[k]["ty"] for k, _ in mem[:rd.MAX_MEMORY]],
        game_x=[*(types.count(t) for t in CAMP_TYPES), sum(CAMP_HP[t] for t in types), g["gems"], g["gold"],
                sum(rd.nearest(c[k], g["tiles"]) <= 5 for k in allies), sum(rd.nearest(c[k], g["tiles"]) <= 5 for k in vis),
                rd.nearest(me, spawn[me["t"]]), rd.nearest(me, spawn[1 - me["t"]]), rd.nearest(me, alt),
                rnd["r"], rnd["sg"][me["t"]] - rnd["sg"][1 - me["t"]], math.log1p(me["g"]), rd.nearest(me, g["tiles"])],
    )


def decision_round(rounds, i, ch, g):
    j = i
    for k in range(i, max(0, i - LOOKBACK) - 1, -1):
        me = rounds[k]["c"][ch]
        if not alive(me):
            break
        j = k
        if rd.nearest(me, g["tiles"]) >= DECIDE:
            break
    return j


def game_rows(args):
    game, map_name = args
    _, rounds = load_game(game)
    groups = map_groups(map_name)
    tile_group = {(x, y): gi for gi, g in enumerate(groups) for _, x, y in g["camps"]}
    spawn, alt = rd.spawn_tiles(rounds), rd.altars(map_name)
    cds = cooldowns(rounds)
    n = len(rounds[0]["c"])
    memory_at = []
    last_seen = [dict() for _ in range(n)]
    for rnd in rounds:
        memory_at.append([dict(m) for m in last_seen])
        for ch, me in enumerate(rnd["c"]):
            if not alive(me):
                last_seen[ch].clear()
                continue
            for k in rnd["vis"][ch]:
                if alive(rnd["c"][k]):
                    ck = rnd["c"][k]
                    last_seen[ch][k] = dict(r=rnd["r"], x=ck["x"], y=ck["y"], hp_frac=ck["hp"] / ck["mhp"], g=ck["g"])
    last_hit, rows = {}, []
    for i, rnd in enumerate(rounds[:-1]):
        for ch, me in enumerate(rnd["c"]):
            if not alive(me):
                continue
            for act in rnd["act"][ch]:
                h = hits(act)
                if not h or h[0] != "m":
                    continue
                x, y = (act[1], act[2]) if act[0] == "attack" else (act[2], act[3])
                gi = tile_group.get((x, y))
                if gi is None:
                    continue
                prev = last_hit.get((ch, gi))
                last_hit[(ch, gi)] = i
                if prev is not None and i - prev <= QUIET:
                    continue
                g = groups[gi]
                success, taken = outcome(rounds, i, ch, g)
                j = decision_round(rounds, i, ch, g)
                rows.append(dict(game=game, idx=j, champ=ch, group=gi, success=success, rounds=taken + (i - j), clear=max(taken, 1),
                                 **features_at(rounds, j, ch, g, memory_at[j][ch], cds, spawn, alt)))
    return rows


def main():
    games = load_games()
    games = games[~games["map"].str.contains("boss_battle")]
    split = dict(zip(games["game"], games["split"]))
    with Pool(6) as pool:
        rows = [r for rs in pool.map(game_rows, list(zip(games["game"], games["map"])), chunksize=4) for r in rs]
    arrays = dict(
        self_x=np.array([r["self_x"] for r in rows], np.float32), self_t=np.array([r["self_t"] for r in rows], np.int64),
        game_x=np.array([r["game_x"] for r in rows], np.float32),
        success=np.array([r["success"] for r in rows], np.float32), rounds=np.array([r["rounds"] for r in rows], np.float32),
        clear=np.array([r["clear"] for r in rows], np.float32),
        group=np.array([r["group"] for r in rows]), idx=np.array([r["idx"] for r in rows]), champ=np.array([r["champ"] for r in rows]),
        game=np.array([r["game"] for r in rows]), split=np.array([split[r["game"]] for r in rows]),
    )
    for name, width, n_feat in [("ally", rd.MAX_ALLIES, 11), ("enemy", rd.MAX_ENEMIES, 11), ("mem", rd.MAX_MEMORY, len(rd.MEMORY_FEATURES))]:
        arrays[f"{name}_x"], arrays[f"{name}_m"] = rd.pad(rows, f"{name}_x", width, n_feat)
        arrays[f"{name}_t"], _ = rd.pad(rows, f"{name}_t", width, 0, np.int64)
    np.savez(OUT / "fpr_dataset.npz", **arrays)
    s = arrays["success"]
    print(f"{len(s)} capture attempts from {len(games)} games; success {s.mean():.1%}; "
          f"rounds to capture (successes) median {np.median(arrays['rounds'][s == 1]):.0f}, p90 {np.percentile(arrays['rounds'][s == 1], 90):.0f}")


if __name__ == "__main__":
    main()
