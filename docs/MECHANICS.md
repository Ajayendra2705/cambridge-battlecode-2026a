# Cambridge Battlecode 2026a: verified mechanics reference

Engine 3.0.5 (local `cambc` 3.0.5, matching platform patches 1.0.0-1.0.2). Written 2026-10-23.

Every value carries its source:

- **[engine]** read from the engine's own tables by `bots/probe/probe305` (raw dumps in `docs/reference/probe/`). These are exact.
- **[doc]** stated by the handbook (`docs/reference/GameRules.md`, 15 Oct export, re-checked against the live handbook on 2026-10-22). Rules text is current; its *numbers* are outdated wherever they disagree with [engine].
- **[measured]** observed in our own local or platform games.
- **[unverified]** stated somewhere but not yet confirmed; see the last section.

`docs/reference/GameRules.md` is outdated on numbers: it has no Heart of Ruin, clusters at 500 hp, monolith range 3, wolf 22 gems, kill gold 50, altar lock 3 hits, Vesper +20%, Prism 0.2 focus per gem. Use this file instead.

## 0. Sprint 3 patch (announced, not live yet)

Source: patch notes posted on the competition Discord on 2026-10-26 (pasted by the team) [patch notes]. Not live at 02:51 IST on 10-26: platform matches still ran engine 1.0.3 (build hash `fcb6c3e881c4...`), and PyPI still had `cambc` 3.0.5. `tools/platform/patchwatch.sh` waits for either to change. The tables in sections 6, 10 and 11 below are the live engine until then; once it is live, re-run the probe `exp/ps1` (prints every champion design and item from the engine) and update them with [engine] values.

| Change | Old | New |
|---|---|---|
| Ryth strength per shard | 5 | 4.5 |
| Vesper Vale base strength | 55 | 45 |
| Marcella strength per shard | 5 | 4.5 |
| Marcella focus per shard | 15 | 14 |
| Heart of Ruin strength per shard | 3.5 | 3 |
| Heart of Ruin focus per shard | 12 | 10 |
| Cassi base focus | 70 | 100 |
| Issac base strength | 40 | 45 |
| Stellar focus per shard | 7 | 8.5 |
| Prism health per shard | 60 | 65 |
| Willow base focus | 120 | 140 |
| Ren stun damage (slot 1) | 0.75 x focus | 1.1 x focus |
| Varg base strength | 40 | 45 |
| Tavi stun damage (slot 2) | 1.4 x focus | 1.6 x focus |
| Treasure emblem bonus gold | 20% | 10% |
| Monster emblem bonus damage to camps | 10% | 15% |

New item families (each emblem is 5 shards of the chosen stat, like the old families, except Greed):

| Family | Passive |
|---|---|
| Tribute | tribute 33% shorter, rounded up, at least one turn |
| Capture | capture takes 3 turns instead of 5 when the holder is present as the capture starts |
| Prospector | 25% more gold and gems from your share of cluster rewards, rounded down |
| Hunter | 100 extra gold per champion kill, before gold bonuses; a linked duo's death grants one reward |
| Skirmish | 5% more damage to champions |
| Greed | no passive; combines at 25 shards (750 gold) into an item worth 35 shards of stat points |
| Collectors | 1% more damage per unique completed emblem family owned, Collectors included; shards and duplicate stat variants do not add families |

Live engine values before the patch, read by the probe `exp/ps1` on 10-26 (engine 1.0.3 locally): base + growth per shard for health / strength / focus: Ryth 1200+100 / 45+5 / 100+10, Vesper 1000+100 / 55+5 / 100+10, Vendetta 1000+100 / 70+6 / 100+10, Cassi 600+65 / 30+3 / 70+13, Issac 900+80 / 40+3 / 100+10, Stellar 650+65 / 30+3.5 / 70+7, Prism 700+60 / 35+2.5 / 80+8, Marcella 1200+100 / 45+5 / 60+15, Willow 700+50 / 55+3 / 120+5, Ren 900+100 / 35+5 / 100+9, Varg 1000+100 / 40+5 / 100+10, Tavi 900+75 / 45+5 / 110+10, Heart of Ruin 1000+100 / 30+3.5 / 100+12; camp damage multiplier 1 for all. 42 item types (7 families x 3 stats, shard then emblem); emblem passive magnitudes Monster 0.1, Durability 0.1, Treasure 0.2, Jungle 0.3, Home 0.5. [engine]

