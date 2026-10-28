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
| **cc2** (2026-10-27 00:05, version 796) | mw1 + carrier caution: a champion with 30+ gems never engages and counts any threat as a lost fight (the `big_bag` bar was 150) | b11p (paired to r1000): gems lost on death 141 to 80 per game, deaths -0.4, tributed +58; 7 vs 7 wins |
| **dh3** (2026-10-27 03:41, version 831) | cc2 + dash routes over one-tile hole lines, switched on per map only where they shorten the walk from our spawn to the altar by 40+ steps (road_of_riches, shortcut, concentrated_wealth, fracture); identical to cc2 on every other map | new pinned panel bhp (those four maps and gemfight against the ten b11p and b12p opponents): 20 vs 10 of 50 wins, tribute margin on the four maps +290 per game, our deaths +2.5 and theirs +2.8; gemfight games identical |
| **cw1** (2026-10-27 05:38, version 838) | dh3 + the big-group wait (`camp_fight.h`) runs once per group life: main restarted its 25-round count after every approach step, so a lone champion crawled one step per 26 rounds towards an undamaged group of 200+ strength | bvp 19 vs 16 and bhp 20 vs 20 of 50; idle off camps and enemies on the maps with such groups -2.7 +- 0.6 per 100 alive rounds (paired); gems collected by r1000 +5.4% over both panels, deaths equal |
| **cr3** (2026-10-28 00:50, version 974; first live as v964 and v968 on 10-27) | cw1 + dm1 (death marks in `pick_group`) + hw1 (no help call with three or more enemies within 6 of the caller) + mr1 (Marcella does not root herself while losing) | b13p 23 vs 23 of 50 (our deaths 396 vs 442, theirs 303 vs 329); b10p 33 vs 44 of 105, where cw1's base is a lucky draw (every child of cw1 lost there by 6-11). Ranked: 14 of 25 in its two windows on 10-27, main 23 of 55 after it. Rejected by its panel rule at 23:10 (kills -0.44 per game), adopted on the user's call at 00:50 ("Do what is best") after a losing run under cw1: at worst equal on the panels, so the switch costs nothing |
| **go1** (2026-10-28 06:27, version 985) | cr3 + turn order: each turn a champion sets its priority for the next round (`set_priority`), so a champion within 5 of a visible enemy acts before its teammates, the most hurt first; we had never set it, so our turns always ran in draft order while 19 of the 21 top teams reorder | brkp (paired to r1000, 100 games): ours first in contact 0.729 against 0.455, our deaths -1.1 +- 0.4, theirs +0.9 +- 0.4, collected +13%, tributed +14%, 17 vs 14 wins; b13p guards held: our deaths +0.0, collected 97.2%, tributed 98.4%, 22 vs 23 wins |


`go1` is the ladder bot and `bots/main` (submitted as version 985 on 2026-10-28 06:27 IST). Previous ladder bots: `cr3` (`bots/pool/cr3`, version 974, resubmitted by each gate up to 984), `cw1` (`bots/pool/cw1`, version 838, resubmitted by each gate up to 973), `dh3` (`bots/pool/dh3`, version 831, resubmitted by each gate up to 837), `cc2` (`bots/pool/cc2`, version 796, resubmitted by each gate up to 830), `mw1` (`bots/pool/mw1`, version 766, resubmitted by each gate up to 795), `hc2` (`bots/pool/hc2`, version 761), `m4` (`bots/pool/m4`, version 734), `fd2z` (`bots/pool/fd2z`, versions 723-733, with gs1 from 03:15), `cand1` (`bots/pool/cand1`, version 712), `cp3` (`bots/pool/cp3`, the Sprint 2 entry: version 689 at 03:09 IST and 691 at 03:30, before the lock), `dr3` (`bots/pool/dr3`), `fx1` (`bots/pool/fx1`), `fe1` (`bots/pool/fe1`), `hb4` (`bots/pool/hb4`, same wasm as the old split `bots/main`).

Also in the pool: **fh2** (candidate, never main: dr3 + gold not doubled before the first emblem, no mid-push bonus, bank past an unseen altar guard once the enemy tributes, take free hits before kiting, melee hits before fleeing; quick 194/240; platform b5 / b34 wins equal to ge4, but fewer deaths, more hits and more gems tributed on both panels; see experiments 2026-10-24 evening), **tf1** (local default pool), **bt1** and **bt8** (best local banking variants of hb4: 405 and 410 of 560 locally, no platform gain; kept as strong local opponents).

## Lineage check

`python -I tools/local/rr.py pool/c_g1,pool/b_log,pool/dv,pool/dm1,pool/pd1,pool/pw3,pool/tf3,pool/ea3,pool/mid4,pool/k5,pool/ts1,pool/gb2,pool/hb4` plays a local round robin (6240 games) and prints new-vs-previous win rates. The first attempt was killed before finishing. It is still open.
