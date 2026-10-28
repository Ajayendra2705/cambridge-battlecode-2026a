# h3 notes: map research for task 6 (10-28)

Third agent ("h3"). Read-only on the shared docs; everything h3 learns is here. Tools in `tools/helper3/`, outputs in
`data/helper3/`, replays in `data/replays/platform/h3_*`, decodes in `data/fights/h3_*`.

## Latest (IST)

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
- Next: 01corridors.

## Method

- Games: our newest ranked games per map (`tools/helper3/h3_qmaps.py`: pages past the 100-game limit of
  `cambc matches list`, so `tools/replay/qmaps.py` alone sees only the last ~2.5 hours). Each game's `meta.tsv` line
  names the bot that was live when the game was created, from the submission list (zip size 62557 = go1, 62258 = cr3,
  60976 = cw1, other sizes are gated variants, which play ranked games while their gate runs).
- Numbers per game, us against the opponents: `tools/helper3/h3_mapsum.py` (collected, of it taken from kills,
  tributed, lost on death, deaths at r300 and r1000; first gem capture and first tribute),
  `tools/replay/firstcap.py`, `decoded.py gold`, `cohesion.py`, `deathfactors.py`, `bagdeath.py`, `hpbag.py`.
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
Vendetta; 8 of the 12 opponents field Ryth, one fields Cassi and Issac, five bodies). Data: `data/fights/h3_00interlock`.

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
after r600; `tools/helper3/h3_deathgrp.py`): on the lanes, not at camps. We stand apart more (allies within 6 per alive champion-round 0.70 against
0.97; alone 50% against 42%; r600-1000 0.58 against 0.87).

**Cause, from the trace of 43c8d164** (go1, side a, lost 457-968 to Valenki's five bodies, `tools/replay/trace.py`):
their four or five walk our half's top lane as a pack. r87-r106: our Vendetta leaves spawn alone along the top edge
toward our elk group, sees Marcella and Cassi at 8 tiles at r87 and keeps walking toward them for 9 rounds (one ally
within 6 from r93), trades hits at r95-r97 and dies fleeing at (10,0). r96-r109: our Heart of Ruin leaves our elk group at (28,2) at 49% health (the heal rule
(`bot.cpp`, "Heal when worn down") sends a champion home under 50% only if an enemy was seen in the last 30 rounds,
else under 20%) and walks west along the same lane, sees the pack at r99, keeps walking and dies at (16,2), alone
from r103. r207-r219: Vendetta walks from the gem-wolf group at (4,13) toward
(10,16) into five enemies and dies; r224-r247: Heart of Ruin fights at (11,13), flees at 30% and dies at (5,10), 9
steps from spawn. The map's long lanes (our elk group is 25 steps out) make every trip a walk alone past where their
pack stands.

**Fix idea (no map code):** go home and recall at 50% health whenever home is 15+ steps away, also when quiet (the
heal rule's quiet threshold of 20% assumes home is near; the rivals go home at about half health, mostly by recall,
`docs/findings.md`, 00ribs), and never take a lane step that brings a visible pack of 3+ closer (the 9 rounds of
warning above). Metric: our deaths per game by r1500 more than 5 tiles from any camp (`h3_deathgrp.py`, now 4.4
against their 1.7); bar: 2.5 or fewer; guards: collected by r1000 not below 95% of base, tributed by r1500 up. Earlier pack-avoidance variants (pa1, kb1, ob1, `docs/experiments.md`)
failed on mixed panels, so judge this on interlock and the other long-lane maps first. A cohesion variant (sq1,
`bots/exp/sq1`, teammates within 6 at r300-1000 locally 1.25-1.31) is the other lever for the 0.70 against 0.97 gap.

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
