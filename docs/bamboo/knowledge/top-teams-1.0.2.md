# How the top teams play on engine 1.0.2 (October 21)

The October 21 balance patch (engine 1.0.2: Stellar 650 health / 70 Focus, Heart of Ruin Strength 30, Ren's stun 0.75×,
Vesper, Vendetta, Tavi and Prism buffs; `patch-2026-10-20.md`) went live on the ladder at **05:20 UTC on October 21**.
Everything below is measured on 1.0.2 games only.

**Data:** 103 ranked matches between two of the top ten (05:20–10:15 UTC; mostly Intercontinental Fish's games, plus
:3, procless, Pantheon, EMPEROR Tung, Sponge, new team(4), NTU, policy wonk), our 40-game ladder bench of v205 against
Nyx and procless (10:20 UTC), our 50 ranked games since v205 went live, and local games of our bots against B7Live.
Replays live under `replays/top102`, `replays/me102`, `replays/p2/sl_np205` (regenerable: `tools/stress/dlmatches.py`).

**Tools** (all in `tools/stress/`; Deno scripts read replay directories or `run-batch` bundles):

| Tool | Measures |
|---|---|
| `teammatches.py`, `topdrafts.py`, `toppick.py`, `dlmatches.py` | a team's ranked matches (signed-in CLI), drafts per pick count and map, picking and downloading top-vs-top replays |
| `behave.ts` + `behaverun.py` + `behavesum.py` | per team and game: income curves, gold holders, item families and first emblems, pickups by map half, recalls and tributes, deaths and kills, enemy-half time, activity split (camp / walk / fight / recall / idle), travel detours, camp damage dealt |
| `capsum.py` | camp captures per game by camp class and round window |
| `engage.ts` + `engagesum.py` | escape and attack patterns: each engagement (an enemy champion first within 5) by local numbers, the response and the outcome |
| `killctx.ts` | every champion kill: what the victim was doing, who killed it, local numbers, map half |
| `elkkill.ts` + `elksum.py` | every wolf/elk/monolith kill: the killing party's size and how long the monster took |
| `mapbench.py` | per map, the top teams' gold and banked gems against a bot's local games (an absolute yardstick) |
| `localrun.py`, `mapgrid.ts` | our bot against an opponent on all maps with the bundles kept (`LOGS=1` keeps stdout); ASCII map from a replay |

## Drafts (ranked games since 05:20 UTC; `topdrafts.py`)

Nine of the top ten draft **Heart of Ruin in every game**; most have one fixed list per pick count:

| Team (1.0.2 record) | 3 picks | 4 picks | 5 picks |
|---|---|---|---|
| Intercontinental Fish (102/145) | Stellar, HoR, Ren | + C&I | + Ryth (Prism draft x2) |
| :3 (85/140) | HoR, Vendetta, Ren | + Vesper | + Varg (58) or HoR, Ryth, Vesper, Marcella, Stellar (33) |
| procless (83/145) | HoR, Vesper, Ryth | + Marcella | + Vendetta (63) or HoR, Ryth, Ren, Stellar, Marcella (21) |
| Pantheon (82/145) | HoR, Marcella, Vesper | + Ryth | + Stellar |
| NTU (84/140) | Vendetta, Vesper, HoR | + Marcella | + Ren |
| Sponge (77/145) | HoR, Vendetta, Ryth | + Marcella | + Ren |
| policy wonk (93/145) | Marcella, Vesper, Tavi | + Willow | + Ryth (the only top team without HoR) |

Across 1,430 top-ten drafts: HoR 89%, Ryth 66%, Marcella 53%, Vesper 51%, Ren 47%, Stellar 41%, Vendetta 34%, Varg 22%,
C&I 13%, Tavi 11%, Willow 7%, Prism 0%. Vesper and Marcella rose with the patch.
Ours on 1.0.2 (145 ranked games, 65 wins): HoR in 62% (HoR, Ryth, Stellar, Ren, Marcella on farming maps 16/54;
Stellar, Prism, Ren, Tavi, Ryth on contest maps 16/30; HoR, Ryth, Varg 12/17).

## Items and who holds the gold (`behave.ts`)

