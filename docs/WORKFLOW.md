# Workflow: from idea to ladder

All commands run from the repo root. Python scripts run with `python -I`. On Windows, run shell scripts with Git Bash (`"C:\Program Files\Git\bin\bash.exe"`). In PowerShell, `bash` is WSL, which has no Python.

## Setup

- Install the CLI: `pip install cambc`. It is not on PATH; every tool calls it through `tools/cambc.ps1` or the full path in the Python scripts (`%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_...\Scripts\cambc.exe`). If your path differs, change it in one place per script (search `cambc.exe`).
- `powershell -File tools/cambc.ps1 login` once, then `... maps pull` to refresh `maps/`.
- Engine version is pinned in `cambc.toml` (`sdk_version`). After a CLI upgrade, run `cambc init` in a scratch folder and copy `sdk/` and `cmake/` across.
- Build check: `powershell -File tools/cambc.ps1 build main --release`. Bot names are paths under `bots/` (`main`, `pool/hb4`, `exp/x1`).

## The loop

1. **Find the factor.** Compare us with the teams just above us on the platform: download a panel run (`tools/replay/gdl.py RUN`), then run `cgold`, `cdmg`, `fight`, `tline2` and `early3`. Pick the one factor where we lack most. Name a **target metric** (for example "flee deaths per game") before writing code.
2. **Make a variant.** `python -I tools/variant/mkvar.py main exp/NAME FILE "OLD" "NEW" [...]`. Each OLD must match exactly once. For logging, also run `tools/variant/mklog.py exp/NAME` (the convention is to add the suffix `l`).
3. **Debug it locally.** Add temporary prints, run one game, and confirm the rule fires. Then remove the prints.
4. **Local run.** `python -I tools/local/multi.py exp/A,exp/B --jobs 6`. The default is all 40 maps x 7 pool bots x 2 sides = 560 games per candidate. Compare with the base on the same run. Current base `main` is `fx1` (2026-10-24); `pool/fe1` scores 414/560 (`pool/hb4` 384). For a quicker breakage check use `--pool pool/b_log,pool/pd1,pool/tf3` (240 games, about 43% of the time): `main`/`fx1` scores 188/240 there (`fe1` 191, `hb4` 176). Add `pool/fe1` with `--pool` to test against the previous ladder bot.
5. **Platform small gate** (about 20 games): `bash tools/platform/gate.sh exp/NAME` submits the bot and plays 4 fixed groups of 5. Run it back to back with the base, giving the base run a unique name each time (see rcmp trap below): `bash tools/platform/gate.sh main submit base_s5`.
6. **Compare.** `python -I tools/platform/rcmp.py BASE@p8s NEW@p8s` pairs games by (opponent, map) and prints wins, flips (L->W, W->L), margin per game and a sign-test p-value. Also check the target metric in the replays.
7. **Decide.** Accept only if the platform result is better and the target metric moved. Copy the winner over `bots/main` and move the old main into `bots/pool/`. Add one row to `docs/experiments.md` for every variant tested, accepted or not, then delete `bots/exp/NAME`.
8. **Ladder.** `powershell -File tools/cambc.ps1 submit main`. The bot submitted at the Sprint lock time is the tournament bot.

## What the evidence says about testing

- **Local results do not predict the platform for fighting.** The local pool is our own old bots. Changes that make us fight more (pa1, lf1, hc2, k_danger0) won locally and lost on the platform. Changes to items, draft and danger settings also failed to transfer. Use local runs as a filter against breakage, and for economy-only changes.
- **Platform games are nearly deterministic.** The same bots on the same map give the same score. A same-bot rerun 1.5 h later flipped 0-3 of 20 games. Run-to-run drift (about 10 of 100 games) comes from opponents changing their bots, so always run the base at the same time. Against a single opponent that did not resubmit, the base is exactly repeatable: hb4 vs AlphaSlop gave identical 40-game results 2.5 h apart (hb4_a and hb4_b @r30).
- **Code changes flip games chaotically.** A pure bug fix (hc3) went 2 up, 5 down. A 20-game gate is noisy: treat ±3 wins as noise and look at the margin and flips.
- **Never pick games by past result.** Replaying only the games we lost (the "lost-match spec") showed big gains that vanished on the full panel (bt1: 32/75 on the lost set, 40/100 vs 41/100 full). That was regression to the mean.
- **Local noise:** a no-op change (removing prints) moved 80-game results by 9 wins. Trust 560-game runs, and treat differences under about 10 wins as noise.
- **Optimisers overfit.** Tuning constants against the starter bot (`opt.py`, deleted) produced a bot that scored 15/90 on the platform.

## Platform quirks

- Upload limit: **20 bot submissions per hour** (HTTP 429). A gate plus the main resubmit is 2 uploads, so at most about 10 gates per hour. `gate.sh` aborts when its submit fails (otherwise the games run with whatever bot is on the platform), and `gateq.sh` requeues that gate and retries the main submit until it succeeds. A combined gate over both map sets (`data/specs_bNc.txt`, 10 groups) tests a variant with one upload. A queued gate of `main` itself skips the upload (main is already on the platform). Never edit `gateq.sh` while it runs: bash reads scripts as it goes.
- Unranked quota: 50 match groups per hour. A group must have exactly 5 maps. `tools/platform/qwait.sh N` waits for N free groups.
- Gates submit the bot. Never run two gate chains at once, because the second submission replaces the first bot mid-gate.
- Run names in `results/gate.log` are `BOT@PANEL[@OFFSET] groupid...`. Panels: `p8` = full panel (`gate_full.sh`, 10 teams at ladder ranks 60-69 on 2026-10-23), `p8s` = small gate. `GATE_OFFSET` shifts the map windows of the full panel. Opponent team ids are inside the gate scripts. Refresh them when the ladder moves.
- **rcmp cache trap:** `rcmp.py` caches results per run name in `data/cache/res_<run>.json` and reads the last `gate.log` line with that name. Reusing a name (`hb4l@p8s` twice) silently reuses the old result. Give every base run a unique name, or delete the cache file.
- Opponent teams without a bot for the current engine cannot be scheduled ("doesn't have an eligible bot", HTTP 409). The gates skip them.
- Platform stdout in replay bundles is NUL-padded per turn. Strip `\0` before splitting lines.
- Ranked matches run every 10 minutes with the currently submitted bot. Each gate puts a test bot on the ladder for its whole run, so a day of gating costs rating (2026-10-24: rank 76 to 82 between 11:30 and 15:15 while main itself was unchanged). Near a lock, gate less and leave main submitted.

## Local quirks

- Copying a bot with `cp -r` also copies `.cambc/`, which breaks the build. `mkvar.py` skips it.
- After editing a bot, if the build looks stale, delete `bots/X/.cambc`.
- Local replays fill the disk fast (a 560-game run with `--keep` writes several GB). `multi.py` deletes replays unless `--keep`. Clear `data/runs/` regularly.
- Heavy runs get killed when RAM is low. Use `--jobs 6`.
- Some source files use CRLF line endings. Patch scripts must keep them (`mkvar`, `mklog` and `mklock` do).
- `init_world` spreads over the first rounds (fuel). For init debug prints, run 40+ rounds.

## Team rules

- One factor at a time: list every gap against the teams above, pick the largest, and stay on it until matched.
- Before each step, ask whether it is needed and how the idea could be better.
- Prefer measured or learned formulations over hand-tuned constants.
- Platform tests are about 20 games (small gate) unless a result needs confirming.
- Ladder rating does not matter during testing. Bot quality does. Submit `main` again after tests if the deadline is near.
