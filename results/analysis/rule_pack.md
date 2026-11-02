# Rule for the pack opening (written 11-03 01:40 IST, before the local screen)

Factor: early contact. On `t1503_tm@t03`, 79 of 170 games have a contact by r40 and we win 6 of them. Traces of those games show our team split in the first 16 rounds (Heart of Ruin and Vendetta 12 tiles from Marcella, Willow and Vesper) while the rivals walk as one pack of spread about 6. Allies within 6 before contact: us 2.5-2.83 against 3.04-3.26.

`exp/vpk1` is `exp/vtg70` (group choice toward safe camps early) plus `P_OPENING 1` and a pack rule before `P_PK_R` 60, while no enemy is in sight: all champions take the group of the lowest living teammate, no travel dash, and a champion more than `P_PK_GAP` 2 steps ahead of a teammate on the same group waits.

Local screen: `tools/local/screen.sh pk1 data/runs/multi-003744 pool.v1503 exp/vpk1 11`, the pool of that run, 85 maps, both sides (680 paired games against `pool/v1503`).

Local bar:
- Target: our deaths minus theirs to r300 (`tools/local/ldeaths.py`) down by 1 standard error or more.
- Guards: gems collected to r1000 not down by more than 2 standard errors, wins not down by more than 0.03 a game.
- Mechanism: allies within 6 before r40 up by 0.5 or more on a local decode (the change must do what it says).

Pass goes to the platform on the pinned panel `t03p`, judged there by deaths to r100 and r300 (`early2.py`, `rcmp.py`) against the same-session base. Wins are recorded.

## Result of vpk1, and the near-map form vpk2 (written 11-03 02:00 IST, before vpk2's screen)

vpk1 (data/runs/multi-013848, 680 paired games): deaths minus theirs to r100 -0.15 +- 0.05, to r300 -0.15 +- 0.10, collected -0.6 +- 10, wins -0.031 +- 0.020 (over the 0.03 guard by a hair), team gold r150 -58 +- 10. It misses its guard and is not sent. Split by spawn walk (`tools/local/lnear.py`): near maps (under 61) deaths r100 -0.26 +- 0.08, r300 -0.38 +- 0.15, gold r150 -17 +- 14, wins -0.010 +- 0.026; far maps deaths r300 +0.05 +- 0.14, gold r150 -86 +- 17, wins -0.051 +- 0.040. The pack helps where contact comes early and only costs gold where it does not.

`exp/vpk2` gates every part (group scoring, opening, follow, wait, no dash) on spawns at most 61 walking steps apart. The split was seen before this bar, so the near-map numbers are not a fresh test; the local screen checks the gate works and the guards hold.

Local bar, same pool and maps, paired against `pool/v1503`:
- Target: deaths minus theirs to r300 down by 1 standard error or more over all games.
- Guards: collected to r1000 not down by more than 2 standard errors, wins not down by more than 0.03 a game, no fault.
- Mechanism: every game on a map over 61 steps identical to v1503's (same winner and margin), as the gate removes all the changes there. Allies within 6 before r40 up by 0.5 or more on near maps.

Pass goes to the platform: three parts `t03pa`, `t03pb`, `t03pc`, pinned to `t1503_tm@t03`. Platform bar: our deaths to r300 down by at least one standard error (`paired.py`, `early2.py`), margin not down by more than one standard error, collected r1000 not down by more than one standard error. Wins recorded, not judged.

## vpk2's far maps, and vpk3 (written 11-03 02:25 IST, before vpk3's result)

vpk2 passes the target and guards (data/runs/multi-015136: deaths minus theirs r300 -0.21 +- 0.09, collected -3.5 +- 9.6, wins -0.007 +- 0.016) but not the mechanism: on far maps 02tangle, 02geodes, 00lanes, 00expanse, 02harvest and 01starvation every game changed, with gold r150 -10 +- 5. No behaviour change is active there, so the extra distance field in `World::init` is the suspect. `exp/vpk3` reads the near-map test from the field the central gate already computes. Same bars; the mechanism is judged on the same far maps: games identical to v1503's or the changes explained.

vpk3's result (data/runs/multi-021216): deaths minus theirs r100 -0.19 +- 0.05, r300 -0.20 +- 0.09, collected -3.3 +- 9.6, wins -0.010 +- 0.016, no fault: target and guards pass. Near maps: deaths r300 -0.40 +- 0.15, gold r150 -8 +- 13. The far maps still change (gold r150 -14 +- 5, margin +1 +- 9), so the extra field was not the whole cause. They are explained by `if (fuel() < 120000) return;` and by setup running at the edge of the first turn's 200k: on 02harvest v1503's champions end setup with 12-22k left and vpk3's with 0.3-9k or spilled into round 2, one dash a round later (first difference at r4). Any added cost in `World::init` moves that edge (`tools/local/firstturn.py`, `rule_firstturn.md`). vpk3 goes to the platform: t03pa, t03pb, t03pc, queued 11-03 02:35.
