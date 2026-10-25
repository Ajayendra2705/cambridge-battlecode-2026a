import copy
from dataclasses import dataclass

RESET, DAMAGE, AOE, CC, HEAL, DASH, SHIELD = 1, 2, 3, 4, 5, 6, 7
CASSI, ISSAC, PRISM, RYTH, HOR = 3, 4, 6, 0, 12

CHAMPS = {
    0: dict(range=1, hp=(1200, 100), str=(45, 5), focus=(100, 10), slots=[(AOE, 1.0), (RESET, 0)]),
    1: dict(range=3, hp=(1000, 100), str=(55, 5), focus=(100, 10), slots=[(RESET, 0), (DASH, 0)]),
    2: dict(range=1, hp=(1000, 100), str=(70, 6), focus=(100, 10), slots=[(RESET, 0), (DASH, 0)]),
    3: dict(range=3, hp=(600, 65), str=(30, 3), focus=(70, 13), slots=[(DAMAGE, 2.0), (CC, 0)]),
    4: dict(range=1, hp=(900, 80), str=(40, 3), focus=(100, 10), slots=[(RESET, 0), (DASH, 0)]),
    5: dict(range=3, hp=(650, 65), str=(30, 3.5), focus=(70, 7), slots=[(DAMAGE, 2.0), (AOE, 1.4)]),
    6: dict(range=3, hp=(700, 60), str=(35, 2.5), focus=(80, 8), slots=[(CC, 1.5), (AOE, 1.0)]),
    7: dict(range=1, hp=(1200, 100), str=(45, 5), focus=(60, 15), slots=[(RESET, 0), (DAMAGE, 2.0)]),
    8: dict(range=3, hp=(700, 50), str=(55, 3), focus=(120, 5), slots=[(HEAL, 3.0), (RESET, 0)]),
    9: dict(range=1, hp=(900, 100), str=(35, 5), focus=(100, 9), slots=[(CC, 0.75), (DASH, 0)]),
    10: dict(range=1, hp=(1000, 100), str=(40, 5), focus=(100, 10), slots=[(RESET, 0), (SHIELD, 2.5)]),
    11: dict(range=3, hp=(900, 75), str=(45, 5), focus=(110, 10), slots=[(RESET, 0), (CC, 1.4)]),
    12: dict(range=1, hp=(1000, 100), str=(30, 3.5), focus=(100, 12), slots=[(SHIELD, 1.5), (DASH, 1.5)]),
}

ITEM_UNITS = {}
for fam in range(7):
    for stat in range(3):
        shard, emblem = fam * 6 + stat * 2, fam * 6 + stat * 2 + 1
        units = [0, 0, 0]
        units[stat] = 1
        ITEM_UNITS[shard] = tuple(units)
        units = [1 if fam == 6 else 0] * 3
        units[stat] = 6 if fam == 1 else 5
        ITEM_UNITS[emblem] = tuple(units)


def stats(c):
    t = CHAMPS[c["ty"]]
    u = [0, 0, 0]
    for i, n in c.get("it", []):
        for k, v in enumerate(ITEM_UNITS[i]):
            u[k] += v * n
    strength = t["str"][0] + t["str"][1] * u[0]
    focus = t["focus"][0] + t["focus"][1] * u[1]
    if c["ty"] == RYTH:
        strength += 0.01 * t["hp"][1] * u[2]
    if c["ty"] == PRISM:
        focus += 1.5 * c["g"]
    return strength, focus


def coef(ty):
    resets = per_round = cast = 0.0
    for kind, mod in CHAMPS[ty]["slots"]:
        if kind == RESET:
            resets += 1 / 8
        if kind not in (SHIELD, HEAL) and mod > 0:
            per_round += mod / 8
            cast = max(cast, mod)
    return resets, per_round, cast


def damage_scale(c):
    if c["ty"] != HOR or c["mhp"] <= 0:
        return 1.0
    return 1.0 + 0.5 * (1 - c["hp"] / c["mhp"])


def champion_dps(c):
    strength, focus = stats(c)
    resets, per_round, _ = coef(c["ty"])
    return strength * (1 + resets) + per_round * focus


def my_dps(c):
    strength, focus = stats(c)
    d = strength
    for kind, mod in CHAMPS[c["ty"]]["slots"]:
        if kind in (DAMAGE, AOE):
            d += mod * focus / 8
        if kind == RESET:
            d += strength / 8
    return d


@dataclass
class SimSlot:
    dmg: float = 0
    cd: int = 99
    stun: bool = False
    reset: bool = False


@dataclass
class SimUnit:
    hp: float
    str: float
    range: int
    slots: list
    d: int = 99
    link: int = -1
    stunned: bool = False


def read_slots(c, cds):
    _, focus = stats(c)
    out = []
    for (kind, mod), cd in zip(CHAMPS[c["ty"]]["slots"], cds):
        dmg = mod * focus if kind in (DAMAGE, AOE, CC, DASH) else 0.0
        out.append(SimSlot(dmg=dmg, cd=cd, stun=kind == CC, reset=kind == RESET))
    return out