---

## 1. Winning

| Rule | Value | Source |
|---|---|---|
| Instant win | first team to **1000** tributed gems | [engine] winning_gems |
| Round limit | **2000** rounds | [engine] max_rounds |
| Tiebreak at round 2000 | tributed gems, then lifetime gold *earned* (not held), then champion kills; full tie: Team B (acted second in round 1) | [doc] |
| Carried gems | count for nothing until tributed | [doc] |

How much gem income exists matters more than it looks. The whole board yields between **1.2 and 15.7 gems per round for both teams combined** (table in section 15). On fragment and elk_arena (1.2 per round) even a team that takes every group the moment it respawns cannot reach 1000 gems before round 2000, so those games are decided by tributed gems at round 2000, then gold earned. Contested gems and tiebreaks decide many games.

## 2. Round and turn structure

- A round is: camp respawns, existing spell and ward updates, camp captures, camp actions, then champion turns. [doc]
- Champion turns alternate between teams, and **the team that starts swaps every round**. Within a team, higher priority acts first, then draft order. `set_priority` applies from the next round and persists. [doc]
  - Consequence [measured]: an enemy can act twice between two of our turns, at the end of round N and the start of round N+1. Fight maths must count two enemy actions per gap.
- Each champion turn starts by resolving timers that reached zero, in this order: respawn, ward recharge, buff and shield expiry, channels. Timers then decrement at that champion's **turn end**. [doc]
- Dead champions still get a turn, and can shop during it. [doc]
- Captures resolve before channels, so gems captured this round are included in a tribute that completes this round. [doc]
- Camps act before champions every round, so a camp hits you before your next turn. [doc]

## 3. What a champion can do in one turn

| Action | Limit | Notes | Source |
|---|---|---|---|
| Move | 1 tile, any of 8 directions | Chebyshev geometry: a diagonal costs 1 | [doc] |
| Basic attack | 1 | Damage = Strength. Range 1 (melee) or 3 (ranged), Chebyshev | [engine] base_attack_range |
| Ranged move/attack | either one | Ranged champions cannot move and basic-attack in the same turn. Melee can do both. A **dash still works after a ranged basic attack** (`can_move()` is false, the dash lands): shoot, then dash away | [doc]; dash [measured 2026-10-25, probe pf19: 40 of 40 Vesper dashes right after her attack succeeded] |
| Ability cast | **one successful cast per turn across both slots** | Each slot has its own 8-turn-end cooldown | [engine] cooldown=8 |
| "Excludes walking" spells | cannot share a turn with a walk, before or after | Engine flag `exclusive_with_movement`. See the champion table for which spells have it | [engine] attrs bit 0 |
| Attack reset | restores the basic-attack allowance | Lets a melee champion step, hit, reset, hit | [doc] |
| Ward | place or move the free ward | Once per round, see section 8 | [doc] |
| Consumable | use one you carry | | [doc] |
| Shop | on own spawn tiles, or while dead | Tavi also buys shards anywhere | [doc] |
| Channels | recall, tribute, teleport crystal | Starting one blocks other actions until it ends or is cancelled. Recall and tribute each allow one start and one cancel per turn | [doc] |

Blocked moves: a move or dash onto a tile occupied by an *unseen* unit returns `false`. That tile is then revealed for the rest of the round (`tile_reveal_rounds` = 1 [engine]), and the move allowance, cooldown and consumable are **not** spent, so you can try another tile. Moving onto a *known* occupied tile throws. [doc]

