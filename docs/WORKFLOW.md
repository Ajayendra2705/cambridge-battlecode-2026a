# Workflow: from idea to ladder

All commands run from the repo root. Python scripts run with `python -I`. On Windows, run shell scripts with Git Bash (`"C:\Program Files\Git\bin\bash.exe"`). In PowerShell, `bash` is WSL, which has no Python.

## Setup

- Install the CLI: `pip install cambc`. It is not on PATH; every tool calls it through `tools/cambc.ps1` or the full path in the Python scripts (`%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_...\Scripts\cambc.exe`). If your path differs, change it in one place per script (search `cambc.exe`).
- `powershell -File tools/cambc.ps1 login` once, then `... maps pull` to refresh `maps/`.
- Engine version is pinned in `cambc.toml` (`sdk_version`). After a CLI upgrade, run `cambc init` in a scratch folder and copy `sdk/` and `cmake/` across.
- Build check: `powershell -File tools/cambc.ps1 build main --release`. Bot names are paths under `bots/` (`main`, `pool/hb4`, `exp/x1`).

## The loop

1. **Find the factor.** Compare us with the teams near us on the platform. Decode a panel run (`bash tools/replay/decode_run.sh RUN@PANEL [JOBS]`, Node 22, about 4 minutes for 50 games at the default 3 jobs; see "Local quirks" for more). Count the decoded games against the run's games: on 10-25 a fifth to two fifths of each run's replays failed to download while gates ran, until `gdl.py` got retries; running `gdl.py RUN` again fetches only the missing files and measure us vs them with `python -I tools/replay/decoded.py CMD data/fights/RUN_PANEL` (`gems`, `fights`, `channels`, `types`, `items`, `risk`, `sources`). The older summary tools (`cgold`, `cdmg`, `fight`, `tline2`, `early3` on `gdl.py` downloads) still work. Pick the one factor where we lack most. Name a **target metric** (for example "champion damage per game by r800") before writing code.
2. **Make a variant.** `python -I tools/variant/mkvar.py main exp/NAME FILE "OLD" "NEW" [...]`. Each OLD must match exactly once. For logging, also run `tools/variant/mklog.py exp/NAME` (the convention is to add the suffix `l`).
3. **Debug it locally.** Add temporary prints, run one game, and confirm the rule fires. Then remove the prints.
4. **Local run.** `python -I tools/local/multi.py exp/A,exp/B --jobs 6`. The default is all 40 maps x 7 pool bots x 2 sides = 560 games per candidate. Compare with the base on the same run. Current base `main` is `cp3` (2026-10-25): 406/560 (`pool/dr3` 391, `pool/fe1` 414 on an older pool run, `pool/hb4` 384). For a quicker breakage check use `--pool pool/b_log,pool/pd1,pool/tf3` (240 games, about 43% of the time): `cp3` scores 184/240 there (`dr3` 180, `fx1` 188, `hb4` 176). Local runs do not judge fight, item or banking changes; check those with decoded platform replays (`docs/findings.md`). Add `pool/fe1` with `--pool` to test against the previous ladder bot.
5. **Platform gate.** Use a batch panel from `results/panels/` (README there), ideally `b56`-style combined panels of about 90 games in one gate (one upload). Write a plan of `BOT RUN PANEL` lines and run `bash tools/platform/gatechain.sh PLAN [CUTOFF]` in the background: it runs the gates one by one and refuses to start while another gate runs. Put a base line `main base_NAME PANEL` in the same plan (main is not uploaded again), because opponents change bots over the day. Give every run a unique name (rcmp trap below). The old small gate (`gate.sh exp/NAME`, 20 games against panel 8) still works but is too small to decide anything.
6. **Compare.** `python -I tools/platform/rcmp.py BASE@PANEL NEW@PANEL` pairs games by (opponent, map) and prints wins, flips (L->W, W->L), margin per game and a sign-test p-value. Separate runs can be joined to match a combined panel: `rcmp.py "A@b5+B@b6" C@b56`. Then decode both runs and compare the target metric with `decoded.py`.
7. **Decide.** Accept only if the target metric moved and the wins are not worse beyond noise (about 3 wins per 50 games between two variants; see "What the evidence says"). Write the decision rule down before the result comes in. `bash tools/platform/adopt.sh NEW OLD_NAME` moves the old main to `bots/pool/OLD_NAME`, copies `bots/exp/NEW` over `bots/main`, build-checks and submits it. Add one row to `docs/experiments.md` for every variant tested, accepted or not, then delete `bots/exp/NAME`.
8. **Ladder.** `powershell -File tools/cambc.ps1 submit main`. The bot submitted at the Sprint lock time is the tournament bot.

