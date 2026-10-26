# Platform panels

Each `specs_NAME.txt` is a space-separated list of `TEAM_ID:map1,map2,map3,map4,map5` groups (5 games each). Run one with
`GATE_SPECS="$(cat results/panels/specs_NAME.txt)" GATE_PANEL=NAME bash tools/platform/gateq.sh`, or as a line
`BOT RUN NAME` of a plan for `tools/platform/gatechain.sh`. Runs are logged in `results/gate.log` as `RUN@NAME`.

Opponents change bots over time. A panel result is only comparable with runs made around the same time; re-run the base
(see `docs/WORKFLOW.md`, "Drift").

A **pinned** panel (name ending in `p`) adds a fourth field to each group, `TEAM:MAPS:SIDES:GROUP_ID`: `gate.sh` passes it
as `--source-group` (CLI 4.0.0), so the opponent plays the bot version it used in that earlier match group. Games are
deterministic, so on a pinned panel the base run that supplied the group ids is the exact base for every later run: no
re-run of main, no dropped opponents. Pin again (a fresh unpinned base run, then its group ids) when the opponents' current
bots matter more than a stable comparison, at least once a day.

| Panel | Built | Teams (ladder ranks then) | Games |
|---|---|---|---|
| `b9p` | 2026-10-26 12:00 | `b9` pinned to the opponents' bots of `main1026h_b9@b9` (10:30-11:05 IST), whose games are its base | 120 |
| `b9` | 2026-10-26 04:15 | the 12 `b8` teams on the platform's 70-map pool (the 15 new `02` maps, 10 more `00` maps and adgato_gemcombat1-5 had never been in a panel; they are 43% of ranked games): `mkpanel.py` seed 9, 65 maps, 52 of the 120 games on the 30 newer maps | 120 |
| `b8` | 2026-10-26 01:00, we were 59 (1899) | Nyx, subscribe to caterpillow, Tartarus, conqueror_of_openai, Jupiter, FürFortnite, meow, smurphy, Let's LARP again, the ruliad, ha²t, Nanyang Technological University (every other rank from 18 to 40, ratings 1958-2101: the user asked for a stronger batch than `b7`); `mkpanel.py` seed 8, same layout as `b7` | 120 |
| `bb8` | 2026-10-26 01:00 | the 12 `b8` teams, one group each: boss_battle (our side a for the 1st, 3rd, ... team, b for the others) plus 4 maps of their first `b8` window | 60 |
| `b7` | 2026-10-25 22:05, we were 63 (1888.7) | umamusume, BBL, filter, 💩 Super Intelligence 💩, janestreethireusplease, geese geese go, Valenki, SquidProxyLovers, Sneaky Bush Campers, SkuBap, Bamboo Teahouse, error404 (every other rank from 40 to 62, ratings 1890-1956); `mkpanel.py` seed 7: three blocks of 4 teams, each block covers all 40 maps once, our side alternates (5 games on each side per team). The first panel with side b games | 120 |
| `bb7` | 2026-10-25 22:05 | the 12 `b7` teams, one group each: boss_battle (our side a for 6 teams, b for 6) plus 4 of their `b7` maps. For changes that act only on boss_battle (`gk1`) | 60 |
| `b6` | 2026-10-24 23:25, we were 77 | 剑桥夜爬者, AlphaSlop, Stubborn Gold Clusters (no eligible bot since 10-25 00:00: skipped), HouseOfCoders, The Party of Heroes (ranks 60, 62-65); two 5-map windows per team covering all 40 maps | 40 |
| `b5` | 2026-10-24 18:00, we were 88 | Sydney's Realist, HouseOfCoders, ha²t, :3, umamusume (ranks 72-77 without 75); two windows each | 50 |
| `b56` | | `b5` then `b6` in one gate (90 games, one upload). `rcmp.py "A@b5+B@b6" C@b56` compares it with separate runs | 90 |
| `b3456` | 2026-10-25 | `b34` then `b56` in one gate (about 140 games, one upload) | 140 |
| `b4` | 2026-10-24 16:25, we were 94 | Sydney's Realist, 67 Lions, The Mania, DOOMSDAY, :3 (ranks 79-83) | 25 |
| `b3`, `b3x` | 2026-10-24 09:20, we were 77 | The Mania, cronjohn, Zkey Farming, DOOMSDAY, will think later (ranks 62-66); `b3x` = second map set | 25 + 25 |
| `b34`, `b3c` | | `b3` + `b4` in one gate; `b3` + `b3x` in one gate | 50 |
| `b2`, `b2x` | 2026-10-24 06:55, we were 98 | Brakence Fan Club, Agentic Loop Builders, Sic Mundus Creatus Est, test4, HouseOfCoders (ranks 83-87) | 25 + 25 |
| `b1`, `b1x` | 2026-10-24 03:00, we were 96 | Ninja Turtles, DOOMSDAY, Sic Mundus Creatus Est, error404, Shawn (ranks 81-85) | 25 + 25 |
| `r70` | 2026-10-23 | ranks 70-80 | 55 |
| `r30` | 2026-10-23 | AlphaSlop (then rank 30) on all 40 maps | 40 |
| `bb` | 2026-10-25 | the 15 `b3456` teams, one group each: boss_battle plus 4 of the maps they play in `b3456` (a group needs 5 different maps). For changes that act only on boss_battle (`gk1`) | 75 |
| `lost1` | 2026-10-25 | umamusume on 5 maps every variant lost (boss_battle, contest, gemfight, packs, concentrated_wealth) | 5 |

A new batch panel: read the ladder (`cambc ladder --page N --limit 25 --json`, one line per page, into
`data/ladder_NAME.jsonl`), check eligibility (`python -I tools/platform/eligible.py LADDER_JSONL RANKS`), then
`python -I tools/platform/mkpanel.py SEED TEAM_ID... > results/panels/specs_NAME.txt`.

Until `b7`, every panel game had us on side a (the default of `match-groups create`). A game's result depends on the
side too, so those panels sampled half of the possible games. Our ranked games 10-25 (57 with summaries): side a 14/25,
side b 20/32.
