# Camps and maps (after the October 20 patch)

## Camp stats

From the 3.0.1 SDK, a settings probe (`bots/SetProbe`, base stats and group rewards) and post-patch replay state.

| Camp | HP | Strength | Reach | Gems | Gold | Notes |
|---|---|---|---|---|---|---|
| Wolf | 1350 | 20 | 3 | 4 | 40 | mostly a gold source now |
| Elk | 2400 | 60 | **4** | 15 | 90 | main gem source on maps without monoliths |
| Gem cluster | 120 | 0 | — | 7 | 0 | doesn't attack |
| Gold cluster | 120 | 0 | — | 0 | 20 | best gold per hit point by far |
| Monolith | 20000 | 200 | **5** | 200 | 300 | its group usually adds gem clusters |
| Golem | 5000 | 120 | 4 | 36 | 160 | respawn 80; not on any pool map yet |

Rewards are per group: the sum of its members. Rewards go to allies on the capture tiles (lowest ID gets the remainder);
groups respawn together on the longest member cooldown.

### Farming and contest maps (the draft's split, October 21)

The draft treats a map as a **farming map** when the spawns are more than 45 walking steps apart (draft.cpp
`kRangedSteps`), else as a **contest (PvP) map**. From our ladder logs (the first pick is Heart of Ruin exactly on
farming maps): farming = 00ambush, 00eight, 00expanse, 00lanes, 00monolith, 01big_world, 01concentrated_wealth,
01fracture, 01gold_rush, 01islands; contest = 00collision, 00contest, 00corners, 00elkring, 00fragment, 00interlock,
01boss_battle, 01broken_curve, 01corridors, 01elk_arena (01hooks: contest). The analysis of the top teams' drafts and
items by map type uses this split (`champions.md`).

### Our half of the map: the rule the bot already uses, and the farming-speed gap (October 21)

Eric asked for a symmetry-proof rule for "our half". The bot has one: at set-up it computes, for every camp group,
the **walking distance from our spawn and from the enemy's spawn** (distance fields around walls and holes, with the
straight-line region distance as the fallback), and a group is `far_side_` when their spawn is more than
`kFarSideMargin` (2) steps nearer than ours; `midline_` when the two walks differ by at most `kMidline` (6). Because it
is path-based it is the same rule under 180° rotation, horizontal or vertical mirroring and diagonal symmetry. What
the rule does is weak: a far-side camp's score is only multiplied by `kFarSide` 0.7 (1.2 when ahead), and far-side
camps are forbidden only on control maps before round 100 (`kFarSideEarly`).

The five-game group 7be1b56b against meow (expanse, interlock, fragment, islands, boss_battle; `tools/stress/halfscan.ts`)
shows the real gap is **throughput on our own half**, not invading: per 300 rounds we captured 42/58/56 camps on
expanse to their 60/64/75, 25/24/19 on interlock to 37/37/38, 32/33/34 on boss_battle to 48/44/70, with 0–2 enemy-half
captures a window. They farm in more, smaller parties: 4.65 separate parties on expanse to our 3.60, 3.16 to 2.40 on
interlock, 2.48 to 2.13 on boss_battle. Fragment is the exception: we moved as **1.24 parties** (one stack) all game to
their 2.00, captured 13/8/6 to their 18/31/31, and spent 16–24% of the early rounds on their half (Heart of Ruin
alternated camp_route, escape, contest_altar and evade there) while they took 12 camps on ours.

### 01shortcut and 01gold_rush layouts (October 21, `tools/edits/edit_mapdump.py` prints any map)

