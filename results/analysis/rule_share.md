# Decision rule: a joiner's share in the pick (bots/exp/vnt1, vnt2, vnt3), written 11-03 before any result

**Factor.** Speed of the first captures. On `t1503_tm@t03` our Vesper's first capture comes at r69 with 0.7 helpers, 48 rounds after her first hit; the rivals' at r43 with 1.8 helpers, 26 rounds after it (scratch `vesfirst.py`, `walklost.py`). Marcella: 1.6 against 2.3 helpers, and the second capture at r108 against r85. The walk to the first hit is nearly equal (21.0 against 22.8 rounds, distance 13.9 against 15.2, lost rounds 7.1 against 7.6), so the gap is in the kill. `choose_task` divides a group's value by the number of champions on it.

**Variants, on `exp/vnl1`.** `vnt1`: n^0.75 before r150. `vnt2`: n^0.5 before r150. `vnt3`: n^0.75 in every round.

**Metric and bar, local screen (680 paired games against `exp.vnl1`).** Team gold at r150 and r300 up by at least 1 SE. Guards: deaths not up by more than 0.3, wins not down by more than 0.03, collected not down by more than 2 SE, no fault.

**Solo chipping (`vch1`, `vch2`), written before any result.** Same factor. A champion alone on a damaging group chips it over healing trips (`P_CHIP`), which keeps it busy for long with no reward. `vch1`: no chipping before r150 for anyone. `vch2`: none for Vesper before r200. Same bars.
