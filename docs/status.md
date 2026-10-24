# Status (updated 2026-10-25 04:00 IST)

## Now

- **Ladder bot and Sprint 2 entry:** `cp3` (= `bots/main`), submitted as version 691 at 03:30 IST on 10-25, before the lock (Sat 24 Oct 23:59 BST = 04:29 IST). What it changes over `dr3`: `docs/ARCHITECTURE.md`, "Changes in cp3". Previous ladder bot: `dr3` (`bots/pool/dr3`).
- **How good it is:** over 140 platform games run on the night of 10-24/25 (panels b5, b6, b34) cp3 won 59 and `dr3g` (dr3 + the altar-guard fixes) 60: a tie in wins. cp3 had the better score margin in 73 games and the worse in 63. It is better against the higher-ranked b6 teams (20 vs 15 of 40) and worse against b34 (20 vs 24 of 50) and b5 (19 vs 21 of 50). Decoded, its fights are level with the rivals' (champion damage 13.4k vs 13.8k per game by round 800; dr3 had 11.1k vs 15.3k). Full local run: 406/560 (dr3 391), no bot faults.
- **Next deadline:** Sprint 3 locks Sat 31 Oct 23:59 GMT (Sun 1 Nov 05:29 IST). The bot submitted at that moment is the tournament bot. Season ends 18 Nov.
- **Event:** cambc2026a, https://2026a.battlecode.co.uk, account Ajay_2705 (team id `118dbffc-87ec-48a6-ac9c-dc1e371ba364`). Rank 77 at 23:25 on 10-24 (rating moves while test bots play ranked games during gates).
- **Branch:** the work of 10-24/25 is on `batch-loop-2026-10-24` (not merged into `master`).

## Next steps (in order of expected value)

Each step names the measured gap, where to change the code and how to judge it. Measure with
`bash tools/replay/decode_run.sh RUN@PANEL` then `python -I tools/replay/decoded.py CMD data/fights/RUN_PANEL` (numbers
below are cp3 on b56, 70 decoded games, per game, us vs the rivals; full tables in `docs/findings.md`).

