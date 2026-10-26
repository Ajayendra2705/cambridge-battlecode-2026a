# Diagnosis from ranked replays (2026-10-27)

Data: 1,290 ranked games on engine 1.0.3 (harvested 2026-10-24, ranks 40-90 and their opponents), boss_battle included unless noted. "Ours" = the 50 Velvet Tributers games (the bot submitted around 2026-10-24). Other team-sides are grouped by current ladder rating relative to ours (1841): higher (> +75, 659 side-games), similar (±75, 1,808), lower (< -75, 89). Scripts: `ml/death_trace.py`, `ml/death_analysis.py`, `ml/side_stats.py`. Our sample is small: treat differences under ~15% as noise.

## Headline

We do not lose by dying. We die less than every group and kill much less. We stay in our own half, farm camps, and let opponents carry and bank big bags.

| Per side-game | Ours | Higher | Similar |
|---|---|---|---|
| Deaths | 6.9 | 9.1 | 9.7 |
| Kills | 5.0 | 8.3 | 8.2 |
| Gems we tribute | 703 | 727 | 703 |
| Gems the opponent tributes | 778 | 697 | 708 |
| Win rate | 46% | 49% | 50% |

## 1. Deaths look the same for everyone

- Bot activity at death (our D lines): flee 73%, pvp 9%, retreat 7%.
- Before a death, hp bleeds from ~0.79 to 0 over 13-16 rounds while enemies near rise (0.9 -> 1.9) and allies near fall. The final turn away comes at ~0.3 hp. Same for all groups.
- Killers were almost always seen before: never seen in the previous 30 rounds 3-4%, first seen in the last 7 rounds ~20%. Same for all groups.
- Flee survival by hp at the turn (P(dead within 10 rounds)): ours 35/14/11/8/3% for hp bins 0-0.3/0.3-0.5/0.5-0.7/0.7-0.9/0.9+, others 31-33/16-18/10-11/6/4%. No difference.
- The reinforcement model predicts the average (0.42 arrivals) before our deaths while 1.09 actually arrive: it does not see the reinforcements that kill us, which explains rf3-rf7 being neutral.

## 2. Contact, position and grouping

Share of alive champion-rounds:

| | Ours | Higher | Similar |
|---|---|---|---|
| Enemy within reach, r0-300 | 6.9% | 9.5% | 9.9% |
| Enemy within reach, r300-1000 | 9.0-9.4% | 10.3% | 11.3-11.6% |
| In the enemy half, r0-300 | 8.4% | 14.3% | 14.8% |
| In the enemy half, r300-1000 | 9.8-10.9% | 16.1-17.8% | 17.8-18.4% |
| Allies within 5 tiles, r600-1000 | 0.59 | 0.70 | 0.69 |

- Engage rate when an enemy is in reach, by simulate_fight verdict: sim says we win 75-77% (others 68-72%), even/not ahead 42% (49%), they win 23% (40%).
- Low-hp (< 30%) enemies within 4 tiles: 9.4 per game (others 11.9-13.7), converted to a kill 45% (47-49%).

## 3. Fighting and economy

| Per side-game | Ours | Higher | Similar |
|---|---|---|---|
| Hits on enemy champions | 147 | 207 | 237 |
| Hits per contact round | 0.36 | 0.43 | 0.43 |
| Enemy hp lost near us per contact round | 55 | 55 | 53 |
| Hits on camps | 1,218 | 1,062 | 990 |
| Wards placed | 342 | 273 | 228 |
| Deposits / gems per deposit | 19 / 45 | 22 / 46 | 23 / 43 |
| Mean bag of enemies we see | 48.8 | 20.6 | 20.6 |

- Our fighting is not weaker per contact round (same damage); it is rarer.
- The mean bag of enemies *we see* (48.8 vs 20.6) is inflated by who we see: we meet few enemies, often carriers. True team carried gems (mean over rounds, boss_battle excluded):

| Phase | r0-300 | r300-600 | r600-1000 | r1000+ |
|---|---|---|---|---|
| Our opponents | 28 | 55 | 73 | 68 |
| Opponents of similar teams | 24 | 40 | 49 | 59 |
| Us | 30 | 74 | 84 | 103 |
| Similar teams | 23 | 39 | 49 | 59 |

Both sides of our games carry 35-75% more: fewer fights, bigger bags. We bank less often (19 vs 22 deposits per game).

## 4. Big carriers (>= 50 gems) in view

