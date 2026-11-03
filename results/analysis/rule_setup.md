# Decision rule: rounds lost to setup fuel, written 11-03 10:09 IST before any variant was built

**Factor.** Rounds lost at the start of the game. `World::init` and `Bot::init` run on the first play turn and spill into later turns on big maps. After the setup, `Bot::play_turn` returns when less than 120k fuel is left. A later turn has only 100k, so any setup that spills loses the rest of that turn too.

**Measured** (`exp/fp1`, a probe that never ships, 11-03 09:45): the first action comes on r2 on 00vault, r3 on 00ambush, r4 on 01big_world and r6 on 03the_front. The costly parts are the groups and altar spots (59k to more than 172k) and the reachability and halves (42k to 180k). On the platform, rivals have 0 exhaustions on r1-3 on many maps where we have 5 to 10 (00ambush 6/0, 00vault 5/0, 00expanse 6/0, 00quadrants 6/0, 01islands 10/3.3), and they hit camps at r2-3.

**Variants.** `vfu1`: the gate at 120k falls to 45k, so a setup that ends with fuel left still acts on that turn. `vfu2`: `vfu1` plus a cheaper setup with the same decisions (fewer host calls in the groups, reachability and halves loops).

**Probe bar.** A variant must move the round of the first action earlier on at least three of the four probe maps. `vfu2`'s setup must cost at least 25% less fuel on those maps than the setup of `vnl1`. The decisions must not change: on a map where the setup ends on r1 in both bots (first action r1 in `vnl1`), the replay of the first 100 rounds in a mirror against the same opponent must be identical.

**Local screen bar** (680 paired games against `exp.vnl1`): exhaustions on r1-3 down by at least half on the maps where the setup spills, deaths not up by more than 0.3, wins not down by more than 0.03, collected not down by more than 2 SE, no fault. Team gold at r150 is recorded and not judged, because the gain per map is small and most maps do not spill.

**Platform bar.** Paired with the base on a panel of the spilling maps: our first camp hit on the panel earlier by at least 1 SE, exhaustions on r1-3 down by at least half; guards: deaths to r300 minus theirs not up by more than 1 SE, team gold r300 not down by more than 1 SE, no fault. Wins are recorded and not judged.

## Local results and the next step, 11-03 10:29 IST

`vfu1` (gate 45k, the setup unchanged; multi-101914, 680 paired): wins -0.04, margin -33.7 +- 19.2, collected -19.7 +- 8.9, deaths +0.38 +- 0.19, team gold r150 -13.3, r300 -38.4 +- 16.9, r600 -123 +- 38. It fails. A first turn with 45k to 100k fuel stops `choose_task` early (`P_CT_FUEL` 35k) and builds no group field (`ensure_field` needs 70k), so the first choice is worse. Reading: acting early on a thin turn costs more than the round it saves.

A probe over all 85 maps shows that the gate at 120k fires on every map: the first action comes on r2 on 40 maps, r3 on 28, r4 on 15, r5 and r6 on one each (mean r2.76).

`vfu2` and `vfu4` (setup from a draft plan, lazy group bitboards, no objects for the camp layout, gate 45k and 80k): a check build found 0 mismatches of the plan's numbers against computed numbers on all 85 maps, and the plan was read on all 85. Setup ends on r1 on 78 maps (r2 on 6, r3 on 1); first action on r1 on 74 maps at gate 45k.

The screen of `vfu2` and `vfu4` uses the bar above.
