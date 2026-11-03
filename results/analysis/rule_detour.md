# Cheap harmless groups on the way (written 11-03 06:07 IST, before the screen)

Our first reward comes at r50 on average, the rivals' at r32; our third at r91, theirs at r64 (`data/openmap_t03.txt`, 510 games against ranks 1-20). Example, `00vault`: at r10 one rival already holds 40 gold from two gold clusters beside its spawn and rejoins its team at r20, while all four of ours walk past the same clusters to the centre and hold no gold until r60. `choose_task` scores a group by `value / (distance + clear time)`. The distance counts the whole walk from here, even when the group lies on the route to the chosen task, so a cheap group near the route looks worse than it is.

`exp/vdt1` and `exp/vdt2` (`mk_vdt.py`, on `exp/vnl1`): after the usual choice, a harmless group nobody took, on our side or contested, within `P_DETOUR_D` steps, is taken first when its value per round of extra time (detour plus clear time plus 2) beats the chosen task's score. Only while the chosen task is a group that hits or one still respawning.

- `exp/vdt1`: before r150, within 10 steps, gold weight 1.5.
- `exp/vdt2`: before r400, within 8 steps, gold weight 1.

Local bar (base `exp.vnl1`, `multi-031107`, 680 paired): team gold r150 and r300 up by 1 standard error or more. Guards: deaths not up by more than 0.3 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault.

Platform only after a pass: `t03p` parts pinned to `t1503_tm@t03`. Target: decoded team gold r100 and r300 up by 1 standard error or more, first reward earlier. Guards: margin and collected not down by more than 1 standard error. Wins recorded, not judged.

## Waits and captures in the opening (written 11-03 06:29 IST, before the screen)

Our Vesper spends 18% of her turns to r300 waiting (`wait_respawn`, `wait_tank`, `gather`). `P_PULL_WAIT` 15 makes a non-tank stand up to 15 rounds at a group it cannot tank alone until the tank pulls. Rivals land 135 hits on camps by r100 against our 103. `exp/vpw1` and `exp/vpw2` set `P_PULL_WAIT` to 6 and 2.

The rivals' Vesper makes 5.5 captures by r300 and holds 629 gold, ours 2.8 and 232. Team gold is above the camps' nominal gold by 21% for them and 11% for us after kill gold. `exp/vcv1`: before r300 Vesper's capture weight is 2 (was 0.85) and she no longer leaves gold groups to Marcella on her way.

Local bar for all three as above (base `exp.vnl1`, 680 paired): team gold r150 and r300 up by 1 standard error or more; deaths not up by more than 0.3, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault. For `exp/vcv1` the gold bar counts at r300 only.
