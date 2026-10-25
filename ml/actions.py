from simfight import alive, dist


def hits(act):
    if act[0] == "attack" and len(act) == 5:
        return act[3], act[4]
    if act[0] == "cast" and len(act) == 6:
        return act[4], act[5]
    return None


def engaged(rounds, idx, champ):
    rnd = rounds[idx]
    c = rnd["c"]
    targets = set()
    for act in rnd["act"][champ]:
        hit = hits(act)
        if hit and hit[0] == "c" and c[hit[1]]["t"] != c[champ]["t"]:
            targets.add(hit[1])
    if idx + 1 < len(rounds) and alive(after := rounds[idx + 1]["c"][champ]):
        for enemy in rnd["vis"][champ]:
            if alive(c[enemy]) and dist(after, c[enemy]) < dist(c[champ], c[enemy]):
                targets.add(enemy)
    return targets
