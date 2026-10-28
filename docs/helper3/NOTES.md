# h3 notes: map research for task 6 (10-28)

Third agent ("h3"). Read-only on the shared docs; everything h3 learns is here. Tools in `tools/helper3/`, outputs in
`data/helper3/`, replays in `data/replays/platform/h3_*`, decodes in `data/fights/h3_*`.

## Latest (IST)

- 12:45 01yellow_brick_road done. Cause: the `covered` rule in `pick_group` (`targets.h`) never lets us pick a group
  within reach 4 of a live elk group, even a sleeping one; two elk groups that cover each other block each other for
  good. On yellow that is our corner pair and the centre pair (39% of the map's gems). `tools/helper3/h3_cover.py`
  finds the same lock on 7 of 70 maps (01hooks 100% of gems, 00fragment 76%, 01boss_battle 63%, yellow 39%,
  01corridors 22%, 00corners 15%, 00swirl 5%).
- Next: 00interlock, adgato_gemcombat1, adgato_gemcombat5, 01corridors (downloads running).

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
