from simfight import alive

HORIZON = 60


def step_gain(rounds, k, e):
    p, q = rounds[k]["c"][e], rounds[k + 1]["c"][e]
    if not (alive(p) and alive(q)):
        return 0.0, 0.0
    gold = max(0.0, q["au"] - p["au"])
    if q["g"] >= p["g"]:
        return float(q["g"] - p["g"]), gold
    t = p["t"]
    banked = rounds[k + 1]["sg"][t] - rounds[k]["sg"][t]
    if banked <= 0:
        return float(q["g"]), gold
    droppers = [j for j, (a, b) in enumerate(zip(rounds[k]["c"], rounds[k + 1]["c"]))
                if a["t"] == t and alive(a) and alive(b) and b["g"] < a["g"]]
    hidden = max(0, banked - (p["g"] - q["g"])) if droppers == [e] else 0
    return float(q["g"] + hidden), gold


def enemy_gain(rounds, i, e, horizon):
    end = rounds[i]["r"] + horizon
    gems = gold = 0.0
    k = i
    while k + 1 < len(rounds) and rounds[k + 1]["r"] <= end:
        g, au = step_gain(rounds, k, e)
        gems += g
        gold += au
        k += 1
    return gems, gold
