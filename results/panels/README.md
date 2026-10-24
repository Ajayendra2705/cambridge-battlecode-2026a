# Platform panels

Each `specs_NAME.txt` is a space-separated list of `TEAM_ID:map1,map2,map3,map4,map5` groups (5 games each). Run one with
`GATE_SPECS="$(cat results/panels/specs_NAME.txt)" GATE_PANEL=NAME bash tools/platform/gateq.sh`, or as a line
`BOT RUN NAME` of a plan for `tools/platform/gatechain.sh`. Runs are logged in `results/gate.log` as `RUN@NAME`.

Opponents change bots over time. A panel result is only comparable with runs made around the same time; re-run the base
(see `docs/WORKFLOW.md`, "Drift").

| Panel | Built | Teams (ladder ranks then) | Games |
|---|---|---|---|
| `b6` | 2026-10-24 23:25, we were 77 | 剑桥夜爬者, AlphaSlop, Stubborn Gold Clusters (no eligible bot since 10-25 00:00: skipped), HouseOfCoders, The Party of Heroes (ranks 60, 62-65); two 5-map windows per team covering all 40 maps | 40 |
| `b5` | 2026-10-24 18:00, we were 88 | Sydney's Realist, HouseOfCoders, ha²t, :3, umamusume (ranks 72-77 without 75); two windows each | 50 |
| `b56` | | `b5` then `b6` in one gate (90 games, one upload). `rcmp.py "A@b5+B@b6" C@b56` compares it with separate runs | 90 |
| `b4` | 2026-10-24 16:25, we were 94 | Sydney's Realist, 67 Lions, The Mania, DOOMSDAY, :3 (ranks 79-83) | 25 |
| `b3`, `b3x` | 2026-10-24 09:20, we were 77 | The Mania, cronjohn, Zkey Farming, DOOMSDAY, will think later (ranks 62-66); `b3x` = second map set | 25 + 25 |
| `b34`, `b3c` | | `b3` + `b4` in one gate; `b3` + `b3x` in one gate | 50 |
| `b2`, `b2x` | 2026-10-24 06:55, we were 98 | Brakence Fan Club, Agentic Loop Builders, Sic Mundus Creatus Est, test4, HouseOfCoders (ranks 83-87) | 25 + 25 |
| `b1`, `b1x` | 2026-10-24 03:00, we were 96 | Ninja Turtles, DOOMSDAY, Sic Mundus Creatus Est, error404, Shawn (ranks 81-85) | 25 + 25 |
| `r70` | 2026-10-23 | ranks 70-80 | 55 |
| `r30` | 2026-10-23 | AlphaSlop (then rank 30) on all 40 maps | 40 |
| `lost1` | 2026-10-25 | umamusume on 5 maps every variant lost (boss_battle, contest, gemfight, packs, concentrated_wealth) | 5 |

A new batch panel: read the ladder (`cambc ladder --page N --json`), check eligibility
(`python -I tools/platform/eligible.py LADDER_JSONL RANKS`), and pick maps so that each team's two windows together cover
the pool (seeded shuffle, see `docs/WORKFLOW.md`).