1. **Heart of Ruin is built too thin.** At r600 it has 1184 max health vs the rivals' 1700 and dies 1.79 times per game by r1000 vs 1.27 (champion damage 3032 vs 3739). cp3's item formula (`shop.h`) gives it Power-focus because focus growth 12 looks big against its focus, but Heart of Ruin trades blows in melee; the rivals build it Bruiser-focus, Treasure-focus and Jungle. Make the formula count health for melee front-liners (or use Bruiser for them, as before sp1). Judge by `decoded.py types` (deaths, damage) and `items`.
2. **Vendetta still does little.** Champion damage 2972 vs 4317 per game, gems 91 vs 168, hit-round share 0.029 vs 0.041, hit rate at 2-3 tiles 0.16 vs 0.23. Her kills reset all cooldowns: chain dash and attack reset after a kill. Code: `bot.cpp` attack on sight (cp3 dash-in) and the pvp step. Judge by `decoded.py types`.
3. **Big tributes still break.** cp3 starts 1.2 channels per game with a bag over 100 gems and only 61% complete: 406 gems started, 118 banked per game (rivals 0.6 such channels). A tribute stands for bag / 10 turns. Find where the big bags come from (monolith or golem captures, the 150-gem and deadline paths in `bot.cpp` bank) and bank before them or at a safe altar. Judge by `decoded.py channels`.
4. **Carriers still lose bags.** By r1000 we lose 68 gems on death (rivals 31) and carry 117 at any time (87). Order-quantity banking (`bot.cpp`, "Order quantity") uses a fitted trip overhead x3 from one panel; fit it on b56 instead, and check the hazard term `h` against `decoded.py risk`.
5. **Centre groups on b5/b34 maps.** cp3 lost elk_arena (576-648; dr3 won 1008-108), contest and corridors that dr3 won. ge4 removed the mid-push x2 (`targets.h`); test restoring it inside cp3 as one variant, on b56 + b34.
6. **Maps every version loses:** boss_battle (whoever kills the guard monolith beside the altar first owns the only altar; HouseOfCoders did it by r550-700), hooks (4v4 centre fight, 0-1012), road_of_riches and gemfight (rivals cross hole lines with dashes; our routing cannot, and gd1's dash routing failed locally because champions without a dash split off), shortcut (we collect 398 vs 1161 by r1000), contest and eight (5-stacks).
7. **Draft:** we field Varg where the rivals field Ryth or Marcella; Varg deals the least champion damage of ours (2411 per game) and dies 1.74 times. Only the platform can judge a draft change.

Method for every step: one change at a time on `main`, local quick pool as a breakage filter (floor about 165/240), then one combined gate on `b56` (90 games, `tools/platform/gatechain.sh`) with a fresh base run of main in the same session, compared with `rcmp.py` and the decoded metric. 50-game win counts move by about 3 wins from chaos alone (`docs/findings.md`, "Platform noise"), so a change needs its metric to move, not only its wins.

## Mistakes to avoid (from 10-24/25)

- Judging variants on 50-game win counts: near-identical bots differ by about 3 wins from chaos alone. Use decoded continuous metrics and the always-lost games.
- Winner's curse: dr3 was picked as the best of about 40 variants on b3/b4, so its 28/50 there was inflated, and later candidates were judged against it on the same games. Compare on a fresh panel, with a fresh base run.
- Comparing with old base runs: opponents change bots (dr3's evening b5 score of 23 reproduced only 19 of 50 game scores 9 hours later and became 21).
- Building before checking the whole flow: an hour went into dash routing over holes (gd1) before checking what happens to champions without a dash.
- Deleting variant folders before their platform verdict, then rebuilding them.
- Hunting map by map before measuring where the gap is overall: the biggest gap (rival champions land 40% more hits) was found late.
- Process control in Git Bash: `ps | grep` shows only `/usr/bin/bash`, so a kill matched nothing and two gate chains ran at once (their results are void). Use `bash tools/platform/procs.sh` (it reads `/proc/PID/cmdline`).
- `rm -rf data/runs/multi-*` while a local run was writing there: it lost most of that run.
- Editing bot code through shell and Python string escapes: `'\n'` became a real newline and broke three builds. Edit files directly, then build.

## History

### Night of 10-24/25: gems, fights, final pick (batches b5, b6)

- **Gem phase (18:50-22:15, team decision: only gem collection until matched).** On b5 dr3 collected 108 gems by r300 vs the rivals' 133. Cause: before the first emblem gold counted double, so a gold cluster scored 40 against a gem cluster's 7. ge4 (no x2, no mid-push) collected 140 vs 127 by r300 and 319 vs 320 by r600; tributes stayed behind (200 vs 256 by r600) because carriers died with bags. Eight banking and carrier-safety variants gave no platform gain.
- **Fight phase (22:15-23:20).** We lost fights we started (0.36-0.55 own deaths vs 0.31-0.38 kills per start; rivals 0.2 vs 0.5-0.64) because we hit less. fh1 (free hit before kiting) and fh2 (melee hits before fleeing) raised hits and cut deaths on b5, b34 and b6.
- **Batch b6 (fresh panel at rank 77) and the final comparison (23:25-03:30).** The banking formula was missing a factor (ef1, ef3), items were bought from a fixed health-heavy list (sp1, sp3), a capture rule never ran (cp1), Vesper held fire when hurt (cp2), and Vendetta did not dash in (cp3). Tonight's runs on the same games:

| bot | b6 (40) | b5 (50) | b34 (50) | total |
|---|---|---|---|---|
| dr3g (dr3 + guard fixes) | 15 | 21 | 24 | 60 / 140 |
| **cp3** (adopted) | **20** | 19 | 20 | 59 / 140 |
| cf1 (dr3 + fight layers + guard) | 18 | 19 | - | 37 / 90 |
| sp3 / sp1 / ef3 | 18 / 17 / 17 | - / - / 18 | - / - / 25 | - |
| fh2 | 13 | 20 | 25 | 58 / 140 |

  dr3's b5 score from 18:14 (23) did not reproduce later: b5 opponents changed bots in between. b6 matched in 29 of 40 games.

### Batch b4 (10-24 16:25, ranks 79-83)

fx1 13/25, c5 12, dr3 14. Over b3 + b3x + b4 (75 games) dr3 41, c5 39, fx1 36: dr3 beat fx1 on every set and was adopted below the 17/25 bar at the user's call.

### Batch b3 (10-24 09:20-16:25, ranks 62-66)

Base fx1: b3 12/25, b3x 11/25. Gap: early deaths while fleeing near our spawn, enemy rushes (swirl: all four of ours dead by r90). About 40 variants; best c5 (27/50) and dr3 (c5 + Varg instead of Ryth, 27/50). 'will think later' (rank 66) beat us 8 of 10.

### Batch b2 (10-24 06:55-09:20, ranks 83-87)

Base fe1: b2 11/25, b2x 15/25. Accepted `fx1`: b2 19/25, b2x 15/25. Fight-behaviour variants and teleports did not hold on b2x.

### Batch b1 (10-24 03:00-06:55, ranks 81-85)

Base hb4: 15/25 (12/25 after Shawn changed bot). Accepted `fe1`: b1 17/25, b1x 13/25, local 414/560. Still lost by every variant: starvation, road_of_riches, interlock, rows, gem_fields.

### Rank 30 AlphaSlop push (10-23 evening)

hb4 11/40 against AlphaSlop on all 40 maps, exactly repeatable. Best variant pk4 13/40 but 22 vs 24 on ranks 70-80, so not adopted. Teams that beat AlphaSlop take the middle before round 600 and bank within 15 rounds; pushing us into the middle (md1) lost, because we lost the fights there.

## Parked ideas (not settled on the platform)

- `lc1`: flee at enemy power > 0.7x ours (more caution). Local 385, never gated.
- `fl3`: also count as losing when hit for > 40% health last round. Its small-gate groups may still hold results (`rcmp.py hb4l@p8s fl3l@p8s`).
- Altar locks: rivals buy 4-6 per game. Our tries (lk1-lk3, lke, lkh, pl1) gave no gain; lk3 (lock only to cancel an enemy tribute) never fired.
- cp1's passive-aware capture rule and cp2/cp3's fight rules are in cp3; their separate platform effect is unknown.
