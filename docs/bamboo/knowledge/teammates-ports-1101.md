# Ports from the Velvet Tributers bots (Nov 1, 00:30 UTC)

Read-only study of the teammates' repository (github.com/Ajayendra2705/cambridge-battlecode-2026a; local clone in the session scratchpad
`vt/`) against our B579c. Tags: [code] checked in the source, [docs] from their docs, [logs] from our local run of 70 maps x 2 sides
(`results/ev/run1793488979`, our #458 vs VTmain = vx1 89/140, VTcmb1 68/140, VTb10 71/140). No bot_10 mechanism was ever tested on its own.

**cmb1 = vx1 at 3 picks, bot_10 otherwise** [code]; everything we lose to cmb1 at 4-5 picks is bot_10. Their whole-bot evidence [docs]:
bot_10 beat vx1 87/140 locally; on their platform cmb1 beat vx1 by +62 +-48 margin, fought more, lost fewer gems on death (152 -> 84) and
held rivals' collected gems down by 113 a game; its own collection was level. Our losses [logs]: farm maps with 0 kills and equal gold but
they bank faster (geodes 789 v 1004 by r853, cuts 759 v 1078, big-world 519 v 1070 by r915); fight maps out-killed (arena 3 v 16,
interlock 8 v 18, fragment 1 v 11).

bot_10 in brief [code]: every champion picks its own camp (no team opening), reward split 1/n; a camp is feasible when a step-by-step
damage estimate fits 0.85 of the committed allies' spare health; only tanks open heavy camps. Banking: tribute at 60 gems, or any amount
within 6 steps of an altar, or 25 within 10; heal at 30% health (55% with enemies seen recently); recall during a capture only when going
home anyway. Fights: focus-fire simulation with approach delays and enemy cooldowns; engage at +0.3, hold in contact unless <= -0.6, back
away out of contact below -0.85.

## Ranked ports

1. **Hurt-first turn order in contact** (`fight.cpp` set_turn_priority): a champion within 6 of a visible enemy sets priority 100, +50 under
   50% health, +(6 - distance); else 0 [code]. vx1's go1 [docs]: "ours act first in contact" 0.455 -> 0.729, deaths -1.1 +-0.4 a game,
   collected / tributed +13-14%. Ours: none - publish_priority writes aggro_key<<27 | (7-slot)<<24 | payload and aggro_key is 0 outside
   boss-camp fights, so fights run in draft order. Sketch: bits 27-30 = 8 + (under 50% ? 4 : 0) + min(3, 6 - d) when an enemy champion off
   its spawn is within 6; order and payload bits unchanged (kCarryCast readers unaffected); not in camp-only fights (camps hit whoever
   acts first on a distance tie).
2. **Monolith siege on a schedule** (`farm.cpp` update_rally / is_gate_group / work_group): from r350 once the lead (lowest slot) has 1800
   max health, or from r900, the team goes to the nearest own-half monolith (side >= -4); under 60% health (85% after 8 rounds waiting)
   heals first; tank = lowest slot with health > max(25%, 2.5 x the camp's hits a round), others no nearer than the tank; called off after
   300 rounds, 2 of ours dead at once, or < 30% of its health gone 120 rounds after the call (then avoided 500 rounds). Gap [logs]:
   00monolith 387 v 1084 by r786, big-world 519 v 1070, gold-rush 147 v 1036, boss-battle 169 v 1497. Ours: kBossMode needs team health x
   1.5 to cover the whole kill (kBossBudget); kBossCommit 31 already rotates hits; kSiege off (-100..-267 pre-2.0). First measure our
   first monolith capture round on those maps; then this gate as an alternative to kBossBudget (non-boss maps too).
3. **Hold our capture under pressure** (`fight.cpp` combat, P_CAP_STAY): on our reward tile, camp worth >= 20 gems or >= 100 gold, health
   >= 35%: stay while health > 1.5 x (summed ready burst + damage a round of enemies within burst reach) + 1, hitting the weakest enemy in
   reach. vx1's hc2 [docs]: captures abandoned 12.1 -> 5.8 a game, collected +6%, deaths unchanged. Ours: none (wants_evade has no reward
   tile exception). Sketch: wants_evade / wants_kite false under that condition, enemy_burst_ for the sum.
4. **Bank under fire by damage forecast** (`bot.cpp` play_turn): >= 15 gems, altar <= 4 steps, nearest enemy >= 3: tribute if the sum over
   enemies of (damage a round x rounds they can hit during walk + channel, plus burst) < 0.8 x our health. Not measured alone. Ours:
   kChannelSafe 6 blocks any tribute with an enemy within 6; contest_bank_ok() forecasts but only for Marcella (kMarcTribute, off; +17 of
   2,240 locally) and the finish. Sketch: a switch in channel_unsafe() for everyone, plus a ready-enemy-stun check (stuns break tributes).
5. **End-of-game banking deadline** (vx1 bank stage): enemy rate = max(0.2, their banked over the last 150 rounds / 150); rounds left =
   min((1000 - their banked) / rate, 2000 - round); bank now if 2 x (altar walk + ceil(gems / 10) + 1) >= rounds left. [docs] 53 v 46 of 90
   platform games. Ours: none (our banking never reads the enemy's pace); close losses e.g. islands 986 v 1014 [logs].
6. **Multi-trip clears priced into each champion's own pick** (`farm.cpp` choose_task; vx1 clear_time): score = value / (walk + 1.5 x wait +
   kill time + 5 + trips x (2 x spawn distance + 8)), trips <= 3 (8 shared on golems), health >= 60%; after 3 rounds waiting at a heavy camp
   with nobody coming and no enemy seen, chip it alone. Ours: kWaveFallback (40 idle turns), kRelayGems (-41 / -72); split play lost
   (s_farm -84) - screen against VTb10 / VTcmb1 directly.
7. **Calm-avoid**: every enemy >= 5 away and none closer over 2 rounds, health >= 60%, < 30 gems carried: don't leave the work. Ours:
   kWalkEvade (reachability only). Low expected value (aggression has lost on our ladder).

Skip: Willow escort (our kWillowFollow -85), small bags near altars (kNearbyGems -14), team spreading (-84), the 850 bank-everything sweep
(neutral for vx1), vx1's bag formula bb2 (+3% tributed; our fixed 40 is tuned), their draft differences. vx1's dh3 / gf2 hardcode maps:
never port. VTb10 runs with its per-turn log on (fuel) and still beats us.

## Where cmb1 beats us, measured (Nov 1 ~03:40 UTC; 26 recorded games #458 vs cmb1 on 13 maps cmb1 wins both sides, scratchpad vtrep/;
tools/stress/vt/vtcompare.py, vtcaps.py, vtsplit.py)