Per side-game: we see 4.1 carrier sightings (others 5.7-6.6), approach 32% (37-39%), kill 3% within 10 rounds (everyone 2-3%), gems taken from carriers 13 (29-37). Carrier hunting is rare for every team: not a big lever on its own.

## 5. Our wins vs losses (23 / 27 games)

| | Losses | Wins |
|---|---|---|
| Contact share | 9.8% | 6.1% |
| In enemy half | 7.2% | 12.2% |
| Kills | 4.0 | 6.0 |
| Opponent tributed | 856 | 687 |

Similar teams' wins come with far more kills (11.7 vs 4.7 in losses).

## 6. Per champion (ours vs the same champion on similar/higher teams, per game)

| Champion | Kills | Deaths | Contact share |
|---|---|---|---|
| Marcella | 1.29 vs 2.59 | 1.14 vs 1.83 | 0.06 vs 0.10 |
| Vesper | 1.20 vs 2.25 | 1.20 vs 1.84 | 0.07 vs 0.10 |
| Vendetta | 1.00 vs 1.98 | 1.55 vs 2.06 | 0.08 vs 0.10 |
| HoR | 1.24 vs 1.67 | 1.74 vs 2.13 | 0.10 vs 0.12 |
| Ryth | 0.76 vs 0.99 | 1.95 vs 2.21 | 0.09 vs 0.10 |

## 7. Who starts fights (first champion hit after 15 quiet rounds; kills in the next 20 rounds)

| Per side-game | We hit first | -> our / their kills | They hit first | -> our / their kills |
|---|---|---|---|---|
| Ours | 4.7 | 0.33 / 0.19 | 6.1 | 0.20 / 0.37 |
| Higher | 6.1 | 0.43 / 0.22 | 6.0 | 0.24 / 0.36 |
| Similar | 6.4 | 0.37 / 0.20 | 6.4 | 0.19 / 0.39 |

- We are attacked as often as anyone and fare the same; we start ~25% fewer fights and convert them worse.
- Encounters in the enemy half: others 0.33-0.39 kills vs 0.26 deaths; we break even (0.28 vs 0.27).
- At the first hit our starts look like everyone's (hp, numbers within 5, victim bag, spell vs attack ~50/50). But our fights are started by Ryth 35%, Vesper 26%, HoR 17%, Marcella 16%; similar teams lead with Marcella 27%, Vesper 24%, Ryth 17%.
- Victim killed within 20 rounds when one behind / one ahead in numbers: ours 11% / 21%, others 22-25% / 30-34% (our cells are 30-140 fights: suggestive).

## 8. Builds at round 800

Total stat units bought are the same (ours 37.7 vs 36.1). We buy no Power or Monster shards, more Durability/Treasure/Jungle and more Bruiser. The outlier is Marcella:

| Round 800 | Strength units | Focus units | Strength | Focus |
|---|---|---|---|---|
| Our Marcella | 3.3 | 23.0 | 61 | 405 |
| Others' Marcella | 13.2 | 15.3 | 111 | 289 |

Her spell is ~40% stronger, her basic attacks ~45% weaker, and she kills half as much as Marcella elsewhere.

## 9. Early game timing (median round, boss_battle excluded)

| | First kill | First death | First tribute | Opponent's first tribute |
|---|---|---|---|---|
| Ours | 280 | 158 | 231 | 92 |
| Higher | 168 | 169 | 115 | 116 |
| Similar | 163 | 163 | 114 | 117 |

- No kill by round 300 in 52% of our games (others 34-36%).
- Altars are almost never contested: ~1% of opponent deposits have one of our champions within 6 tiles, for every group.

## 10. Income curves (median gems held = tributed + carried)

| | r100 | r200 | r300 | r500 | r800 |
|---|---|---|---|---|---|
| Ours | 24 | 58 | 98 | 230 | 506 |
| Higher | 34 | 74 | 124 | 241 | 462 |
| Similar | 30 | 70 | 110 | 212 | 398 |
| Our opponents | 38 | 93 | 134 | 253 | 478 |
| Opponents of similar teams | 30 | 68 | 110 | 216 | 404 |

Banked (tributed only) at r200 / r300 / r500: ours 0 / 27 / 107, similar 34 / 72 / 163. We start slow and finish strong; opponents start fast against us.

## 11. Why the slow start: early camp choice

Opponents do not farm our half more (29 early camp hits in our half vs 37-39). Our early farming volume is normal, but each capture pays fewer gems:

