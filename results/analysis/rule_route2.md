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
