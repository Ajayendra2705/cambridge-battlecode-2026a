# Cambridge Battlecode 2026a bot

Our C++ bot for [Cambridge Battlecode 2026a](https://2026a.battlecode.co.uk) (engine `cambc` 3.0.5). Two teams of champions farm neutral camps for gems and gold and tribute gems at altars. The first team to tribute 1000 gems wins.

**Start here:** `docs/status.md` (where we are and what to do next), then `docs/ARCHITECTURE.md` (how the bot works), then `docs/WORKFLOW.md` (how to test a change).

The ladder bot is `cp3` (`bots/main`, Sprint 2 entry, version 691). The next lock is Sprint 3, Sat 31 Oct 23:59 GMT.

## Layout

```
bots/
  main/          current best bot = ladder bot (cp3). The only bot edited in place.
  pool/          frozen past ladder bots (dr3, fx1, fe1, hb4, ...) and candidates, used as local opponents (docs/lineage.md)
  probe/         rule-probing bots (engine tables, mechanics tests)
  starter/       engine starter bots (cpp, rust)
  exp/           your temporary variants (gitignored)
tools/           scripts by purpose: local/ platform/ variant/ replay/ (tools/README.md)
results/
  gate.log       every platform test run: "RUN@PANEL group-ids" (input to rcmp.py, gdl.py, decode_run.sh)
  panels/        the opponent/map panels used for platform tests (README there)
  analysis/      saved outputs of local runs and replay analyses
docs/
  status.md      current ladder bot, deadline, next steps, mistakes to avoid, history
  ARCHITECTURE.md  bot design: files, turn pipeline, shared memory, logs, changes per version
  WORKFLOW.md    idea -> variant -> local run -> platform gate -> accept; testing lessons
  MECHANICS.md   exact engine rules and numbers (trust this over the handbook)
  experiments.md every variant tried and its result
  lineage.md     history of ladder bots
  findings.md    measured facts: us vs the rivals, platform noise, what top teams do
  reference/     handbook export (outdated numbers), C++ API, engine table dumps, map table, patch notes 2.0.0
  journal/       raw dated work logs up to 10-23 (frozen)
data/            replays, decoded datasets, summaries, local runs, caches (gitignored, data/README.md)
maps/            the 40 map files of the current pool
sdk/ cmake/ cambc.toml   engine SDK pinned to 3.0.5 (vendored, do not edit)
```

## Quickstart (Windows, Git Bash for .sh)

```
pip install cambc
powershell -File tools/cambc.ps1 build main --release                        # compile check
python -I tools/local/multi.py main --pool pool/dr3 --maps 00corners --jobs 2  # one quick local game pair
python -I tools/variant/mkvar.py main exp/try1 targets.h "OLD" "NEW"          # make a variant
python -I tools/local/multi.py exp/try1 --pool pool/b_log,pool/pd1,pool/tf3 --jobs 6   # breakage check (main 184/240)
printf "exp/try1 try1_b56 b56\nmain base_b56 b56\n" > data/plan.txt
bash tools/platform/gatechain.sh data/plan.txt > data/chain.log 2>&1 &         # 90 platform games each (submits try1!)
python -I tools/platform/rcmp.py base_b56@b56 try1_b56@b56                    # paired comparison
bash tools/replay/decode_run.sh try1_b56@b56                                   # decode the games (Node 22)
python -I tools/replay/decoded.py fights data/fights/try1_b56_b56              # us vs them: hits, damage, deaths
bash tools/platform/adopt.sh try1 old_main_name                                # adopt and submit
```

## Where is ...

| Looking for | Go to |
|---|---|
| What to work on next | `docs/status.md`, "Next steps" |
| Why the bot does X | `docs/ARCHITECTURE.md` (turn pipeline), then the file named there |
| An exact rule or number | `docs/MECHANICS.md` |
| How we compare with the rivals | `docs/findings.md`, then `tools/replay/decoded.py` on a fresh run |
| Where a turn's fuel goes | locally `tools/local/fuel_probe.patch` + `fuel_probe.py`; on the platform `decoded.py fuel` |
| Engine errors the bot catches, unused attacks | `tools/local/audit_layer.patch` + `audit_errors.py` (check builds, never submitted) |
| Whether an idea was tried | `docs/experiments.md` (names are reused across eras: read a row within its batch), then `docs/journal/status_log.md` |
| Platform results of a run | `results/gate.log` + `tools/platform/rcmp.py` |
| The teams and maps of a panel | `results/panels/README.md` |
| Old bot source | `bots/pool/NAME`, or `git checkout archive/pre-cleanup -- bots/NAME` |
