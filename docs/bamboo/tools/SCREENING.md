# Testing bot changes faster

How we screen Bamboo7 changes since the October 20 balance patch, when games grew from roughly 400–700 rounds to
1,300–2,000 and a full local screen started taking hours on a 12-thread Ryzen 5 5600.

## 0. `tools/fastscreen.py` (use this from October 21)

Same candidates, cache and summary as `tools/evaluatec.sh` below, but driven from Python with one `cambc run-batch`
process instead of a `cambc run` per game from Git Bash. Measured on this PC (Oct 21):

| What | Games per second |
|---|---|
| `evaluatec.sh` (shell: ~10 helper processes per game at ~0.1 s each under Git Bash, plus a polling loop) | 0.9 |
| `fastscreen.py`, full games | **3.1** |
| `fastscreen.py` with `ROUNDS=800` (games stopped at round 800) | **6.8** |

What did not help: `--release`, `--log-limit 0` and more than ~4 parallel jobs change nothing by themselves; a game
costs ~0.15 s plus ~0.55 ms a round once the compiled-module cache (`CAMBC_WASMTIME_CACHE`) is warm. The shell's
process launches were the whole difference.

```sh
# full games, all 35 pool maps, B7Live and B7Base (defaults), seed 1
python3 tools/fastscreen.py B7Dev "" B7Dev 's/kFoo = 0;/kFoo = 1;/'
# fast reject filter: games stopped at round 800, margin = banked gems there
ROUNDS=800 python3 tools/fastscreen.py B7Dev "" B7Dev 's/kFoo = 0;/kFoo = 1;/'
# options: MAPS="00corners 01shortcut" OPP="B7Live B7Base Opp95" SEEDS="1 2" JOBS=11 KEEP=1 KEEPTMP=1
```

**When the cut-off is trustworthy.** Checked on the 35-map screen of Oct 21 (6 candidates, 210 paired games each),
comparing each candidate's paired difference from the base at rounds 600–1200 with the full games
(`scratchpad/ft/cutoff.py`): every candidate that lost in full games also lost at round 800–1000, usually with a
higher z-score (Heart of Ruin in every draft −76 ± 31 in full games, −37 ± 11 at round 800; siege −53 ± 32 and
−47 ± 12; dash-saving −29 ± 12 and −8 ± 3). But a **late-game gain is invisible early**: lone casters staying home
was +60 ± 26 in full games and +3 ± 12 at round 1000. So: run `ROUNDS=800` to throw losers out, and confirm anything
that survives with full games. The cut-off needs `kReportRound` in the source (`tools/edits/edit_report.py`;
B7Dev and Bamboo7 have it): candidates print both teams' banked gems just before the cut-off, because games stopped
early write no statistics file.

**Keep the base cached.** The base candidate's games come from the cache only while its source is unchanged; every
code addition (even a switch that is off) changes the binary. Batch new switches into the dev base, run the base once,
then screen several candidates against it.

