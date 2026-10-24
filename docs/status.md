# Status (updated 2026-10-24 17:00 IST)

## Now

- **Ladder bot:** `dr3` (= `bots/main`, submitted as version 619 at 16:56 IST on 10-24). Previous: `fx1` (`bots/pool/fx1`), `fe1` (`bots/pool/fe1`), `hb4` (`bots/pool/hb4`). Rank 94 at 16:25 (it fell from 76 while test bots played ranked games during gates).
- **Deadline:** Sprint 2 locks Sat 24 Oct 23:59 BST. The bot submitted at that moment is the tournament bot. Sprint 3 locks Sat 31 Oct 23:59 GMT. Season ends 18 Nov.
- **Event:** cambc2026a, https://2026a.battlecode.co.uk, account Ajay_2705 (team id `118dbffc-87ec-48a6-ac9c-dc1e371ba364`).
- **Method (batch loop):** panel = the 5 ladder teams at ranks R-15 to R-11, 5 fixed maps each (`data/specs_bN.txt`), base = main on it, improve until 17/25, then confirm on a second map set (`data/specs_bNx.txt`) against the same teams before adopting.
- **Upload limit:** 20 submissions per hour. See `docs/WORKFLOW.md`.

## Batch b4 (2026-10-24 16:25 IST): check run

- Panel ranks 79-83 (`data/specs_b4.txt`): fx1 13/25, c5 12, dr3 14. Over b3 + b3x + b4 (75 games) dr3 41, c5 39, fx1 36: dr3 beats fx1 on every set, so it was adopted below the 17/25 bar at the user's call.
- Next session: start a fresh batch from the rank after a quiet ladder period (no gates), so the rating reflects dr3.

## Batch b3 (2026-10-24 09:20 IST -): closed

- Rank 77 at the start. Panel ranks 62-66: The Mania, cronjohn, Zkey Farming, DOOMSDAY, will think later (`data/specs_b3.txt`, `data/specs_b3x.txt`).
- Base fx1: b3 12/25, b3x 11/25. Gap: early deaths (3.5 per lost game before r300, fleeing near our spawn) and enemy rushes (swirl: all four of ours dead by r90).
- Best so far c5 (nm5 + lowest-health prey + contested groups cost more after recent deaths + ability-slot cache): b3 13, b3x 14 (27/50 vs 23). Far from 17; not adopted. About 20 variants tested (`docs/experiments.md`, batch b3). Deadline extended to 17:00 IST; the platform group quota (50 per window) now limits gates to about 5 combined gates per hour, so variants are screened on b3 alone first.
- Later (13:35-15:20): about 20 more variants (cohesion, help calls, travel weights, draft, endgame, fuel, tribute safety). Best on b3 is `dr3` (c5 drafting Varg instead of Ryth): b3 14, b3x 13, 27/50, the same total as c5. Source of c5 and dr3 is kept in `bots/exp/` for the next session. Main stays `fx1`.
- Next session: continue batch b3 from c5/dr3. Remaining gap: early and mid-game deaths while fleeing from 2-4 enemies (79% of deaths in losses); 'will think later' (rank 66) beats us 8 of 10.

## Batch b2 (2026-10-24 06:55-09:20 IST): done

- Rank 98 at the start (82 by 08:30 with fe1). Panel ranks 83-87: Brakence Fan Club, Agentic Loop Builders, Sic Mundus Creatus Est, test4, HouseOfCoders (`data/specs_b2.txt`, `data/specs_b2x.txt`).
- Base fe1: b2 11/25, b2x 15/25. Accepted `fx1`: b2 19/25 (8 up, 0 down), b2x 15/25. Gap: early deaths in the contested middle on small-team maps.
- Fight-behaviour variants (lh2, fp1, ch1, fp3, sh1, bg1) and teleports moved b2 by +1 to -6 and did not hold on b2x. Details: `docs/experiments.md`, batch b2.
- Next: batch b3 (open, see above).

## Batch b1 (2026-10-24 03:00-06:55 IST): done

- Rank 96 at the start. Panel ranks 81-85: Ninja Turtles, DOOMSDAY, Sic Mundus Creatus Est, error404, Shawn (`data/specs_b1.txt`, second set `data/specs_b1x.txt`).
- Base hb4: 15/25, then 12/25 after Shawn changed bot (rerun hb4_b1b). b1x: 9/25.
- Accepted `fe1`: b1 17/25 (6 up, 1 down), b1x 13/25 (6 up, 2 down), local 414/560 (hb4 384). Its parts and every rejected variant: `docs/experiments.md`, batch b1. Facts found: `docs/findings.md`, batch b1.
- Still lost by every variant: starvation (enemy owns the centre gem cluster), road_of_riches (enemy camps the mid-map altars), interlock, rows, gem_fields. Rivals tribute 2-3x as often (median bag 22 vs our 29) and hunt in packs (Shawn).
- Next: batch b2 (done, see above).

## Rank 30 AlphaSlop push (2026-10-23 evening to 10-24 01:30): result

- Ladder bot is still hb4 (`main`, submitted as version 410 at 01:28 on 10-24).
- Panel `r30` (AlphaSlop, all 40 maps, `data/specs_r30.txt`): hb4 11/40, exactly repeatable. Best variant pk4 13/40, but on panel `r70` (ranks 70-80, 55 games, `data/specs_r70.txt`) pk4 22 vs hb4 24: the gain is specific to AlphaSlop, so it was not adopted. fn1 also lost on r70 (22 vs 24).
- About 20 ideas tested (`docs/experiments.md`, rows from pv1 to md1). None gave a reliable gain; most moved 1-3 games either way.
- What the teams that beat AlphaSlop do (`docs/findings.md`): they take the middle before round 600 (first mid capture at round 86-105, ours 351) and bank within 15 rounds. Pushing us into the middle (md1) lost, because we lose the fights there: fight strength and gold (we earn 60-85% of AlphaSlop's) come first.
- Next: the gold gap (team earned gold), not the middle or banking. Use panel r70 with hb4_70@r70 as the paired base (24/55) to check any change against more than one opponent.

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

## Main loss shape (gb2l and hb4l logs)

Blowouts are decided before round 600: deaths before round 300 are 2.7 vs 0.9, camps cleared 19.6 vs 35.1, tributes 2.5 vs 15. Fatal engagements start even and end outnumbered while fleeing.
