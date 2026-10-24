# Bot architecture (`bots/main`)

`bots/main` is the current best bot, ladder bot `dr3` (2026-10-24): `pool/hb4` split into files by concern, plus the batch-b1 changes listed under "Changes since hb4". Read this page before you open the code.

## Game in one paragraph

Two teams of 3-5 champions share a grid map. Neutral camp groups (wolves, elks, monoliths, golems, gem and gold clusters) sit on fixed spawn tiles. You kill a group, stand on its spawn tiles to capture the reward (gems and gold), carry the gems to an altar and tribute them. The first team to tribute 1000 gems wins. At round 2000 the tiebreak is gems, then gold earned, then kills. Gold buys items at your spawn. A champion killed by an enemy drops its whole gem bag to the killer. Every turn has a fuel budget (100k), and every engine call costs fuel. Exact rules and numbers: `docs/MECHANICS.md`.

## Process model

- Each champion runs its own copy of the program (`main.cpp`). There is no central controller.
- State persists between turns in globals, per champion.
- Teammates coordinate only through 8 bytes of shared memory (see "Shared memory" below) and what each one sees.
- `main.cpp` loops forever: `play_draft()` during the draft, otherwise `Bot::play_turn()`, then `end_turn()`. An exception is logged as `bot error: ... at <stage>` and the turn still ends.

## Files

`bot.cpp` is a unity build. It includes the concern files below, in this order, inside one anonymous namespace, then defines `Bot::play_turn()`. The concern files are not standalone headers. They depend on everything included before them, so keep the order.

| File | Concern |
|---|---|
| `main.cpp` | Entry loop: draft or turn, error logging. |
| `draft.cpp` | Draft: on teams of 5 or fewer, picks Heart of Ruin, Vendetta, Vesper, Ryth, Marcella (the top-10 meta). |
| `random.h` | Seeded RNG (WASI randomness is always zero). Currently unused by the turn logic. |
| `core.h` | Constants (`MAX_SLOTS`, `CAMP_RANGE`), `dist` (Chebyshev), debug tracing (`STAGE`, `TRACE`), activity counters (`ACT`). |
| `world.h` | `Group` and `World W`: static map knowledge built once by `init_world()`. Holds camp groups, altars, distance fields (to altars, own spawn, enemy spawn), strong camps, altar guard and team slots. Also holds the observed state of each group (alive / reward ready / respawning, member hp, last awake round). |
| `snapshot.h` | `Snap S`: the per-turn view (self, visible camps, allies, enemies, danger tiles). `FightCoef` reads damage coefficients from ability metadata: `champion_burst` (one round) and `champion_dps` (sustained). |
| `sim.h` | `simulate_fight`: 3-round focus-fire simulation between nearby champions, using live cooldowns, stuns and the Cassi/Issac link. `my_dps`, `my_spell_dps`. |
| `knowledge.h` | Known units (camps by tile, every champion handle). `take_snapshot()` makes one raw engine call per unit. `build_phantoms()` covers unseen camps of recently awake groups. `update_knowledge()` updates group states. |
| `comms.h` | Shared memory: target claims, help call, respawn broadcast, `home_side`. |
| `move.h` | Movement: field descent, dashes, `step_to_tiles`, `step_away`, `step_out_of_danger`, `walk_home` (avoids awake camp reach), `go_home` (recall only when no enemy is near). |
| `shop.h` | Item plan per champion type (Treasure, Durability, Jungle emblems, then Power or Bruiser shards). Also holds capture priority and wealth (owned shards). |
| `abilities.h` | Casting on camps (stun, area hit, landing dash, damage spell) and on champions. Also attack resets, heals, shields, ward placement and basic attacks. |
| `camps.h` | Camp threat and incoming damage, `clear_time` estimate, `standoff` groups (casters hit from spell range 4), `gold_weight`. |
| `enemies.h` | Enemy sightings (per champion, last 40 rounds), the team focus call, and `group_danger`. |
| `state.h` | Banking statistics for the order-quantity rule, per-champion turn state, the death context (`D` line). |
| `targets.h` | `pick_group()` scores every group as value per champion-round. `bank_gems()` walks to an altar, breaks enemy altar locks and tributes. `choose_camp()` picks the camp to hit. |
| `camp_fight.h` | `fight_or_approach()`: wait beside a respawning group, capture, standoff casting, gather for big groups, approach and hit camps. |
| `bot.cpp` | `Bot::play_turn()`: the decision pipeline below. |

