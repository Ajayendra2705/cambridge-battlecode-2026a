# Rule for walking distances in the first rounds (written 11-03 03:37 IST, before the local screen)

**Factor.** Early camp choice. `World::dist_to_group` (`world.cpp`) returns the group's distance field when it exists, otherwise a crow's-line estimate: Chebyshev x 5/4 + 2. Fields are built one or so a turn from r3 (`W.precompute(45000, ...)`, only with 60000 fuel left), nearest first, and each champion builds its own. So for the first tens of rounds a champion picks its camp with an estimate, and on walled maps (01corridors, 00dunes, 02cuts) that estimate is far off; `P_SWITCH` then keeps the pick. On 01corridors our Vesper goes back and forth across the map between groups 5 and 11 for 300 rounds. A turn uses about 27k fuel of 100k with the log off (`rule_shootdash.md`), so there is room.

**Variants on `exp/vnl1` (v1503 with the log off).** `exp/vdg1`: without a field, the distance is at least the difference between `g.spawn_dist` and my steps from spawn (triangle inequality on the spawn field, which exists from setup). `exp/vdg2`: vdg1, and before r60 the precompute keeps 20000 fuel instead of 45000 and runs with 35000 left.

**Local bar** (base `exp.vnl1`, its 680 games in `multi-031107`, same pool and 85 maps). Target: team gold at r300 up by 1 standard error or more. Guards: deaths not up by more than 0.3 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, exhausted turns not up by more than 1 a game, no fault.

**Platform.** Only a pass goes on, on `t03p` parts pinned to `t1503_tm@t03`: team gold r300 up by 1 standard error or more; margin and collected not down by more than 1 standard error. Wins recorded.

**Task switches (`exp/vsw1`, `vsw2`, `vsw3`, written 11-03 03:43 IST, before their screen).** On `t1503_tm@t03` our champions change task 5.65 times per 100 turns to r500 (logs in the replays), one capture per capturer every 51 rounds; `tank` (walking to the task) is 42% of turns and `wait_respawn` 12.5%. On `exp/vnl1`: `P_SWITCH` 2.0 (vsw1), a re-plan every 8 rounds instead of 4 (vsw2), both (vsw3). The same bar as above.
