# Decision rule: per-map router between the Bamboo line and v1503 (bots/exp/rt1), written 11-03 before any result

**Factor.** Map choice: the two lines differ strongly per map. Within the same opponent since 10-31 23:00 UTC (`tools/platform/mapstrat.py`), the Bamboo line beats the
bot_10 line on some near maps by 20-50 points (00interlock +53, 00fragment +39, adgato_gemcombat1 +32, 02crossing +29, 00corners +31, 00anvil +22, 00dunes +32), and
loses on far maps (near overall +2.5 +- 1.6, far -16.1 +- 2.8). Those differences compare lines, not the exact bots: the Bamboo line holds many versions and bot_10
holds several too. So the table needs a check with the exact bots.

**Metric.** Win rate on the routed maps, pinned pairs: v1472 (Bamboo) against v1512 (v1503) on panel `b1p` (12 teams x 5 maps, 60 games on 15 candidate maps).
Exact pairs by `tools/platform/rcmp.py base1503_b1p@b1p v1472_b1p@b1p`, per map by `tools/platform/mapcmp.py`.

**Table rule, written before the b1p result.** A map stays in `kBambooMaps` when it has z >= 2 in `mapstrat.py` and is not behind on `b1p` by more than 1 of its games.
A map at z < 2 joins only when `b1p` shows it ahead by at least 2 of its games. The table comes from these two sources and from no other choice; b1p picks on 15 maps with
4 games a map is noisy, so it can only veto or confirm, never carry a map alone from z < 1.

**Local screen of the router.** `tools/local/screen.sh` with the same pool. Bars, written before it runs:
1. Routing is correct: on a default map the router's decisions match v1503, so games with the same seed have the same result as v1503 (the first default-map game is checked with the same seed against `pool/v1503`; a difference means the signature read changed something).
2. No fault: no crash or timeout on any map (`tools/replay/decoded.py` and the run's error count).
3. Fuel: the signature read costs less than 1% of the first turn's budget (its six counts run once); turn-time faults on the fast path do not rise.
4. On routed maps the win rate is at least the Bamboo bot's own local rate minus 1 se (the same code, so no drop).
Local cannot prove the choice is right: a local pass only says the router works as a program. It does not judge the map table, because local pool bots are not the ladder's teams.

**Platform.** After the local pass: routed maps pinned, the router against v1512 on `b1p` restricted to the routed maps. Target: wins on routed maps up by at least 1 se in pairs, and no default-map change (those games should be the same bot, so a paired control on some default maps gives 0 expected flips beyond the platform's noise). Guards: no fault in decoded games; wins on default maps not down by more than 1 se. Wins are recorded as the targeted factor here, because the factor is the map choice itself and the win rate per map is its metric (user, 11-03: "try to go for map wise fixes").

**Base.** The router's default is v1503 because its source is in the repo. Eric's 1513 (v1503 with every-turn recall and bush wards) is live and leads v1503 in pairs (42 vs 36 of 160); when its source reaches the repo the default arm should be 1513, tested the same way.

**Table, from the rule above (11-03 03:05 IST).** `v1472_b1px@b1p` against `base1503_b1p@b1p`: 21 wins against 13 of 60, margin +186 +- 84. Kept: 00interlock, 00fragment, adgato_gemcombat1, 02crossing, 00corners, 00anvil, 00dunes (z at least 2, none behind). Not added: every map under z 2 (none ahead by 2 games). `exp/rt2` is `exp/rt1` with this table; the program is otherwise the same, and one game each on 00anvil and 00swirl ran without a fault.

**Platform test of `exp/rt2`.** Panel `r7p` (`tools/platform/mappanel.py b1p r7p ...`: the 12 teams of `b1p`, pinned to their bots of that run, five of the seven maps a group, 60 games). Base `base1503_r7p`, new `rt2_r7p`. Bar: wins on those maps up by 1 standard error or more in pairs and margin up by 1 standard error or more; no fault. Wins are the target here because the table is a choice of bot per map, and the only factor is the result on those maps.

**Second table panel `b2p` (written 11-03 03:18 IST, before any result).** `v1472` against `v1512` on 15 more maps, 4 games each, the 12 teams of `b1p`: 00reverse_spiral, 00lost_world, 00breadcrumbs, 02guardians, 01elk_arena, 00vault, 01shortcut, 00quarry, 00ribs, 00gem_fields, 00swirl, 00eight, 01yellow_brick_road, 02fields, 01starfish. These have z from -0.3 to 1.3 in `mapstrat.py`, so the rule for maps under z 2 applies: a map joins only when `v1472` is ahead by at least 2 of its 4 games and its margin a game is up by more than 300. It then needs its own pinned check before it stays.

**`exp/rt3`, the router with the no-log default arm (written 11-03 04:50 IST, while its screen runs and before reading any of it).** `rt3` is `rt2` with `BOT_LOGC 0` in the v1503 namespace, so the default arm is `exp/vnl1`, which passed its own screen (exhausted turns 9.78 to 6.79 a game). Local bars, screen `data/runs/multi-043908` against `pool.v1503`, 680 pairs: the four router bars above (routing, no fault, fuel, win rate on routed maps at least the Bamboo bot's local rate minus 1 se), plus exhausted turns down by at least 2 a game on default maps and the vnl1 guards there: gold r300 not down by more than 1 se, deaths r300 not up by more than 1 se.

**`rt2` on `r7p` (11-03 04:55 IST).** `rcmp.py base1503_r7p@r7p rt2_r7p@r7p`: 15 wins against 8 of 60, flips 9 against 2, margin +152 +- 63 a game. Wins up by 2.1 standard errors in pairs and margin by 2.4: the bar is passed. The table holds.

**`rt3` local result (11-03 04:55 IST).** `data/runs/multi-043908`: no fault in 680 games. Routed maps 47 of 56, the Bamboo bot's own rate there 49 of 56 and v1503's 44 of 56. Default maps 517 of 624 against 509. Exhausted turns a game on default maps 10.19 to 7.73 (bar: at least 2 down); on routed maps 5.21 to 27.36, because the Bamboo arm uses more fuel (the Bamboo bot alone has 27.8 there and 100 on the default maps). Gold r300 +30.1 +- 11.5, deaths -0.35 +- 0.17, collected +18.8 +- 7.6. All bars pass. `rt3` went live as version 1522 at 04:54 IST, replacing 1519 (the pack opening, which has no gain on the platform).

**`rt3` on the platform, panel `t03p` (written 11-03 04:55 IST, before any game).** Versus the mean of the other variants on this panel, because the base run `t1503_tm@t03` is lucky by about 6 wins (37 wins, margin -398; the variants' mean is 30.7 wins, margin -455). Target: exhausted turns per game on default maps down by at least 2, from the decoded games, and margin over the variants' mean by at least 1 standard error. Guards: no fault; wins not below the variants' mean by more than 1 standard error. Wins are recorded, not judged. `rt3` stays live unless a guard fails, since the table's gain is already measured on `r7p`.
