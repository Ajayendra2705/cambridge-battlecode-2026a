# Health first on Vendetta and Heart of Ruin (written 01:43 IST 11-04, before any game)

**Gap.** v1536 against the top teams on `tt1` (`rf1_tt1_tt1`, `decoded.py types`, `items --round 300`), to r1000 per game:

| type | deaths us / them | max health r300 us / them |
|---|---|---|
| Vendetta | 2.61 / 0.80 | 941 / 1370 |
| Heart of Ruin | 2.00 / 1.00 | 917 / 1123 |
| Marcella | 1.49 / 0.83 | 1294 / 1312 |
| Vesper | 1.61 / 0.96 | 1100 / 1215 |

Vendetta has the largest gap in both. Ours opens Prospector of strength in 64% of games, at r258 on average; top teams open with a mix, and Fish's Vendetta opens Capture of health (`docs/bamboo/knowledge/fish-builds-1031.md`). `wdh1` (Durability first on four types) failed locally on collected and wins, and `vbd1` (the whole Fish line) failed on gold, but one champion's first emblem has not been tried. All of this is on the default arm only (`src/cj`).

**Variants of `exp/vf3`, default arm only, `P_VEN_FIRST` in `src/cj/params.h`.**

- `vh1` (1): Vendetta's Prospector first is replaced by Capture of health.
- `vh2` (2): Vendetta's Prospector first is replaced by her plan's Durability of health, moved to the front.
- `vh3` (3): as `vh1`, and Heart of Ruin's Prospector first is replaced by Capture of health too.

**Local bar (needed, not enough; `multi-011232` is the paired base, `exp.vf3`, 544 games on the 68 default-arm maps).** Deaths not up by more than 0.3, wins not down by more than 0.03, collected r1000 not down by more than 2 SE, no fault. Team gold is recorded. Only the best passing variant goes to the platform. If none passes, none goes.

**Platform rule (target metric, not wins).** Against `rf1_tt1@tt1`, then `rf1_nb1@nb1`, on default-arm maps only. Metric: Vendetta's deaths r1000 down by at least 1 SE on `tt1`. Guards: team deaths r1000 not up, tributed r1000 and margin not down by more than 1 SE, team gold r600 not down by more than 1 SE, no fault.

**`vd1` (written 01:49 IST, before any game).** `exp/vf3` plus `P_VDASH`: Vendetta's `dash_strike` onto a champion needs enemies within 3 of the target to be at most ours within 3 of it, herself counted, or one more on a target at 40% health or less. Reader (`rf1_tt1_tt1`, per game): 2.24 of her 2.61 deaths come within 8 rounds of her own cast, 1.64 of them with enemies outnumbering allies within 5 of her after it; the rivals' Vendetta 0.30. The same idea failed for Heart of Ruin on another line (`hd1`, 10-30: fewer dives cost 30% of its damage and did not lower its deaths), so the bar also watches her damage. Local bar as above, plus Vendetta champion damage recorded (`ltypes.py`). Platform rule as above, plus her champion damage at least 90% of the base.
