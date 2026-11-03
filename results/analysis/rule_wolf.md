# Wolves first in the opening (written 11-03 06:05 IST, before the screen)

Decoded `t03p` runs (510 games against ranks 1-20, `data/openmap_t03.txt`, scratch `openmap.py`). Hits on camps to r100 per game, us against the rivals: wolves 33 against 56, elks 44 against 48, gem clusters 10 against 14, gold clusters 11 against 14, golems 5 against 3. First reward r50 against r32, third r91 against r64; team gold r50 87 against 144, r100 250 against 373, r150 409 against 613; deaths to r100 0.71 against 0.34. The extra rival work is nearly all wolves. Some maps show it plainly: 01corridors wolves 26 against 185, elks 63 against 2; 00great_wall wolves 0 against 89, elks 148 against 85.

Per damage taken a wolf is the cheap gold: 40 gold for 27000/D damage against an elk's 90 for 144000/D and a golem's 160 for 600000/D (D = team damage per round). `choose_task` values gems at 3 gold, which puts elks and golems first.

Variants on `exp/vnl1` (`mk_vwf.py`), before round R: a group whose hardest camp is a wolf or weaker counts `P_WOLF_W` times, a group with an elk, golem or monolith counts `P_HEAVY_W` times, and `P_ENABLE` (1.6, the pull towards a heavy group that needs me) becomes `P_ENABLE_EARLY`.

- `exp/vwf1`: R 120, 1.5, 1, 1.6.
- `exp/vwf2`: R 120, 1, 0.6, 1.2.
- `exp/vwf3`: R 200, 1.5, 0.8, 1.2.

Local bar (base `exp.vnl1`, `multi-031107`, 680 paired): team gold r150 and r300 up by 1 standard error or more. Guards: deaths not up by more than 0.3 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault. The same variants may pass only on some maps: read `tools/local/lgoldmap.py` for a per-map arm, as `exp/vlm1` did.

Platform only after a pass: `t03p` parts pinned to `t1503_tm@t03`. Target: decoded team gold r100 and r300 up by 1 standard error or more, wolf hits to r100 closer to the rivals'. Guards: margin and collected not down by more than 1 standard error. Wins recorded, not judged.