- **01shortcut** (40×40, 4 picks): each spawn sits in a walled room (x 10–23); the room's side towards the centre is a
  **single row of holes** (row 23 for the south spawn, row 16 for the north). The centre corridor (rows 19–20) holds
  the shared camps (two elks, wolves, clusters) five tiles from each spawn across that row. On foot the way round is
  ~50 steps (out of the room's far side, along the map edge, up the left column). A dash (range 2) crosses the row in
  one cast, so dash champions (Heart of Ruin, Ren, Vendetta, Vesper, Issac) reach the centre in three turns.
- **01gold_rush** (31×31, 3 picks): one monolith at the centre (15,15) whose **group includes the 24 gem/gold
  clusters in the ring around it**. Damaging any cluster wakes the whole group, so the monolith turns on whoever stands
  nearest though it has full health. Our awake model counted only hurt monsters until `kTrueWake`.

### Monolith maps: where our champions die (October 21)

In 60 ladder games against the top three (v200), 55 of our 158 camp-involved deaths were to **monoliths** (200 strength,
reach 5): 32 on 01boss_battle, 23 on 01gold_rush. 01boss_battle holds **two monoliths side by side at (23,20)/(24,20)**
(one group: 400 gems, 600 gold) at the map's centre, 20 steps from either spawn, with clusters and elk camps around them,
so the teamfights happen inside their reach. The monoliths sleep until something damages them; an area spell aimed at a
champion beside them (Stellar's blast, Ryth's stun, a Heart of Ruin landing) wakes both, and from then on the nearest
champion takes 400 a round: Fish fights beside the sleeping pair on purpose (bait), and our champions kept walking to 1–2
tiles of the woken pair after enemies (also against our own code locally: 18–24 monolith deaths a game per side). On
01gold_rush a single monolith at (15,15) plays the same role. Bot switches: `kWakeGuardStr`, `kBaitGuard`,
`kAggroExitStr` (bot-status.md). The monolith pair is not a boss-mode target (`kBossMaxStr` 100 excludes 200-strength
monsters), so nobody on our side ever intends to fight it.

### Elk camps at level 0: who can clear them (October 21)

`scratchpad/ft/campsim.ts` plays a party against a cluster of elks round by round with the engine's rules (every
living, unstunned elk hits the nearest champion once a round for 60; melee members stand in front and the healthiest
one tanks until it falls under 45% of its health, then the next steps in; ranged members at distance 3 are never the
nearest while a melee stands in front; spells every 8 rounds, stuns skip a hit). Nobody has items.

| Camp | Total damage taken | Smallest party that clears it (stun draft: HoR, Ryth, Stellar, Ren, Marcella) |
|---|---|---|
| 1 elk | ~800–1,000 | 2 (two melee: Ryth + Ren or Ryth + Marcella), 3 by pick order |
| 2 elks | ~1,500–1,800 | 4 (three melee + one caster), the tanks end at 35–40% |
| 3 elks | ~2,800 | **not at level 0**: all five retreat after 23 rounds with 2,760 taken; feasible once the tanks hold a Jungle emblem (−30%: cleared in 26 rounds, lowest 41%) or with the tanks taken to the 35% retreat line |
| 4 elks | ~4,000+ (retreat at 2,700–2,900) | not even with Jungle on the tanks: items first |

The old party-size rule (`champions_needed`) assumed a camp's damage is shared evenly by the party; the fight's damage
really goes to one tank at a time, so what matters is the **front line**: the melee members' health above the retreat
line. `kFrontNeed` (bot-status.md) sizes squads that way: the first k members (tanks first, then ranged by damage)
whose summed damage clears the camp before its damage uses up the front line.

## The ladder pool (35 maps since October 21)

Checked with `cambc maps list` on October 21 ~03:00 UTC: the pool grew from 21 to **35**. Back in: 00packs, 00pilgrimage,
00quadrants, 00reverse_spiral, 00rows, 00rushbait_v2, 00split, 00stampede, 00swirl. The five Sprint 1 maps are in as
01shortcut, 01starfish, 01starvation, 01the_farm, 01yellow_brick_road, and their contents **differ** from the
`sprint_1_*` files we kept (every hash differs), so the old copies are not a substitute. `cambc maps pull --force`
fetches them all (hyphenated file names: `01yellow-brick-road.map26a`). The local replay engine with cambc 3.0.1's
visualiser rejected server replays from after the Heart of Ruin nerf (engine error 11); with cambc 3.0.4's assets
(unpacked by `cambc-3.0.4.exe view` once) `tools/replay_engine.ts` reads ladder replays again (October 21, 03:45 UTC).

### The old 21-map pool

00ambush, 00collision, 00contest, 00corners, 00eight, 00elkring, 00expanse, 00fragment, 00interlock, 00lanes,
00monolith, 01big_world, 01boss_battle, 01broken_curve, 01concentrated_wealth, 01corridors, 01elk_arena, 01fracture,
01gold_rush, 01hooks, 01islands. Local files from `cambc maps pull` use hyphens for the 01 maps (`01big-world.map26a`);
the platform's scrim API takes the underscore names.

## Where the gems are

Share of each map's gems (per respawn cycle) held in monolith groups (settings probe, Oct 20):

