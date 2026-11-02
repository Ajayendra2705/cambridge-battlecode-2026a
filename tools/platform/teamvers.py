"""Per-version results of the team's unranked tests, paired against one base version.

Usage: python -I tools/platform/teamvers.py SINCE_ISO BASE_VERSION [--refresh]
  e.g. python -I tools/platform/teamvers.py 2026-11-01T20:00 1490

Every unranked match of our team since SINCE is given to the newest submission uploaded at least two minutes before
the match was created (teammates test each upload right after it compiles; the platform does not say which version
played). For each version: raw wins by team size, then wins on the (opponent, map, side) keys it shares with the base
version, with losses turned to wins and wins turned to losses. Matches are cached in data/teamvers.json.
"""
import collections
import datetime as dt
import json
import os
import subprocess
import time
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, "data", "teamvers.json")


def cambc():
    base = os.path.expandvars(r"%LOCALAPPDATA%\Packages")
    for root, dirs, files in os.walk(base):
        if "cambc.exe" in files:
            return os.path.join(root, "cambc.exe")
        if root.count(os.sep) > 9:
            dirs[:] = []
    raise SystemExit("cambc.exe not found")


def run(exe, args):
    # The API rate-limits (HTTP 429, "retry after N seconds"): retry a few times before giving up.
    for k in range(8):
        r = subprocess.run([exe] + args, capture_output=True, text=True, encoding="utf-8")
        out = r.stdout.lstrip("﻿")
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            if k == 7:
                raise SystemExit(f"cambc {' '.join(args[:2])} failed: {(r.stderr or out).strip()[:300]}")
            time.sleep(20)


def fetch(since):
    exe = cambc()
    subs = run(exe, ["submissions", "list", "--json"])
    subs = subs["submissions"] if isinstance(subs, dict) else subs
    team = None
    ms, cur = [], None
    while True:
        a = ["matches", "list", "--team", "me", "--kind", "unranked", "--limit", "100", "--json"]
        if cur:
            a += ["--cursor", cur]
        d = run(exe, a)
        ms += d["matches"]
        cur = d.get("nextCursor")
        if not cur or ms[-1]["createdAt"] < since:
            break
    quota = run(exe, ["match-groups", "quota", "--json"])
    team = quota["team"]["name"]
    data = {"since": since, "team": team, "subs": subs, "ms": [m for m in ms if m["createdAt"] >= since]}
    json.dump(data, open(CACHE, "w", encoding="utf-8"))
    return data


def t(x):
    return dt.datetime.fromisoformat(x.replace("Z", "+00:00"))


def main():
    since, base_v = sys.argv[1], int(sys.argv[2])
    if "--refresh" in sys.argv or not os.path.exists(CACHE) or json.load(open(CACHE, encoding="utf-8"))["since"] > since:
        data = fetch(since)
    else:
        data = json.load(open(CACHE, encoding="utf-8"))
    subs = sorted((s for s in data["subs"] if s["createdAt"] >= since[:13]), key=lambda s: s["createdAt"])
    games = collections.defaultdict(dict)
    sizes = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for m in data["ms"]:
        tm = t(m["createdAt"])
        v = None
        for s in subs:
            if t(s["createdAt"]) + dt.timedelta(minutes=2) <= tm:
                v = s["version"]
        us = [x for x in m["teams"] if x["name"] == data["team"]]
        if v is None or not us or us[0]["result"] is None:
            continue
        us = us[0]
        op = [x for x in m["teams"] if x is not us][0]
        win = us["result"] == "win"
        games[v][(op["name"], m["map"], us["side"])] = win
        c = sizes[v][len(us["characters"])]
        c[0] += 1
        c[1] += win
    base = games.get(base_v, {})
    for s in subs:
        v = s["version"]
        if v not in games:
            continue
        g = games[v]
        raw = sum(g.values())
        by = " ".join(f"{k}:{w}/{n}" for k, (n, w) in sorted(sizes[v].items()))
        line = f"{v} {s['createdAt'][5:16]} {raw}/{len(g)} [{by}]"
        if v != base_v:
            common = [k for k in g if k in base]
            lw = sum(1 for k in common if g[k] and not base[k])
            wl = sum(1 for k in common if base[k] and not g[k])
            line += f" | paired {len(common)}: {sum(g[k] for k in common)} vs {sum(base[k] for k in common)}, L->W {lw} W->L {wl}"
        print(line, "|", (s.get("note") or "")[:80])


if __name__ == "__main__":
    main()
