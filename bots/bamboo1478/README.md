# bamboo1478 (v1472 + bot_10 on far maps, platform version 1478)

`bots/bamboo458sf` (v1472) plus `kHybridWalk 61`, uploaded to Velvet Tributers as **v1478** on 1 Nov 08:29 UTC (note "Bamboo v1472 + bot_10 on
far maps (hybrid 61)"). The source is exactly what was submitted. Build it with `cambc build bamboo1478`.

`kHybridWalk 61`: `main()` computes the walking steps from our spawn to theirs; above 61 the teammates' bot_10 (`src/cj`, namespace `cjb`,
from `bots/pool/cmb1`) plays the whole game, draft included, otherwise our bot. Local tests against a common field (our pool + vx1, all 70
maps x 2 sides) had bot_10 better on far maps (175 vs 152 of 220 games, ~10% faster gem farming) and our bot better on near maps.

## Results

- Ladder quick panel (pinned 30 Oct top-10 opponents + Fish): 15 / 55, below v1472's 21. Far-map games 4 / 14 for both versions; near-map
  games 10 / 36 vs v1472's 17.
- The near-map loss is the hybrid's own cost: with `kHybridWalk 999` (the walk runs, bot_10 never plays) our bot lost 29 of 1,104 near-map
  games locally against the same build without it. The walk runs at program start, probably cutting into the draft turn's map-plan work.
  Shelved; a fix would take the spawn walk from the draft plan instead of computing it again.
- The teammates' 39-group panel (their v1476 window, same opponent bots via `--source-group`), 100 paired games: v1476 22 wins, v1478 20.
