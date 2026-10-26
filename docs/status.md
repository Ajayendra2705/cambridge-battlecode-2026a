# Status (updated 2026-10-23)

## Now

- **Ladder bot:** `hb4` (= `bots/main`). Rank about 70 (1814) after many test submissions.
- **Deadline:** Sprint 2 locks Sat 24 Oct 23:59 BST. The bot submitted at that moment is the tournament bot. Sprint 3 locks Sat 31 Oct 23:59 GMT. Season ends 18 Nov.
- **Event:** cambc2026a, https://2026a.battlecode.co.uk, account Ajay_2705 (team id `118dbffc-87ec-48a6-ac9c-dc1e371ba364`).
- **Yardstick:** panel 8 (ladder ranks 60-69). hb4 wins 36-41 of 100 full-panel games and 10 of 20 small-gate games.

## Fix list (in order)

1. Help teammates: done (hb4).
2. Bank smaller batches: caps 25/30/40 lost locally and on the platform (bk1-bk3). Parked.
3. Vendetta/Vesper damage: same cause as 1 (we die and flee more).
4. **Next: maps we lose every game** (elk_arena, boss_battle, lanes, contest, starfish, quadrants). See `docs/findings.md`, "Maps".

## Open, not yet tested on the platform

- `lkh`: hb4 + altar locks (`tools/variant/mklock.py`). Rivals buy 4-6 per game, we buy none. Locks were only rejected locally, where local bots rarely tribute. Target metric: enemy tributed gems per game.
- `lc1`: flee at enemy power > 0.7x ours (more caution). Local 385.
- `fl3`: also losing when hit for > 40% hp last round. Its small-gate groups were created and may hold results: `python -I tools/platform/rcmp.py hb4l@p8s fl3l@p8s`.
- Elk_arena: regroup and do not contest the centre early.
- Boss_battle: team monolith assault plus an altar lock after the kill.
- Lineage round robin (`docs/lineage.md`).
- `fpr`: farm prediction model in target choice (Michael, `ml/`). `pick_group`'s best live-camp groups are weighted by a learned P(our team captures the group). Local only so far: style bench 94/140 vs main 76; 560-game run 391 vs 384 with deaths -24%, captures +13%, margin +21%; held-out opponents 163/240 vs 154. Build on any base with `python -I ml/bot/make_fpr_variant.py BASE exp/NAME` (works on main; on another bot it stops if a patch point differs). Target metric: captures per game and deaths per game. Details: `ml/README.md`, `results/analysis/diagnosis_2026-10-27.md`.

## Main loss shape (gb2l and hb4l logs)

Blowouts are decided before round 600: deaths before round 300 are 2.7 vs 0.9, camps cleared 19.6 vs 35.1, tributes 2.5 vs 15. Fatal engagements start even and end outnumbered while fleeing.