- "Known" follows the view at the moment of the action, not at the start of the turn: after our own move or dash, units that came into view count as known, and a move or landing onto one throws "Known occupied destination" (error 22 for a move, 32 for a dash). All 56 such errors per 80 games in the au11 audit were next to a tile we had just reached, on a tile out of view at the snapshot. Read `champion_tiles()` and `camp_tiles()` again after a move or dash before the next one. [measured]
- A ward placed this turn counts the same way: the units its vision shows are known at once, and a later move onto one throws (3 of the 9 caught errors per 80 games in the au14 audit, each on a bush tile out of our view at the snapshot). [measured]
- A dash landing that can be reached only across enemy spawn tiles was refused with "Destination is unreachable within movement range" (once in 80 games, au14); the SDK's own `move_towards` also treats enemy spawn tiles as blocked. With enemy spawn tiles closed in our dash search, no refusal in the next 320 games (au15). [inferred]

## 4. Terrain and movement

| Tile | Walk on | Dash over | Blocks sight | Notes |
|---|---|---|---|---|
| Wall | no | no | yes | A teleport crystal can cross walls |
| Hole | no | **yes** | no | |
| Bush | yes | yes | yes from outside | From inside you see across your whole bush cluster and out of it, but not into other bushes |
| Altar | no | no | - | Tribute from any tile within Chebyshev 1 (`submit_gems_range` = 1 [engine]) |
| Spawn tiles | own team only | - | - | Heal and shop here. Enemies cannot step on them |

Source: [doc]. Maps run from 30x30 to 100x100 tiles [engine]. All maps are symmetric: horizontal mirror, vertical mirror or 180° rotation [engine].

- **Dash:** up to 2 steps including diagonals, along a legal path; it may cross holes. [doc] [engine] range 2
- **Teleport crystal:** range 3, ignores terrain in between, 3-turn channel (`tp_crystal_time` = 3 [engine]). Damage does not interrupt it; enemy stuns and death do; it cannot be cancelled. [doc]
- **Landing:** never on a wall, hole, altar, enemy spawn or occupied tile. [doc]

## 5. Combat

| Item | Rule | Source |
|---|---|---|
| Basic attack | Strength damage, needs a visible target in range | [doc] |
| Spells | modifier × Focus (e.g. 2.0 × Focus) | [engine] modifiers |
| Cooldown | 8 owner turn ends per slot | [engine] |
| Stun | target loses its next turn (duration 1) | [engine] durations |
| Shield | absorbs damage for 5 turns | [engine] |
| Durability emblem | 10% less incoming damage, all sources | [engine] magnitude 0.1 |
| Jungle emblem | 30% less damage from camps | [engine] 0.3 |
| Monster emblem | 10% more damage to camps | [engine] 0.1 |
| Heart of Ruin passive | up to +50% damage, scaling linearly with missing health | [engine] |
| Ren passive | 0.2 × Focus damage back to each attacker, even as Ren dies | [engine] |
| Varg passive | basic attacks also hit enemies and camps within radius 1 of the target for Strength | [engine] |
| Visibility | targets must be visible; you cannot hit what you cannot see | [doc] |
| Live cooldowns | an enemy's ability cooldowns and `damage_amount(target)` are readable | [measured] |

Stacking: whether reductions multiply or add is [unverified].

## 6. Champions (13; Cassi & Issac are one draft pick)

All champions: vision 8, move 1, both slots on 8-turn cooldown, one cast per turn [engine]. Stat columns show **base + growth per matching shard** [engine]. "Roots" means the spell excludes walking.

