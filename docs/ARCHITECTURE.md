# Bot architecture (`bots/main`)

`bots/main` is the current best bot, ladder bot `m4` (2026-10-26 07:50 IST, version 734): `pool/hb4` split into files by concern, plus the changes listed under "Changes since hb4" (up to `dr3`), "Changes in cp3" (the Sprint 2 entry, now `bots/pool/cp3`), "Changes in cand1" (now `bots/pool/cand1`), "Changes in fd2z" (now `bots/pool/fd2z`) and "Changes in m4". Read this page before you open the code.

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
| `draft.cpp` | Draft: on teams of 5 or fewer, picks Heart of Ruin, Vendetta, Vesper, Varg, Marcella (Varg replaced Ryth in dr3). |
| `random.h` | Seeded RNG (WASI randomness is always zero). Currently unused by the turn logic. |
| `core.h` | Constants (`MAX_SLOTS`, `CAMP_RANGE`), `dist` (Chebyshev), debug tracing (`STAGE`, `TRACE`), activity counters (`ACT`). |
| `world.h` | `Group` and `World W`: static map knowledge built once by `init_world()`. Holds camp groups, altars, distance fields (to altars, own spawn, enemy spawn), strong camps, altar guard and team slots. Also holds the observed state of each group (alive / reward ready / respawning, member hp, last awake round). |
| `snapshot.h` | `Snap S`: the per-turn view (self, visible camps, allies, enemies, danger tiles). `FightCoef` reads damage coefficients from ability metadata: `champion_burst` (one round) and `champion_dps` (sustained). |
| `sim.h` | `simulate_fight`: 3-round focus-fire simulation between nearby champions, using live cooldowns, stuns and the Cassi/Issac link. `my_dps`, `my_spell_dps`. |
| `knowledge.h` | Known units (camps by tile, every champion handle). `take_snapshot()` makes one raw engine call per unit. `build_phantoms()` covers unseen camps of recently awake groups. `update_knowledge()` updates group states. |
| `comms.h` | Shared memory: target claims, help call, respawn broadcast, `home_side`. |
| `move.h` | Movement: field descent, dashes, `step_to_tiles`, `step_away`, `step_out_of_danger`, `walk_home` (avoids awake camp reach), `go_home` (recall only when no enemy is near). |
| `shop.h` | Items: the Treasure emblem first, then each emblem chosen by its fight-power gain (Power, Bruiser, Durability, Jungle; see "Changes in cp3"). Also holds capture priority and wealth (owned shards). |
| `abilities.h` | Casting on camps (stun, area hit, landing dash, damage spell) and on champions. Also attack resets, heals, shields, ward placement and basic attacks. |
| `camps.h` | Camp threat and incoming damage, `clear_time` estimate, `standoff` groups (casters hit from spell range 4), `gold_weight`. |
| `enemies.h` | Enemy sightings (per champion, last 40 rounds), the team focus call, and `group_danger`. |
| `state.h` | Banking statistics for the order-quantity rule, per-champion turn state, the death context (`D` line). |
| `targets.h` | `pick_group()` scores every group as value per champion-round and decides who captures a defeated group. `bank_gems()` walks to an altar (unless the altar guard blocks it), breaks enemy altar locks and tributes. `choose_camp()` picks the camp to hit. |
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
10. **Threat** (`kite`, `duel`, `flee`): if threatened and losing (outnumbered, weaker, under 40% hp, in kill range, or the simulation says we die), step out of danger when healthy, first hitting the weakest enemy in reach if the hit is free (melee keeps its move; a target out of its own reach cannot answer). Duel a lone adjacent chaser only if we kill it first, or if running home is fatal anyway. Otherwise flee home through bushes: melee first hits the weakest adjacent enemy, then the run hits whatever is in range, and calls focus on the chaser.
11. **Attack on sight:** hit the weakest enemy in reach before anything else. Vendetta first dashes next to an enemy 2-3 tiles away when the simulation does not say she dies. Ranged champions shoot when healthy, when the target cannot reach them, or when the enemies near cannot burst them this round.
12. **Heal wait** (`heal_wait`): at spawn below 90% hp.
13. **Camp retreat** (`retreat`, `home_heal`): sum the camps that target us and the steps needed to leave all their reaches. Leave before the next hits could kill. Rejoin if healthy, else go home (bank on the way if an altar is within 3).
14. **Low health** (`home_heal`): below 50% (20% when quiet) with no camp hitting us.
15. **Bank** (`bank`): order-quantity batch `g* = sqrt(2 * 3 * c^2 * tau / (m h + lambda c / 5))`, where c = collection rate (gems per round), tau = trip length (detour past the altar plus the channel), x3 = measured overhead of a trip, h = death plus game-end hazard, m = loss multiplier for champion kills, and lambda = fitted chance per turn that a tribute channel breaks (0.0065 + 0.009 per enemy within 10 of an altar). Bank at once near the game end (deadline from the enemy's tribute rate), after round 1900, or when the bag would win.
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
| `R<round> s<slot> ...` | every 100 rounds, and on death | type, hp, gems, gold, target, position (integers only) |
| `G <round> <ours> <theirs>` | slot 0, every 100 rounds | tributed gems both teams |
| `A s<slot> r<round> ...` | round 30 and every 250 | attack/cast counters, rounds per activity |
| `D<round> s<slot> r<last> hp=... <activity> en: type@dist/hp...` | on death | what this champion last saw |
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

## Changes in cp3 (ladder bot from 2026-10-25 03:09 IST)

cp3 = dr3 plus these layers, each with its experiments row (batches b5 and b6):

- `targets.h` (ge4): gold counts `gold_weight(round)` also before the first emblem (no x2), and the mid-push x2 bonus is off. Collection by r300 went from 108 to 140 on b5 (rivals 127).
- `targets.h` `bank_gems` (ab1, ab2): the altar guard blocks banking only while a guard camp next to an altar is alive in our knowledge, and never within 100 rounds of an enemy tribute (an enemy tribute means a tile is free).
- `bot.cpp` threat branch (fh1): before kiting away, hit the weakest enemy in reach when the hit is free (melee keeps its move; a target out of its own reach cannot answer). Attack on sight: ranged champions also shoot targets that cannot reach them.
- `bot.cpp` flee (fh2): melee hits the weakest adjacent enemy before running home.
- `bot.cpp` bank (ef3): order quantity `g* = sqrt(2 * 3 * c^2 * tau / (m * h + lambda * c / 5))`; the trip costs c x tau gems of lost collection (the old form dropped one c), x3 for the measured overhead of breaking the farming flow, and lambda = 0.0065 + 0.009 per enemy within 10 of an altar is the fitted chance per turn that a tribute channel breaks.
- `shop.h` (sp1, sp3): after the Treasure emblem each emblem is chosen by its fight-power gain: Power 6 gm / main, Bruiser 5 gm / main + gh / hp, Durability 5 gh / hp (+0.11 for the first), Jungle 5 gh / hp (+0.15 for the first). An emblem is finished once started (its bonus comes on completion).
- `targets.h` capture (cp1): the `capture_priority` rule now runs (it compared against the constant `16 * 16` before). The claimant whose passive adds most captures: Vesper +33% of the gold, Marcella +2 gold per gem; then damage growth, then slot.
- `bot.cpp` attack on sight (cp2, cp3): hurt ranged champions shoot unless the enemies near can burst them this round; Vendetta dashes next to an enemy 2-3 tiles away and hits, when past the flee branch and the simulation does not say she dies.

## Changes in cand1 (ladder bot from 2026-10-25 17:05 IST)

cand1 = cp3 plus the bug-fix line bf1-bf7 (found by the check builds au1-au9) and two accepted layers, each with its experiments row:

- `abilities.h` (bf1, bf4, bf5): dash landings come from `reachable_tiles` (walls, altars and units block the path, holes do not); an attack reset is cast only after a spent basic attack and retargets to the weakest enemy champion, else the weakest awake camp, when the target died; spells check that their target is alive and in reach; rooting spells are not cast after a walk; Marcella's damage spell takes the weakest enemy in range when the prey is out of range; Vendetta steps in at 2 tiles (step, hit, reset) and dashes only at 3.
- `bot.cpp` (bf2, bf3): a free hit at the end of the turn with any attack left unused (the weakest enemy champion in reach, else the weakest awake camp that no enemy is nearer to), from our real tile.
- `bot.cpp` (bf4, bf5, bf6): stunned turns return early; a turn that ends on an enemy danger tile without having walked steps out; every action helper refuses once the round changed since the snapshot (a turn that ran out of fuel resumes next round on a stale snapshot).
- `snapshot.h`, `knowledge.h` (bf2, bf4, bf7): champion occupancy from `champion_tiles()`, refused tiles marked occupied; alive checks from raw state structs; the view read once per turn into a per-tile round stamp and visible camp health into a per-camp array.
- `move.h` (bf6): local paths route around enemy danger tiles; local searches are skipped below 20k fuel. `targets.h` (bf6): a target whose way stayed blocked two turns is skipped for 20 rounds.
- `world.h` (bf4): the group route field is rebuilt when the set of live monoliths and golems changes (it was built once).
- `comms.h` (bf2, bf4): the help-call cell size is fitted to the map; the focus byte stores index + 1.
- `sim.h` (bf4): spell reads of champions out of view are skipped; each spell's real reach is used.
- `world.h`, `knowledge.h`, `targets.h`, `bot.cpp` (bf7, fuel): camp design stats read once per kind; group vectors reserved; covered-by pairs pre-checked by bounding box; a pick waits a turn below 45k fuel (plus a field's cost until the travel fields exist), and a target that changed state on such a turn is dropped for that turn; travel fields built several per turn at their measured cost.
- `targets.h` capture claim (wc1): the solo capture goes to the claimant for whom the gold adds most, (gold + passive bonus) / (wealth in shards + 10); cp3 gave every solo capture to Vesper.
- `shop.h` (hr1): Heart of Ruin values Bruiser-focus's strength growth (its basic attack scales with strength).

Decoded on b56 (78 games, by r1000, against base1025c = cp3 in the same session): champion damage per game Heart of Ruin 4090 (3172), Vendetta 3676 (2657), Varg 2637 (2030); Vesper deaths 1.60 (1.21) and gems 162 (240).

## Changes in fd2z (ladder bot from 2026-10-26 02:14 IST)

fd2z = cand1 plus the audit line cand6 (check builds au10-au17, probes pf7-pf18) and two changes from plan8 (fd2's flee dash, fz1's fight-turn fuel fixes), each with its experiments row:

- `move.h` (cand3): one move per turn in `safe_move`; occupancy read again after our own move or dash, before the next move or landing; our own `walk_towards` (around tiles known to be held, never onto a held goal); a group route that reads unreachable at our tile opens the strong-camp reach we stand in and closes it again once we are out; the local-search fuel guard follows the measured worst cost (decaying maximum + 5k) instead of a fixed 20k; the respawn-wait loop checks that the move is still unused.
- `abilities.h` (cand3): the attack reset checks the round right before casting.
- `bot.cpp` (cand3): status lines every 100 rounds, integers only (one line cost 13k fuel).
- `snapshot.h`, `knowledge.h` (cand3, cand4: fuel): the view is read as packed bits in one call (`export_linear_buffer`) instead of a round stamp on every visible tile; awake camps get a round stamp per camp; the knowledge update skips groups outside the view's rows; phantoms are built group by group.
- `snapshot.h` (cand6): `stale()` is also true under 1000 fuel left.
- `abilities.h`, `move.h`, `sim.h`, `targets.h` (cand6): every action that follows a search (dashes, casts, attacks, ward, tribute, recall) checks `stale()` right before the call, and `read_slots` stops when stale; occupancy is read again after placing a ward; dash paths are closed at enemy spawn tiles.
- `bot.cpp` (cand4, cand6: opening): the opening turn ends after a setup that leaves under 50k fuel, or under 80k when the setup ran into a later round; no camp fight starts under 15k fuel (the turn ends instead).
- `bot.cpp` (fd2): a fleeing champion with a dash ready dashes first, to the landing closer to home that ends farthest from the enemies and outside awake camps' reach, then walks.
- `bot.cpp`, `sim.h` (fz1): the big-hit `H` log line is gone (37.6k fuel a line); the fight simulator keeps its unit buffers across turns and `simulate_fight` works on a reused copy.
- `shop.h` (gs1, 10-26 03:15): per-shard growth comes from the engine (`self().base_stats()`, read once) instead of a hard-coded table, so the Sprint 3 growth changes apply by themselves. Same play on engine 1.0.3 (240 identical local games).

Audit result (cand6): 0 caught engine errors and 0 bot errors in 400 local games of its check builds (au15, au16); 0 `botFault` events on the platform in plan8 (700 games). Platform (plan8, b3456, 95 games against opponents that kept their bots): fd2 49 and fz1 41 wins vs cand1's 48 and cand6's 41; paired decoded margin fd2 +18 per game, our deaths -0.8 per game.

## Changes in m4 (ladder bot from 2026-10-26 07:50 IST, version 734)

m4 = fd2z (now `bots/pool/fd2z`) built on SDK 4.0.0 (engine 2.0.0, Sprint 3) plus two changes:

- `shop.h`, `targets.h` (wf1, exact fuel): `shard_weights()` holds each item type's weight in shards (1 for a shard, 5 for an emblem), read once; `wealth_of`, the per-round teammate wealth cache (`slot_wealth_now`) and `solo_phase` sum item counts against it. SDK 4.0.0 has 84 item types, and asking each for its result on every call had doubled `wealth_of` to 4.0k fuel.
- `world.h`, `targets.h` (ag4): `W.altar_guards` is the set of groups whose camps fill every standable tile in tribute range of every altar (01boss-battle: one group; 02guardians: two monoliths, one group each), and banking is blocked while each guard camp beside an altar lives. It replaces the single `altar_guard`.

70-map local quick pool against b_log, pd1, tf3: 358 of 420 (fd2z 359), 0 bot faults, turns out of fuel after round 3 386 (fd2z 934).

## Changes in cc2 (ladder bot from 2026-10-27 00:30 IST, version 796)

cc2 = mw1 (now `bots/pool/mw1`) plus carrier caution in the fight step of `bot.cpp`: `big_bag` is a bag of 30+ gems (was 150). Such a carrier never takes the engage branch, and `losing` counts it as losing whenever it is threatened, so it kites or flees instead of trading blows. Cause: our carriers died 2-6 times as often per round alive as the rivals' (`docs/findings.md`, "Gems lost on death: carriers"); on b11p cc2 cut our gems lost on death by r1000 from 141 to 80 per game. cc1 (the same rule at 50 gems) cut them to 109.

## Changes in mw1 (ladder bot from 2026-10-26 17:20 IST, version 766)

mw1 = hc2 (now `bots/pool/hc2`) plus one change in `pick_group` (`targets.h`): `wait_w`, the weight of the rounds a champion would wait at a respawning group after arriving, is 1.0 for groups with side -6..6 (the middle) and stays 4.0 on our side and 2.0 on contested groups elsewhere. The middle bonus (`mid_push`) stays off: restoring it (mb1, mb2) raised deaths.

## Changes in hc2 (ladder bot from 2026-10-26 16:17 IST, version 761)

hc2 = m4 (now `bots/pool/m4`) plus the draft by team size (dq3) and holding a capture (hc1, hc2), each with its experiments row:

- `draft.cpp` (dq3): on 4- and 5-pick maps the team drafts Heart of Ruin, Vesper, Marcella, Vendetta, Varg in that order (`big_pref`, dq2m's order), so a 4-pick team fields Marcella instead of Varg; 3-pick maps keep Heart of Ruin, Vendetta, Vesper (`small_pref`). A pick already taken is skipped as before; maps with more than 5 picks use `preference`.
- `bot.cpp`, `snapshot.h`, `knowledge.h`, `state.h` (hc1): `S.holding` is set each turn after the knowledge update: our target's camps are dead (`state == 1`), we stand on one of its spawn tiles, no teammate stands on its tiles, and we first stood there less than 8 rounds ago (`hold_since`, `hold_group`). A holding champion keeps its target: no re-pick, no target drop for want of pick fuel, no bank trip (the endgame rule still banks) and no shop trip.
- `bot.cpp`, `abilities.h` (hc2): a holding champion also holds against enemies while it is healthy (50%+ health, not hit this turn): the threat branch keeps working instead of the kite step, the pvp branch hits only what is in reach (no chase, no melee dash at 3 tiles), no Vendetta close-in, no striking dash (Heart of Ruin) and no end-of-turn step out of danger. Inside kill range (the burst of the enemies near is 90% of our health or more) `S.holding` is cleared and the usual threat rules apply.

Platform (pinned panel b9p, the same 120 games as main1026h): dq3 won 44 against main1026h's 33 (4-pick maps 11 of 26 against 6, our deaths per game by r1000 7.08 against 9.69; 5-pick 23 of 73 against 17; 3-pick identical). hc2 on dq3: 43 wins; holds of a defeated group left before the capture 5.8 per game (dq3 12.1, the rivals 8.0), captures 41.0 (39.4), gems collected by r1000 673 (634), tributed 532 (505), our deaths 5.6 (5.7).

## Known leftovers (harmless)

- `bot.cpp`: an `if (false)` feature-log block and comments naming deleted tools (`hazard.py`, `calib.py`; source in tag `archive/pre-cleanup`).
- `targets.h`: a dead `recent` loop. (The `capture_priority` check that never fired is fixed in cp3.)
- `enemies.h`: unused `shared_sighting_seen` and `first`.
- `shop.h`: `burst_caster` is computed and unused.

Removing any of these changes the wasm. Do it in a variant and test it like any other change.
