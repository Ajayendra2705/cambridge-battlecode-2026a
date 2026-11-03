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

**Ranged champions in range (`vfx2`), added 11-03 09:02 before its screen.** With an enemy within 3, our Vesper hits a champion in 0.39 of the rounds at r0-100 and 0.32 at r100-300 on the platform, against 0.52 and 0.42 for the rivals' Vesper and 0.52 and 0.48 for our own bot locally. `vfx2`: `P_HOLD_C` -0.6 to -0.85 only for a ranged champion whose target is in range. Same local bar as `vfx1`. Platform metric: Vesper's share of hits on a champion with an enemy within 3 up by at least 1 SE in pairs (`tools/replay/inrange.py`), same guards.

**Free shots (`vfx3`), added 11-03 09:03 before its screen.** A ranged champion at 3 tiles from a melee enemy cannot be reached this turn, yet below a sim of -0.3 (`P_SKIRMISH_MIN`) she goes on working, unless the strike-first rule fires (sim above -0.5, enough allies). `vfx3`: the skirmish test also passes for a ranged champion that is not threatened. Same local bar and platform metric as `vfx2`.

**Striking first (`vms1`, `vms2`), added 11-03 09:24 before their screen.** In contact at r1-100 with even numbers (`tools/replay/exchange.py`, within 3 tiles, 12.5 rounds a game), our champions land 0.40 basic hits per body-round and 0.015 casts on champions, the rivals 0.48 and 0.033; we lose 51 health a round and they lose 39. They outnumber us in contact for 5.9 rounds a game, we them for 3.3. The strike-first rule (`P_MSTRIKE`) needs a sim above -0.5, health above 50%, and enemies within 6 at most allies + 1. `vms1`: `P_MS_SIM` -0.8, `P_MS_SLACK` 2. `vms2`: also `P_MS_HP` 0.35. Same local bar as `vfx1`. Platform metric: basic hits per body-round in contact at even numbers, r1-300, up by at least 1 SE; same guards.
