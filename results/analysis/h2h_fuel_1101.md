# Head to head over fuel values, 2026-11-01 (local, branch night-1101)

Three measurements, each with its reading rule written before its games (copied here unchanged), then the result.
Games: `tools/local/multi.py --fuel N` (N = 99000, 99500, 100500, 101000) plus the default-fuel games. Shares are
the first bot's wins, with the standard error over (map, side) clusters (`tools/local/h2hfuel.py`, logic below).

## Five a side

> Reading rule for the five-a-side head-to-head enlargement (written 07:59 IST 11-01, before any of its games; local
> only; a measurement, not a variant).
> 
> Question: which bot should hold the five-a-side slot by head to head: bot_10 (b10n) or a Bamboo bot? Locally the pool
> favours b10n (210 of 252 against 183 for the Sprint 3 bot), but the pool is vx1's ancestors and the ladder rates the
> Sprint 3 bot higher five a side than the pool does. Head to head is level so far (b10n 44 of 84 against bamboo458sf,
> 43 of 84 against bamboo8).
> 
> Games: exp/b10n against bamboo458sf and bamboo8 on the 42 five-a-side maps, both sides, at fuel per turn 99000, 99500,
> 100500 and 101000 (multi.py --fuel; each value replays every pairing on another path), plus the default-fuel games
> already played (bamboo458sf: multi-062416; bamboo8: multi-044220). 420 games per pairing.
> 
> Reading: b10n's win share per pairing, with the standard error over the 84 (map, side) clusters (each cluster's mean
> over its five fuel values is one observation, since a map's advantage repeats across fuel values). Above 0.5 by more
> than one standard error: the head to head supports b10n five a side. Below 0.5 by more than one: it supports the Bamboo
> bot. Otherwise level, and the pool's verdict (b10n) stands as the local pick, with the platform to settle it.

Result: bot_10 (b10n) against bamboo458sf 235 of 420, 0.560 +- 0.041 (supports bot_10); against bamboo8 220 of 420,
0.524 +- 0.041 (level). Runs `data/runs/multi-080001`, `-080156`, `-080355`, `-080556`; default games
`multi-062416` and `multi-044220`.

## Three a side

> Reading rule for the three-a-side head-to-head enlargement (written 08:02 IST 11-01, before any of its games; local
> only; a measurement, not a variant).
> 
> Question: three a side, vx1 (cmb7's pick by the pool guard) or the Sprint 3 bot (bamboo458sf)? Over the six opponents
> the Sprint 3 bot was +0.056 +- 0.052, but -0.069 +- 0.067 against the pool; head to head vx1 won 9 of 24.
> 
> Games: main (vx1) against bamboo458sf on the 12 three-a-side maps, both sides, at fuel per turn 99000, 99500, 100500
> and 101000, plus the default-fuel games (multi-062416, bamboo458sf against main). 120 games.
> 
> Reading: vx1's win share with the standard error over the 24 (map, side) clusters. Below 0.5 by more than one standard
> error: the head to head supports the Sprint 3 bot three a side, and cmb9 (the Sprint 3 bot three and four a side,
> bot_10 five a side) becomes the platform alternative to cmb7. Otherwise cmb7 stays as built.

Result: vx1 against bamboo458sf 56 of 120, 0.467 +- 0.077 (level): cmb7 stays as built. Runs `multi-080809` to
`-080908`; default games `multi-062416`.

## Four a side

> Reading rule for the four-a-side head-to-head enlargement (written 08:10 IST 11-01, before any of its games; local
> only; a measurement, not a variant).
> 
> Question: is the Sprint 3 bot (bamboo458sf) the right four-a-side pick? By row bamboo458sf's rule it beat vx1 by
> +0.052 +- 0.040 over the six opponents (the narrowest pass of the night); head to head 21 of 32 against vx1 and 16 of
> 32 against b10n.
> 
> Games: bamboo458sf against main (vx1) and exp/b10n on the 16 four-a-side maps, both sides, at fuel per turn 99000,
> 99500, 100500 and 101000, plus the default-fuel games (multi-062416). 160 games a pairing.
> 
> Reading: the Sprint 3 bot's share against each, standard error over the 32 (map, side) clusters. Against vx1 above 0.5
> by more than one standard error: the head to head supports the pick. Below 0.5 by more than one against either bot:
> the head to head favours that bot four a side, and the pick is reopened with that bot. Otherwise the pick stands.

Result: bamboo458sf against vx1 104 of 160, 0.650 +- 0.061 (supports the pick); against bot_10 90 of 160, 0.562 +-
0.063 (level). Runs `multi-081059` to `-081316`; default games `multi-062416`.

## Standard error

Each (map, side) cluster's mean over its fuel values is one observation; the share is the mean of the cluster means
and its standard error is their standard deviation over the square root of the number of clusters. A map's
advantage repeats across fuel values, so counting every game as independent would understate the error.
