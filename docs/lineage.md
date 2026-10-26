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
| **fe1** (2026-10-24) | hb4 + exact fuel fixes (pick_group branch-and-bound, per-group travel fields built when fuel allows), futility scoring (rounds sunk into a group lower its score), clusters beside sleeping elks farmable, camp-retreat rejoin needs health for the whole group, bank trip cost = detour via the altar | b1 (ranks 81-85) 17 vs 12 /25; b1x 13 vs 9 /25; local 414/560 (hb4 384) |
| **fx1** (2026-10-24) | fe1 + no early middle bonus for teams of 4 or fewer, static parts of standoff / clear_stats cached (exact fuel cut) | b2 (ranks 83-87) 19 vs 11 /25; b2x 15 vs 15 /25 |
| **dr3** (2026-10-24 16:56) | fx1 + early middle bonus for full teams only until killed, lowest-health prey, contested groups cost more after recent deaths, ability-slot cache, Varg drafted instead of Ryth | b3 14 vs 12, b3x 13 vs 11, b4 14 vs 13 (41/75 vs 36); below the 17/25 bar, adopted by the user's call |
| **cp3** (2026-10-25 03:09, version 689) | dr3 + gold not doubled early and no mid-push (ge4), altar-guard fixes (ab1, ab2), free hits before kiting and melee hits before fleeing (fh1, fh2), order-quantity banking with the c^2 trip cost and channel risk (ef3), items by fight-power gain (sp1, sp3), capture priority fixed and passive-aware (cp1), hurt ranged shoot and Vendetta dash-in (cp2, cp3) | same 90 games tonight (b5 + b6): 39 vs dr3g 36 (dr3 + guard fixes), b6 20 vs 15, b5 19 vs 21, margin better in 49 of 90 (p = 0.29); champion damage per game 13.4k vs the rivals' 13.8k (dr3 11.1k vs 15.3k). With b34 added (20 vs 24): 59 vs 60 of 140, a tie |
| **cand1** (2026-10-25 17:05, version 704) | cp3 + the bug-fix line bf1-bf7 from the check builds au1-au9 (dash landings, attack-reset targets, free end-of-turn hit, stale-turn guard, danger-aware local paths, route field rebuilt on monolith changes, fuel fixes) + gold-spread capture claim (wc1) + Heart of Ruin Bruiser strength term (hr1) | b56 (90 games, same session): 42 vs base1025c (cp3) 31, 18 L->W, 7 W->L, margin +100/game; cand1n (without the free hit) also 42 |
| **fd2z** (2026-10-26 02:14, version 723) | cand1 + one move per turn and occupancy re-read after our own moves, own `walk_towards`, measured local-search fuel guard (cand3); view read as packed bits and other exact fuel speed-ups, opening-turn fuel limits (cand4, cand6); `stale()` under 1000 fuel and checked before every action that follows a search (cand6, from the audit builds au14-au17); flee dash (fd2); no big-hit log line and reused fight-simulator buffers (fz1) | b3456 (plan8, 95 games against opponents that kept their bots): fd2 49 vs main1025g (cand1) 48 and cand6 41; fz1 41 vs cand6 41; paired decoded margin fd2 +18 per game, our deaths -0.8 per game; deaths after our own fuel run-out 0.00 (fz1) vs 0.29 (cand6) |
| **m4** (2026-10-26 07:50, version 734) | fd2z + gs1 on SDK 4.0.0 (engine 2.0.0) + item shard weights read once (wf1: SDK 4.0.0's 84 item types doubled `wealth_of`) + altar guards as a set of groups (ag4, 02guardians) | local 70-map quick pool 358/420 (fd2z 359), 0 bot faults, turns out of fuel after round 3 386 vs 934; 02guardians gems 1160 vs 900 per game |
| **hc2** (2026-10-26 16:17, version 761) | m4 + draft by team size (dq3: Heart of Ruin, Vesper, Marcella, Vendetta, Varg on 4- and 5-pick maps) + a lone capturer holds its capture (hc1: no re-pick, bank or shop trip for up to 8 rounds on the tile; hc2: holds against enemies while healthy and outside kill range) | pinned panel b9p (the same 120 games): dq3 44 vs main1026h 33; hc2 43 with holds left 5.8 vs 12.1 per game, captures 41.0 vs 39.4, gems collected by r1000 673 vs 634, deaths 5.6 vs 5.7 |
| **mw1** (2026-10-26 17:20, version 766) | hc2 + a respawning middle group (side -6..6) counts its wait once per round in `pick_group` instead of x4 (our side) or x2 (contested) | b9p: 47 vs hc2 43, gems collected by r1000 672 vs 673, middle captures 8.2 vs 8.2 |


`mw1` is the ladder bot and `bots/main` (submitted as version 766 on 2026-10-26 17:20 IST). Previous ladder bots: `hc2` (`bots/pool/hc2`, version 761), `m4` (`bots/pool/m4`, version 734), `fd2z` (`bots/pool/fd2z`, versions 723-733, with gs1 from 03:15), `cand1` (`bots/pool/cand1`, version 712), `cp3` (`bots/pool/cp3`, the Sprint 2 entry: version 689 at 03:09 IST and 691 at 03:30, before the lock), `dr3` (`bots/pool/dr3`), `fx1` (`bots/pool/fx1`), `fe1` (`bots/pool/fe1`), `hb4` (`bots/pool/hb4`, same wasm as the old split `bots/main`).

Also in the pool: **fh2** (candidate, never main: dr3 + gold not doubled before the first emblem, no mid-push bonus, bank past an unseen altar guard once the enemy tributes, take free hits before kiting, melee hits before fleeing; quick 194/240; platform b5 / b34 wins equal to ge4, but fewer deaths, more hits and more gems tributed on both panels; see experiments 2026-10-24 evening), **tf1** (local default pool), **bt1** and **bt8** (best local banking variants of hb4: 405 and 410 of 560 locally, no platform gain; kept as strong local opponents).

## Lineage check

`python -I tools/local/rr.py pool/c_g1,pool/b_log,pool/dv,pool/dm1,pool/pd1,pool/pw3,pool/tf3,pool/ea3,pool/mid4,pool/k5,pool/ts1,pool/gb2,pool/hb4` plays a local round robin (6240 games) and prints new-vs-previous win rates. The first attempt was killed before finishing. It is still open.
