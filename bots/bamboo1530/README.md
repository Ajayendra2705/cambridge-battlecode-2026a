# bamboo1530 (v1523 + review fixes, capture hits, crystal threshold, Fish pack on 3-4 picks; platform version 1530)

`bots/bamboo1523` plus the switches below, uploaded to Velvet Tributers as **v1530** on 3 Nov 08:14 UTC (note "Bamboo R15b: v1523+siege
fixes+capture hits+TP>=8 rounds+Fish pack (3-4 picks)"); live since 08:28 UTC. The source is exactly what was submitted. Build it with
`cambc build bamboo1530`. All switches are `P_*` macros in `src/params.h` with the edit script named in their comments.

| Switch | What it does |
|---|---|
| `P_SPAWN_SIEGE_HP` (rename) | fixes bamboo1523's macro clash: the team siege on gated / heavy maps needs 3000 max health or round 900 again |
| `P_FIX_SIEGE 1` | the spawn siege only within 10 steps of home, never off a capture or fight of the champion's own task, only while a spawn tile in reach is free (mates out of sight counted by their task slots); the spawn hit checks health before waking a group; the walk home uses the spawn field (fuel guard) |
| `P_FIX_PIN 1` | "heal fully first" on the spawn no longer pins a champion that an awake camp hits every round: healed last turn and >= 75% health, it goes on; "low" on the spawn it hits from the tile |
| `P_CAP_HIT 1` | a capture is not a channel: on a capture tile the unused attack hits the weakest enemy champion in reach, else a cluster or an awake monster (never a sleeping hostile group) |
| `P_TP_GAIN 6` | teleport crystals only when they save at least 8 rounds of walking (was 5) |
| `P_ELK_CHAIN 10`, `P_ELK_FISH 1`, `P_ELK_UNTIL 120`, `P_ELK_MAXN 4` | on elk maps (>= 2 team-killable elk groups on our half within 40 of the spawn) with at most 4 allies, the whole team works the nearest heavy groups together (elk, 2+ wolves, golem) through the opening code, comes back to them as they respawn, and returns to normal routes at round 120 - Fish's opening, measured in Fish's replays |
| `P_FIX_NAV 0`, `P_FIX_RPK 0` | two more review fixes, off (they changed many games for nothing measurable locally) |

## Results

- Local (5 pool bots, 86 maps, 860 games, paired with v1523): 648 wins, margin +17 +- 9 (v1523 643). The siege-health fix alone was
  661 wins, +5 +- 3. The Fish pack on 3-4-pick elk maps: +39 +- 32 a map against 7 other opponents (independent of the first screen).
- Ladder half panel (same 80 games as bamboo1523's): 24 wins (margin -26,560) against v1523's 22; flips 5 to a win, 3 to a loss.
- Stress gate (24 local games): 22 wins, 0 faults, no stuck champions, 2 fuel-limit turns.