| Champion | Type | Health | Strength | Focus | Passive |
|---|---|---|---|---|---|
| Ryth | melee 1 | 1200 + 100 | 45 + 5 | 100 + 10 | +Strength equal to 1% of bonus health |
| Vesper Vale | ranged 3 | 1000 + 100 | 55 + 5 | 100 + 10 | +33% gold from every gold gain |
| Vendetta | melee 1 | 1000 + 100 | **70 + 6** | 100 + 10 | a credited kill (camps too) resets her **ability** cooldowns (attack reset, dash), not the basic attack: after a killing basic attack `can_attack()` stays false [measured 10-25, vk1 corners pair; SDK `reset_cooldowns_on_kill` "reset ability cooldowns"] |
| Cassi | ranged 3 | 600 + 65 | 30 + 3 | 70 + 13 | linked with Issac: if either dies, both die; one kill reward |
| Issac | melee 1 | 900 + 80 | 40 + 3 | 100 + 10 | (linked with Cassi) |
| Stellar | ranged 3 | 650 + 65 | 30 + 3.5 | 70 + 7 | none |
| Prism | ranged 3 | 700 + 60 | 35 + 2.5 | 80 + 8 | +1.5 Focus per carried gem |
| Marcella | melee 1 | 1200 + 100 | 45 + 5 | 60 + **15** | stun-immune; **+2 gold per gem she tributes** |
| Willow | ranged 3 | 700 + 50 | 55 + 3 | 120 + 5 | none |
| Ren | melee 1 | 900 + 100 | 35 + 5 | 100 + 9 | retaliation 0.2 × Focus |
| Varg | melee 1 | 1000 + 100 | 40 + 5 | 100 + 10 | splash radius 1 |
| Tavi | ranged 3 | 900 + 75 | 45 + 5 | 110 + 10 | buys shards anywhere; sells at spawn for full price |
| Heart of Ruin | melee 1 | 1000 + 100 | 30 + 3.5 | 100 + **12** | up to +50% damage at full missing health |

Abilities [engine]:

| Champion | Slot 0 | Slot 1 |
|---|---|---|
| Ryth | area: 1.0 × Focus in radius 1 + stun 1, ground range 4, **roots** | attack reset |
| Vesper Vale | attack reset | dash 2 (no damage) |
| Vendetta | attack reset | dash 2 (no damage) |
| Cassi | damage 2.0 × Focus, range 4, **roots** | stun 1, no damage, range 4, walking OK |
| Issac | attack reset | dash 2 |
| Stellar | damage 2.0 × Focus, range 4, **roots** | area 1.4 × Focus radius 1, range 4, **roots** |
| Prism | damage 1.5 × Focus + stun 1, range 4, **roots** | area 1.0 × Focus radius 1, range 4, **roots** |
| Marcella | enhanced attack reset: next basic attack stuns 1 | damage 2.0 × Focus, range 4, **roots** |
| Willow | heal ally 3.0 × Focus, range 4 | attack reset |
| Ren | damage 0.75 × Focus + stun 1, range 4, **roots** | dash 2 |
| Varg | attack reset | self shield 2.5 × Focus for 5 turns |
| Tavi | attack reset | damage 1.4 × Focus + stun 1, range 4, **roots** |
| Heart of Ruin | self shield 1.5 × Focus for 5 turns | dash 2 landing 1.5 × Focus in radius 1 + stun 1 |

Targeting [engine]: target masks are camps 1, enemies 2, allies 4, self 8, ground 16. Damage spells (mask 3) hit enemies *or* camps. Area spells (mask 19) target ground. Stuns from Ren, Tavi and Prism report kind `cc` and carry damage; Cassi's stun has none.

## 7. Camps, capture and respawn

| Camp | Health | Strength (per hit) | Attack range | Gems | Gold | Respawn |
|---|---|---|---|---|---|---|
| Wolf | 1350 | 20 | 3 | 4 | 40 | 40 |
| Elk | 2400 | 60 | **4** | 15 | 90 | 60 |
| Gem cluster | 120 | 0 | (3, harmless) | 7 | 0 | 50 |
| Gold cluster | 120 | 0 | (3, harmless) | 0 | 20 | 50 |
| Golem | 5000 | 120 | 4 | 36 | 160 | 80 |
| Monolith | 20000 | 200 | **5** | 200 | 300 | 150 |

Health, strength and range are [engine] designs. Rewards and respawn come from solving all 40 maps' groups: 826 groups without golems match the rule below exactly, and the golem values fit every golem group. [engine]

