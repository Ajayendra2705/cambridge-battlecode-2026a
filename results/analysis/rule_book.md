# Opening book by map (written 11-03 06:41 IST, before the screen)

`tools/replay/openbook.py` reads 75 maps with at least 6 rival games: which groups the rivals' team hits by r60, against ours (`data/openbook_r60.txt`, games against ranks 1-20 and ranked games of the v1503 line). The first targets differ a lot on many maps, for example 00interlock wolf at 5,8: rivals 0.85 of games, us 0.06; 00ambush elk group at 31,44: 0.67 against 0, elk group at 22,43: 0 against 0.75; 00eight elk at 12,4: 1.00 against 0, elk at 12,26: 0.33 against 1.00. Wolves first on every map lowered gold (`rule_wolf.md`), so the kind is not the point; the group is. The difference could be the walk, the safety from first contact or the follow-up route.

`exp/vbk1` and `exp/vbk2` (`mk_vbk.py`, on `exp/vnl1`): before round R a group's value is multiplied by `(f_them + 0.15) / (f_us + 0.15)`, clamped, with rows under a factor 1.25 left out.

- `exp/vbk1`: R 80, clamp 0.5 to 2.5.
- `exp/vbk2`: R 120, clamp 0.35 to 4.

Local bar (base `exp.vnl1`, `multi-031107`, 680 paired): team gold r150 or r300 up by 1 standard error or more, deaths r300 not up by more than 1 standard error. Guards: wins not down by more than 0.03, collected not down by more than 2 standard errors, deaths a game not up by more than 0.3, no fault. The local pool does not play like the top teams, so a per-map reading comes next: where the book gains locally and where it does not.

Platform only after a pass: `t03p` parts pinned to `t1503_tm@t03`. Target: decoded team gold r100 and r300 up by 1 standard error or more. Guards: margin and collected not down by more than 1 standard error. Wins recorded, not judged.
