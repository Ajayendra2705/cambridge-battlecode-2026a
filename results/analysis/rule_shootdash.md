# Rule for Vesper's shot before a retreat dash and for the log-free build (written 11-03 03:08 IST, before the local screen)

**Factor.** Fights: damage dealt in contact. `tools/replay/logacts.py t1503_tm_t03`: within 3 tiles, the largest label is `F:retreat` (29% of champion turns, 77% move away, 1% hit). Vesper hits a champion in 0.44 of her close turns against 0.57 for the rivals' Vesper, and moves away in 0.32 against 0.23. MECHANICS section 3: a dash still works after a ranged basic attack; the walk does not. So a retreating Vesper with her dash ready loses nothing by shooting first.

**Variant `exp/vsd1` (`pool/v1503` + `P_SHOOT_DASH 1`).** A retreating shooter with a dash ready and a target in reach shoots the weakest target, then dashes (no walk that turn).

**Local bar** (`pool/v1503`, same pool and 85 maps, 680 paired). Target: kills minus deaths up by 1 standard error or more. Guards: deaths not up by more than 0.2 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault. Mechanism: label `retreat_shot` fires on maps with Vesper.

**Variant `exp/vnl1` (`pool/v1503` with `BOT_LOGC 0`).** Target: exhausted turns a game down (`fuelExhausted`). Guards as above. Passes only if the target moves; the logs are also the source of `logacts.py`, so a neutral result keeps them.

**Platform.** Only a pass goes on: `t03p` parts pinned to `t1503_tm@t03`; kills minus deaths (`paired.py`) up by 1 standard error or more, margin and collected not down by more than 1 standard error. Wins recorded.

**Results (11-03 03:28 IST, `multi-031107`, 680 paired against `pool/v1503`).**

- `exp/vnl1` passes. Exhausted turns of ours 9.78 to 6.79 a game (`fuelExhausted` events; to r3 3.47 to 3.35; the rivals' stay 10.9). Collected +14.8 +- 7.1, tributed +18.8 +- 7.2, team gold r300 +31.4 +- 11.4, r600 +76, deaths -0.17 +- 0.17, wins +0.01, no fault. One game's fuel per turn (`team-a.fuel`, against cmb7): 00anvil mean 31079 to 26645, 00contest 34273 to 24509, 00breadcrumbs 36450 to 31629. The compact log costs 5000 to 10000 fuel a turn.
- `exp/vsd1` fails: kills +0.03, deaths +0.12 +- 0.13, us minus them r300 -0.05 +- 0.05, wins -0.01. The target did not move.