## What the evidence says about testing

- **Local results do not predict the platform for fighting.** The local pool is our own old bots. Changes that make us fight more (pa1, lf1, hc2, k_danger0) won locally and lost on the platform. Changes to items, draft and danger settings also failed to transfer. Use local runs as a filter against breakage, and for economy-only changes.
- **Platform games are nearly deterministic.** The same bots on the same map give the same score. A same-bot rerun 1.5 h later flipped 0-3 of 20 games. Run-to-run drift comes from opponents changing their bots, so always run the base at the same time. Against a single opponent that did not resubmit, the base is exactly repeatable: hb4 vs AlphaSlop gave identical 40-game results 2.5 h apart (hb4_a and hb4_b @r30). **Drift check:** re-run a bot that changes little (or main) and count identical game scores. On 10-25, dr3g matched dr3's b6 run from 3 hours earlier in 29 of 40 scores but its b5 run from 9 hours earlier in only 19 of 50 (b5 score 23 became 21).
- **50-game panels are noisy.** Eight near-identical variants on the same 50 b5 games: 17 games lost by all, 7 won by all, 26 swing; about 2.2 wins of chance per run, about 3 between two variants. A change that rarely fires leaves almost every game identical (rg1 vs fh1: 1 of 50 changed), so the noise comes from changes that alter behaviour broadly. Decide with continuous decoded metrics (damage, deaths, gems tributed and lost) and with games every variant loses.
- **Code changes flip games chaotically.** A pure bug fix (hc3) went 2 up, 5 down. A 20-game gate is noisy: treat ±3 wins as noise and look at the margin and flips.
- **Never pick games by past result.** Replaying only the games we lost (the "lost-match spec") showed big gains that vanished on the full panel (bt1: 32/75 on the lost set, 40/100 vs 41/100 full). That was regression to the mean.
- **Local noise:** a no-op change (removing prints) moved 80-game results by 9 wins. Trust 560-game runs, and treat differences under about 10 wins as noise.
- **Optimisers overfit.** Tuning constants against the starter bot (`opt.py`, deleted) produced a bot that scored 15/90 on the platform.

## Platform quirks

