# h3 notes: map research for task 6 (10-28)

Third agent ("h3"). Read-only on the shared docs; everything h3 learns is here. Tools in `tools/helper3/`, outputs in
`data/helper3/`, replays in `data/replays/platform/h3_*`, decodes in `data/fights/h3_*`.

## Latest (IST)

- READY 14:16: h3bq1 (bank batch capped at 40), `docs/helper3/patches/h3bq1.patch`, built in `bots/exp/h3bq1`;
  applies to tg1 and uf1. Exposure to big bags -22% locally; lost on death flat locally (a platform question). See
  "Job 4".
- READY 14:10: h3cv1 (the cover fix), `docs/helper3/patches/h3cv1.patch`, built in `bots/exp/h3cv1`; applies to
  tg1 and uf1. Local check and proposed bwm rule in "Job 3" below. Job 4 (bank batch cap) next.
- 12:45 01yellow_brick_road done. Cause: the `covered` rule in `pick_group` (`targets.h`) never lets us pick a group
  within reach 4 of a live elk group, even a sleeping one; two elk groups that cover each other block each other for
  good. On yellow that is our corner pair and the centre pair (39% of the map's gems). `tools/helper3/h3_cover.py`
  finds the same lock on 7 of 70 maps (01hooks 100% of gems, 00fragment 76%, 01boss_battle 63%, yellow 39%,
  01corridors 22%, 00corners 15%, 00swirl 5%).
- 12:52 00interlock done. Gap after r600: lone champions die on the long lanes of our half (4.4 deaths per game
  away from camps against 1.7) and the rivals take the middle elk group in their corner 6.1 times to our 2.0.
- 12:57 adgato_gemcombat1 done. Gap: gems lost on death 289 against 49 by r1000 (their kill gems are our bags);
  our banking batch grows with the collection rate, and with no gold camps and no Marcella our team gold is 0.21 of
  theirs by r600.
- 13:00 adgato_gemcombat5 done. Gap: gems lost on death 434 against 174 (bags of 80+ carried 129 rounds); the
  same banking batch as gemcombat1, with a 25-step trip from the rich groups to the one altar.
- 13:05 01corridors done. Gap: the five east lanes (groups 6-10), which we never enter: the same `covered` lock
  (elk groups 7 and 8 cover each other). Across the five maps: the cover lock (yellow, corridors, and five more maps
  by `h3_cover.py`) and the banking batch on gem-cluster maps (gemcombat1, gemcombat5) repeat; interlock is lane
  deaths.
- 13:23 Job 2 done: we use alive time like the rivals (walking about half for both); 74% (brk) and 91% (b13) of
  the capture gap is what a farming round yields. On brk that is strong-camp lives (elk -173, monolith -66 of -376;
  58% after r600): we lose 3.1 strong-camp lives per game that we hit to their capture (they 0.75). On b13, 16% of
  the gap is the cover lock. Fix idea: no futility discount on strong camps under half health.

## Method

- Games: our newest ranked games per map (`tools/helper3/h3_qmaps.py`: pages past the 100-game limit of
  `cambc matches list`, so `tools/replay/qmaps.py` alone sees only the last ~2.5 hours). Each game's `meta.tsv` line
  names the bot that was live when the game was created, from the submission list (zip size 62557 = go1, 62258 = cr3,
  60976 = cw1, other sizes are gated variants, which play ranked games while their gate runs).
- Numbers per game, us against the opponents: `tools/helper3/h3_mapsum.py` (collected, of it taken from kills,
  tributed, lost on death, deaths at r300 and r1000; first gem capture and first tribute),
  `tools/replay/firstcap.py`, `decoded.py gold`, `cohesion.py`, `deathfactors.py`, `bagdeath.py`, `hpbag.py`.
- Lane deaths: `tools/helper3/h3_deathgrp.py` (deaths by the nearest group, in the victim's own view). Cover lock:
  `tools/helper3/h3_cover.py` (all maps), `h3_lockgems.py` (gems from the locked groups in a decoded run).
- Layout: `tools/helper3/h3_layout.py data/maps_txt/<map>.txt --map` (groups with ids, gems, gold, health, walking
  steps from each spawn; zone A / mid / B by 6+ steps). `tools/helper3/h3_groups.py` counts captures, camp hits and
  presence per group, us against them, with games on side b mirrored so a group id always means the same group seen
  from our spawn.

## 01yellow_brick_road (12 ranked games, 10-27 16:00 to 10-28 05:20 UTC; 1 win)

Bots: go1 5 games, cr3 5, gated variants 2. Data: `data/fights/h3_01yellow_brick_road`.

**Layout** (40x30, 180-degree rotation, no walls). Spawns at x2-5 and x34-37, y13-16, 29 steps apart. The "road"
joins them: rows 13-16 between two rows of 30 gold clusters (y12 and y17, x5-34; each row is one group worth 600
gold, 3600 health), which act as walls until cleared. The road's camps sit on rows 14-15, so rows 13 and 16 are
one-tile lanes. Along the road, per side: 2 wolves + 2 gold (8 gems, 2 steps from spawn), 2 elks + 2 gold (30 gems,
6 steps), and in the centre two groups of 2 elks, 2 wolves, a gem and 2 gold clusters (45 gems, 300 gold, 7860
health), one per side (10 and 14 steps from our spawn), touching the two central altars (19,14) and (20,15). Ten
altars in all; each side has four within 7-10 steps off the road. Off the road, each side has two corner elk groups
(x0-1 y3-6: elk, wolf, gem, 3 gold = 26 gems, 6 steps; x3-5 y0-1: elk, gem, 2 gold = 22 gems, 11 steps), a 15-gem
wolf group 3 steps out, an elk-wolf group (19 gems, 7 steps) and small groups; mid groups (22 and 15 gems) top and
bottom. Gems per full clear: 150 per side and 172 in the middle.

**Us against them** (per game):

| | r300 us | r300 them | r1000 us | r1000 them |
|---|---|---|---|---|
| collected (of it from kills) | 98 (1) | 141 (1) | 498 (13) | 883 (22) |
| tributed | 82 | 119 | 454 | 837 |
| lost on death | 4 | 2 | 27 | 14 |
| deaths | 3.2 | 3.2 | 7.4 | 6.8 |

First gem capture median r88 against r84; first reward of any kind (`firstcap.py`) r79 against r50, third r150
against r90; team gold r100 536 against 766, r300 1894 against 2844, r600 3990 against 6985. First tribute median
r128 against r104. Deaths are even (8 of 12 games in `deathfactors.py`'s even class), carriers are safe (bags of
20+ lost 0.58 per game), and we stay together more than they do (allies within 6, r0-1000, 2.09 against 1.71). The
gap is farming: 385 gems collected by r1000, 342 of it after r300.

**Largest gap: two pairs of groups we never pick.** Captures by r1000 per game (`h3_groups.py`, ids seen from our
side):

| groups | us: captures (gems) | them, on their mirrored pair | our / their champion-rounds within 2 |
|---|---|---|---|
| our corner pair (0: 22 gems, 3: 26 gems) | 0.25 (6) | 8.4 (207) | 10 / 378 |
| centre pair (13: ours, 14: theirs; 45 gems each) | 0.92 (41) | 4.9 (224) on both | 621 / 972 |

Other groups roughly cancel (we take our road elks, 3-step wolves and south elk-wolf group more than they take
theirs). Gems by zone from the capturer's side by r1000: own 359 against 480, middle 124 against 337.

**Cause: the `covered` rule in `pick_group`.** `knowledge.h` puts into `W.covered_by[g]` every group with a camp of
reach above 3 within reach of one of g's tiles, and elks reach 4. `pick_group` (`targets.h`, "covered") skips g while
a covering group is alive and is not strong (strongest camp under 100: any elk group) and g is not a cluster-only
group, whether the elk is awake or not (golems and monoliths block only within 10 rounds of waking). The corner elk at
(0,4) is within 4 of group 0's tiles and the elk at (4,0) within 4 of group 3's, so each corner group blocks the
other while both live, and nothing ever kills either: they stay up all game. The two centre groups' elks stand 2-3
tiles from each other's tiles, so we touch the centre only after the rivals have taken their side (71% of our 31 hits
per game on group 13 come while group 14 is dead; our first hit on group 13 at r519 in e2e5000d (go1) and r393 in
e9727218 (cr3)). Replay
rounds: e2e5000d (go1, side b, lost 189-980): the rivals take their corner pair at r78 and r97 and again every 60-80
rounds (r170, r185, r246, r268, r329, r404, r413, r488, r501, r605, r621), then both centre groups from r448 (r448,
r461, r538, r587, r641); we never capture our corner pair. 4cb91349 (go1, lost 155-974): their first capture is their
corner group at r33.

`tools/helper3/h3_cover.py` replays the rule on all 70 map dumps: groups our bot can never pick while both covers
live (gems per full clear): 01hooks 88 of 88 (100%), 00fragment 52 of 68 (76%), 01boss_battle 746 of 1180 (63%;
the 400-gem guard monolith is among them: "boss_battle: we never hit the guard" in `docs/findings.md`),
01yellow_brick_road 186 of 472 (39%), 01corridors 166 of 752 (22%), 00corners 60 of 396 (15%), 00swirl 30 of 638
(5%).

**Fix idea (no map code):** an elk group covers its neighbours only while awake (hit within the last 10 rounds), as
golems and monoliths already do; a sleeping elk hits nobody, and hitting one group wakes only that group (Varg's
splash or an area spell can still wake a camp one tile away, as at the diagonal seam of the centre pair). Metric:
our captures per game by r1000 of the groups `h3_cover.py` lists as blocked (yellow now 1.2 for groups 0, 3, 13, 14;
the rivals take their mirrored four 13.3 times). Bar: 4+ per game on yellow, and on the seven maps together at least
a third of the rivals' rate on their mirrored groups; guards: deaths per game not up by more than 1.0, collected by
r1000 up. Captures are an economy metric, so a local run on the seven maps can check the mechanism before a gate.

## 00interlock (12 ranked games, 10-27 05:40 to 10-28 06:50 UTC; 2 wins)

Bots: go1 3 games, cr3 3, cw1 2, older 1, gated variants 3. 4-pick map (we draft Heart of Ruin, Vesper, Marcella,
Vendetta; 8 of the 12 opponents field Ryth, one fields Cassi and Issac, five bodies). Data:
`data/fights/h3_00interlock`.

**Layout** (40x40, 180-degree rotation). Spawns in opposite corners (x0-2 y0-2 and x37-39 y37-39), 41 steps apart.
Gem-poor: 200 gems per full clear, about 3.5 gems a round for both teams together, so games run to r1160-r1450.
Walls form a pinwheel that splits each half into lanes: on our half a wall line at y7 (x15-32, with a bush gap at
x16-25), a column at x15 (y7-15), a column at x32 (y0-7) and a line at y15 (x31-39); the mirror on theirs; a hole
block in the centre (x16-23, y19-20). Our groups: 2 gold (x19 y2, 16 steps), a wolf (x5 y8, 5 steps), gem + wolf
(x4-5 y14, 11 steps, 11 gems), gold + wolf (x4-5 y21, 18 steps), and our only elk group (2 elks, gem, gold: 37 gems)
far out in the top-right corner (x28-29 y2-4, 25 steps from us, 33 from them). Two middle elk groups (2 elks, 2 gems:
44 gems), each 28 steps from both spawns: group 4 (x31-32 y9-11) beside our elk group, group 9 (x7-8 y28-30) beside
theirs. Four altars: two in the centre ((19,16) 17 steps from us, (20,23) 17 from them) and two in the far corners
(33 steps from both).

**Us against them** (per game; games end r1163-r1445, so r1500 is the end):

| | r300 us | r300 them | r1000 us | r1000 them | r1500 us | r1500 them |
|---|---|---|---|---|---|---|
| collected (of it from kills) | 107 (2) | 97 (0) | 580 (20) | 684 (44) | 779 (24) | 991 (77) |
| tributed | 86 | 69 | 512 | 592 | 675 | 910 |
| lost on death | 2 | 9 | 46 | 32 | 79 | 35 |
| deaths | 1.2 | 0.7 | 6.2 | 4.2 | 8.8 | 5.2 |

First gem capture median r48 against r34 (ours is the gem-wolf group at r48 in 11 of 12 games); first reward median
r24 against r26, third r89 against r50, reward events by r100 2.9 against 5.3, team gold r100 136 against 317 (they
take four or five small groups in parallel by r60: 2 gold, gem-wolf, wolf, gold-wolf; we take 2 gold, then the
gem-wolf group, then the gold-wolf one). The gold gap closes by r300 (968 against 1061) and r600 (2525 against 2582).
First tribute median r146 against r118. We lead at r300 and r600 (collected 305 against 287); from r600 to the end
they collect 704 to our 474 and we die 6.2 times to their 3.2.

**Largest gap: lone champions killed in our half after r600, and the middle elk group in their corner.** By r1500,
gems from the middle: 279 against 442, of which group 9 (beside their elk group) 88 against 274 (captures 2.0 against
6.1) and group 4 (beside ours) 191 against 169 (4.3 against 3.8); gems from kills 24 against 77 and lost on death 79
against 35. Our own-half groups give 470 against their 436. Deaths: 4 of the 12 games are massacres (our deaths minus
theirs 6+ by r1000, all lost); in them 5.0 of our 8.75 deaths per game are in our own half, 4.75 more than 20 steps
from home, contacts last 11-30 rounds, and the bot was in its flee branch at 60% of the deaths (77% in the even
games: 2.0 of 2.6). Our deaths more than 5 tiles from any camp: 4.4 per game against their 1.7 (3.2 against 1.3
after r600; `tools/helper3/h3_deathgrp.py`): on the lanes, not at camps. We stand apart more (allies within 6 per
alive champion-round 0.70 against 0.97; alone 50% against 42%; r600-1000 0.58 against 0.87).

**Cause, from the trace of 43c8d164** (go1, side a, lost 457-968 to Valenki's five bodies, `tools/replay/trace.py`):
their four or five walk our half's top lane as a pack. r87-r106: our Vendetta leaves spawn alone along the top edge
toward our elk group, sees Marcella and Cassi at 8 tiles at r87 and keeps walking toward them for 9 rounds (one ally
within 6 from r93), trades hits at r95-r97 and dies fleeing at (10,0). r96-r109: our Heart of Ruin leaves our elk
group at (28,2) at 49% health (the heal rule, `bot.cpp` "Heal when worn down", sends a champion home under 50% only
if an enemy was seen in the last 30 rounds, else under 20%) and walks west along the same lane, sees the pack at r99,
keeps walking and dies at (16,2), alone from r103. r207-r219: Vendetta walks from the gem-wolf group at (4,13) toward
(10,16) into five enemies and dies; r224-r247: Heart of Ruin fights at (11,13), flees at 30% and dies at (5,10), 9
steps from spawn. The map's long lanes (our elk group is 25 steps out) make every trip a walk alone past where their
pack stands.

**Fix idea (no map code):** go home and recall at 50% health whenever home is 15+ steps away, also when quiet (the
heal rule's quiet threshold of 20% assumes home is near; on 00ribs the rivals went home at 51% health, mostly by
recall, `docs/status.md`, late night 10-27), and never take a lane step that brings a visible pack of 3+ closer (the
9 rounds of warning above). Metric: our deaths per game by r1500 more than 5 tiles from any camp (`h3_deathgrp.py`,
now 4.4 against their 1.7); bar: 2.5 or fewer; guards: collected by r1000 not below 95% of base, tributed by r1500
up. Earlier pack-avoidance variants (pa1, kb1, ob1, `docs/experiments.md`) failed on mixed panels, so judge this on
interlock and the other long-lane maps first. Cohesion alone is a weak lever: du1 (pairs) cut our alone share from
51% to 44% but raised deaths 0.5 per game (`docs/findings.md`, "Idle time and deaths near home"); sq1
(`bots/exp/sq1`) is the untested cohesion candidate.

## adgato_gemcombat1 (9 ranked games, 10-27 04:40 to 10-28 06:10 UTC; 0 wins)

Bots: cr3 2 games, cw1 2, older 3, gated variants 2 (all the gemcombat1 games in our ranked list since 10-26 21:00
UTC). 3-pick map: we draft Heart of Ruin, Vendetta, Vesper (our 3-pick draft on every 3-pick map, 173 games); 6 of
the 9 opponents field Marcella. Data: `data/fights/h3_adgato_gemcombat1`.

**Layout** (31x31, 180-degree rotation). Spawns in opposite corners (x1-3 y1-3 and x27-29 y27-29), 26 steps apart.
Six groups, each three gem clusters (21 gems, 360 health, no damage, no gold), respawn 50: per side one 3 steps
from spawn and one 10 steps along the edge, and two in the middle corners (18 steps from both). 126 gems per full
clear, about 2.5 a round for both teams. One altar, in the centre (15,15), 12 steps from each spawn, inside a ring of
holes that is open only toward each spawn's side (x9-12 y8-10 for us, the mirror for them). No camp gives gold, so
gold comes only from kills (100) and Marcella's tributes (+2 per gem).

**Us against them** (per game; games end r820-r1188):

| | r300 us | r300 them | r1000 us | r1000 them |
|---|---|---|---|---|
| collected (of it from kills) | 299 (14) | 271 (65) | 744 (51) | 1036 (288) |
| tributed | 164 | 199 | 424 | 946 |
| lost on death | 67 | 13 | 289 | 49 |
| deaths | 1.9 | 1.0 | 8.7 | 2.1 |

First capture r11 against r19 (we farm faster: reward events by r100 5.0 against 3.4); first tribute median r71
against r44. Team gold r300 115 against 278, r600 170 against 803 (0.21). Captures from camps are level by r1000
(own half 474 against 452, middle 205 against 234). 5 of the 9 games are massacres (our deaths minus theirs 6+), in
which the bot was in its flee branch at 68% of our deaths.

**Largest gap: gems lost on death, 289 against 49 by r1000.** The rivals' 288 gems from kills are our bags: the
whole collected gap (292) is gems they took off our dead. Deaths by bag (`bagdeath.py`): with 20-39 gems 2.8 per
game (58 gems), 40-79 1.6 (79), 80+ 1.0 (151); theirs 0.3, 0.6 and 0.1. Our bags of 20+ were carried 92 rounds
before the death (theirs 53). Tribute channels per game (`decoded.py channels`): we start 11.1 (7.1 of 21-50 gems,
2.6 of 51-100, 1.4 over 100), they 27.9 (23.4 of 21-50); our channels over 100 gems complete 31% (259 gems started,
56 banked per game), theirs 100%.

**Cause.** (1) Our banking batch is large on this map: the order-quantity rule (`bot.cpp`, "Order quantity", line
672) sets the batch to sqrt(6 c^2 tau / (m h + lambda c / 5)), which grows in proportion to the collection rate c,
and harmless 21-gem cluster groups make c high while the hazard h comes from our own past deaths (low early). So the
carriers hold 40-150 gems on a map whose only altar is the contested centre. (2) We lose the fights at equal
numbers and fall behind in gold, which on this map only kills and Marcella give: our 3-pick draft has no Marcella,
so our team gold stays at 170 by r600 against 803 (about 21 shards' worth less), and fights get worse as the game
goes on (deaths r300 1.9 against 1.0, r600 4.4 against 1.6). Trace 79c1f4c2 (cr3, side a, lost 672-987 to PtitLK's
Heart of Ruin, Vesper, Vendetta, the same three as ours): r36-r61 our Vesper takes 42 gems from the middle group at
(7,22), walks alone east and then up to the centre altar, trades shots with their Vesper at r45-r54, meets their
Heart of Ruin and Vendetta at the altar at r53-r59 and dies at (13,12) with the 42 gems; r62-r76 our Heart of Ruin
meets their Vendetta at (8,11) and dies 7 steps from spawn; r99-r125 our Vendetta walks alone through the centre to
(23,26), 25 steps from home beside their spawn, attacks their Vendetta and dies.

**Fix idea (no map code):** cap the banking batch at 40 gems (the rivals' typical bag here is 21-50; on normal maps
the rule already gives about 26, so the cap acts on fast-collection maps). Metric: gems lost on death per game by
r1000 on gemcombat1; bar: 150 or less (now 289); guards: tributed by r1000 up, collected not below 95%. Second
lever, platform only: a 3-pick draft with Marcella (Heart of Ruin, Vesper, Marcella, the first three of our 5-pick
draft), metric team gold at r600 on gem-only maps (170 now, bar 400).

## adgato_gemcombat5 (12 ranked games, 10-27 06:50 to 10-28 06:00 UTC; 2 wins)

Bots: cr3 3 games, cw1 4, older 4, gated variants 1. 5-pick map (we draft Heart of Ruin, Vesper, Marcella, Vendetta,
Varg; 11 of 12 opponents field Marcella too). Data: `data/fights/h3_adgato_gemcombat5`.

**Layout** (99x99, left-right mirror, much of it holes). The spawns sit side by side at the top centre (x37-40 and
x58-61, y35-38), only 18 steps apart. One altar, at (49,51), 15 steps south of both spawns, between them. 24 groups,
all gem clusters (no gold anywhere): 735 gems per full clear. Near the spawns only small groups (2-3 clusters, 14-21
gems, 23-32 steps out, three of them walled in and reachable only by dashing over holes); the rich groups are far
south: a 20-cluster group (140 gems, 2400 health) at x47-51 y75-78 (56 steps from both spawns, about 25 from the
altar), two 9-cluster groups (63 gems) at x19-21 and x77-79, y79-81 (45 steps), 5-cluster groups (35 gems) at y66-68
(39 steps from the near spawn) and in the far corners (63-65 steps). Games are short (end r434-r682): about 4.4
gems a round for both teams.

**Us against them** (per game; r1000 is the end):

| | r300 us | r300 them | r600 us | r600 them | end us | end them |
|---|---|---|---|---|---|---|
| collected (of it from kills) | 486 (72) | 523 (145) | 1025 (174) | 1180 (394) | 1064 (174) | 1235 (418) |
| tributed | 192 | 298 | 488 | 822 | 508 | 868 |
| lost on death | 145 | 72 | 410 | 174 | 434 | 174 |
| deaths | 2.9 | 2.3 | 6.1 | 5.1 | 6.2 | 5.2 |

First capture median r66 against r57, first tribute median r204 against r96. Captures from camps: ours are as good
or better (own side 229 against 156 by the end, middle 661 against 650; we take the 140-gem group 2.6 times a game
to their 2.3). Team gold r300 332 against 361 (both teams have Marcella, the only gold source besides kills).

**Largest gap: gems lost on death, 434 against 174, and so the rivals' kill gems (418 against 174).** Deaths with
80+ gems: 1.9 per game (369 gems) against their 0.75 (139); our bags of 20+ were carried 129 rounds before the death,
theirs 38. We start 8.1 tributes per game (3.2 of over 100 gems, completed 61%), they 16.7 (5.5 of 21-50, 6.9 of
51-100). Of our deaths with 30+ gems, 0.42 per game are in a channel (94 gems) and 0.75 within 3 of the altar (88
gems): the one altar sits in the rivals' home ground, 15 steps from their spawn.

**Cause: the banking batch again, now with a long trip.** The order-quantity batch (`bot.cpp`, "Order quantity")
grows with the collection rate c and with the square root of the trip tau; here a capture brings 63-140 gems and the
altar is about 25 steps from the rich groups, so a champion that holds 140 still counts as under its batch and goes
on to the next group. Bag histories in 0bc6e870 (cr3, side b, lost 504-980 to BBL): Marcella takes 63 gems at r79
and 63 more at r143, and banks the 126 only at r221; Varg takes the 140-gem group at r417, walks to a 9-cluster group
for 63 more (203 at r468) instead of banking, and dies with the 203 at (48,45), 6 tiles from the altar, at r525;
Heart of Ruin dies with 63 at (52,52), beside the altar, at r280.

**Fix idea (no map code):** the same cap as on gemcombat1: once the bag reaches 40 gems, bank before taking another
group (a capture that brings more than 40 is banked at once). Metric: gems lost on death per game by r600 on
gemcombat5; bar: 200 or less (now 410); guards: tributed by r600 up, collected by r600 not below 95%.

## 01corridors (12 ranked games, 10-27 02:20 to 10-28 02:10 UTC; 3 wins)

Bots: go1 1 game, cr3 2, cw1 1, older 6, gated variants 2. 5-pick map. Data: `data/fights/h3_01corridors`. (A first
run of `h3_groups.py` mirrored side-b games by 180-degree rotation, which also maps this map's centred spawns onto
each other; the tools now take the symmetry from the dump header, which says top-bottom mirror. The numbers below
are from the corrected run; the other four maps were mirrored correctly.)

**Layout** (51x40, top-bottom mirror). Spawns at the top and bottom centre (x24-26, y0-2 and y37-39), 35 steps apart.
Wall columns every 4 tiles (x3, 7, ..., 47) cut the map from y3 to y36 into twelve 3-wide vertical lanes; lanes
connect only along the top and bottom rows (and over a few one-tile holes in the walls, by dash). Every camp group
sits on the mirror rows y19-20 and fills its lane, so each group is a gate that both teams reach from opposite ends,
at the same distance. Centre lane: 2 monoliths + 4 gems (428 gems, 40480 health, 16 steps). West of it: group 4
(2 elks + 4 gems, 58 gems, 17 steps), group 3 (4 wolves + 2 gold, 16 gems, 21), group 2 (8 gems, 25), the altar lane
((13,19) and (13,20), 25 steps; it stays open past the altars), group 1 (16 gems, 33) and group 0 (2 elks, 2 gems,
2 gold: 44 gems, 37). East of it: group 6 (4 wolves + 2 gold, 16 gems, 17 steps), group 7 (4 elks + 2 gold, 60 gems,
21), group 8 (2 elks, 2 gems, 2 wolves: 52 gems, 25), group 9 (2 elks + 4 gold, 30 gems, 29), group 10 (8 gems, 33),
group 11 (16 gems, 37). 752 gems per full clear.

**Us against them** (per game; games end r1170-r1555):

| | r300 us | r300 them | r1000 us | r1000 them |
|---|---|---|---|---|
| collected (of it from kills) | 124 (3) | 100 (6) | 440 (22) | 628 (21) |
| tributed | 56 | 60 | 367 | 474 |
| lost on death | 9 | 8 | 28 | 62 |
| deaths | 1.1 | 1.6 | 4.2 | 7.1 |

First capture median r58 against r51, first tribute median r282 against r178 (the altar lane is 25 steps out).
Team gold r300 637 against 965, r1000 2656 against 4781 (0.56). No massacres: we die less than they do, carriers
are safe (deaths with 20+ gems 0.6 per game) and channels complete (97-100%). The gap is farming.

**Largest gap: the five east lanes, which we never enter.** Captures by r1000 per game (`h3_groups.py`): groups 6-10
us 0 (0 gems), them 6.4 (197 gems); our camp hits on them 0 and our champion-rounds within 2 of them 0 in all 12
games (theirs 87-171 per group). We put our farming into group 4 (5.4 captures, 314 gems, against their 3.5 and 203)
and the west lanes 0-3 (102 gems against 164). Group 11 at the far east edge: 0.08 against 0.5.

**Cause: the `covered` rule again** (see 01yellow_brick_road). Group 7's elks stand 2 tiles from group 6's and group
8's tiles, group 8's from 7's and 9's, group 9's from 8's and 10's, so 7 and 8 lock each other and 6, 9 and 10 sit
behind them: `h3_cover.py` lists groups 6-10 (166 gems per clear) as never pickable while 7 and 8 live. The rivals do
kill 7 and 8 (1.0 and 1.1 times per game), which would free 6 and 9 for a while, but our champions never see those
lanes, so our knowledge keeps 7 and 8 alive. On the west side group 4's elks cover 3 and the monolith lane, so those
wait for group 4 to die, which we do (5.4 times).

**Fix idea:** the same as on yellow: an elk group covers its neighbours only while awake. Metric: our captures per
game of groups 6-10 by r1000 (0 now, theirs 6.4); bar: 3 or more; guards: deaths per game not up by more than 1.0,
collected by r1000 up.

## Across the five maps

Two causes repeat, and both live in general code, not in the maps. (1) **The `covered` rule** in `pick_group`
(`targets.h`): any group within reach 4 of a live elk group is skipped, sleeping elk or not, so elk groups that sit
within 4 of each other lock each other for good. It costs us our corner pair and the centre pair on
01yellow_brick_road (we take them 1.2 times per game by r1000, the rivals their mirrored four 13.3 times) and the
five east lanes on 01corridors (0 against 6.4), and `h3_cover.py` finds the same lock on 01hooks (all 88 gems per
clear), 00fragment (76%), 01boss_battle (63%, including the 400-gem guard), 00corners (15%) and 00swirl (5%): seven
of our worst maps. One change (elks cover only while awake, as golems and monoliths do) addresses all seven, and its
metric (captures of the listed groups) can be checked locally before a gate. (2) **Carriers lose their bags on
gem-cluster maps.** On adgato_gemcombat1 and adgato_gemcombat5 we collect as much from camps as the rivals but lose
289 and 434 gems per game on death (they 49 and 174), and those bags become their kill gems; the order-quantity
batch (`bot.cpp`, "Order quantity") grows with the collection rate and the trip length, so on maps with harmless,
rich cluster groups and one contested altar the carriers hold 40-200 gems for 90-130 rounds. A cap on the batch (about
40 gems) is the simple fix. 00interlock is the odd one: its gap is lone champions dying on long lanes after r600
(4.4 deaths per game away from camps against 1.7), the cohesion and fleeing problem seen on other maps before.

## Job 2: why the rivals collect about twice our gems (go1 on brk and b13, to r1000)

Runs (read only): `data/fights/main_brk1028_brk` (100 games, the five bad maps 00ribs, 00contest, 00crater, 00packs,
00eight) and `data/fights/main_b13_1028_b13` (50 games on 50 maps), both go1, decoded; and for comparison
`data/fights/tg1e_brkp2_brkp2` (tg1 on brkp2, which is pinned to main_brk1028's games, so the same opponents and
maps). Readers: `tools/helper3/h3_gemgap.py` (source, time band, activity per champion-round, decomposition),
`h3_lives.py` (camp-hit rounds by who captured the life), `h3_lostlives.py` (strong-camp lives one side hit and the
other captured), `h3_campdmg.py` (damage per camp hit), `h3_lockgems.py` (gems from the groups `h3_cover.py` lists).
Outputs in `data/helper3/h3_*_{brk,b13,tg1e}.txt`.

Collected by r1000: brk 373 against 749, b13 604 against 803 (deaths 9.6 against 4.9 and 6.5 against 3.8).

**By source** (gems per game, us / them, gap):

| source | brk | b13 |
|---|---|---|
| elk groups | 178 / 351 (-173) | 304 / 346 (-42) |
| monolith groups | 6 / 72 (-66) | 13 / 20 (-8) |
| cluster-only groups | 63 / 119 (-56) | 119 / 176 (-57) |
| wolf groups | 77 / 121 (-44) | 106 / 144 (-37) |
| golem groups | 26 / 35 (-9) | 43 / 52 (-9) |
| kills (the killer takes the bag) | 22 / 47 (-24) | 20 / 52 (-32) |

Captures make 94% of the brk gap and 84% of the b13 gap; kills the rest.

**By time** (captures; kills): brk r1-300 -45 (0), r301-600 -90 (-9), r601-1000 -217 (-16): 58% of the brk gap
comes after r600, mostly strong camps (elk lives r601-1000: our 2.1 captures against their 4.3, and nearly all of
their monolith captures). b13: -35 (-10), -64 (-14), -68 (-8).

**Per champion-round** (brk; shares of alive rounds, us / them): walking 60% / 58% (empty and healthy 49% / 47%, with
a bag of 20+ 6% / 7%, under half health 5% / 4%), farming 13% / 15%, on a dead group's tiles 5% / 5%, fighting 5% /
6%, waiting 9% / 9%, at home 6% / 5%, banking 1% / 2%; dead 12% of all champion-rounds against 6% (560 against 280
per game). b13 is the same picture (walking 51% / 52%, farming 20% / 19%, waiting 9% / 8%, dead 9% / 5%). We use our
alive time as they do.

**Decomposition.** Capture gems = alive champion-rounds x share of them farming or on a dead group's tiles x capture
gems per such round. brk: 351 / 702 = 3947 / 4385 x 0.185 / 0.199 x 0.48 / 0.80; share of the log gap: alive rounds
15%, farm share 11%, **gems per farming round 74%**. b13: 585 / 751 = 3634 / 3833 x 0.277 / 0.269 x 0.58 / 0.73;
alive rounds 21%, farm share -13% (we farm more), gems per farming round 91%. tg1 on the same brk games: 0.49 / 0.77,
93% of the log gap.

**The largest piece: what a farming round yields, and on brk that is strong-camp lives.** Within a camp type a
capture is worth the same to both sides (elk lives 41 against 42 gems, golem 64 against 66, monolith 200), and our
damage per camp hit is the same as theirs (elks 64 / 63 at r1-300, 96 / 101 at r301-600, 140 / 140 at r601-1000 on
brk; b13 alike), so it is not weaker hits. On brk we put the same share of our camp hits into elk groups as they do
(40% against 39%), but finish 4.4 elk lives per game to their 8.3, and their 0.36 monolith lives per game (72 gems,
00contest) to our 0.03. Our captures are cheaper on average (9.7 gems per capture against 17.7; 66% of ours are
cluster-only groups, many of them gold, against 52%). 16% of our camp-hit rounds (elk 19%) go into lives the rivals
then capture, theirs 4% (3%). Strong-camp lives we hit and they capture: 3.1 per game against 0.75 the other way
(b13 2.0 against 0.6). In 53% of those the rivals resume hitting it while one of ours still stands within 6 (a camp
fight we lose; one of ours dies before their capture in 14%), in 30% after we left; 39% are left under 30% health,
and they capture 34 rounds after our last hit on average. tg1 (cl1 + the opening) on the same games lowers our lost
elk share to 14% and the elk gap to -105 (elk captures 4.7 against 7.1), but leaves 2.3 lost strong-camp lives per
game. On b13 a second piece is the cover lock of the map sections above: 6 of b13's 50 maps have groups our bot
never picks, and those groups give the rivals 43 gems per game over the whole panel against our 11, 32 of the
198-gem gap (16%).

**Fix idea:** camps never heal, so a damaged strong camp is the cheapest gems on the map: in `pick_group`, the
futility discount (`targets.h`, `score /= 1.0 + group_invested[i] / 150.0`, which grows with every round this
champion spent on the group) should not apply to a group under half its health, and a champion that has to leave one
(heal, flee) should not count it as worth less on its return. This targets the 30% of lost lives we walk away from
and the 39% left under 30% health. Metric: strong-camp lives we hit and the rivals capture, per game by r1000
(`h3_lostlives.py`; go1 brk 3.13, tg1 2.28, theirs 0.75-0.91); bar: 1.5 or fewer on brkp2; guards: our elk
captures per game up (4.4), deaths per game not up by more than 0.5. The contested half (we stand there and lose the
camp fight) is the fighting gap the team has worked on all week (turn order, stuns, packs); the cover-lock fix of the
map sections is the separate, larger lever on normal panels (16% of the b13 gap) and on the seven lock maps.

## Job 3: the cover fix h3cv1 (10-28, 13:30-14:10)

**Change** (`bots/exp/h3cv1` = go1 with one edit in `pick_group`, `targets.h`): an elk group covers its neighbours
only while it is awake (seen awake within 10 rounds), as golems and monoliths already did. Diff:
`docs/helper3/patches/h3cv1.patch` (`patch -p1` inside a bot folder; removes the `strong` and `cluster` tests, which
only served the asleep-elk case, and adds a comment with the h3_cover.py numbers). Built `--release` clean. Dry runs
(`patch -p1 --dry-run` on copies in `data/helper3/dry/`): applies to `bots/exp/tg1` and `bots/exp/uf1` (hunk at line
159, offset -1). Pushed with the rest of HEAD to `origin/h3/cloud-1028` (user, 13:38: pushing allowed).

**Local check** (`data/runs/multi-134001`, main and exp/h3cv1 against pool/cand1, pool/cp3, pool/dh3 on the seven lock
maps, both sides: 42 games each, `--jobs 2` at 1.5 GB free RAM with the user's approval; decoded into
`data/fights/local_multi-134001_main` and `..._exp.h3cv1`). Local opponents are our own old bots with the same cover
rule, so these games show the mechanism and the economy, not fights.

(a) Mechanism: captures of the locked groups per game by r1000 (`tools/helper3/h3_jsoncaps.py`, from the statistics
JSONs; ours / all ours / the opponent's of locked groups):

| map | main | h3cv1 |
|---|---|---|
| 01yellow-brick-road | 1.67 / 50.2 / 1.17 | 20.33 / 47.7 / 0.83 |
| 01corridors | 0.00 / 14.2 / 0.00 | 4.33 / 14.0 / 0.00 |
| 01hooks | 4.17 / 52.2 / 3.33 | 15.00 / 42.7 / 10.17 |
| 00fragment | 0.00 / 29.0 / 0.00 | 9.67 / 32.8 / 11.67 |
| 01boss-battle | 0.00 / 74.5 / 0.00 | 26.33 / 58.2 / 0.50 |
| 00corners | 0.17 / 63.7 / 0.00 | 13.50 / 55.0 / 7.33 |
| 00swirl | 2.67 / 37.8 / 5.17 | 12.33 / 43.3 / 7.50 |
| all seven | 1.24 / 45.9 / 1.38 | 14.50 / 42.0 / 5.43 |

The opponents' captures of locked groups rise too: a pair split across the two halves (00fragment, 00corners)
unlocks for them once we take our half.

(b) Gems per game to r1000 (`tools/helper3/h3_bymap.py`, as `decoded.py gems`), us / them, main against h3cv1:

| map | wins | collected | tributed | lost on death | our deaths |
|---|---|---|---|---|---|
| 01yellow-brick-road | 3 -> 6 of 6 | 788 / 755 -> 1034 / 516 | 751 -> 976 | 17 -> 7 | 7.8 -> 5.0 |
| 01corridors | 3 -> 5 | 419 / 491 -> 448 / 421 | 364 -> 391 | 19 -> 20 | 7.7 -> 7.0 |
| 01hooks | 4 -> 3 | 77 / 51 -> 354 / 205 | 77 -> 332 | 4 -> 11 | 6.7 -> 9.3 |
| 00fragment | 4 -> 2 | 118 / 115 -> 334 / 414 | 108 -> 304 | 3 -> 18 | 2.8 -> 3.5 |
| 01boss-battle | 5 -> 3 | 1695 / 1548 -> 2225 / 1761 | 0 -> 390 | 5 -> 438 | 1.0 -> 2.2 |
| 00corners | 5 -> 3 | 1041 / 991 -> 945 / 927 | 946 -> 793 | 10 -> 73 | 2.3 -> 5.8 |
| 00swirl | 1 -> 4 | 469 / 789 -> 649 / 482 | 412 -> 547 | 44 -> 56 | 10.5 -> 10.5 |
| all 42 games | 25 -> 26 | 658 / 677 -> 855 / 675 | 380 -> 533 | 15 -> 89 | 5.5 -> 6.2 |

Collected +30% and tributed +40% overall, with yellow the clearest gain (6 of 6, tributed +225, deaths -2.8).
On 01boss-battle main never tributes by r1000 (the guard monolith is locked, 0 hits); h3cv1 kills it and banks 390,
but carries big bags into the altar fight (lost on death 438). The one map that got worse is 00corners (tributed
-153, deaths +3.5): its locked pair sits near the middle (17 and 20 steps), so taking it means fighting there.

(c) Elk hits taken per game to r1000 (`tools/helper3/h3_elkdmg.py`, inferred: each live elk of a group hit in the
last 3 rounds hits its nearest champion within 4 for 60): us 506 -> 623 (+23%, about +7,000 damage before Jungle),
of which "bystander" hits (an elk of a group the victim was not hitting) 14 -> 19 per game, 3% in both; deaths within
3 rounds of a bystander hit 0.26 -> 0.21. The extra elk damage is from farming the unlocked elk groups, not from
waking sleeping neighbours.

**Proposed gate rule on bwm** (the lead writes the final rule; base = go1 or the current main in the same session,
or the pinned base):
- Mechanism: our captures per game of the locked groups by r1000 (`python -I tools/helper3/h3_lockgems.py --quiet
  DIR`, which reads `data/maps_txt` and mirrors side-b games): on the 01yellow_brick_road games 6 or more (ranked
  go1 1.2), on the 01corridors games 2 or more (ranked 0).
- Target, on the 40 yellow and corridors games: collected by r1000 at least +15% over the base (ranked go1: 498 and
  440 a game) and tributed by r1000 up.
- Guards: on yellow and corridors our deaths per game up by at most 1.0; on the 60 interlock, gemcombat1 and
  gemcombat5 games (no locked or delayed groups there, so the patch changes no decision; on a pinned panel nearly
  every game should be identical) collected and tributed at least 95% of the base and our deaths up by at most 0.5.
- Record wins without judging them. Watch 00corners and 01boss-battle (bags lost at the altar fight) on a broad panel
  before adopting; a 70-map local check of h3cv1 against main is running on a cloud agent.

## Job 4: the bank batch on gem-rich maps, h3bq1 (10-28, 14:00-14:15)

**Mechanism, measured.** Probe twin h3bql (go1 plus one `BQ` line every 10 rounds while carrying 10+ gems in the bank
stage: batch, collection rate c, trip tau, m x h, lambda; `docs/helper3/patches/h3bql.patch`; the folder is deleted,
never shipped), local run `data/runs/multi-141017` (main, exp/h3bq1, exp/h3bql against pool/cand1, pool/cp3, pool/dh3
on adgato-gemcombat1-5, 01the-farm, 00road-of-riches, 00great-wall, both sides: 48 games each), read with
`tools/helper3/h3_bqprobe.py`. go1's batch on these maps: quartiles 31 / 52 / 75 gems (gemcombat1 31 / 50 / 67,
gemcombat5 36 / 65 / 94, road_of_riches 36 / 65 / 89), with c 0.25-0.35 gems per alive round (two to three times a
normal map's), tau 24-78; in 29% of the probe's carrying rounds a champion holds 40+ gems and is still under its
batch (gemcombat5 45%). The rivals' bag at a tribute start on the platform (`tools/helper3/h3_tribbag.py`, our ranked
games): gemcombat1 median 21 (q3 42; ours 42, q3 63), gemcombat5 63 (q3 84; ours 63, q3 140), brk 33 (ours 30).
Platform exposure, champion-rounds per game carrying 40+ / 80+ gems to r1000: gemcombat1 us 687 / 227, them 355 / 57;
gemcombat5 us 817 / 441, them 414 / 148.

**Change** (`bots/exp/h3bq1` = go1 with one edit, `bot.cpp` "Order quantity"): `batch = min(40, sqrt(...))`, with a
comment citing the numbers above. Diff: `docs/helper3/patches/h3bq1.patch`; built clean; dry runs apply to tg1
(exact) and uf1 (offset 16).

**Local numbers** (48 games each, to r1000, from the statistics JSONs: `tools/helper3/h3_jsonbank.py`, which agrees
with `decoded.py gems` on tributed and lost on death; main -> h3bq1):

| map | tributes | median bag tributed | rounds carrying 40+ / 80+ | tributed | lost on death | our deaths |
|---|---|---|---|---|---|---|
| adgato-gemcombat1 | 17.8 -> 21.8 | 42 -> 42 | 737 / 186 -> 487 / 94 | 882 -> 934 | 72 -> 51 | 3.2 -> 3.5 |
| adgato-gemcombat5 | 9.7 -> 12.5 | 63 -> 63 | 1003 / 374 -> 860 / 374 | 840 -> 970 | 225 -> 234 | 5.7 -> 5.8 |
| adgato-gemcombat2 | 13.7 -> 15.8 | 63 -> 49 | 755 / 234 -> 489 / 95 | 964 -> 916 | 58 -> 62 | 3.3 -> 3.3 |
| adgato-gemcombat3 | 17.8 -> 21.0 | 42 -> 42 | 493 / 125 -> 373 / 31 | 856 -> 951 | 91 -> 76 | 4.0 -> 3.2 |
| adgato-gemcombat4 | 17.7 -> 16.3 | 42 -> 42 | 647 / 151 -> 712 / 193 | 960 -> 860 | 56 -> 111 | 3.7 -> 3.0 |
| 00great-wall | 12.7 -> 15.5 | 58 -> 50 | 1435 / 526 -> 1020 / 524 | 788 -> 863 | 117 -> 78 | 4.2 -> 3.2 |
| 00road-of-riches | 21.2 -> 21.2 | 36 -> 41 | 1488 / 406 -> 937 / 160 | 985 -> 934 | 10 -> 54 | 0.8 -> 1.8 |
| 01the-farm | 9.8 -> 10.5 | 66 -> 59 | 1416 / 752 -> 1342 / 660 | 813 -> 761 | 49 -> 37 | 0.7 -> 1.3 |
| all eight | 15.0 -> 16.8 | 49 -> 43 | 997 / 344 -> 778 / 266 | 886 -> 899 | 85 -> 88 | 3.2 -> 3.1 |

The cap does what it should to exposure (rounds carrying 40+ -22%, 80+ -23%; gemcombat1 80+ halved), but locally the
gems lost on death do not fall (85 -> 88): our old pool bots do not hunt carriers the way the platform rivals do, so
the outcome is a platform question. On gemcombat5 the 80+ exposure does not move: one capture there brings 63-140
gems at once, and the 25-step walk to the one altar follows either way. Wins (not judged) 31 -> 35.

**Proposed gate rule on bwm** (the cap binds on gemcombat1, gemcombat5 and 01corridors, where our tribute bag median
is 58, a little on 00interlock (37), hardly on 01yellow_brick_road (19)):
- Mechanism: our champion-rounds carrying 40+ gems per game by r1000 on the 40 gemcombat1 and gemcombat5 games
  (`h3_tribbag.py` on the decoded run; ranked go1-era base 687 and 817): at least 25% fewer than the base.
- Target: gems lost on death per game on those 40 games at least 30% lower (ranked base 289 and 434), tributed by
  r1000 not lower.
- Guards: our deaths per game on those maps up by at most 0.5; on the other 60 games collected and tributed at least
  95% of the base and our deaths up by at most 0.5.
- h3cv1 and h3bq1 touch different files and act on mostly different bwm maps (the cover lock on yellow and corridors,
  the cap on gemcombat1, gemcombat5 and corridors), so one combined gate could judge both by map if the lead prefers
  to save quota; "one factor at a time" argues for two gates.