**What a local screen cannot judge (Oct 21).** The local opponents are our own code, so a farming fault we share with
them is invisible: on 01yellow_brick_road v205 idles at spawn for ~100 rounds and loses 0/6 on the ladder, yet beats
B7Live locally because B7Live idles too. For farming changes also compare our income per map with the top teams' own
games: `tools/stress/localrun.py BOT B7Live OUTDIR` (both sides, all maps, bundles kept), `behaverun.py` + `behave.ts`
on OUTDIR, then `mapbench.py TOP.jsonl OURS.jsonl BOT` (median gold by r300/r600 and banked gems by r600/r900 per map;
the top teams' rows come from `behave.ts` on downloaded top-vs-top replays, `.info/knowledge/top-teams-1.0.2.md`).
Two games a map are noisy (±30% per map); read the sums.

**Run manifest (from Oct 22).** Every fastscreen run writes `results/ev/run<t>/manifest.json`: git HEAD and the
number of modified tracked files, the cambc path and version, SEEDS/MAPS/OPP/ROUNDS/JOBS, each candidate's base, edits,
seed, per-file source hashes and wasm hash, a zip of its edited source (`C<i>-src.zip`), the opponents' source and
wasm hashes, and every map with its hash. Quote the run directory with any screen result.

**Check what a bench actually ran.** Each upload copy prints `BAMBOO vN` on its first turn (`kBotVersion`): read it from
the downloaded bundles (`team-a.stdout`/`team-b.stdout`) before comparing benches. On Oct 21 the bench queued while v205
was the latest upload played **v203** (all 40 games), and ranked games switched between v205 and v203 during the day.
Also compare benches only on the same engine (`engineVersion` in the match listing: 1.0.1 until 05:20 UTC Oct 21, then
1.0.2).

## 1. Cached local screens (`tools/evaluatec.sh`)

`tools/evaluatec.sh` is `tools/evaluate.sh` with a game cache (`tools/sweepc.sh`); `tools/fastscreen.py` (section 0)
replaces it.

- **Why it works:** builds are byte-identical (the same source gives the same `.wasm`, whatever the bot's folder name),
  and local games are deterministic (the same two compiled bots, map and side always play the same game).
- **What it caches:** every finished game's log, in `results/cache/`. The key is the engine version, both bots' `.wasm`
  hashes, the map and the side. Bot names in the stored log are placeholders, so a cached game serves any candidate
  name (`C1s1`, `C2s1`, …).
- **Effect:** the baseline config (and any config whose compiled bot hasn't changed) costs nothing after its first run.
  A 2-config screen gets about 50% cheaper and a 4-config screen about 25%.
- **Importing older runs:** `tools/cacheimport.sh RUNDIR HASHFILE` adds an uncached run (from `evaluate.sh`). It needs
  the `.wasm` hashes of the run's bots, recorded while the `C*s*` builds still exist (`evaluate.sh` deletes them at the
  end).
- **Invalidation:** the cache key includes the `cambc --version` string, so a new engine starts a fresh cache. Delete
  `results/cache/` if in doubt; it's regenerable.

Usage (same as `evaluate.sh`):

```sh
export CAMBC="$LOCALAPPDATA/cambc/bin/cambc-3.0.4.exe"   # the exe path, never the bare name (no cambc on PATH: every build fails)
MAPS="00ambush 00collision ... 01islands" OPP="B7Live B7Base Opp95" SEEDS="1" JOBS=11 \
  sh tools/evaluatec.sh Bamboo7 "" Bamboo7 's/kFoo = 0;/kFoo = 1;/'
```

## 2. One seed first

Run a new idea on **one seed** (21 maps × 2 sides × 3 opponents = 126 games per config) and add a second seed only
for configs that look promising. Most rejected ideas were obvious after the first 126 games (boss mode −322, early
siege −353, Willow drafts −376). Promising ones get seeds 2+ to confirm, and the cache keeps the earlier seed's games.

## 3. Benches

- **Local opponents:** `B7Live` (a frozen copy of the live code; refresh it whenever a new version goes live), `B7Base`
  and `Opp95`. We win about 55%, 65% and 80% against them. The old Castery/Hunter6/Mitey set is too weak (~96%).
- **Ladder bench** (runs on the platform's servers, not this PC): **only against the current top 10** (some other teams
  run troll submissions: Univardisty of Shingtonwash handed us 20/20 wins on Oct 21) and **against two teams only**
  (Eric, Oct 21 05:15: the match quota does not stretch further). The standard bench is `bench_np.txt`: Nyx and
  procless (both top 10) × four groups of five old maps = **8 groups, 40 games**, about 10 minutes; deterministic
  baselines exist for every version since v197. `bench_top.txt` (top three, 12 groups) is kept for reference only.
  The quota is a **rolling 60-minute window of 50 groups** (shared with the team): group creation stalls until old
  groups age out. Only the live submission can be scrimmed, so each candidate goes live while it's measured; keep the
  better one live afterwards, and when the 40 games tie (under ~3,000 margin) let the local screen decide.
- **The local screen does not predict the ladder for play changes (Oct 21).** v201, v203 and v204 each gained
  locally (+20 to +48 on 35 maps, up to three seeds) and each lost ground on the ladder against Nyx and procless
  (v200 6/40 → v203 5/40 → v204 3/40). The local opponents are our own older code; a change in fighting, positioning
  or party structure can beat them without beating a top team. Treat the local screen as a filter for regressions and
  bugs, and let the two-team ladder bench (or replay evidence from top-team games) decide what stays live.
- **Disk:** `results/cache/` holds every cached local game (1.6 GB on Oct 21; keyed by engine, both bots' wasm hashes and
  the map) and only speeds up repeat screens: safe to delete when space matters. `results/ev/run*/` (per-screen
  summaries), `replays/`, `tools/stress/out/` and experiment copies under `bots/` are regenerable and were cleared on
  Oct 21 (keep the tracked bots plus Champ, Mimic*, B7Live, B7Base and the current dev/live copies).
- **Determinism:** a ladder match is played within seconds of the group's creation and is fully determined by the two
  submissions and the map: v200's 100 games at 03:00 and at 04:00 on Oct 21 were identical game by game. So a repeated
  bench of unchanged versions is a free consistency check, not new information, and a baseline only needs re-running
  when an opponent resubmits or the engine changes (watch `engineVersion` in `cambc match-groups show GROUP --json`).
- **Noise:** with games re-randomised, a 40-game ladder sum moves by about ±2,700 margin. Even 80 games are coarse: on
  Oct 20 the paired difference between two versions had a standard error of 2,500–3,300 margin, and v190 moved −2,197 on
  maps where its behaviour equals v189's. The ladder bench only catches effects of ~5,000+ margin (or 4+ wins of 80);
  for smaller changes the local screen decides, and the ladder bench is a guard against large regressions.
- **Back to back:** benches an hour apart differ by more than most changes (v188's −20,666 at 06:30 vs the same
  behaviour's −23,663 at 08:23). Re-bench the baseline right next to the candidate.

## 4. `cambc run-batch` (cambc 3.0.1)

`run-batch MANIFEST --jobs N` runs many matches from a text manifest
(`"botA-dir" "botB-dir" "map" "out.repl26a" --statistics "out.stat"`, absolute paths). Each replay bundle holds both
teams' stdout, so it also serves trace runs (e.g. a `kTraceMap` copy printing every map's profile).

- **Same games as `cambc run`:** 01islands MapDbg vs B7Live gave the same winner and final round (B7Live, round 1014)
  both ways (Oct 20).
- **Same speed:** one game took 4.7 s with `cambc run`; 21 games took 16 s with `run-batch --jobs 8`. It only saves
  writing the parallel loop. `--release` builds like the platform (no debug blocks); not needed for screens.
- **Screens are fast again:** a 2-config screen against a cached baseline (252 new games, 11 jobs) took 7.5 minutes on
  Oct 20 (the treasure screen, 07:53–08:01 UTC).

## 5. Stress maps (unseen terrain)

Sprint maps are new to every team, and Sprint 1 broke us on four of them (corridors, the_farm, boss_battle, islands).
Before a sprint, run the bot on generated maps it has never seen:

- `scratchpad/ft/mapgen.ts BOOTREPLAYDIR OUTDIR FIRSTSEED COUNT` draws random maps with the engine's own map builder
  (`MapBuilder_*` exports reached through any replay): mazes, rooms with doors, hole rivers with 1- and 2-tile gaps,
  islands, bush fields and altar bush rings, walled pockets with one entrance, diagonal walls, camps inside corridors,
  dead ends; sizes 28-90, 3-5 champions, either symmetry. Symmetry 0 mirrors x, 1 mirrors y, and the builder mirrors
  what you add. Maps whose spawns cannot walk to each other are redrawn. `OUTDIR/gNNNN.txt` holds an ASCII view.
- `scratchpad/genrun.sh BOT TAG "OPP1 OPP2"` plays BOT against each opponent on every generated map, both sides, via
  `run-batch`, then `ft/genscan.ts` reports per game: gems, deaths, walking loops (16 rounds on at most 4 tiles while
  moving), stuck episodes (30+ rounds on one tile), guarding, champions that never left spawn, and fuel-limit turns.
  Rounds spent fighting a camp, capturing or channelling are not counted as loops or stuck.
- 40 maps x 2 sides x 2 opponents = 160 games: ~3 minutes to play, ~10 minutes to scan.
- Oct 20 baseline (v193 code): 96 stuck episodes (7,256 rounds), 295 loops (3,791 rounds), one map at 9% gem share
  (every camp too big: the squad idled 2,000 rounds). See `.info/knowledge/bot-status.md` for the fixes.

## Pitfalls

- **Disk:** `results/ev/run*` keeps every screen's logs (25–100 MB each). 314 runs filled C: on Oct 20 and killed a
  screen. Prune old runs; they're regenerable.
- **cambc 3.0.1:** `match-groups create` needs `--json` and prints compact JSON (`{"groupId":"..."}`).
- **Ineligible teams:** teams whose submission doesn't compile against the new SDK get "no eligible bot (HTTP 409)";
  skip them (Intercontinental Fish after the patch).
- **One screen at a time, and not right after another:** every run copies its candidates to the same `bots/C<i>s<seed>`
  names and deletes them when it finishes. A second run that starts while the first is still cleaning up (or still
  running) loses its copies mid-game: games fail with `bot does not exist: bots\C2s1`, the summary shows
  `INCOMPLETE: N failed/missing` or `BUILD FAILED C2s1`, and whole maps have no candidate games (Oct 21, three times).
  Check for those strings before reading a screen. Killing a screen: its games are `sweep.sh` processes whose
  arguments name the run directory; confirm the directory before `pkill -f`.
- **Running scripts:** never edit a shell script that a running screen is executing (`sh` reads it as it goes); write a
  new file instead.
- **Fuel side effects:** a switch that adds work to every turn can change games on maps where it never acts, because
  fuel-dependent scheduling shifts. Keep per-turn checks cheap, and test where the behaviour is meant to matter.

## 4. Judging an upload: ranked games by version, not the top-team bench (October 21)

The Mite + procless bench (`bench_pm.txt`) loses every version by ~500 a game, so it cannot separate versions that differ
against teams at our rating: v224 and v225 benched the same (6/40) but went 18/30 and 4/20 in ranked games. It did see
the draft change (v229: 7/40, -15,789 vs v228's 5/40, -20,412 on the same games). So after every upload:

```sh
DETAIL=1 python3 tools/stress/ratinghist.py                      # one line per ranked group: time, rating, wins of 5, opponent
# list the matches since a time from the match-groups API (see scratchpad rk_since*.tsv in bot-status), then
python3 tools/stress/dlmatches.py LIST replays/rkDATE 3           # download with our logs
# split by the "BAMBOO vN" banner in team-<side>.stdout (our version prints it on its first turn)
```

Forty ranked games (~80 minutes) resolve about ±150 a game. Keep the bench for the deterministic like-for-like economy
profile (`tools/stress/benchprof.py TAG1 TAG2`).
