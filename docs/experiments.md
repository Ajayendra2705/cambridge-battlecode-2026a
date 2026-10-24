# Experiment log

One row per tested variant. Source of every deleted bot: `git checkout archive/pre-cleanup -- bots/NAME`. Variants not listed here have no recorded result; their source is in the same tag.

**Columns:** Local = wins in the standard local run (560 games: 40 maps x 7 pool bots x 2 sides) unless noted. Platform = wins/games on a panel (see `docs/lineage.md` for panel names), plus a paired comparison against the same-time base. **A** = accepted (became ladder), **R** = rejected, **N** = neutral / not adopted.

**Add a row for every new test**, accepted or not.

## Batch b4 (2026-10-24 16:25 IST): panel ranks 79-83 (we were 94): Sydney's Realist, 67 Lions, The Mania, DOOMSDAY, :3; `data/specs_b4.txt`

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| fx1 (base) | - | main on b4 | - | b4 13/25 | base |
| gm1 | dr3 | no gold-first opening: gold at the normal weight from round 0 (we out-build rivals but collect fewer gems early) | quick 185 (dr3 180) | b3 12, b4 12: 24/50 vs dr3 28 (dr3's 28 is inflated: it was chosen on these games) | retest on fresh panel b5 |
| bk4 | dr3 | bank batch capped at 25 gems before r600 (our first tribute median r279 with about 50 gems; rivals r102-130 with about 22) | quick 178 (dr3 180), gems lost 74 vs 47 | b3 11, b4 12: 23/50 vs dr3 28 | R (forced early tributes lose again, as bk1-3) |
| sh1 / sh2 | dr3 | contested group already claimed by a teammate x1.25 / x1.6 before r600 | quick 187 / - | shared camp hits locally 39% / 35% vs main 37%: metric did not move | R (not gated) |
| sh3 | dr3 | team-optimal sharing: joining k teammates on a group credits the k x (clear(k) - clear(k+1)) rounds it saves them (greedy scores ignored it). Shared camp hits locally 37% to 49% (rivals 47%; early 57% vs 59%, late 37% vs 39%) | quick 170 (dr3 180) | b3 6 vs dr3 14, b4 12 vs 14: 18/50 vs 28 | R (matching the rivals' sharing rate made us much worse) |
| c5 | - | batch b3 best | - | b4 12/25 | - |
| dr3 | - | batch b3 best (c5 + Varg for Ryth) | - | b4 14/25 | adopted as main |

## Batch b3 (2026-10-24): panel ranks 62-66 (we were 77): The Mania, cronjohn, Zkey Farming, DOOMSDAY, will think later; `data/specs_b3.txt`, second set `data/specs_b3x.txt`

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| fx1 (base) | - | main on b3 / b3x | - | b3 12/25, b3x 11/25 | base |
| fa1 | fx1 | flee toward a healthy teammate within 8 instead of home (b3: 3.5 deaths per lost game before r300, fleeing near our spawn) | quick 170, deaths +42% | - | R (local deaths) |
| rs1 | fx1 | champion ability slots read once per champion per round (enemies were read twice per turn; exact). Exhaustions -10-20% on elk_arena, lanes | quick 186 | b3 11 vs 12, b3x 12 vs 11: 23/50 = base | N |
| nm5 | fx1 | a full team keeps the early middle bonus only until an enemy has killed this champion | quick 190 | b3 13 vs 12 (1 up, 0 down), b3x 12 vs 11 (1 up, 0 down): 25/50 vs 23 | open (best) |
| nm7 | nm5 | full team drops the bonus at the first enemy sighting outside their spawn (earlier than first death) | quick 181 | b3 12, b3x 13: 25/50 = nm5 | N |
| pe1 | nm5 | before r300, 2+ enemies within 7 that outnumber us and no winning sim count as a threat (leave before they reach us) | quick 189, deaths -9% | b3 13 vs nm5 13 (0 flips), b3x 11 vs 12: 24/50 | R |
| lh3 | nm5 | prey = lowest-health enemy in reach (lh2 on fe1 was +1 on b2) | quick 192 | b3 13 vs nm5 13 (1 up, 1 down), b3x 13 vs 12: 26/50 | open (best) |
| tu2 | lh3 | contested groups (side > -3) score / (1 + this champion's deaths to enemies in the last 400 rounds) | quick 189, deaths -8% | b3 12 vs lh3 13, b3x 14 vs 13: 26/50 = lh3 | N |
| c5 | tu2 | + rs1 slot cache | quick 188; full local 399/560 | b3 13 vs lh3 13 (1 up, 1 down, margin +51/game), b3x 14 vs 13: 27/50; b4 12 vs fx1 13 | feeds dr3 |
| es2 | c5 | endgame sweep: every bag banks once the enemy has 800 tributed | quick 183 | b3 12 vs 13 (1 up: corners; 2 down), b3x 15 vs 14: 27/50 = c5 | N |
| dr2 | c5 | draft Marcella second and Vendetta last (our Vendetta 4789 damage vs theirs 13721 on b3) | quick 188, deaths -21% | b3 10 vs c5 13, b3x 11 vs 14 | R |
| nm8 | c5 | every team size keeps the early middle bonus until an enemy has killed this champion (b3 gemfight: a 4-pick enemy owned the 78-gem centre) | quick 188 | b3 13 vs c5 13, b3x 11 vs 14: 24/50 | R |
| kn1 | c5 | update_knowledge: one pass over visible camps per turn (was per seen group and per spawn; exact). yellow_brick_road knowledge stage 13k median, 30k p90 | quick 184 | b3 14 vs c5 13, b3x 11 vs 14: 25/50 | N |
| gt1 | c5 | gather the team before a contested group (side > -6) with enemies seen near it, as for big groups | quick 185 | b3 8, b3x 11: 19/50 vs c5 27 | R |
| so1 | c5 | no gold-first opening (gold at the normal weight before the first emblem) | quick 174 vs c5 188 | - | R (economy, local) |
| sp1 | c5 | no 0.7 travel discount for contested groups when enemies were seen recently | quick 180 | b3 9, b3x 12: 21/50 vs c5 27 | R (the discount helps) |
| nh1 | c5 | no help-call answering (the reverse of ec2) | quick 188, deaths -8% | b3 9, b3x 11: 20/50 vs 27 | R (the current help call is right: both wider and none lose) |
| in1 | c5 | init: reserve the group vector, read camp base stats once per kind (each read is a ~600-fuel host call); init done one round earlier on corners (exact) | quick 182 | b3 11, b3x 14: 25/50 vs c5 27 | N |
| sb1 | c5 | shop trip tributes first when an altar is within 3 (as the heal trip does) | quick 185 | b3 12, b3x 13: 25/50 vs c5 27 | N |
| co1 | c5 | support: a contested group (side > -6) scores x1.3 when a teammate's claimed group is within 10 (b3 losses: 148 of 195 flee deaths had 2-4 enemies on us); bound raised to match | quick 178 | b3 11, b3x 14: 25/50 vs c5 27 | N |
| co2 | c5 | spread penalty: a contested group with no teammate's target within 15 scores x0.7 | quick 185, deaths -6% | b3 10 vs c5 13 | R (cohesion: pk6, co1, co2 all failed to hold; factor closed) |
| vd1 | c5 | Vendetta hits the lowest-health camp first (her cooldowns reset on any credited kill, camps too) | quick 183 | b3 12 vs c5 13 (3 up, 4 down) | N |
| zf1 | c5 | routes (group fields) avoid only monolith/golem reach, not every living elk group (elks reach 4 since 3.0 and asleep hit nobody) | quick 183; walking share unchanged locally | b3 10 vs c5 13 | R |
| c6 | c5 | + vd1 + es2 (the pieces that flipped some c5 losses) | quick 184 | b3 12 vs 13 (4 up, 5 down; vd1's same flips) | N |
| dr3 | c5 | draft Varg instead of Ryth (our Ryth 6854 damage vs theirs 11207 on b3) | quick 180 | b3 **14** vs c5 13 (2 up, 1 down); b3x 13 (c5 14, fx1 11): 27/50 = c5; new panel b4 (ranks 79-83) 14 vs fx1 13, c5 12: 41/75 vs fx1 36 | **A** (main, v619; adopted below 17 by the user's call: better than fx1 on all three sets) |
| dr4 | dr3 | fifth pick Tavi instead of Marcella (buys shards anywhere) | quick 179 | b3 11 vs dr3 14 | R |
| dr5 | dr3 | Varg second (3-pick maps: Heart of Ruin, Varg, Vendetta) | quick 172 | b3 8 vs dr3 14 | R |
| dr6 | dr3 | Varg second, Vendetta fourth (3-pick maps: Heart of Ruin, Varg, Vesper) | quick 177 | b3 10 vs dr3 14 | R |
| dr7 | dr3 | + es2 endgame sweep | quick 182 | b3 11 vs dr3 14 | R |
| dr8 | dr3 | + kn1 knowledge cache (exact) | quick 178 | b3 11 vs dr3 14 | R |
| dr9 | dr3 | fifth pick Ryth instead of Marcella | quick 181 | b3 11 vs dr3 14 | R |
| dr10 | dr3 | Varg on the Bruiser build (as Ryth was) | quick 187 | b3 11 vs dr3 14 | R |
| ts2 | dr3 | no tribute start with a non-spawn enemy within 4 | quick 175 | b3 12 vs dr3 14 | R |
| sp2 | dr3 | solo opening ends at round 150 at the latest | quick 184 vs dr3 180 (same run) | - | N (noise; not gated) |
| hc8 | dr3 | answer help calls only within 8 (was 14): wider (ec2) and none (nh1) both lost | quick 186 | b3 11 vs dr3 14 | R (help radius 14 is right: wider, narrower and none all lose) |
| ab1 | dr3 | tribute any 4+ bag when an altar is adjacent | quick 180 = dr3 180 (same run) | - | N (not gated) |
| rp1 | c5 | chase a carrier from 20 gems (was 30; rival bags median 22) | quick 184 | b3 11 vs 13 (0 up, 2 down) | R |
| ec2 | c5 | help call also when 2+ enemies are within 8 on our half | quick 189 | b3 7 vs c5 13 (1 up, 7 down), b3x 12 vs 14 (combined gate b3c): 19/50 | R (wider help calls hurt, as hc2) |
| fw1 | lh3 | fleeing: when walk_home stalls at an awake camp's reach, step home anyway | quick 190 | queued | open |
| hs1 | lh3 | early rush: before r300, 2+ enemies on our half within 10 means hold the spawn (100% heal per round, enemies cannot enter) until gone 5 rounds | quick 184 | b3 10 vs lh3 13 (1 up: swirl, the target; 4 down) | R |
## Batch b2 (2026-10-24): panel ranks 83-87 (we were 98), `data/specs_b2.txt`, second set `data/specs_b2x.txt`, base fe1_b2@b2 11/25, fe1_b2x@b2x 15/25

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| pk7 | pk6 | + all team sizes before r300 | quick 157 | - | R (local floor) |
| pk6 | fe1 | small teams pack early: before r600 on teams of 4 or fewer, follow the lowest-slot teammate's target (b2 gold_rush, packs: our 3 solo farmers died to the enemy 3-stack by r40-137) | quick 186 | b2 12 vs 11 (2 up: packs, collision; 1 down: hooks); gold_rush still 4 early deaths (target-following does not keep positions together) | N |
| tpe | fe1 | tp2 teleports (b2 has 6 wall maps where rivals use them) | quick 195 | b2 14 vs 11 (6 up, 3 down: expanse, reverse_spiral, corridors); b2x 12 vs fe1 15 | R (teleports net 0 or worse over b1, b2, b2x) |
| c4 | tpe | + pk6 | quick 182 | b2 11 vs tpe 14 (0 up, 3 down) | R |
| lh2 | tpe | prey = lowest-health enemy in reach (rivals attack the weakest; our champions deal 30-100% less damage than theirs on b2 with more shards) | quick 197 | b2 15 vs tpe 14 (1 up, 0 down) | N (chain judged by fp1 on b2x) |
| fp1 | lh2 | flee test trusts the fight sim: drop the 'enemy power > 0.9x ours' clause | quick 192 | b2 16 vs lh2 15 (3 up, 2 down); b2x 10 vs fe1 15 (0 up, 5 down): 26/50 = fe1 26/50 | R (does not generalise) |
| fp2 | fp1 | outnumbered alone no longer means losing when the sim says we win | quick 192 | b2 identical to fp1 (0 flips) | N |
| bg1 | fp1 | a carrier with 20+ gems engages only if the sim says it survives (bags lost to kills: starfish 395, reverse_spiral 242, corridors 196) | quick 190 | b2 15 vs fp1 16 (0 up, 1 down) | R |
| ch1 | fp1 | chase at most 3 turns out of reach (rivals' habit) | quick 176, kills -38%, deaths -9% | b2 10 vs fp1 16 (0 up, 6 down) | R (chasing pays here) |
| fp3 | fp1 | an even sim (same deaths) counts as winning whenever our health fraction is higher (was +0.2) | quick 190, kills +13%, deaths +21% | b2 14 vs fp1 16 (3 up, 5 down) | R |
| sh1 | fp1 | fight sim horizon 5 rounds (was 3) | quick 190 | b2 10 vs fp1 16 (1 up, 7 down) | R |
| nm1 | fe1 | drop the early middle bonus (x2 for mid groups before r400) | quick 190 | b2 **17** vs 11 (7 up, 1 down, p=0.039: gold_rush, packs, fragment, collision, gemfight, contest, yellow_brick_road); b2x 12 vs 15 (2 up, 5 down) | R (fails the second map set) |
| nm2 | fe1 | keep the early middle bonus only while no enemy was seen for 30 rounds | quick 188 | b2 13 vs 11, b2x 14 vs 15: 27/50 vs 26 | N |
| fx1 | nm3 | static parts of standoff and clear_stats cached per group (exact, less pick fuel; b2 elk_arena / yellow_brick_road 88-109 exhaustions per game) | quick 188 | b2 **19** vs fe1 11 (8 up, 0 down, p=0.029); b2x 15 vs 15 (2 up, 2 down) | **A** (main, v518) |
| nm3 | fe1 | drop the early middle bonus on teams of 4 or fewer only | quick 175 of 222 (79%) | b2 16 vs 11 (5 up, 0 down); b2x 15 vs 15 (2 up, 2 down): 31/50 vs 26 | feeds fx1 |
| os1 | fe1 | until a champion's first emblem it farms only our half (side <= 0) | quick 192 (on fp1: 187) | b2x 12 vs fe1 15 (2 up, 5 down) | R |

## Batch b1 (2026-10-24): panel ranks 81-85 (we were 96), `data/specs_b1.txt`, base hb4_b1@b1 15/25, second map set `data/specs_b1x.txt`

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| cg1 | hb4 | contest together: before r600 a contested group (side >= -6) that nobody else claims is worth half | quick 181 | b1 15 vs 15 (5 up, 5 down) | R |
| fu1 | hb4 | fuel: pick_group scores a cheap upper bound per group, sorts by it and skips groups that cannot beat the best (same choices). Exhaustions road_of_riches 294 to 40 | quick 176 | b1 16 vs 15 (3 up, 2 down: boss_battle, monolith, big_world up) | open |
| fu3 | fu1 | + cache the BFS from us, refresh it on non-pick turns when we moved (travel off by up to 2). big_world exhaustions 370 to 80 | quick 171 | b1 12 vs 15 (3 up as fu1, 6 down) | R (approximate travel flips other maps) |
| cv2 | hb4 | cv1 only for clusters (no strength) beside sleeping elks | quick 175 | b1 13 vs 15 (2 up, 4 down); starvation gems 18 to 336 but still lost | N |
| fc1 | fu1 | + cv2 | quick 172 | b1 16 vs 15 (3 up, 2 down) | open |
| cr2 | cr1 | + no approach into an awake group without health for its full strength | quick 163 | - | R |
| hb4 (rerun) | - | base rerun hb4_b1b at 04:02: Shawn (rank 85) changed bot (3-2 to 0-5) | - | b1 12/25 | new base |
| fu4 | fu1 | + exact travel from per-group fields (walking distance is symmetric: the field rooted at a group's camps, read at our tile), built one per non-pick turn; no BFS per pick. 0 mismatches in 11k checks; big_world exhaustions 370 to 92 | quick 182 | b1 15 vs hb4_b1b 12 (6 up, 3 down, margin +136/game, p=0.11) | open (best) |
| cr1 | hb4 | camp retreat: rejoin only with health for the target group's remaining strength (shared by claimants) for range + 2 rounds (was: the single hardest camp) | quick 169 | b1 12 vs 12 (2 up, 2 down), margin +126/game, better 13 worse 5 | open (in c1) |
| fu5 | fu4 | tighter pick bound: live groups also need health over our best damage per round (0 violations in 22k checks). boss_battle exhaustions 140 to 62 | quick 180 | b1 14 vs 12 (5 up, 3 down); vs fu4 2 up 3 down | N |
| st1 | fu4 | steal learning: each champion counts captures it sees by us and by the enemy per group; score x (wins+1)/(wins+steals+1) | quick 180, deaths -16% | b1 13 vs fu4 15 (base 12); the sink maps did not flip | R |
| c1 | fu5 | + st1 + cr1 | quick 175 | dropped with st1 | - |
| c2 | fu5 | + cr1 | quick 172 | b1 13 vs 12 (3 up, 2 down), margin +161/game | N |
| ag3 | fu5 | altar guard counted down (150 rounds) when the enemy's tributed total rises while it looked alive (boss_battle: 1390 gems carried, 0 tributed after the enemy killed it unseen) | same as fu5 locally (local bots never kill the guard) | b1 identical to fu5 game for game (fu5 already won boss_battle) | N (untested trigger) |
| ft1 | fu4 | futility: score / (1 + rounds this champion spent on the group since it last went down / 150) | sink maps 12 vs 8 of 16, deaths -36%; quick 174, deaths -17%, caps +9% | b1 14 vs 12 (4 up, 2 down), margin +210/game, better 17 worse 8 | open |
| c3 | ft1 | + cr1 + cv2 | quick 184 | b1 15 vs 12 (3 up, 0 down), margin +196/game, deaths 121 vs 169 | open (best) |
| lke | c3 | + altar locks when an enemy is within 3 of the altar (`mklock.py --enemy-only`) | quick 181 | b1 12 vs 12 (2 up, 2 down) | R |
| dt1 | c3 | bank trip cost = detour through the altar on the way to the target (exact, from the per-group fields), not a round trip | quick 187, deaths -8%, bag losses -19% | b1 **16** vs 12 (5 up, 1 down), margin +161/game; vs c3 3 up 2 down. Second map set b1x: 11 vs hb4 9 (5 up, 3 down) | open (best) |
| hb4 (b1x) | - | base on the second map set `data/specs_b1x.txt` (05:31) | - | b1x 9/25 | base |
| tp2 | dt1 | teleport crystals: buy one per shop visit; with no enemy in view, flash to a tile within 3 that is 5+ steps nearer on the walking field (target group or altar). Rivals buy 9-17 per game on wall maps. 8-14 uses per game locally on starfish/expanse | quick 187 | b1 14 vs dt1 16 (4 up, 6 down) | R (dt1 rerun dt1b_b1 = 16, 0 flips: no drift) |
| fd1 | dt1 | + fu5's tighter pick bound (exact choices, less fuel) | quick 198 | b1 16 vs dt1 16 (2 up, 2 down); b1x 10 vs hb4 9, dt1 11 | open |
| hq1 | fd1 | low-health heal trip at 46% also when quiet (was 20%): rivals recall at about 46% | quick 193 | b1 10 vs fd1 16 (1 up, 7 down) | R |
| fe1 | fd1 | build the per-group travel fields on any non-pick turn with 50k+ fuel left (was only the turn after a pick); same choices. big_world exhaustions 75 to 37, yellow_brick_road 120 to 52 | quick 191 | b1 **17** vs hb4 12 (6 up, 1 down, margin +196/game); vs fd1 3 up 2 down; b1x 13 vs hb4 9 (6 up, 2 down); local 414/560 | **A** (main, v474) |
| dw1 | fd1 | bank trip cost minus the respawn wait of the target (the walk that fits in the wait is free) | quick 181 | b1 13 vs fd1 16 (2 up, 5 down) | R |
| pa1 | fd1 | skip a group with a fresh pack (3+ enemies) near it unless 2+ teammates head there or it is deep on our half | quick 187 | b1 14 vs dt1 16 (2 up, 4 down) | R |
| tpd | fd1 | + tp2 teleports | quick 195 | b1 14 vs fd1 16; loses fragment, elkring, broken_curve as tp2 did | R (teleports: 2 tries, both -2) |
| dt3 | dt1 | bank hazard learned per state (enemy seen within 20 rounds or not), shrunk toward the pooled rate | quick 192 | b1 14 vs dt1 16 (4 up, 6 down) | R |
| cv1 | hb4 | covered groups: a group beside sleeping elks is farmable (elks reach 4 since 3.0, so they counted as covering camps forever) | quick 166, deaths +16% | - | R (waking elks) |

## Current era: hb4 base (2026-10-23), base = hb4 384/560 local, hb4l@p8@20 38/100, small gate 10/20

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| cg1 | hb4 | contest together: before r600 a contested group (side >= -6) with no other claimant is worth half; joining keeps the mid bonus | quick 181 vs 176 /240, deaths -17% | queued | open |
| tp1 | hb4 | teleport crystal shortcut: buy one per spawn visit; out of enemy view, teleport to a tile within 3 that is 7+ steps nearer (or reachable) | quick 171 | - | R (clashes: fn1+tp1 163) |
| hm1 | hb4 | Home emblem as fourth core item (recall 3 turns) | quick 170, deaths -10% | - | in c5 |
| fn1 | hb4 | gold funnel: ready rewards that Vesper claims are hers alone (pv2 without the Power build) | quick 185 | r30 8 vs 11 /40; r70 22 vs hb4 24 /55, margin -70/game | R (local gain did not transfer) |
| fn2 / sc1 | fn1 | Vesper values gold x1.5 / single capturer (poorest one stays) | quick 178 / 174 | - | N |
| f_cg1 / f_tp1 / f_hm1 | fn1 | fn1 + cg1 / + tp1 / + hm1 | quick 181 / 163 / 182 | - | pairs for c5 |
| c3 / c4 | hb4 | cg1 + tp1 + hm1 / + fn1 | quick 178 / 166 | - | superseded by c5 |
| kt1 / eb1 | fn1 | ranged step away from an adjacent melee instead of attacking / bank 20+ gems before r400 when an altar is within 8 | quick 179 / 186 | - | N |
| es1 | hb4 | endgame sweep: bank any bag once our team has 850+ tributed or the enemy 800+ (r30 monolith 954+52 and big_world 953+93 carried were lost) | quick 178 | in c6 | see c6 |
| tu1 | hb4 | stop feeding: after 2 enemy kills of this champion within 400 rounds, contested groups (side > -3) worth a quarter | quick 171 | in c6 | see c6 |
| ec1 | hb4 | early help call: 2+ enemies within 8 also write the help call (was enemy within 3) | quick 170 | in c6 | see c6 |
| bb1 | hb4 | altar guard alive: a 200+ gem bag waits at spawn | quick 169, gold -10% | - | R (holds farming; local bots never kill the guard) |
| aslop | fn1 | local AlphaSlop imitation (Power build, funnel, early pack, Home, teleports, frequent tributes) | hb4 beats it 58/80 | map agreement with platform 16/40 | R as proxy |
| c5 | hb4 | fn1 + cg1 + hm1 | quick 179 | r30 9 vs 11 /40, margin +40/game | N |
| c6 | hb4 | es1 + ec1 + tu1 | quick 172 | r30 10 vs 11 /40 (3 up, 4 down), margin +15/game | N (base for pk3/pk4) |
| pk3 | c6 | + pack before r600 (follow lowest-slot teammate target) | - | r30 9 /40: gained packs, interlock, reverse_spiral, swirl, pilgrimage; lost 5-pick farm races | feeds pk4 |
| pk4 | c6 | + pack before r600 only when the team has 4 or fewer champions | quick 170 | r30 **13 vs 11** /40 (7 up, 5 down), margin +101/game; vs c6 5 up 2 down; r70 (ranks 70-80, 55 games) 22 vs hb4 24, margin -91/game | R for the ladder (gain is specific to AlphaSlop) |
| dr1 | hb4 | draft order HoR, Marcella, Vesper, Vendetta, Ryth (AlphaSlop order; Marcella now on 3-4 pick maps) | quick 176, margin +18% | r30 10 vs 11 /40 (6 up, 7 down), margin -53/game | N |
| pk5 / c7 | hb4 / pk4 | small-team pack on plain hb4 / pk4 + dr1 draft | quick 163 / 182 | pk5 r30 8 vs 11 (5-pick games identical to hb4: determinism confirmed) / c7 not run | R / dropped |
| fc1 / fc3 | pk4 | commit to the fight with hp > 60% when not outnumbered (hb4l p8 logs: fleeing while ahead or even died more and killed less) / + outnumbered by one at hp > 80% | quick 181 / 177 | r30 10 / 8 vs pk4 13 /40 | R (selection bias in the log statistics; platform punishes aggression) |
| fc2 | fc1 | commit also at hp > 40% when ahead | quick 173 | - | R |
| bf1 / bl1 | pk4 | bank fast: any 25+ gem bag when an altar is within 12 steps (the ruliad recipe) / + altar locks | quick 173 / 173 | bf1 r30 8 vs pk4 13 (lost the small-map pack gains) / bl1 not run | R |
| mv1 | pk4 | melee steps to a tile that still reaches the prey but takes less enemy burst after hitting | quick 169 | r30 10 vs pk4 13 (1 up, 4 down) | R |
| lh1 | pk4 | prey = lowest health in reach (was dps/hp weighted by gems) | quick 174 | r30 13 vs pk4 13 (1 up, 1 down), margin +12/game | N |
| md1 / lm1 | pk4 / md1 | middle first: x3 for groups with side in [-6, 6] within 30 steps until r600 (was x2, 20 steps, r400) / + lh1 | quick 162 / - | md1 r30 7 vs pk4 13 (2 up, 8 down, p=0.013): mid gems before r600 97 vs 109, own half 110 vs 162 / lm1 not run | R (we go to the middle but lose the fights there) |
| bd1 | hb4 | buddy pairs: slot 1 follows slot 0, slots 3 and 4 follow slot 2 (all game) | quick 143 vs 176 /240 (deaths -10%, gold -9%) | - | R (following slows farming, as pk1) |
| k5 (pool) | - | lineage check: older ladder bot vs rank-30 AlphaSlop | - | r30 10 vs hb4 11 /40 (4 up, 5 down) | = hb4 |
| pk1 / pk2 | hb4 | pack: follow the target of the lowest-slot teammate with an uncaptured target, before r600 / all game | 264 / 115 of 259 (stopped) | - | R (team moves too slowly) |
| pv1 | hb4 | Vesper Power strength, Marcella Power focus after the core three emblems (AlphaSlop build) | 382 | r30 5 vs 11 /40 (W->L 6, L->W 0) | R |
| pv2 | pv1 | + non-Vesper champions leave ready rewards that Vesper claims (gold funnel) | 369 | r30 9 vs 11 /40 (5 up, 7 down) | R |
| bt1 | hb4 | hazard x3 when not quiet + detour bank (gems>=10, altar within 4) | 405 | p8 40 vs 41 /100 (L8 32/75 was selection bias) | N |
| bt2 / bt3 | hb4 | detour only / hazard only | 396 / 380 | - | N |
| bt4 / bt5 / bt6 | hb4 | detour 8 gems 6 tiles / hazard x5 / x1.5 quiet x3 | 397 / 390 / 391 | - | N |
| bt7 / bt8 / bt9 | bt1 | home-heal banks if altar <= 6 / bank >= 4 gems when altar adjacent / shop trip banks first | 403 / 410 / 402 | bt8 p8@20 34 vs 38 /100 | N (banking family 74 vs 79 wins pooled) |
| bc1 | bt8 | bt7 + bt9 combined | 399 | - | N |
| bm1 | bt1 | mid bonus 1.5 (was 2.0) | 401 | - | N |
| bw1 / bw2 | bt8 | respawn-wait penalty 4/3, 6/3 | 404 / 401 | - | N |
| drw / drt / drg | bt8 | draft Willow / Tavi / Varg instead of Ryth | 339 / 393 / 392 | - | R |
| sh1 / sh2 | bt8 | shop trip at 210/120 / 110/60 gold | 403 / 369 | - | N |
| hh1 / hh2 | bt8 | heal trip below 40% / 60% (quiet 30%) | 386 / 376 | - | R |
| tr1 / tr2 | bt8 | hunt enemies channelling a tribute | 400 / 409 | - | N |
| th2 | hb4 | tr2 tribute hunt | - | p8@20 33 vs 38, p=0.11 | R |
| ag1 | bt1 | altar-guard value grows with bag | boss_battle 2/14 | - | R |
| ag2 | bt8 | whole-team guard assault from r500 | boss_battle 5/14 | - | R (monoliths kill us) |
| lk1 / lk2 / lk3 | bt1 | altar locks: every altar within 2 / only with enemy near / only to cancel a tribute | 382 / 390 / never fired | - | R locally |
| lkh | hb4 | altar locks (`mklock.py`), 9 bought per game | 382 | r30 6 vs 11 /40 (W->L 5, L->W 0); AlphaSlop still tributed 21 per game | R |
| fl1 / fl2 | bt1 | also losing when hit > 40% hp last round | 402 / 406 | - | N |
| fl3 | hb4 | fl1 rule | 385 | small gate: groups created, result unread | open |
| hl1 | bt1 | help radius 20 | 395 | - | N |
| pa1 / pa2 | hb4 | sim "winning" looser (+0.1 / -0.25 hp edge) | 371 / 362 | pa1 p8 38 vs 41 | R |
| pc1 | hb4 | engage only if prey within range+2 or finisher | - | p8 41 vs 41 | N |
| bpa1 / bpc1 | bt1 | pa1 / pc1 rules | 367 / 392 | - | R |
| bpt1 / bpt2 | bt1 | tighter: sim edge +0.35 / 1v1 race < 1.0 | 373 / 388 | - | R (current thresholds are a local optimum) |
| ga1 / ga2 | hb4 | gather threshold 100 / + when enemies near a 40-gem group | 314 / 309 | ga1 p8@20 26 vs 38, p=0.001 | R |
| gx1 / gx2 / gx3 | hb4 | gather threshold 300 / wait cap 10 / need 3 | 379 / 385 / 380 | - | N |
| fp1 | hb4 | flee path with least enemy burst exposure | 384 | p8@20 33 vs 38, p=0.20 | R (barely moved its own metric) |
| hc1 / hc2 / hc3 | hb4 | help margin 12 / help whole map / clearing own call keeps teammate's newer call | 388 / 388 / 387 | small gate 7 / 5 / 7 vs 10 /20 | R |
| lo1 / lo2 | hb4 | flee power threshold 1.2 / 1.5 (was 0.9) | 391 / 385 | lo1 8 vs 10 /20 | N |
| la1 | hb4 | allies counted within 6 (was 5) | 396 | 9 vs 10 /20 | N |
| lh1 | hb4 | flee below 30% hp (was 40%) | 389 | - | N |
| lf1 | hb4 | lo1 + la1 + lh1 | 407 | 6 vs 10 /20, -225/game | R (flee-less family rejected) |
| lf2 / lf3 / lf4 / lfb | hb4 | lf variants / lf1 + bt8 banking | 402 / 405 / 408 / 384 | - | R (family) |
| bk1 / bk2 | gb2 | bank batch cap 40 / 25 | 355 / 359 (vs gb2 366) | - | R |
| bk3 | hb4 | bank batch cap 30 | 376 | 3 vs 10 /20 | R |
| lc1 | hb4 | flee at enemy power > 0.7x ours | 385 | not tested | open |

## gb2 / ts1 era (2026-10-22 night)

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| gb1 | ts1 | capture sharing by stat-estimated wealth | 156/240 vs 150 | - | superseded by gb2 |
| gb2 | ts1 | sharing by exact owned shards | 366 | L7 23 vs 20 /45 | A |
| gb3 | gb2 | Marcella captures gem rewards alone | 388 | L7 20/45 | R (overfeeds one champion) |
| gr1 | gb2 | Ryth Bruiser strength first | 367 | - | N |
| gc1 | gb2 | core build without Jungle | 367 | L7 21/45 | R |
| hb3 / hb4 | gb2 | help call, response radius 10 / 14 | 379 / 384 | hb4 p7@20 34 vs 29 /90 | hb4 A |
| wx1 / wx3 / wx4 / wx5 / wx6 | ts1 | rooting-spell timing rules | 324 / 341 / 358 / 358 / - | wx6 L7 13 vs 12 | N |
| lg1, gb2l, hb4l | - | combat-log copies (V lines) | - | analysis runs | tool |
| ts1 | k5 | speed weights only where safe | 363 | p7 20 vs 15 /45 | A |
| ts2 / ts3 | k5 | speed only when quiet / side <= -5 or quiet | 371 / 376 | ts3 p7 run | N |
| pr1 / pr2 | k5 / ts1 | prey by burst/hp | 375 / 360 | - | R |
| tw1 / tw2 / nw1 / tn1 / tnm | k5 | travel weight 1.0 / 1.3 / wait penalty 4.0 / both / + Monster | 144 / 140 / 147 /240 | - | R (faster farming, more deaths) |
| mo1 / mo2 | k5 | Monster emblem instead of Jungle / first | 143 / 141 /240 | - | R |
| ge1 / ge2 / ge3 | k5 | opening gold weight 0.5 / 1.0+0.1 / 0+0.1 | 131 / 142 / 100 /240 | ge2 p7 15 vs 15 | R |
| bs1 | k5 | bag safety (100+ gems: no tribute with enemy within 6) | 384 | - | N |
| gp1 / bg1 | k5 | regroup when outnumbered / bs1 + gp1 | 381 / 378 | bg1 L6 25 vs 29 | R |

## k5 / mid era (2026-10-22 evening)

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| k5 / k7 / k8 / kall | mid4 | Marcella focus / vk2 dash micro / quiet heal 0.3 / all | 383 / 381 / 383 / 374 | k5 L6 29/40 | k5 A |
| k57 / k58 / k78 / mid6 | mid4 | pairwise combos / boost x1.5 | 148-158 /240 (mid4 161) | - | N |
| mid1 / mid3 | co1 | middle groups x2 / x3 before r400 | 349 / 333 | mid1 L6 28/40 | mid1 A (briefly) |
| mid4 / mid5 | mid1 | boost only travel <= 20 / x1.5 | 378 / 369 | mid4 L6 29/40 | mid4 A |
| co1 / co2 | fx3b | sleeping strong camps do not block neighbours / all camps | 397 / 377 | co1 lost-maps 5/10 | co1 base |
| rg1 | co1 | flee toward a teammate | 364 | L6 20/40 | R |
| fx1 / fx2 | ev1 | burst counts 2nd basic attack + big bag no fight | - | fx1 L6 25/40 | base |
| fx3 / fx3b | fx2 | altar-guard boost / only skip bank trips while guard lives | worse / boss_battle 5/6 | fx3b L6 25/40 | fx3b base |
| ev1 / ev2 / ev3 | ef1 | Vesper bruiser build / + Marcella focus / + quiet heal | 387 / 362 / 376 | ev1 p5 15 vs 16 /40, p6 27/45 | N |
| vb1 / mb1 / mv1 / mv2 / vm1 | ea3 | Vesper bruiser / Marcella focus / both / + quiet heal / vk2 + builds | 371 / 364 / 366 / 372 / 368 | vb1 p5 29/80 = ea3 | N |
| cb1 | ea3 | core Treasure + Durability only | 349 | - | R |
| vk1 / vk2 / vk3 | ea3 | dash micro (kite dash, gap dash) / + no travel dash near enemies / + hysteresis | 355 / 378 / 352 | vk2 p4 10 vs 8, p5 13 vs 16 | N |
| fh1 / fh2 | ea3 / vk1 | flee hysteresis | 353 / 354 | - | N |
| hb1 / hb2 | ea5 | power health shard per 2 / 1 main shards | 357 / 336 | - | R |
| ea1 / ea2 / ea3 | tf3 | lethal in retreat / heal 0.5 / both | 344 / 348 / 355 | ea3 = ladder on local evidence | A |
| ea4 / ea5 / ea6 | ea3 | heal 0.6 / quiet heal 0.3 / ea5 + fb2 | 351 / 367 / 365 | - | N |
| fb1 / fb2 / ci1 | tf3 | flee power 1.25 / duel within 20% / C&I link in prey | 340 / 345 / 346 | - | N |
| df1 / df2 | ea3 | turn and duel when fleeing is fatal (1.5x / 2.0x) | 353 / 341 | df1 p4 9/45 | N |
| ef1 / ef2 | df1 | + first strike in lone 1v1 (1.2x / 1.5x) | 371 / 370 | ef1 p4 7/45, -2141 | R (later kept inside mid4) |
| nf1 / nf2 | df1 / ef1 | never flee a lone adjacent melee | 306 / 348 | nf2 p4 5/45, -6267 | R |
| ag1-ag4 | nf2 | blind aggression variants | 250-319 | ag1 tainted | R |
| dg1 / cv1 | ea3 | leave lone contact unless winning / converge to call | 355 / 335 | - | R |
| dc1 / dc2 / dc3 | ev1 | draft swaps (C&I, Stellar) | built, not tested | - | open |

## tf / pw / pg era (2026-10-22 day)

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| tf1 | pw3 | team focus call (byte 7) | 133/240 | p3 p=0.036 | A |
| tf3 | tf1 | call on attack on sight | 135/240 | p3 9/45, p=0.023 | A |
| tf4 | tf1 | sim counts allies within 8 of prey | 134/240 | p3 7/45 | N |
| tf5 / tf6 | tf4 | responder radius 12 / stuns to focus target (bug: never fires) | 140 / 134 | - | N |
| tf7 / tf8 | tf4 | converge to called enemy / + tf3 | 148 / 125 /240 | tf8 p3 3/45, p=0.032 | R |
| pw4 / pw5 / pw6 / pw7 | pw3 | sighting penalty 0.1 / none for clusters / none < 1500 hp / exposure-scaled | - / 70.8% / 70.4% / 65% | pw4, pw5 p3 6 = pw3 | N |
| pw8 | pw3 | threatened radius max(range+2, reach+1) | 67.3% | p3 4/45 | N |
| pw9 / pw10 / pw11 / pw12 | pw3 | cohesion / pw8+pw6 / pw8+cohesion / ranged step away | - | pw9 4/45, pw10 7/45 | N |
| pw13 / pw14 / pw15 | pw3 | altar locks / Home emblem / no attack on sight when outnumbered | 127 / 139 / - | - | N |
| pw1 / pw2 | pg5 | whole-game gold weight 0.5 / 1.0 | 292 / 301 vs 309 | - | R |
| pm1 / pmx | pgq | Monster strength after Treasure (Vendetta, Marcella) / + weight 3.0 | 355 / 310 | pm1 p3 7/45 | R |
| pg1 / pg2 / pg3 / pg6 | pd1 / pgq | opening gold weight 1.0 / single capturer / skip respawning groups / weight 3.0 | 331 / 338 / 329 / 355 | - | N |
| pb1 / pb2 / pb3 / pbq | pd1 | top-10 build ratios / Vendetta Bruiser 2:1 / + Jungle / pb2 + order-quantity bank | 285 / 316 / 310 / 337 | pb1 p3 4/45 (R), pbq p3 8/45 | pbq feeds pgq |
| po1 | pd1 | solo opening until first emblem | 275 | p3 5/45 | R |
| pl1 | pd1 | altar locks | 290 | - | R locally |
| pd1q | pd1 | + order-quantity bank | 326 | p2@50 33 vs 30 | N |
| pd2 / pd3 | pd1 | stacked danger / old rule OR stacked | worse / - | pd3 = pd1 | N |
| pe1 / pk1 / pk2 / pf1 | pd1 | threat radius / escape dash / flee to ally / fight when run home futile | worse / 304 / 268 / deaths +43% | - | R |
| pv2 | pv1 | Jungle strength for Vendetta, Vesper, Marcella | - | - | N |
| dm2 | dv | draft HoR, Vendetta, Marcella, Ren, Ryth | - | 10/45, p=0.023 | R |
| dva / dm1a / dm2a | - | API fight math (burst from ability metadata) | - | dm1a gated | feeds pv1 |

## Early 3.0 era (2026-10-20 to 10-21)

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
| dvq / dvq2 / dvqs / dvc | dv | order-quantity banking / measured kill share / tribute safety / copy-top logistic | 240 / 242 / = / 158 of 420 | dvq 24 vs 22 /90 | N (local gain did not transfer) |
| dvp / dvr / dvg | dv | Vesper for Tavi / Ryth for Tavi / melee gold funnel | - | dvp 8 vs 14, dvg 9 vs 14 /45 | R |
| sv1 / fxb / fx_na1-3 | dv | Ren strength value function / dead-code audit / bisect | - | sv1 10 vs 13 | R |
| x1 / x2 / x3 / x4 | dv | melee tile with least camp exposure / skip captures / shields / nearer camps | flat | x1 contaminated | N |
| i1 | h1 | melee Jungle health first | +8k | 7 vs 11 /45, p=0.010 | R |
| m1 / m2 / m5 / m6 | kc4 | melee Monster first / fixed capture priority | worse in PvP | - | R |
| c1 / c2 / c3 | kc4 | covered_by elk fix / splash-safe AoE | worse | - | R |
| w1-w3 | kc4 | melee wait caps | +2% | - | N |
| kc1-kc12, kb1-kb3, kh4, kh5, kp/kx | k_log | calibration variants, engagement bandit, sim horizon 4-5 | kc4 best | kc4 6 vs 5 /45 | kc4 A |
| st5 | b_log | ready-stun danger zones | neutral | 41 vs 53 | R |
| r1-r7, ev05-ev20 | b_log | hazard-model target choice / EV bank rule | worse | - | R |
| b_k15 / b_k2 / b_k3 | c_g1 | endgame deadline k | k=2 best | b_log 53 vs 46 | A |
| clu2 / clu4 / cap1 / l1 / l2 | c_g1 | cluster gold x2 / x4 / single capturer / locks | flat or worse | - | N |
| c_gw15-50 / c_tre / c_tr7 / c_tr13 | f_c1 | gold weight / Treasure first / travel weight | c_g1 best | - | feeds c_g1 |
| f_shield / f_bush / f_pre / f_sha / f_away / f_dash | n_d5 | flee tweaks | f_c1 combo best | - | feeds f_c1 |
| n_brs / n_sd / n_sd2 / n_ks / n_sg / n_sf / n_dz / n_rb / n_qr | n_q | bruisers fight back / sim duels / kill secure / monolith siege / Stellar funnel / danger zones / respawn banking / Ryth draft | all worse or flat | n_qr 34/90, n_sf 38/90 | R |
| n_phantom / n_sb / n_hor / n_path2 / n_ward / n_pl / n_pg / n_pr / n_stell / n_bank | j_standht | early 3.0 feature variants | - | 19-26/90 | N |
| opt_e1 / opt_g1t / opt_best | j_standht | evolution strategy on economy constants vs starter | race 523-549 | 15-20/90 | R (overfits, kills survival) |

## Engine 2.x era (2026-10-18 to 10-20)

Variants c1-c37, e_* (e_bank20, e_fuel, e_power, e_flee, e_jung, e_jung1, e_hp, e_stand, e_prism, e_pf, e_sp), j_* (j_end, j_end2, j_goldmap, j_prism, j_standh), k_danger0/1/25, k_stall12, jc_*. Accepted: c36, c37, e_jung, j_standht. Lessons are in `docs/findings.md`. Results are in `docs/journal/findings_log.md`.

## Batch b5 (fresh panel, ranks 72-77 without 75, two 5-map windows; counters the winner's curse of b3/b4)

| bot | parent | change | local | platform | verdict |
|---|---|---|---|---|---|
| dr3 (main) | - | base | - | b5 23/50; gems 31450 vs 39536, deaths 515 vs 394 | base |
| gm1 | dr3 | no solo x2 gold weight | quick 185 | b34 24/50; b5 21/50 (dr3 23) | rejected on both panels |
| bk4 | dr3 | bank batch capped at 25 gems before round 600 | see b34 row | b34 23/50; b5 21/50 (dr3 23) | rejected on both panels: earlier banking alone does not close the gem gap |
| hp1 | dr3 | help call when an enemy is within 5 (was 3); answer from up to 22 tiles (was 14) with under 150 gems (was 100) | quick 186 | not gated | dropped: the team chose to work on gem collection only |
| ge1 | dr3 | = gm1 (gold not doubled before the first emblem) | quick 185; gems collected by r300 145 vs main 121 (coll_at.py) | b5 as gm1: r300 gems 123 vs dr3 108 (rivals 133) | gem metric up; base of ge4 |
| ge2 | dr3 | gold x0.5 before the first emblem (cluster 10 vs gem 7) | quick 181; r300 gems 137 | - | dropped: ge1 collects more |
| ge3 | dr3 | gold worth 0 before the first emblem | quick 138; r300 gems 158 but whole-game collection 971 vs 1072 | - | broken: no gold, no items, gems fall later |
| ge4 | ge1 | no mid-push x2 bonus | quick 183; r300 gems 151, r600 375 (main 121 / 345) | b5 23/50 (= dr3). Collected gems matched: r300 140 vs rivals 127 (dr3 108 vs 133), r600 319 vs 320. Tributed still behind: r300 62 vs 89, r600 200 vs 256; we lose 42 gems per game on death by r600 (rivals 12) | gem-collection gap closed; base for the tribute (conversion) work |
| ge5 | ge4 | shop trip at 250 gold (was 150) unless within 8 of spawn | quick 183; r300 150, r600 376 | - | no gain over ge4 |
| ge6 | ge4 | bk4 batch cap (25 gems before r600) | quick 168; tributed r300 90 vs ge4 71, but collected r600 354 vs 375 | - | rejected: banking more often costs collection |
