# Which part plays the worst ranked maps: a local per-map screen (Bamboo against bot_10)

Written Mon, Nov  2, 2026, 02:30 IST, before the run.

## Why

1478 (and our copy hy1) plays the Bamboo bot on maps whose spawn walk is under 61 and bot_10 on the rest. Its ranked
record on some five-a-side maps is far below its 49% five a side (800 ranked games to 01:37 IST 11-02,
`data/ranked_1102_0137.json`; the last 225 games are the 1478 era): 00monolith 0 of 12 (0 of 5 recent; sd 49, Bamboo),
02uncharted_lands 2 of 10 (42, Bamboo), adgato_gemcombat5 3 of 9 (18, Bamboo), 01elk_arena 4 of 11 (19, Bamboo),
01yellow_brick_road 4 of 11 (29, Bamboo), 00elkring 5 of 13 (31, Bamboo); 00expanse 2 of 12 (0 of 5 recent; 85,
bot_10), 01big_world 2 of 14 (139, bot_10), 01fracture 3 of 11 (160, bot_10), 01boss_battle 3 of 10 (no walking way,
Bamboo). The split at 61 came from a local head to head over all maps (findings, 11-01 "bot_10 on far maps"), where
bot_10 also won the near maps 00monolith (6 of 8) and 00stampede (8 of 8). A per-map choice is a small factor with a
direct ranked count.

## Screen

Both whole bots, `bamboo458sf` (hy1's near part) and `exp/b10n` (hy1's far part), on the ten maps above, against eight
pool bots (pool/bb2, pool/fin1, pool/vx1, pool/cp3, pool/bot_10, pool/rz20, pool/dh3, pool/cand1), both sides: 16 games
per map and bot.

## Bar (per map)

A map moves to the other part only if the other part wins at least 5 more of its 16 games than the part that plays it
now, and its gem margin per game is higher. (Ten maps at about 1.8 standard deviations each: under one map is expected
to pass by chance.) Maps that pass become one variant of hy1 (`main.cpp` routing by a map signature); that variant
then goes to the platform on a panel of those maps, judged on wins and margin on them against hy1, the same games
pinned. No map passing: nothing goes to the platform.

## Result of the screen (02:36 IST, `data/runs/multi-023038`, `tools/local/routemaps.py`)

| map | Bamboo wins, margin a game | bot_10 wins, margin a game | plays now | other part clears the bar |
|---|---|---|---|---|
| 00monolith | 8 of 16, -30 | 14 of 16, +415 | Bamboo | **yes** |
| 01yellow_brick_road | 5, -184 | 9, +60 | Bamboo | no (4 more wins) |
| 01boss_battle | 10, +217 | 12, +695 | Bamboo | no |
| adgato_gemcombat5 | 13, +266 | 14, +640 | Bamboo | no |
| 02uncharted_lands | 10, +91 | 10, +98 | Bamboo | no |
| 00elkring | 9, +54 | 7, +16 | Bamboo | no |
| 01elk_arena | 13, +632 | 6, -58 | Bamboo | no |
| 00expanse | 8, -11 | 12, +168 | bot_10 | no |
| 01big_world | 4, -232 | 13, +145 | bot_10 | no |
| 01fracture | 4, -198 | 8, -16 | bot_10 | no |

Only 00monolith moves: variant hym (hy1, `main.cpp`: a 50 x 50 map with a spawn walk of 45-55 plays bot_10; on the
70 maps that is 00monolith alone, sd 49; the other 50 x 50 maps have 19, 39, 41 and 73).

## hym's own local bar (written 02:37 IST, before its run)

hy1 and hym against the same eight pool bots on the five 50 x 50 maps (00monolith, 00contest, 00rows, 01elk_arena,
01starfish), both sides, 80 games each. hym passes if: no bot fault; on the four other maps every game equals hy1's
(winner and margin: the routing touches only 00monolith); on 00monolith hym wins at least 5 more of its 16 games than
hy1 and its margin a game is higher. Then the platform: a panel of 00monolith games, hy1 (1484, selected) as the base,
then hym on the same games pinned; hym is kept if it wins more of those games than hy1 and its margin a game is higher
by more than one standard error (`rcmp.py`).

## hym's local result (02:40 IST, `data/runs/multi-023744`)

No bot fault (160 of 160 games). On 00contest, 00rows, 01elk_arena and 01starfish all 64 games equal hy1's (winner,
rounds and gems). On 00monolith hym won 14 of 16 (margin +409 a game) against hy1's 4 (-28). hym passes its local bar.

## Platform rule (written 02:42 IST, before any game)

A group must hold five different maps (a group of 00monolith five times was refused: "Choose exactly five different
maps", HTTP 400). Panel m42 (`results/panels/specs_m42.txt`): the 18 teams ranked 35-53 on the 02:45 ladder (we are
44th, 2077.5), one group each: 00monolith with our side alternating a, b by team, plus 01yellow_brick_road,
01boss_battle, adgato_gemcombat5 and 00expanse (the near misses of the screen, as a base for later variants). Base:
hy1 (1484, selected) on m42; the panel is then pinned to that run (m42p) and hym is uploaded for m42p.

- Target, the 18 monolith games: hym kept if it wins more of them than hy1 and its margin a game is higher by more
  than one standard error.
- Guard: on the 72 other games, at most 2 differ in winner between the two runs; more makes the run void (the build
  would differ outside 00monolith).
- Wins elsewhere are not judged. A pass is a proposal to the user: 1478's source gets the same routing line.

## The other four- and five-a-side maps (written 02:50 IST, before the run)

The same screen on the 48 remaining four- and five-a-side maps (`data/maps_route2.txt`), the same eight pool bots, 16
games per map and bot. With 48 maps the first bar alone would pass one or two maps by chance, so it has two stages:
1. as above: the other part wins at least 5 more of 16 and has the higher margin;
2. a map that clears stage 1 is played again against eight other pool bots (pool/hb4, pool/dr3, pool/fe1, pool/mi8,
   pool/ts1, pool/sq2, pool/cmb7, pool/k5), both sides, and the other part must again win at least 3 more of 16 with
   the higher margin.
Maps that clear both join hym's routing in a new variant, which then needs its own local check (no fault, other
maps unchanged) before the platform.

Stopped at 03:05 IST when the session closed: 1195 of 1536 games (`data/runs/multi-024657`). Bamboo's 16 games are
complete on the first 40 maps, bot_10's only 8-10 per map, so no map is judged (`routemaps.py` flags made on unequal
game counts are not passes). The partial games repeat the 11-01 pattern: on near maps the Bamboo bot wins far more
(00contest 16 of 16 against 8 of 10, 00crater 16 against 6 of 10, 00gemfight 16 against 4 of 10, 02crossing 16
against 5 of 8).

## hym on the platform: not run (03:00 IST)

The chain waited for quota (50 of 50 used, reset 03:08) and was stopped before any game: a teammate made 1488 live
at 02:26 IST ("v540 = v484 with shorter waits"), which drafts bot_10's picks on every map, so it plays bot_10 on near
maps and three a side too; the runner's `GATE_RESTORE=1478` would have put 1478 back over it. hym's question (which
part plays 00monolith inside the 1478 hybrid) is moot while 1488 is live: 1488 already plays bot_10 there.
