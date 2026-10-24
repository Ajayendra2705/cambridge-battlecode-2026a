# Status (updated 2026-10-25 03:15 IST)

## Now

- **Ladder bot (Sprint 2 entry):** `cp3` (= `bots/main`, submitted as version 689 at 03:09 IST on 10-25, before the 04:29 IST lock). It is dr3 plus the layers listed in `docs/ARCHITECTURE.md` ("Changes in cp3"). On the same 90 games tonight (b5 + b6) it won 39 against dr3g's 36 (dr3 + the altar-guard fixes): b6 20 vs 15, b5 19 vs 21, better score margin in 49 games and worse in 39 (p = 0.29). Decoded, its champion damage per game is at the rivals' level (13.4k vs 13.8k; dr3 11.1k vs 15.3k). Full local check: 406/560 (dr3 391), no bot faults. Previous: `dr3` (`bots/pool/dr3`), `fx1`, `fe1`, `hb4`. Rank 77 at 23:25.
- **Deadline:** Sprint 2 locks Sat 24 Oct 23:59 BST. The bot submitted at that moment is the tournament bot. Sprint 3 locks Sat 31 Oct 23:59 GMT. Season ends 18 Nov.
- **Event:** cambc2026a, https://2026a.battlecode.co.uk, account Ajay_2705 (team id `118dbffc-87ec-48a6-ac9c-dc1e371ba364`).
- **Method (batch loop):** panel = the 5 ladder teams at ranks R-15 to R-11, 5 fixed maps each (`data/specs_bN.txt`), base = main on it, improve until 17/25, then confirm on a second map set (`data/specs_bNx.txt`) against the same teams before adopting.
- **Upload limit:** 20 submissions per hour. See `docs/WORKFLOW.md`.

## Mistakes so far (review 2026-10-24 23:30 IST)

