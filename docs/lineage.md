# Ladder lineage

Each step was the ladder bot after beating the previous one on a platform gate. Bots marked **pool** are kept in `bots/pool/` as local opponents. All others can be restored with `git checkout archive/pre-cleanup -- bots/NAME`.

Panels: `p2` ranks 30-78, `p3` top 10, `p5` ranks 30-49, `p6` ranks 75-94, `p7` ranks 40-49, `p8` ranks 60-69. `@N` = map offset. `L6`/`L7` = lost-match replays (biased, see WORKFLOW).

## Engine 2.x (to 2026-10-20)

c9 -> c12 -> c14 (Bruiser health tier, shared captures) -> c25 (max-2 capture sharing) -> c36 (XSquare-style PvP approach: step through the tile least exposed to bursts) -> c37 (cautious mode after 2 deaths; Sprint 1 entry) -> e_jung (Treasure/Monster, Durability, Jungle emblems) -> j_standht (herd-only standoff, Tavi draft).

## Engine 3.0 (from 2026-10-20)

| Bot | Change over parent | Platform evidence |
|---|---|---|
| n_rec | shop at 150+ gold, attack on sight, no recall when exposed | 26/90 |
| n_esc2 | summed camp danger, BFS path out of all camp reach, reach-avoiding walk home | camp deaths fixed |
| n_sim3 | 3-round fight simulator replaces hp*dps test | 29/90 |
| n_ast | sim includes allies; help allies' fights | 29/90, +9570 vs n_esc2 |
| n_cr | camp ranges from the API (elk 4, monolith 5) | 31/90, p=0.035 |
| n_q | quiet mode: deeper heal trips when no enemy for 30 rounds | 37/90, p=0.063 |
| n_d5 | draft without Cassi & Issac (Stellar, Ren, Tavi, Varg, HoR) | 40 vs 34 /90, deaths -30% |
| f_c1 | shield while fleeing, flee through bushes, leave when sim says we die | local |
| **c_g1** | Treasure emblem first, gold weight 0.25, travel weight 0.7 | 46/90, p=0.028 |
| **b_log** | endgame banking deadline (enemy tribute rate, k=2) | 53 vs 46 /90 |
| kc4 | online combat calibration of enemy damage (caution only) | +2816 |
| h1 | standoff only if every camp range < 4 (stampede fix) | 10 vs 6 /45, p=0.014 |
| **dv** | Vendetta instead of Heart of Ruin | 14 vs 11 /45 |
| **dm1** | top-10 meta draft: HoR, Vendetta, Vesper, Ryth, Marcella | 16/45, p=0.072 |
| pv1 | HoR on focus, Bruiser builds, shield in combat | 22/45 |
| **pd1** | duel only when we kill first (API dps) | 20 vs 16 /45, p=0.053 |
| pg5 | pgq (pb2 + order-quantity banking + gold weight 1.0 before first emblem) with opening gold weight 2.0 | p3 8 vs 5 |
| **pgq** | (pool member: base of pg5) | local 342 |
| **pw3** | bank cost charged by share of a trip (gold-only groups free) | p3 9/45, +9765 |
| **tf1** | team focus call in shared byte 7 | p=0.036 |
| **tf3** | focus call also on attack on sight | p3 9/45, p=0.023 vs pw3 |
| **ea3** | retreat counts visible enemy burst (`lethal`) + heal home at 50% when not quiet | local 355 vs 347 |
| ev1 / fx1 / fx3b / co1 | Vesper bruiser build, burst counts 2nd basic attack, big bag never fights, skip bank trips while altar guard lives, sleeping monoliths do not block neighbours | L6 25-28/40 |
| mid1 | middle groups x2 score before round 400 | L6 28/40 |
| **mid4** | middle boost only when travel <= 20 | L6 29/40, local 378 |
| **k5** | Marcella on focus | L6 29/40, local 383 |
| **ts1** | speed weights only where safe (own half or quiet) | p7 20 vs 15 /45 |
| **gb2** | capture sharing by fewest owned shards (fixes Ryth/Marcella gold starvation) | L7 23 vs 20 /45 |
| **hb4** | help call: caught champion on our half writes its position, healthy teammates within 14 come | p7@20 34 vs 29 /90 |

`hb4` is the ladder bot and `bots/main` (byte-identical, split into files).

Also in the pool: **tf1** (local default pool), **bt1** and **bt8** (best local banking variants of hb4: 405 and 410 of 560 locally, no platform gain; kept as strong local opponents).

## Lineage check

`python -I tools/local/rr.py pool/c_g1,pool/b_log,pool/dv,pool/dm1,pool/pd1,pool/pw3,pool/tf3,pool/ea3,pool/mid4,pool/k5,pool/ts1,pool/gb2,pool/hb4` plays a local round robin (6240 games) and prints new-vs-previous win rates. The first attempt was killed before finishing. It is still open.
