# Decision rule: per-map opening arms in the router, written 11-03 08:38 IST before any result of the fresh sample

**Factor.** Gold at r300 on single maps. No opening rule helps on all maps, because the gains are large on some and large losses on others (`data/armtable_r300.json`: nine variants on 85 maps, 8 games a map, against the pool cmb7, bot_10, cp3, dh3). `vlm1` (light camps first on five maps chosen from such a table,
confirmed in 40 local games) beat `rt3` on the platform on those maps: 16 against 9 of 60, flips 12 against 5, margin +208 +- 112, gold r300 997 to 1118, r600 1995 to 2227, the rivals' gold r600 3935 to 3570 (`vlm1_l5p`, `rt3_l5p`).

**Arms.** `L` (light 1.5, enable 1.6, r150), `L3` (light 1.5, enable 1, r150), `W1` (light 1.5, enable 1.6, wolves counted as light, r120), `W2` (heavy 0.6, enable 1.2, r120), `B1` and `B2` (opening book, as `vbk1` and `vbk2`), each only on the maps where the first table shows at least +100 and at least 8% of the base's gold (`data/arm_candidates.json`).
Maps already routed to Bamboo or already in `rt5`, and 00oasis (it lost on the platform), are left out.

**Fresh sample.** 16 games a map against eight other pool bots (v1498, v1502r, v1491, v548, cmb2, hb4, mi8, rz20), paired with `exp/rt3`, whose v1503 arm is the bot under change on those maps.

**Table rule.** An arm goes in the table for a map when its gold r300 gain in the fresh sample is at least +100 and at least 8% of the base's gold there, and its wins on that map in the fresh sample are not below the base's. With several arms passing, the largest mean of the two samples wins.

**Platform rule.** The new table (`rt6`) against `rt5` on a panel of the table's maps (`mappanel.py`, 12 teams, 60 games, pinned, same session): team gold at r300 up by at least 1 SE, margin not down by more than 1 SE, deaths to r300 not up by more than 1 SE, no fault. Wins recorded, not judged.