| Map | Monolith share | Monolith groups |
|---|---|---|
| 00contest | 100% | two groups of 200 gems |
| 00monolith | 76% | 256 gems each (monolith + 8 gem clusters) |
| 01gold-rush | 75% | 200 |
| 01corridors | 57% | 428 (two monoliths + 4 gem clusters) |
| 01big-world | 55% | 228 |
| 01broken-curve | 54% | 200 |
| 01fracture | 47% | 200 |
| 01boss-battle | 34% | 400 (two monoliths) |
| the other 13 | 0% | — |

Maps without monoliths have small gem totals, so their games run long: 00fragment and 01elk-arena hold well under 100
gems per respawn cycle, and 01hooks' best camp is worth 22 gems.

## Game length and scaling maps

The bot's map profile (`kTraceMap`, Oct 20) and the mean final round of 160 ladder games against Nyx, Univ, Mite and
procless. "Bound" is the profile's lower bound on rounds for our half's camps to yield 1,000 gems; boss camps are
excluded from it, so monolith maps look fast by the bound but play long. **Scaling** maps (`scaling_map()`: gem-count or
tiebreak plan, or a boss camp) get Treasure-first builds from v190.

| Map | Plan | Bound | Boss gems | Ladder rounds | Scaling |
|---|---|---|---|---|---|
| 00contest | gold_tiebreak | — | 400 | 2,000 | yes |
| 01boss-battle | race | 168 | 400 | 2,000 | yes |
| 01gold-rush | gem_count | 1,272 | 200 | 1,813 | yes |
| 00fragment | gem_count | 1,862 | 0 | 1,781 | yes |
| 01corridors | race | 195 | 428 | 1,491 | yes |
| 01fracture | race | 285 | 400 | 1,327 | yes |
| 01broken-curve | race | 367 | 400 | 1,284 | yes |
| 01big-world | race | 322 | 456 | 1,231 | yes |
| 00monolith | race | 731 | 512 | 1,067 | yes |
| 01hooks | gem_count | 1,500 | 0 | — | yes |
| 00collision | race | 393 | 0 | 1,505 | no |
| 01elk-arena | race | 916 | 0 | 1,481 | no |
| 00ambush | race | 480 | 0 | 1,460 | no |
| 01concentrated-wealth | race | 471 | 0 | 1,418 | no |
| 00eight | race | 557 | 0 | 1,178 | no |
| 00interlock | race | 632 | 0 | 1,170 | no |
| 00corners | race | 324 | 0 | 1,160 | no |
| 00expanse | race | 350 | 0 | 1,137 | no |
| 01islands | race | 190 | 0 | 1,135 | no |
| 00lanes | race | 408 | 0 | 1,088 | no |
| 00elkring | race | 600 | 0 | 847 | no |

## Layout notes

- **01yellow_brick_road** (40x30, spawns at the left and right ends of the middle rows): two **30-tile gold-cluster rows**
  (groups 0 and 1, rows 12 and 17) run the whole width between the spawns: 30 clusters, 3,600 HP, 600 gold, no monsters.
  One group each, so (a) a capture needs every cluster dead and nobody of the other team on any of the 30 tiles, usually
  out of our sight, and (b) the group's centre is 15 tiles from spawn. Our party rule waited at spawn for mates "near"
  that centre (fixed Oct 21: harmless groups never wait; nearness from the nearest tile), and recall-captures of a
  contested row looped (fixed: `kCaptureBlind`). The 30-member groups also cost fuel: ~780 overrun turns a game.
- **01starfish** (50x50 star): both spawns at the top corners, the only two altars in a bush pocket at the centre
  (row 17), reached down a 6-wide corridor flanked by elk columns (five elks each at x=20 and x=29, rows 36-40) and
  camp pairs along the stalk. A contest map: our October 19 code beat v197's defence-first build 52 kills to 13 there.


- **01concentrated-wealth**: the centre node sits inside a wall ring whose north side (row 17, x 23–30) is a single
  row of holes, dashable from (x,16) to (x,18). Champions without a dash hop the wall with crystals from (19,15).
- **00eight**: the altar at (20,15) sits inside a ring of 8 bush tiles; tributers there are hidden from outside.
- **01elk-arena**: both altars (22,22) and (27,27) have 3 bush tiles beside them.
- **00contest**: the monoliths sit in walled pockets; all the map's gems are in them.
