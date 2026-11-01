# bamboo1479 (v1472 + pre-started recall, platform version 1479)

`bots/bamboo458sf` (v1472: #458 + spell finisher) plus the switches below, uploaded to Velvet Tributers as **v1479** on 1 Nov 10:09 UTC (note
"Bamboo v1472 + pre-started recall + field-first guards + wait-avoid 30"). Built from the same Bamboo source as v1472, without the hybrid code.
The source is exactly what was submitted. Build it with `cambc build bamboo1479`.

| Switch | What it does |
|---|---|
| `kEarlyRecall` | the top teams' pre-started recall: start a recall at the turn end when the next turn would head home anyway |
| `kFieldFirst` + `kFieldFirstGuard` + `kFieldFirstStill 6` | a path field step() could not afford is built first next turn, only after 6 rounds within one tile (fixes the 01islands stall the recall exposed) |
| `kWaitAvoid 30` | after a party wait expires, the camp is avoided 30 rounds, so followers farm alone instead of re-adopting their leader's camp (01the_farm replay 38a369da: two champions waited ~60 rounds while the leader banked and shopped) |

## Results

- Local: on a v1478 base the recall set was +35 / +27 wins (pool / teammates' bots); on the plain v1472 base earlier it was -24. Builds of
  near-identical bots swing by +-25-35 wins locally, so the ladder decides.
- Ladder: a quick panel against the opponents' latest bots (not the pinned 30 Oct versions), paired with v1472 on the same groups, is in
  progress.
