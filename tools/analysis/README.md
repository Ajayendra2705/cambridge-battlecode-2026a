# Platform game analysis scripts

Run from the project root. RUN names come from `tools/gate.log` (e.g. `hb4@p7@20`); downloaded
replays land in `rk_replays/<RUN with @ replaced by _>/` and summaries in `ladder_replays/`.

| Script | Use |
|---|---|
| `gdl.py RUN` | download every match of a gate run: `rk_replays/<run>/index.txt` (match map side result) + replays |
| `cgold.py DIR...` | gold, gold by r500, spent, gems collected, deaths per champion, us vs them |
| `cdmg.py DIR...` | champion damage and K/D per champion, us vs them |
| `build.py "Champ,Champ" DIR...` | item purchases per champion, us vs them (bulk buys: count by gold/30) |
| `fight.py DIR...` | team metrics per game, fights (clustered deaths), who dies first |
| `tline2.py DIR` | by outcome (win/close/blowout): collected, clears, gem losses, tributes before r600 |
| `early2.py DIR` | early deaths (<= r300): activity, distance from our spawn |
| `vana.py DIR` | needs V combat-log lines: stats us vs them by 500 rounds, 1v1 damage per turn, actions |
| `dpre2.py DIR` | needs V lines: anatomy of each fatal engagement (start/end allies vs enemies, first flee) |
| `dact.py DIR...` | death activity per champion (from D lines) |
| `acts.py DIR` | rounds per activity per champion (from A lines) |
| `ehp.py DIR...` | enemy health and count at our deaths |
| `grp.py DIR...` | kill participation and grouping |
| `lgold.py MULTIDIR` | per-champion gold/damage for a local `tools/multi.py --keep` run |

V lines exist only for combat-logging bots (bots/lg1, bots/gb2l: the "Combat log" block in play_turn).
