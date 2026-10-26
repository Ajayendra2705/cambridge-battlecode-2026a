import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

from common import ROOT, load_game

EARLY = 300


def side_metrics(path):
    cand, opp, map_name, us = path.name.removesuffix(".jsonl.gz").split("~")[:4]
    t = 0 if us.endswith("A") else 1
    _, rounds = load_game(path)
    solo = shared = 0
    for x, y in zip(rounds, rounds[1:]):
        if x["r"] >= EARLY:
            break
        n = sum(1 for ch, (p, q) in enumerate(zip(x["c"], y["c"]))
                if p["t"] == t and p["a"] and q["a"] and q["g"] > p["g"] and q["k"] == p["k"] and not any(a[0] == "tribute" for a in x["act"][ch]))
        solo += n == 1
        shared += n > 1
    at = {r["r"]: r for r in rounds}
    held = lambda r, side: r["sg"][side] + sum(c["g"] for c in r["c"] if c["t"] == side) if r else np.nan
    return dict(cand=cand.replace(".", "/"), opp=opp, map=map_name, solo=solo, shared=shared,
                have200=held(at.get(200), t), opp_have200=held(at.get(200), 1 - t),
                banked300=at[300]["sg"][t] if 300 in at else np.nan,
                first_trib=next((r["r"] for r in rounds if r["sg"][t] > 0), np.nan))


def main():
    run = Path(sys.argv[1])
    out = ROOT / "data/fights" / f"local_{run.name}"
    replays = sorted(str(p) for p in run.glob("*.repl26a"))
    if not out.exists() or len(list(out.glob("*.jsonl.gz"))) < len(replays):
        chunks = [replays[i::6] for i in range(6)]
        procs = [subprocess.Popen(["node", str(ROOT / "tools/replay/rounds_extract.mjs"), str(out), *c], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for c in chunks if c]
        for p in procs:
            p.wait()
    with Pool(6) as pool:
        rows = pool.map(side_metrics, sorted(out.glob("*.jsonl.gz")))
    df = pd.DataFrame(rows)
    df.to_parquet(ROOT / "data/ml" / f"opening_{run.name}.parquet")
    print(f"opening metrics (r0-{EARLY}), {run.name}:")
    print(df.groupby("cand").agg(games=("solo", "size"), solo=("solo", "mean"), shared=("shared", "mean"), have200=("have200", "median"),
                                 opp_have200=("opp_have200", "median"), banked300=("banked300", "median"), first_trib=("first_trib", "median")).round(2).to_string())


if __name__ == "__main__":
    main()
