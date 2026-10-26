# Tools

Run everything from the repo root: `python -I tools/<dir>/<script>.py ...`, and run shell scripts with Git Bash. Bot names are paths under `bots/` (`main`, `pool/hb4`, `exp/x1`). Run names (`hb4l@p8s`) are the first word of each line in `results/gate.log`. The workflow that ties these together is in `docs/WORKFLOW.md`.

`cambc.ps1` wraps the `cambc` CLI, which is not on PATH: `powershell -File tools/cambc.ps1 build main --release`.

## local/ (games on this machine)

| Tool | Use |
|---|---|
| `multi.py CANDS [--pool a,b] [--maps m1,m2] [--jobs 6] [--keep] [--from RUNDIR]` | Every candidate vs every pool bot on every map, both sides. Default: 7 pool bots x 40 maps = 560 games per candidate. Prints wins, kills, deaths, flee deaths, margin, gold, captures, gems collected/lost/carried, and per-champion damage. `--from` only summarises a finished run folder (same CANDS, `--pool`, `--maps`), for when the summary step failed. Map names use hyphens (`01boss-battle`). |
| `local_decode.sh RUNDIR CAND [JOBS]` | Decode one candidate's kept replays of a `multi.py --keep` run (CAND as in the file names: `main`, `exp.gw2`) into `data/fights/local_<run>_<cand>/` with an `index.txt`, so `tools/replay/decoded.py` reads local games too (about 25 s and 140 MB per 2000-round game). Local opponents are our own pool bots: use it for economy and opening metrics (`gold`, `gems`, `captures`), not fights. |
| `audit_errors.py RUNDIR` | Totals for a `multi.py --keep` run of a check build (`exp/au*`, see `docs/experiments.md`, "Code audit"): caught engine errors per call site, end-of-turn detector counts (`miss_attack_champ`, `miss_attack_camp`, `miss_cast_*`, `stuck_*`, by activity), turns that aborted (`bot error`) and turns that used their whole 100k fuel. From au14 on, check builds print each caught error once when it happens ("E" lines); those are counted per site and split by whether the turn had run out of fuel since its snapshot ("split") or had just placed a ward ("ward"), with the stage. |
| `audit_layer.patch` | The check-build layer of au17 (caught-error "E" lines, end-of-turn detectors, notes, dash traces) as a diff against `exp/fd2` (= cand6 + flee dash). To audit a candidate: copy it to `bots/exp/auN`, then in that folder `patch -p1 < ../../../tools/local/audit_layer.patch` (fix any rejected hunks by hand where the candidate differs), build with `--release`, run `multi.py --keep` and read it with `audit_errors.py`. Never ship the result: the prints cost fuel. |
| `fuel_probe.patch`, `fuel_probe.py RUNDIR` | Fuel probe layer (pf21) as a diff against `exp/fz1`: every stage records its fuel and round, and each champion prints a "PF" summary every 250 rounds for contact turns (an enemy champion within 6) and quiet turns. Copy a candidate to `bots/exp/pfN`, `patch -p1 < ../../../tools/local/fuel_probe.patch` inside it, build `--release`, run `multi.py --keep` on heavy maps (for example 01yellow-brick-road, 00swirl, 00lanes, 01elk-arena, 01starfish, 00stampede vs pool/dr3 and pool/cp3), then `fuel_probe.py` on the run folder: turns that ran out of fuel per 1000, fuel per stage, the stage that ran out. |
| `engine_probe.patch`, `engine_probe.py BUNDLE` | Engine probe (never ship), as a diff against `bots/main`'s `bot.cpp`: from round 6, slot 0 prints every champion design (base + growth), the game settings a patch may change (capture, recall, tribute timing, kill gold, lock hits) and the item table (cost, combine count, stat points, passive and magnitude), a few lines a round. Copy main to `bots/exp/ps1`, `patch --binary -p1 < ../../../tools/local/engine_probe.patch` inside it, build `--release`, run `cambc run exp/ps1 exp/ps1 --map 00ambush --rounds 40 --release -o DIR`, then `engine_probe.py DIR/*.repl26a` prints the tables and the item list for `tools/replay/decoded.py` `ITEMS`. |
| `coll_at.py RUNDIR [ROUND...]` | Gems collected by our team and the opponent by each round (default 300, 600), per candidate, from a `multi.py` run's replay timelines. The early-gem metric; matches the platform direction (gm1/ge1: +24 locally, +15 on b5). |
| `rr.py BOTS [--jobs 6]` | Round robin among the given bots: win matrix and new-vs-previous rows. |
| `log.py [bundle] [regex]` | Print a team's stdout from the newest local replay bundle. |
| `allmaps.txt` | All 70 platform map names (default `--maps` of `multi.py` and `rr.py`; 40 until 10-26). `maps40.txt` is the first 40 (quick-pool numbers before 10-26), `newmaps.txt` the 30 added later. |

