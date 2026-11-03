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

**`vh1` local result (01:59 IST).** `multi-014355`, 544 paired with `exp.vf3`: wins 478 to 453, flips 26 up and 51 down, collected on five picks 1129 to 1092, deaths on five picks 4.38 to 4.41. Fails the bar on wins. It stays out of the 02:00 upload.

**`vh2` and `vh3` stopped (02:09 IST).** `vh2` on 478 pairs: wins 418 to 401, flips 26 up and 43 down, collected on five picks 1130 to 1083. It fails like `vh1`; `vh3` adds to `vh1`, which failed. Item changes keep losing here, so the CPU goes to the dash rule.

**Dash variants (written 02:11 IST, before their games).** `vd1`'s partial read at 02:08 IST, 410 pairs: wins 356 to 363, flips 20 up and 13 down, deaths on four picks 8.17 to 6.26, on five 4.89 to 4.43. Traces on `tt1` show Vendetta dying at r25 to r40 from full health with 4 or 5 enemies around (15 deaths by r120 in 40 games). `vd2`: `P_VDASH` 3, also Heart of Ruin's landing dash. `vd3`: Vendetta only, needs one more ally than enemies (`P_VDASH_M` -1). `vd4`: `P_VDASH` 5, also Vesper's dash. Same local bar and same platform rule; for `vd2` Heart's champion damage must also stay at least 90% of the base, the point where `hd1` failed.

**Dash variants, local result (02:40 IST, all 544 pairs against `exp.vf3` of `multi-011232`, no fault).** All three sizes together, wins of 544, then per game deaths, collected, wins:

| variant | wins | deaths | collected | wins per game |
|---|---|---|---|---|
| `vd1` Vendetta | 478 to 484 | -0.49 +- 0.18 | -2.79 +- 9.35 | +0.01 +- 0.01 |
| `vd2` + Heart | 478 to 475 | -0.55 +- 0.21 | -0.41 +- 9.75 | -0.01 +- 0.01 |
| `vd3` needs one more ally | 478 to 466 | -0.35 +- 0.23 | +0.28 +- 13.20 | -0.02 +- 0.01 |
| `vd4` + Vesper | 478 to 479 | -0.60 +- 0.19 | -3.21 +- 9.29 | +0.00 +- 0.01 |

All pass the local bar. On four picks `vd1` (the same as `vd4` there, no Vesper in that draft) has deaths -1.42 +- 0.54, captures +1.64 +- 0.84, wins +0.05 +- 0.03; on five picks deaths -0.39 +- 0.29, collected -15.53 +- 14.49, wins 0; on three picks deaths +0.09 +- 0.18, wins +0.02 +- 0.03. Vendetta's deaths per game 0.99 to 0.80 and her damage 9628 to 9054 (94%; the base figure mixes two candidates). `vd1` goes to the platform first: most wins, fewest changes. `vd4` is the next if `vd1` holds on `tt1`.

**`vd1` missed its first slot (02:35 IST).** Quota ran out before `tt1` could start under v1539: a second copy of the slot script created `nr5` again and part of `nr6`, 11 groups wasted (a killed runner had left its `gate_slot.sh` child running, and `procs.sh` did not list that script; it does now). Three groups of `tt1` (`rh5_tt1a@tt1a`) were created at 02:35:15 while the switch back to v1536 was under way: every margin equals `rf1_tt1@tt1`, so they played v1536 and say nothing about the dash rule.

**Prospector first on Heart of Ruin (written 02:59 IST, before any game).** On `tt1` our Heart opens Prospector of focus in 53% of games, at r298 on average, and captures 2.7 rewards by r600; the rivals' Heart opens Jungle of focus most often (31%) at r269. Prospector pays 25% more of her share of cluster rewards, so little on so few captures, while Jungle cuts camp damage by 30%. Our Heart holds 917 health at r300 against 1123 and dies twice as often. Variants of `exp/vd1`: `pf1`, Heart skips Prospector first (`P_PROSP_HEART` 0); `pf3`, no champion does (`P_PROSP_FIRST` 0; `vpf0` passed locally on v1498 with no gain and was never played). Local bar, 544 pairs against `exp.vd1` of `multi-015042`: wins not down by more than 0.03, deaths not up by more than 0.3, collected r1000 not down by more than 2 SE, no fault; team gold recorded. Platform rule, on `tt1` against `rf1_tt1@tt1` and the dash result: Heart's deaths r1000 down by at least 1 SE; guards as the dash rule.

**Prospector variants, local result (03:19 IST, `multi-030016`, 544 pairs against `exp.vd1`, no fault read yet).** `pf1`: wins 484 to 469, flips 17 up and 32 down, deaths +0.18 +- 0.14, collected -14.9 +- 12.1. `pf3`: wins 484 to 460, flips 26 up and 50 down, deaths +0.07 +- 0.18, collected -11.4 +- 12.3, captures +1.09 +- 0.37. Neither lowers deaths, and both lose wins, `pf3` beyond the bar. Prospector first stays. Item changes have now lost locally on `wdh1`, `vbd1`, `vh1`, `vh2`, `pf1` and `pf3`.

**`rh6` on `tt1` (03:32 IST, v1541, `data/judge_rh6_tt1.txt`).** Against `rf1_tt1@tt1`, 40 pinned games: wins 8 to 7, flips 1 up and 2 down, margin -58 +- 72. On the 32 default-arm games: Vendetta's deaths r1000 +0.1 +- 0.3 (the metric needed a fall of 1 SE), team deaths +0.7 +- 0.7, tributed -33 +- 39, margin -28 +- 73, her collected -23 +- 18. **It fails: the dash rule stays out.** The cause shows in `dashes.py`: her dashes with an enemy within 4 are 10.6 a game in both runs, and her casts while outnumbered before a death fall only from 1.64 to 1.38. So `dash_strike` is not how she enters these fights. "Dies within 8 rounds of a cast" measured that she was fighting, not that the cast killed her. The local gain (deaths -0.49, four picks -1.42) did not transfer. `vd2`, `vd4` and `vd5` share the rule and are not played.
