# Cambridge Battlecode 2026a bot

Our C++ bot for [Cambridge Battlecode 2026a](https://2026a.battlecode.co.uk) (engine `cambc` 3.0.5). Two teams of champions farm neutral camps for gems and gold and tribute gems at altars. The first team to tribute 1000 gems wins.

**Start here:** `docs/status.md` (where we are), then `docs/ARCHITECTURE.md` (how the bot works), then `docs/WORKFLOW.md` (how to test a change).

## Layout

```
bots/
  main/          current best bot = ladder bot. The only bot edited in place.
  pool/          frozen past ladder bots, used as local opponents (docs/lineage.md)
  probe/         rule-probing bots (engine tables, mechanics tests)
  starter/       engine starter bots (cpp, rust)
  exp/           your temporary variants (gitignored)
tools/           scripts by purpose: local/ platform/ variant/ replay/ (tools/README.md)
results/
  gate.log       every platform test run: "RUN@PANEL group-ids" (input to rcmp.py, gdl.py)
  analysis/      saved outputs of local runs and replay analyses
docs/
  status.md      current ladder bot, deadline, next steps
  ARCHITECTURE.md  bot design: files, turn pipeline, shared memory, logs
  WORKFLOW.md    idea -> variant -> local run -> platform gate -> accept; testing lessons
  MECHANICS.md   exact engine rules and numbers (trust this over the handbook)
  experiments.md every variant tried and its result
  lineage.md     history of ladder bots
  findings.md    measured facts, what top teams do
  reference/     handbook export (outdated numbers), C++ API, engine table dumps, map table
  journal/       raw dated work logs (search here for details behind any result)
data/            replays, summaries, local runs, caches (gitignored, data/README.md)
maps/            the 40 map files of the current pool
sdk/ cmake/ cambc.toml   engine SDK pinned to 3.0.5 (vendored, do not edit)
```

## Quickstart (Windows, Git Bash for .sh)

```
pip install cambc
powershell -File tools/cambc.ps1 build main --release                    # compile check
python -I tools/local/multi.py main --pool pool/hb4 --maps 00corners --jobs 2   # one quick local game pair
python -I tools/variant/mkvar.py main exp/try1 targets.h "OLD" "NEW"     # make a variant
python -I tools/local/multi.py exp/try1 --jobs 6                         # 560-game local run (base hb4 = 384)
bash tools/platform/gate.sh exp/try1                                     # 20 platform games (submits the bot!)
python -I tools/platform/rcmp.py BASE@p8s try1@p8s                       # paired comparison
powershell -File tools/cambc.ps1 submit main                             # put the best bot back on the ladder
```

## Where is ...

| Looking for | Go to |
|---|---|
| Why the bot does X | `docs/ARCHITECTURE.md` (turn pipeline), then the file named there |
| An exact rule or number | `docs/MECHANICS.md` |
| Whether an idea was tried | `docs/experiments.md`, then `docs/journal/status_log.md` |
| Platform results of a run | `results/gate.log` + `tools/platform/rcmp.py` |
| Old bot source | `git checkout archive/pre-cleanup -- bots/NAME` |
