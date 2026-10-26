import subprocess
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from common import OUT, ROOT
from side_stats import side_stats

FEATURES = ["contact_early", "contact_mid", "enemy_half_early", "enemy_half_mid", "allies_near", "kills", "champ_hits", "camp_hits",
            "deposits_per_1000r", "gems_per_deposit", "wards"]


def style_features(df):
    out = pd.DataFrame(index=df.index)
    share = lambda k, p: df[f"{k}_p{p}"] / df[f"alive_p{p}"].clip(lower=1)
    out["contact_early"] = share("contact", 0)
    out["contact_mid"] = (share("contact", 1) + share("contact", 2)) / 2
    out["enemy_half_early"] = share("enemy_half", 0)
    out["enemy_half_mid"] = (share("enemy_half", 1) + share("enemy_half", 2)) / 2
    out["allies_near"] = (share("allies_near", 0) + share("allies_near", 1)) / 2
    for k in ["kills", "champ_hits", "camp_hits", "gems_per_deposit", "wards"]:
        out[k] = df[k]
    out["deposits_per_1000r"] = 1000 * df["deposits"] / df["rounds"]
    return out


def extract(run):
    out = ROOT / "data/fights" / f"local_{run.name}"
    replays = sorted(str(p) for p in run.glob("*.repl26a"))
    if not out.exists() or len(list(out.glob("*.jsonl.gz"))) < len(replays):
        procs = [subprocess.Popen(["node", str(ROOT / "tools/replay/rounds_extract.mjs"), str(out), *replays[i::6]],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(6)]
        for p in procs:
            p.wait()
    return sorted(out.glob("*.jsonl.gz"))


def one(path):
    cand, opp, map_name, us = path.name.removesuffix(".jsonl.gz").split("~")[:4]
    t = 0 if us.endswith("A") else 1
    rows = side_stats((path, map_name, defaultdict(lambda: "local")))
    return [dict(r, bot=(cand if r["team"] == t else opp).replace(".", "/")) for r in rows]


def real_axes():
    teams = pd.read_parquet(OUT / "team_styles.parquet")
    scaler = StandardScaler().fit(teams[FEATURES])
    pca = PCA(4).fit(scaler.transform(teams[FEATURES]))
    z = pca.transform(scaler.transform(teams[FEATURES]))
    return scaler, pca, pd.DataFrame(z[:, :2], columns=["PC1", "PC2"], index=teams.index).assign(games=teams["games"])


def main():
    run = Path(sys.argv[1])
    with Pool(6) as pool:
        rows = [r for rs in pool.map(one, extract(run)) for r in rs]
    df = pd.DataFrame(rows)
    feats = style_features(df).assign(bot=df["bot"]).groupby("bot").mean()
    scaler, pca, real = real_axes()
    z = pca.transform(scaler.transform(feats[FEATURES]))
    sim = pd.DataFrame(z[:, :2], columns=["PC1", "PC2"], index=feats.index)
    sim.to_parquet(OUT / "style_calibration.parquet")
    pd.set_option("display.width", 200)
    print("Realised style of each bot on the real teams' PCA axes (PC1 = aggression, PC2 = small frequent deposits):")
    print(sim.join(feats[["contact_mid", "enemy_half_mid", "kills", "deposits_per_1000r", "gems_per_deposit"]]).round(2).to_string())
    w = real["games"] / real["games"].sum()
    for ax in ["PC1", "PC2"]:
        m = np.average(real[ax], weights=w)
        sd = np.sqrt(np.average((real[ax] - m) ** 2, weights=w))
        print(f"real teams {ax}: weighted mean {m:.2f}, sd {sd:.2f}, 10-90% {np.percentile(real[ax], 10):.2f} to {np.percentile(real[ax], 90):.2f}; "
              f"sim bots span {sim[ax].min():.2f} to {sim[ax].max():.2f}")


if __name__ == "__main__":
    main()
