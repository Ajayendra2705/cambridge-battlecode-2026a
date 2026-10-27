import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import fpr_data as fd
import reinforce_data as rd
from actions import hits
from common import OUT, load_game
from simfight import alive

try:
    import eg_labels
except ImportError:
    eg_labels = None

W2 = Path("/home/ming/work/pytorch/cb-2_0_0")
SOURCES = [(W2 / "data/fights/headroom", W2 / "data/replays/platform/headroom/index.txt"),
           (W2 / "data/fights/eg", W2 / "data/replays/platform/eg/index.jsonl")]
EVERY = 5
VISION = 8
NEAR_US = 4
NEAR_THEM = 5
TOP_GROUPS = 2
GROUP_FEATURES = ["dist", "gems", "gold", "hp_log", "cleared"]
FEATURES = ["hp_frac", "bag_log", "dist_altar", "dist_me", "us_near", "them_near", "round", "capturing", "score_diff",
            "our_bag_near_log", "dist_our_nearest"] + [
    f"g{k}_{f}" for k in range(TOP_GROUPS) for f in GROUP_FEATURES]


def cheb(a, b):
    return max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))


def camp_tiles(rounds):
    pos = {}
    for rnd in rounds:
        for acts in rnd["act"]:
            for a in acts:
                h = hits(a)
                if h and h[0] == "m":
                    pos[h[1]] = (a[1], a[2]) if a[0] == "attack" else (a[2], a[3])
    return pos


def group_state(rnd, g, idx_of):
    hp, alive_camps = 0.0, 0
    for t, x, y in g["camps"]:
        i = idx_of.get((x, y))
        h = rnd["mh"][i] if i is not None and i < len(rnd["mh"]) else fd.CAMP_HP[t]
        hp += h
        alive_camps += h > 0
    return hp, alive_camps == 0


def game_rows(args):
    path, map_name = args
    _, rounds = load_game(path)
    groups = fd.map_groups(map_name)
    if not groups:
        return []
    idx_of = {v: k for k, v in camp_tiles(rounds).items()}
    alt = rd.altars(map_name)
    n = len(rounds[0]["c"])
    seen = [dict() for _ in range(n)]
    rows = []
    for i, rnd in enumerate(rounds[:-1]):
        c = rnd["c"]
        for o, me in enumerate(c):
            if not alive(me):
                continue
            for gi, g in enumerate(groups):
                if min(max(abs(x - me["x"]), abs(y - me["y"])) for _, x, y in g["camps"]) <= VISION:
                    seen[o][gi] = group_state(rnd, g, idx_of)
        if rnd["r"] % EVERY:
            continue
        for o, me in enumerate(c):
            if not alive(me):
                continue
            us = [me] + [c[k] for k in rnd["avis"][o] if alive(c[k])]
            them = [c[k] for k in rnd["vis"][o] if alive(c[k])]
            for e in rnd["vis"][o]:
                en = c[e]
                if not alive(en):
                    continue
                near = sorted(range(len(groups)), key=lambda gi: rd.nearest(en, groups[gi]["tiles"]))[:TOP_GROUPS]
                gx, capturing = [], 0
                for gi in near:
                    g = groups[gi]
                    hp, cleared = seen[o].get(gi, (sum(fd.CAMP_HP[t] for t, _, _ in g["camps"]), False))
                    d = rd.nearest(en, g["tiles"])
                    capturing |= cleared and d <= 1
                    gx += [d, g["gems"], g["gold"], math.log1p(hp), float(cleared)]
                label = eg_labels.enemy_gain(rounds, i, e, eg_labels.HORIZON) if eg_labels else (np.nan, np.nan)
                rows.append(dict(game=str(path.name), idx=i, observer=o, enemy=e, e_type=en["ty"], label=label, x=[
                    en["hp"] / en["mhp"], math.log1p(en["g"]), rd.nearest(en, alt), cheb(me, en),
                    sum(cheb(u, en) <= NEAR_US for u in us), sum(cheb(t, en) <= NEAR_THEM for t in them if t is not en),
                    rnd["r"], float(capturing), rnd["sg"][en["t"]] - rnd["sg"][me["t"]],
                    math.log1p(max((u["g"] for u in us if cheb(u, en) <= NEAR_US), default=0)), min(cheb(u, en) for u in us), *gx]))
    return rows


def sources():
    out = []
    for fights, index in SOURCES:
        if not index.exists():
            continue
        for line in open(index):
            line = line.strip()
            if not line:
                continue
            if line.startswith("{"):
                m = json.loads(line)
                mid, mp = m["matchId"], m["map"]
            else:
                mid, _, mp, *_ = line.split()
            p = fights / f"{mid}.jsonl.gz"
            if p.exists():
                out.append((p, mp))
    return list({p.name: (p, mp) for p, mp in out}.values())


def main():
    games = sources()
    if len(sys.argv) > 1:
        games = games[:int(sys.argv[1])]
    rng = np.random.default_rng(0)
    split = {p.name: s for (p, _), s in zip(games, rng.choice(["train", "val", "test"], len(games), p=[0.7, 0.15, 0.15]))}
    with Pool(6) as pool:
        rows = [r for rs in pool.map(game_rows, games, chunksize=2) for r in rs]
    arrays = dict(x=np.array([r["x"] for r in rows], np.float32), e_type=np.array([r["e_type"] for r in rows], np.int64),
                  label=np.array([r["label"] for r in rows], np.float32), game=np.array([r["game"] for r in rows]),
                  idx=np.array([r["idx"] for r in rows]), observer=np.array([r["observer"] for r in rows]),
                  enemy=np.array([r["enemy"] for r in rows]), split=np.array([split[r["game"]] for r in rows]))
    np.savez(OUT / "eg_dataset.npz", **arrays, features=np.array(FEATURES))
    lab = arrays["label"]
    print(f"{len(rows)} rows from {len(games)} games; label {'missing (write eg_labels.py)' if np.isnan(lab).all() else f'mean gems {lab[:, 0].mean():.2f}, gold {lab[:, 1].mean():.1f}'}")


if __name__ == "__main__":
    main()
