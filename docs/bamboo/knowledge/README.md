# Battlecode knowledge base

The up-to-date reference for Cambridge Battlecode 2026a (team Bamboo Teahouse). `../GameRules.md` is the official
handbook export (pre-patch text with marked corrections); the files here hold everything we have verified since, so
they win wherever the two disagree.

| File | What it holds |
|---|---|
| [**MASTER.md**](MASTER.md) | **Read first:** the one-sheet summary of everything verified - rules, toolchain, testing, engine facts beyond the docs, game numbers, maps, top teams, the live bot and what was tried |
| [patch-sprint3.md](patch-sprint3.md) | The Sprint 3 patch (announced Oct 26, not yet in the engine): champion nerfs/buffs, Treasure/Monster changes, seven new emblems, 30 new maps |
| [patch-2026-10-20.md](patch-2026-10-20.md) | The October 20 balance patch: every changed number, the new champion and camp, the SDK changes |
| [engine-mechanics.md](engine-mechanics.md) | Engine behaviour verified by probes or replays, including what the handbook gets wrong |
| [camps-and-maps.md](camps-and-maps.md) | Camp stats and rewards after the patch, the 21-map ladder pool, where each map's gems are |
| [champions.md](champions.md) | Draft and champion enums, the patch's champion changes, what our draft tests found |
| [top-teams-1.0.2.md](top-teams-1.0.2.md) | How the top ten play on engine 1.0.2 (Oct 21): drafts, items, gold holders, farming throughput, recalls, escapes, ganks and invasions, with the replay tools that measure them |
| [top-teams-grouping-1031.md](top-teams-grouping-1031.md) | How the top 13 group and split off on engine 2.0.0 (Oct 31, 140 top-vs-top games, all 70 maps): main-group size by map class (spawn walk <= 30 / 31-60 / > 60) and pick count, who splits first and when, what split champions earn, contact and fights, boss timing, team styles, candidate rules |
| [top-builds-1031.md](top-builds-1031.md) | The top 12's builds, 3-pick drafts and Vendetta kit use on engine 2.0.0 (Oct 31, 599 summaries + 66 traced replays): emblem lines per champion and pick count, Marcella's Health emblems, the dash trio's strength-adjusted record (-7..-11 per 100), Vendetta resets / kill refreshes / dash hits |
| [recall-cycle-1031.md](recall-cycle-1031.md) | Recall cycles, pre-started recalls and "clockwork" farming (Oct 31, 203 games: Fish's Oct 30 version, the top 13, ours): pre-start use by team, joint recalls, where champion-rounds go (walk out 28% vs 21%), light-camp captures away from the group (the clockwork), camp damage and gold income per champion; edit_clockwork.py / kEarlyRecall |
| [fish-builds-1031.md](fish-builds-1031.md) | Intercontinental Fish (rank 1) on engine 2.0.0, Oct 30-31 (739 ranked games, 437 summaries): the Oct 30 ~15:55 resubmission (204-55 after 249-231), Capture-first vs Prospector-first emblem templates by map, drafts per map and pick count, purchases, and a comparison with our #458 lines |
| [bot-overview-371.md](bot-overview-371.md) | The live bot (#371, Oct 26): draft, map reading, turn priority, farming, builds, coordination, fuel, and what is switched off |
| [bot-status.md](bot-status.md) | Bamboo7: live version, the switches that matter, what was tested and the result |
| [glossary.md](glossary.md) | Eric's terms (node, aggro, backing, offering, cheese, …) mapped to the game and the code |
| [../../tools/SCREENING.md](../../tools/SCREENING.md) | How we test changes quickly (cached local screens, ladder benches) |
| [../Reviews/](../Reviews/) | Dated code, match and strategy reviews (Oct 13–19). Historical: their numbers predate the patch |

## Keeping it current

- A fact goes here once it is **verified**: by a probe bot, a replay, or the SDK source (`sdk/cpp/cambc.h`). Note how
  it was verified and the date.
- When the game changes (patch, new engine), update `patch-*.md`, the affected tables, and mark what became outdated
  rather than deleting it silently.
- Probe bots used for verification live in `bots/` (`WallProbe*`, `AggroProbe*`, `SetProbe`); their maps are built
  with the scratchpad scripts named in each entry.
