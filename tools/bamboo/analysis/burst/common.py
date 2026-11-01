# common.py : loader for burst/extract.ts output (one JSON per game, file name = replay dir name map__teamA__teamB__id).
# Game(path, focus) gives per-round states, actions, PvP damage events (actor -> enemy champion), deaths with the killing actor,
# and helpers. focus = the team name as written in the directory (IntercontinentalFish, BambooTeahouse, ...).
import json, os, collections

NAMES = ["Ryth", "Vesper", "Vendetta", "Cassi", "Issac", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg", "Tavi", "HoR"]
# One-round damage model per champion (2.0.0 abilityProps, probe abprops.ts): auto = strength; extra autos from a reset (type 1, not
# enhanced); damaging spells modifier x focus. Slots whose type is 2/3/4 deal modifier x focus (Cassi S1 / Prism S0 stun modifiers kept).
SPELL_MOD = {  # (name, slot) -> focus multiplier of the damaging spell
    ("Marcella", 1): 2.0, ("HoR", 1): 1.5, ("Cassi", 0): 2.0, ("Ren", 0): 1.1, ("Ryth", 0): 1.0, ("Prism", 0): 1.5, ("Prism", 1): 1.0,
    ("Tavi", 1): 1.6, ("Stellar", 0): 2.0, ("Stellar", 1): 2.0,
}
RESET = {("Vendetta", 0), ("Vesper", 0), ("Issac", 0), ("Ryth", 1), ("Willow", 1), ("Tavi", 0), ("Varg", 0)}
DASH = {("Vendetta", 1), ("HoR", 1), ("Vesper", 1), ("Issac", 1), ("Ren", 1)}
CC = {("Marcella", 0), ("HoR", 1), ("Cassi", 1), ("Ren", 0), ("Ryth", 0), ("Prism", 0), ("Tavi", 1)}  # stun-carrying slots


def cheb(a, b):
    return max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))


class Game:
    def __init__(self, path, focus):
        d = json.load(open(path))
        base = os.path.basename(path)[:-5]
        p = base.split("__")
        self.name, self.map, self.gid = base, p[0], p[-1]
        self.teams = (p[1], p[2])
        self.focus = 0 if p[1] == focus else (1 if p[2] == focus else None)
        self.opp_name = p[2] if self.focus == 0 else p[1]
        self.ch = {int(k): v for k, v in d["champions"].items()}
        self.team = {k: v["team"] for k, v in self.ch.items()}
        self.cname = {k: v["name"] for k, v in self.ch.items()}
        self.byr = {r["r"]: {c["id"]: c for c in r["ch"]} for r in d["rounds"]}
        self.rounds = sorted(self.byr)
        self.last = self.rounds[-1]
        self.acts = collections.defaultdict(list)  # r -> acts in order
        for a in d["acts"]:
            self.acts[a["r"]].append(a)
        self.pvp = []  # (r, actor, victim, amt, kind, slot)
        self.dmg_on = collections.defaultdict(lambda: collections.defaultdict(float))  # victim -> r -> damage from enemy champions
        self.dmg_by = collections.defaultdict(lambda: collections.defaultdict(float))  # (victim, r) -> actor -> damage
        self.heal = collections.defaultdict(float)  # (victim, r) -> healed
        for a in d["acts"]:
            if not a.get("d"):
                continue
            for v, amt in a["d"].items():
                v = int(v)
                if amt > 0 and self.team[v] != self.team[a["id"]]:
                    self.pvp.append((a["r"], a["id"], v, amt, a["k"], a.get("s")))
                    self.dmg_on[v][a["r"]] += amt
                    self.dmg_by[(v, a["r"])][a["id"]] += amt
                elif amt < 0:
                    self.heal[(v, a["r"])] += -amt
        self.mdmg = collections.defaultdict(float)
        for m in d["mdmg"]:
            self.mdmg[(m["v"], m["r"])] += m["amt"]
        self.deaths = d["deaths"]
        r1 = self.byr[self.rounds[min(1, len(self.rounds) - 1)]]
        self.spawn = {t: [c["p"] for c in r1.values() if c["t"] == t and c.get("p")] for t in (0, 1)}

    def st(self, r, cid):
        return self.byr.get(r, {}).get(cid)

    def alive(self, r, team=None):
        return [c for c in self.byr.get(r, {}).values() if c["al"] and c.get("p") and (team is None or c["t"] == team)]

    def near(self, r, p, team, rad, excl=None):
        return [c for c in self.alive(r, team) if c["id"] != excl and cheb(c["p"], p) <= rad]

    def spawn_dist(self, p, team):
        return min(cheb(p, s) for s in self.spawn[team]) if self.spawn[team] else 99

    def burst(self, c, ready_only=True):
        """One-round damage potential of champion state c on an enemy: auto + reset auto + damaging spells (ready only)."""
        nm = self.cname[c["id"]]
        dmg = c["st"]
        for s in (0, 1):
            if ready_only and (len(c["cd"]) <= s or c["cd"][s] > 0):
                continue
            if (nm, s) in RESET:
                dmg += c["st"]
            if (nm, s) in SPELL_MOD:
                dmg += SPELL_MOD[(nm, s)] * c["fo"]
        return dmg

    def spells_ready(self, c):
        nm = self.cname[c["id"]]
        return sum(1 for s in (0, 1) if len(c["cd"]) > s and c["cd"][s] == 0 and ((nm, s) in SPELL_MOD or (nm, s) in RESET or (nm, s) in CC or (nm, s) in DASH))

    def busy(self, v, r):
        """What champion v was doing at round r: channel kind, camp (hit a camp or took monster damage in r-3..r), fighting
        (dealt or took champion damage in r-5..r-1), walking (moved in r-1), else idle."""
        c = self.st(r, v) or {}
        chn = c.get("chn", 0)
        acted = any(a["id"] == v and a["k"] in (4, 5, 6) for a in self.acts.get(r, []))
        if chn == 1:
            # four top teams pre-start a recall at every turn end and cancel it at the next turn start: a genuine recall keeps
            # channelling (no move / attack / cast this round); a pre-start shows as channel 1 at the round start only.
            if not acted: return "recall"
            chn = 0
            c = dict(c, prestart=True)
        if chn == 2: return "tribute"
        if chn == 4: return "crystal"
        camp = any(a["id"] == v and a.get("tc") == "m" for rr in range(r - 3, r + 1) for a in self.acts.get(rr, [])) or \
            any(self.mdmg.get((v, rr), 0) > 0 for rr in range(r - 3, r + 1))
        if camp: return "camp"
        fight = any(self.dmg_on[v].get(rr, 0) > 0 for rr in range(r - 5, r)) or \
            any(x[1] == v for rr in range(r - 5, r) for x in self.pvp_at(rr))
        if fight: return "fighting"
        if any(a["id"] == v and a["k"] == 4 for a in self.acts.get(r - 1, [])): return "walking"
        return "idle"

    def pvp_at(self, r):
        if not hasattr(self, "_pvp_r"):
            self._pvp_r = collections.defaultdict(list)
            for x in self.pvp:
                self._pvp_r[x[0]].append(x)
        return self._pvp_r.get(r, [])


def chains(rounds, gap):
    """Split a sorted list of rounds into chains whose consecutive members are at most gap apart."""
    out = []
    for r in rounds:
        if out and r - out[-1][-1] <= gap:
            out[-1].append(r)
        else:
            out.append([r])
    return out
