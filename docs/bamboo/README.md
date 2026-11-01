# Bamboo Teahouse documentation

The knowledge base Bamboo Teahouse kept while building its bot (October to 1 November 2026), copied as it was. It covers the engine's
behaviour beyond the official docs, our bot's design and every switch we tested with its result, and studies of the top teams.

**Start with `knowledge/MASTER.md`**: one sheet with the goals, the toolchain, how we test, verified engine behaviour, game numbers, maps,
the top teams, our bot and the open levers. The other files are its detail.

| File | What it holds |
|---|---|
| `knowledge/MASTER.md` | the overview (read first) |
| `knowledge/engine-mechanics.md` | engine behaviour found by probes and replays: aggro and camp ties, recall and channel rules (damage cancels a recall; a recall started at a turn end counts that turn), vision, priority word, memory limits, fuel costs |
| `knowledge/champions.md` | champions, abilities, builds and how the top teams use their kits |
| `knowledge/camps-and-maps.md` | camp types and numbers, map notes and classes |
| `knowledge/glossary.md` | the team's slang (node, backing, offering, ...) |
| `knowledge/bot-overview-371.md` | how our bot is organised (turn pipeline, squads, camp scoring, fights) as of version 371 |
| `knowledge/bot-status.md` | the full experiment log: every switch, screen and ladder test with its numbers, newest at the end (large) |
| `knowledge/teammates-ports-1101.md` | 1 Nov: what this team's bot_10 / cmb1 do better, what we ported and how it measured |
| `knowledge/recall-cycle-1031.md` | the top teams' pre-started recall and clockwork farming, and our versions |
| `knowledge/top-builds-1031.md`, `fish-builds-1031.md` | top-team drafts, item builds and Intercontinental Fish's builds |
| `knowledge/top-teams-grouping-1031.md`, `top-teams-1.0.2.md` | how the top teams group, split and fight by map class |
| `knowledge/patch-2026-10-20.md`, `patch-sprint3.md` | balance patch notes and what they changed for us |
| `tools/SCREENING.md` | how we screened changes locally (the `tools/bamboo` suite is the ported version) |
| `tools/EDITS.md` | how our switches were added: one exact-text edit script per feature (`tools/edits/edit_*.py` in our repository) |

Names: the docs refer to our local build folders (`bots/B579x`, `bots/Up1472`, ...) and versions by number (#458 = Bamboo Teahouse's
version 458; v1469-v1481 = Velvet Tributers' submissions). In this repository our bots are `bots/bamboo*` (each with a README) and the test
suite is `tools/bamboo` (its README).

Most recent conclusions (1 Nov): v1472 (#458 + spell finisher) is our best proven bot. Local screens against our own bots did not predict the
ladder; against the top teams' latest bots the gap is fighting - they killed our champions 139 times to their 30 in ten games, mostly on our
own half - not farming.
