# Experiment log

One row per tested variant. Source of every deleted bot: `git checkout archive/pre-cleanup -- bots/NAME`. Variants not listed here have no recorded result; their source is in the same tag.

**Columns:** Local = wins in the standard local run (560 games: 40 maps x 7 pool bots x 2 sides) unless noted. Platform = wins/games on a panel (see `docs/lineage.md` for panel names), plus a paired comparison against the same-time base. **A** = accepted (became ladder), **R** = rejected, **N** = neutral / not adopted.

**Add a row for every new test**, accepted or not.

## Current era: hb4 base (2026-10-23), base = hb4 384/560 local, hb4l@p8@20 38/100, small gate 10/20

| Bot | Parent | Change | Local | Platform | Verdict |
|---|---|---|---|---|---|
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
| lkh | hb4 | altar locks (`mklock.py`) | killed mid-run | not tested | open |
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
| fq1 | main | learned engage decision (ml/ FightQ v1, 1 model, 2.3k params) replaces the hand rules whenever an enemy is within max(range,4) | 60 games (3 pool bots x 10 maps x 2 sides): 19 wins vs main 34, deaths 1153 vs 565. 10x fuel: 19 vs 43 | not gated | R |
| fq2 | fq1 | 5-model ensemble; acts only when all 5 agree on engage vs stay (42% of decisions offline), else hand rules | 15/60 (fuel exhaustion: 301 vs 13 turns in one game). 10x fuel: 33 vs main 43 | not gated | R |
| fq3 | fq1 | commitment: keep engaging unless Q gap < -0.1 std (flip rate offline 11% -> 5%) | 17/60. 10x fuel: 19 | not gated | R (no effect) |
| fq4 | fq2 | gate + commitment | 8/60. 10x fuel: 32 | not gated | R |
| fq5 | fq1 | FightQ with simulate_fight outputs + hand-rule verdict as features and a team-id embedding (our team's) to adjust for confounding | 16/60 (main 34), deaths 1010 vs 565 | not gated | R |
| fq0 | fq5 | control: all model plumbing runs, decision always from the hand rules | 35/60, deaths 569 (= main) | - | control: plumbing is clean, losses come from the model's decisions |
| rf1 | main | learned reinforcement prediction (ml/reinforce_*, expected new enemies within 6 tiles in 7 rounds) added to the flee rule: enemy_count + expected > ally_count | 34/60 (main 34), deaths 538 vs 565, margin +1678 vs +2715; turns at fuel limit 2x main | not gated | N |
| rf2 | rf1 | count one extra enemy only when P(arrival) > 0.5 (rate > ln 2) | 32/60, deaths 540, margin +4707 | not gated | N |
| rf3 | main | two-head model (enemy and ally arrivals), rule enemy_count + [enemy rate > ln 2] > ally_count + [ally rate > ln 2], predicted only when threatened and > 50k fuel left | 35/60, deaths 525, margin +5494, gems lost 80/g; turns at fuel limit 116 vs 64 (3 games) | pending | 560-game run next |
| rfc | rf3 | control: memory and plumbing, prediction off | fuel = main (61 vs 64 turns at limit) | - | control |
| rf4 | rf3 | symmetric expected counts: enemy_count + rate_e > ally_count + rate_a | 36/60 (main 34), deaths 560, margin +10050; 560: 380 (main 384), deaths 3272 vs 3120 | not gated | N |
| rf5 | rf3 | engage veto: no new fight when an enemy arrival is likely (rate > ln 2) and an ally arrival is not, finishers excepted | 28/60, deaths 610 | not gated | R |
| rf6 | rf3 | cheaper model: one shared hidden layer of 8 for both heads (~4x fewer head MACs; death AUC 0.731 vs 0.734) | 38/60, deaths 545, margin +8099; 560: 378 (main 384), deaths 3138 vs 3120 | not gated | N |
| rf7 | rf3 | likely arrivals join simulate_fight as average champions (1445 hp, 102 str, basic attacks): enemy at the prey, ally at us | 38/60, deaths 475, flee deaths 317 (main 380), margin +5433; 560: 374 (main 384), deaths 3266 vs 3120, margin +77.8k vs +96.6k | not gated | N (60-game lead was noise) |

## Engine 2.x era (2026-10-18 to 10-20)

Variants c1-c37, e_* (e_bank20, e_fuel, e_power, e_flee, e_jung, e_jung1, e_hp, e_stand, e_prism, e_pf, e_sp), j_* (j_end, j_end2, j_goldmap, j_prism, j_standh), k_danger0/1/25, k_stall12, jc_*. Accepted: c36, c37, e_jung, j_standht. Lessons are in `docs/findings.md`. Results are in `docs/journal/findings_log.md`.
