# Decision rule: our target rule and fight simulation know that Cassi and Issac die together (bots/exp/vpa1), written 11-03 12:08 IST before any game

**Factor.** Games against a rival pair. On `t1503_tm@t03`, five a side, we win 3 of 34 against the pair (deaths to r300 3.35 against 1.18, with the pair's count including both bodies) and 22 of 65 against other drafts (2.09 against 1.46). Ranks 1 and 2 (Mite, Fish) field the pair. Our hit rounds fall on Issac 19.6 a game and on Cassi 7.8 of 118, although Cassi has 600 + 65 health against Issac's 900 + 80 and either death kills both.

**Variant.** `vpa1`, on `exp/vnl1`: the fight simulation kills both when one of the linked pair falls; the target score takes 200 off for Cassi and 100 off for Issac. The games change only when an enemy Cassi or Issac is seen, so the usual pool (no pair) says nothing; the local test plays against `exp/opcm` and `exp/opcf` (v1503 with Mite's and Fish's five picks, no six-body support), on the 51 five-pick maps, both sides, paired with `exp/vnl1`.

**Metric and local bar.** Target: pair deaths (one a pair) to r1000 up by at least 1 SE. Guards: our deaths to r1000 not up by more than 1 SE, margin not down by more than 1 SE, no fault. Wins are recorded, not judged.

**Platform, for a local pass.** Games against pair teams only, pinned from `b1p` on the same maps, base in the same session. Target: pair deaths to r300 and to r1000 up by at least 1 SE in pairs, with our deaths to r300 not up by more than 1 SE. Guards: team gold r300 and tributed r1000 not down by more than 1 SE, no fault.

**Local result (`data/runs/pa_join`, 208 paired games on 51 five-pick maps against `exp/opcm` and `exp/opcf`).** Wins +0.04 +- 0.03, margin +30 +- 31, deaths -0.33 +- 0.34, kills +0.45 +- 0.32, no fault. Deaths to r1000 with the pair counted once (`tools/local/ldeaths.py`): base us 5.09, them 6.05; vpa1 us 4.81, them 6.60; us minus them -0.83 +- 0.45. Passes: the target moved by more than 1 SE and the guards hold. It goes into the next candidate; on the platform it can only change games against a pair.