- Upload limit: **20 bot submissions per hour** (HTTP 429). A gate plus the main resubmit is 2 uploads, so at most about 10 gates per hour. `gate.sh` aborts when its submit fails (otherwise the games run with whatever bot is on the platform), and `gateq.sh` requeues that gate and retries the main submit until it succeeds. A combined gate over both map sets (`results/panels/specs_bNc.txt`, 10 groups) tests a variant with one upload. A queued gate of `main` itself skips the upload (main is already on the platform). Never edit `gateq.sh` while it runs: bash reads scripts as it goes.
- Unranked quota: 50 match groups an hour. From 2026-10-25 a refused creation reads "Your team can start 50 unranked matches an hour" (HTTP 429, with a retry time); on 10-23/24 it acted like 50 per rolling 30 minutes. The window is a rolling hour: each group frees its slot 60 minutes after it was created, and `resetsAt` is when the oldest counted group ages out, not a full reset (10-25: at 20:40 used 50, resetsAt 20:55:45; at 21:01 still used 50, resetsAt 21:09:52). `cambc match-groups quota --json` shows `limit`, `used` and `resetsAt`. A group must have exactly 5 different maps ("Choose exactly five different maps", HTTP 400, for 5x boss_battle on 10-25); `--sides a,b,a,b,a` sets our side per game. A b3456 gate (140 games) is 28 groups, so under two fit in an hour: size a chain to the quota (six such gates take about 3.5-4 hours). `gate.sh` retries a refused creation every 30 s. `tools/platform/qwait.sh N` waits for N free groups. Other teams can also queue unranked games against us; those use their quota.
- Gates submit the bot. Never run two gate chains at once, because the second submission replaces the first bot mid-gate. In Git Bash, `ps` does not show command lines, so find and stop gates with `bash tools/platform/procs.sh [kill]`. Near a lock, stop every gate in time and make sure the last upload is main (after `gateq.sh` the last upload always is).
- Run names in `results/gate.log` are `BOT@PANEL[@OFFSET] groupid...`. Panels: `p8` = full panel (`gate_full.sh`, 10 teams at ladder ranks 60-69 on 2026-10-23), `p8s` = small gate. `GATE_OFFSET` shifts the map windows of the full panel. Opponent team ids are inside the gate scripts. Refresh them when the ladder moves.
- **rcmp cache trap:** `rcmp.py` caches results per run name in `data/cache/res_<run>.json` and reads the last `gate.log` line with that name. Reusing a name (`hb4l@p8s` twice) silently reuses the old result. Give every base run a unique name, or delete the cache file.
- Opponent teams without a bot for the current engine cannot be scheduled ("doesn't have an eligible bot", HTTP 409). The gates skip them.
- Platform stdout in replay bundles is NUL-padded per turn. Strip `\0` before splitting lines.
- Ranked matches run every 10 minutes with the currently submitted bot. Each gate puts a test bot on the ladder for its whole run, so a day of gating costs rating (2026-10-24: rank 76 to 82 between 11:30 and 15:15 while main itself was unchanged). Near a lock, gate less and leave main submitted.

## Local quirks

- Copying a bot with `cp -r` also copies `.cambc/`, which breaks the build. `mkvar.py` skips it.
- After editing a bot, if the build looks stale, delete `bots/X/.cambc`.
- Local replays fill the disk fast (a 560-game run with `--keep` writes several GB). `multi.py` deletes replays unless `--keep`. Clear `data/runs/` regularly, but never while a run is writing there (that lost most of a 560-game run on 10-25).
- Heavy runs get killed when RAM is low. The machine has 12 threads and 16 GB, usually 3-5 GB free. On 10-25 the quick pool at `--jobs 11` took 135 s with free RAM 0.4 GB lower, and gave the same result as at 6 jobs. Decoding (`decode_run.sh RUN 10`) needs about 140 MB per job (10 jobs: 3.1 GB free fell to 1.7 GB). Do not run both at full width at once. With under 2 GB free, use `--jobs 6`.
- The disk fills with run outputs: on 10-25 `data/summaries` (1 MB per platform game) held 20 GB and `data/runs` 11 GB, with 5 GB left on C:. Check `df -h /c` before long runs.
- Some source files use CRLF line endings. Patch scripts must keep them (`mkvar`, `mklog` and `mklock` do). Git Bash `sed -i` writes a CRLF file back with LF endings (10-26, `docs/experiments.md`), and its `grep` does not see the `\r`: edit such files with the editor, or with Python in binary mode.
- `init_world` spreads over the first rounds (fuel). For init debug prints, run 40+ rounds.

## Team rules

- One factor at a time: list every gap against the teams above, pick the largest, and stay on it until matched.
- Before each step, ask whether it is needed and how the idea could be better.
- Prefer measured or learned formulations over hand-tuned constants (fit the constant on decoded platform games, write the fit next to the code).
- Judge fight, item and banking changes with decoded platform metrics, not local runs or 50-game win counts alone.
- Platform tests: batch panels of 40-90 games since 10-24 (a 20-game small gate is within noise; use it only as a quick check).
- Ladder rating does not matter during testing. Bot quality does. Submit `main` again after tests if the deadline is near.
