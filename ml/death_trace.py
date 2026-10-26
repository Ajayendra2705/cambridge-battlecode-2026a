import json
import math
import re
import zipfile
from collections import Counter
from multiprocessing import Pool

import numpy as np
import pandas as pd
import torch

import reinforce_data as rd
from common import FIGHTS, INDEX, OUT, ROOT, load_game
from rf_calibration import predict, to_arrays
from simfight import alive, dist

TEAM = "Velvet Tributers"
BACK = 15
LN2 = math.log(2)


def our_games():
    out = []
    for line in open(INDEX):
        m = json.loads(line)
        for side, t in (("a", 0), ("b", 1)):
            if m["teams"][side]["name"] == TEAM and (FIGHTS / f"{m['matchId']}.jsonl.gz").exists():
                out.append((m["matchId"], t, side, m["map"]))
    return out


def death_lines(game, side):
    with zipfile.ZipFile(ROOT / "data/replays/ranked" / f"{game}.repl26a") as z:
        text = z.read(f"team-{side}.stdout").decode(errors="replace").replace("\0", "")
    out = []
    for line in text.splitlines():
        m = re.match(r"D(\d+) s(\d+) r(\d+) hp=(\S+) (\S+) en:(.*)", line)
        if m:
            out.append(dict(last_round=int(m[3]), hp=float(m[4]), act=m[5], enemies=len(m[6].split())))
    return out


def trace(args):
    game, team, side, map_name = args
    _, rounds = load_game(game)
    rd.load_game = lambda _: (None, rounds)
    saved = rd.EVERY
    rd.EVERY = 1
    rows = rd.game_arrays((game, map_name))[1]
    rd.EVERY = saved
    by_key = {(r["idx"], r["champ"]): i for i, r in enumerate(rows)}
    dlines = death_lines(game, side)
    deaths = []
    for d in range(1, len(rounds)):
        for ch, (p, c) in enumerate(zip(rounds[d - 1]["c"], rounds[d]["c"])):
            if c["t"] != team or not p["a"] or c["a"]:
                continue
            last = rounds[d - 1]["r"]
            act = next((x["act"] for x in dlines if x["last_round"] == last), None)
            steps = []
            for k in range(BACK, 0, -1):
                i = d - k
                if i < 1:
                    continue
                rnd, nxt = rounds[i], rounds[i + 1]
                me = rnd["c"][ch]
                if not alive(me):
                    continue
                vis = [j for j in rnd["vis"][ch] if alive(rnd["c"][j])]
                near_e = sum(dist(me, rnd["c"][j]) <= 6 for j in vis)
                near_a = sum(dist(me, rnd["c"][j]) <= 5 for j in rnd["avis"][ch] if alive(rnd["c"][j]))
                away = None
                if vis and alive(nxt["c"][ch]):
                    j = min(vis, key=lambda j: dist(me, rnd["c"][j]))
                    before, after = dist(me, rnd["c"][j]), dist(nxt["c"][ch], rnd["c"][j])
                    away = 1 if after > before else -1 if after < before else 0
                steps.append(dict(k=-k, hp=me["hp"] / me["mhp"], near_e=near_e, near_a=near_a, away=away, row=by_key.get((i, ch)),
                                  arrived=rd.arrivals(rounds, i, ch)))
            deaths.append(dict(game=game, champ=ch, round=rounds[d]["r"], act=act, steps=steps))
    return deaths, rows


def main():
    ckpt = torch.load(OUT / "rf_model_s0.pt", weights_only=False)
    with Pool(6) as pool:
        results = pool.map(trace, our_games())
    records = []
    for deaths, rows in results:
        mu = predict(ckpt, to_arrays(rows)) if rows else np.zeros((0, 2))
        for dth in deaths:
            for s in dth["steps"]:
                e, a = (mu[s["row"]] if s["row"] is not None else (0.0, 0.0))
                records.append(dict(game=dth["game"], champ=dth["champ"], death=dth["round"], act=dth["act"], k=s["k"], hp=s["hp"],
                                    near_e=s["near_e"], near_a=s["near_a"], away=s["away"], pred_e=e, pred_a=a, arrived=s["arrived"]))
    df = pd.DataFrame(records)
    df.to_parquet(OUT / "death_trace.parquet")
    deaths = df.groupby(["game", "champ", "death"]).first().reset_index()
    print(f"{len(deaths)} deaths of our champions in {df['game'].nunique()} games")
    print("bot activity at death (D lines):", Counter(deaths["act"].fillna("no D line")).most_common(10))
    df["fires"] = (df["pred_e"] > LN2) & (df["pred_a"] <= LN2)
    df["fleeing"] = (df["away"] == 1).where(df["away"].notna())
    table = df.groupby("k").agg(hp=("hp", "mean"), enemies_near=("near_e", "mean"), allies_near=("near_a", "mean"),
                                pred_enemy=("pred_e", "mean"), rule_fires=("fires", "mean"), moving_away=("fleeing", "mean"),
                                true_arrivals=("arrived", "mean"))
    print("\nAverage over deaths, by rounds before death:")
    print(table.round(2).to_string())

    leads = []
    for _, g in df.sort_values("k").groupby(["game", "champ", "death"]):
        fired = g[g["fires"]]
        warn = fired["k"].min() if len(fired) else None
        flee_run = None
        known = g[g["fleeing"].notna()]
        for k, f in zip(known["k"][::-1], known["fleeing"][::-1]):
            if not f:
                break
            flee_run = k
        leads.append(dict(first_warning=warn, flee_start=flee_run, act=g["act"].iloc[0]))
    L = pd.DataFrame(leads)
    print(f"\nDeaths with a warning (ln 2 rule fired) in the last {BACK} rounds: {L['first_warning'].notna().mean():.0%}")
    print(f"Deaths where the champion was moving away from the nearest enemy in its last rounds: {L['flee_start'].notna().mean():.0%}")
    both = L.dropna()
    if len(both):
        print(f"When both: first warning at {both['first_warning'].median():.0f} rounds before death (median), continuous fleeing from {both['flee_start'].median():.0f}")
        print(f"  warning came before fleeing started in {(both['first_warning'] < both['flee_start']).mean():.0%} of them")


if __name__ == "__main__":
    main()
