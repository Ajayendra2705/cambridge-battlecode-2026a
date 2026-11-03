# Gold on the enemy half (11-03 15:10 IST)

Against hard neighbours the far half gives 87 / 316 gold a game by r600 (`capkinds.py`, `docs/findings.md`, "Gold against the neighbours"), so about 229 of the 600 gold gap is taken on our half. `P_ENEMY_SIDE_W` halves a group's value on the enemy half and has not been tested on this code line. Variants: `esw75` (0.75), `esw100` (1.0), on `exp.b30`, one change each.

**Local bar (680 paired against `exp.b30`, before the screen).** The factor is team gold at r600: up by at least 1 SE. Guards: deaths not up by more than 0.3, collected not down by more than 2 SE, margin not down by more than 1 SE, no fault. Wins are recorded and not judged.

`pk5` (`P_ELK_MAXN` 6: the elk pack on five picks too): v1530's author measured no gain on five picks. Same bar, on five-pick maps. It goes on the same run because the change is one constant.