| per game | #458 | cmb1 |
|---|---|---|
| captures | 39.0 | 54.7 (+40%) |
| gems captured | 598 | 709 |
| banked r400 / r800 | 173 / 439 | 194 / 582 |
| deaths / gems lost on death | 5.0 / 26 | 2.7 / 18 |
| tributes (mean size) | 18.9 (36.4) | 27.8 (33.0) |
| big camps (golem / monolith) taken | 1.3 | 0.1 |

Champion-rounds r0-900: camp 18.7% vs 21.7%, walk 51 / 50%, dead 4.6 / 2.5%. **Champions hitting one camp per hit-round: ours 2.17,
theirs 1.52; by phase ours 2.63 / 2.13 / 2.17 / 1.96 / 1.47 (r0-150 / -300 / -600 / -900 / later), theirs 1.64 / 1.50 / 1.52 / 1.45 /
1.34, with ~1.8x our camp hit-rounds in r300-600 (5,520 vs 3,073).** They run more camps in parallel all game. bot_10's choose_task
scores value / party size / (walk + 1.5 x wait + kill time + gather + health cost), feasible when the step-by-step damage fits 0.85 of the
committed allies' spare health, only tanks open heavy groups, solo chipping over <= 3 trips; no whole-team opening. Ours: on 48 of 70
maps (boss maps, kBossMode) team_rounds_ = 2000 - one squad of five all game. Split-play arms lost before, but only against our own pool
(which also squads). s_split: v1472 + kBossMode false / kSplitRound 300 / 150, against the pool and the teammates' bots.

## Results of the ports (Nov 1, on v1472; pool = 2 seeds x 1,120 games, teammates = seed 1 x 560)
kHurtFirst 6: pool -18 vs v1472, teammates +13 wins; kHurtFirst 4: pool +12 (teammates pending). kCapHold: pool -6, teammates +7 wins.
kBossMode false: -144 / -139; kSplitRound 300: -57 / +4; 150: -89 / -33. Function-level ports are neutral, splitting loses: built the
whole-bot hybrid kHybridWalk 61 (edit_hybrid.py, bot_10 on spawn walks > 61) - s_hybrid pending.

## Farming rate against a common field (s_hyb logs: pool + vx1, all 70 maps x 2 sides, 700 games a bot; gems / gold per 100 rounds)
| maps | bot | our gems | our gold | opponent gems |
|---|---|---|---|---|
| walk <= 60 | v1472 | 69.6 | 483 | 45.2 |
| walk <= 60 | bot_10 | 69.5 | 429 | 60.3 |
| walk <= 60 | cmb1 | 64.6 | 441 | 62.1 |
| walk > 60 | v1472 | 75.8 | 470 | 60.0 |
| walk > 60 | bot_10 | 83.1 | 466 | 60.2 |
| walk > 60 | cmb1 | 82.4 | 465 | 60.9 |
On near maps bot_10 farms exactly as fast as we do (more gold for us) - our edge is denial (opponents bank 45 vs 60 a 100 rounds); on far
maps bot_10 farms ~10% faster with the same opponent pace - its parallel small-party farming pays only there. kHybridWalk 61 adopts it
there whole; ports into our squad bot lost (kBossMode false -144 / -139, kSplitRound). By pick count vs the field: 3 picks v1472 85 / 120,
bot_10 70, vx1 68; 4 picks 117 / 160 vs 91 / 88; 5 picks 305 / 420 vs 287 / 280 - their drafts / bots are not better at any team size.
