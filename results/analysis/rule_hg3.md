# One small factor: gold clusters taken early, three a side (hg3a, hg3b, hg3c)

Written Sun, Nov  1, 2026, 21:14 IST, before any hg3 game (local or platform).

## Factor

Gold clusters killed by r300 (`decoded.py gold`, "camp kills per game to r300", side that hit last), three a side.
On panel b40 (1478 as live, 90 games against ranks 18-38) we kill 13.2 a game, the rivals 24.9; in 17 ranked
three-a-side games of 1472 against teams above us 13.7 against 21.6; locally against the pool (hy1, 72 games) 13.7
against 22.6. Team gold at r300 on b40: 876 against 1,199. Gold buys the first emblems.

## Change (one constant)

The Bamboo part values a gold piece at `kGoldWeightEarly` (0.3) gems at round 0, fading to `kGoldWeight` (0.12) by
r800 (Vesper x3, Vendetta and Varg x3.5). The variants use another round-0 weight three a side only (`kGoldEarly3`):
hg3a 0.45, hg3b 0.6, hg3c 0.9. Everything else is hy1 (our copy of 1478); four and five a side are unchanged.

## Local rule (12 three-a-side maps x pool/cand1, cp3, dh3 x 2 sides = 72 games each, paired with hy1 in
`data/runs/multi-195654`, local games replay exactly)

Target: gold clusters by r300 up by at least 4 a game. Guards: gems collected to r1000 (`econpair.py`) not down by
more than one standard error and not below -20 a game; deaths not up by more than 0.3 a game; no bot fault. The
smallest weight that meets the target with the guards goes to the platform. None meets it: stop, record, no gate.

## Platform rule (b40p, pinned to `l1478_b40@b40`; paired game by game)

Target: gold clusters by r300 up by at least 3 a game. Guards: our gems collected to r1000 (`paired.py`) not down by
more than one standard error; deaths to r1000 not up by more than 0.3; team gold at r600 not down. Wins are recorded,
not judged. A run during which the active version changed by someone else's hand is void.
