---
name: cambc-workspace
description: "Cambridge Battlecode 2026a (CAMBC) workspace setup, tooling (local test tools, platform gates), and tooling quirks"
metadata:
  node_type: memory
  type: project
  originSessionId: 216f6a38-86df-4df5-8b16-c10d739a1cc4
  modified: 2026-10-21T13:27:47.043Z
---

User competes in Cambridge Battlecode autumn 2026 (event cambc2026a, season 12 Oct - 18 Nov 2026, platform https://2026a.battlecode.co.uk, account Ajay_2705, team id 118dbffc-87ec-48a6-ac9c-dc1e371ba364). Bots live in `bots/<name>`; variants are copies made by small Python patch scripts (tools/mkvar.py or inline shutil+replace).

**Local testing (12 logical cores, use 16 jobs):**
- `python -I tools/multi.py C1,C2 --pool a,b --maps m1,...` — all candidates x pool x maps, both sides, one run-batch; prints wins, kills, deaths, flee deaths, gem margin, gold, captures, collected/lost/carried, race rounds and per-champion monster damage. Deletes replays unless `--keep`.
- `python tools/batch.py BOT starter-cpp [--maps ..]` — race vs starter (deterministic farming test); delete `replays/batch-*` afterwards.
- Local noise is large: a no-op change (removing prints) moved 80-game results by 9 wins / 5k margin. Use 168-280 game runs; local clone pools do NOT predict platform for item/draft/danger changes.
- Analysis: tools/hazard.py (death hazard fit), tools/calib.py (damage calibration), tools/simfit.py (fight sim fit), tools/fes.py / es.py (evolution strategies over params headers in bots/fp, bots/bp), tools/compare_teams.py RUN (us vs opponents, every metric), tools/killers.py, tools/deaths.py, tools/agg.py, tools/econ.py.

**Platform gates:** unranked quota = 50 GROUPS/hour (verified 2026-10-22 with `cambc match-groups quota --json`: limit 50, used counts groups, fixed window with resetsAt). A half gate = 9 groups, so ~5 gates/hour: chain gates back to back, never wait an hour. `GATE_HALF=1 bash tools/gate2.sh BOT [nosubmit]` = 45 games vs ladder neighbours ranks 30-78 on the 35-map pool, logged as BOT@p2 in tools/gate.log; it SUBMITS the bot unless `nosubmit`. Compare with `python -I tools/paired.py OLD@p2 NEW@p2 [--maps]`. Always run the baseline at the same time (opponents drift: b_log 53/90 at night vs 44/90 next afternoon). Old panel: tools/gate.sh (ranks 3-255).

**Quirks:**
- cambc CLI not on PATH: `tools/bc.ps1 <args>` (PowerShell). `cambc maps pull` refreshes maps (35 maps since 2026-10-21). `ladder --limit` max 100 (use --page 2).
- Bash heredocs turn `\n` inside Python strings into real newlines in C++ files: write C++ escapes with the Edit tool. bot.cpp/draft.cpp have CRLF line endings: patch scripts must normalise `\n` to `\r\n`.
- Background chains: never `&` inside a Bash call; use run_in_background. A wait loop that greps for `gate.sh` matches itself.
- Disk: local replays filled C: (100%) once; keep replays/ small.
- Heavy per-turn printing costs fuel and changes play (k_sim lost 18k); ship lean builds.

**Why:** avoids re-discovering tooling each session. **How to apply:** see [[cambc-status]] for current state and [[cambc-findings]] for measured facts.

- 2026-10-22: ranked matches start every 10 minutes (:00, :10, ...) and always use the currently submitted bot; unranked matches finish ~10 s after their group is created. `bash tools/gate_safe.sh gate2|gate3 BOT LADDER` waits until one minute after a ranked slot, runs the gate, and resubmits LADDER when done (guard resubmits after 470 s regardless), so test bots never play ranked games. Needs a fresh hourly quota (45 matches). Never edit a gate script while a gate is running (bash reads it incrementally).
