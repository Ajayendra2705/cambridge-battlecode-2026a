# Decision rule: Vesper follows the team to gold and captures it (bots/exp/vvj1, vvj2, vvj3), written 11-03 before any result

**Factor.** Vesper's gold in the opening. On `t1503_tm@t03` her camp gold by r150 is 97 against the rivals' 263 (r300 232 against 629), which is nearly the whole team gold gap at r150 (409 against 613). Her first capture comes at r83 against r44, and by r150 she takes 0.43 captures of groups that two or more teammates hit against 1.32 (`tools/replay/soloshare.py`). In the traces the rivals' Vesper moves with the team, the team kills an elk or wolf group and she captures it. Ours walks alone to far gold or chips wolves.

**Cause in the code (`farm.cpp`).** Her pick divides a group's value by the number of committed champions, although a capture by her alone keeps all its gold (`choose_task`). In `capture` a hurt ally counts +1000, so after an elk the hurt tank usually takes the capture, and she leaves any group with 10 or more gems when Marcella is on her way to it. `vcv1` (in the screen `pw`) only raises her capture weight, so it does not beat the hurt rule.

**Variants, all on `exp/vnl1`.**
- `vvj1` (R 200, W 1.33, CAP 0): her pick only. Before r200, on a group with gold and at least one committed ally, the gold is not split and counts 1.33 times.
- `vvj2` (R 200, W 1.33, CAP 1): the same, and before r200 her capture weight beats a hurt ally's and she does not leave a gold group to Marcella.
- `vvj3` (R 300, W 0, CAP 1): the capture rule only, until r300.

**Metric and bar, local screen (680 paired games on 85 maps against `exp.vnl1`).** Her gold r150 and r300 up by at least 1 SE. Team gold at r150 and r300 not down by more than 1 SE. Guards: deaths not up by more than 0.3, wins not down by more than 0.03, collected not down by more than 2 SE, no fault.

**Platform, for a local pass.** `t03p` parts pinned to `t1503_tm@t03`, the same panel as `vvg1`. Her gold r300 up by at least 1 SE, margin and collected not down by more than 1 SE. Wins are recorded, not judged.

**Second family: captures go to the gold carriers (`vce1`, `vce2`, `vce3`), written 11-03 before any result.** Big captures (base gold at least 60) by r150 on `t1503_tm@t03` (scratch `capwho.py`): ours go to Vendetta 0.89 a game, Heart of Ruin 0.79, Marcella 0.64, Vesper 0.36; the rivals' to Marcella 1.13, Vesper 1.11, Heart of Ruin 0.45, Vendetta 0.41. A hurt capturer is rare on both sides (under 45% health in 6-13% of the events), so the hurt rule is not the cause; the weights are (Vendetta 1 beats Marcella 0.6 on every group) and the arrival order is.
- `vce1`: Vendetta's capture weight 0.45 (Heart of Ruin's) instead of 1.
- `vce2`: the same, and Marcella's weight 0.9 instead of 0.6.
- `vce3`: as `vce1`, and until r300 a champion other than Vesper, not hurt and with no enemy in sight, leaves a gold group to a free Vesper within 15 tiles; her pick values such a reward 1.33 times.

Same bars: the gold of Vesper plus Marcella at r150 and r300 up by at least 1 SE (the judge's table has Vesper only, so read `decoded.py champs` if she alone misses), team gold at r150 and r300 not down by more than 1 SE, the same guards.

**Result of the first family, 11-03 07:40.** `vvj3` passes (her gold r150 +11.1 +- 2.0, r300 +16.7 +- 3.5; team gold flat; guards hold). `vvj1` and `vvj2` fail: her gold and the team's fall, because following the team costs her the solo clusters. **Combination `vvk1`** (written before its screen): `vvg1` (harmless gold first before r200) plus `vvj3`'s capture rule. Same bars. If it passes, it replaces `vvg1` on the plan: her gold r300 up by at least 1 SE on `t03p`, margin and collected not down by more than 1 SE.

**Her pick by value (`vgv1`, `vgv2`), written 11-03 07:50 before any result.** All of the team's gold gap at r300 is in two types (scratch `tribshare.py`): Vesper 232 against 629, Marcella 295 against 507, while Vendetta 310 against 294 and Heart 227 against 226 are level. Her gold per capture is 83 against 113, and a fifth of her first captures carry no gold against a tenth of theirs. `vgv1`: before r300 her pick values a gem 1.5 (now 3) and a gold 1.33 (now 1). `vgv2`: a gem 1, a gold 2. Same bars as `vvj`: her gold at r150 and r300 up by at least 1 SE, team gold not down by more than 1 SE, the usual guards.

**Results of `vgv1`, `vgv2` (multi-085343, 680 paired, 09:17).** Both pass. `vgv1`: her gold r150 +29.4 +- 5.0, r300 +64.3 +- 11.3, team r150 +7.5, r300 +10.9, r600 -28.7, wins -0.03, margin -22.9 +- 12.8, collected -8.9 +- 6.5, deaths +0.08. `vgv2` (gems 1, gold 2, before r300): her gold r150 +30.3 +- 5.1, r300 +83.5 +- 11.8, team r150 +7.9, r300 +30.6 +- 11.6, r600 -1.5, wins -0.02, margin -22.2 +- 13.1, collected -10.6 +- 6.2, deaths +0.02. `vgv2` beats `vvk1` (her gold r300 +45.1, team +16.5).

**Combinations (`vgk1`, `vgk2`), written 11-03 09:18 before their screen.** `vgk1`: `vgv2` plus `vvj3`'s capture rule. `vgk2`: `vgv2` plus `vvk1` (harmless gold first and the capture rule). Same bar as `vgv`, against `exp.vnl1`. The one with the larger team gold at r300 replaces `vvk1` in the router if it beats `vgv2` by at least 1 SE on her gold at r300; otherwise `vgv2` does.
