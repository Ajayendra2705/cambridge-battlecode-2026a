"""evalsum.py RUNDIR NAME... : summary of an evaluate.sh run (tools/evalsum.ts is the same for evaluate_deno.sh).

Per candidate: official wins first, then mean margin +- standard error, pace vs starter with how many of those games
reached 1000, the difference from C1 (paired by map, opponent, side and seed), per-opponent margins. Then per map:
each candidate's mean +- se and how many distinct games it produced (identical results across seeds mean the seed
did not change the game, so those games are not independent samples).

Fails closed (exit 1) unless the run is exactly the expected match manifest (review b4e8fd2: a log without a winner
and two copies of one match both passed before). With EXPECT_MAPS ("ambush collision ..."), every NAME (C<i>s<seed>)
x opponent (EXPECT_OPPS) x map x side must be present once, as <map>-<A>-<B>.log in <RUN>/<NAME>-<opp>, whose header
names those two bots and that map, with a terminal "Team X (bot) wins:" line, both result rows and no candidate
crash; any other log in those folders (a duplicate, a stray copy) invalidates the run. Without EXPECT_MAPS every log
is still checked the same way and each (candidate, opponent, map, side) may appear only once (EXPECT: logs a sweep).
"""
import collections
import math
import os
import re
import sys

run = sys.argv[1]
names = sys.argv[2:]
games = collections.defaultdict(list)  # cand -> [(map, opp, side, seed, margin, win)]
pace = collections.defaultdict(list)   # cand -> [(map, round, reached)]
failed = collections.defaultdict(list)  # cand -> reasons the run is invalid
expect_opps = os.environ.get("EXPECT_OPPS", "").split()
expect_maps = os.environ.get("EXPECT_MAPS", "").split()
expect_games = int(os.environ.get("EXPECT", "0"))


def ls(d):
    try:
        return sorted(os.listdir(d))
    except OSError:
        return []


def parse(t):
    """One game log as a dict, or the reason it is not a finished game."""
    h = re.search(r"^(\S+) vs (\S+) on maps[\\/]([^\s\\/]+?)\.map26a\s*$", t, re.M)
    if not h:
        return "no match header"
    w = re.findall(r"^Team ([AB]) \((\S+)\) wins: (.+?)\s*$", t, re.M)
    if len(w) != 1:
        return "several winner lines" if w else "no winner"
    letter, winner, reason = w[0]
    gems, crashes = {}, {}
    for r in re.finditer(r"^\s+([AB])\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", t, re.M):
        if r.group(2) != (h.group(1) if r.group(1) == "A" else h.group(2)):
            return f"result row {r.group(1)} is {r.group(2)}"
        gems[r.group(2)] = int(r.group(3))
        crashes[r.group(2)] = int(r.group(7))
    if len(gems) != 2:
        return "result table incomplete"
    if winner != (h.group(1) if letter == "A" else h.group(2)):
        return f"winner {winner} is not team {letter}"
    mp = re.sub(r"-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$", "", h.group(3))
    return {"a": h.group(1), "b": h.group(2), "map": mp, "winner": winner, "reason": reason, "gems": gems, "crashes": crashes}


seen = set()
for n in names:
    cand, seed = n.split("s")
    expected = set()
    for o in expect_opps:
        if not ls(f"{run}/{n}-{o}"):
            failed[cand].append(f"{n}-{o}: sweep missing")
        for m in expect_maps:
            for a, b in ((n, o), (o, n)):
                expected.add(f"{n}-{o}/{m}-{a}-{b}.log")
    for e in sorted(expected):
        if not os.path.isfile(f"{run}/{e}"):
            failed[cand].append(f"{e}: missing")
    for dname in ls(run):
        d = f"{run}/{dname}"
        if not dname.startswith(f"{n}-") or not os.path.isdir(d):
            continue
        opp = dname[len(n) + 1:]
        logs = [f for f in ls(d) if f.endswith(".log")]
        if not expect_maps and expect_games and len(logs) != expect_games:
            failed[cand].append(f"{dname}: {len(logs)} games, expected {expect_games}")
        for lf in logs:
            rel = f"{dname}/{lf}"
            if expect_maps and rel not in expected:
                failed[cand].append(f"{rel}: not in the manifest")
                continue
            g = parse(open(f"{d}/{lf}", encoding="utf-8", errors="replace").read())
            if isinstance(g, str):
                failed[cand].append(f"{rel}: {g}")
                continue
            side = "A" if g["a"] == n else "B" if g["b"] == n else ""
            if not side or (g["b"] if side == "A" else g["a"]) != opp:
                failed[cand].append(f"{rel}: header is {g['a']} vs {g['b']}")
                continue
            if expect_maps and rel != f"{dname}/{g['map']}-{g['a']}-{g['b']}.log":
                failed[cand].append(f"{rel}: header is {g['a']} vs {g['b']} on {g['map']}")
                continue
            key = (n, opp, g["map"], side)
            if key in seen:
                failed[cand].append(f"{rel}: duplicate of {opp} {g['map']} side {side}")
                continue
            seen.add(key)
            if g["crashes"].get(n, 0) > 0:
                failed[cand].append(f"{rel}: {g['crashes'][n]} crashes")
            if g["crashes"].get(opp, 0) > 0:  # review 2026-10-22: an opponent fault is not a candidate result
                failed[cand].append(f"{rel}: opponent {opp} crashed {g['crashes'][opp]}x (excluded)")
                continue
            win = g["winner"] == n
            if opp == "starter":
                r = re.search(r"reached 1000 gems in round (\d+)", g["reason"])
                pace[cand].append((g["map"], int(r.group(1)) if win and r else 2000, bool(win and r)))
                continue
            games[cand].append((g["map"], opp, side, seed, g["gems"][n] - g["gems"][opp], win))