def simulate_fight(u, rounds=3, them_first=True):
    u = copy.deepcopy(u)
    start = [sum(x.hp for x in side) for side in u]
    for _ in range(rounds):
        for k in range(2):
            s = 1 - k if them_first else k
            o = 1 - s
            for x in u[s]:
                if x.hp <= 0:
                    continue
                if x.stunned:
                    x.stunned = False
                    continue
                t = None
                for y in u[o]:
                    if y.hp > 0 and (t is None or y.hp < t.hp):
                        t = y
                if t is None:
                    break
                moved = False
                want = max(x.range, 4)
                spell_ready = any(sl.cd <= 0 and (sl.dmg > 0 or sl.stun) for sl in x.slots)
                if x.d > (want if spell_ready else x.range):
                    x.d -= 1
                    moved = True
                dmg = 0.0
                melee = x.range <= 1
                cast = None
                if not moved and x.d <= 4:
                    for sl in x.slots:
                        if sl.cd <= 0 and sl.stun and not t.stunned:
                            cast = sl
                    if cast is None:
                        for sl in x.slots:
                            if sl.cd <= 0 and sl.dmg > 0 and (cast is None or sl.dmg > cast.dmg):
                                cast = sl
                if cast is None and x.d <= x.range and (melee or not moved):
                    for sl in x.slots:
                        if sl.cd <= 0 and sl.reset:
                            cast = sl
                if x.d <= x.range and (melee or not moved):
                    dmg += x.str
                if cast is not None:
                    if cast.reset:
                        dmg += x.str
                    dmg += cast.dmg
                    if cast.stun:
                        t.stunned = True
                    cast.cd = 9
                t.hp -= dmg
                if t.hp <= 0 and t.link >= 0:
                    u[o][t.link].hp = 0
        for side in u:
            for x in side:
                for sl in x.slots:
                    if sl.cd > 0:
                        sl.cd -= 1
    dead = [sum(x.hp <= 0 for x in side) for side in u]
    left = [sum(x.hp for x in side if x.hp > 0) for side in u]
    hp_frac = [left[s] / start[s] if start[s] > 0 else 0 for s in range(2)]
    return dict(dead=dead, hp_frac=hp_frac, unit0_dead=bool(u[0]) and u[0][0].hp <= 0)


def dist(a, b):
    return max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))


def alive(c):
    return c["a"] and "x" in c


def engage_decision(rnd, cds, i):
    c = rnd["c"]
    me = c[i]
    enemies = [j for j in rnd["vis"][i] if alive(c[j])]
    allies = [j for j in rnd["avis"][i] if alive(c[j])]
    my_range = CHAMPS[me["ty"]]["range"]
    dps = {j: champion_dps(c[j]) * damage_scale(c[j]) for j in enemies + allies}

    enemy_hp = enemy_dps = 0.0
    enemy_count = 0
    prey = None
    key = lambda j: dps[j] / max(c[j]["hp"], 1) * (1 + c[j]["g"] / 40)
    for j in enemies:
        if dist(me, c[j]) > 6:
            continue
        enemy_hp += c[j]["hp"]
        enemy_dps += dps[j]
        enemy_count += 1
        if dist(me, c[j]) <= max(my_range, 4) and (prey is None or key(j) > key(prey)):
            prey = j
    if prey is None:
        for j in enemies:
            if dist(me, c[j]) > 8:
                continue
            if any(dist(c[a], c[j]) <= 3 for a in allies) and (prey is None or c[j]["hp"] < c[prey]["hp"]):
                prey = j

    ally_hp, ally_dps = me["hp"], my_dps(me)
    for a in allies:
        if dist(me, c[a]) <= 5:
            ally_hp += c[a]["hp"]
            ally_dps += dps[a]
    enemy_power, ally_power = enemy_hp * enemy_dps, ally_hp * ally_dps

    out = dict(prey=prey, engage=False, winning=False, finisher=False, rich=False, sim=None)
    if prey is None:
        return out

    side_idx = [[i] + [a for a in allies if dist(me, c[a]) <= 8], [j for j in enemies if dist(me, c[j]) <= 8]]
    side = [[], []]
    for s in range(2):
        for j in side_idx[s]:
            strength, _ = stats(c[j])
            side[s].append(SimUnit(hp=c[j]["hp"], str=strength, range=CHAMPS[c[j]["ty"]]["range"], slots=read_slots(c[j], cds[j])))
    for s in range(2):
        for a, x in enumerate(side[s]):
            x.d = min((dist(c[side_idx[s][a]], c[q]) for q in side_idx[1 - s]), default=99)
            for b in range(len(side[s])):
                if {c[side_idx[s][a]]["ty"], c[side_idx[s][b]]["ty"]} == {CASSI, ISSAC}:
                    x.link = b
    res = simulate_fight(side, 3, True)
    me_dies = res["unit0_dead"]
    winning = bool(side[1]) and (res["dead"][1] > res["dead"][0] or (res["dead"][1] == res["dead"][0] and res["hp_frac"][0] > res["hp_frac"][1] + 0.2)) and not (me_dies and res["dead"][1] == 0)

    if not winning and enemy_count == 1 and me["hp"] >= me["mhp"] * 0.5:
        mine = champion_dps(me)
        if mine > 0 and dps[prey] > 0 and c[prey]["hp"] / mine < 1.2 * me["hp"] / dps[prey]:
            winning = True
    finisher = c[prey]["hp"] <= ally_dps * 2.5 and me["hp"] > me["mhp"] * 0.3 and not me_dies
    rich = c[prey]["g"] >= 30 and ally_power >= enemy_power * 0.5 and me["hp"] > me["mhp"] * 0.5 and not me_dies
    big_bag = me["g"] >= 150
    out.update(engage=not big_bag and (winning or finisher or rich), winning=winning, finisher=finisher, rich=rich, sim=res)
    return out