| Team | Richest champion at r600 | Main item family (share of item gold) | First two emblems |
|---|---|---|---|
| Fish | Stellar 49 of 79 games, HoR 25 | Stellar and HoR: **Power Focus 81–83%** | Treasure Focus, then Power Focus; Ren: Bruiser Health, Durability Health, then Power Focus |
| Nyx | Stellar 12 of 20 | Stellar Power Focus 80%, HoR/Ryth Power Strength 81–83% | Treasure first on everyone |
| procless | Vesper 12, Marcella 10, HoR 7 | HoR Power Focus 77%; Vesper/Marcella Bruiser Strength | HoR Treasure Focus, Durability Health |
| :3 | HoR 15 of 39 | HoR Bruiser Focus 65% | Jungle Focus, Treasure Focus |
| Pantheon | Vesper, Marcella, HoR | Power Strength 57–75% | Jungle Strength, Power Strength |
| **us** | Ren, Marcella, Ryth | **Bruiser** 50–70% (`kMetaBuild` 1) | Jungle/Treasure, Durability Health |

The richest champion's share of team gold is the same for everyone (43–48% at r300): concentration is not the
difference; **total** gold is. By r600 the top teams own 17.5–19.4 emblems as a team, we 11–12.
Power stacking tested locally on our play: `kMetaBuild` 3 (Treasure, Power) **−227 ± 38**, 4 (+ Durability Health)
−117 ± 36, 5 (our Jungle/Durability/Monster opening, then Power) −138 ± 27, 6 −92 ± 32 (35 maps): our champions fight
camps with Jungle and Bruiser health and lose without them. The build stays.

## Economy and farming

| Per game (r1–600 unless noted) | Fish | :3 | procless | Nyx | us vs Nyx/procless | us ranked | our ranked opponents |
|---|---|---|---|---|---|---|---|
| gold earned r300 / r600 / r900 | 1360 / 3326 / 5403 | 1302 / 3284 / 5691 | 1264 / 3405 / 6098 | 1212 / 3044 / 5278 | 1046 / 2291 / 3616 | 914 / 2214 / 3659 | 1047 / 2436 / 3983 |
| gems banked r600 / r900 | 303 / 509 | 254 / 440 | 289 / 563 | 203 / 396 | 191 / 312 | 202 / 360 | 214 / 393 |
| camp captures r0–150 / r150–300 / r300–600 | 4.6 / 5.6 / 13.1 | 5.6 / 5.7 / 13.5 | 4.6 / 6.3 / 14.4 | 3.3 / 3.0 / 7.9 | 3.9 / 4.9 / 8.6 | 3.5 / 4.8 / 10.0 | 4.7 / 5.0 / 10.0 |
| elk kills r300–600 (party, rounds per kill) | 6.1 (3.3, 43) | 7.2 (2.0, 39) | 7.6 (1.8, 37) | 6.2 (2.2, 28) | 4.5 (2.2, 39) | 3.7 (2.3, 49) | 5.1 (2.2, 48) |
| wolf kills r300–600 (party, rounds) | 8.0 (2.7, 26) | 9.8 (1.6, 25) | 10.9 (1.4, 19) | 8.8 (1.6, 20) | 7.7 (1.8, 26) | 6.3 (1.7, 30) | 7.7 (1.9, 25) |
| champion-rounds walking / at camps | 50 / 21% | 49 / 22% | 46 / 26% | 51 / 24% | 54 / 20% | 53 / 21% | 51 / 21% |
| camp damage dealt per camp round / per 1000 rounds | 67 / 80k | 86 / 94k | 78 / 100k | 71 / 102k | 65 / 68k | 57 / 63k | 63 / 82k |
| champions on the tiles when a reward is claimed | 1.2–1.3 | 1.1 | 1.1 | 1.0–1.1 | 1.2–1.5 | 1.2–1.6 | 1.1–1.2 |
| captures on own / mid / enemy half, r0–150 | 78 / 15 / 5% | 80 / 15 / 4% | 86 / 7 / 5% | 80 / 10 / 9% | 74 / 21 / 3% | 74 / 21 / 4% | 78 / 12 / 8% |

- **The gap is throughput.** The top teams kill about 1.6× as many elks after r300 (elks hold the gems: 15 gems + 90
  gold each) with the same party size, faster, and spend more of their time at camps and less walking. They claim
  each reward with one champion while the rest move on.