- **Groups:** camps that touch cardinally form one group. A group's reward is the **sum** of its camps; it respawns after its **slowest** camp's time. [engine] [doc]
- **Waking:** camps are asleep until hit. Hitting one wakes the **whole group**. An awake camp attacks the nearest champion every round and stays awake until it dies, or until no champion has been in its range for 2 rounds (`camp_sleep_time` = 2). [engine] [doc] [measured]
- **Camp behaviour:** vision 8, sees through bushes, never moves or chases, never regenerates health. [doc] [measured]
- **Reach vs spells:** wolves and clusters reach 3, but damage spells reach 4, so a caster at distance 4 from wolves takes no hits ("standoff"). Elk and golem reach 4 and monoliths 5, so standoff does not work on them. [engine]
- **Capture:**
  - When every camp in a group is dead, stand on one of its spawn tiles with no enemy on the region.
  - Capture takes **5** rounds (`capture_time` = 5). It resets if the region is left empty or an enemy enters. Extra allies do not speed it up. [engine] [doc]
  - The reward is split among the allies present when it completes; the lowest ID gets the remainder. [doc]
- **Respawn:** the timer starts once the reward is claimed. The group returns at full health only if **every** spawn tile is free; one occupied tile delays the whole group. [doc]

## 8. Vision and wards

- Vision radius 8 using symmetric shadowcasting. Walls and bushes block sight; holes do not. [engine] [doc]
- **Vision is not shared** between teammates, and that includes their wards. Teammates out of your own view are invisible to you (no position, no stats). [doc] [measured]
- **Ward:** one free ward per champion (`active_wards` = 1, `ward_charges` = 1). Place it within 2 tiles (`ward_placement_radius` = 2). It gives vision 6, lasts forever (`ward_lifetime` = -1) and cannot be damaged. Placing a new one replaces the old. It recharges in 10 rounds (`ward_cooldown` = 10). [engine]
- Item counts (`item_count()`), carried gems and buffs of *visible* champions, allies and enemies alike, are readable. Gold is readable for yourself only. [measured]

## 9. Gems, tribute and altar locks

- Capturing gives gems to the capturers' bags. Carried gems count for nothing until tributed. [doc]
- **Tribute:**
  - Stand within Chebyshev 1 of an altar with at least 1 gem and start the channel.
  - Duration = max(1, ceil(gems × 0.1)) turn ends, using the bag at the start (`submit_mult` = 0.1, `submit_base` = 0, `submit_min` = 1). [engine]
  - The starting turn counts. Completion happens at your next turn start after the timer reaches zero, and tributes the **whole current bag**, including gems gained since. [doc]
  - **Damage does not cancel it**; a stun, death or a new altar lock does. [doc]
