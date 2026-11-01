# Glossary: how we talk about the game

Terms as Eric uses them, mapped to the handbook's names and to the bot's code where that helps. Collected from his
messages, October 2026.

## The map and its contents

| Term | Meaning |
|---|---|
| **Node** | A camp group: monsters and resource clusters that are cardinally connected. They wake together, must all die before the reward can be captured, and respawn together ("finish the rest of the node", "the massive center node"). Code: `Group`, `groups_`. |
| **Camp** | A node, or the monsters in it ("dying to a camp", "taking of the camp"). |
| **Monster / mob** | A member that fights back: wolf, elk, monolith, golem. |
| **Cluster / resource cluster / resource** | A gem cluster or gold cluster: 120 health, never attacks. Hitting one wakes the monsters in its node ("a resource within the node was attacked"). |
| **Gem node / gold node / resource-rich node** | A node worth many gems or gold. |
| **Void** | A hole tile: blocks walking, not sight; dashes cross it. |
| **1-hole gap / 2-hole gap** | A wall line broken by one (or two) hole tiles. A 2-tile dash crosses a 1-hole gap. |
| **Entry point** | A walkable gap between two walls: a choke worth warding. |
| **Lanes (top / middle / bottom lane)** | The parallel corridors of maps like 00lanes. |
| **Outer rings** | The outer loops of ring-shaped maps (swirl). |
| **Their side / enemy territory** | The half of a symmetric map nearer the enemy spawn. |

## Actions

| Term | Meaning |
|---|---|
| **Autos** | Basic attacks. |
| **Spells** | The two abilities. |
| **Offering / banking / tributing** | Tributing gems at an altar ("interrupted from offering", "once we bank in our monolith gems"). |
| **Loot** | A captured node's reward. |
| **Backing** | Retreating, usually recalling home ("prevents a champion from backing preemptively"). |
| **Recall** | The 5-turn channel that teleports a champion home, where it heals fully. |
| **Teleport crystal / teleport stone / TP crystal** | The consumable that hops 3 tiles over any terrain after a 3-turn channel. |
| **Dash** | The 2-tile movement ability (Issac, Vendetta, Vesper Vale, Heart of Ruin). Crosses holes, not walls. |
| **Ward the bushes / ward over walls** | Place a ward where it sees into bushes or over a wall. Placement ignores walls, and attacks need only vision, so a ward over a wall lets ranged champions shoot over it. |
| **Spam the altar lock** | Keep re-placing our lock on a contested altar (a lock needs enemy hits to break: 5 since the patch). |

## Strategy and fighting

| Term | Meaning |
|---|---|
| **Micro** | Per-turn control of one champion: positioning, kiting, targeting, spell timing. |
| **Macro** | Team strategy: what to farm, routes, when to bank or recall, drafts, map plans. |
| **Teamfight** | A fight between groups of champions. |
| **Aggro** | A monster's (or enemy's) current target. A monster hits the nearest champion; on a tie, whoever acts first (priority). |
| **Rotation aggro** | Sharing camp hits across the team so no one soaks them all, while everyone keeps attacking (code: `kAggroPriority`). |
| **Bait / let the mob kill them** | Using aggro offensively: stay farther from an awake monster than the enemy, so it hits them. |
| **Tank** | The champion meant to soak hits up front. |
| **Front line** | The health a party can spend on a camp: each melee member's health above the retreat line, one tank at a time (camps hit the nearest champion). Sizes squads in the code: `kFrontNeed` (`camps-and-maps.md`, elk camps). |
| **Incidental aggro / aggro exit** | A camp hitting us only because a fight with (or flight from) enemy champions crossed its reach. Rule (Eric, Oct 21): step out of that reach first, towards allies or home, even past the enemy, before trading blows (code: `kAggroExit`). |
| **Solo / 1v1 a monster** | One champion clears a node alone. |
| **Power farming** | Clearing camps as fast as possible to buy items and scale; Varg's strength in the old meta. |
| **Scaling / early-game scaling** | Growth from gold and items over the game. |
| **Scaling map** | A map whose game runs long, so gold-boosting items compound: the gems sit in monoliths, or come so slowly that the game reaches round 2,000. In the code: `scaling_map()` (gem-count or tiebreak plan, or a boss camp). |
| **Farming map** | A map whose spawns are far apart (walk over 45 steps), so early fights are rare and teams farm; the draft uses its farmer lists there (10 of the 21 maps, 00eight to 01concentrated-wealth). The opposite is a ranged (contest) map. |
| **Build** | A champion's emblem purchase order ("treasure emblems in our builds"). Code: `build_plan`, `plan_`. |
| **Contest / contesting** | Fighting over a node, altar or area. |
| **Invade** | Going into the enemy's half to fight or steal camps. |
| **Swarm** | Several enemies converging on us. |
| **Snipe / snipe strategy** | Hitting a camp with range-4 spells from just outside the monsters' reach of 3, so they can't hit back. Pointless since the Oct 20 patch (elks reach 4, monoliths 5); only wolves remain. |
| **Stun chain / chained stuns** | Staggering stuns so one starts as the last wears off, keeping an enemy locked (Heart of Ruin's dash, then Ryth's area stun). Code: `kChainStun`. |
| **Burst** | A lot of damage in one turn or a short combo (Stellar's area spells). |
| **Cheese** | A cheap, exploit-like trick: sneaking a monolith, the 4-range snipe, stealing a kill while a monster is hitting the enemy. |
| **Waves / attack in waves** | Sieging a big monster in trips: attack, recall and heal, come back. Monsters never heal (code: `kSiege`). |
| **Overtime / win on most gems** | Reaching round 2000 without 1000 gems, so banked gems (then gold) decide. |
| **Gold lead** | More gold earned than the enemy. |
| **Meta** | The strategies and drafts that currently win. |
| **Early / mid / late game** | Roughly rounds 0–300, 300–900 and 900+ since the patch (games now last 1,300–2,000 rounds). |

## Platform and testing

| Term | Meaning |
|---|---|
| **Ladder** | The ranked leaderboard; rating ("elo") and rank. |
| **Scrims / queued games** | Unranked match groups (5 maps) against a chosen team, from the shared hourly quota. |
| **Screen** | A local batch of test games comparing switch settings (`tools/evaluatec.sh`). |
| **vN** (v140, v188, …) | Our submission version numbers. |
| **Cutoff** | A tournament submission deadline. |
| **Sprint** | A tournament round (Sprint 1 ended Oct 19; Sprint 2 next). |
