# Rule for light camps first in the opening (written 11-03 03:25 IST, before the local screen)

**Factor.** Early team gold. On `t1503_tm@t03` plus `base1503_s3p@s3p` (`tools/replay/mapgap.py`) team gold at r300 is under 0.4 of the rivals' on 12 maps, and under 0.2 on four. On 01corridors (trace `9648827e`) our whole team walks to one heavy group and takes 260 gold at r81, then no one else earns until r126; the rivals send a pair and a lone champion to clusters and hold 259 gold by r60, and they make 13 captures to r300 against our 5. Our Vesper still has 0 gold at r420 in that game. Over the 170 games: 16.0 captures against 12.2 to r300 (`decoded.py captures`). Bamboo's study found the same gap against Fish: light camps 15.3 against 25.7 a game (`docs/bamboo/knowledge/recall-cycle-1031.md`).

**Cause in the code.** `choose_task` in `farm.cpp`: a heavy group that needs helpers scores `P_ENABLE` (1.6) times, and each champion's score is split among the `n_team` the group needs, so the team piles on.

**Variants on `pool/v1503`.** Before round `P_LIGHT_R`: harmless groups (clusters only, `g.dps` 0) count `P_LIGHT_W` times and the enabler multiplier is `P_ENABLE_EARLY`.

| Variant | `P_LIGHT_W` | `P_ENABLE_EARLY` | `P_LIGHT_R` |
|---|---|---|---|
| `exp/vlc1` | 1.5 | 1.6 | 150 |
| `exp/vlc2` | 1 | 1 | 150 |
| `exp/vlc3` | 1.5 | 1 | 150 |
| `exp/vlc4` | 2 | 1 | 250 |

**Local bar** (`pool/v1503`, same pool and 85 maps, 680 paired). Target: team gold at r300 up by 1 standard error or more (`lgold2.py`). Guards: deaths not up by more than 0.3 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault.

**Platform.** Only a pass goes on: `t03p` parts pinned to `t1503_tm@t03`. Target: team gold at r300 up by 1 standard error or more (`decoded.py gold`, paired where possible); margin and collected not down by more than 1 standard error. Wins recorded.