- **Death:** a champion killer takes **all** carried gems. A camp kill destroys them. [doc]
- **Altar lock** (consumable, 10 gold):
  - Place it on an altar within 2 tiles. Placing it cancels existing enemy tribute channels there. It blocks enemy tributes; its owner's team can still tribute.
  - Removing it takes **5 basic attacks** (`altar_lock_hits` = 5 [engine]; the handbook's 3 is outdated).
  - An enemy's tribute attempt at a locked altar is converted into a basic attack on the lock. [doc] [measured]

## 10. Gold

| Source | Amount | Source tag |
|---|---|---|
| Capture | group's gold, split among capturers | [engine] |
| Champion kill | **100** to the credited killer | [engine] kill_gold |
| Assist | **0** | [engine] assist_gold |
| Passive income | **0** per round | [engine] passive_gold |
| Treasure emblem | +20% of gold gained | [engine] magnitude 0.2 |
| Vesper Vale | +33% of base gold | [engine] |
| Marcella | +2 gold per gem she tributes | [engine] |

Bonuses add, so Treasure on Vesper gives +53%. [doc] The tiebreak counts gold *earned*, so refunds do not count. [doc]

## 11. Items

- **Shards:** cost 30 and add **1 × the champion's growth** in their stat. Every shard family adds the same stats; the family only decides the emblem's passive. [engine]
- **Emblems:** five shards of one family and stat combine automatically into the emblem (150 gold in total). The emblem keeps the five shards' stats. [engine]

| Family | Emblem stats (in growth units) | Passive | Source |
|---|---|---|---|
| Monster | 5 of the stat | +10% damage to camps | [engine] |
| Power | **6** of the stat | none | [engine] |
| Durability | 5 | −10% incoming damage | [engine] |
| Treasure | 5 | +20% gold | [engine] |
| Jungle | 5 | −30% damage from camps | [engine] |
| Home | 5 | recall 50% shorter (5 turn ends become 3) | [engine] 0.5 |
| Bruiser | 5 of the stat **+1 of each other stat** | none | [engine] |

- Stats from duplicate emblems stack; a second emblem's passive does not. [doc]
- Buying Health on spawn also heals that amount; Tavi's purchases away from spawn do not heal. [doc]
- **Consumables** (10 gold each, bought on spawn or while dead) [engine]:
  - Teleport crystal: carry limit 1.
  - Altar lock: carry limit **1** (the engine table says 0, but a second buy throws "error 58: Consumable carrying limit reached"). Placed with `consumables()[altar_lock].use(altar)` from within 2 tiles; works on any unlocked altar. [measured 2026-10-23, probe bot lkp, deleted]
  - Platform rivals (panel 8, ranks 60-69) buy **6.6 altar locks per game** (up to 18); we bought none before lk1. [measured]
- Example: one Durability-health shard on Ryth adds 100 max health, and through her passive +1 Strength. One strength shard on Vendetta adds 6 Strength.

## 12. Death, respawn, recall and healing

- **Respawn:** 60 owner turn-end ticks (`respawn_time` = 60), at your next turn start once a spawn tile is free. You come back at full health with abilities reset. [engine] [doc]
- **Spawn healing:** standing on your spawn restores **100% of max health per round** (`spawn_healing` = 1.0). [engine] [measured]
- **Recall:**
  - 5 turn ends (3 with a Home emblem); the starting turn counts. You arrive at your next turn start after zero and keep your gems. [engine] [doc]
  - Damage, stun or death interrupts it. Stay on spawn until that turn ends to heal fully. [doc]
- **Cassi & Issac:** they die together and give one kill reward plus both bags. [doc]

## 13. Fuel and memory

- **Fuel** (Wasmtime instructions, deterministic) [doc] [measured]:
  - C++ gets 100k per turn, 2× on the first play turn and 10× on the first draft turn.
  - Unused fuel does not carry over.
  - Running out suspends the bot; it **resumes from the same point on its next turn**, so a long computation silently spans several turns.
  - Every SDK accessor is a host call costing about 40 fuel. Printing is expensive.
  - Measured costs differ a lot by call [measured 2026-10-25, probes pf4-pf6 on boss_battle, `cambc::fuel_remaining()` deltas]:
    - `distance_field::get`: about 46 fuel per call, loop included (pf18: 200 random reads per turn, rounds 50-149, four maps; the earlier estimate of about 70 from 474 reads in init_world included other work). A direct read of the raw buffer costs about 37 with the chunked index below, 18 with a plain row-major index, so reading the buffer directly saves little.
    - `distance_field` raw storage [measured 2026-10-25, pf18, 0 mismatches in about 550,000 reads on maps 41x30, 90x30, 40x40, 100x100]: uint16 in 8x8 chunks; the value of tile (x, y) is at index `((y >> 3) * chunked_width + (x >> 3)) * 64 + (y & 7) * 8 + (x & 7)` of `ptr()`, with `chunked_width = ceil(width / 8)` from `cambc::detail::layout()` (not `chunk_stride`, which is the bitboard's padded stride). `field_bytes = chunked_width * chunked_height * 128`. A plain row-major or column-major read is wrong for about 95% of tiles.
    - `camp::base_stats()` and `camp::attack_range()` (a design query): about 730 fuel each. Read them once per camp kind.
    - A heap allocation (vector growth, a new `bitboard`, which allocates its buffer): about 400 fuel. Growing three vectors camp by camp cost 66k on one map; `reserve` removed it.
    - `cm::camp_groups()`: about 40k for one call on boss_battle (31 groups).
    - `cm::width()` and `cm::height()` read a cached struct (free); `bitboard::is_set` and `set` are host calls.
    - `distance_field::compute_to` from a goal set until it reaches our tile: 4.3k at the median, 11k at the 95th percentile, 25k at most over 1,886 calls in 80 games (au10); about 4k within 10 steps, 10k beyond 40, more on some maps (ambush, starvation).
    - One status line with two floats, two `to_string` strings and five integers through `std::cout`: about 13k fuel. Every 20 rounds per champion it raised the median turn from 38k to 51k fuel on those rounds and made 1.6% of them run out (0.17% of other rounds; au10).
  - A plain C++ loop also costs: fuel counts wasm instructions. 9,000 distance checks (strong camps against every spawn) took 430k.
  - Bulk memory is not free either [measured 2026-10-25, probes pf9-pf10 on big_world, 100x100]: clearing a 10,000-byte array (`vector::assign`) costs about 12.5k fuel (about 1.25 per byte); `bitboard::positions()` on the view plus one store per tile costs about 25 fuel per visible tile (10k a turn); `bitboard::export_linear_buffer` of the whole map (1,250 bytes, packed row-major bits, least significant first) costs about 600.
  - A full-map `distance_field` on big_world costs about 35k (travel field or the BFS from us); a group route with detours up to 54k [measured, pf7-pf8].
  - A turn that runs out resumes next round from the same point, with every value read before still from the old round (snapshot, positions of teammates): moves onto tiles a teammate took since then throw "Known occupied destination". Check `cambc::round_number()` against the snapshot round before acting.
  - The platform logs each exhaustion as a `fuelExhausted` event.
- **Shared memory:** 8 bytes per team, readable and writable all match, invisible to the opponent. [engine]
- **Draft memory:** 1024 bytes, writable during the draft, read-only afterwards. [engine]

## 14. Draft

- Each team picks 3 to 5 champions, depending on the map (see table). Picks are simultaneous and revealed one by one. A champion can be picked once per team, but both teams may pick the same one. Cassi & Issac is one pick and fields two bodies. [doc] [engine]
- The draft bot sees the whole map. If it fails to pick, the remaining picks are random. [doc]

## 15. Map pool (40 maps, local `maps/`)

**The platform pool is larger [platform 10-26]:** the match-group quota listing (`cambc match-groups quota --json`, field `maps`) had 55 maps at 03:20 IST on 10-26 and 70 at 03:50: our 40, then 00anvil, 00breadcrumbs, 00crater, 00dunes, 00galaxy, 00oasis, 00quarry, 00ribs, 00the_line, 00vault and adgato_gemcombat1-5 (already played in ranked games before 10-26), then fifteen new `02` maps: arena, crossing, cuts, famine, fields, geodes, gift_wrapping, guardians, harvest, stalactites, tangle, the_pack, the_pond, treasure_box, uncharted_lands. All 70 are in `maps/` since 10-26 (`cambc init` in a scratch folder downloads them); `tools/local/newmaps.txt` lists the 30 added ones, and `tools/local/allmaps.txt` stays the first 40. The tables below cover only the first 40.

Totals are for one full clear of every group (shared by both teams). "Max gems/round" = Σ group gems / group respawn: the most gems per round the whole map can produce if every group is taken the moment it respawns. Generated from `docs/reference/probe/maps/*.txt`.

See `docs/reference/probe/map_table.md` for the full table. Highlights:

- Gem-poor maps (whole-map gems per round), where 1000 gems is hard or impossible and the tiebreak or contesting decides:
  - fragment 1.2 (68 gems per full clear) and elk_arena 1.2 (72): 1000 is unreachable by round 2000.
  - hooks 1.5.
  - contest 2.7: only its two monoliths hold gems (400 per clear).
  - stampede 2.7, gold_rush 2.7, packs 2.8, pilgrimage 3.2.
- Gem-rich maps decided by farming speed: boss_battle 15.7, the_farm 14.6, road_of_riches 14.5, great_wall 14.4, quadrants 12.9, shortcut 12.1.
- 3-pick maps: collision, fragment, packs, broken_curve, gold_rush, the_farm. 4-pick maps: gemfight, interlock, reverse_spiral, rows, rushbait_v2, swirl, hooks, shortcut.
- Golems appear on great_wall (4, in a 256-gem group), lost_world, quadrants, reverse_spiral, road_of_riches and split.

## 16. Things that follow from the rules

1. **Tribute often.** A killer takes the whole bag, and damage does not interrupt a tribute, so a short channel next to an altar is safe from damage.
2. **Gold decides fights.** No passive income, no assist gold. Every point of stat comes from captures (or kills, 100 each). A champion that never captures stays at base stats.
3. **Marcella should tribute gems** (+2 gold per gem). **Vesper should take gold** (+33%).
4. **Stats per shard differ:**
   - Vendetta gets 6 Strength per shard; Heart of Ruin only 3.5 Strength but 12 Focus.
   - Marcella gets 15 Focus but 5 Strength per shard; her spell is 2 × Focus.
   - Ryth's Strength comes from strength shards; health shards add only +1 Strength per 100 health.
5. **One cast per turn plus rooting spells:** a rooting spell costs that turn's step. Casting from range 4 lets you hit without approaching but leaves you standing still.
6. **Two enemy actions can land between our turns** (alternating start), so a "safe" gap of one tile is not safe against a melee champion with a dash.
7. **Elk and golem reach 4 and monoliths 5:** spell standoff only works on wolves and clusters.
8. **Respawn needs every spawn tile free:** standing on one blocks the whole group indefinitely (verified, section 17). That can deny the enemy a camp. It also means our own champions must step off a captured group's tiles or they hold back our own respawn.
9. **Spawn heals 100% per round:** a round on spawn is a full heal. Recall (5 turns, broken by damage) is the slow way home.
10. **A woken camp hits the nearest champion, not the one who woke it.** Waking a group next to a teammate gets the teammate hit. Sleeping camps are harmless even when adjacent, so walking past them is safe as long as nobody hits them.

## 17. Verified by local experiment (2026-10-23)

Test bots: `bots/probe/mt1` (turn order, camp behaviour) and `bots/probe/mt2` (rooting cast, respawn blocking), on 00collision.

| Question | Result |
|---|---|
| Order of our champions within a round | Fixed every round, in draft order (default priority) |
| How often a woken camp hits | Every round, full Strength. A wolf hit in round 7 dealt 20 per round from round 8 on. The camp design's "cooldown 2" does not mean every other round |
| Who a woken camp hits | The **nearest** champion in range, whoever woke it. A wolf woken by our Ren went on hitting our Heart of Ruin, who stood 2 tiles away, until it died |
| When a camp sleeps | With no champion in range it was still awake on the next round and asleep the round after (`camp_sleep_time` 2) |
| Do sleeping camps attack? | **No**, not even with a champion adjacent. Only damage wakes them |
| Health regeneration away from spawn | None |
| Can you walk or dash after a rooting cast? | No. After Ren's stun `can_move()` is false, and a dash fails with "A spell was already cast this turn" |
| Capture timing and reward | Two gold clusters gave 40 gold. The respawn timer starts at the group's respawn (50) on capture and drops by 1 per round |
| Does standing on a spawn tile block the respawn? | **Yes, indefinitely.** The timer sat at 0 from round 73 to 93 while our champion stood on the tile, and the group respawned the round after it left |

## 18. Still to verify

| Claim | Why it matters | Test |
|---|---|---|
| How damage reductions combine (Durability with the Heart of Ruin bonus, shields) | fight maths | buy items in a long test, hit a dummy, log health loss |
| Whether higher `set_priority` moves a champion earlier in our order | who acts first in a fight | set priorities, log the order |
| Exact interleaving of the two teams' champions within a round | how many enemy actions land between ours | log both teams' order in one game |
