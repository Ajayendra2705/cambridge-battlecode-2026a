# Tools

Run everything from the repo root: `python -I tools/<dir>/<script>.py ...`, and run shell scripts with Git Bash. Bot names are paths under `bots/` (`main`, `pool/hb4`, `exp/x1`). Run names (`hb4l@p8s`) are the first word of each line in `results/gate.log`. The workflow that ties these together is in `docs/WORKFLOW.md`.

`cambc.ps1` wraps the `cambc` CLI, which is not on PATH: `powershell -File tools/cambc.ps1 build main --release`.

## local/ (games on this machine)

| Tool | Use |
|---|---|
| `multi.py CANDS [--pool a,b] [--maps m1,m2] [--jobs 6] [--keep]` | Every candidate vs every pool bot on every map, both sides. Default: 7 pool bots x 40 maps = 560 games per candidate. Prints wins, kills, deaths, flee deaths, margin, gold, captures, gems collected/lost/carried, and per-champion damage. |
| `rr.py BOTS [--jobs 6]` | Round robin among the given bots: win matrix and new-vs-previous rows. |
| `log.py [bundle] [regex]` | Print a team's stdout from the newest local replay bundle. |
| `allmaps.txt` | All 40 map names (default `--maps`). |

## platform/ (unranked games on the website; quota 50 groups per hour)

| Tool | Use |
|---|---|
| `gate.sh BOT [submit\|nosubmit] [RUN_NAME]` | Small gate: submit, then play 20 games (4 fixed groups of 5). Logs `RUN_NAME@p8s`. |
| `gate_full.sh BOT [submit\|nosubmit] [RUN_NAME]` | Full gate: 100 games against panel 8 (ranks 60-69). `GATE_OFFSET=N` shifts map windows. Logs `RUN_NAME@p8[@N]`. |
| `rcmp.py BASE NEW...` | Paired comparison of runs on shared (opponent, map) games: flips, margin, sign test. Caches in `data/cache/`; give every run a unique name. |
| `group.py GROUP...` | Results of match groups. Saves summaries to `data/summaries/`. |
| `panel_result.py GROUP...` | Totals (wins, gems, deaths) for a set of groups. |
| `qwait.sh [N]` | Block until N groups of quota are free. |
| `waitrun.sh RUN` | Block until every group of a run has finished. |
| `ranked.py [limit]` | Our recent ranked matches. |
| `eligible.py LADDER_JSONL RANKS` | Teams that can be scheduled (bot on the current engine). |

## variant/ (make bot copies)

| Tool | Use |
|---|---|
| `mkvar.py BASE NAME [FILE OLD NEW]...` | Copy `bots/BASE` to `bots/NAME` (use `exp/NAME`) with exact-once text substitutions. |
| `mklog.py BOT` | Add the per-turn combat log (`V` lines, source `combat_log.cpp`). Logging bots are named `...l` and never go on the ladder. |
| `mklock.py BOT [--keep N] [--enemy-only] [--cancel] [--debug]` | Add altar-lock buying and placing. |

## replay/ (analyse platform games)

Download a run first: `gdl.py RUN` writes `data/replays/platform/<run>/` (replays + `index.txt`). Scripts taking `DIR` read that folder plus the summaries in `data/summaries/`, and compare us against them.

| Tool | Use |
|---|---|
| `gdl.py RUN` | Download every match of a run. |
| `cgold.py DIR...` | Gold (also at r500), spending, gems collected, deaths per champion. |
| `cdmg.py DIR...` | Champion damage and K/D per champion. |
| `build.py "Champ,Champ" DIR...` | Item purchases per champion. |
| `fight.py DIR...` | Team metrics per game, fights (clustered deaths), who dies first. |
| `tline2.py DIR` | By outcome (win/close/blowout): collected, clears, gem losses, tributes before r600. |
| `early3.py DIR` | Deaths before r300: activity, distance from our true spawn. |
| `dact.py DIR...` | Death activity per champion (from `D` lines). |
| `acts.py DIR` | Rounds per activity per champion (from `A` lines). |
| `ehp.py DIR...` | Enemy health and count at our deaths. |
| `grp.py DIR...` | Kill participation and grouping. |
| `vana.py DIR` | Needs `V` lines: stats by 500 rounds, 1v1 damage per turn, actions. |
| `dpre2.py DIR` | Needs `V` lines: anatomy of each fatal engagement. |
| `lgold.py MULTIDIR` | Per-champion gold and damage for a local `multi.py --keep` run. |
| `agg.py RUN` / `compare_teams.py RUN...` / `killers.py RUN` / `deaths.py RUN` | Whole-run tables: per-champion averages, every metric us vs them, who kills whom, death contexts. |
| `cmp.py MATCH` / `econ.py MATCH` / `timeline.py JSON` / `summ.py JSON` | One match: economy per champion, gem sources, event timeline, metric dump. |