## Turn pipeline (`Bot::play_turn`)

Each step either acts and returns, or falls through to the next. The activity name (`ACT`) appears in logs.

1. **First turn only:** `init_world()`, splash and fragile flags.
2. **Logging:** `R` line every 20 rounds, `G` (score) every 10 rounds from slot 0, `A` (activity counts) every 250 rounds.
3. **Dead** (`dead`): print the `D` line, shop, clear the claim and help call.
4. **Busy:** recalling (`recall`), tributing (`tribute`), teleporting. Do nothing.
5. **Read the world:** snapshot, claims, group states, phantoms, respawn broadcast, sightings, death context. Write the help call if an enemy is within 3 on our half.
6. **Ward and spawn:** place the ward towards the enemy approach. At spawn: shop, reset `retreating`.
7. **Damage accounting:** damage taken that camps do not explain is blamed on an unseen camp in range, or else on an unseen enemy. A big hit (>25% hp) prints an `H` line.
8. **Calibration:** `cal_f` scales enemy damage in the simulator when the opponent hits harder than local play (clamped 1-2).
9. **Engage enemy** (`pvp`): choose prey (best dps/hp weighted by its gems, an enemy fighting an ally, or the team focus call). Engage when the simulation says we win, when the prey is nearly dead (`finisher`), when it carries 30+ gems (`rich`), or when we stand on our spawn. A lone 1v1 with a close kill race also counts as winning. Never engage with 150+ gems in the bag.
10. **Threat** (`kite`, `duel`, `flee`): if threatened and losing (outnumbered, weaker, under 40% hp, in kill range, or the simulation says we die), step out of danger when healthy. Duel a lone adjacent chaser only if we kill it first, or if running home is fatal anyway. Otherwise flee home through bushes, hitting whatever is in range, and call focus on the chaser.
11. **Attack on sight:** hit the weakest enemy in reach before anything else.
12. **Heal wait** (`heal_wait`): at spawn below 90% hp.
13. **Camp retreat** (`retreat`, `home_heal`): sum the camps that target us and the steps needed to leave all their reaches. Leave before the next hits could kill. Rejoin if healthy, else go home (bank on the way if an altar is within 3).
14. **Low health** (`home_heal`): below 50% (20% when quiet) with no camp hitting us.
15. **Bank** (`bank`): order-quantity batch `g* = sqrt(2 c tau / (m h))`, where c = collection rate, tau = trip length, h = death plus game-end hazard, and m = loss multiplier for champion kills. Bank at once near the game end (deadline from the enemy's tribute rate), after round 1900, or when the bag would win.
16. **Shop trip** (`shop_trip`): 150+ gold, or 90+ within 8 tiles of spawn.
17. **Answer help** (`help`): healthy, under 100 gems, nothing in view, call 3-14 tiles away on our half.
18. **Target:** re-pick every 3 rounds or when the target's state changes, unless fighting. Write the claim. Then `fight_or_approach` (`resp_wait`, `capture`, `to_capture`, `standoff`, `gather`, `approach`, `fight`), or bank if there is no target.

## Shared memory (8 bytes, all used)

| Bytes | Content | Code |
|---|---|---|
| 0-4 (bits 0-35) | Six 6-bit target claims, slot s at bits 6s..6s+5, value = group + 1 | `write_claim`, `refresh_claims` |
| 0-4 (bits 30-39) | Help call (overlaps the unused slot 5 when the team has 5 or fewer): `(x/3)*22 + y/3 + 1`, 0 = none | `write_help`, `read_help` |
| 5-6 | Respawn broadcast: group + 1, respawn round low byte | `broadcast_respawn`, `read_broadcast` |
| 7 | Team focus call: `(enemy index << 5) | (round & 31)`, expires after 3 rounds | `call_focus`, `focus_target` |

Slot = rank of this champion's handle among allied handles (sorted), set in `init_world`.

## Log lines (stdout, visible in platform replays)

| Line | When | Format |
|---|---|---|
| `R<round> s<slot> ...` | every 20 rounds | type, hp, gems, gold, target, position |
| `G <round> <ours> <theirs>` | slot 0, every 10 rounds | tributed gems both teams |
| `A s<slot> r<round> ...` | round 30 and every 250 | attack/cast counters, rounds per activity |
| `D<round> s<slot> r<last> hp=... <activity> en: type@dist/hp...` | on death | what this champion last saw |
| `H<round> s<slot> ...` | hit for >25% hp in one round | position, damage, camps, enemies with burst |
| `V...` | only in logging variants (`tools/variant/mklog.py`) | per-turn combat state; read by `tools/replay/vana.py`, `dpre2.py` |

Logging costs fuel and changes play. Never put a logging variant (`*l`, for example `hb4l`) on the ladder.

## Design rules that hold everywhere

- **Fuel:** read each unit once per turn through raw `cambc::detail::sdk_*` structs. Accessors such as `is_set`, `get` and `health()` are host calls costing about 40 fuel each.
- **Engine values, not constants:** camp attack ranges, ability damage and cooldowns come from the API. Hard-coded numbers broke at every patch.
- **Camps:** they never regenerate or chase, sleeping camps never attack, and a woken camp hits the nearest champion. Damage dealt is banked: fight until low, step out of reach, heal, return.
- **Danger tiles:** after the engage decision, moves avoid tiles where a visible enemy's one-round burst would exceed 30% of our hp.

## Changes since hb4 (batches b1-b3, 2026-10-24)

- `targets.h` `pick_group`: groups are scored in order of a cheap upper bound (value x side and mid factors over travel + health / our best damage); a group whose bound cannot beat the best is skipped. Same choices as hb4, far less fuel.
- `targets.h` travel fields: one distance field per group (rooted at its camps), built on non-pick turns while 50k+ fuel is left. Walking distance is symmetric, so `travel_fields[g]->get(me)` equals the BFS from us; until all exist the BFS is used.
- `targets.h` futility: `group_invested[g]` counts rounds this champion targeted g since g was last seen down; score / (1 + invested / 150).
- `targets.h` cover: a cluster (no strength) beside sleeping elks is not covered (elks reach 4 since 3.0 and count as covering camps).
- `bot.cpp` camp retreat: rejoin only with health for the target group's remaining strength, shared by its claimants, for range + 2 rounds.
- `bot.cpp` bank: the order-quantity trip cost is the detour through the altar on the way to the target (from the travel fields), not a round trip.
- `targets.h` middle bonus (x2 for mid groups before r400) only on teams of 5 (fx1): small teams lost the early middle fights.
- `camps.h`: `clear_stats` range and the static part of `standoff` are cached per group (`static_range`, `static_standoff`).
- `targets.h` (dr3): the middle bonus for full teams lasts only until this champion has been killed by an enemy; contested groups (side > -3) score / (1 + deaths to enemies in the last 400 rounds).
- `bot.cpp` (dr3): prey is the lowest-health enemy in reach. `sim.h`: `cached_slots` reads each champion's ability slots once per round.
- `draft.cpp` (dr3): teams of 5 or fewer draft Heart of Ruin, Vendetta, Vesper, Varg, Marcella (Varg replaced Ryth).

## Known leftovers (harmless)

- `bot.cpp`: an `if (false)` feature-log block and comments naming deleted tools (`hazard.py`, `calib.py`; source in tag `archive/pre-cleanup`).
- `targets.h`: `capture_priority` check compares against `16 * 16` and never fires. A dead `recent` loop and two orphan comments about the altar guard.
- `enemies.h`: unused `shared_sighting_seen` and `first`.
- `shop.h`: `burst_caster` is computed and unused.

Removing any of these changes the wasm. Do it in a variant and test it like any other change.