| r0-300, per side-game | Ours | Higher | Similar |
|---|---|---|---|
| Camp hits | 338 | 320 | 299 |
| Capture payouts (gem pickups) | 10.6 | 9.4 | 8.9 |
| Gems per payout | 9.8 | 15.9 | 14.8 |
| Gems gained | 111 | 140 | 129 |
| Gold gained | 1,075 | 1,047 | 971 |

Mid-game (r300-1000) gems per payout are equal (21 vs 22-23) and we out-farm everyone (536 vs 436-479 gems). Cause (code): in the opening (`solo_phase()` in `targets.h`, until the champion owns its first emblem) a group is scored `gems + 2.0 x gold`, against `gems + 0.25 x gold` afterwards, to rush the first emblem. The trade does not pay: our early gold equals other teams' (1,075 vs 1,047) while their captures pay 35% more gems.

## 12. Opening captures: we pair up

| r0-300, per side-game | Solo captures | Shared captures (2+ of the team paid in the same round) | Gems per solo capture |
|---|---|---|---|
| Ours | 3.3 | 3.5 | 11.8 |
| Higher | 7.5 | 0.9 | 16.6 |
| Similar | 7.5 | 0.6 | 15.4 |

Camp types hit in the opening: gem clusters 3.7% of our hits vs 7.2%, gold clusters 21% vs 18%, elks 36% vs 30-32%; mean gem value of the hit groups 17.7 vs 18.9-20.4.

Other teams spread out early (~7.5 solo captures, almost none shared). We share half our captures, so we finish fewer (6.8 vs 8.4) and split the rewards. `solo_phase()` in `targets.h` was written for exactly this ("top-10 teams make 16 solo captures and 1 shared one in the first 300 rounds, we made 6 and 5"), but our ranked games (bot submitted around 2026-10-24) still pair up. Check whether that bot had `solo_phase()`, and if so why champions still converge.

## 13. Current main pairs up too (local games), and why it might

80 local games (current `main` vs hb4/tf3/pd1/dm1, 10 maps, kept from the calibration run). Opening (r0-300) per game: main 1.8 solo vs 3.1 shared captures, first tribute at median round 343, 45 gems held at r200. The pool bots pair up as much (1.6-2.1 solo, 2.3-3.0 shared): it is a trait of all our bots, not of one version.

By zone (my approximation: |distance to own spawn - distance to enemy spawn| <= 6 = centre): main's opening captures are 62% centre (242/388) vs 44% for the pool bots; main shares 144 centre and 92 own-half captures.

Code reading (`pick_group` in `targets.h`), hypotheses not yet tested:
- `solo_phase()` only changes the value line (gold x2). Despite its comment, nothing stops two champions choosing the same group, and the clear-time branch scores group sizes up to the whole team.
- "Take the middle first" doubles the score of the same centre groups for every champion before round 400, pulling them together.

## 14. How games end