- **They open on their own half.** Fish's first capture on 00corners is its own elk at r28; our opening target on
  corners was the top-middle group, where both teams met at r35–45.
- **Fish keeps four to six together for elk pairs** on 01corridors (r64, r157, r250), procless three to five; we take
  two elks in the opening and then only wolves (gold, few gems).
- Against the top teams' median per map (`mapbench.py`), our local games bank about a third of their gems by r600
  (sum over 32 maps: top 15,293, our dev base 5,355, v205 5,482); worst: 00corners, 01shortcut, 01islands, 00eight,
  00rows, 01starfish, 01concentrated_wealth, 01corridors.

## Recalls and tributes

| | Fish | :3 | procless | Nyx | us |
|---|---|---|---|---|---|
| recalls per 1000 rounds | 53 | 40 | 52 | 58 | 48–56 |
| gems carried when the recall starts | 18 | 22 | 36 | 32 | 5–11 |
| health share at recall start | 0.52 | 0.61 | 0.51 | 0.65 | 0.68–0.70 |
| recalls started above 90% health | 16% | 28% | 11% | 32% | 37–41% |
| tributes per 1000 rounds × gems each | 24 × 45 | 15 × 56 | 27 × 33 | 20 × 35 | 15–18 × 32–41 |

Recall is cancelled by damage (GameRules: "Recall … is interrupted by damage, stun or death"); Fish's carries own a
Home emblem (5% of their item gold: a 3-turn recall).

## Escape and attack patterns (`engage.ts`, `killctx.ts`)

- **Kills happen at camps.** 52–74% of every team's champion kills land on a victim fighting a camp, 28–33% on one
  walking, 4–12% on one channelling. The pattern is ganking farmers, not open team fights.
- **The top teams win duels.** Fish's kills: 30% by a single champion, procless 56%, Nyx 48%; HoR takes part in
  26–36% of the leaders' kills (procless's Vesper 25%). Against Nyx and procless, 51% of our champion deaths are to a
  single killer and 68% happen on our own half (they invade our farmers); Stellar is 30% of our deaths.
- **Engagements** (an enemy first within 5): with more of ours near, Fish kills 0.48 enemies per engagement (K/D 5.9),
  procless 3.4, Nyx 3.7, we 1.8 against them (4.3 in our ranked games); with equal numbers Fish 2.6, procless 2.2,
  Nyx 3.9, we **0.47** against them. Below half health Fish answers with a recall 26% of the time (procless 19%, we
  10–13%). The leaders are rarely outnumbered (Fish 1 engagement a game, we 0.5).
- **Invasions:** Fish spends 7.5% of champion-rounds before r600 on the enemy half in parties of 2.5 and makes 56% of its
  kills there; procless's kills are 68% on our half. We: 4.6–5% of rounds, parties of 2.3, 37–49% of kills there.
- `kHuntOdds` (chase the weakest enemy in sight when stronger) as a stand-in for ganking: 1.5 −103 ± 36, 2.5 −130 ± 34
  (two seeds): our fights are not won by numbers alone.

## Our ladder results on 1.0.2 (200 ranked games since 05:20 UTC, 90 wins)

Fighting maps are won, farming maps lost: 00corners 6/6, 01elk_arena 5/5, 00quadrants 5/5, 00collision 3/3, 00rows
3/3, 01the_farm 8/10; but **01yellow_brick_road 0/6, 01starvation 0/6, 01islands 0/5, 00lanes 0/5, 01corridors 0/5,
00swirl 0/4, 01concentrated_wealth 1/8, 00interlock 1/5, 01gold_rush 3/11**. On 01yellow_brick_road v205's five
champions stand at spawn in `wait_party` for ~100 rounds and then freeze in `travel` (Stellar on (6,12) from r100 to
r340): 110 gold by r600 against the opponent's 4,019 (reproduced locally, release and debug builds alike; our dev base
with v204's settings farms 1,046 gold by r300 there). On 01corridors and 01starvation we earn the opponent's gold but
bank 40–60 gems by r600 to their 140–420.

**Ladder bench on 1.0.2:** v205 (v200's code) 3/40, −17,885 against Nyx and procless (10:20 UTC); v204 3/40, −19,686
(08:15, also 1.0.2). The earlier "v204 worse than v200" compared a 1.0.2 bench with a 1.0.1 one: on the same engine the
two tie.
