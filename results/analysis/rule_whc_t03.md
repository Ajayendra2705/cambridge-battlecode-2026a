# Rule for whc on the platform (written 11-02 19:55 IST, before any game of the variant)

The user chose (11-02 19:50 IST) that we take the team's platform slot for this test and tell the teammate to pause.

- **Base:** `t1503_tm@t03`, the teammate's own games of 1503 (v606) against the 12 teams of their ranks 1-20 panel,
  13:31-14:03 UTC: 34 groups, 170 games (32 three a side, 39 four, 99 five), 37 won. Logged in `results/gate.log`
  from `data/teamvers.json` (`teamvers.py`); groups with other teams (challenges) left out.
- **Variant:** `exp/h1503` = the 1503 source with whc's thresholds (`P_HOLD_C` -0.6 to -0.3, `P_AVOID` -0.85 to
  -0.5), on `t03p` (`pin.py`: every opponent plays the bot of its base group). The two bots differ only in the two
  constants, so a game differs from its base only through them.
- **Gate only if** h1503 passes its local bar (`rule_1498.md`, "Fight thresholds on the dash-bridge line").
- **Factor and target:** our deaths a game to r1000 (`tools/replay/paired.py t1503_tm@t03 h1503_t03p@t03p`): down
  by 1 standard error or more and by at least 0.5 a game.
- **Guards:** our gems collected and tributed to r1000 not down by more than 2 standard errors each; no bot fault.
- **Recorded, not judged:** wins and flips (`rcmp.py`), the rivals' deaths, deaths by team size (`pairsize.py`),
  outnumbered deaths (`packs.py`).
- **If it passes:** h1503 stays live and the change goes to the teammate as "v548 + `P_HOLD_C` -0.3, `P_AVOID` -0.5".
  If it fails: 1503 is selected again (`GATE_RESTORE=auto`) and the result goes to the teammate.