## platform/ (unranked games on the website; quota 50 match groups an hour, see `docs/WORKFLOW.md`, "Platform quirks")

| Tool | Use |
|---|---|
| `gate.sh BOT [submit\|nosubmit] [RUN_NAME]` | Small gate: submit (aborts if the upload fails), then play 20 games (4 fixed groups of 5). Logs `RUN_NAME@p8s`. Override the groups with `GATE_SPECS="TEAM:m1,m2,m3,m4,m5 ..."` and the panel tag with `GATE_PANEL` (rank-30 AlphaSlop on all 40 maps: `GATE_SPECS="$(cat results/panels/specs_r30.txt)" GATE_PANEL=r30`). |
| `gateq.sh [WAIT_RUN]` | Gate queue: runs `gate.sh` for each "BOT RUN_NAME" line of `data/gate_queue.txt` in order (edit the file to reorder or add while it runs), resubmitting `main` after each (retrying through the 20-uploads-per-hour limit; a gate whose submit fails is requeued; a queued `main` gate skips the upload). Optionally waits for a running gate first. Batch panels: `results/panels/specs_bN.txt`, second map set `results/panels/specs_bNx.txt`, both together `results/panels/specs_bNc.txt`. |
| `gate_full.sh BOT [submit\|nosubmit] [RUN_NAME]` | Full gate: 100 games against panel 8 (ranks 60-69). `GATE_OFFSET=N` shifts map windows. Logs `RUN_NAME@p8[@N]`. |
| `rcmp.py BASE NEW...` | Paired comparison of runs on shared (opponent, map) games: flips, margin, sign test. Caches in `data/cache/`; give every run a unique name. Join runs with `+` to match a combined panel: `rcmp.py "A@b5+B@b6" C@b56`. |
| `sandwich.py BASE1 BASE2 NEW...` | Verdict for candidates gated between two runs of the same base (plan5 style): drops opponents whose games differ between the two base runs (they changed bots), then compares each NEW with BASE1 and with every earlier NEW on the kept games. Reads rcmp.py's cache, so run `rcmp.py BASE1 BASE2 NEW...` first. |
| `pin.py RUN@PANEL [NAME]` | Pins a panel to the opponents' bots of one run: writes `results/panels/specs_NAME.txt` (default PANEL + `p`) with the run's group ids as a fourth spec field, which `gate.sh` passes as `--source-group` (CLI 4.0.0). Games are deterministic, so RUN is the exact base of every later run on the pinned panel (no base re-runs, no dropped opponents). Refuses a run with a skipped group. Re-pin at least daily from a fresh unpinned base run. |
| `gatechain.sh PLAN [CUTOFF]` | Run gates one after another from a plan of `BOT RUN PANEL` lines (panels in `results/panels/`), through `gateq.sh`. Refuses to start while another gate runs; starts no gate after `CUTOFF` (HHMM). Run it in the background. |
| `procs.sh [kill]` | List (or stop) running gates, chains, local runs and replay decodes (also those a previous session left running). Git Bash `ps` hides command lines; this reads `/proc/PID/cmdline`. |
| `patchwatch.sh [MINUTES]` | Wait for a game patch: checks the newest `cambc` on PyPI, the `cambc` the platform publishes for download (`/api/v1/distribution`) and the engine version and build hash of the newest finished ranked match every MINUTES (default 10), and exits with one line when one of them changes (10-26: the engine moved to 2.0.0 hours before any new `cambc`). Run it in the background after patch notes are announced. |
| `adopt.sh NEW OLD_NAME` | Make `bots/exp/NEW` the ladder bot: old main to `bots/pool/OLD_NAME`, copy, one-game build check, submit main until "Submitted". Refuses while a gate runs. |
| `group.py GROUP...` | Results of match groups. Saves summaries to `data/summaries/`. |
| `panel_result.py GROUP...` | Totals (wins, gems, deaths) for a set of groups. |
| `qwait.sh [N]` | Block until N groups of quota are free. |
| `waitrun.sh RUN` | Block until every group of a run has finished. |
| `ranked.py [limit]` | Our recent ranked matches. |
| `eligible.py LADDER_JSONL RANKS` | Teams that can be scheduled (bot on the current engine). Retries listings that come back empty (HTTP 429). |
| `mkpanel.py SEED TEAM_ID...` | Panel specs for a list of teams: blocks of 4 teams, each block covering all 40 maps (two seeded 5-map windows per team), our side alternating a/b. Output goes to `results/panels/specs_NAME.txt`. |

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
| `gdl.py RUN` | Download every match of a run (8 tries per replay; run it again to fetch only the missing ones). |
| `teamdl.py NAME PER_TEAM ENGINE TEAM_ID...` | Scouting: the newest PER_TEAM ranked matches of each team on engine ENGINE (e.g. `2.0.0`) into `data/replays/platform/NAME/`, with an `index.txt` whose side and result are the listed team's (a match between two listed teams is kept once). Decode like `decode_run.sh` does (`rounds_extract.mjs`), then `decoded.py items DIR` shows that team side as "us". Team ids from `cambc ladder --json`. |
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
| `fuel_events.py RUN...` | The platform side of the code audit: `botFault` events and `fuelExhausted` events per game for us and the opponents, ours split by round (1-3 is the setup spilling over), map size and champion, from the match summaries. Group listings are retried; summaries that fail to download are skipped, so check the game count. |
| `cmp.py MATCH` / `econ.py MATCH` / `timeline.py JSON` / `summ.py JSON` | One match: economy per champion, gem sources, event timeline, metric dump. |
| `vis_decode.mjs REPLAY [POS]` | Node 22. Decodes a replay with the official visualiser engine (both teams, per-champion fog). Needs `data/vis/`: `python -I tools/replay/vis_assets.py REPLAY` fetches it from `cambc view`. |
| `decode_run.sh RUN@PANEL [JOBS]` | Download and decode a whole run into `data/fights/<RUN>_<PANEL>/` with a clean `index.txt`, ready for `decoded.py`. A decode job needs about 140 MB of RAM. |
| `decode_chain.sh JOBS RUN@PANEL...` | Beside a gate chain: waits until each run's games are all finished, then `decode_run.sh` and `fuel_events.py` on it. |
| `decoded.py CMD DIR...` | Us vs the opponents in decoded games: `gems` (collected, tributed, lost on death, bag, deaths by round), `fights` (hits, champion damage, deaths, fight-start outcomes), `channels` (tribute completion by bag size, break rate by enemies near the altar), `types` (per champion type: deaths, damage, gems, hit rate by distance), `items` (emblems per type at a round), `risk` (P(death in 10 rounds) and rounds per game by enemies, allies, health, both sides), `sources` (gems by camp type), `starts` (fight starts by champions of each side near the target; deaths by which side started the fight), `fuel` (deaths within 5 rounds after the champion's own fuel exhaustion and exhaustions in contact, from the match summaries in `data/summaries/`), `assist` (what a healthy champion does when a teammate near it is hit, and how joining or holding went), `guard` (boss_battle: round the guard first died, hits on it, tributes), `shots` (per type, with an enemy in basic reach: hit, move or stay by health and by a hit taken the round before), `captures` (group captures by region, 250-round band and killing side; clear, claim and cycle times, moves between captures), `defend` (per type, fights started on it at half health or more: hit back, move, move away, stand, die, kill), `gold` (team gold, unspent plus 30 per shard owned, by round and team size; camp kills by type with their gold and gems to the first round), `champs` (per champion type to a round: camp gold, kill gold, capture events with their base gold and gems, camp hits by camp type). Several DIRs pool. |
| `paired.py BASE_RUN NEW_RUN [ROUND]` | Pair the decoded games of two runs on (opponent, map, repeat) (opponents from `cambc match-groups show`, cached in `data/cache/mm_<run>.json`) and compare game by game: deaths, collected, tributed, lost on death, hit rounds by flip class (L->W, W->L, same), then paired mean differences with standard errors. Platform games are deterministic, so on unchanged opponents a paired difference is the sharper test than wins (a neutral change flips a quarter of the games). |
| `rounds_extract.mjs OUTDIR REPLAY...` | Node. Per-round dataset per replay (`.jsonl.gz`): every champion's state, enemies each can see, moves / attacks / casts with the entity hit, every camp's health (`mh`, by camp entity index) and camp types in the first (meta) line (`camps`). About 14 s per replay; run with `xargs -P 4`. It skips replays whose output already exists, so write to a new folder after changing it. |
| `team_features.py ranked FIGHTDIR` / `ours FIGHTDIR INDEX...` | Per-team behaviour features (tributes by r300/r600, tribute count, deaths, kills, grouping, enemy-half time, shared camp hits, bag) for winners vs losers. |
| `fight_geo.py FIGHTDIR INDEX...` | Team geometry from those datasets, us vs them by phase: distance to nearest teammate, teammates within 5, time on the enemy half, local numbers at deaths. |
| `fetch_ranked.py RANKS [--per-team N]` | Download recent ranked replays of a ladder rank range into `data/replays/ranked/`. |
| `vis_assets.py REPLAY` | Fetch the installed cambc's visualiser engine WASM and decoder JS into `data/vis/<newest engine>/` (starts and stops `cambc view`). `vis_decode.mjs` reads each replay with the folder of its engine, else the flat `data/vis/` (cambc 3.0.5, engines up to 1.0.3). |
