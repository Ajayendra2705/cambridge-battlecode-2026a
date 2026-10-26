import math
from multiprocessing import Pool

import numpy as np

from common import OUT, ROOT, cooldowns, load_game, load_games
from features import unit
from simfight import alive, dist

W = 7
MEMORY = 10
NEAR = 6
EVERY = 4
DEATH_AFTER = 9
MAX_ALLIES, MAX_ENEMIES, MAX_MEMORY = 5, 6, 6
MEMORY_FEATURES = ["dx", "dy", "dist", "rounds_since", "hp_frac", "log_gems"]
RF_GAME_FEATURES = ["round", "score_diff", "my_gems_log", "visible_ally_gems_log", "visible_enemy_gems_log", "dist_own_spawn", "dist_enemy_spawn", "dist_altar"]
MAP_DUMPS = ROOT / "docs/reference/probe/maps"


def arrivals(rounds, idx, champ, allies=False):
    seen = set(rounds[idx]["avis" if allies else "vis"][champ])
    pos = rounds[idx]["c"][champ]
    came = set()
    for rnd in rounds[idx + 1:idx + 1 + W]:
        c = rnd["c"]
        if alive(c[champ]):
            pos = c[champ]
        for e, ce in enumerate(c):
            if e != champ and (ce["t"] == pos["t"]) == allies and e not in seen and alive(ce) and dist(pos, ce) <= NEAR:
                came.add(e)
    return len(came)


def died_after(rounds, idx, champ):
    return any(not rounds[k]["c"][champ]["a"] for k in range(idx + W + 1, min(idx + W + 1 + DEATH_AFTER, len(rounds))))


def altars(map_name):
    out = []
    for line in open(MAP_DUMPS / f"{map_name.replace('_', '-')}.txt"):
        if line.startswith("ALTAR "):
            x, y = line.split()[1].split(",")
            out.append(dict(x=int(x), y=int(y)))
    return out


def nearest(me, points):
    return min((dist(me, q) for q in points), default=99)


def spawn_tiles(rounds):
    tiles = [set(), set()]
    for c in rounds[0]["c"]:
        if "x" in c:
            tiles[c["t"]].add((c["x"], c["y"]))
    for prev, cur in zip(rounds, rounds[1:]):
        for p, c in zip(prev["c"], cur["c"]):
            if not p["a"] and alive(c):
                tiles[c["t"]].add((c["x"], c["y"]))
    return [[dict(x=x, y=y) for x, y in sorted(t)] for t in tiles]


def game_arrays(args):
    game, map_name = args
    _, rounds = load_game(game)
    alt = altars(map_name)
    spawn = spawn_tiles(rounds)
    cds = cooldowns(rounds)
    n_champs = len(rounds[0]["c"])
    last = [dict() for _ in range(n_champs)]
    rows = []
    for idx, rnd in enumerate(rounds[:len(rounds) - W - 1]):
        c = rnd["c"]
        for champ in range(n_champs):
            me = c[champ]
            if not alive(me):
                last[champ].clear()
                continue
            visible = [j for j in rnd["vis"][champ] if alive(c[j])]
            memory = [(j, m) for j, m in last[champ].items() if j not in visible and rnd["r"] - m["r"] <= MEMORY]
            if idx % EVERY == 0 and (visible or memory):
                allies = [j for j in rnd["avis"][champ] if alive(c[j])][:MAX_ALLIES]
                enemies = visible[:MAX_ENEMIES]
                mem = sorted(memory, key=lambda jm: -jm[1]["r"])[:MAX_MEMORY]
                rows.append(dict(
                    self_x=unit(me, me, cds[idx][champ]), self_t=me["ty"],
                    ally_x=[unit(me, c[j], cds[idx][j]) for j in allies], ally_t=[c[j]["ty"] for j in allies],
                    enemy_x=[unit(me, c[j], cds[idx][j]) for j in enemies], enemy_t=[c[j]["ty"] for j in enemies],
                    mem_x=[[m["x"] - me["x"], m["y"] - me["y"], max(abs(m["x"] - me["x"]), abs(m["y"] - me["y"])), rnd["r"] - m["r"], m["hp_frac"], math.log1p(m["g"])] for _, m in mem],
                    mem_t=[c[j]["ty"] for j, _ in mem],
                    game_x=[rnd["r"], rnd["sg"][me["t"]] - rnd["sg"][1 - me["t"]], math.log1p(me["g"]),
                            math.log1p(sum(c[j]["g"] for j in allies)), math.log1p(sum(c[j]["g"] for j in enemies)),
                            nearest(me, spawn[me["t"]]), nearest(me, spawn[1 - me["t"]]), nearest(me, alt)],
                    label=arrivals(rounds, idx, champ), ally_label=arrivals(rounds, idx, champ, allies=True), team=me["t"], died=died_after(rounds, idx, champ), idx=idx, champ=champ,
                ))
            for j in visible:
                last[champ][j] = dict(r=rnd["r"], x=c[j]["x"], y=c[j]["y"], hp_frac=c[j]["hp"] / c[j]["mhp"], g=c[j]["g"])
    return game, rows


def pad(rows, key, width, n_feat, dtype=np.float32):
    out = np.zeros((len(rows), width, n_feat) if n_feat else (len(rows), width), dtype)
    mask = np.zeros((len(rows), width), bool)
    for i, r in enumerate(rows):
        v = r[key]
        if len(v):
            out[i, :len(v)] = v
            mask[i, :len(v)] = True
    return out, mask


def main():
    games = load_games()
    games = games[~games["map"].str.contains("boss_battle")]
    split = dict(zip(games["game"], games["split"]))
    with Pool(6) as pool:
        results = pool.map(game_arrays, list(zip(games["game"], games["map"])), chunksize=4)
    rows, gids = [], []
    for g, rs in results:
        rows += rs
        gids += [g] * len(rs)
    arrays = dict(
        self_x=np.array([r["self_x"] for r in rows], np.float32), self_t=np.array([r["self_t"] for r in rows], np.int64),
        game_x=np.array([r["game_x"] for r in rows], np.float32),
        label=np.array([r["label"] for r in rows], np.float32), ally_label=np.array([r["ally_label"] for r in rows], np.float32),
        team=np.array([r["team"] for r in rows]), died=np.array([r["died"] for r in rows]),
        idx=np.array([r["idx"] for r in rows]), champ=np.array([r["champ"] for r in rows]),
        game=np.array(gids), split=np.array([split[g] for g in gids]),
    )
    for name, width, n_feat in [("ally", MAX_ALLIES, 11), ("enemy", MAX_ENEMIES, 11), ("mem", MAX_MEMORY, len(MEMORY_FEATURES))]:
        arrays[f"{name}_x"], arrays[f"{name}_m"] = pad(rows, f"{name}_x", width, n_feat)
        arrays[f"{name}_t"], _ = pad(rows, f"{name}_t", width, 0, np.int64)
    np.savez(OUT / "rf_dataset.npz", **arrays)
    y = arrays["label"]
    print(f"{len(y)} samples from {len(results)} games; arrivals mean {y.mean():.3f}, P(>0) {(y > 0).mean():.1%}")
    print(f"remembered enemies per sample {arrays['mem_m'].sum(1).mean():.2f}, visible {arrays['enemy_m'].sum(1).mean():.2f}")


if __name__ == "__main__":
    main()
