# Rule for the first turn (written 11-03 02:25 IST, before the local screen)

**Factor.** Opening tempo. `Bot::play_turn` ends the first turn when `fuel() < 120000` after `Bot::init`. `tools/local/firstturn.py pool/v1503`: on 81 maps with a reading, 0 of 356 champions have 120000 left, so every champion skips round 1 on every map. Where setup runs over 200k (values near 100000 on 00dunes, 02geodes, 01boss_battle, adgato_gemcombat5 for some champions) the line also skips round 2, because a later turn only has 100000. The teammate's notes measured the same gap on the Bamboo line (first move at round 2.67 against 1.92 of top teams), and `tools/replay/openpace.py` on `t1503_tm@t03` gives 2.3 tiles from the start at r4 against 2.7, level by r8.

`exp/vfi1` lowers the line to 50000 (212 of 356 champions then act on round 1), `exp/vfi2` to 25000 (about 305 of 356).

**Local bar** (`pool/v1503`, same pool and 85 maps, 680 paired). Target: team gold at r150 up by 1 standard error or more, or our deaths minus theirs to r100 down by 1 standard error or more. Guards: collected to r1000 not down by more than 2 standard errors, deaths a game not up by more than 0.2, wins not down by more than 0.03 a game, no fault. A first turn that runs out of fuel resumes on the next round with old values, so faults and fuel events are watched.

**Platform.** Only a pass goes on. `t03p` parts pinned to `t1503_tm@t03`: deaths to r100 down or team gold r150 up by 1 standard error or more, margin not down by more than 1 standard error. Wins recorded.

**Result (11-03 02:45 IST, data/runs/multi-022620).** vfi1 and vfi2 fail: deaths +0.53 +- 0.18 and +0.51 +- 0.19, wins -0.04, gold r150 -9 +- 8. The tempo gap itself is small: rivals' first move is r2.78 against our r3.73 (`tools/replay/logacts.py`), but our travel dashes close it by r8 (5.9 tiles from the start against 6.0, `openpace.py`). Rejected; the line stays at 120000.