def stats(xs):
    if not xs:
        return 0.0, 0.0
    mean = sum(xs) / len(xs)
    if len(xs) < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)
    return mean, math.sqrt(var / len(xs))


meta_path = os.path.join(run, "meta.txt")
if os.path.isfile(meta_path):
    meta = [ln.strip() for ln in open(meta_path, encoding="utf-8") if re.match(r"^(engine|head|base|maps)=", ln)]
    if meta:
        print("meta: " + "  ".join(meta))
cands = sorted(games)
base = cands[0] if cands else None
bm, bse = stats([g[4] for g in games[base]]) if base else (0, 0)
for c in cands:
    m = [g[4] for g in games[c]]
    mean, se = stats(m)
    wins = sum(g[5] for g in games[c])
    line = f"{c}: wins {wins}/{len(m)} margin {mean:+.0f} +-{se:.0f}"
    p = pace[c]
    if p:
        line += f" pace {sum(x[1] for x in p) / len(p):.0f} ({sum(x[2] for x in p)}/{len(p)} reached)"
    if c != base:
        diff, dse = mean - bm, math.sqrt(se * se + bse * bse)
        line += f" | vs {base} {diff:+.0f} +-{dse:.0f}{' *' if abs(diff) > 2 * dse else ''}"
        # Paired by map, opponent, side and seed, over the same game set only.
        bk = {(g[0], g[1], g[2], g[3]): g[4] for g in games[base]}
        pd = [g[4] - bk[(g[0], g[1], g[2], g[3])] for g in games[c] if (g[0], g[1], g[2], g[3]) in bk]
        if len(pd) != len(m) or len(pd) != len(bk):
            failed[c].append(f"pairing with {base}: {len(pd)} of {len(m)}/{len(bk)} games")
        if len(pd) > 1:
            pm, pse = stats(pd)
            line += f" paired {pm:+.0f} +-{pse:.0f} (n {len(pd)})"
    if failed[c]:
        line += f" | INCOMPLETE: {len(failed[c])} failed/missing"
    per = collections.defaultdict(list)
    for g in games[c]:
        per[g[1]].append(g[4])
    line += " | " + " ".join(f"{o}:{sum(v) / len(v):+.0f}" for o, v in sorted(per.items()))
    print(line)
for c, p in sorted(pace.items()):
    if c not in games:
        print(f"{c}: pace {sum(x[1] for x in p) / len(p):.0f} ({sum(x[2] for x in p)}/{len(p)} reached)")

maps = sorted({g[0] for c in cands for g in games[c]})
if maps:
    print("per map: mean +-se [distinct games / games]")
    for mp in maps:
        cells = []
        for c in cands:
            sel = [g for g in games[c] if g[0] == mp]
            mean, se = stats([g[4] for g in sel])
            distinct = len({(g[1], g[2], g[4]) for g in sel})
            cells.append(f"{c} {mean:+5.0f}+-{se:<3.0f}[{distinct}/{len(sel)}]")
        print(f"  {mp:11} " + "  ".join(cells))

# Fail closed: a missing, duplicate, stray, unfinished or crashed game makes the run invalid.
bad = [c for c in sorted({n.split("s")[0] for n in names}) if failed[c]]
if bad or (expect_opps and not games and not pace):
    print("INCOMPLETE - results invalid:", ", ".join(f"{c} ({len(failed[c])}: {'; '.join(failed[c][:3])}...)" for c in bad) or "no games")
    sys.exit(1)