92% of games for every group are races to 1,000 gems (median ~1,150 rounds); 2,000-round tiebreaks are 7-8% (we lost all 4 of ours). Our losses are close: median deficit at the end 254 gems (similar teams' losses: 414), and 37% of our losses are within 150 gems (21%). A faster opening and earlier banking could flip some of them.

## Candidate experiments (ranked by evidence and cost)

1. Opening captures (economy, local runs are valid): make the opening actually parallel (section 12), and/or lower the opening gold weight from 2.0 (e.g. 0.5 or the normal 0.25). Measure solo vs shared captures before r300 locally first. Target metrics: gems held at r200/r300 (ours 58/98, similar 70/110), first tribute round (231 vs ~115). Cheap: one constant.
2. Earlier first banking (economy): the first tribute comes ~115 rounds later than every other group, partly from the slow gem start, partly from batch sizes. Target: banked at r300 (27 vs 72).
3. Marcella build: our Marcella is almost all focus (strength 61 vs 111 at r800) and kills half as much. Try the balanced build other teams use. Fighting change: needs the platform.
4. Fight starts: we start 25% fewer fights and lead with Ryth (35%) instead of Marcella. Fighting change: platform only; earlier loosening (pa1, lf1) failed, so target who opens rather than how often.
5. Not worth pursuing now: flee timing and reinforcement prediction (deaths are the same for all groups), carrier hunting (2-3% kill rate for everyone), altar contesting (~1% for everyone).

## 15. Test of candidate 1 (local, 60 games each, `ml/opening_metrics.py`)

| Bot | Wins | Deaths | Solo / shared captures r<300 | Gems at r200 | First tribute |
|---|---|---|---|---|---|
| main | 34 | 565 | 1.6 / 3.0 | 43 | 321 |
| op1 truly solo opening | 28 | 665 | 2.5 / 1.5 | 30 | 354 |
| op2 no middle x2 | 33 | 539 | 1.7 / 2.7 | 46 | 334 |
| op3 both | 23 | 668 | 2.5 / 1.4 | 30 | 332 |

Forcing solo farming halves shared captures but makes the opening economy worse (30 vs 43 gems at r200) and costs lives. "Other teams farm solo and earn more" was a correlation: our farming (targets, clear routines) is built for pairs. The slow start is real, but pairing is not its cause on its own.

## 16. Opening and banking variants (local)

| Bot | Games | Wins | Deaths | Gems lost dying /g | First tribute | Banked at r300 |
|---|---|---|---|---|---|---|
| main | 560 | 384 | 3,120 | 66 | r321 (60-game set) | 0 |
| op4 solo + quick groups only | 60 | 21 (main 34) | 680 | 92 | r413 | 0 |
| bk4 first trip at <= 20 gems | 560 | 380 | 3,023 | 62 | r172 | 47 |
| bk5 banking batch x0.5 | 560 | 389 | 2,971 | 51 | r188 | 59 |

The opening-dispersion idea is dead (op1, op3, op4 all worse). Smaller banking batches (bk5, named bk2 during the run) keep wins (+5, within noise) and cut deaths 5% and gems lost dying 23%. But an earlier variant in the same direction (bk3, batch cap 30) was neutral locally and lost 3 vs 10 of 20 on the platform, so treat bk5 with caution.

## 17. Style bots: first calibration (local, 20 games each vs main, 10 maps)

`ml/bot/make_style_bots.py` builds 15 variants of main with knobs AGG in {-2..+2} (enemy-half penalty scale, engage looseness, flee hp threshold 0.4 - 0.1 AGG) and BANK in {0.5, 1, 1.8} (banking batch multiplier). `ml/style_calibration.py` projects each bot's realised style onto the real teams' PCA axes.

- The knobs move the axes as intended: PC1 0.5 (AGG -2) to 7.9 (AGG +2); bigger BANK gives fewer, bigger deposits (18.6 -> 3.6 per 1000 rounds).
- Local and platform styles are on different scales: main measures PC1 +3.8 in these local games and -2.6 on the platform. Style depends on the matchup and maps, not only the bot. Anchoring on main (shift ~-6.4 on PC1) puts the grid at -5.9..+1.5 vs real -2.2..+2.8 (10-90%): too passive, missing the aggressive tail. The constant-shift assumption is unverified.
- AGG +2 is reckless, not skilled: 28-32 deaths per game (real teams ~9), 3-5 wins of 20, although kills (~12/game) match real aggressors. Matching a style statistic does not mean matching behaviour.

## 18. Farm prediction model (fpr) (fpr1-fpr5)

Data: 261,195 capture attempts from platform games (a champion's first hit on a camp group; success = any teammate paid at the group within 60 rounds, 84%). Model A: MLP on group features (camp kinds, hp, gems, gold, allies/enemies near the group), the champion (stats, type) and its position (spawn/altar distances, round, score, bag).

| Bot | Change | Style bench (140) | 560 | Deaths (560) |
|---|---|---|---|---|
| main | - | 76 | 384 | 3,120 |
| fpr1 | model total time incl. distance | 20 | - | - |
| fpr2 | model after-arrival time + travel, replaces the formula | 61 | - | - |
| fpr3 | formula score x model P | 91 | 386 | 2,492 |
| fpr5 | fpr3, fuel-optimised | 94 | 391 | 2,375 |

Lessons: (1) fpr1 extrapolated outside its training distances (trained only 8-12 tiles from the group); (2) features measured at arrival leak information the bot does not have when it chooses (AUC 0.80 at arrival vs 0.72 at decision time); (3) the model works as a multiplicative correction to the formula, not as a replacement; (4) fuel: the first integration cost 21k per pick and doubled fuel-limit turns; precomputing static parts brought it to 92 vs 64.

Held-out check (opponents never used to choose between fpr variants: pool bt1, bt8, c_g1, dv, ea3, gb2, k5, mid4, ts1 and style bots am1_b0p5, ap1_b1p8, ap2_b0p5; 10 maps outside the style bench; 240 games): fpr5 163 vs main 154, deaths 1,290 vs 1,475, captures 60.4 vs 54.9, margin +46k vs +34k. Every opponent is still our own lineage: the platform is the only test against real teams.
