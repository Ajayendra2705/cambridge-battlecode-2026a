# bamboo1477 ("H", platform version 1477)

`bots/bamboo458sf` (v1472: #458 + spell finisher) plus two switches, uploaded to Velvet Tributers as **v1477** on 1 Nov 08:01 UTC. The source
is exactly what was submitted. Build it with `cambc build bamboo1477`.

| Switch | What it does |
|---|---|
| `kHurtFirst 4` | in fights, champions within 4 tiles of a visible enemy champion act first within the team, the hurt ones first (ported from `bots/pool/bot_10` `set_turn_priority`) |
| `kHybridWalk 61` | on maps whose spawn-to-spawn walk is longer than 61 steps, the teammates' bot_10 (`src/cj`, namespace `cjb`, taken from `bots/pool/cmb1`) plays the whole game, draft included; our bot everywhere else |

## Results

- Local, vs our pool bots (1,120 games): 839 wins (v1472 801). Vs the teammates' bots vx1 / cmb1 / cmb2 / bot_10 (1,120 games): 721 (v1472 600).
  70 maps x 2 sides stuck scan: 135 / 140 wins.
- Ladder, pinned 30 Oct opponents: quick panel 16 / 55 (v1472 21); full panels A + B 53 vs #458's 54. Not better than v1472 on the ladder.
- Later finding: the start-up spawn walk of `kHybridWalk` costs our own bot about 2.6% on maps where bot_10 never plays (bamboo1478 README).
