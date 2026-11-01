# cmb7 against the team's live bot 1478 on b38p: decision rule

Written Sun, Nov  1, 2026  2:32:31 PM (IST), before any game of the panel.

Panel b38 (90 games, 18 groups): nine teams rated above us at 13:35 IST (we were 48, 2050.6), ranks 21-45 (2068-2189):
procless, BattleCats, SkuBap, JukeFall, Jupiter, Olympus, The Party of Heroes, SilverSamurai, QS2isLaw
(`results/panels/specs_b38.txt`, `mkpanel.py 3801`; 56 five-a-side, 21 four-a-side, 13 three-a-side games).

Runs: `l1478_b38@b38` = the team's live bot 1478 ("Bamboo v1472 + bot_10 on far maps", uploaded by Bamboo 13:59 IST)
without an upload; `b38p` = b38 pinned to it (`pin.py`), so it is the exact base of every later run; then
`cmb7_b38p@b38p` = cmb7 (`bots/pool/cmb7`: vx1 three a side, 1472 four a side, bot_10 five a side), uploaded and
selected, and 1478 selected again after the games (`tools/platform/gateq_live.sh`, GATE_RESTORE=1478).

Factor: gems collected. Against teams above us 1472 collected 473 / 763 / 795 a game to r1000 three / four / five a
side against their 701 / 889 / 859 (95 decoded ranked games, `data/fights/rk1472_above`).

Metrics, paired on (opponent, map, side) from decoded games (`decode_run.sh`, `paired.py`): collected to r1000 (target),
tributed to r1000, deaths to r1000; wins and flips recorded.

cmb7 becomes the team's live bot only if all of these hold (the user: only when sure it is better):
1. collected to r1000 up by more than two standard errors;
2. flips favour cmb7: L->W more than W->L, sign test p < 0.10;
3. deaths up by at most 0.3 a game;
4. tributed to r1000 not down by more than one standard error.
Otherwise 1478 stays live (it is selected again after the gate in any case). A run during which the active version
changed (someone else uploaded or selected; `data/gate_live.log` WARNING) is void.
