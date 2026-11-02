"""Apply a deaths bar to lscreen.py output: python -I tools/local/lbar.py LSCREEN_OUTPUT [CAND ...]

Prints PASS or FAIL per candidate (all candidates in the file when none are named) for the bar used by the fight
variants of 11-02 (results/analysis/rule_1498.md): deaths down by at least one standard error, gems collected by the
round not down by more than two standard errors, wins not down by more than 0.03 a game, and no bot fault.
Exit status 0 when every named candidate passes.
"""
import re
import sys

NUM = r"([+-]?\d+\.\d+) \+-\s+(\d+\.\d+)"


def rows(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        parts = line.split()
        if len(parts) < 4 or not parts[1].isdigit():
            continue
        nums = re.findall(NUM, line)
        if len(nums) != 9:
            continue
        name, faults = parts[0], int(parts[2])
        win, margin, coll, trib, their, deaths = (tuple(map(float, x)) for x in nums[:6])
        out[name] = {"faults": faults, "win": win, "coll": coll, "deaths": deaths}
    return out


def verdict(r, bar="fight"):
    why = []
    if bar == "fight" and r["deaths"][0] > -r["deaths"][1]:
        why.append(f"deaths {r['deaths'][0]:+.2f} +- {r['deaths'][1]:.2f}")
    if bar == "item" and r["deaths"][0] > r["deaths"][1]:
        why.append(f"deaths up {r['deaths'][0]:+.2f} +- {r['deaths'][1]:.2f}")
    if r["coll"][0] < -2 * r["coll"][1]:
        why.append(f"collected {r['coll'][0]:+.1f} +- {r['coll'][1]:.1f}")
    if bar == "item" and r["coll"][0] < -26.0:
        why.append(f"collected {r['coll'][0]:+.1f} (more than 3% down)")
    if r["win"][0] < -0.03:
        why.append(f"wins {r['win'][0]:+.2f}")
    if r["faults"]:
        why.append(f"{r['faults']} faults")
    return not why, why


def main():
    # --bar item (for item changes, whose gain shows only against strong teams): deaths not up by more than one
    # standard error, collected not down by more than two standard errors nor by more than 26 a game (3%), wins
    # not down by more than 0.03.
    bar = "fight"
    if "--bar" in sys.argv:
        i = sys.argv.index("--bar")
        bar = sys.argv[i + 1]
        del sys.argv[i:i + 2]
    table = rows(sys.argv[1])
    names = sys.argv[2:] or list(table)
    ok = True
    for n in names:
        if n not in table:
            print(n, "MISSING")
            ok = False
            continue
        good, why = verdict(table[n], bar)
        ok &= good
        r = table[n]
        print(n, "PASS" if good else "FAIL", f"deaths {r['deaths'][0]:+.2f} +- {r['deaths'][1]:.2f}",
              f"collected {r['coll'][0]:+.1f} +- {r['coll'][1]:.1f}", f"wins {r['win'][0]:+.2f}", "; ".join(why))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