- Judged variants on 50-game win counts. Near-identical bots differ by about 3 wins from chaos alone; most rejections of the evening were inside that noise. Use decoded continuous metrics (hits, deaths, gems collected/tributed/lost) and the always-lost games.
- Winner's curse: dr3 was picked as best of about 40 variants on b3/b4, so its 28/50 there is inflated, and every later candidate was compared against it on the same games. Compare on a fresh panel (b6).
- Spent about an hour on dash routing over holes (gd1) without first checking team-level effects (champions without a dash split off). Check the whole flow before building.
- Deleted variant folders before their platform verdict and rebuilt them later; keep a candidate until its gate is read.
- Hunted symptoms map by map before measuring where the gap was overall; the biggest gap (we land 40% fewer hits in fights) was found late.
- 01:15 on 10-25: `ps | grep` in Git Bash shows only `/usr/bin/bash`, not the command line, so a kill of the gate chain matched nothing and two chains ran gates at once (sp1_b5 and sp2_b5 overlapped). Find processes through `/proc/PID/cmdline` before killing, and check that only one gate chain is alive.
- Edited bot code through shell and Python string escapes and broke builds three times ('
' became a real newline).

## Improvement plan (written 2026-10-25 02:20 IST, for the next session)

In order of expected value, each with its measured gap (details in `docs/findings.md`):

1. Ranged champions shoot when an enemy is in range instead of stepping (Vesper hits in 41% of in-range rounds, rivals 53%). Check the attack-on-sight health gate and the plan's move before the attack.
2. Vendetta dashes in on an enemy 2-3 tiles away when the fight is not lost (16% vs 26% hit rounds at that distance).
3. Capture priority: fix the dead rule (`mine = 16 * 16`) and give captures to the passives that pay (cp1: Vesper +33% gold, Marcella +2 gold per tributed gem; local gold +5%, tributed r600 304).
4. Items: the formula (sp1/sp3) moved Power emblems from 0.07 to 0.45 per champion, but rival Vespers hold 3.0; damage counted twice (sp4) dies too much locally. Needs the gold from 3 first.
5. Banking: we carry about 30 more gems and lose about 30 more on death by r1000 than the rivals; ef3's trip-overhead factor 3 is a fit to one panel.
6. Maps: boss_battle (kill the guard first or hold the altar), hooks (centre 4v4), hole maps (dash routing failed as gd1; needs team-level planning).

## Batch b6 (2026-10-24 23:25 IST, rank 77)

Panel ranks 60, 62-65 (61 KKB and 66 The Mania have no eligible bot): 剑桥夜爬者, AlphaSlop, Stubborn Gold Clusters, HouseOfCoders, The Party of Heroes; two 5-map windows each covering all 40 maps (`data/specs_b6.txt`, seed 6060). First run: dr3 vs pool/fh2.

Result (closed 03:09 on 10-25): wins on the same games, tonight's runs only:

| bot | b6 (40) | b5 (50) | total |
|---|---|---|---|
| dr3g (dr3 + guard fixes, fresh base) | 15 | 21 | 36 |
| cf1 (dr3 + fight layers + guard) | 18 | 19 | 37 |
| **cp3** (adopted) | **20** | 19 | **39** |
| sp3 / sp1 / ef3 | 18 / 17 / 17 | - / - / 18 | - |
| fh2 | 13 | 20 | 33 |

dr3's evening b5 run (23) no longer reproduces: only 19 of 50 scores match the re-run, so b5 opponents changed bots in between. b6 matched in 29 of 40.

## Single factor: gem collection (team decision, 2026-10-24 18:50 IST)

Work only on gems collected until we match the rivals; no other factor until then.
- Metric: gems collected by round 300 per game, from decoded replays (`tools/replay/rounds_extract.mjs`, which now stores camp types in the meta line). Fresh panel b5 (ranks 72-77): dr3 108, rivals 133. In b5 losses we take 6 gems from gem clusters vs their 30, elk 33 vs 61, wolf 28 vs 43.
- Cause found: before the first emblem a gold cluster scores 40 (gold x2) and a gem cluster 7, so we skip gem clusters. gm1 (no x2) raised the metric to 123 but won 21/50 vs 23.
- We hit elks more often than rivals (124 vs 105 hits per game before r300) but collect fewer elk gems: elk bouts are abandoned or lost.

- Gem targets (rival winners, 94 decoded rival-vs-rival ranked games, by r600): collected 360, tributed 279, lost on death 17, bag 64. ge4: 319 / 200 / 42 / 77.
- Next phase (team request, after about 3-4 hours on gems): replace hand-tuned constants with functions of the variables they depend on (for example a death hazard from visible enemies, distance and health instead of fixed multipliers; gold value as the marginal win value of the next item). One constant family at a time, each derived, then tested.

- Result of the gem phase (18:50-22:15): collection matched (ge4: 140 vs 127 by r300 on b5). Tribute conversion not matched (200 vs 273 by r600); the gap is gems lost when carriers die (42 vs 15). Eight banking and carrier-safety variants gave no platform gain. Kept as candidate layers: `bots/exp/ge4` (gold not doubled before the first emblem, no mid-push bonus) and `bots/exp/ab1` (ge4 + bank when the enemy tributes past an unseen altar guard).
- Measurement limit: a 50-game panel has about 2.2 wins of noise per run (26 of 50 b5 games swing between near-identical bots; findings). Judge changes on the always-lost games or on many more games, not on 50-game win counts.
- Fight phase (22:15-23:20): we lose fights we start (0.36-0.55 own deaths vs 0.31-0.38 kills per start; rivals 0.2 vs 0.5-0.64) because we hit less (124 vs 208 champion hits per game by r800; adjacent enemy: we hit 58% of rounds, rivals 82%). fh1 (free hit before kiting) and fh2 (melee hits before fleeing) raise hits and cut deaths on b5 and b34, and fh2 is best locally (194/240), but platform wins equal ge4 (25/50 on b34 vs dr3's selection-inflated 28). Candidate kept as `bots/pool/fh2`.
- Next: build on `bots/pool/fh2`: the remaining hit gap (ranged champions, idle rounds near enemies), eight-style 5-stacks (rg1's early-threat rule rarely fired), then a larger platform sample before adopting. Old next item: deaths in champion fights (3.1 vs 2.0 per game by r600; contest: 35-43 deaths per game in fights, 0 gems); always-lost maps one at a time (findings, platform noise section).

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
