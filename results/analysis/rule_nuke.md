# Decision rule: Marcella's nuke against strong teams, written 11-03 08:33 IST before any result

**Factor.** Who opens fights. On `t1503_tm@t03` (1503 against ranks 1-20, 170 games, to r600) we are hit first 4.5 times a game and hit first ourselves 2.4 times. The opening hit is a cast in 43% of the
rivals' openings and 21% of ours: their Marcella opens by cast 1.29 times per game she plays, ours 0.63. With her nuke ready and an enemy champion within 4 tiles (`nukeuse.py marcella 1 4`), the rivals' Marcella casts it on
a champion in 0.34 of those rounds, ours in 0.18 (r0-100), 0.35 against 0.19 (r100-300), 0.32 against 0.15 (r300-600). She walks instead: 0.58 against 0.47. Locally the same bot casts in 0.41, 0.33, 0.32 of those rounds, so
the block is against strong teams only. The nuke excludes walking, so `free_cast` fires it only when `(!low && !loaded && outcome > P_FREE_EXCL_MIN) || stand_safe` or when it kills; against strong teams the fight sim reads below -0.3.

**Variant.** `vfx1`: `P_FREE_EXCL_MIN` -0.3 to -1.01. Marcella fires whatever the sim reads, unless she is hurt (under 35%) or loaded (30 gems). One turn of walking lost, 2 x Focus of damage dealt. Only Marcella has such a spell in our drafts.

**Local bar (needed, not enough).** 680 paired games against `exp.vnl1` (`multi-031107`): deaths not up by more than 0.3, wins not down by more than 0.03, collected not down by more than 2 SE, no fault. Her spell on a champion per
opportunity is recorded, not judged locally: she already casts at the rivals' rate there.

**Platform rule.** Against the base on the same pinned panel, playing in the same session. Metric: casts of the nuke on a champion per game up by at least 1 SE in pairs. Guards: our deaths to r300 minus theirs not up by more than 1 SE, team gold at r300 and
tributed by r1000 not down by more than 1 SE, no fault. Wins recorded, not judged.
