---
name: battlecode-references
description: Past MIT Battlecode postmortems/code fetched for ideas (XSquare micro etc.) and where they live
metadata:
  node_type: memory
  type: reference
  originSessionId: 216f6a38-86df-4df5-8b16-c10d739a1cc4
  modified: 2026-10-19T08:10:11.735Z
---

Fetched 2026-10-19 at the user's request ("fetch winning codes from past years"):
- Postmortems: battlecode.org/assets/files/postmortem-<year>-<team>.pdf (e.g. 2026-generalized-strokes-theorem (2nd place), 2025-confused (1st seed), 2024-cout-for-clout (2nd), 2025-just-woke-up, 2022-5-musketeers).
- Code: github.com/ChiMasterBing/battlecode24 (src/waxingmoon/AttackerMicro.java = XSquare-style micro), cloned to the session scratchpad refs/.
- Common winning ideas: "XSquare micro" = score all 9 move tiles (canMove, incoming DPS, enemies targeting, min enemy distance, allies near) with a priority comparator; when the attack is ready go to an in-range tile with least incoming DPS, when on cooldown step out of every enemy's reach. Macro: copy what stronger teams do from replays; minimise idle time with idle timers; watch individual units in replays.

Applies to [[cambc-findings]] PvP work.

Process research (2026-10-19, sprint 2 prep): read 19 postmortems (2019-2026, list incl. 2023-dont-at-me, 2023-4-musketeers, 2023-gone-fishin, 2021-wololo, 2025-om-nom, 2026-lorem-ipsum; text via pdftotext). Recurring process lessons: copy stronger teams' macro from scrims, prioritise by expected win-rate gain, micro worth far more than constant tuning, reproduce opponent bots locally, auto-scrim many teams, no last-minute changes.
- Rival in OUR event (cambc2026a) has a public repo: github.com/dpark2380/cambridge-battlecode (tools/batch.py with Beta posterior + Wilson CI, docs/BatchTesting.md, tools/tune.py, tools/arena.py).

## cambc2026a rival research (2026-10-20, user: "find what people have done, spend a lot of time on that")
- `gh search repos "cambridge battlecode"` / "cambc" lists ~40 public repos. Key ones (cloned to session scratchpad refs/):
  - FHL-08/Tarot-Club-Cambc2026: docs/strategy.md (engine tricks: tribute length locks at channel start; parking on enemy spawn tiles delays respawn; enemy gem_count/is_submitting_gems readable), bots/clones/{ifish,mite,shawn,hello}-clone (measured top-4 policies, clone_config.h), issues #84 #101 #103 #53 #39 #47 #60 #113 #35 = measured top-team behaviour from ~3,300 decoded replays.
  - dpark2380/cambridge-battlecode: team ranked 18-47 (v5). bots/daniel/v8 already on SDK 3.0.1 (docs/v8/summary.md: patch breakages, cluster plan at 500 hp, monolith leave rule, boss_battle no-altar gold play); bots/jame/v3-v4 (stronger than v8); simon hunter; research/v6-improvements.md (bush killers 32%, unseen-attacker response), simon/docs/research/league_macro.md.
  - jamesrdainton-jpg/Cambridge-Battlecode research/2026-10-19/REPORT.md: pros spend gold (shop at >=150 any hp), farm in packs early, poke bosses from exactly 4, pro draft C&I/Stellar/Ren/Ryth/Varg.
  - HerbertTheBird (Pantheon) = spring 2026 winner (different game), postmortem in repo.
- Top-team policy (Tarot #84): attack-on-sight lowest hp% in range incl. spells (~220 casts/game), chase <=3 turns, recall at ~46% hp and never with an enemy within ~4 (damage cancels recall), bank at ~44 gems, shop whenever affordable (bruiser health heavy), wards ~21-28/game, opening converge then fan out. Kill mechanic = disable then focus fire; fight while withdrawing.
- Their bots are imported locally as bots/ref_dv8, ref_jv4, ref_jv3, ref_shunt, ref_dhunt, ref_sq21 (git-excluded via .git/info/exclude; never submit their code). Locally j_standht already beats dv8 26/42 and jv4 27/42, so they are weaker than the platform teams that beat us; use as a sanity filter only.
