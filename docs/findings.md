# Findings

Measured facts that shaped the bot, and what we know about stronger teams. Exact engine numbers live in `docs/MECHANICS.md`. The raw dated logs these come from are in `docs/journal/`.

## Engine and fuel

- The engine is deterministic: the same bots on the same map give the same result, locally and on the platform.
- Every SDK accessor is a host call (about 40 fuel). Read raw structs (`cambc::detail::sdk_champion`, `sdk_camp`) once per unit per turn. Printing is expensive too: heavy per-turn logging cost a bot 18k gem margin locally.
- Always test with `--release`, because the platform runs release builds.
- Our champions hit fuel exhaustion about 10 times per game, against about 4 for rivals, mostly on big maps. `pick_group`'s BFS costs about 45k fuel.
- `init_world` spreads over the first rounds.
- Fight-turn fuel (probe `exp/fuelm`, hb4 code, 32 local games vs hb4/tf3 on 8 maps, 2026-10-24): turns with a prey use 41.7k on average (p50 41k, p90 56k, p99 70k, max 88k). Building the sim inputs costs 10k (max 44k) and `simulate_fight` 4.5k (max 11k), with 3.7 units on average. `fuel_remaining()` costs 6 fuel.
- Small dense nets cost about 7 fuel per multiply-add as written (scalar loops, no vectorisation): a set encoder with phi 6->16 and head 32->16->1 cost 6.8k on average (max 9.3k), and a 2-layer phi 6->16->16 cost 13.9k (max 47k incl. first-call weight init). Clang `-O3 -msimd128` only half-vectorises dot-product loops (`a += W[j][k] * x[k]`), because it may not reorder float adds. Transposed weights with explicit `wasm_simd128.h` axpy loops (`acc[j] += W[k][j] * x[k]`) cut this to 2.9k (max 3.7k) and 7.0k (max 16k), with outputs equal to the scalar nets within 6e-8.

## Camps and economy

- Camps never regenerate or chase. A whole group wakes when one member is hit. A woken camp hits the nearest champion, not the one that woke it. Sleeping camps never attack, even adjacent. Camps fall asleep 2 rounds after no champion is in range.
- Spells reach 4. Camps reach 3, except elks 4, golems 4 and monoliths 5. Casters standing at 4 from range-3 camps take no damage ("standoff").
- Standing on a group's spawn tile blocks its respawn indefinitely.
- Gold gap against the top 10: 79% comes from captures (68 vs 40 clears per game, same ~118 gold per clear) and 21% from kills (kill = 100 gold, assist = 0).
- Opponents capture many small groups and gold clusters near their spawn every 80-110 rounds. Top teams tribute about every 32 gems; our order-quantity batch gives 60-100.
- Items: health emblems matter (all-Power builds lost on the platform). Top teams build Bruiser everywhere, HoR on focus, Marcella on focus (15 focus per shard, spell 2x focus). They buy Monster shards 7-14 per game and altar locks about 4-6 per game. We buy none of either.

## PvP

- Most of our deaths happen while fleeing (51-80% depending on the bot). The typical fatal engagement starts near full hp while walking to a capture, with about 2 allies and 0.8 enemies within 5. It ends 14 rounds later with 0.7-1.8 allies against 2.1-2.5 enemies: their teammates join and ours do not.
- Per-turn 1v1 damage is equal to rivals. Total champion damage is lower only because we die and flee more.
- Ryth and Marcella were starved of gold by slot-order capture sharing. `gb2` fixed it by sharing by fewest owned shards. Overfeeding one champion (gb3) was wasted.
- Platform opponents punish aggression that local bots reward. Blind no-flee play (nf2, ag*) and looser fight entry (pa1, lf1) lost on the platform. Current fight thresholds look like a local optimum both ways (tighter bpt1/bpt2 is also worse).
- Widening the help call made things worse (hc2: whole map 5/20 vs 10/20).

## Maps

- `boss_battle`: the single altar is walled in by a group of 2 monoliths (40000 hp). Nobody can tribute until it dies, so we skip bank trips while it lives (`altar_guard`). Rivals kill it. We have no team monolith assault yet (ag1/ag2 failed).
- `contest`: the only gems are two sleeping monoliths. The enemy farms the 4 centre gold clusters beside them, so we now treat sleeping monoliths as harmless.
- `elk_arena`: all 72 gems are in the centre group. The enemy 5-stack meets us there at rounds 17-30, and we arrive one by one.
- Maps we lose almost every game (panel 8): elk_arena, boss_battle, lanes, contest, starfish, quadrants. Earlier panels: the_farm, starvation, road_of_riches, lost_world, gemfight, hooks. Map facts are in `docs/reference/probe/map_table.md` (gem income per round 1.2-15.7; some maps cannot reach 1000).

## What top teams do (platform summaries, ranks 1-70)

- Attack on sight at the lowest-hp target in range, spells included. They chase 3 turns at most and recall at about 46% hp, never with an enemy within 4.
- They place wards constantly (100-280 per game) and farm in packs early, then fan out.
- Draft meta: Heart of Ruin, Marcella, Vesper, Ryth, Vendetta (in 63-76% of top-10 drafts).
- Kill participation is similar to ours (3+ participants in about 60% of kills). They win fights by numbers arriving and by not fleeing late.

## Testing lessons

See `docs/WORKFLOW.md`. In short: local results do not predict the platform for fighting, items or draft. Always run the base at the same time. Never select games by past result. Judge every fix by its own target metric as well as by wins.

## Outside references

Past postmortems and rival repositories (including measured top-team policies from decoded replays) are listed in `docs/journal/references.md`.
