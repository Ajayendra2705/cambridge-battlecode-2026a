import subprocess
import sys
import zipfile
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

from common import load_game
from simfight import alive

HORIZON = 10
COLS = ["d0", "d1", "h0", "h1", "power_ratio", "ally_count", "enemy_count", "my_hp", "prey_hp", "my_bag", "prey_bag"]
W2 = Path("/home/ming/work/pytorch/cb-2_0_0")


def logged(replay, side):
    text = zipfile.ZipFile(replay).read(f"team-{side.lower()}.stdout").decode("latin1").replace("\x00", "")
    rows = []
    for chunk in text.split("SL ")[1:]:
        v = chunk.split()[:20]
        if len(v) < 19:
            continue
        rows.append(dict(r=int(v[0]), me=(int(v[1]), int(v[2])), prey=(int(v[3]), int(v[4])), x=[float(a) for a in v[5:16]], engaged=int(v[16])))
    return rows


def at(rnd, team, pos):
    for i, c in enumerate(rnd["c"]):
        if c["t"] == team and alive(c) and max(abs(c["x"] - pos[0]), abs(c["y"] - pos[1])) <= 1:
            return i
    return None


def game(args):
    replay, decoded = args
    side = replay.stem.split("~")[3]
    team = 0 if side == "A" else 1
    _, rounds = load_game(decoded)
    by_r = {r["r"]: k for k, r in enumerate(rounds)}
    out = []
    for row in logged(replay, side):
        k = by_r.get(row["r"])
        if k is None:
            continue
        me, prey = at(rounds[k], team, row["me"]), at(rounds[k], 1 - team, row["prey"])
        if me is None or prey is None:
            continue
        future = rounds[k + 1:k + 1 + HORIZON]
        prey_dies = any(not alive(r["c"][prey]) for r in future)
        me_dies = any(not alive(r["c"][me]) for r in future)
        out.append(dict(x=row["x"], engaged=row["engaged"], win=prey_dies and not me_dies, prey_dies=prey_dies, game=replay.name))
    return out


def main():
    run = Path(sys.argv[1])
    out = W2 / "data/fights" / f"local_{run.name}"
    replays = sorted(run.glob("*.repl26a"))
    if len(list(out.glob("*.jsonl.gz"))) < len(replays):
        out.mkdir(parents=True, exist_ok=True)
        procs = [subprocess.Popen(["node", str(W2 / "tools/replay/rounds_extract.mjs"), str(out), *map(str, replays[i::6])],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(6)]
        for p in procs:
            p.wait()
    pairs = [(r, out / f"{r.stem}.jsonl.gz") for r in replays if (out / f"{r.stem}.jsonl.gz").exists()]
    with Pool(6) as pool:
        rows = [x for rs in pool.map(game, pairs) for x in rs]
    rows = [r for r in rows if r["engaged"]]
    x = np.array([r["x"] for r in rows], np.float64)
    x[:, 4] = np.log(np.clip(x[:, 4], 1e-3, 1e3))
    games = np.array([r["game"] for r in rows])
    ug = np.unique(games)
    val = np.isin(games, np.random.default_rng(0).choice(ug, len(ug) // 4, replace=False))
    for label in ["win", "prey_dies"]:
        y = np.array([r[label] for r in rows])
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(x[~val], y[~val])
        lr, sc = m[-1], m[0]
        p = m.predict_proba(x[val])[:, 1]
        print(f"\n[{label}] engaged decisions {len(rows)} ({len(ug)} games), base rate {y.mean():.3f}, val AUC {roc_auc_score(y[val], p):.3f}")
        print("  calibration (predicted -> actual, val):", ", ".join(
            f"{p[(p >= a) & (p < b)].mean():.2f}->{y[val][(p >= a) & (p < b)].mean():.2f} (n={((p >= a) & (p < b)).sum()})"
            for a, b in [(0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)] if ((p >= a) & (p < b)).any()))
        print("  coefficients:", ", ".join(f"{c}={w:+.3f}" for c, w in zip(COLS, lr.coef_[0])), f"intercept={lr.intercept_[0]:+.3f} (standardised, power_ratio logged)")
        np.savez(W2.parent / "Cambridge-Battlecode-2026-Autumn/data/ml" / f"simcal_{label}.npz", coef=lr.coef_[0], intercept=lr.intercept_, mean=sc.mean_, scale=sc.scale_, cols=np.array(COLS))


if __name__ == "__main__":
    main()
