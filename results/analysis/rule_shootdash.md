# Rule for Vesper's shot before a retreat dash and for the log-free build (written 11-03 03:20 IST, before the local screen)

**Factor.** Fights: damage dealt in contact. `tools/replay/logacts.py t1503_tm_t03`: within 3 tiles, the largest label is `F:retreat` (29% of champion turns, 77% move away, 1% hit). Vesper hits a champion in 0.44 of her close turns against 0.57 for the rivals' Vesper, and moves away in 0.32 against 0.23. MECHANICS section 3: a dash still works after a ranged basic attack; the walk does not. So a retreating Vesper with her dash ready loses nothing by shooting first.

**Variant `exp/vsd1` (`pool/v1503` + `P_SHOOT_DASH 1`).** A retreating shooter with a dash ready and a target in reach shoots the weakest target, then dashes (no walk that turn).

**Local bar** (`pool/v1503`, same pool and 85 maps, 680 paired). Target: kills minus deaths up by 1 standard error or more. Guards: deaths not up by more than 0.2 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault. Mechanism: label `retreat_shot` fires on maps with Vesper.

**Variant `exp/vnl1` (`pool/v1503` with `BOT_LOGC 0`).** Target: exhausted turns a game down (`fuelExhausted`). Guards as above. Passes only if the target moves; the logs are also the source of `logacts.py`, so a neutral result keeps them.

**Platform.** Only a pass goes on: `t03p` parts pinned to `t1503_tm@t03`; kills minus deaths (`paired.py`) up by 1 standard error or more, margin and collected not down by more than 1 standard error. Wins recorded.
