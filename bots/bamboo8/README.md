# bamboo8 (Bamboo Teahouse G3, platform version 1469)

Eric's best bot from the Bamboo Teahouse project, uploaded to Velvet Tributers as **v1469** on 31 Oct 23:02 UTC. The source is
exactly what was submitted: every switch is baked into the `constexpr` values near the top of `src/bot.cpp`. Build it with
`cambc build bamboo8` from the repository root.

## What it is

The Bamboo live bot #458 plus six changes, each a switch in `src/bot.cpp`:

| Switch | What it does |
|---|---|
| `kSightCache`, `kPairWalkCache`, `kScoutWindow` | fuel caches that leave every decision unchanged (out-of-fuel turns -26% on all 70 maps) |
| `kGemLate 3` | past 3 emblems a champion values gold less (fading to 0.04 gems a gold piece), so late-game routes favour gem camps |
| `kEarlyRecall` | the top teams' pre-started recall: start a recall at the turn end when the next turn would head home anyway |
| `kFieldFirst` + `kFieldFirstGuard` + `kFieldFirstStill 6` | a path field step() could not afford is built first next turn, only after 6 rounds stuck within one tile (fixes the 01islands stall) |
| `kSpellFinish 1` | at the turn start, a ready single-target damage spell finishes the weakest visible enemy champion under 30% health or within the spell's damage (copied from Intercontinental Fish's Marcella) |

## Results

Local screens against four pool bots, 2 seeds x 70 maps x 2 sides x 4 opponents (1,120 games), margin vs #458: G3 -1 +-20 on seeds
1-2, +12 +-20 on seeds 3-4. `kSpellFinish 1` alone: +32 +-18 and +9 +-18. All 70 maps x 2 sides vs the Oct 18 bot: stuck / loop
rounds 443 vs #458's 1,016; no map with 100+.
