# e_c3 against the team's live bot 1472 on b38p: decision rule

Written Sun, Nov  1, 2026  3:40:41 PM (IST), before any game of e_c3 (local or platform) and before the base run
`l1472_b38p@b38p`.

e_c3 = bb458c (1472 with bamboo8's three exact fuel caches) plus the three economy changes that passed locally on
their own (rows e_elk, e_tw, e_lk): `kElkBonus` 1.5 -> 1.0, `kTravelWeight` 1.15 -> 1.4, `kLookahead` 0 -> 0.5
(`bots/exp/e_c3/src/bot.cpp`).

Factor: gems collected. Against teams above us 1472 collected 473 / 763 / 795 a game to r1000 three / four / five a
side against their 701 / 889 / 859, with 33 captures a game against their 50 (95 decoded ranked games,
`data/fights/rk1472_above`).

## Local screen (before any platform game)

420 games against pool/cand1, exp/b10n and bamboo8, paired with bb458c's games (`multi-071805`) by
`tools/local/econpair.py`. e_c3 goes to the platform only if: no bot fault; collected up by more than two standard
errors; captures up; deaths up by at most 0.3 a game; wins not down by more than one standard error.

## Platform (panel b38p, 90 games against ranks 21-45)

Runs: `l1472_b38p@b38p` = 1472 as selected now (no upload); `e_c3_b38p@b38p` = e_c3 uploaded and selected, and the
version live before the gate selected again after it (`gateq_live.sh`, GATE_RESTORE=auto). Metrics paired on
(opponent, map, side) from decoded games (`decode_run.sh`, `paired.py ... 1000`).

e_c3 becomes the team's live bot only if all of these hold:
1. collected to r1000 up by more than two standard errors (target);
2. deaths to r1000 up by at most 0.3 a game;
3. tributed to r1000 not down by more than one standard error;
4. flips do not favour 1472: L->W at least W->L.

Otherwise 1472 stays live. A run during which the active version changed (someone else uploaded or selected;
`data/gate_live.log` WARNING) is void.
