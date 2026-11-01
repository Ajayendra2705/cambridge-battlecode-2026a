# Bamboo test suite

The tools Bamboo Teahouse used to test its bots, ported into this repository. Everything runs from the repository root in Git Bash (Windows)
with `cambc` 4.0.0, Python 3 and Deno. Set `CAMBC` if the CLI is not at `%LOCALAPPDATA%/cambc/bin/cambc-4.0.0.exe`.

## Bots that come with it

| Folder | What it is |
|---|---|
| `bots/bamboo_dev` | the newest Bamboo source, set to v1472's configuration (#458 + `kSpellFinish 1`), `kBotVersion` 0. Every experiment switch is present and off - test new ideas here |
| `bots/bamboo458sf`, `bamboo1477`, `bamboo1478`, `bamboo1479`, ... | the exact sources submitted as those versions (each folder's README) |
| `bots/BambooPoolLive`, `BambooPoolCarry`, `BambooPoolAggro`, `BambooPoolFinish` | the local opponent pool (older Bamboo bots of different styles) |
| `bots/BambooB7Live` | the opponent for the stuck scans |

## Local screens (`local/`)

`fastscreen.py BASE "EDITS" [BASE "EDITS"]...` plays every arm against the opponents on all maps (both sides, per seed) and prints wins,
gem margin, a paired comparison with the first arm and a per-opponent split. `EDITS` are exact-text substitutions on `bots/BASE/src/bot.cpp`,
`s/old/new/` joined by `@@` (`apply_edits.py`; a substitution that does not apply fails the run).

```sh
SEEDS="1 2" OPP="BambooPoolLive BambooPoolCarry BambooPoolAggro BambooPoolFinish" \
  python tools/bamboo/local/fastscreen.py bamboo_dev "" bamboo_dev "s/constexpr int kHurtFirst = 0; /constexpr int kHurtFirst = 4; /"
```

Env: `SEEDS` (each seed replays every map; 2 seeds x 70 maps x 2 sides x 4 opponents = 1,120 games an arm), `MAPS` (a subset), `OPP`,
`JOBS` (11). Games are cached in `results/cache`; runs go to `results/ev/run<epoch>`; candidate copies are built as `bots/C<n>s<seed>` - none
of these belong in git. The teammates' bots work as opponents too (copy `bots/main` etc. to a top-level `bots/<name>` and pass the name).

**Caveat (Nov 1):** local wins did not predict the ladder. Builds of the same bot with an extra unused feature differ by +-25-35 wins of 1,120
(fuel-driven divergence), and the local opponents fight far less than today's top teams (Sponge / Mite now win fights 4 to 1 and kill
us on our own half). Use local screens to reject bad ideas and the ladder panels to accept good ones.

## Stuck scans (`ladder/widescan.sh`, `ladder/upload373.sh`)

- `widescan.sh TAG BOT EDITSFILE`: builds `bots/T<TAG>` = BOT + EDITS, plays all maps x 2 sides against `BambooB7Live` (`SCAN_OPP`) and
  prints `replay/genscan.ts`'s summary: wins, gems, walking loops, stuck episodes, champions that never left spawn, fuel-limit turns, worst maps.
- `upload373.sh N BOT "EDITS" "NOTE"`: builds `bots/Up<N>` with `kBotVersion = N` (the platform number it will get), runs a 24-game stuck scan
  (12 maps x 2 sides), and submits with the note "Bamboo NOTE" only if the scan passes. `mkmanifest.sh` writes the game lists for both.

## Ladder panels (`ladder/`)

All scrims use the team's shared quota (50 groups an hour). Games are played by whatever version is live when they run: wait until
`cambc submissions list` shows `Live: N` (a selection can take minutes to go live) and do not switch until the panel has finished.

- `queuelatest.sh TAG SPECFILE`: one 5-game group per spec line against the opponent's **current** bot; group ids go to `scrim_TAG.ids`.
- `bench2qs.sh TAG SPECFILE SRCTAG`: the same groups against the **exact opponent bots of an earlier panel** (`--source-group`, line by line
  from `scrim_SRCTAG.ids`) - same maps, sides and opponent versions, so two of our versions compare game for game.
- `allfinished.sh TAG...` waits for every game; `benchcmp.ts TAG...` prints each game and the totals; `pairsum.awk` sums a paired table.
- `quick.sh queue TAG` / `quick.sh cmp BASE TAG`: the 11-group quick panel (top 10 + Fish's newest) pinned to the 30 Oct panel.
- `latestpanel.sh`: the 1 Nov procedure - candidate against the latest bots (`queuelatest.sh`), then the baseline on those groups.
- Spec files: `bench_top10.txt` (10 top teams x 5 maps), `bench_fishnew.txt`, `bench_fish405*.txt`, `bench_x1r6.txt`, `benchB_*.txt`
  (panel B: rotated maps, flipped sides), `bench_vt1476.txt` (the panel this team ran on v1476).
- Pinned panels: `scrim_L1479_*` / `scrim_L1472_*` are the **latest-opponent panel of 1 Nov 10:15 UTC** (use it as SRCTAG); `scrim_p445f_*`,
  `scrim_p458_*`, `scrim_B458_*`, `scrim_q14*` the 30 Oct ones (opponents have changed since: v1472 21 / 50 there, 12 / 50 against the latest bots).
- `vtgroups.ts SINCE` lists this team's groups since an ISO time; `mkpanel.ts` turns a window of them into a replayable panel; `winsum.ts`
  scores live windows by version; `games.ts` one row per game.

## Replays and analysis (`replay/`, `analysis/`)

`replay/extract1.ts DIR` turns `DIR/replay.repl26a` into `DIR/trace.json` (positions, health, items, damage, income, recalls each round);
`replay/genscan.ts @LIST` is the stuck scan. `analysis/vt` compares two bots from traces (captures, banking pace, party size, deaths,
champion-time split, per-map results by spawn walk), `analysis/late` farming by phase (gems / gold mix, emblems, unspent gold),
`analysis/burst` the 31 Oct study of Intercontinental Fish's kills (`extract.ts` re-extracts with per-attacker damage).
