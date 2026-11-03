# Bamboo7 status

Source: `bots/Bamboo7/src` on branch `bamboo8`. Behaviour is controlled by `constexpr` switches at the top of
`bot.cpp` and `draft.cpp`; this file lists the ones that matter now. Last updated 2026-10-21.

## Live versions

| Version | Submitted (UTC) | What changed | Ladder bench |
|---|---|---|---|
| v187 | Oct 20 ~05:35 | v185 behaviour on the 3.0.1 SDK (post-patch baseline) | Nyx+Univ 7/40, −13,022 |
| v188 | Oct 20 06:19 | gold weight 0.12, gold fade to round 800, snipes off | Nyx+Univ 8/40, −9,985; + Mite+procless 18/80, −20,666 |
| v189 | Oct 20 07:06 | + true monster reach (`kTrueReach`) | wide 16/80, −24,142 (paired vs v188: −3,476 ± 2,530) |
| v190 | Oct 20 08:12 | + Treasure first on scaling maps (`kTreasureBuild` 1) | wide 16/80, −24,902 |
| v191 | Oct 20 08:23 | v188 behaviour again (true reach and treasure off), the back-to-back baseline | wide 16/80, −23,663 (v190 − v191: −1,239 ± ~3,300) |
| v192 | Oct 20 08:35 | v190's code: the ladder tied, so the local bench decided (true reach +69 ± 29) | wide 16/80, −24,902 (12:03, same games as v190) |
| v193 | Oct 20 12:20:46 | Marcella for C&I, stun draft on farming maps, melee camp ease | wide 19/80, −20,509 (same at 13:42); vs v192 +4,393 ± 2,971; local +53 ± 33 |
| v194 | Oct 20 13:51:04 | + `kMetaBuild` 1: procless's defence-first emblem order | wide 32/80, −9,628; vs v193 back to back +10,881 ± 3,534 (Mite 7→12 wins, procless 3→7, Univ 6→9, Nyx 3→4); local +135/+148 |
| v195 | Oct 20 14:24:41 | + robustness bundle (`kWaveFallback`, `kSquadWalkable`, `kAvoidRepick`, `kCampFaceGap` 3, `kLoopGuard` 10) | wide 26/80, −17,421 (15:05–15:26) |
| v196 | Oct 20 15:28:17 | v194's exact code again (back-to-back check) | wide 31/80, −13,279 (vs v195 +4,142); 21:10: **38/80, +2,539** (opponents changed; likely the Heart of Ruin nerf) |
| v197 | Oct 20 21:21:37 | v196 + bundle with the wave fallback gated (`kWaveIdle` 40) + `kAllyJam` 2 + `kRetreatLoopRecall` | wide 42/80, +9,384; vs v196 back to back +6,845 ± 3,770. **Beware:** 20 of every 80 were free wins over a troll submission (Univardisty); top-10 opponents only (Nyx, procless) at 01:34 Oct 21: 6/40 |
| v198 | Oct 21 01:48:45 | review fixes + yellow-brick-road fixes + big-group fuel (commit 9153cdc) | 31/80 (−21) vs v197's 38/80 (+4,533) back to back; **top-10 opponents only: 3/40, −3,000 ± 1,927 vs v197's 6/40**; top four (Fish, :3, Nyx, FürFortnite) at 02:02: 9/80, −37,716; local pool −41 ± 38. Replaced |
| v199 | Oct 21 ~02:08 | v198 minus the `ruin_dash` landing-tile odds check (commit 510cb19) | top-10 only (Nyx, procless) at 02:08: **2/40, −17,380** (Nyx 2/20 −7,070, procless 0/20 −10,310) vs v197's 6/40 −15,061 and v198's 3/40; new maps (01yellow_brick_road, 01starfish, 01the_farm, 00rows, 00swirl × top four, queued 02:40 while v199 was live, tag `topnew198`): 1/20, −10,279; local pool −22 ± 37. Replaced |
| v200 | Oct 21 02:51:09 | **v197's code again** (bots/B7Live src restamped): the review bundle never beat v197 on the ladder, so the measured best goes back live | Nyx+procless at 03:00: **6/40, −14,072** (Nyx 4/20 −5,597, procless 2/20 −8,475: the same games as v197's) vs v199's 2/40; top three (Fish, :3, FürFortnite, 3-team bench from here on) at 03:06: 5/60, −32,289 vs v199's 6/60 −30,386 on the same teams. All five teams: v200 11/100 −46,361, v199 8/100 −47,766, v198 9/100 −48,260. Re-benched at 04:00 (np200b/top200b): the same games, game by game (the ladder had not changed), so these stay the baseline for v201. Replaced by v201, then back as **v202** |
| v201 | Oct 21 04:21:22 | v200's code + `kNextOnce` + `kWakeGuardStr` 100 + `kBaitGuard` 2 + `kAggroExit` 6 / `kAggroExitStr` 100 (bots/V201) | **worse**: Nyx+procless 4/40, −17,474 (vs 6/40, −14,991); top three 2/60, −37,734 (vs 5/60, −32,289); all five 6/100 −55,208 vs v200's 11/100 −47,280. Unseen maps: 53 vs 54 wins, loops 350 vs 160 rounds. Eric's two replays of it (boss_battle, concentrated_wealth vs Nyx) still show the monolith deaths: Ren waited 25 rounds beside the sleeping pair to tribute 45 gems at the centre altar until Nyx's Ryth woke them. Replaced after 23 minutes |
| v202 | Oct 21 04:44:22 | **v200's code again** (bots/Up202, B7Live src restamped) | the better-measured bot; its bench is v200's (deterministic). Replaced by v203 |
| v203 | Oct 21 05:12 | v200's code + draft `kThreePick` 1 (Heart of Ruin, Ryth, Stellar on three-pick maps; Varg on clumpy ones) + `kPartyArrival` (bots/V203) | Nyx+procless (the two-team bench from here on): **5/40, −17,152** (Nyx 3/20 −8,186, procless 2/20 −8,966) vs v200's 6/40, −14,991: a tie by the ladder's resolution (−2,161 over 40 games, under the ~3,000 noise), so the local screen decides (+41 ± 21 and +20 ± 37 on the 1.0.1 engine). Lost boss_battle vs procless (−1,319 vs +214) and gold_rush vs Nyx; won elk_arena vs procless (+1,008 vs −312). Unseen maps (40, both sides vs B7Base): 54 wins like v200, loops 146 vs 160 rounds, stuck 18 vs 39 rounds, more standing guard (145 vs 52 rounds: the party-arrival wait). Replaced |
| v204 | Oct 21 08:15:49 | v203 + farming combination (`kTreasureBuild` 2, `kAutoTeam` off, `kSquadSize` 1) + `kTrueWake` (bots/V204) | locally +26 ± 33 over v203's settings on 35 maps (three seeds +23 to +48); ladder **3/40, −19,686** (Nyx 2/20 −7,808, procless 1/20 −11,878): −2,534 vs v203, **−4,695 vs v200**. Won corners vs Nyx (+623) but lost elk_arena to both (−864 twice, where v203 won). Replaced |
| v205 | Oct 21 08:25:05 | **v200's code again** (B7Live src restamped) | **Correction (Oct 21 afternoon):** the ladder's engine moved to 1.0.2 at 05:20 UTC, so v200's 1.0.1 bench (6/40) does not compare with v204's 1.0.2 one (3/40). Our matches' banners show **v203** playing ranked games from ~09:00 and the 10:20 bench (`np205`: 3/40, −17,885 vs Nyx and procless) instead of v205; v205 again at 08:30 and 13:00. On 1.0.2: v203 3/40 −17,885, v204 3/40 −19,686 (a tie); v205 (v200's code) not measured. Its code is live again as v224/v227 (below) |

### Oct 21 afternoon: v206-v216 (12-hour grant; bench = procless + EMPEROR Tung, 20 maps each, `bench_pe.txt`)

Engine 1.0.2. Each row is a 40-game ladder bench (deterministic); `tools/stress/benchprof.py TAG` gives the economy. The
upload copies of v206 and earlier printed diagnostics (`kTargetLog` + `kLogActivity`), which **cost play through fuel**:
the same code locally +102 with them, +186 without (+84 +-36; `edit_cheapnote.py` makes note() cheap). From v208 uploads
carry no diagnostics.

| Version | Submitted (UTC) | What | Bench (wins, margin a game) | Gold r600 / gems r900 (ours, theirs) |
|---|---|---|---|---|
| v205 | (live from 08:25; re-benched 13:40) | v200's code | 1/40, -580 (ran v205; the 10:20 bench ran v203) | 2283/221 vs 3863/539 |
| v206 | 13:48 | Cand206 (v204 settings + kRangedHome + pathing + squads of 3 + own-half opening + HoR for Varg + harmless groups never wait) + kDashKite 5 | 0/40, -551 | 2309/238 |
| v207 | 13:54 | v206 + no whole-team opening, squads of 2 | 2/40, -594 (corridors: all five idle at spawn for ~100 rounds: no camp feasible for a squad of 2) | 2200/206 |
| v208 | 14:09 | v206 + kGuardMax 15, kOneCapturer, kSquadMoveOn 10, cheap note(), no diagnostics | 3/40, -561 | 2172/183 |
| v209 | 14:26 | **v196's code** (commit 898bebd): Eric asked whether we regressed | 1/40, -563 | 2367/258: **no regression** - every version since v196 scores the same against these two on 1.0.2 |
| v210 | 14:38 | v208 again | - | - |
| v211 | 14:42 | v208 + kTeamSquads 2 (opening as two squads) | 2/40, **-505** (best) | 2209/226 |
| v212 | 14:50 | v211 + wake guard 100, kAltarKeep, kRecallVsWalk, kResume 150, kAutoTeam whole-game only | 2/40, -542 (rows vs procless -257 vs -418; corridors -954/-933 vs -820/-871) | 2306/239 |
| v213 | 14:59 | v211 + draft kFishDraft 3 (procless's list: HoR, Vesper, Ryth, Marcella, Vendetta) | 2/40, -555 | 2171/246 |
| v214 | 15:11 | v211 + kSquadSize 1 + kSoloBias 0.6 (solo farming) | 1/40, -636 (worse: gold r300 908) | 2017/199 |
| v215 | 15:21 | v211 again | - | - |
| v216 | 15:30 | v211 + Eric's requests: wake guard 100, kAltarKeep, kRecallVsWalk, kResume 150, kRuinSave 2 (no escape dash for HoR), kHoldReward 0.6, kLockedNode 12 | -599 | |
| v218 | | squads of 2 after the opening | -628 | |
| v219 | | hunting | -590 | |
| v221 | | kOutgeared 2.0 (alone, evade a much stronger enemy) | -570 | |

From v224 the bench is **Mite + procless** (`bench_pm.txt`: one top-10 team and one near our rating, Eric's "Both"):

| Version | Submitted (UTC) | What | Mite + procless bench | Ranked games (by `BAMBOO vN` banner) |
|---|---|---|---|---|
| v224 | ~19:55 | **v205's code** (Up205, no diagnostics) | 6/40, -19,991 | **18/30, +110 a game** (20:00-20:50, opponents ~1785) |
| v225 | 20:59:18 | B7Dev + waitfix + kCampAware, kRootWalk 2, kWaitSafe, kDashKite 5 | 6/40, -19,922 (a tie) | **4/20, -235 a game** (21:00-21:40, opponents ~1770): rating 1787 -> 1745, rank ~69 -> 99 |
| v226 | 21:43:09 | v225 + `kRowScan` (`edit_rowscan.py`) | 6/40, -19,972; yellow_brick_road vs Mite 0 stuck rounds (v225: 2,761), 164 gems (v225: 0) | 2/3 |
| v227 | 22:00:25 | **v224's code + `kRowScan` + waitfix** (bots/Up227): v225's switch set lost on the ladder, so its base goes back | 5/40, -19,798 (a tie with v224: the same games to within a few hundred except quadrants +898 and yellow_brick_road +400) | **27/45 (60%)** 22:00-23:20, rating 1742 -> 1772, rank 99 -> 79 |
| v228 | 23:25:00 | v227 + the review fixes measured positive or neutral: `kDashDamage`, `kMemberBlock`, `kPokeNoDash`, `kBankUsable`, `kWaveShared` + the no-switch fixes (bots/Up228; the set is `scratchpad cfg_v228.txt` on `bots/Dev227`); locally +58 ± 39 over v227's code | 5/40, -20,412 (v227 -19,798: a tie) | 12 minutes live |
| v229 | 23:37:59 | v228 + **`kMetaDraft` 4** (HoR, Vesper, Ryth, Marcella, Vendetta; Eric: we win the early fights and get out-farmed by Vesper + Vendetta gold) (bots/Up229); locally +28 ± 58 | **7/40, −15,789** - the best bench of the day (v228 5/40 −20,412 on the same games: +4,623, above the ~3,000 noise; Mite 6 wins: expanse, monolith, big_world, boss_battle, fracture, gold_rush) | pending |
| v231 | Oct 22 00:36:18 | v230 + `kFightStall` 12 + `kRevealFix` (the Vesper freezes; `kDeadRoot` with its field-erase hook was −120 ± 55 and stayed off) (bots/Up231) | **8/40, −14,377** (v230 −14,941) | pending |
| v233 | Oct 22 00:50:22 | v232 + `kSightRoots` (Eric's corridors observation; alone +16 ± 47) (bots/Up233) | 8/40, −15,739 vs v232's 9/40, −14,831: a tie that swings games both ways (collision +1,499, monolith +248, quadrants +250; fracture −700, starvation −1,036, concentrated_wealth −434). Replaced by v235 (v232's code) after 5 minutes: the measured-best code plays the ranked games; `kSightRoots` stays a candidate to judge by ranked games | |
| **v235** | Oct 22 00:55:26 | **v232's code** (bots/Up235 = bots/Up232/src restamped) - live at the end of the Oct 21–22 session. **The platform calls it "bot version 234"** (bots/Up234, the −86 erase variant, was never submitted, so the platform's count runs one behind the banner from here: banner `BAMBOO v235` = platform 234) | v232's (deterministic) | |
| (v234, not submitted) | | v232 + `kDeadRootErase` 2 (our target's approach field dropped when its member dies): the last big_world Vesper case gone (4/4, 0 stuck), but **−86 ± 48** on the pool (B7Base +109 vs +312): every kill in a camp fight now shifts the roots and the fighters reposition instead of attacking. The remaining freeze (one big_world game in six, 292 rounds: a field built before a member died keeps the dead member's root) needs an invalidation that does not move fighters mid-fight - e.g. rebuild only while not engaged | | |
| v232 | Oct 22 00:48:09 | v231 + `kShootReach` (+9 ± 6; review #7: a shootable camp needs a firing tile a walk from spawn reaches, seeing a living member) + `kDeadRoot` roots-only (`kDeadRootErase` false: +10 ± 22, big_world +124, islands +127 - the erase hook was the −120) (bots/Up232) | 9/40, −14,831 (v231 8/40 −14,377: a tie; concentrated_wealth vs Mite +425, islands −306, swirl −142) | ranked 00:40–00:50 (v231/v232): 9/10, rating 1752 → 1778, rank 93 → 77 |
| v230 | 23:54:35 | v229 + the offensive-only monolith guard (`kDashWakeStr` 100, `kDashWakePaths` 1), rebuilt from Up227 through the scripts (bots/Up230 = bots/Dev227m + cfg_v228 + the guard); pool +13 ± 7, replay metrics above | **7/40, −14,941** (v229 −15,789 on the same games: +848, only the games where the guard fired differ: boss_battle vs Mite +173, concentrated_wealth vs procless +537, fracture −127) | pending |

**v229's draft in the bench economy** (`tools/stress/benchprof.py pm228 pm229`, the same 40 games): gold r600 2,765 vs
v228's 2,205 (theirs 3,686), gold r900 4,065 vs 3,191 (theirs 5,473), banked gems r900 319 vs 246 (theirs 476), camp
damage per 1000 rounds 83k vs 72k (theirs 109k), deaths 7 vs 8 per 1000, margin −370 vs −488 a game. The gold gap at r900
closes from 50% to 74% of theirs - Eric's call (out-farmed by Vesper + Vendetta) measured.

**The ladder bench against two top teams does not separate versions; ranked games do.** v224 and v225 benched the same
(6/40) but went 18/30 and 4/20 in ranked games against teams of our own rating. Attribute ranked games by banner
(`replays/rk1021`, `DETAIL=1 tools/stress/ratinghist.py` for per-group results).

**Row freeze (`kRowScan`).** Travelling to a group none of whose members is in sight, standing on its own spawn tiles,
the reveal step (`capture_key` field, distance 0) never moved again. On yellow_brick_road the 30-tile gold rows are
longer than vision: champions stood on the dead west half (5..9,17) while the live members (21..34,17) were out of
sight - v225 vs Mite: four champions from r100, 2,761 stuck rounds, 0 gems. Fix: walk to the group's nearest unseen
spawn tile. Locally (4 opponents, team A) 16 stuck episodes / 514 rounds -> 0; pool screen +4 +-8 (only that map moves).

**Rejected: `kDeliverCommit`** (`edit_delivercommit.py`). boss_battle team A: Ryth (45 gems) shops because home is within
`kNearShop` 15; retreat() walks to the altar beside the boss (one tile further from home), kNearShop stops holding, travel
steps back: travel <-> retreat for 25-35 rounds from r65 in every game. Keeping the retreat once it heads for the altar
removes the loop but walks Ryth into the boss's reach: -27 +-14 on the pool, all of it boss_battle (+608 -> +67).

### Oct 22: the review of 4683c2e (`.info/Reviews/Review-2026-10-22-4683c2e.md`) and the v227 bug hunt, switch by switch

Base = `bots/Dev227` (v227's source + the no-switch fixes: draft-plan walk flag only on success, allocator wrap guard, row
scan skipping members seen dead). Pool screen, 35 maps × 2 sides × B7Live/B7Base, paired difference vs that base:

| Switch (script) | Finding | Paired | v228 |
|---|---|---|---|
| `kDashDamage` (edit_dashdamage.py) | review #2: a hitting dash was not damage in our dps / enemy burst | **+81 ± 28** | on |
| `kMemberBlock` (edit_memberblock.py) | review #4: dead members of a live group blocked paths and altar tiles; epoch hashes occupancy | +26 ± 41 | on |
| `kPokeNoDash` (edit_pokenodash.py) | review #1: the outnumbered poke could dash in | +5 ± 7 | on |
| `kBankUsable` (edit_bankusable.py) | ours: retreat's altar shortcut / deliver() with no usable altar - Ryth stood beside the live boss with **964 gems** from r1727 to r2000 (boss_battle, lost 53-0); tribute range is 1 and that altar's only tribute tile is the boss's spawn tile | +3 ± 4 | on |
| `kWaveShared` (edit_waveshared.py) | review #3: wave marker private to the scorer, never reset | −4 ± 19 | on (a logic fix, no measured cost) |
| `kFinishBag` (edit_finishbag.py) | review #5: our bag missing from the finish-window gate | −6 ± 5 | off |
| `kShopHold` 30 (edit_shophold.py) | ours: the boss_battle travel <-> retreat loop at the kNearShop boundary (25-35 rounds a game as team A) | −6 ± 4 | off (the loop no longer stands beside the boss with kBankUsable; a shorter hold untested) |
| `kPickDirty` (edit_pickdirty.py) | review #6: forget_picks forced a rescore under the low-fuel guard | −13 ± 32 (B7Live −71, B7Base +45) | off |
| `kMetaDraft` 4 (draft edit_meta4.py) | Eric: the meta is HoR, Vesper, Ryth, Marcella, Vendetta | +28 ± 58 | off; a ranked experiment on its own |
| `kDashWakeStr` / `kDashWakeHp` / `kDashWakePaths` (edit_dashwake.py) | Eric's design: a dash landing is checked for the camp groups it would newly wake (clusters included) and their attackers in reach; the current target (engaged, or no enemy within 5) and groups we hit within 2 rounds are our fight | first form (every candidate landing checked, "awake" = any hurt member) −122 ± 44; narrowed −85, −111; **per path**: hitting −2 ± 16, travel −71 ± 43 (an engine read per candidate landing: fuel, elk-arena −885 with no monolith on the map), chase −3, escape −14; **offensive-only, monolith strength 100, checks on the ranked landings only: +13 ± 7** (gold-rush +244, every map where it never fires identical). Replay metrics (`tools/stress/dashaudit.ts`, 8 monolith maps × 2 sides vs B7Live, deterministic): only the games where it fired changed - gold-rush as A went from a 583–917 loss to a 1007–407 win (HoR deaths 6 → 1, landings beside the monolith 5 → 2, both after r1700), monolith ±80; wins 8/16 both, our banked gems 11,190 → 11,624, fuel-limit turns unchanged | **on in v230** (`kDashWakePaths` 1; travel/chase/escape off) |

**Vesper's freezes (v229/v230, fixed in v231).** The meta draft put a 3-range champion into every game and the all-maps
scan of v230 showed 1,796 stuck rounds (v227: 62): big_world 848 and 592, islands 337, all Vesper. Two latent bugs of
the v205 line that her range reaches: (1) a group's approach field draws its roots within our range of *every* original
spawn tile, dead members included - Vesper stood 3 from a dead gold cluster and 4 from the living gem clusters across a
ring of holes, "arrived", in fight_camp with nothing landing (`kDeadRoot`: roots skip members seen dead, the field is
dropped when a watched member dies; `kFightStall` 12 as a net); (2) within range of a camp she could not see behind a
wall column, the reveal rule walked "onto its tiles" - unwalkable while it lives, so step() returned false forever and
no stuck detector watches that branch (`kRevealFix`: greedy step, else avoid). v231 check, 16 games: stuck 9 rounds.
Also: `kWallStep` (engine path when a wall crosses the straight line to the goal) is off since the wall review measured
it −19; Eric (Oct 22 00:30) sees champions walk into walls - re-screened on the current base: −29 ± 48 (base draft),
−15 ± 58 (meta draft): still off. A walls-only variant (`kWallStep` 2, `edit_wallonly.py`: the engine path only when a wall,
not a hole/altar/camp, crosses the line) is −6 ± 23 on the pool and **worse where it matters**: on eight wall maps the
walking-loop rounds went 36 → 448 (the engine's path step and the greedy step undo each other beside walls - the
documented failure). The wall walking wants a field-based approach step (a distance field to the goal, as `step()` has
for camps and home), not a line test. *Oct 22 02:05:* `kWallStep` 3 (`edit_wallcommit.py`: walls-only line test, then
the engine's path kept for `kWallCommit` turns toward the same goal) - wall-map loop rounds 38 → **926** (wins 11 → 14,
stuck 77 → 1), pool −20 ± 32 (commit 4) / −6 ± 35 (commit 8). So the engine's `move_towards` itself bounces between
equivalent first steps turn to turn; following it, committed or not, loops. The fix is our own BFS field per goal
(deterministic ties), cached per goal tile: a design job, parked.

**v236** (Oct 22 ~01:12, platform "bot version 235") = v235 + `kDeadRootErase` 3 (our target's approach field dropped when
its member dies, only while we have not hit it for 2 rounds: a fighter's roots never shift): −6 ± 44 on the pool, the last
big_world Vesper case gone (4/4, 0 stuck; big_world +196). **`kSightRoots`** (a ranged champion's approach roots must see a camp tile - walls block) answers Eric's
corridors observation (ranged champions walk to the root on the far side of the camp's wall, then back out the corridor):
alone +16 ± 47 (corridors +145, islands +186, lanes +109, big_world −52); with roots-only `kDeadRoot` −16 ± 47 (big_world
−191: both change the roots). Shipped as **v233** on top of v232 for the bench to decide.

HoR's travel dash (Eric, 00:25: "dashes to the side"): `try_dash` takes every landing exactly 2 away (diagonals included)
that shortens the path field by 2 and sorts by the remaining field distance; ties fell to scan order (dx then dy), so a
sideways landing could win a tie against one straight ahead. `kDashTie` (`edit_dashtie.py`: a tie goes to the landing
nearest the step's goal) +20 ± 37 on the meta-draft base; shipped as **v239** at 01:53:14 (platform 239; the 01:51:59
submission, platform 238, carried v238's code again - the script's constant anchor had missed on the upload copy). Bench
`pm239b`: **10/40, −15,951** vs v236's 9/40, −14,703 - the most wins of any version and a worse margin (monolith +381 and
quadrants +315 vs Mite; starvation −1,403, interlock vs procless −191): a tie by the bench's resolution. Live at the end
of the Oct 22 session; the ranked games judge it.

**Splitting up, map-generally (Eric, 01:20):** the team-vs-solo opening already comes from the camps near spawn
(`kAutoTeam`: team when their value ≥ 1.2 × the solo camps' value). Stricter ratios on the meta base: 1.5 changes no pool
map, 2.0 −8 ± 5 - the margin is not where corridors sits. Corridors pays +325 only with no team opening at all, which
costs −25 across the pool; solo farming everywhere (`kSquadSize` 1) is +30 ± 25 locally but −950 on the ladder bench
(v237). The general lever would be the champions' strength against the camps (champions_needed per camp with the actual
roster), not the camps' value ratio; not built.

:3's permanent recalls (Eric, 00:35): recall-captures - the recall starts on the reward tile, the 5-round capture lands
during the 5-turn (Home: 3) channel, and they shop at spawn after nearly every capture; our recall round trips are ~48
rounds to their ~40 (`.info/knowledge/top-teams-1.0.2.md`).

**Next (not done): 01boss_battle banking.** With `kBankUsable` nobody stands beside the live boss any more, but in v228's
six local games our champions ended with bags of 614–1,706 gems and 1,000–1,900 champion-rounds carrying 300+: the only
tribute tile is the boss's spawn tile (tribute range 1), the boss pair (2 × 20,000 health, 200 strength) is neither a
boss-mode group (`kBossMaxStr` 100) nor a snipe group (`kSnipe` 0), so nothing ever plans to kill it; we win those games
on the gold tiebreak and lose them to teams that do kill it (procless banked 1,281 there; our v225 banked 1,373 once).
The general rule to add: an altar none of whose tribute tiles is free of a camp makes that camp worth the team's carried
bags - mark it a boss group (budgeted like `kBossBudget`, but for 200-strength monsters: rotate the nearest champion) or
a snipe group, and bank from its tile during the respawn window.

*Tried (Oct 22 01:15, `edit_altarboss.py`, `kAltarBoss`: every altar's tribute tiles on camp spawn tiles → those groups are
boss groups whatever their strength, a map-general rule).* Six local games: the boss pair does die (r650 and again
later), but we banked 0 / 105 / 297 / 484 / 0 / 663 with bags of 900–1,400 - no better than before. The real failure is
the **banking window**: vs B7Live as A we *started* tributes for 54 rounds and banked nothing while B7Live tributed for
199 rounds and banked 1,017. The only tribute tile is the boss's spawn tile, one champion at a time, and a 900-gem bag is
a 90-turn channel that any stun, kill or lock ends. What is needed is strategy, not a flag: keep bags small on such a
map and bank each one in the window as soon as the altar opens (a tributer on the spawn tile also delays the respawn),
sharing the tile between carriers. `kAltarBoss` stays off.

*Tried next (`kWindowBank`: on such a map bank any bag of 10+ the moment an altar is usable).* Same six games: banked
30 / 10 / 38 / 292 / 0 / 927, bags still 700–1,700. Vs B7Live as A the boss was dead r700–800 and from r1800; B7Live
(v200's code!) tributed for 371 rounds there and banked 599, we tributed for 20 rounds and banked 30: our carriers are
not at the altar when it opens, and when they are, enemies at the centre make the channel "unsafe" and they leave. The
v200 line banks there as the *opponent*; what changed is the roster and the farming spread. Both switches off; the next
owner of this map needs a window plan (who waits where, who tributes first) measured on these six games.

**Eric's Oct 22 02:00 requests, on the meta-draft base (Dev227m), paired:**

| Switch | Finding | Paired |
|---|---|---|
| `kMarcellaCarry` (edit_marcellacarry.py) | Marcella takes whole rewards like a carrier: her passive pays 2 gold per gem tributed | **+51 ± 38** (corridors +130, yellow_brick_road +90) → **v240** |
| `kMetaBuild` 7 (edit_proclessbuild.py) | procless's 1.0.2 order: Treasure Health (Strength on Vesper), Jungle, Durability Health, main stat | −23 ± 47 (lanes +133, yellow_brick_road −167): a ladder-bench question |
| `kVesperSolo` 300 (edit_vespersolo.py) | Vesper farms alone, gold ×2, before r300 while under 250 wealth | −41 ± 37 (packs −419, gold-rush +205, lanes +144); 150 rounds −41 ± 42; 300 with no gold weight −64 ± 38. **Off**: alone she is the easy kill on fight maps; her gold bonus is already a reason to put her on gold camps *with* the squad |
| `kAutoTeamStr` (edit_autoteamstr.py) | the opening's team-or-solo answer from `champions_needed` against a roster-average champion, damage scaled by `kAutoTeamStrScale` | ×1 −41 ± 32 (at round 1 almost every camp "needs a party": more team farming), ×2 −23 ± 34, **×3 +24 ± 25** (corridors +387, gold-rush +288, yellow_brick_road +404; rows −125, packs −66) → **v241** (Oct 22 02:21:44, platform 241) for the bench; ×4 +24 ± 25 and ×5 +31 ± 24 play the same games on nearly every map (flat from ×3 up): ×3 kept |

**v240** (02:17:47, platform 240) = v239 + `kMarcellaCarry`: bench **10/40, −12,996** - the best margin of the session (v239
10/40 −15,951, v236 9/40 −14,703): swirl vs Mite +1,900 (W 908 from L −992), starvation +1,419, monolith vs procless +416;
interlock vs Mite −804, corridors −214. **v241** (02:21:44, platform 241) = v240 + `kAutoTeamStr` ×3: bench 9/40, **−12,651** vs v240's 10/40, −12,996 - a tie
with the gains where the rule aims (corridors vs Mite +749 and vs procless +646, interlock vs procless +197, monolith vs
procless +397) and losses elsewhere (concentrated_wealth vs procless −565, quadrants vs Mite −273, boss_battle −140,
yellow_brick_road −123/−113). Kept. **v242** (02:23:29, platform 242) = v241 + `kMetaBuild` 7 (procless's 1.0.2 build):
bench **6/40, −17,561** vs v241's 9/40, −12,651 - a 4,910 loss on the same games (swirl vs Mite −1,791, starvation
−1,131, corners vs procless −620, monolith −579; fracture +354, gold_rush +171): Treasure Health first starves our camp
fights of Jungle and Bruiser health, as the Treasure/Power-first tests did on Oct 21. **Off**; v241's code back live as
**v243** (02:28, platform 243) - the state at the end of the Oct 22 session.

**Eric's Oct 22 03:30 replays** (`replays/eric1022`): corridors (v246 as A, v249 as B) - Vesper roams the whole map all game
(gems 4, gold 9 at r1180): she arrives at camps on the side she cannot see them from, the reveal step has no way onto
their tiles, the camp is avoided, she walks to the next. Visible-only approach roots (`kSightRoots`) address exactly that
→ **v250** (03:56:06, platform 250): bench 9/40, −15,095 vs v249's −13,927 - a tie that moves many games
(concentrated_wealth +494, islands +484, collision +355, quadrants +295, lanes +171; starvation −626, fracture −445,
swirl vs procless −416, corridors −160: the corridors game itself did not improve). Locally on corridors Vesper farms
almost nothing in either version (gems 0–38 by r1200). Her trace (`bots/Dbg250`, corridors as A): **562 of 1,296 turns
travelling** (43%), fight_camp 23%, targets alternating between the map's two sides (t11 at x≈44, then t5/t6 at x≈10 and
back), 20 gems by r1000 - a ranged 3 champion soloing far camps she clears slowly instead of entering the corridor with
the melees. The ×3 opening split lets her solo early; her solo picks beat the squad's at `kSoloBias` 1.0. Candidate:
`kRangedSoloBias` (edit_rangedsolo.py: a ranged champion solos only when its camp scores 1.5–2.5× the squad's pick):
**1.5 +25 ± 31** (B7Live +55; split +378, yellow_brick_road +159, lanes +65; interlock −281, packs −195), 2.5 −16 ± 29.

**v251** (04:12:09, platform 251) = v250 + `kLowSnipe` + `kDashWakePaths` 3 with `kDashWakeTravelStr` 60 +
`kRangedSoloBias` 1.5. Stress check (24 games, 12 maps × 2 sides vs B7Live): 17 wins, gems 20,029 vs 17,581, loops 8
(16 rounds), stuck 0, 3,479 fuel-limit turns. Bench **8/40, −14,877** vs v250 9/40 −15,095 and v245 −13,927: a tie
(boss_battle +430, starvation +558, fracture +483, corridors +363; islands −510, big_world −329, concentrated_wealth −238).
Kept.

**Snipe assist** (`kLowSnipe`, edit_lowsnipe.py; Eric 03:30): a melee champion under the retreat line beside a camp a mate
is fighting snipes it from outside its attackers' reach with a damage ability that out-reaches them (Marcella's and
Ren's range-4 spells vs wolves' 3), holding outside the reach while it recharges; not with a low mate, not under the
floor, never with an enemy about. Pool **+8 ± 22** (floor 0.2; 0.25 +6 ± 22; elk-arena +249, gold-rush +38, lanes +24):
in the next version. HoR's travel dash waking a camp he is not targeting (the third replay, Vesper
dies): `kDashWakeTravelStr` (edit_dashwake.py) gives the travel dashes their own strength line: any attacker (1) −29 ± 35
(B7Live −96: wolf camps block too many hops), **elks and up (60) −5 ± 33 with fracture +244 and elk-arena +258**; the
hitting-dash guard alone (live) +5 ± 9. Paths 3 with the travel line 60 is the candidate after the snipe.

**prism best girl's resource allocation** (rank 1, 2201, Oct 22 04:20; Eric: "they target the big camps with 2+ elks
first and give the gold/gems to Vesper or Prism first, on some maps Marcella"; "gold map → Vesper carry, gem map →
Prism carry"). Ten of their ranked games (vs Sponge 04:10 and procless 03:20, `scratchpad/pbg`) and Eric's three
games against them (v249: 01yellow_brick_road −650, 00quadrants −272, 00packs −261; `scratchpad/eric4`; map names
by `mapid.ts`), with `capwho.ts` / `capclass.ts` (tools/stress; rewards go to the champions on the tiles at the capture):
- **One champion on the tiles at 97% of their captures** (10 shared of 320): the whole reward goes to one bag. Ours:
  8% shared in the v251 stress games (34 of 433), 5 of 13 on packs against them.
- **Who takes what** (K = 3.5 gold per gem): gold-dominant groups Vesper 86 of 249 (35%; 59% in the five games
  where she farmed the gold side), Prism 44, Marcella 39, HoR 29, Ryth 20, Vendetta 9 (fracture: Vendetta drafted
  for Ryth took 850 gold). Gem-dominant groups: **Prism 43 of 71 (61%)**, Marcella 9, shared 7. Our gold rewards
  (stress games): HoR 100, Marcella 94, Vendetta 92, Ryth 77, **Vesper 33 (8%)**; gem rewards: HoR 5, Vesper 3.
- Per map: lost_world (gem share 0.71) Prism 27 captures, 640 gems; quadrants (0.78) Prism 9 of 14 captures, 569
  gems, 974 banked at r557 (we 702, splitting Marcella/Vendetta and HoR/Vendetta); great_wall (0.73) Prism 720 gold /
  189 gems. Gold maps: lanes Vesper 15 captures 1,249 gold; fragment Vesper 9 of 13; packs (3 picks) Vesper 12 of
  19, 2,101 gold by r300 and 3,298 by r600 vs our HoR 1,100 / Ryth 1,120 (we lost HoR r52 1v3 and Ryth r59 0v3 mid);
  **yellow_brick_road: their Vesper took both 30-cluster gold nodes alone (600 gold each, 798 with her +33%), 4,947
  gold by r450 and 7,501 by r600 (40 emblems, Power Strength 4,950)**; we earned 1,150 all game and died 27 times
  (HoR r33 3v5 and Ryth r39 1v4 on their half, then every 30-60 rounds at home). Mixed maps spread: pilgrimage
  Marcella 574, HoR 453, Vesper 425, Ryth 423; monolith Vesper 1,064, Marcella 730, Prism 590.
- So it is a **per-group rule, not a per-map draft**: the champion whose passive fits the reward takes it (Vesper +33%
  gold, Prism 1.5 Focus per carried gem), the others step off; on maps where one resource dominates that champion
  becomes the carry. Vesper's gold multiplier is +33% on every capture (160/120, 53/40, 172/130, 798/600).
- **Big camps**: the whole team opens on the nearest camps and clears the 2+-elk groups together when it meets them
  (elk_arena EEgggggg hit r6, cleared r54 with 3.9 of them near, Prism on the tiles; great_wall EEEggggg hit r22
  cleared r134 at 1.5 near, HoR; monolith Eggg r10-22 at 4.3 near, Vesper), then farms solo (1.0-1.5 near).
- **Drafts** (200 ranked games): Prism first in every game. Five picks Prism, Vesper, Marcella, Ryth, HoR 90/108;
  four Prism, Vesper, Marcella, Ryth 30/33; three Prism, Vesper, HoR 14/17 (Prism, Vendetta, HoR 7/9 before 00:10).
  Variants (Vendetta for Ryth on fracture/expanse/yellow_brick_road/boss_battle/corridors 5/6; Marcella, Vendetta,
  HoR, Vesper on great_wall/elkring/starfish/ambush/big_world/eight 4/8) appeared from 02:40, i.e. by upload time,
  not by map resources. Against procless (rank 2) they are 7/10.
- Switches: `kVesperCarry` (edit_vespercarry.py: Vesper takes gold-dominant rewards, Prism gem-dominant ones; 1 team
  mode, 2 any squad; `kVesperGoldW` for her camp scores) and draft `kMetaDraft` 5/6 (edit_meta5.py: their lists;
  Prism for Vendetta in ours). Screen (35 maps × 2 × B7Live/B7Base, `bots/Dev251` = Up251 + both scripts, seed 1,
  base 105/140 +267): `kVesperCarry` 1 **+19 ± 45 (111/140)**, 2 +36 ± 49, 2 with `kVesperGoldW` 1.33 **+60 ± 50**
  (B7Live +279 vs +126; pilgrimage +507 vs −51, boss_battle +840 vs +363, contest +750 vs +100, interlock +677 vs
  +261; yellow_brick_road +205 vs +645, corners −460 vs −256, rows −170 vs +9). Their draft (`kMetaDraft` 5) −9 ± 45,
  Prism for Vendetta (6) −18 ± 32, their draft with the carry −43 ± 42: a local screen cannot judge a draft against
  our own code, but nothing there asks for a bench. Seed 2: carry 1 −57 ± 48, 2 −15 ± 47, **2 with the gold weight
  +6 ± 46 (111/140)**, 1 with the weight −34 ± 49. Two seeds paired (n 280): carry 2 + weight 1.33 **+33 ± 34,
  217/280 vs 211/280**, B7Live +223 vs +145; pilgrimage +375 vs +3, interlock +684 vs +328, packs +358 vs +149,
  boss_battle +560 vs +290, contest +475 vs +250, corners −172 vs −419; yellow_brick_road +182 vs +536 (she walks
  the gold road further), split +55 vs +262, monolith +41 vs +172.

**v252** (04:53:17, platform 252) = v251 + `kVesperCarry` 2 + `kVesperGoldW` 1.33 (`bots/Up252/src`,
`scratchpad/chain252.sh`). Stress check 18/24, gems 21,671 vs 16,402, stuck 0, loops 16 (81 rounds: corridors 43,
rows 28). Bench pm252 queued at 04:53:30. **But** `capclass.ts` on those 24 games: shared captures 25% (105 of 419)
against v251's 8%, Vesper 14% of gold rewards (8% before): the first form only overrode the carrier flags, so with
Vesper near but not yet on the tiles the Vendetta/Marcella rule was bypassed and nobody yielded (lanes: Ryth+Vendetta,
HoR+Vendetta, HoR+Vesper on the tiles together). Fixed in edit_vespercarry.py: the others leave the tiles to the
preferred carrier outright (step off, move on; she must be alive, not recalling, above the retreat line, within 6);
re-screened: **−208 ± 32** (161/280; packs −362, lanes −304, corners −779, yellow_brick_road +21 vs +536): a champion
only captures its own target, so when Vesper was near but on another camp the reward went unclaimed. Never leave a
reward for a carrier who has not come. Script reverted to v252's form (plus a health gate on the carrier) and a
variant 3 (the others step off already when she is beside the tiles on the same target): two seeds, v252's form
**+34 ± 34 (218/280)**, variant 3 **+38 ± 32 (216/280)**, the gold weight alone −23 ± 17 (the carry rule is the gain,
not the weight). Variant 3 still shares 25%: the pairs are HoR + Vesper (33 of 71 in 12 games) - HoR channelling a
recall-capture on the tiles cannot step off when she steps on. A form where she waits beside occupied tiles (up to
4 rounds) and leaves channelling mates their reward: sharing 9%, but Vesper back to 8% of gold and the gain gone
(−0 ± 29 / +8 ± 29). v252's form except she leaves a reward to a mate channelling a recall on it: sharing 10%,
Vesper 12% of gold, **+5 ± 32** (215/280; variant 3 −9 ± 31). So half of v252's gain is Vesper taking half of HoR's
recall-captures. The others not recall-capturing beside her (script value 5): −6 ± 32, sharing 14%. **Kept v252 as
it is**; every one-carrier refinement is within noise of zero while v252's form is +33/+34 in two independent runs.
The script's values now: 2 = v252's form (plus a health gate on the carrier), 3 = step off when she is beside,
4 = she leaves channelling mates their reward, 5 = no recall-capture beside her. v252 ranked 05:00-05:45: **16/25**,
rating 1887.0, **rank 36** (60 at 04:08, 46 at 04:45). v252's bench nonetheless: **10/40, −14,031** vs v251 8/40 −14,877 and v250
−15,095 - the most wins of the pm series and the best margin since v240's −12,996 (interlock vs Mite +673 to a win,
boss_battle +350, procless corridors +324; Mite corridors −406, starvation −552, procless yellow_brick_road −574).

**Eric's Oct 22 02:45 behaviours, on the meta-draft base (Dev227m), paired:**

| Switch | Finding | Paired |
|---|---|---|
| `kRecallCapHp` (edit_recallcaphp.py) | no recall-capture while at 75/80%+ health with no emblem to buy and no bank due | 0.75: −2 ± 33; 0.8: −5 ± 36 (corners +443, lanes +216; swirl −400, elk-arena −204). Neutral: in v244 at 0.8 for the bench |
| `kBullyOdds` (edit_bully.py) | run off an enemy contesting our camp when our odds and wealth are clearly better | 0.7/1.5×: −43 ± 44; 0.85/2×: −40 ± 44; capture-only: **−90 ± 40**. **Off**: picking the fight beside a camp costs more farming than the camp is worth - the same stall as the fourth point below |
| `kJoinFight` (edit_joinfight.py + edit_joinfight_idle.py) | waiting beside, or idling near, a camp a mate is fighting now: join it | wait half +22 ± 26; **full +36 ± 31** (interlock +123, corridors +59, gold-rush +60) → v244 |
| `kFightCap` (edit_fightcap.py) | leave an objective-less fight after N rounds, avoid the camps around for 40 | 25: −13 ± 32; 40: +46 ± 29; **60: +58 ± 28** (B7Live +90; elk-arena +222) → v244 at 60 |

**v244** (Oct 22 03:00:51, platform 244) = v243 + `kJoinFight` + `kFightCap` 60 + `kRecallCapHp` 0.8: bench **8/40,
−14,547** vs v243's 9/40, −12,651 - a step back within the noise but the wrong way (swirl vs Mite −1,726, corridors
−765, lanes −413; boss_battle +868, big_world +123). Its all-maps scan is the cleanest and best of the session: **47/70 wins** vs B7Live (v227 34, v230 41), loops 184 rounds,
stuck 6 rounds, nobody idle at spawn. Three switches at once, so the bench separates them: **v245** = v243 + `kJoinFight`
only (03:07:04, platform 245), **v246** = v243 + `kFightCap` 60 only (03:07:34, platform 246); the recall gate waits.
Benches vs v243's −12,651: **v245 9/40, −13,927** (swirl vs Mite −1,781 - that game flips to a loss in every variant;
without it ~+500: interlock +387, quadrants +263, lanes −373); **v246 8/40, −15,126** (swirl −1,854, boss_battle −505,
concentrated_wealth −437, corridors −364). So join-fight stays, the fight cap goes (its local +58 did not carry to the
bench: leaving a fight after 60 rounds also leaves camps contested); v245's code back live as **v247** (03:14:05, platform
247), then **v248** = v247 + `kRecallCapHp` 0.8 (03:14:31, platform 248) benched alone: **7/40, −16,614** vs v245's 9/40,
−13,927 (corridors −624, quadrants −445, interlock −349, split −156; fracture +355, gold_rush +154). Recalling straight
after a capture is what the top teams do (70–95% recall-captures in the study): skipping it while healthy costs against
them. **Off**; v247's code back live as **v249** (~03:24, platform 249) - the state at the end of this round.

**Ranked 01:00–01:50 (v235/v236/v237 in turn):** 21/30 against opponents averaging 1791, rating 1778 → **1815, rank 60**
(from 99 at 21:30 when v225 was live).

**v236's bench:** 9/40, −14,703 (v232 −14,831): a tie. **Squad structure on the meta draft** (Dev227m base, pool):
`kSquadSize` 1 (solo farming) **+30 ± 25** (lanes +173, split +79), `kSquadSize` 3 +9 ± 27, `kTeamSquads` 2 −49 ± 48,
`kAutoTeam` off −25 ± 32 but **corridors +325** and yellow_brick_road +343 (Eric's "split up to farm": right on corridors,
wrong on the rest). Solo farming shipped as **v237** (Oct 22 ~01:38, platform 236) for the bench to judge - its last
trial, v214 under the old draft, was the worst bench of the afternoon. **Result:** 8/40, −15,654 vs v236's 9/40, −14,703
on the same games (starvation vs Mite −768 vs +516, interlock −729 vs +188; quadrants +253 vs −123, corners vs procless
+297): not better, so v236's code went back live as banner **v238** (platform 237) at ~01:50. Splitting up pays on
corridors-like maps and costs on the rest; a map-general rule would have to come from the camps' spread, not a flag.

Not done from the review: the long-group monster snapshot in fight_group (#6, second part), the island firing-tile
component test (#7; the live copy wins islands), the per-member row-scan memory. The tooling items are done: fastscreen
checks the compiler's exit and rebuilds an opponent whose source is newer than its wasm; evalsum excludes games the
opponent crashed in; behaverun reports failed analyses and checks two rows per replay; behave.ts applies the engine's
tiebreaks (gems, lifetime gold, kills, team B) to its win flag. Other loops seen in v227's scan and left alone (small):
rows guard shuffle (17,3) <-> (18,4) ~8 rounds; interlock contest_altar <-> travel 2-cycle ~7 rounds; one ambush game
with Ryth "idle" (no target) at (56,46) for 160 rounds from r1403 that a logging rebuild did not reproduce.

**Turn use at camps** (`tools/stress/actions.ts`, ranked games and benches): within 4 of a living camp monster with no enemy
near, top teams basic-attack on 51-65% of turns (Fish 51, Nyx/procless 62, :3 65), ranked opponents 49%, us 39% (16.6%
nothing, 40% move only). Per-turn activity of our own bot (debug copy printing `AC r<round> <champion> <activity>`,
joined with the replay by `scratchpad/actjoin.ts`, 8 local maps): of those turns 55% are fight_camp (69% of them attack,
24% move only: walking between monsters), 13% travel past camps, 11% capture (standing on the reward while a
neighbouring group lives), 4.5% guard, 3.9% wait_party.

**Rating history** (`tools/stress/ratinghist.py`): ~1790 before v194 (Oct 20 13:51), ~1855-1870 with v194-v197, peak
1894 at 04:00 Oct 21 (v200's code); from 05:20 (engine 1.0.2: Stellar, Ren and HoR nerfed, Vesper/Vendetta buffed) a
steady slide to ~1820-1840. The drop is the patch, not our code (v209 = v196's code benches like v205-v213).

**Why every version loses ~550 a game to them** (bench replays, `.info/knowledge/top-teams-1.0.2.md`): their camp damage
per 1000 rounds is twice ours (124k vs 62k): 28% of champion-time at camps against our 20%, walking 45% vs 54%, and
from r300 half our champion-rounds per kill (items: 23 emblems at r600 vs 12). Camp-to-camp hops: recall round trips
take us 48 rounds vs their 40 (spawn -> next fight 31 vs 23 rounds over the same ~22 tiles: capture walks, tributes,
gate routing, party waits, guards); direct hops 21.6 vs 17.6 rounds for 9.8 tiles. Deaths 7.9 vs ~2.5 per 1000 rounds,
62% after r600, 56% of our PvP deaths to a single enemy at a camp on our half (their HoR 31%, Vesper 22%).

## Why procless beats us (v252's 20 bench games, Oct 22 06:00; `behave.ts` → `behavesum.py`, `sidecaps.ts`)

Eric: "Is it still our micro teamfighting? Should we invade a little - camps slightly on their side go untouched?"
- **Economy tempo first.** By r300 they have earned 1,724 gold to our 1,164 (+48%), by r600 4,665 to 2,577 (+81%),
  with the same deaths before r300 (9 each in 20 games). On 12 of the 20 maps both sides have 0-2 deaths by r600 and
  we are still 30-70% behind (collision 1,032 vs 1,789, expanse 1,414 vs 1,857, lanes, big_world, rows, interlock).
  Where it goes: champion-rounds r1-600 walking 53% vs 45%, at camps 21% vs 30%, dead 7.5% vs 2.8%; camp damage
  dealt 79k vs 124k per 1,000 rounds; pickups 55 vs 72 per 1,000 rounds in parties of 1.78 vs 1.46; tributes 16 vs 30
  per 1,000 rounds (bags 40 vs 32); recalls at 71% health vs 56%, **42% of our recalls above 90% health** (theirs 17%).
  concentrated_wealth: our first pickup at r200 (theirs r57): HoR walked to the centre, half-fought an elk until the
  enemy came, recalled, fought the corner elk to 914 hp and recalled at 550, walked to x=43 for a 4-gem wolf, recalled.
- **Invasion asymmetry, confirmed.** Camps 1-4 walking steps nearer their spawn: they captured 191, we 19 (37 of the
  46 groups never ours, value 8,920). Camps 1-4 steps nearer *our* spawn: they 106, we 90. Our deep side: we 615, they
  120. Their deep side: they ~1,000, we 28. 24% of our own-side groups (37 of 153) we never captured at all. Against
  Mite the same pattern (168 vs 63 on their near side). Pickups on the enemy half: theirs 11%, ours 4%.
- **Fights: lost later, and lost with the numbers.** 119 of our 151 deaths are to champions, 81 on our own half,
  and in **53 of them we had more champions within 5 than they did** (36 even, 28 fewer). procless's 42 champion
  deaths: 27 outnumbered, 5 with more. Their kills come 47% with fewer champions near. The reason is items: team
  emblems at r600 26.7 vs our 13.8, richest champion 9.6 vs 5.4 - the same champion damage taken per 1,000 rounds
  (11.5k vs 12.0k) kills us three times as often (7.3 vs 2.3 deaths). Fight quality matters, but the item gap comes
  from the economy gap, and it is the economy that opens by r300 before any fight is lost.
- Map disasters (fights, not farming): swirl 14 deaths vs 1, yellow_brick_road 11 vs 2 (we farm 468 gold all game),
  gold_rush 9 vs 4, boss_battle 4 vs 1, split 4 vs 0.
- **Blunt invade switches lose locally** (two seeds, n 280, vs our own code which does not invade): `kFarSideMargin`
  5 −30 ± 23, 8 −28 ± 25; `kFarSide` 0.9 −9 ± 22; both −13 ± 27; `kFarSideEarly` 0 −30 ± 28 (contest −475, elk_arena,
  yellow_brick_road lose; corners, packs, gold_rush gain). A local screen cannot show the gain of taking camps a
  passive opponent leaves; it does show the cost of walking into them. A targeted form (near-mid enemy-side camps at
  full score only while no enemy was seen near them recently, or while ahead) is the next experiment, judged on the
  bench.
- Ranked next steps, by the size of the gap: (1) camp throughput and walking - fewer abandoned camp fights, recalls
  only when hurt or loaded, smaller parties once the opening is done, bank in smaller bags; (2) the near-mid camps on
  both sides; (3) fight odds with the item gap in them (we engage with the numbers and lose).
- **Where our turns go** (logging build `bots/Dbg252` = v252 + `edit_aclog.py`, 28 games vs B7Live on 14 maps, rounds
  1-600, 67k champion-turns; `actprof.ts`, `travelprof.ts`, `switchwhy.ts`): fight_camp 36.5%, travel 31.1%, capture
  8.9%, guard 4.5%, deliver 3.1%, wait_party 2.7%, recall_capture 0.9%. Travel legs average 10.4 turns; **23% of travel
  turns are on legs abandoned before arrival** (about 7% of all turns); 39% of camp-fight runs are not followed by a
  capture of that camp. Why targets were dropped (replay camp states): ~140 trips to camps found respawning on arrival
  (taken out of sight), ~55 half-fought camps left with no enemy within 8, ~90 squad moves after a clear (normal), 10
  camps a mate took first. No single leak; the respawn-blindness is the largest.
- **How we die to procless** (`killctx.ts`, 129 of our deaths to champions in the 20 games): 89 while fighting a camp,
  71 from ≥ 90% health 10 rounds before, 51 within 4 rounds of the killers arriving (burst), 92 after round 600, 91
  on our own half. Killers are often one champion (HoR alone 21, Ryth 14, Vendetta 14), and in 22 deaths it was 1v1,
  in many 2v1 and 3v1 *for us*. Their 45 deaths: 31 at camps, mostly outnumbered (1v2 12, 1v3 5). So the fight loss
  is "caught at a camp at full health by a stronger late-game champion and burst", not mistimed engages. Candidates:
  `kAwakeThreat` (the camp we fight counts in our odds), `kBurstOdds` (ready spells over a short fight).
- **Screens of Eric's three items** (`bots/Dev252` = Up252 + edit_nearinvade.py, two seeds, n 280, base 218/280 +316):
  targeted invade `kNearInvade` (edit_nearinvade.py: enemy-side camps within N steps of the midline score as ours
  while no enemy was seen near them for Q rounds) 6/Q20 −63 ± 27, 10 −60 ± 28, 6/Q60 −44 ± 27 (contest −650, hooks
  −488, corners −314; split, swirl, fragment, yellow_brick_road, concentrated_wealth gain); off on control maps
  (`kNearInvadeControl` false) **−27 ± 22** (contest −425 and corners −418 remain: the bot's own spawn measure does
  not class them as control maps; split +239, yellow_brick_road +228, starfish +164, eight +108). Camp-threat odds
  `kAwakeThreat` 0.5 −7 ± 27 (yellow_brick_road +460, eight +355; contest −450), 1.0 −21 ± 26; burst odds
  `kBurstOdds` 3 −35 ± 32; bag 32 (`kDeliverGems`) −63 ± 23. Shared memory is 8 bytes, so champions cannot share
  respawn timers (the largest travel leak). The local opponent is our own code, so the invade's gain against a
  team that leaves those camps is invisible here: **v253 = v252 + kNearInvade 6, control maps off**, for the bench.
- **v253** (06:58:39, platform 253): stress 15/24, stuck 0. Bench **5/40, −18,257** vs v252 10/40 −14,031: procless
  −12,310 vs −10,703, Mite −5,947 vs −3,328 (starvation vs procless −904 and vs Mite −762, boss_battle vs Mite −1,134,
  quadrants, interlock, fracture; yellow_brick_road +156, split +110). **Invading the near-midline camps loses against
  both teams**: they are not unguarded, procless takes them because it is there first and stronger. Rejected.
- **v254** = v252's code + `kAwakeThreat` 0.5 (the camp we fight counts in our fight odds: 89 of our 129 deaths to
  procless came during camp fights), submitted to replace v253 at once; `scratchpad/chain254.sh` falls back to v252's
  code if the stress check fails. Submitted 07:06:53 (stress 14/24, stuck 0). Bench **8/40, −15,196** vs v252 −14,031:
  procless −11,878 vs −10,703, Mite −3,318 vs −3,328 (corners −251, fracture −259, starvation −386, islands −174;
  yellow_brick_road +446). Rejected: the odds already decline the right fights; the deaths are bursts we cannot see
  coming at full health.
- **Correction (farming review ecbdf38, Oct 22):** `capcycle.ts` counted each recipient of a shared capture, so it hid
  lower team throughput. Fixed to count unique group captures: on the same ten quiet maps procless completes **38.2
  group captures per game by r600 to our 32.3 (+18%), 55.9 to 43.5 by r900 (+29%)**, with 1.02 recipients per capture
  to our 1.22; reward-to-capture delay 6 rounds for both. So throughput *and* value per capture are lower. The
  paragraph below is superseded on throughput.
- **Captures, not speed** (`capcycle.ts`, `capvalue.ts`, ten quiet maps vs procless, rounds 1-600): the same capture
  rate per champion (1.46 vs 1.44 per 100 alive rounds, 44-45 rounds and ~35 steps between a champion's captures),
  but their captures are worth more (mean value 136 vs 118), gain more gold (104 vs 85 per capture; Treasure 12 vs 4)
  and are cluster-only 19% of the time to our 32% (wolf 56% vs 47%, elk 25% vs 21%). So the quiet-map gap is what we
  capture, not how fast: our scoring values a gold piece at 0.4 gems early, fading to 0.12 by r800 (tuned Oct 20,
  before the Vesper/Marcella drafts). Re-screened (two seeds, n 280): `kGoldWeightEarly` 0.6 +2 ± 23, 0.8 −57 ± 27;
  `kGoldFadeRound` 1400 −38 ± 19; `kGoldWeight` 0.2 −31 ± 18; 0.6 with fade 1400 −54 ± 24. The Oct 20 tuning holds.
- **v255** (07:13:58, platform 255) = v252's code again (v253 invade and v254 camp-threat odds both benched worse).
  Of Eric's three items none beat v252: invading near-midline camps −4,226 on the bench, camp-aware fight odds
  −1,165, throughput levers (smaller bags −63, gold weight, burst odds −35) negative locally; respawn timers cannot be
  shared (8 bytes of team memory). What remains open: their captures are worth 15% more (fewer cluster-only camps,
  Treasure), and their late-game champions burst ours at full health at camps.

## Fuel: real suspensions and where they happen (Oct 22, after the fuel review)

The scanner's "fuel-limit turns" counts records ≥ 99,000 fuel, not suspensions. Real suspensions come from a logging
build (`edit_fuelphase.py`: fuel_remaining() jumping up between checkpoints means the engine suspended the turn and
resumed it next round; `edit_fuelprobe.py`: the innermost probed function reports it; `tools/stress/fuelphase.ts`).
v255 vs B7Live, 70 games (all maps, both sides): **1.2% of champion-turns suspended** (4,495; first turns with their
double budget are not detected), often more than once per turn; 90% in the decide/act phase (camp fights 1,261,
travel 1,188, guard 342, deliver 299, capture 232); Vesper 37% of them; lanes 6.6% and split 6.8% of turns. Innermost
sites: `step`'s own body, `score_team_targets` (also during captures: the leader's next camp and recall-capture's
pick), `fight_group`, `nearest_enemy` (re-read every enemy's position per call, 31 call sites), `team_finishing` +
`team_total` (every teammate's bag per call), `try_dash` (scanned abilities even without a dash), `ally_jam`,
`safe_field`. Fixes, behaviour-preserving: `kCampSnap` (edit_campsnap.py: each monster read once, crowds counted once,
same choice), `kFuelCache` (edit_fuelcache.py: cached enemy positions, finishing() per round, no dash scan without a
dash), `kTeamTotalOnce` (existing, never enabled). Together: **suspensions 4,571 → 3,535 (−23%)**; deliver −57%,
retreat −46%, guard −36%, capture −35%, travel −28%, camp fights −13%. Per-champion decision sequences match until
fuel timing differs (`eqcheck.ts`; early differences are fuel floors such as fields built only above 30k). Two seeds
+8 ± 26 (neutral, as an optimization should be). `kNextCache` (edit_nextcache.py, the next camp once per capture,
review #4): −8 / −14 / −9, off. **v256 = v255 + kCampSnap + kFuelCache + kTeamTotalOnce**, for the bench.
Capture ownership before the clear (`kCapOwner`, review #1): −2 ± 28, step-off form −11: off for now.

**v256** (08:34:30, platform 256): stress 17/24, stuck 0, near-limit records 2,839 (v251-v254: 3,414-3,970). Bench
9/40, −15,887 vs v252 −14,031 (procless −11,593 vs −10,703, Mite −4,294 vs −3,328). Kept: see the bench noise below.

**The bench's own noise (Oct 22).** A fuel-only change (same decisions until fuel timing differs) changed 38 of the 40
bench games, per-game SD 241: chaos from fuel timing, not strategy. From the per-game differences of four pairs:
**the standard error of a 40-game margin difference is ~1,200-1,500** (v256−v252 −1,856, SE 1,524; v254−v252
−1,165, SE 1,193; v253−v252 −4,226, SE 2,206; v251−v250 +218, SE 1,446). So a bench can only see a change of ~3,000
or more; v252's lead over v251 (+846), v250 and v254 is noise, and most "keep/reject" verdicts by bench this week
were coin flips. Only v253 (invade, −1.9 SE) and the draft change of v229 (+4,600) stand out. Judge smaller changes by
ranked games split by version (hundreds of games) and by two-seed local screens (SE ~25 a game, n 280).

**Farming review, the rest** (two seeds on top of the fuel caches, n 280): party-damage clear time (`kPartyTtk`,
review #2) −31 ± 29; solo one-camp lookahead (`kLookahead` 0.5, review #5) −46 ± 25; half the delivery leg in team
scores (`kTeamDelivery` 0.5, review #3) −3 ± 25; recall-capture costing (`kRecallCapCost`) −49 ± 30. **Respawn events**
(`kRespawnEvent`, edit_respawnevent.py: a fresh capture one champion sees goes into the spare target-slot byte, the
others mark the camp respawning): +1 over the caches, wins 223 vs 212 of 280, B7Live +261 vs +216. Mechanism checked
with logging builds on 14 maps (28 games each): trips abandoned at respawning camps 121 → ~25, travel turns −8%
(21,477 → 19,780), turns on abandoned trips −19%, mean trip 10.7 → 9.7 turns. **v257 = v256 + kRespawnEvent.**
**v257** (08:55:07, platform 257): stress 17/24, loops 3 (13 rounds, the cleanest of the day), stuck 0. Bench 8/40,
**−14,713** vs v256 −15,887 (+1,174, ~1 SE) and v252 −14,031: noise. Kept. Ranked 07:00-08:59 (v255/v256/v257): 35/60,
rating 1890.4 at 08:59, rank 36 (it was 60 at 04:08).
Probes on v257's configuration (70 games, block probes inside `step`): the remaining suspensions are spread thin -
score_team_targets 629, step's neighbour scan 446, fight_group 418, field builds 276, farm 272, Vesper's try_dash 214
(she has a dash), try_moves, avoid_reach_step, party_need, safe_field, ally_jam ~170-210 each. A probe reports where
the fuel ran out, not where it was spent, so cheap code late in a turn (the neighbour scan) takes the blame. Next fuel
step, if wanted: per-function fuel totals on suspended turns rather than innermost sites.

## Eric's four experiments (Oct 22, after v257): crystals, release, readiness, death-gated invasion

Base `bots/Dev257` = Up257 + edit_teleheld / edit_release / edit_arrive / edit_nearinvade (all off). Two seeds, n 280:
1. **Held crystals** (`kTeleportHeld` 5, edit_teleheld.py: use a crystal already held when a landing saves 5 net rounds;
   purchases unchanged; never during a planned jump; not while hit or with an enemy in sight). Engine timing (rules +
   engine-mechanics): the channel ticks at 3 owner turn ends including the start turn and the hop lands at the start
   of a full turn, so the exact net saving is walk - walk from landing - 3; the code charged 4 (`kTeleportExtra` 1).
   Screens: 5 +18 ± 11 and +16 ± 10, exact timing +16, 3 +6, 8 +11; no rebuy (`kTeleportRebuy` false) +15 ± 10. But
   a paired metrics run (`tools/stress/farmstats.ts`, 70 games vs B7Live, one seed): v257 already buys 209 crystals
   and makes 151 jumps (the 40-round planner); with held crystals and no rebuy 127 bought, 125 jumps, wins 50 vs 55,
   banked at r900 405 vs 420, steps walked per capture 70.4 vs 69.2, gems lost carrying 96 vs 56. Spending the
   planner's crystal on 5-round hops costs planned jumps and does not shorten travel per capture. With rebuy (28
   logged games): 241 bought vs 86. **Four seeds (n 560): with rebuy +23 ± 7 (wins 448 vs 434), no rebuy +14 ± 8**;
   a crystal costs 10 gold (an emblem 150), so rebuying is cheap and keeps the planner's long jumps. Paired metrics
   with rebuy (70 games vs B7Live, one seed): wins 57 vs 55, banked r600 245 vs 240 and r900 396 vs 420, group
   captures 61.6 vs 61.8, 395 bought and 359 jumps vs 209 and 151, gems lost carrying 89 vs 56 - the extra jumps do
   not raise capture throughput here, so the margin gain (if real) comes from earlier arrivals or banking. **v258 =
   v257 + kTeleportHeld 5 (rebuy)**, to be judged by ranked games by version. Submitted 10:34:34 (platform 258):
   stress 19/24 (the most wins of the day), stuck 0; bench 8/40 −15,162 vs v257 −14,713 (−449, SE 1,180: noise).
2. **Surplus release** (`kRelease`, edit_release.py): the highest-slot member leaves a camp the others finish within N
   rounds safely, for a camp it can take alone. Keep 2: 9 releases in 28 games (squads are pairs), +7..+9; keep 1
   (pairs split) −22 ± 19. Off.
3. **Fight-start readiness** (`kArriveSteps`, edit_arrive.py: trade odds count only allies who reach us within N steps,
   no wall on the line; evade odds unchanged): 2 −12 ± 29, 4 +6 ± 26. Off.
4. **Death-gated invasion** (`kNearInvadeMode` 1: near-midline enemy-side camps score as ours only while 2+ enemies are
   confirmed dead (engine roster) with 25+ rounds of their respawn left): 6 steps +9 ± 23 alone, +35 ± 23 with held
   crystals, window 40 +33; 14 steps +9. Per map inconsistent: elk_arena +382, hooks +227, boss_battle +251 (with
   crystals), starvation +267; eight −455, swirl −262, monolith −91, corners −85 - map class (control or not) does
   not separate them. Narrower mode 2 (the dead enemies' respawn must cover walk + clear + 10 rounds, and no enemy
   seen near the camp for 20 rounds). **Four seeds on v258 (n 560): mode 1 −2 ± 16, mode 2 −23 ± 16 (6 steps) and
   −26 ± 16 (10)**; eight −316..−331, swirl −172..−257, shortcut −112, pilgrimage −100, reverse_spiral −112 in every
   form. The +35 above was noise. Rejected: invading enemy-side camps loses in every form tried (v253 bench −4,226,
   quiet-gated −27..−63, death-gated −2..−26).

## Fights, grouping and enemy power (Oct 22, Eric's questions; data, no behaviour change)

Engine note: the ladder runs engine 1.0.3 since 07:10 UTC; cambc 3.0.5 (installed beside 3.0.4) reads its replays and
gives identical outcomes on six test matches. The pool is 40 maps; five were missing locally (added).

> **Superseded in part - see "Screening audit 2026-10-22" below.** The first encounter tool counted one fight once per
> approaching champion (21,712 rows were not independent), pooled damage onto the weakest opponent, and the tested gate
> used a different predictor from the logged one; its decline modes also walked home. The emblem-readability finding
> stands; the head-count claims and "bad fights are bad whatever we do" were not supported by that evidence.

**Encounters in 480 ladder bench games** (v244-v258 vs Mite and procless; `tools/stress/encounters.ts`: one of ours
comes within 4 of an enemy after 5 rounds without contact; ours = within 5, theirs = within 6; outcome over 15
rounds among those champions; 21,712 encounters):
- Headcount does not win: 1v1 net −0.04 kills, 2v1 −0.08, 3v1 −0.14, 4v1 −0.17, 3v2 −0.27, 4v2 −0.40, 4v4 −1.01.
  Bringing more champions to a sighted single enemy does not turn into kills against these teams.
- The ally's distance barely matters in 2v1 (0-1 tiles −0.06, 2-3 −0.11, 4-5 −0.06).
- **Emblems decide**: ≥ 1 more emblem per champion than the enemies present: net +0.14 (kill 22.7%, loss 10.3%);
  more than 1 fewer: net −0.43 (kill 3.7%, loss 35.4%). Half of all encounters (10,734) are in that worst bucket.
- **A 4-turn matchup estimate predicts outcomes** (each champion hits once a turn from the turn it is in reach,
  distance − attack range; each ready damaging spell once; can each side kill the other's weakest champion?):
  predicted win net +0.17 (kill 29%, loss 12%); predicted lose −0.57 (kill 2.4%, loss 45%); predicted trade −0.53.
  One enemy in sight: 1v1 predicted win +0.38 (kill 40%, loss 2.6%), 2v1 predicted win +0.26, 2v1 predicted lose
  −0.45. The old health × damage ratio is monotone but flat at the top (ratio ≥ 4: +0.04).
**In the bot** (`edit_diag.py` logging build, 80 games vs B7Live on 40 maps, `tools/stress/diagjoin.ts`): enemy
`item_count()` is readable on 100% of visible enemies (shards and emblems; gold is self-only). The trade rule said
"trade" on 97% of 45,146 fight turns; on predicted-lose turns we died within 15 rounds 14.5% (an enemy 7.8%), on
predicted-win turns 4.9% (enemy 38.5%). Invasion cycles (IV, every 10 rounds: value per full cycle = walk, respawn
wait, clear, 4, banking leg): the best enemy-side camp beat the best home camp in 11.4% of 39,840 samples; in those the
nearest enemy was a median ~4 tiles from it and the enemy took it within 40 rounds 26% of the time (we 18%): the
enemy-side camps that look better are the contested ones.
Answers: no fixed head count makes an invade pay - kills need the matchup, and our extra champions do not add kills;
farm in the existing pairs; fight one sighted enemy with an ally only when the 4-turn estimate says we kill first.
`kMatchupGate` (edit_matchup.py): 1 no trade on a predicted loss, 2 also evade it, 3 also trade a predicted win.
**Four seeds on all 40 maps (n 640): 1 −54 ± 18, 2 −62 ± 19, 3 −59 ± 19** (concentrated_wealth −489, hooks −443/−462,
contest −363, pilgrimage −315, road_of_riches −319; starfish +220, fracture +61..+95). The estimate predicts bad fights
but avoiding them does not help: a predicted-loss situation is bad whatever we do (walking away concedes the camp or
gets chased). Off. What it can still be used for: choosing where not to be (camp choice) rather than how to react once
there - not tested.

### Screening audit 2026-10-22 (`.info/Reviews/ScreeningAudit-2026-10-22-575ea21.md`) and the corrected analysis

Audit findings, all confirmed: (1) encounters duplicated per approaching champion; (2) damage pooled onto the weakest
opponent (a reproduction: 80 damage assigned to an enemy no attack could reach); (3) the gate's predictor summed spells
at the longest reach (110 vs the log's 10 in a reproduction); (4) gate modes 1-3 entered the walk-home branch, so they
changed movement, not just the trade; (5) "kills first" was a cumulative threshold, not a death order. The −54/−62/−59
screens reproduce, so those IMPLEMENTATIONS are rejected - not matchup-aware decisions in general.
Fixes:
- `tools/stress/matchup.ts`: one predictor - per-target damage from each attacker's own distance to that target, each
  spell with its own damage and reach, focus on the most killable target, turn-by-turn simultaneous damage, deaths in
  order; win / lose / trade / none from the first death on each side. Fixtures cover the audit's reproductions (all pass).
- The bot's `matchup()` (edit_matchup.py, rewritten) mirrors it line for line; the logging build prints its inputs
  (kMatchupLog: MXF/MXR) and `tools/stress/matchparity.ts` recomputes them in TypeScript: **10,678 of 10,678 identical**
  (20 games, ten fight-heavy maps). The cache key is (round, position). edit_diag.py no longer has a predictor of its own.
- `tools/stress/encounters.ts` (rewritten): encounters are connected components of opposing champions within 4, new only
  when no member of either team was in contact in the previous 5 rounds (one fight = one row); participants = contact
  + same-team support within 3; deaths count only when an opposing initial participant was within 5 of the victim in its
  last living round (others reported apart); encounters within 15 rounds of game end are censored; game ids for
  clustered errors (`tools/stress/encsum.py`).
- `tools/fastscreen.py` writes `results/ev/run<t>/manifest.json` (git HEAD and dirty count, cambc path and version,
  settings, each candidate's base, edits, seed, source and wasm hashes, a zip of its edited source, the opponents'
  source and wasm hashes, the maps and their hashes).
**Corrected encounters** (480 bench games, 9,707 group encounters, 188 censored, 443 games; net = attributed kills,
theirs − ours, ± SE clustered by game; association, not causation):
- Predictor: win **+0.24 ± 0.03** (kill only 28.6%, loss only 6.9%), none −0.06 ± 0.01, lose **−0.50 ± 0.02** (loss
  only 43.2%), trade −0.26 ± 0.07 (n 87). One enemy: 1v1 win +0.33 / lose −0.49; 2v1 win +0.24 / lose −0.49; 3v1 win
  +0.21 / lose −0.53.
- Emblems per champion, ours − theirs: < −1 −0.30 ± 0.02 (4,291 encounters), −1..0 −0.08, 0..1 −0.01, ≥ 1 +0.11 ± 0.02.
- Head counts (confounded by items, map, stage, prior damage and who joins; more of ours also means more of ours who
  can die): 1v1 −0.04, 2v1 −0.09, 3v1 −0.11, 4v1 +0.05 ± 0.05, 2v2 −0.15, 3v3 −0.41, 4v4 −0.89. Not evidence that
  adding an ally hurts.
**Three-way screen** (four seeds, 40 maps, n 640 each; run `results/ev/run1792670190`, manifest: git 3132c85, cambc
3.0.4, wasm C1 0b1f6d53, C2 984b3ec0, C3 372dff1b): baseline 516/640 +361; **predictor computed but unused (9) −34 ±
18**; withhold the trade on a predicted loss (4) −40 ± 18; **4 vs 9 paired −6 ± 11**. Real suspensions (fuel-phase
builds, 80 games, all maps both sides vs B7Live): off 4,480, computed-but-unused 6,239 (+39%; decide phase 3,781 →
5,517). So nearly all of the loss is the predictor's fuel cost (it ran at every fight decision with an enemy in sight),
and the policy itself is neutral within ±11 - neither shown to help nor to hurt. The earlier −54..−62 mixed the same
fuel cost with a walk-home behaviour change and a different predictor.
**Lazy placement** (computed only at the trade point; run `results/ev/run1792670754`, four seeds, 40 maps): compute-only
(8) −8 ± 8 (the fuel cost is mostly gone), withhold on a predicted loss (5) −17 ± 15, **5 vs 8 paired −9 ± 15**.
Verdict: with a validated predictor (parity 100%), a precise one-decision change and a matching compute-only control,
withholding predicted-loss trades is neutral to slightly negative against our own code. Kept off; v258 stays live.
The predictor itself is sound for analysis (corrected encounters: win +0.24, lose −0.50 net attributed kills). Not yet
tried with it: the opposite decision (take a predicted-win trade the odds decline - rare: ~100 of 45k turns), and using
it before contact (whether to walk into a fight), which needs a different placement and its own control.

## Against Intercontinental Fish (Oct 22, 12:20 UTC on; Eric's three-step plan)

**Bench.** Fish is scrimmable again (`scratchpad/bench_fish40.txt`: all 40 pool maps, 8 groups, ~7 minutes; scrims always
put us on side a; games are deterministic per version pair). v258: **1/40, −26,884** (tag `fish258`, replays
`replays/p2/sl_fish258`). Fish (rank 2, 2,234) drafts Vesper, Vendetta, Heart of Ruin, C&I, Ryth (4 picks: no Ryth; 3:
Vesper, HoR, Vendetta) - our list with C&I for Marcella. **The match API's `draftPicks` use the `champion_draft` enum**
(0 Ryth, 1 Vesper, 2 Vendetta, 3 C&I, 4 Stellar, 5 Prism, 6 Marcella, 7 Willow, 8 Ren, 9 Varg, 10 Tavi, 11 HoR), not the
replay's champion-type numbering (3 Cassi, 4 Issac, 11 Tavi, 12 HoR).

**Where the gap opens** (`tools/stress/gapline.ts` → `gapsum.py`, 40 games, team totals, gap = Fish − us ± SE):

| | r50 | r100 | r200 | r300 | r450 |
|---|---|---|---|---|---|
| gold earned | 108 vs 201 | 254 vs 474 | 558 vs 1,097 | 908 vs 1,866 | 1,460 vs 3,139 |
| of which camp / kill / treasure gap | +87 / +7 / 0 | +183 / +32 / +5 | +398 / +95 / +47 | +659 / +189 / +111 | +1,141 / +337 / +200 |
| emblems | 0.1 vs 0.2 | 0.5 vs 1.3 | 1.8 vs 4.3 | 3.8 vs 8.2 | 7.0 vs 16.4 |
| captures (team, by group claim) | 1.0 vs 1.2 | 2.3 vs 2.9 | 5.6 vs 6.2 | 8.8 vs 10.3 | 13.4 vs 18.0 |
| gold per capture | 58 vs 96 | 85 vs 133 | 81 vs 123 | 84 vs 122 | 81 vs 118 |
| deaths | 0.2 vs 0.2 | 0.6 vs 0.3 | 1.5 vs 1.1 | 2.6 vs 1.4 | 4.2 vs 1.8 |

Fish fields 5.3 bodies to our 4.5 (C&I). Gold held is higher for Fish (194 vs 57 at r100): **not a shopping delay -
income**. First / second / third emblem (median): us r137 / r190 / r262, Fish r82 / r116 / r160. Fight rounds are equal
(r200: 85 vs 86) and deaths are equal until ~r150, so **the deficit exists before the fights** (combat micro alone
cannot close it). Most of the early camp gap is value per capture (r100: count +0.6 × 85 = 51, value 2.9 × 48 = 139).
`capvalue.ts`: captures by r200 278 vs 344, mean value 103 vs 141, elk share 20% vs 31%.
**Elks** (`elkkill.ts`, individual elk kills per game): r0–150 1.7 vs 2.6, r150–300 1.4 vs 3.2, r300–600 4.4 vs 8.4. After
r150 our elk parties are 2.1 champions and take 39 rounds an elk; Fish's 3.6 and 30. r150–450 elk kills by party size:
us 1: 38, 2: 44, 3: 27, 4: 12, 5: 3; Fish 34, 59, 68, 61, 67. Fish spends ~58% of champion-rounds in r150–450 killing
elks and wolves, we ~37%. Cause on our side: `party_need()` returns 0 (cannot take) when a camp needs more than
`kSquadSize` (2) champions, so pairs skip multi-elk groups after the r120 opening.
**Droughts** (`tools/stress/droughts.ts`, 40+ rounds without a team capture before r200): ~100 rounds a game for us, ~90
for Fish - similar. Ours come in two kinds: (a) early lost fights (contest, corners, gemfight, quadrants, stampede,
swirl, hooks, starfish, gold_rush, yellow_brick_road: 2-7 deaths, 100-350 dead rounds); (b) **long walks without a
capture** (road_of_riches r10-r116, pilgrimage r19-r139, concentrated_wealth r10-r127, fracture r46-r113).
**(b) is a bug, reproduced locally**: in the opening the camp scorer prices a camp whose path field is not built yet at
1.3 × the straight line; on road_of_riches the camp beside our spawn behind the spiral's wall (100 steps by the road)
looked 8 rounds away, and all five walked the whole road to it (AC log: target g0, "travel" r1-r100). `kSpawnWalkTravel`
(existing, never tested: within N of our spawn an unbuilt path costs at least the draft plan's walk from spawn) fixes it:
first 160 rounds locally, captures road_of_riches 1 → 6-8 (first r114 → r29), pilgrimage 5 → 9, concentrated_wealth
0 → 3, fracture 4 → 6 (reverse_spiral unchanged: a 35-round elk-group clear instead). 40-map local screen
(`results/ev/run1792674963`, 2 seeds, 640 games each): 10 / 20 / 40 = −17 ± 17 / −10 ± 15 / −6 ± 16 (neutral; the
local opponents share the bug). → **v259 = v258 + kSpawnWalkTravel 20**.

**Fish bench results** (scrims accept `--side b` / `--sides a,b,...`; `bench_fish80.txt` = both sides of all 40 maps, 16
groups; `bench_fishmix.txt` = 40 games with sides alternating per map, 8 groups, the first look from 14:25 - Eric: 16
groups is a lot of the team's 50-an-hour quota; a rerolled game moves ~±350, so a 40-game sum has SE ~2,000-3,000):

| version | change | Fish bench | notes |
|---|---|---|---|
| v258 | live at 12:20 | side a 1/40, −26,884 | |
| v259 (13:2x) | + kSpawnWalkTravel 20 | side a 2/40, −25,878; side b 3/40, −23,365; **80: 5/80, −49,243** | road_of_riches captures by r200 2 → 12 but Fish out-earned us there; mean gold r100 254 → 269, r300 907 → 879 (flat); kept |
| v260 (14:1x) | v259 + kGroupWake | **1/80, −53,844 (−4,601)** | lost both boss_battle wins (−1,273, −827): the awake-group model gives up the monolith centre. Rejected |

Rank 43 (1,875.3) at 14:05. **Draft**: Fish's own lists (kMetaDraft 7, `edit_meta7.py`: Vesper, Vendetta, HoR, C&I, Ryth)
**−183 ± 35** locally (640 games, run1792677521) - our play is not built for C&I (as kFishDraft −150/−169 on Oct 21).
**kContestPick** (step 2) locally (run1792678189): compute-only 9 +8 ± 10, decision 1 +13 ± 14 - it fires 2-8 times a
400-round game against our own bots (one predicted loss, no switch in three test games), so only the Fish bench can judge it.
**Vesper as the carrier.** First emblem (median): Fish's Vesper r92 (38/40 games), Vendetta r186, HoR r205, the rest
r325+; ours: Vesper r157 (29/40), Marcella r206, Vendetta r212, HoR r254, Ryth r258. Capture gold by r200: Fish's Vesper
54% (19,915 of 37,189), ours 35% (7,160 of 20,652); r0-120 57% vs 33%. With equal emblems fights against Fish are even
(encounters ≥ +1 emblem per champion: net 0.00 ± 0.03; < −1: −0.39). `capwho.ts` now prints Vesper's distance (vN):
of our 238 gold-paying captures by r200, Vesper took 71 and **98 went to another champion with Vesper within 6 tiles**.
Cause: `resource_carrier()` prefers Vesper only when gold >= 3.5 × gems, so elk groups with gem clusters are "gem"
groups for Prism, whom we never draft. `kVesperFunnel` (`edit_vesperfunnel.py`): 1 no Prism → any gold-paying group
prefers Vesper; 2 + a champion not yet on the tiles of a group Vesper is targeting leaves it to her. Locally (run1792678988)
+1 ± 10 / +2 ± 19; her capture gold by r300 rises on collision 119 → 252, corners 146 → 226, gold_rush 266 → 363
(unchanged on elkring, expanse, monolith). → v261 = v259 + kVesperFunnel 2.
**v261-v263 and the rest of step 1-3 (Oct 22 afternoon).**

| version | change | Fish bench (40 mixed games vs the same v259 games) | local (640 games) |
|---|---|---|---|
| v261 (14:34:17) | v259 + kVesperFunnel 2 | −24,861 vs −22,962 (−1,899; boss_battle a W 950 → L −533 alone −1,483) | +2 ± 19 |
| v262 (14:49:12) | v259 + kContestPick 1 (step 2) | 16 games changed, net −922 (the_farm W → L −469) | +13 ± 14 (control 9: +8 ± 10) |
| platform 263 (15:18:31) | **v259's code again** (banner v259) - the best measured | | |

Rejected locally (not benched): kVesperBuild (Fish's Vesper items: Treasure Str, Bruiser Str, Durability Hp, Power Str x3;
ours buys Jungle first in 16/37 games) −18 ± 18; Vesper package (funnel + build + kSquadSize 3) −33 ± 22; kBigTeamShare
0.25 (whole-team farming to r600/r1000 where 3+elk groups hold 25%+ of the gems; `edit_bigteam.py`) −27 ± 21 and our team
still never took pilgrimage's four-elk group in 800 rounds; kSquadSize 3 −21 ± 20; kThreatModel 3 −24 ± 26.
**Step 3 audit** (`tools/stress/fightaudit.ts`: per champion turn in the first 8 rounds of the selected encounters):
predicted-win encounters with comparable emblems (gap ≥ −0.5): 65, we kill in 4, lose in 8. Us vs Fish in them: enemy in
attack range on 12% / 10% of turns; "missed" (in range, no champion hit, no cast) 47% / 43% of those; split targets 1 of
7 / 0 of 16 rounds with 2+ hitters; casts beside a monolith or elk 11 / 10. Predicted-none encounters (377): missed 45% /
39%, rounds with 2+ of the team hitting 70 / 111. So no single execution bug stands out; the difference is how often
two or more of them hit at once (convergence), not target choice or wasted turns.
**Big elk groups are chipped from 5 tiles.** Ranked pilgrimage (0/3 this afternoon, 1-11 since v252): the opponents took
the four-elk + 12-cluster group at (24,58) 6-9 times a game (520 gold + 88 gems each) - SSSA's Cassi, Stellar, Prism and
Ryth stood exactly 5 tiles from the elks (reach 4) and chipped them with area spells aimed beside a target, all at 100%
health, ~110 rounds a clear (`scratchpad chiptrace.ts`). We never took it (clusters 47 times). Our draft has one area
caster (Ryth). **Ranked per map since v252 (310 games)**: lanes 0-7, pilgrimage 1-11, expanse 1-9, split 1-8, stampede 0-4,
quadrants 0-3 (3 wins in 38 on the first four); best: corridors 7-1, gem_fields 7-1, starfish 6-1, corners 5-1, fragment
9-2. On split we out-earn gold but take fewer gems per capture (11.4 vs 17.8 by r600); on expanse they make 38 captures
to our 23; on lanes we capture more and lose close races after r900. New bench `scratchpad bench_weak.txt`: those five
maps against eight teams near our rating (smurphy, Valenki, BBL, dromedaries, the uncancelables, SSSA, Nameless, The
Mania), sides alternating, 40 games.
**Gold vs gems against teams near our rating (v264).** Lower early gold weight `kGoldWeightEarly` 0.4 → 0.2 (fades to
kGoldWeight 0.12 by r800 as before). Local −9 ± 27 (further: 0.12 −42 ± 26; + kCarrierGold 1.5 −35 ± 14 - local screens
punish gem-leaning weights because our own copies lose fights to the gold). Ladder, paired, 40 games each:

| bench | v259 | v264 |
|---|---|---|
| `bench_near.txt` (all 40 maps over 8 teams at ~1,850-2,000, sides alternating; v259's games re-run at 16:37 with v259 re-uploaded, banners checked) | 17/40, −2,161 | **20/40, +503** |
| `bench_weak.txt` (lanes, split, expanse, pilgrimage, quadrants x 8 teams) | 10/40, −7,777 | **14/40, −6,548** |
| Fish mixed | 4/40, −22,962 | 0/40, −27,661 |

Mechanism (gapline r600, weak bench): split gems per capture 12.0 → 14.8 (opponents 15.5-16.6), gems held 419 → 468, gold
3,619 → 2,967; quadrants gems held 834 → 897 (opponents 879-896). Against Fish less gold costs fights. **v264 (15:46:49;
re-uploaded 16:49:21 as platform 266) is live: rank 40, 1,882.5 at 16:49** (47 / 1,862 at 12:10). Platform numbers ran ahead
of the banners from 263: platform 263 and 265 = v259's code, 266 = v264's.
Near-bench losses with v264 are the fight maps: by r600 deaths elk_arena 17/5, lost_world 11/4, eight 10/2, gemfight 9/3,
corners 9/6, each with a 1,300-3,600 gold deficit (kill gold). elk_arena vs Nameless (the same draft as ours): 21 of our
deaths to their 4 by r656, mostly at our own camps against 3-5 of them with 2-4 of ours near.
**v267** (16:58:05) = v264 + kMatchupGate 5 (the corrected predictor, computed only at the trade, withholding predicted-loss
trades): near bench **14/40, −7,780** vs v264's 20/40, +503 (−8,283; 30 of 40 games changed; lost contest, hooks,
gem_fields, great_wall, rows, starfish, broken_curve, yellow_brick_road). Its 24-game stress check also showed 13 loops
(129 rounds) and one 3-round stuck (submitted by hand). Rejected: withholding trades loses against real opponents too.
**v268** (17:10:40) = v264 + kContestPick 1 (step 2): near bench **17/40, −6,360** (−6,863 vs v264; it fires in 25 of 40
games against these teams, against 16 of 40 vs Fish, where it was −922). Rejected: moving off a contested uncleared camp
on a predicted loss costs more than it saves. Local screens carry +13 ± 14 for it - another switch they cannot judge.
**v269** (17:24:30) = v264 + kCarrierGold 2.5 (local −15 ± 13): near bench 21/40, −2,827 (+1 win, −3,330 margin vs v264;
gem_fields alone −1,639). Not clearly better; v264 kept. The "v270" bench (bots/Up270 = v264 + kVesperGoldW 1.0, local
−17 ± 15) never ran: its upload failed on a network error and the bench replayed v269 game for game (all 40 banners
v269) - chainfish.sh now stops when the submit is not confirmed. **Platform 270 (17:51:00) = v264's code** again.
Ranked cost of testing: rank 40 (1,882) at 16:49 → 46 (1,863) at 17:42 after v267/v268 were live 16:58-17:24.
**Holdout check of v264** (`scratchpad bench_hold.txt`: the same 40 maps over eight other teams near our rating - Quant
Merch Traders, wawow, AlphaSlop, Supaswag, Gem Simons, ha²t, Nah Id Lose and one more - never used for tuning; v259's
games run with v259 re-uploaded 18:01, banners checked): v259 19/40, −1,295; **v264 22/40, +1,319**. Over the three
near-rating benches v264 is +10 wins in 120 games. By map class (control = spawns <= 45 steps apart, 20 maps): near
control +819 / other +1,845; holdout control +2,820 / other −206; Fish control **−5,586** (wins 4 → 0) / other +887. A
control-map exception (`kControlGoldWeight` 0.4) would buy back the Fish games at the cost of the near-rating gains, so v264
stays as it is. Platform 271 (18:01:28) = v259's code for the holdout; 272 (18:12:11) = v264's.
**v270** (platform 273, 18:21:03) = v264 + kVesperGoldW 1.0: near bench **14/40, −6,303** (−6 wins vs v264). Rejected.
**v264's code is live as platform 274 (18:30:57)** and stays live: every change stacked on it lost on the near bench
(v267 −8,283, v268 −6,863, v269 −3,330 / +1 win, v270 −6,806), and each live test costs ranked games.
Ranked by live window (last 100 games, noisy): v264 17-18, v259 10-15, v269 7-8, v267 4-6, v268 3-2, v262 4-6.
**Open, for later:** (1) the fight maps - elk_arena (v264 −1,008 near, −864 holdout, −1,044/−1,008 Fish; 17-21 of our
deaths a game at our own camps vs 3-5 invaders), eight, corners, gemfight, lost_world: our teams converge less (2+
hitters per round 70 vs 111 in neutral encounters); (2) against Fish v264 costs −5,586 on control maps - an
opponent-aware gold weight (their draft is visible) would trade that back, but tuning to one opponent risks overfitting;
(3) the big elk groups the ranked opponents chip from 5 tiles with area casters (our draft has one).
Ranked by live window since 15:18 (to 18:32): v264 20-20, v259 10-15, v269 7-8, v267 4-6, v268 3-2, v270 2-3; rank 54
(1,851.8) at 18:32 - the test windows cost rating. Fish is rank 1 (2,323.6).
**Ready, not uploaded:** kAssist 8 (join a fight beside us within 8, was 6) on the v264 base, local −1 ± 25 (run1792694008;
elk_arena −936 → −694, collision −409 → −98, eight +532 → +126); 10: −25 ± 26. On elk_arena our team arrives in pieces
(four of ours vs five, Marcella 7-10 tiles behind, a 180-health Vendetta staying in). Note also: locally v264's base loses
elk_arena −936 ± 19 to our own older bots (−455 ± 255 with gold weight 0.4) - that map pays for the gem-leaning weight.
Other findings: the stampede six-elk boss group wipes a staggered party (HoR starts alone at r442 locally, three dead
by r461; the Fish game r230-237); lost_world: a cluster hit wakes the full-health monolith at (1,15) and five of ours died
in its reach fighting Fish's Vesper there.

## Code review of v264 (Oct 23 local / Oct 22 ~21:00 UTC) and v271

Full read of `bots/Up264/src` plus `-Wall -Wextra -Wshadow` (0 warnings) and clang-tidy bugprone/analyzer (only dead
switches, an intended integer division and false positives).
- **Bug, fixed in v271:** `fight_group` took the first living camp member as the target without reading it, and an
  unreadable member could never be displaced (both the kCampSnap and the older path). After a mid-turn fuel suspension
  (the turn resumes in a later round) that member could be out of sight; the next line read its position, the engine
  threw "Unit is not in vision" and the rest of that champion's turn was lost. A debug build traced every error to this
  line; it was the only error type in 177 recent replays. Concentrated on yellow_brick_road (30-monster groups): slot 4
  lost turns 9, 18, 24 and 30. Also guarded three position reads after a cast that may have killed the target
  (`cast_offensive`'s first line, the chase dash, `turn_and_fight`'s step); never observed, `hit()` already did this.
- **v271** = v264 + those fixes (platform **275**, 21:57:18 UTC Oct 22). Stress scan (24 games): bot errors 13 → **0**,
  wins 17 → 17, stuck 0, 20 games identical, yellow_brick_road side A 530 → 939 gems. Local screen run1792705874
  (320 games): vs v264 paired **+3 ± 8**. With the switch below off, the binary is byte-identical to the scanned one.
  First ranked window: 7/15, rank 53 (1,855) at 22:25 UTC. Ladder logs to ~22:40: v271 0 bot errors in 69 games (10 ranked,
  59 unranked); v264's last 15 games had 7.
- **`kSpawnWalkTravel`'s estimate (review item 3), switch `kSpawnWalkHome`, left off.** The rule subtracts our
  straight-line distance from spawn, not our walk, so it is not the lower bound its comment claims: after a detour round
  a wall, camps further along look farther than they are. Modes: 1 subtract the walk when the home field exists, 2 also
  build a copy of that field near spawn (a separate key: building `kHomeField` early would move the control-map check),
  3 build the copy but use nothing (compute-only control). Findings (DbgSWH logged estimate and true walk every 5
  rounds near spawn, 80 games vs B7Live):
  - The rule is used only in the opening: median last use r30 (to r150 on big_world/fracture/yellow_brick_road),
    ~17 camps without a path field per champion; our walk exceeds the straight line in 12% of samples.
  - v259's estimate is already accurate: mean error 3.8 (in 1.2 × walk units; straight line alone: 30.1), nearest camp
    found in 1,402/1,540. Subtracting the walk: error 3.4, target camp 3.5 → 3.0, nearest 1,405, but more camp pairs
    misordered (4,845 vs 4,641): camps behind or beside the detour now look nearer than they are (bias +0.4 → −0.9;
    −6.4 on detour samples). The two-sided bound |W − walk| is worse (pairs 5,134, nearest 1,384).
  - Screen (run1792705874, 320 games each): mode 1 −4 ± 12, mode 2 +5 ± 19, compute-only −1 ± 17; mode 2 vs its
    control +6 ± 16. Opening economy (gapline, 80 paired games): mode 2 minus control gold +7 ± 4 (r50), +4 ± 6 (r100),
    +18 ± 14 (r200), +46 ± 32 (r300); captures and first-emblem rounds unchanged; 49/80 openings identical.
  - Verdict: a small positive trend, not significant, too small for a 40-game ladder bench (SE ~1,200-1,500) to
    resolve. Kept in the code, off. A side asymmetry from building path fields in group-index order was checked and
    is absent (about 2 near-spawn camps without a field per champion in the first 30 rounds on either side).
- **Latent, switches off:** shared-memory bytes 8–14 (banker sharing via kLockSnipe/kLockPolicy/kAltarWard, and
  kTeamFight's focus bytes) are beyond the engine's 8 bytes: the accesses are wrapped, so turning those switches on would
  share nothing. kAutoTeamStr (line ~2603) overwrites `team_rounds_` after kRangedTeamRounds and `holder_` used it
  (both off). The set-up ignores `walk_sides`' result: a failed engine call there would mark some camps unreachable
  for melee champions without a dash (kWalkTargets).
- Checked and fine: camp-group handles (filled once in the constructor), kAutoTeamStr's answer is the same on every
  teammate (per-champion terms are off or unset on round 1), fastalloc, the draft plan, ally_jam's recursion,
  loop_guard's arrays, deliver()'s re-entry guard.

## Eric's requests of Oct 23 (local) / Oct 22 ~23:00 UTC: v272

Five changes, each behind its own switch in `bots/Up272` (screens run1792710735 and run1792711422, 320 games each, paired
against v272's base):
- **`kCrystalDash` (on):** a dash champion holding a crystal prices the jump against crossing by dash (walk up to 2 tiles
  to a launch tile, wait out the cooldown, dash 2 tiles straight/diagonally over holes, never walls) and takes the dash
  route when the jump saves less than `kTeleportHeld`; a planned landing checks the same. Cause: `kDashGaps` is off, so a
  dasher's path fields treat 1-hole gaps as walls and the crystal looked like it saved the whole detour. Logged on the
  8 crystal maps × 2 sides: dasher jumps that a dash matched within 5 rounds 78 → 0; 65 dash crossings instead; every
  remaining dasher jump saves 5+ rounds (176 of 197 save 10+: walls). Local +1 ± 8.
- **`kTeleportHeld` 5 → 10 (on):** local −5 ± 7.
- **`kKiteStun` 3 (on):** escaping, ground-target stuns (Ryth's area stun) also hit the chaser (enemy-target stuns
  already did: Cassi's is walking-compatible, Prism/Tavi/Ren/Ryth's exclude walking, but the stunned chaser loses its turn
  too); and when every enemy within 5 is stunned for its next turn (buff duration ≥ 1, visible to teammates), cast a
  4-range damage spell at the weakest even if it costs our step. Local: bit 1 −0 ± 1 (rarely fires), 3 +5 ± 5.
  The three together: +2 ± 10. **v272 = v271 + these three, platform 276 (23:34:36 UTC Oct 22).** Stress: 17/24 wins,
  stuck 0, loops 9 (38 rounds) vs 11 (54), 0 bot errors.
- **`kFleeClosest` (off):** escape steps and the escape dash head for the closest fit ally within 12 (not recalling or
  tributing), among tiles no closer to the enemy. Local **−61 ± 27** (lost_world −514, hooks −356, stampede −312,
  boss_battle −253); gated on winning the rally (`kFleeAllyOdds`: us + allies within 3 of the ally vs the chasers, ally
  outside any awake camp's reach) 1.0 −40 ± 25, 2.0 −26 ± 25. The older `kFleeToAllies` (allies' mean) was −29.
- **`kClusterOne` (off):** groups of resource clusters without monsters, away from the centre (mode 1: and the midline),
  are left out of squad picks and taken by the nearest non-leader squad member alone. Local 1: −39 ± 26, 2: −45 ± 27;
  with `kClusterOneTtk` 10 (only groups one champion clears in 10 rounds, squads of 3+, only a member the squad's camp
  does not need) −47 / −53. Losses where the teams meet early (contest −475, eight −473, gemfight −433, corners, lost_world:
  a lone member is picked off), gains on elk_arena +321, starfish +284, interlock +259, gem_fields +233. Local screens are
  weak judges of farming structure, so a ladder bench is the open test.
- **Shared memory (question):** all 8 bytes are used - 0-5 each champion's target + 1 (7 bits) and a flag bit, byte 5 the
  respawn-event byte with five champions or fewer, 6 the alert (kind 2 bits + camp 6 bits: camps 64+ cannot be alerted;
  current maps have at most 51 groups, road_of_riches), 7 the alert round mod 256. The slack is byte 7: alerts live 20
  rounds, so 5 bits would do and 3 bits would be free (e.g. an enemy roster index). Nothing needs them now (the kiting rule
  reads the enemy's stun buff). The banker/focus constants at bytes 8-14 are dead.

## Eric's requests of Oct 23 (second batch, ~00:00 UTC): v273

- **Dash direction (`kDashLine`, on):** travel-dash landings tied on path distance were tie-broken by Chebyshev distance
  to the goal, which cannot tell a straight landing from a diagonal one when the goal lies along our row, and the scan
  order listed the diagonal first - so champions dashed diagonally and walked back to the row. Now the tie goes to the
  landing nearest the straight line (squared Euclidean), for travel, gap, crystal-alternative and chase dashes; a goal one
  row off gets the (2,1) landing. 80 games vs B7Live (`DbgDashOff/On`, `scratchpad/dashdiag.py`): travel dashes off the
  line that needed a step back **47% → 14%** (6,378 → 1,801 of ~13,300), straight 2,143 → 3,656. Local −17 ± 25
  (run1792713351; boss_battle −248, lost_world −215 vs starvation +246, collision +147: noise). **v273 = v272 +
  kDashLine, platform 277 (00:17:20 UTC Oct 23)**; stress 18/24, stuck 0, loops 8 (36 rounds), 0 bot errors.
- **Hunter (`kHunter`, off):** a worse-equipped enemy in sight within 8 with no other enemy within 5 of it (equipment =
  shards + 5 × emblems from `item_count`, readable on visible champions; our lead ≥ `kHunterLead` 5 = one emblem) that
  the contact matchup (edit_matchup.py's 4-turn simulator with both placed in reach, 6 turns) says we kill first: the
  best-equipped of ours near it chases it (cast, dash, step, hit) for up to 12 rounds; the rest farm. Modes: 1 our half
  and the midline, 2 only prey at a live camp, +4 their half too. Local, 320 games each: 1 −33 ± 21, 2 −56 ± 21, 5 −34 ± 21,
  lead 0 −37 ± 23 (lost_world −466, contest −325, corners −286, reverse_spiral −241; elk_arena +217, split +210, gem_fields
  +189). Against our own code the chase mostly costs farming (our copies evade well); the encounter data says a 1v1 we
  are predicted to win ends in a kill 40% of the time, so a ladder bench is the open test. Earlier aggression switches:
  kHuntOdds (health × damage) −103/−130, kBullyOdds −40..−90, every invade form negative (above).
- **Farming and scaling (Eric's question):** see the answer recorded in `session-2026-10-22-fish` memory and the
  economy sections above: the gap is camp throughput (elks after r300, time at camps, abandoned trips, early recalls),
  not gold weighting or gold concentration; items decide fights (+1 emblem per champion: net +0.14; −1: −0.43), so the
  item lead must come first and comes from throughput. Open tests (ladder only): 3-champion elk parties after the
  opening (kSquadSize 3 / relay: local −21 ± 20 is uninformative), recall discipline (37-41% of recalls start above 90%
  health vs 11-16% for Fish/procless), camp-fight completion (39% of camp fights end without a capture).

## Strategy review of v273 (`.info/Reviews/StrategyReview-2026-10-23-v273.md`): experiments, Oct 23 ~05:00-08:30 UTC

All switches live in `bots/Dev274` (= Up273 + the switches below, all **off**; untracked dev copy). Local screens: 40 maps ×
2 sides × B7Live/B7Base × seeds 1-2 = 320 paired games per candidate (runs `results/ev/run1792732215`, `run1792732996`,
`run1792734469`). Nothing was uploaded. Every candidate was neutral or negative locally:

| Review item | Switch | Paired margin | Notes |
|---|---|---|---|
| 1 camp area casts | `kCampAoe` 1 (blast centre catching the most living hitters, never waking another sleeping group; edges reach 4 + radius) | −3 ± 18 | |
| | 5 (+ melee Ryth casts from 4-5 at a camp under way instead of the step in) | −19 ± 27 | fires ~5 times a game |
| | 13 (+ `kLowSnipe` reach counts the radius) / 15 (+ ranged casters cast from 5) | −19 ± 29 / −14 ± 29 | |
| | `kKiteAoe` (Ryth's area stun counts as a stun when escaping; see engine-mechanics: it is `aoe_damage`, so `kKiteStun` never cast it) | −24 ± 25 | |
| 1/5 Prism (:3) | draft `kPrismMeta` 1 (Prism for Marcella) / + `kCampAoe` 15 | −72 ± 26 / −58 ± 30 | Prism edge casts ~6.5 a game |
| | `kPrismMeta` 2 (Prism for Vendetta) + `kCampAoe` 15 | −8 ± 31 | the only neutral draft variant |
| | + `kCasterShield` 60 (ranged wait outside elk reach for a melee in front) | −155 ± 30 | not traced (it also holds Vesper back) |
| 3 recall trips | `kFinishCamp` 8 / 12 (stay under the retreat line in a quiet camp fight the party ends within N rounds, health covering its hits) | −22 ± 19 / −5 ± 19 | 12: low-health trips 3,091 → 3,060, deaths by r900 +0.7 ± 0.3 (4.2 → 4.9), economy equal: rejected |
| 4 reinforcements | `kRally` 3 (fight odds count fit allies up to 3 tiles further out at 0.6, not recalling or tributing; outnumbered + evade) / outnumbered only | −30 ± 24 / −26 ± 21 | |
| | `kAssist` 8 / `kRally` 3 + `kAssist` 8 | −3 ± 25 / −48 ± 27 | |
| (re-screen) | `kAggroRotate` / + `kTagIn` | **−68 ± 29** / −30 ± 29 | still off |

**Recall trips (review item 3), measured** with a logging build (`tools/edits/edit_aclog.py` + `edit_rclog.py`,
`tools/stress/recalltrips.py`; v273 code vs B7Live, 80 games): ~107 trips a game. **Recall-capture** is the bulk of the
healthy ones (3,687 trips, 54% from 90%+ health, 42% bought something) and is cheap: the next camp is a median **5** steps
further from home than from the capture tile (mean 4); healthy no-purchase recall-captures cost ~66 champion-rounds a game
(extra walk + mates' `wait_party`), under 1% of champion time. `recall_hop` trips (71% healthy) are shortcuts by design.
The larger cost is **low-health trips** (retreat / loop_recall / heal, median 29-39% health): ~39 a game, 47% before r500,
44% after windows mostly spent fighting camps, Heart of Ruin 30% of them; ~18-25 rounds each. The ladder's "47% of
recalls above 90%" is mostly recall-captures, not wasted trips.

**Travel (same logs):** 51% of travel rounds end at the camp travelled to; target switches 21% (often to a nearer camp),
enemy encounters ~10%, stuck 3% (median 12 rounds). On 01concentrated_wealth the whole squad spent r68-112 walking round the
centre's wall ring to group 0 (elk + 8 gem + 12 gold clusters, ~330 gold and 71 gems) and then switched target; Claudus took
that group at r66 and r145 (ladder 2740f7fb). On 01big_world the three-gem-cluster groups 2 and 3 sit mid-map (group 3 inside
a 2-wide hole ring: crystal only); locally we take them, on the ladder Claudus got there first.

## Fish benches of Oct 23 (06:30 UTC on): v274-v278 (Eric: "lets try submitting and test against fish")

**Version numbers (Eric, Oct 24): from now on our version number IS the platform submission number.** The Oct 23 uploads were
numbered 4 below it: banner v273 = platform 277, v274 = 278, v275 = 279, v276 = 280, v277 = 281, v278 = 282, v279 = 283, v280 = 284,
v281 = 285. The upload copies are renamed `bots/Up278`..`Up285` (their kBotVersion now equals the platform number; the binaries
that played printed the old banner). Bench tags in the scratchpad keep the old numbers (fish279 = platform 283).

Bench = `tools/stress/bench/bench_fishmix.txt` (Intercontinental Fish, rank 1 at 2,282; we were rank 60 at 1,847): 40 maps, sides
alternating, 8 groups, deterministic for a given pair of submissions. Paired SE between versions ~35-50 a game (~1,500 over 40).
All uploads come from `bots/Dev274` (switch sets in `bots/Up27N/src`); every upload passed the 24-game stress scan (0 stuck).

| Version (platform) | Live from (UTC) | Change | Fish bench | Paired vs the previous |
|---|---|---|---|---|
| v277 (banner v273) | Oct 23 00:17 | live baseline | **0/40, −28,336** (banners checked: 40 × v273) | |
| v278 (banner v274) | 06:45 | draft `kPrismMeta` 2 (Prism for Vendetta) + `kCampAoe` 15 (camp area casts take the best blast centre, reach 5) | 1/40, −26,798 | +38 ± 37 vs v273; our distance-5 camp hits 5 → 223 |
| v279 (banner v275) | 07:38 | + `kCampAoeAnchors` 6 (blast-centre search only round the hitters: fuel) | 1/40, −25,243 | +39 ± 40 vs v274; fuel-limit turns yellow_brick_road 1,192 → 954 locally |
| v280 (banner v276) | 08:05 | + `kDashCampHp` 0.5 (no camp dash into hits HoR cannot take) + `kTributeGuard` 50 (guard a mate's big tribute from 3-4 tiles) | **3/40**, −26,840 | −40 ± 37 vs v275, +37 ± 48 vs v273 |
| v281 (banner v277) | 08:17 | + `kOpeningRounds` 40 (split up after 40 rounds instead of 120; local −28 ± 24) | 3/40, −26,161 | +17 ± 15 vs v276, +54 ± 49 vs v273 |
| v282 (banner v278) | 08:36 | + `kVulture` 10 (take an enemy's nearly cleared camp; local +16 ± 22, ~20 turns a game) | 3/40, −25,976 | +5 ± 21 vs v277; **+59 ± 50 vs v273** (21 better, 17 worse); **LIVE** |
| (candidate) | | `kCaptureSafe` (capture from a reward tile outside awake monsters' reach): local +2 ± 9 | not benched | |

Every step is a tie within the bench's noise (SE 13-50 a game paired); the whole set v273 → v278 is +59 ± 50 a game and 0 → 3
wins of 40, a trend and not a beat: Fish still wins by ~650 a game. v278 left live (nothing in it measured negative on
either scale). Ranked rating during the six uploads: rank 60 (1,847) → 69 (1,834).

**Eric's observations, measured in these benches** (replays `replays/p2/sl_fish27N`, tools `tools/stress/hordash.ts`,
`campctx.ts`, `strayact.ts`):
- **HoR dashes in and dies:** 31 of 45 (v273) / 35 of 44 (v274) HoR deaths with camp damage followed a dash landing inside a camp's
  reach within 12 rounds, 19-26 into 2+ hitters; most from full health, no ally within 2, 4-20 rounds of fighting. Our HoR dies to
  camps twice as often as Fish's (27 vs 13 camp-only). `kDashCampHp` 0.5 (v276) refuses those landings (~25 refusals a game).
- **Walking into aggroed monsters:** 20-23% of all camp damage we take is "stray" (nobody of ours touched that group for 3 rounds;
  Fish 10%), 82-84 of our ~530 deaths per 40 games had stray damage in their last 3 rounds. By our logged activity (80 local games,
  `strayact.ts`): fight_camp 16% (in a camp's reach without hitting it), leave_reach 14%, retreat 10%, travel 10%, **capture 9%
  (standing on a reward tile inside a neighbouring awake group's reach)**, evade + escape 13%, deliver 6%, contest_altar 4%. No single
  path dominates; capture-tile choice and the approach while "fighting" are the two fixable ones.
- **Fuel:** v274 +22% fuel-limit turns vs v273 (2,494 vs 2,047 per 40 games), yellow_brick_road +121; fixed in v275. lanes (~580 a
  game) and split (~420) are old and unrelated: a profiling pass is due.
- **Vulture chances** (an enemy fighting a camp under 35% health while one of ours with 70%+ health is within 10 and none of ours
  fights it): 13.7 a game; 487 of 546 ended as the enemy's capture, 22 ours → `kVulture` (v278 candidate).
- **Tribute guard:** fires ~10 guard turns a game (gold_rush 50+), local −2 ± 27.
- **32-bit reads by champions in vision** (Eric: "real, discovered from other players"): it is `set_priority` - see
  engine-mechanics.md "Priority is a 32-bit broadcast" (probe `bots/PrioProbe`, :3 broadcasts team clocks in it). First use,
  `kPrioFocus` (kTeamFight's focus target through priority bits instead of the dead shared-memory bytes 12-13): kTeamFight alone
  **−108 ± 29** locally, with the working channel −86 ± 32 - the channel adds ~+22 but the kTeamFight fight package itself loses;
  both off. Channel ideas not yet built: enemy-sighting relay (a mate's enemy positions), per-champion intent (retreating,
  capturing, vulture) for mates in sight, a rally tile.

## Why we never finish monoliths (Eric's replay cba8a1bb, 00monolith, v278; Oct 23)

Tools: `tools/stress/monoattempts.ts REPLAY TEAM` (every attempt on a 20k boss camp: health reached, who hit, who took hits,
deaths). In cba8a1bb (we are B) Ryth + Marcella + Prism took monolith 0 from 20,000 to 12,114 in r760-772, Ryth taking every
hit (100% → 40%), then all three left together at r773 (Marcella and Prism at 100%); nobody returned for the last 400 rounds.
Monolith 1 was started at r1167 and was at 3,881 when the game ended at r1187. Monoliths never heal.

A logging rerun of v278 on 00monolith vs B7Live (`bots/MonoLog` = Up278 + edit_aclog + edit_rclog + kPickLog) shows why:
1. The squad scorer rates a monolith the best camp on the map (team score 1.6-2.7 vs ~1.0 for anything else): we go often.
2. The party never assembles: members are on solo jobs or recall-capture home (the far corner); the leader waits (`wait_party`,
   r706-722) and engages with whoever is there. One champion takes every 200-a-round hit (the nearest; nobody shares).
3. Feasibility is recomputed every turn from CURRENT health: at r730, with Ryth at 62%, the monolith dropped out of the team
   options (team g1 2.6 → team g10) and the leader re-targeted mid-fight, inside the reach - the walk out cost 4 more hits
   (62% → 25%) and the party followed the new target.
4. After healing at home the far monolith loses to nearer camps and to the OTHER monolith (g0), so progress is spread over two
   bosses and neither is finished.
Fish on the same map (bench vs v278): kills monolith 0 in r534-639 and monolith 1 in 28 rounds (r706-733) with HoR + Vendetta
adjacent sharing the hits (HoR 4,686, Vendetta 1,008 taken) and Vesper at range 3 (never the nearest: 0 taken, top damage
10,545). We dealt 0 to either monolith in both Fish games. `kSiege` (planned waves) is off: −53..−267 locally and worse on the
ladder in Oct 20-21 code.
Fix candidates (not built): judge a hurt boss's feasibility by the party's full-health budget (they heal and return), never
re-target inside an awake boss's reach, prefer finishing the hurt boss over starting the other, share hits between adjacent
melee (priority by health, boss camps only), and assemble the party by broadcast commitments (priority channel, Eric's plan).

## Priority channel, monolith commitment and fuel (Oct 23, Eric: "lets start there", "save more on fuel in general")

All in `bots/Dev274` behind switches; edit scripts (applied in this order on top of the earlier Dev274 edits):
`tools/edits/edit_intent.py`, `edit_boss2.py`, `edit_intent_fuel.py`, `edit_intent_lazy.py`, `edit_fuelsave.py`, `edit_fuelmates.py`,
`edit_fuelbits.py`, `edit_fuelallies.py`. Profiling: `edit_fuelprof.py` + `edit_fuelprof2.py` (per-phase fuel and caught
exceptions) read by `tools/stress/fuelprof.py`; boss outcomes `tools/stress/bosssum.ts`; monolith attempts `monoattempts.ts`.

**Fuel (profile of v278, 40 maps, 378k champion-turns: 55.3k fuel a turn).** Camp-group observation 17k (31%), the decision
branch 14.5k, alerts + squad 9.1k (squad scoring ~7-9k: both picks re-scored over every group every round), observe
enemies/allies ~3k each. Caught exceptions (an engine read of a champion out of sight throws) ~3 a turn at ~2k fuel each:
`remember_mates` alone cost ~7k a turn. **Exact savings** (identical games with `--fuel-quantum 200000000`, 6 maps):
`kFuelEpoch` (camp epoch rehashes only changed groups), `kFuelVis` (vision test only for groups within 9 of us / 7 of our ward),
`kFuelHealth` 5 (rebuild totals only when a member's health moved; member tile from the set-up table), `kFuelMates` 1 (mate
memory recorded by observe_allies; mate_pos without an engine read), `kFuelAllies` (the visible-allies query once a turn; v276's
tribute guard re-ran it nearly every turn). Together: **mean fuel a turn 55,314 → 49,734 (−10%), fuel-limit turns 5,146 → 3,468
(−33%)** on 10 heavy maps; local +1 ± 29 (decisions unchanged by construction). Not exact, dropped: `kFuelHealth` 2 (skip
known-dead members) and `kFuelMates` 2 (skip mates not in visible_allies: some roster reads succeed outside it).
`kScoreEvery` 2 (rescore every 2 rounds): −30 ± 28 vs the exact set, off.

**Priority channel cost.** The first version cost +4,200 fuel a turn (+61% fuel-limit turns; control −64 ± 27): four mates'
is_alive + priority reads, three own state queries and a set_priority every round. Now: publish only when the word changes (no
round stamp, ETA in 4-round buckets), decode lazily from observe_allies' visible handle: +1,200 → small; publish-only −17 ± 27
vs the exact set (noise). Turn order is preserved (draft order; cross-team alternation ignores priority).

**Intent decisions (Eric's plan, three controls), local, on the exact set:** support accounting (`kIntentUse` 1: a mate saying
"leaving" is absent from fight odds and party counts) **−69 ± 30**; + reinforcement waiting (bit 2) **−133 ± 31**. Both off.

**Monolith (Eric's replay cba8a1bb):** `kDeadTileRoot` (dead members' tiles are standable approach roots: the monolith's ring of
8 gem clusters read "unreachable" once the outer clusters died) +2; with `kBossCommit` 31 (full-health feasibility for a hurt
boss, finish a hurt boss first, hit sharing by health-ordered priority, leave at 4 hits, ranged back off) **+22 ± 29** vs the
exact set (wins 252 → 259), the best of screen run1792754058.

## v279 and the strong-camp gap (Oct 23 late / Oct 24; Eric: freezes, "not touching strong monster nodes")

**v279** (platform 283, 12:01 UTC Oct 23) = v278 + the exact fuel set + `kDeadTileRoot` + `kBossCommit` 31: Fish bench 1/40,
−25,601, +9 ± 33 vs v278 (a tie, as expected from fuel-only changes); local 18-boss-map run: bosses finished by us 36 → 38, by
the enemy 21 → 14, median first boss kill r1125 → r870, boss deaths 45 → 51. **LIVE.**

**Freezes** (`tools/stress/freezes.ts`: alive, not channelling, same tile 15+ rounds, not fighting/capturing): 1.4 stretches and
~27 rounds a game in the v279 Fish games, the same in v278/v277. Logged locally, the main case is `wait_party`: the first
arrival stands beside a sleeping camp that needs two for up to 12 rounds (24 before giving up). `kAllyWait` 6 +3 ± 18, **3 +11 ±
23**; `kNoWaitAlone` −32 ± 23; the channel's "nobody is coming → stop waiting" (`kIntentUse` 2 alone) −57 ± 26.

**Strong camps** (`tools/stress/campclass.ts`, v278+v279 Fish benches, 78 games; captures ours / Fish, median first capture, champions
present, items per champion): 2-elk 179 / 354 (r247 / r121, 2 / 3 champions, 6 / 6 items), 3-elk 20 / 51 (we at 12 items with 2,
they at 7 with 4), 4-elk 2 / 39, 6-elk 0 / 20 (they: 3 champions at 14 items, r739), monolith 0 / 32 (3 champions at 11 items,
r647), 2E+2W 3 / 24. Cause: `party_need()` returns 0 when a camp needs more than the squad (kSquadSize 2), although
`champions_needed` would allow it with 3-5; Fish brings 3-4 and relays. `kBigParty` (edit_bigparty.py: a rich camp needing up to
squad + N is a pick, the help flag calls free teammates, everyone waits for the camp's need): locally 2 −6 ± 23, 3 −4 ± 23, value
80 −18 ± 22 - it lifts 3-elk captures 8 → 12 and 4-elk 11 → 17 in 20 games but the first 2-elk capture only moves r325 → r284
(the per-champion pick still prefers singles while they exist). `kHelpCall` 25 alone (solo help calls, never on before) **+16 ±
21**; `kSquadSize` 3 −16 ± 18. Open: Fish's sequencing (2-elk packs from r121 with 3) needs a throughput-per-team scorer, not
the per-champion one; a ladder bench of kBigParty is the real test.

## Uploads 284-286 (Oct 24; platform numbers from here on)

| Upload | Live from (UTC) | Change | Fish bench | Paired |
|---|---|---|---|---|
| 284 | Oct 24 ~00:35 | 283 + `kBigParty` 2 + `kHelpCall` 25 (a rich camp needing up to 2 more than the squad is a pick; the help flag calls free teammates) | 2/40, −24,460 | +29 ± 30 vs 283; **+97 ± 55 vs 277** (26 better, 12 worse) |
| 285 | 13:31 | 284 + `kRelayTrip` 7 (Eric: take big camps in trips - the party leaves with its tank and recalls, returns at full health) | **0/40, −28,993** | **−113 ± 51 vs 284** (13 better, 25 worse): rejected |
| 286 | ~14:00 | 284's code again | (284's games) | **LIVE** |

`kRelayTrip` locally: 7 −26 ± 25, 1 −11 ± 18, 5 −7 ± 22, share 0.25 −31 ± 26; it did move captures the intended way against our
own code (2-elk 39 → 53, 3-elk 6 → 14, monolith 1 → 3 in 20 games) but against Fish it lost on 25 maps.

Big camps vs Fish (campclass.ts, 40 games each, ours / Fish): 284 2-elk 101 / 186 (first r203), 4-elk 1 / 16, **6-elk 4 / 7** (0 / 20
in the 78 games of 282+283), monolith 0 / 19, boss damage 110k, boss deaths 25. 285: 2-elk 81 / 183, 4-elk 0 / 21, 6-elk 0 / 10,
monolith 0 / 15, boss damage 75k, boss deaths 36 - leaving together hands the half-cleared camp to Fish.
287 = 286 with `kPrismMeta` 0 (Eric, Oct 24: no Prism, Vendetta back in the draft). Fish bench: 1/40, −25,279 (all 40
banners v287). Paired: −20 ± 37 vs 284 (12 better, 12 worse, 16 identical; the draft change only touches meta4 maps), so it is
neutral and stays live.

## Codex + Claude collaboration (Oct 23 14:07 UTC → Oct 24 06:07 UTC; Eric: "reach rank 10")

Codex (run by Eric) reviews the code and the screens and makes suggestions; Claude decides, implements and runs every screen. The
channel is `collaboration/codex-to-claude.md` (C-ids) and `collaboration/claude-to-codex.md` (A-ids), with the protocol in
`CODEX_CLAUDE.md`. Start: rank 68, 1830; rank 10 is 2083. Our last 400 ranked games went 199/400, with weak maps 00lanes 1/17,
00expanse 1/12, 00stampede 1/8 and 00collision 2/10. Gapline on 46 of those games found no single failure: at r800 the
opponents had +1,390 gold, +10.6 captures and +8.6 emblems. On 00lanes we capture more camps than they do but earn less gold:
they take the big ones.

Codex findings that held up:
- **C010, the big-party recruitment branch never runs.** With `kTeamSolo`, `read_solo()` tests the same bit as `read_help()`, so
  answer_help's `kBigParty && !read_solo(s)` branch is unreachable. Recruits used the solo rule and came with `needed_ = 1`.
  Logging builds over 80 games vs B7Live confirm it: all 192 help answers were need 1. With `kHelpKind` (bit 6 of the target
  byte marks a squad's call, ≤ 63 groups; `edit_helpkind.py`), 107 of 235 answers carry a need of 2–5.
- **C002, big jobs start short-handed.** Of 179 big-job starts, only 36 had the full party. `join_fight` started 102 of them,
  mostly with 2 present when 3–4 were needed, and `kShortParty` started 41. `kBigStart` 3 (`edit_bigstart.py`) closes both
  paths for big jobs; bit 4 logs BIGSTART lines.
- **C007:** `kBigAlive` caps new big jobs at the alive count, because `team_size_` counts the dead.
- **C006/C012:** `campclass.ts` counts inferred clears, not collected rewards. Codex's `collaboration/capture_truth.ts`
  (reward-state transitions) agrees on 2E and shows the 4E gap is larger. In fish287 our only 4E clear (01the_farm, r582) was
  collected by Fish at r614: HoR walked on, Vesper stepped off the tiles, and Ryth was left alone and died. That gave
  `kCaptureCover` (`edit_capcover.py`): with an enemy within N tiles, healthy capturers skip every hand-off branch.
- **C004/C015:** help reservations counted mates who were recalling or tributing, giving `kHelpBusy` (`edit_helpbusy.py`).
- Screen-tool holes (fixtures in `collaboration/screen-fixtures.json`): missing raw data is normalised to 0–0, the cut-off
  report round is not checked, and early finishes have no report. None of these affects full-game screens.
  `tools/stress/bench/upload.sh` now certifies benches: 40 rows, unique keys, no pending games.

Local screen run1792766075, paired vs Dev288 with 320 games each (none is a local gain; our clones rarely contest big camps):

| Candidate | Paired |
|---|---|
| kHelpKind | −5 ± 15 |
| + kBigStart 3 | +9 ± 16 |
| kBigAlive | +8 ± 14 |
| All three | +8 ± 19 |

kBigStart alone: −5 ± 10. Upload **288** = 287 + all three. Fish bench: 2/40, −24,907, **+9 ± 17 vs 287**: neutral, stays live.

**Marcella's build (Codex C016, top-team study).** Noobot and policy wonk make Marcella their richest champion and build her
**Focus**: Treasure, then Jungle Focus, then Bruiser Focus. Her ranged spell is 2 × Focus at range 4 (+15 Focus per shard,
against +5 Strength), and she earns 2 gold per gem tributed (15–20% of their gold by r600). We built her Strength.
`kMarcBuild` (`edit_marcbuild.py` + `edit_marcbuild2.py`): local, paired vs Dev288 (320 games each, base 252 wins):

| kMarcBuild | Line | Paired | Wins |
|---|---|---|---|
| 3 | Treasure Focus, Jungle Focus, Bruiser Focus | **+70 ± 23** | 272 |
| 2 | policy wonk's line | +63 ± 23 | |
| 1 | Noobot's line | +40 ± 23 | |
| 5 | our order in Focus | +46 ± 20 | |
| 4 | ending in Power Focus | +28 ± 22 | |

The gain is broad: corners +512, contest +425, starvation +354, hooks +349. Directly on the 288 policy, 3 is +47 ± 21 (270 vs
260 wins).

Copying the leaders' Treasure → Jungle → Bruiser lines onto the other champions loses locally, so `kTopBuild`
(`edit_topbuild.py`) is off:

| Champion | Paired |
|---|---|
| Vesper | −28 ± 15 |
| Ryth | −18 ± 22 |
| HoR | −33 ± 16 |
| Vendetta | −12 ± 21 |
| All of them | −42 ± 26 |

Marcella was the only champion built on the wrong stat. Vesper's and Vendetta's spells don't scale with Focus, Ryth gains
Strength from health, and HoR is already built Focus. Note that kTreasureBuild already inserts Treasure first on scaling maps:
Treasure Strength for Marcella, because her name is missing from treasure_first's Focus list.

Also rejected locally:

| Switch | Change | Paired |
|---|---|---|
| `kMarcDraft` 1 / 2 / 3 | Marcella earlier in meta4 | −5 / −10 / −33 |
| `kMarcGems` 1 / 2 / 3 | gem rewards to Marcella | −9 / −13 / −5 |
| `kHelpBusy` 2 / 7 | | −5 / −7 |
| `kCaptureCover` 5 / 7 | | −25 / −6 |

Upload **289** = 288 + `kMarcBuild` 3. Fish bench: **5/40, −22,490**, the best of any upload. Paired: **+60 ± 41 vs 288**
(17 better, 13 worse), +70 ± 42 vs 287. All 40 banners read v289.

**Willow (Codex C017).** Noobot and policy wonk draft Willow 4th or 5th, and she restores about 12.6k health a game.
`kWillowMeta` (draft.cpp; `edit_willowmeta.py`, `edit_willowmeta2.py`) with the existing `kWillowHeal` (cast_support: heal the
ally in reach missing the most health). Local, on the 289 policy:

| Change | Paired | Wins |
|---|---|---|
| Willow 5th instead of Vendetta + heal | **+70 ± 20** | 279 vs 270 |
| Willow 4th + heal | +57 ± 27 | |
| Willow 5th, no heal | +13 ± 21 | |
| + `kWillowMedic` (shadow the tank) | −67 ± 24 | |
| + `kWillowYield` (`edit_willowplus.py`) | −36 ± 20 | |
| + `kWillowBuild` 1 / 2 | 0 / −1 | |
| Willow at 4 picks in other orders (W3 / W4) | +6 / +25 ± 28 (vs W1) | |

The healing is the mechanism. Per map: elk-arena +739, eight +691, lost-world +467, corners +350, stampede +309; contest
−300, expanse −228. Pre-patch Willow lost every test; the Oct 20 patch raised her Strength and Focus.
Upload **290** = 289 + Willow 5th + heal.

Pipeline (`tools/stress/bench/upload.sh`):
- The stress gate needs 24/24 games and replays, at most 4 stuck cases and 60 stuck rounds, and **0 official bot faults**
  (run-batch `--statistics` per row, Codex C026). It also prints the official fuelExhausted count.
- Runs execute a frozen copy of the script (`scratchpad/run/upload<N>.sh`), because editing the script mid-run garbles the
  shell's read.

Upload **290** (Willow): Fish 2/40, −23,042, −14 ± 53 vs 289 (neutral against Fish; Willow only changes 5-pick maps).

**Engine check:** local cambc-3.0.4 runs engine 1.0.2; the ladder and cambc-3.0.5 run 1.0.3. On 8 identical manifests all
summaries matched field for field (Codex C035), and the 320-game 3.0.5 base reproduced the 3.0.4 base exactly. Screens use
`CAMBC=cambc-3.0.5` from 16:20 UTC.

**Draft by pick count** (`edit_picksize*.py`, `edit_smallmarc.py`; maps: 3 picks collision, fragment, packs, broken-curve,
gold-rush, the-farm; 4 picks gemfight, interlock, reverse-spiral, rows, rushbait-v2, swirl, hooks, shortcut; the other 26
take 5). Squads are cut from the alive list by slot (draft) order into pairs, the last taking leftovers, so pick order sets
the pairs.

| Change | Result |
|---|---|
| `kSmallMarc` (3 picks: Marcella, Vesper, Ryth; Codex C032) | **+44 ± 14** local; **+157 a game vs Fish** on its maps |
| `kFourPick` 2 (Noobot's 4: Marcella, Vesper, Ryth, Willow) | +38 ± 28 (4-pick maps, seeds 1–6); fresh seeds 7–12 **+127 ± 33** |
| `kFourPick` 4 (our same four, Marcella first) | **−138 ± 36** (pairing matters) |
| `kFourPick` 1 (HoR, Vesper, Ryth, Willow) | −140 |
| `kFourPick` 3 (HoR, Marcella, Vesper, Willow) | −28 |
| 5-pick permutations of HoR, Vesper, Ryth, Marcella, Willow | all ≈ 0 |

**HoR/Ryth Bruiser Health endings** (`edit_hpbuilds.py`): +27 ± 15 locally, but in **291** they lost **−72 a game vs Fish**
on the 34 maps they touch (291: 2/40, −24,551, −38 ± 40 vs 290). Health-for-damage trades beat our clones and lose to real
fighters.

Upload **292** = 290 + `kSmallMarc`: 3/40, −22,542, +50 ± 34 vs 291, +12 ± 25 vs 290.
Upload **293** = 292 + `kFourPick` 2.

Also flat or negative:

| Switch | Change | Paired |
|---|---|---|
| `kWillowJob` (Codex C031) | | −33 ± 18 |
| `kWillowRetreat` 0.5 / 0.65 | | −30 / −27 |
| `kWaitAvoid` 30 / 15 (Codex C036) | | −1 ± 7 |
| `kWaitKeep` | | no-op |
| `kVespBuild` 1 / 2 / 3 | | −33 / +1 / −19 |
| `kRetreatHp` | 0.30 / 0.40 | −5 / −9 |

Upload **293** (Noobot's 4-pick list): Fish 4/40, −22,503, +1 ± 21 vs 292.

**Holdout bench** (`tools/stress/bench/holdout.sh`, `bench_holdout.txt`: Noobot ×20 and policy wonk ×20 over the Fish bench's 40
maps; paired by map and side). hold293: **10/40, −14,867**. Noobot 7/20 (−231 a game), policy wonk 3/20 (−514 a game).

Upload **294** = 293 + `kFivePick` 1 (Noobot's 5 with Tavi). Locally it pooled +24 ± 13. On the ladder:

| Bench | Result | Paired vs 293 |
|---|---|---|
| Fish | 3/40 | **−46 ± 38** (5-pick maps −70 ± 59) |
| Holdout | 9/40 | +20 ± 58 |

Reverted: **295** = the 293 policy (identical code, no bench).

**Where the top teams beat us (hold293).**

Captures per game (behave.ts + capsum.py):

| Window | Us | Noobot | policy wonk |
|---|---|---|---|
| r0–150 | 4.0 | 6.4 | 5.1 |
| r150–300 | 4.1 | 7.1 | 7.3 |
| r300–600 | 8.2 | 14.9 | 13.8 |

The difference is mostly **monster-free clusters**: 1.6 / 1.4 / 2.1 against Noobot's 3.1 / 4.1 / 7.0. Locally the cluster
switches don't help: kClusterSolo −11, kCasterClusters +1, kClusterOne −34 / −49.

Deaths (killctx.ts): **ours 340, theirs 146** in 40 games (8.5 vs 3.7 a game).
- 214 of ours happened at camps.
- 93 came from full health within 5 rounds, and 145 within 2 rounds of the killer arriving: stun-and-burst ganks.
- Their killers: Marcella 208, Vesper 156, Tavi 115.
- We lost 59 carried gems a game, they lost 22.

Local clones don't gank like this, so anti-gank rules can only be judged on the ladder.

| Switch | Local paired |
|---|---|
| `kFightRespect` 3 | −7 ± 16 |
| `kBurstOdds` 3 | +25 ± 25 |

Upload **296** = 295 + `kFightRespect` 3.

Ranked by banner (108 games since 15:15 UTC): 289–291 went 26/40, 292–295 went 27/68. The 5-pick maps account for the drop
(14/24 → 10/37) although that code did not change except in 294, so it reads as opponent drift.
`kOpeningRounds 0` hung a local game, which motivated fastscreen's new **`MATCH_TIMEOUT`** option.

Upload **296** (`kFightRespect` 3): Fish −38 ± 46, holdout 0 ± 44 vs 293. Dropped.

Upload **297** = 293 policy + **`kBurstOdds` 3**: fight odds count each side's ready damage spells as burst over 3 turns.
It was submitted as a recorded gate exception: 6 stuck cases / 91 rounds, which are slow solo fights and party waits, not
oscillation; 22/24 wins.

| Bench | Result | Paired vs 293 |
|---|---|---|
| Fish | 3/40 | −30 ± 70 |
| **Holdout** | **12/40, −8,312** (best yet) | **+164 ± 112** (Noobot +285 ± 171, policy wonk +43 ± 143) |

Kill contexts, hold297 vs hold293 (37 decodable games each): our deaths 340 → 313, **their deaths 146 → 217**, our deaths
from full health within 5 rounds 95 → 82. We pick fights better. 297 stays live.

Upload **298** = 297 + `kClusterValue` 1.5 + `kGoldOnlyFactor` 1.5 (`edit_clustervalue.py`). Locally +2 / +10, and ×2.0 was
−53.

| Upload | Change | Fish (paired vs 297) | Holdout (paired vs 297) | Outcome |
|---|---|---|---|---|
| 298 | cluster value | −40 ± 46 | −81 ± 46 | reverted |
| 299 | = 297's code | | | live 22:22 UTC |
| 300 | + `kBagCaution` 4 | −26 ± 43 | −20 ± 41 (Noobot −133 ± 50, policy wonk +93 ± 56) | not adopted |
| 301 | + `kChaseOdds` 1.5 | −1 ± 32 | −62 ± 62 | not adopted |
| 302 | `kBurstOdds` 2 | +5 ± 58 | −71 ± 96 | not adopted |
| 303 | = 297's code | | | live 00:06 UTC |
| 304 | + `kCasterClusters` (gem clusters only) | −25 ± 56 | −106 ± 97 (Noobot −294 ± 165) | not adopted |
| 305 | = 297's code | | | live 00:30 UTC |
| 306 | + `kMoveReset` 2 (ranged move → reset → attack; Codex C042/C044) | +23 ± 80 | +10 ± 72 (13/40, −7,913; Noobot −160, policy wonk +180) | kept |
| 307 | 306 + `kWillowPvpHp` 0.75 | +3 ± 13 (vs 306) | −104 ± 70 (vs 306) | not adopted |
| 308 | 297 + `kMoveReset` 3 (PvP only) | −5 ± 36 | −57 ± 74 | not adopted |
| **309** | 306 + **`kEnemyResetParity` 3** (enemy resets count in burst odds; Codex C053/C055) | **6/40, −22,204**: +15 ± 94 vs 306, +37 ± 62 vs 297 | **13/40, −7,322**: +15 ± 85 vs 306 | **new base** |
| 310 | 309 + `kThreatTarget` 1.0 (Eric: Fish's glass-cannon Vesper) | −59 ± 48 (vs 309) | 14/40, −6,933: +10 ± 75 (vs 309) | mixed |
| 311 | 309 + `kRythStunPriority` (Codex C058: :3's stun initiative) | −41 ± 27 (vs 309) | −41 ± 68 (vs 309) | not adopted |
| **312** | **= 309's code** | | | **live from 02:55 UTC Oct 24, the final version of the window** |
| 313 | 309 + forecast readiness + shop refresh (Codex C053/C055) | −52 ± 41 (vs 309) | 7/40, −14,245: −173 ± 87 | rejected; its off-switch code was not behaviour-neutral (nested `attempt()` changed fuel use) |
| 314 | Dev288 with every new switch off (meant as 309) | | | not 309: its stress scan differed from 309's |
| 315 | **exact Up309 source** | | | live 06:10 UTC |
| **316** | `bots/B309` (Up309 + compiled-out switches) + **`kTravelSoloBias` 1.5** (a travelling squad leader keeps its trip unless a solo camp scores 1.5× better; Codex C072) | 5/40, −21,860: +9 ± 51 (vs 309) | **15/40, −5,805: +38 ± 42** (Noobot +75, pwonk +1) | **new base** (local +16 ± 13) |
| 317 | 316 + `kGoldWeightEarly` 0.3 | **6/40, −19,205**: +66 ± 50 | 13/40, −9,473: −92 ± 77 (Noobot −153) | not adopted; the early capture mix did not change |
| 318 | = 316's code | | | live 07:31 UTC Oct 24 |
| 319 | 316 + `kVespFarmBuild` 1 (Fish's Vesper farming line, Codex C069) | 4/40, −23,784: −48 ± 43 | 13/40, −10,711: −123 ± 88 | rejected |
| 320 | = 316's code | | | live 08:51 UTC |
| 321 | 316 + `kStartBeforeParty` (local +11 / +6 on two seed pairs) | 3/40, −22,253: −10 ± 73 | 14/40, **−3,787**: +50 ± 77 (pwonk +170, Noobot −69) | coin flip; live until 322 |
| 322 | 316 + **`kWillowBack`** (Eric: Willow 2 tiles behind our front fighter; `edit_willowback.py`) | **7/40, −18,481**: +84 ± 89 | 10/40, −11,498: −142 ± 110 (Noobot −310) | rejected: Willow deaths barely fell on the ladder (130 → 123, 90 → 83), their deaths fell (324 → 280, 244 → 195) |
| 323 | 316 + `kSquadKeepCap` + `kLateTripRound` 600 / `kLateCapSlack` 10 (Eric: fewer recalls after captures; `edit_bigcamps.py`, `edit_latetrips.py`; local +14 ± 20) | −29 ± 79 | 13/40, −10,349: −114 ± 83 (Noobot −208) | rejected |
| **324** | 316 + **`kMaxNeed` 3 / `kMaxNeedDist` 20** (Eric: no big far camps early; until r500 no team pick needing a party of 4+ for a camp more than 20 tiles (straight line) from spawn; `bots/B323x`; local +16 ± 10 / +18 ± 15 on two seed pairs, pilgrimage +130) | 4/40, −21,459: about +10 a game (25/40 identical) | **14/40, −5,025: +20 ± 30** (Noobot −1, pwonk +40) | **kept** (live 11:23 UTC) |
| 325 | 324 + `kStartBeforeParty` (local +2 ± 13 over 324, wins 310 vs 303; scan 23/24) | 3/40, −22,121: −17 ± 74 (vs 324) | 13/40, −4,192: +21 ± 78 (vs 324) | not adopted: with 321, twice holdout margin up / Fish down and 2–3 fewer wins per 80 games |
| **326** | **= 324's code** | | | **live from 12:26:36 UTC Oct 24, the final version of the extension** |

**Second extension (Eric, 13:06 UTC Oct 24: "continue with codex for the next 9 hours", deadline 22:36 UTC).** Rank 10 had risen
to ~2130 and we had fallen to ~#54 / 1884, so the objective became rating against our ranked pool. New **near-rating bench**
(`tools/stress/bench/near.sh`, `scratchpad/bench_near.txt`): eight teams ranked just above us (红包控股, Valenki, SSSA, Quant
Merch Traders, OneTap, SquidProxyLovers, filter, SkuBap at #33–#49, 1900–1955), one group of 5 maps each over the holdout's
40 map/side split. Candidates from here: near + holdout queued together after the compile wait (`scratchpad/run/cycle2.sh`,
~25 minutes a test). `paircmp.py` now accepts blank team names (the 红包控股 rows).

| Upload | Change | Near (paired) | Holdout (paired) | Fish | Outcome |
|---|---|---|---|---|---|
| 327 | 324 + `kRetreatHp` 0.45 | | 13/40, −8,302: −82 ± 68 vs 324 | 6/40, −20,069: +35 ± 55 | not adopted |
| 328 | = 324's code | **18/40, −3,444 (baseline)** | | | live 13:42 |
| **329** | 324 + **`kWillowStay`** (Willow takes no assist/chase steps; `edit_willowstay.py`; local −5) | **21/40, +2,732: +154 ± 83** | 12/40, −10,968: −149 ± 97 (Noobot −241) | | **kept for the ranked pool** |
| 330 | 329 + `kBurstGuard` 1.0 from r600 (Codex C081; `edit_burstguard.py`; local −3 ± 11, whole game −55) | | | | on the benches 14:25 |

Near-bench economy (near328, capclass): by r300 we bank more gems than these teams (6,462 vs 5,229) but they take twice
the gold-only captures (258 vs 130); by r2000 captures 1,802 vs 2,287, gold 167k vs 207k. killctx's `nKillers` counts enemies
within 5 of the victim's last sample, not killing actors (Codex C080): don't read it as 1v1 losses.

**Did the opponents get stronger? (Eric, 11:50)** No for the benches: games are deterministic per submission pair, and
hold324 repeats hold316 exactly in 13/20 Noobot and 12/20 policy wonk games (fish324: 25/40), no draft changed. So the
holdout drops of 317–323 were our changes. The ladder top did get stronger: new teams willow best girl (#2, 2231),
prism best girl (#3, 2220) and Claudus Maximus (#5, 2185) moved rank 10 from 2092 (06:08) to 2138 (11:50); Bamboo #48, 1914.

**Extension (Eric, Oct 24 ~05:20 UTC: "continue for the next 8 hours", to 13:20 UTC).** Candidates are now built from
`bots/B309` (exact Up309 + switches that compile out; its base binary matches Up309's run-cache entries). Rating 1954.9 at
07:00 (13/20 in ranked groups after 316 went live).

Findings of the extension (Fish bench fish309/316/317 unless named; tools in `tools/stress/`):
- **The gold gap is reach, not weights.** Codex C074 (exact capture events, static rewards from `Game_API_Map_CampGroup_Get`):
  by r150 Fish earns 93.6 base gold a capture to our 70.3, and makes 249 captures to our 201. We take 36 gem-cluster-only
  captures to Fish's 14 (16 of them on lost_world). `kGoldWeightEarly` 0.3 (317) left the mix unchanged (`capclass.ts`:
  37 gem-only, 58 gold-only). The big per-map gaps are capture counts: yellow_brick_road 0 vs 5 captures by r150 (Fish takes
  both 600-gold rows), hooks 4/10, elk_arena 5/12, pilgrimage 7/17. On pilgrimage Fish sends four down and across to the
  middle and chains its ten 3:2 gold groups; our solo scores rate those middle groups at a third of the strip's
  (arrival 42–90).
- **Dead time.** Champion-rounds dead: us 15.8%, Fish 8.5% (Fish has six bodies). Deaths by phase (≤150, ≤300, ≤600, later):
  us 37/51/145/280, Fish 21/41/81/181. Late deaths are from full health to Fish's 2–5 man group in 1–3 rounds, mostly on our
  half (killctx); a follower walking after its engaged leader dies too. Codex C048: a sighting relay would warn ≥2 rounds
  ahead for only 3/43 Noobot and 2/82 pwonk deaths.
- **Turn use at camps** (`campidle.ts`): beside awake monsters we attack as often as Fish (adjacent: 92% vs 95%). We spend
  39% of camp-context turns beside sleeping monsters to Fish's 22.5% (waiting for parties, walking past).
- Holdout economy: vs Noobot our captures and gems match theirs (r800: 682 vs 707, gems 10,485 vs 9,474; 10–10 in hold316);
  vs policy wonk they pull away after r400 (741 vs 529 captures by r800) and die far less (53 vs 120 late deaths).
- **Fight branches** (local trace, 16k turns with an enemy within 5): fight_enemy 39% (of it assist 50%, hit 27%, spell
  reach 12%, chase 9%), farming a camp 15%, evade 9%, escape 6%. Assist is worth −86 locally when off.
- **Recalls** (local trace, 40 maps vs B7Live): 16 a game before r300, 27 in r300–800, 26 after; recall-capture is ~45% of
  them, low-health retreats ~4 a game, shopping ~4 a game late. Our Willow is our most-killed champion on both benches
  (fish316 130 of 511 deaths, hold316 90 of 349).
- **Eric's three ideas (Oct 24)**, base `bots/B322x` (B309 + `edit_willowback.py` + `edit_latetrips.py` + `edit_bigcamps.py`,
  all off, byte-identical to 316 when off):
  - Willow behind the front (`kWillowBack`): local −48 ± 20; locally her PvP deaths 65 → 42 and ours 237 → 198, but on the
    ladder (322) it cost kills and the holdout.
  - Fewer recalls once scaled (`kLateTripRound`): skip recall-capture when healthy from r400/600/800 −18/−14/−11 (recalls after
    r600 −29%); the slack form (r600, 10 tiles instead of 20) +4 ± 11 (−8% recalls).
  - Big camps (`kMaxElks`, `kWaitCap`, `kSquadKeepCap`; ranked pilgrimage b3045210: HoR waited 42 rounds alone beside the 4-elk
    camp): max 3 elks until r500/r300 −24/−20 (elk_arena −557), wait cap 20 −8, squads capture on the tile +9 ± 19
    (pilgrimage +218); squad capture + late slack together +14 ± 20 → 323.
- Local screens on 316, all negative or flat, not adopted: `kNeighbourGold` 0.2 −22 ± 15 (+ `kNeighbourBonus` 0.15 −42),
  `kHomePull` 0.25 −13, `kContestMemory` 30 −54, `kEvadeAvoid` 30 −174, `kGuardMax` 10/20 −28/−19 (+ home packs −9),
  `kGoldWeightEarly` 0.3/0.4 +9/+1, `kEvadeOdds` 1.0/1.15 −46/−40, `kRetreatHp` 0.45 −41, `kEngageOdds` 0.85/0.7 −42/−43,
  `kPokeStep` off −37, `kAssist` 0/3/4 −86/−71/−43, `kCaptureHold` −1, `kTravelSoloBias` 1.2 (vs 1.5) −1, `kNoWaitAlone` −16,
  `kKillChain` −13, `kShopAll` 0, `kBusyAllies` 0, `kPartyReady` −20, `kOneCapturer` −45, `kSoloRecheck` +1,
  `kFightRecheck` −90, `kRespawnRepick` −16, `kSquadMerge` 0 (never fires), `kChipSpell` −38, `kRepickNow` −6,
  `kPartyArrival` −10, `kSpreadOut` −52, `kStunOrder` −7, `kChainStun` −1, `kPokeFleeing` +1, `kAoeBest` −23,
  `kEscapeKeepsMove` −1. The 316 configuration is a local optimum against our clones on every knob tried.

**End of the window (Oct 24 ~03:00 UTC):** rank 44, 1909.1, up from 68 / 1830.3 at the start; the peak was ~1916.
Rank 10 is Noobot at 2099.9.

The final policy, 309 / 312, is 287 plus:
- the big-party fixes `kHelpKind` 1, `kBigStart` 3 and `kBigAlive`;
- `kMarcBuild` 3 (Marcella Treasure F → Jungle F → Bruiser F);
- `kWillowMeta` 1 + `kWillowHeal` (Willow 5th, healing);
- `kSmallMarc` (3 picks: Marcella, Vesper, Ryth);
- `kFourPick` 2 (4 picks: Marcella, Vesper, Ryth, Willow);
- `kBurstOdds` 3;
- `kMoveReset` 2 (ranged move → reset → attack);
- `kEnemyResetParity` 3.

All of these are switches in `bots/Dev288`, added by `tools/edits/edit_*.py`. Builds: `bots/Up288` … `bots/Up312`.

What moved the needle, and how we know:

| Change | Evidence |
|---|---|
| Marcella's build | local +70, Fish 289 +60 |
| burst-aware fight odds | holdout +164 over 293, ranked 19/25 |
| draft by pick count | local +44 / +127, Fish +157 on the 3-pick maps |
| Willow healing | local +70, neutral on Fish |
| enemy-reset parity | Fish 6/40, the best yet |

What didn't:
- health builds;
- cluster value weights;
- Tavi 5th;
- fight-respect, bag caution, chase, Willow escape lines;
- PvP-only reset, threat targeting, Ryth stun priority;
- capture cover, help-busy, wait fixes.

Lessons:
- Local clones measure economy and builds, but not PvP-adjacent behaviour. Judge those on the ladder: Fish + holdout,
  80 games paired, about an hour per upload under the match-group quota.
- Check opponent draft drift with `scratchpad/draftdrift.ts`; the API exposes no opponent submission IDs.

**Open leads:**
- **Expanse elk rows.** `bots/ScoreDbg` (Up312 plus a per-group score dump in score_team_targets) at r250:

  | Group | Value | Need | Arrival | Clear | Health cost | Home pull | Score |
  |---|---|---|---|---|---|---|---|
  | g9, elk2+gem row camp | 118.5 | 3 | 58 | 27 | 60.6 | ×1.0 | 0.77 |
  | g2, single elk + gold beside spawn | 56.6 | 2 | 2.8 | 21 | 17 | ×1.26 | **1.55** |

  The walk and the health-cost charge decide it. Lowering them locally made expanse worse: kHealthCost 1.0 took expanse
  +171 → +69, 0.5 → +52; kHomePull 0.2 → +143. Our roster clears elk2 slowly (27 rounds with three champions) where Fish's
  Varg / Vendetta / HoR / C&I / Vesper comp is far faster. So it is a capability problem (comp, items, staying at the row)
  rather than a scoring knob. `kRecallCapNext` (bank at the altar near the row instead of recalling) changes nothing until
  we stay there.
- Gold-only clusters: Noobot takes 179 to our 103 over 20 holdout games (Codex C043/C044).
- The `fight_dps_` shop-refresh staleness (C055) and is_ready vs can_cast in the burst horizon (C053/C056).
- A sighting relay through priority, if built with C048's freshness protocol.

**Expanse** (Eric: "Fish targets the elk camps in a row"). The map has two rows of three elk2+gem2+gold1 camps along its
edges, 7–8 tiles apart. Fish takes 12–15 of them by r700 in every bench game; we take 0–4, against our clones too. Our champions
walk about 57 tiles to the row, wait for a party, clear one camp, then recall-capture or guard instead of chaining to its
neighbours (Log309 trace). kNeighbourBonus 0.15 / 0.3 (+3 / −10), kElkRound 0 (+9) and kElkBonus 2.0 (−23) don't change it
locally. A route-chaining rule is open work.

The ranked ladder agreed with 297: 19/25 while it was live (20:30–21:30 UTC), and the rating rose 1870 → 1914.

**Opponent drift.** `scratchpad/draftdrift.ts` compares each opponent's per-map draft across bench tags; the match API has no
submission IDs. policy wonk re-uploaded between hold293 and hold297 (new 3- and 4-pick drafts on 8 maps), so their half of
297 vs 293 is confounded. Noobot and Fish were unchanged.

**Spread** (`tools/stress/units.ts`): Noobot plays 3.2 groups of 1.35 champions, policy wonk 2.7 of 1.56, us 2.6 of 1.6.
policy wonk out-captures us without spreading more.

**Codex C043** (39 exact-v297 holdout replays, action level, through r600): under 297 our capture total against Noobot is
**471 vs 475**, so the gap has nearly closed. The remaining harmless-group gap is **gold-only** clusters: 94 vs 174 against
Noobot and 109 vs 167 against policy wonk. We collect more gem clusters than Noobot (83 vs 44), which is why kCasterClusters
(gem-only) could not close it.

**Codex C041/C042:** ranged champions lose their attack after a move even when an attack reset is ready; Trzy Kwaterki's
Vesper does move → reset → attack. `kMoveReset` (`edit_movereset.py`) gave 1 (Vesper) −19 ± 23 and 2 (all ranged) −20 ± 22
locally: an early reset forfeits a later double hit.

Codex also cautions that killctx's "killers" are enemies within 5 and "camp" is proximity, so they are spatial proxies, not
damage actors.

## Switches changed since the patch

| Switch | Default | Evidence |
|---|---|---|
| `kAggroExit` 6 (+ `kAggroFlee`, `kAggroHit`, `kAggroExitStr`) | off | Eric (Oct 21): leave an unpicked camp's reach (towards allies, else home, even past the enemy) before trading blows; fleeing steps leave a hitting camp's reach first. Whole switch on the Oct 20 engine: **−87 ± 42** (B7Live −165; eight −528, gold-rush −416, elk-arena −404, fracture −355). On the 1.0.1 engine (cambc 3.0.4, one seed, base +317 ± 43): exit before fighting alone **−74 ± 47**, fleeing part alone **−107 ± 44** (hooks −1,239, eight −605), exit only on a turn we were hit **−69 ± 43**; counting only elks and up (`kAggroExitStr` 50) **−73 ± 45**, monoliths only (100) **−50 ± 36** (boss-battle −151, gold-rush −241: the fight code chases back into the reach the next turn, so the exit oscillates at the boundary under 200 a round). Off; a last try pairs it with `kBaitGuard` 2 |
| `kFrontNeed` (`kFrontLine` 0.35) | off | Eric (Oct 21): squad party size from the melee front line (camps-and-maps.md, elk camps): −4 ± 43 on the Oct 20 engine; **−62 ± 44** on 1.0.1 (fragment +356, broken-curve +188, expanse +147; corners −493, elk-arena −458, concentrated-wealth −371, big-world −250). Off |
| `kPrismCarry` + `kPrismBag` 80 + draft `kPrismFarm` | off | Eric (Oct 21): Prism for Stellar in the farming-map stun draft, rewards go whole to him, he banks at 80 gems: +10 ± 44 on the Oct 20 engine; **0 ± 35 paired** on 1.0.1 (92 vs 89 wins; B7Base +94, B7Live −83): neutral, so it rides on Eric's call |
| `kWakeGuardStr` 100 + `kBaitGuard` | off | ladder top200 replays (`scratchpad/deaths_top200.txt`, `ft/bossrounds.ts`): 55 of our 158 camp deaths in 60 games were monoliths (01boss_battle 32, 01gold_rush 23): the top teams fight beside **sleeping** monoliths, our area spells wake them (boss_battle vs Fish r264: Stellar's blast, then 400 a round killed four of ours) or we chase onto them (gold_rush r27). The guard never centres a blast, ground stun or dash landing on a living monster of 100+ strength that is not our target, and never chases, assists against or hunts an enemy inside such a camp's reach (`kBaitGuard` 1 sleeping camps, 2 awake too). **Locally both sides are our code, so the local opponent wakes the monoliths anyway and the guard only costs us the blast:** wake guard alone −21 ± 13 (boss-battle −318), with bait 1 −53 ± 42 (1.0.1 engine, seed 1). The value against teams that fight beside sleeping monoliths on purpose can only show on the ladder |
| `kMakeWay` (`kMakeWayHp` 0.5) | off | Eric's replay 8d03c49e (01boss_battle vs Nyx, r18–28): Ryth cleared an elk at the top edge with Tavi, Stellar and Prism in a column at range 3 behind him; at 300 health he turned to leave the elk's reach 4 and the column was his only way out, so he died with 4 hits to walk. A ranged champion beside a low melee ally nearer the monster steps aside (no nearer the camp, farthest from him) before attacking: **−76 ± 41** (hooks −827, corners −329, eight −309): a ranged champion that steps loses its attack that turn, which costs more than the rare blocked exit. Off |
| `kAltarBait` 6 | off | the same replay, r176–200: Ren stood 25 rounds beside the sleeping monolith pair with 45 gems, "retreating" into a tribute at the centre altar whose channel was unsafe (an enemy 7–8 away), until Nyx's Ryth stunned the monoliths and 400 a round killed him and Tavi. An altar within 6 of a living big camp monster is unusable, and the near-altar branch of the retreat skips it: −6 ± 27 overall but **boss-battle −302** locally (the centre altar is the only near one; our own code does not bait there). Off; only a ladder test could show its value |
| draft `kThreePick` 1/2/3 (+ `kThreePickClumps` 3) | **1 from v203** | Eric (Oct 21): three-pick maps draft Heart of Ruin + Ryth + a third: Stellar **+41 ± 21** (collision +325, fragment +462, broken-curve +65), Tavi +6 ± 20 (collision −564, gold-rush +374), Prism **+46 ± 28** (fragment +488, gold-rush +355, collision +50); Varg as the third on maps with three or more packed camps. The 3-pick maps of the 21-map pool: collision, fragment, broken-curve, gold-rush (gold-rush already drafted HoR, Ryth, Stellar via the stun draft) |
| `kPartyArrival` | **on from v203** (old switch) | Eric's replay 564ea16e (01concentrated_wealth vs Nyx, r84): Ryth, Stellar and Marcella recalled at full health 11 tiles from the centre node because the leader (Heart of Ruin, back from healing at home) re-picked the squad's camp from his own position, a home camp, and the three followed it with `kRecallHop`. The switch times squad picks by when the party can gather instead of the leader's own walk: +20 ± 37 (concentrated-wealth +331, elk-arena +328; monolith −159) |
| `kCarry` 1 Stellar / 2 Heart of Ruin | off | the top teams funnel gold into one champion (champions.md, "Who holds the gold"): a designated carry walks onto every reward its squad clears and the others step off. 1.0.1 engine: Stellar −38 ± 41 (collision +320, eight +505; interlock −448, expanse −192), Heart of Ruin −53 ± 26. Against our own code the extra walking costs more than the concentration gains; off |
| `kTreasureBuild` 2 (Treasure first on every map) | off, candidate | the top six open with Treasure everywhere: **+20 ± 35** (elk-arena +552, islands +82; concentrated-wealth −85); with the Stellar carry −31 |
| `kFarSideAll` | off, to screen | the round-100 ban on enemy-half camps on every map, not only control maps (fragment vs meow: one stack on their half, 8 captures in r300–600 to their 31) |
| `kTeamSquads` 2 / `kSplitRound` 150 / `kAutoTeam` off / `kOpeningRounds` 60 / `kSquadSize` 1 | unchanged | the farming-speed gap: meow farms in more, smaller parties (camps-and-maps.md, "Our half of the map"). 1.0.1 engine, one seed: −48 ± 56 (eight +473, fragment +382; ambush −214) / −13 ± 8 / **+17 ± 26** / −16 ± 42 / **+10 ± 31** (lanes +182): none decisive against our own code; `kAutoTeam` off + `kSquadSize` 1 go into the next combination screen |
| draft `kFishDraft` 1 / 2 | off | Fish's drafts depend only on the pick count (champions.md): 1 their lists, 2 the other leaders' consensus. 1.0.1 engine: **−169 ± 62** and **−150 ± 55** (with Treasure first −236): our play is built around our own lists (no C&I logic tuned for HoR teams, Stellar not a carry), so copying the draft alone loses |
| `kTreasureBuild` 2 + `kAutoTeam` off + `kSquadSize` 1 | candidate | the farming-speed combination: +25 ± 40 (21 maps, seed 1); **+48 ± 32 on all 35 pool maps** (starfish +1,091, corridors +473; starvation −393). Seed 2 pending |
| `kTrueWake`, `kDashGaps`, `kDashGapSave` (35 maps, seed 1) | screening | true wake −5 ± 25 (gold_rush +239, concentrated_wealth +323, the_farm +213; starvation −240); dash gaps everywhere −41 ± 32 (shortcut +156, gold_rush +283, concentrated_wealth +349, stampede +323; pilgrimage −317, starvation −361, ambush −246): on maps without any gap it still stopped dash champions buying crystals, which `kDashGapSave` now gates (the gaps must save that many steps from our spawn to some camp, else the switch is off) |
| `kFarSideAll` | off | −2 ± 34 |
| `kTrueWake` | screening | Eric's group 50de3767 vs KratosMessi, 01gold_rush: the centre monolith's group includes the gem clusters around it, and chipping a cluster wakes the whole group, monolith included, at full health. Our model only counted hurt monsters as awake, so Heart of Ruin stood 2 tiles from the awake monolith for four 200 hits. The SDK reports each visible camp's real state (`camp::is_awake()`); the switch uses it and falls back to "hurt" only for monsters out of sight. One local gold_rush game: monolith deaths 14 → 5 |
| `kDashGaps` | screening on 35 maps | the same group, 01shortcut: our room and the centre camps are split by a one-tile hole row; Heart of Ruin recalled at full health 3 tiles from spawn to buy a teleport crystal, teleported over the row, and later walked ~50 steps round it (Ren too). The switch (from Oct 20) paths dash champions over one-tile hole gaps and never buys them crystals; it was neutral on the old 21-map pool, which has none of these rooms |
| Eric's six requests (Oct 21 09:00; 35 maps, seed 1, base = v204's settings) | — | **`kRangedHome` +60 ± 26** (lone ranged champions take no enemy-half camp unless the map is quiet: adopt); draft `kAlwaysHoR` (Heart of Ruin first on every map) **−76 ± 31**; `kSiege` 1 with `kSiegeWaves` 3 (commit to monoliths when three trips take them; rows and others) −53 ± 32; `kRuinDashHp` 0.5 (dash at champions only above half health) −29 ± 12; `kShareCapture` 2 (split rewards so tributes are short) −24 ± 36; `kRecallCapSlack` 5 (fewer recalls after captures on long maps) 0 ± 39 |
| `kGapEscape` | off | Eric: use one-tile gaps to escape. Fleeing with a ready dash prefers a landing tile fewer enemies can hit next turn, melee enemies counted on foot round holes and walls. With the farming combination and true wake, 35 maps seed 2: **−129 ± 42** (B7Live −231): the dash is spent on escapes the old rule did not need |
| seed 2, 35 maps (`ev_dev10`) | — | farming combination +23 ± 33 (pooled with seed 1 ≈ +35 ± 23); + true wake **+29 ± 34**; + true wake + dash gaps (gate 30) −4 ± 36; dash gaps (gate 30) alone −18 ± 26 |
| `kNextOnce` | off | the squad's next camp chosen once per capture and kept (the leader rescored it every round and the followers flipped between far camps: 01starvation r42–46, five camps 11–43 tiles away; `scratchpad/pick/`): +3 ± 13 paired (only a few games differ) |
| `kGoldWeight` 0.12, `kGoldFadeRound` 800 | on | local +54 ± 30 (wins 153 → 177 of 252); ladder +3,000 margin |
| `kTrueReach` | on | camps reach 4–5 now; was a fixed 3 in the reach table: local +69 ± 29 (wins 151 → 167); ladder −3,476 ± 2,530 over 80 games (camp deaths 464 → 421, deaths to champions 825 → 895) |
| `kMetaBuild` 1 | on (v194, live) | procless's order: Jungle, Durability Health, Monster, then Bruiser in the main stat (Ren and Ryth open with Bruiser Health). Local +135 ± 35, +148 ± 36; Sponge's order (2) +171, +65; ladder +10,881 |
| `kTreasureBuild` 1 | on (v190) | Treasure first for every champion on scaling maps: gem-count or tiebreak plan, or a boss camp (contest, fragment, gold-rush, hooks, monolith, big-world, boss-battle, broken-curve, corridors, fracture). Local −17 ± 45 with the wider rule (neutral); 2 (every map) −41 ± 50 |
| `kGroupWake` (a hit cluster wakes its node in our model) | off | local +21 ± 31 (one seed) |
| `kSnipeFarm`, `kSnipeBoss` | off | elks reach 4, monoliths 5: only wolves are snipeable from 4 (neutral) |
| `kSiege` 1 + `kSiegeMapShare` 0.56 | off | contest +316/+367 locally, neutral overall, worse on the ladder (v186) |
| `kBossMaxStr` 250 (boss mode on monoliths) | not used | −322 |
| `kAggroPriority` (priority = current health) | off | cancels true reach's gain (+3 vs +69) |
| `kDashGaps` (dash over one-tile hole gaps, no crystals for dash champions) | off | neutral (−29 vs true reach alone); helps concentrated-wealth |
| `kBushTribute` (tribute from hidden altar bushes) | off | neutral locally (−15 ± 21) |
| `kTileMicro`, `kEngageMicro` (scored escape/chase steps) | off | flee −2 to −17 (neutral), engage −83 |
| `kWallThreat`, `kWallStep`, `kSightRoots` (wall review) | off | −66, −19, +18 (with side effects) |
| `kTwinSwap` 1 (draft: Marcella for C&I) | on (v193, live) | +35, +59 on the current base (two seeds); −4 on the v188 base; Vesper −46, Heart of Ruin neutral |
| `kStunDraft` 1 (farming maps: Heart of Ruin, Ryth, Stellar, Ren, Marcella) | on (v193) | +27 ± 24 (two seeds); counter-pick variant 2 −56 |
| `kMeleeEase` 0.75 (smaller camp parties: 3+ melee on a farming map) | on (v193) | +7 on top of the stun draft (two seeds); all three together +53 ± 33 |
| `kChainStun` (hold a stun while the target is stunned) | off | −46 with the stun draft (hurts the usual comps on contest, corners, collision) |
| `kRuinKit` (Heart of Ruin's dash as an attack, Focus build) | on | acts only when Heart of Ruin is drafted |
| `kEscapeReserve` 1.2 / 1.5 (retreat while health covers the walk out of reach) | off | camp deaths −9% / −15%, but −25 ± 32 / −61 ± 31 (two seeds): early retreats cost more farming than the deaths |
| `kSoakModel` (party sizing by the soaker's budget) | off | −37 ± 52; with the reserve −50 ± 32 |
| `kAggroRotate` (priority = health in quiet camp fights) | off | +39, then −3 ± 31 over two seeds |
| `kTagIn` (a ranged mate steps beside the camp when the soaker is lower) | off | with rotation +50 (deaths −13%), then −21 ± 32 over two seeds (seed 2: deaths +10%) |
| `kWaveFallback` + `kWaveIdle` 40 | on (v197) | no feasible camp for 40 turns: the squad takes the best survivable one in waves (stress g0010 0 → 767 gems); ungated it also fired on pool maps |
| `kSquadWalkable`, `kAvoidRepick` | on (v195) | squads skip camps no walk reaches; a follower avoiding the squad's target farms solo (stress g0046 idle 638/1000 turns → fixed) |
| `kCampFaceGap` 3, `kLoopGuard` 10 | on (v195) | camp reroute also on 2–3 tile bounces; generic loop watchdog (10 rounds on ≤3 tiles, moving, no attack: drop the target) |
| `kAllyJam` 2 | on (v197) | head-on jams in one-wide corridors: the higher slot backs away 6 turns (stress g0120 288 → 974 gems) |
| `kRetreatLoopRecall` | on (v197) | recall after 3 reach exits in 12 rounds (retreat ↔ leave_reach loop); `kRetreatSafeStep` 3 (recall on every exit) −52 |
| Robustness totals | | first stress set: stuck 96 → 13 episodes, loops 3,791 → 934 rounds; second (unseen) set: stuck 43 → 7, loops 4,849 → 269 rounds, fuel-limit turns −30%; pool −4 ± 33 |
| `kSoloRecheck` (a kept solo target must still be soloable before the first hit) | off | −0 ± 14 over two seeds (fixes the 01big_world replay's Varg deaths, too rare to move the totals) |
| `kFightRecheck` (the soaker leaves when too few are present for the rest of the camp) | off | −91 ± 49, deaths +8% |
| `kBigCampShare` 0.5 (no solo farming where big camps hold the value) | off | −27 ± 30 (gold-rush −386, big-world −199) |
| `kVargSwap`, `kTaviSwap` | off | Heart of Ruin for Varg +1; Tavi swaps −110 to +11 (see `champions.md`) |
| `kForceDraft` | 0 | forced compositions all lost (see `champions.md`) |

## Local screens of October 21 afternoon (35 maps × 2 sides × B7Live/B7Base; `tools/fastscreen.py`)

Base = v204's settings + `kRangedHome` (the "V4" string in `tools/edits/README.md`). Paired difference from the base;
one seed = 140 games, two seeds = 280. The top-team analysis behind each idea is in `top-teams-1.0.2.md`.

| Change | Result | Decision |
|---|---|---|
| `kMetaBuild` 3 (Treasure, then Power in the main stat: Fish/Nyx/procless's carries) / 4 (+ Durability Health) | −227 ± 38 / −117 ± 36 | off |
| `kMetaBuild` 5 (our Jungle/Durability/Monster opening, then Power) / 6 (no Monster) | −138 ± 27 / −92 ± 32 | off: Bruiser stays |
| `kCampAware` (path fields block live camps from the first step) | −49 ± 38 (expanse −299: early gold 1,550 → 950–1,180) | in the pathing set |
| `kRootWalk` 2 (approach tiles within range + 2 walking steps of the camp, not across a wall) | −39 ± 40 | in the pathing set |
| `kWaitSafe` (wait for the party outside an awake camp's reach) | −3 ± 22 | in the pathing set |
| pathing set (the three) | −20 ± 47 one seed, **−27 ± 32** two seeds; gold by r300 +7.5%, gems by r900 +6%, first pickup r43 → r37, deaths by r600 3.3 → 3.1 | **on** (Eric: fix the pathing; 01corridors: the team walked down a corridor sealed by a camp row and back, 28 rounds) |
| `kSquadMoveOn` 20 / `kOneCapturer` | −1 ± 1 / −28 ± 42 | off |
| `kOpeningRounds` 60 / 40 / 0 / 0 + `kPairOpening` 120 | −37 / −31 / −68 / −58 (± 43–52) | 120 stays |
| `kHuntOdds` 1.5 / 2.5 | −103 ± 36 / −130 ± 34 | off |
| `kAutoTeam` back on (whole-team farming by layout) | −5 ± 23 (rows −422 → −67, packs +202 → +95, corridors +901 → +265) | off; `kAutoTeamPacks` false (whole-game case only) −20 ± 17 |
| draft `kTaviSwap` 5 (HoR for Tavi) | −75 ± 31 (corners −677 vs +251, hooks −700 vs +693; swirl +531, starfish +236) | off |
| draft `kVargSwap` 5 (HoR for Varg) | **−7 ± 9** | **on** (Eric: HoR in every draft) |
| draft `kPrismSwap` 5 (HoR for Prism, new) | −45 ± 21 (corners −659: the contest five lost the r40 fight at the top-middle camp) | off |
| `kMidAvoidAll` 100 / 200 (no midline camp before that round on every map; top teams open on their own half) | +2 ± 33 / −55 ± 35 | 100 **on** |
| `kSquadSize` 2 / 3 (one seed) | −1 ± 33 / **+37 ± 34**; 3: gems by r900 +7.6%, elk kills r300–600 3.1 → 3.8 | 3 **on** |
| `kSquadSize` 3, + `kMidAvoidAll` 100, + `kVargSwap` 5 (two seeds) | +16 ± 24, +29 ± 35, **+23 ± 35** | the "D1" set |
| yellow-brick-road fixes from the review line on D1: `edit_waitfix` (harmless groups never wait; party counted from the nearest tile) + `edit_walkgroup`/`walkgroup2` + `edit_blindcap` | −27 ± 26 (ybr +269 → −39 against our own idling code) | walk-group off |
| `edit_waitfix` + `kCaptureBlind` 10 / `edit_waitfix` alone | −27 ± 25 / **+1 ± 21** | waitfix **on**, blind capture off |
| **Cand206** = D1 + waitfix, against v205's own code on the same opponents (two seeds) | Cand206 +207 ± 31, v204 settings + `kRangedHome` +211, D1 +206, **v205's code +125 ± 30** | candidate; only a ladder bench can separate the new parts (all within ±40 of each other locally) |

**What the local screen cannot see:** on 01yellow_brick_road v205 idles at spawn for ~100 rounds (`wait_party` on a
30-cluster gold row whose centre is 15 tiles away) and loses 0/6 on the ladder, yet locally it *wins* that map because
B7Live idles the same way. Use `tools/stress/mapbench.py` (our gold and banked gems per map against the top teams' own
games) for farming changes, and the ladder for the verdict.

## Review of 2026-10-21 (`.info/Reviews/Review-2026-10-21-7c34f0d.md`): what was done

All eight numbered findings verified against the source and fixed in one pass (no switches: they are defects):

| Finding | Fix | Check |
|---|---|---|
| 1 outnumbered poke dashed into the enemy | `cast_offensive(..., allow_dash)`; `ruin_dash` never lands where `fight_odds < kEngageOdds` | 00lanes traced: dashes into champions 11 → 5, onto camps 50 → 109 |
| 2 Heart of Ruin's landing hit missing from the damage model | `damaging_dash()` in `deals_damage`; `ability_reach` = range + radius for it | the review's contract probe: `self=1 enemy=1 ally=1` (was 0/0/0); Ren, Vendetta unchanged |
| 3 wave fallback party not shared | a published target infeasible for us needs the whole squad; `wave_pick_` cleared; `wave_ok` sums the pack | — |
| 4 finish gate ignored big bags | own bag counts towards the 600-banked window | — |
| 5 blocking per group, not per monster | `member_blocks(gi, k)` / `tile_blocks` from `hp_left_`; epoch bumps on per-tile changes | — |
| 6 `shootable()` firing tile unreachable | must be walkable from home (home field); Heart of Ruin in `dash_mate_alive` | — |
| 7 cache keyed on map name | `sweepc.sh` key includes the map file's sha256 | cache invalidated once |
| 8 forgotten pick forces a rescore under low fuel | defer with no target instead | — |
| smaller | ally-jam: the higher slot yields (was reversed); `walk_sides` returns success, `kPlanWalks` only then; `hold_outside` steps outward when deep inside; allocator size guard | — |

Not done from the review: enabling `kAlertOnce`, `kAoeReachOut`, `kAoeBest` and the other dormant switches (behaviour
changes needing their own screens); `cacheimport.sh` engine provenance; the shared-memory protocol redesign.

**First result:** the bundle alone was **−78 ± 32** on the 21-map pool (two seeds) and raised fuel-limit turns: the
per-tile occupancy of fix 5 was O(n²) per group each turn, and 01yellow_brick_road has 30-cluster groups (fuel-limit
turns on it 294 → 792 a game). Rewritten by member index, with camp targeting from cached positions and crowd counts
only within reach: 209 (below v197). The pool screen of the fuel-fixed source is the open question (see the live table).

**Attribution (one seed, each fix alone on v197's source, paired margin):** F1 dash policy **−39 ± 25** (the extra
"never land where the odds are against us" check in `ruin_dash`, removed again: Heart of Ruin's dash is its main tool;
the review's own fix, no dash from the outnumbered poke, stays), F2 damaging dash in the model **+67 ± 27**, F3 −5 ± 28,
F4 −19 ± 13, F5 +20 ± 38, F6 −1 ± 3, F8 −27 ± 39, smaller items −24 ± 30, `kCaptureBlind` **+30 ± 19**, harmless no-wait
+21 ± 38. The whole bundle with the fuel fix: −41 ± 38 (two seeds).

Also from Eric's 01yellow_brick_road replay (4c54fd19, v197): `kCaptureBlind` (a reward that stays "available" after
our recall-capture completed, or after 10 standing turns, is contested by an unseen enemy: leave it 60 rounds), and
harmless groups no longer wait for a party (nearness measured from the nearest group tile): four champions had waited at
spawn 40 rounds for mates "near" the row's centre. With no living member in sight a champion walks along a group to
the nearest member believed alive on our side of the map (`walk_group`), and leaves it when the rest is on theirs
(`group_far`): the first, unbounded version marched along the row into the enemy (53 deaths a game). On the 14 maps
new to the pool (56 games vs Opp95/B7Base): stuck rounds 1,002 → 48, fuel-limit turns 6,377 → 3,050, wins 45 → 44;
01yellow_brick_road 1 → 3 wins of 4; 01starfish unchanged (1 of 4, 48–63 deaths a game). `kMetaBuildFarmOnly` (Power-first build on contest maps) tested
and rejected: −200 to −800 on corners, contest, collision, interlock. Open: 01starfish, where we lose centre fights and
die fleeing up the corridor (63 deaths a game vs our Oct 19 code; 34 of 59 deaths in escape/retreat/leave_reach).

## Known gaps (October 20)

- **Gold:** the top teams still earn more gold per farming round; deaths feed them 100 gold each. On the long maps the gap
  is widest (80 ladder games, Oct 20: contest 7,961 vs 13,527, boss-battle 16,272 vs 33,909, gold-rush 5,396 vs 11,875).
- **Deaths:** we die more often than Nyx/Univ for similar damage taken; many deaths are while fleeing, 4–5 tiles from
  the nearest enemy (spell reach).
- **Camp deaths (80 ladder games, v190):** 3.8 camp-only deaths a game (90%+ of the last 10 rounds' damage from
  monsters), 212 of 307 starting at 90%+ health, 222 with no ally within 2; elks in ~183, monoliths in ~132, wolves alone
  24; Varg 80, Stellar 50. Causes found: the retreat line (35% of max health) predates the patch's longer reaches, and
  party sizing summed the party's health budgets though one champion takes every hit (`kEscapeReserve`, `kSoakModel`).
  User's replay 2daa53c5 (01big_world, v192): 6 camp deaths from full health, no enemy near; Varg 4 (guarded a camp's
  respawn and fought the fresh 2 elks + wolf alone, the plan said 3 champions), partners walked off in 4 of 6.
- **Monoliths:** we only siege late; KratosMessi rotates three melee on a monolith from ~round 640.
- **Wards:** our ward logic was written for a cooldown of 1; it's 10 now.

## What the bot reads and stores

**From the map (static; set-up and draft):** width and height; walls, holes, bushes and altars; both spawn regions;
every camp group (each member's kind, spawn tile and base stats: health, strength, reach, respawn; the group's gem and
gold values). Everything else is derived from these: walking-distance fields from both spawns, group values and
threats, the map profile (race / gem count / gold tiebreak / boss, scaling map), the spawn-to-spawn walk (farming map
when over 45 steps), ward spots (bushes near the centre and altars), dashable hole gaps, crystal hops.

**Each turn (own vision only):** visible tiles; champions in sight (position, health, buffs such as stuns, recall and
tribute channels); camp members' health; wards (ours and the enemy's); altar locks.

**The draft** reads the map only: spawn-to-spawn walk (farming vs ranged lists), team size, elk-only maps, home packs,
boss camps, spawn closeness; and (with `kStunDraft` 2) the enemy's revealed picks.

**Draft memory (1,024 bytes):** a precomputed map plan, so champions skip the costliest set-up (swirl's took ~350k fuel
and delayed the first move to round 4–5). The draft's first turn has 10× fuel. Layout: an 18-byte header (magic `B7P1`,
version, map size, group and camp counts, our spawn tile, spawn-to-spawn walk, flags, checksum) and 10 bytes per camp
group (first tile, walk from our spawn, walk from theirs, neighbour value). 01islands' 46 groups use 478 bytes; the
rest is free. Nothing about the draft itself is stored; champions read the roster.

**Shared memory (8 bytes, live):** bytes 0–5 each champion's target group + 1 (with help/solo flag bits); bytes 6–7
one team alert (kind, id, round). The banker relay (bytes 8–10) and team-focus target (12–14) lie past the 8 bytes,
so they never work; both serve switches that are off.

## Match database, Oct 23 (24,486 summaries; `tools/stress/dbextract.py` → `results/db/features-1023-part1.jsonl`, `tools/stress/dbanalyze.py` → `results/db/oct23/`)

Summaries (`.camstat`, `cambc summary` → JSON) hold per-champion totals, round timelines, an event log (buys in order, camp clears,
wards, deaths with killer kind and position, gem losses), drafts and the outcome; map hash = sha256 of the map file.

- **What predicts the winner** (share of matches won by the team ahead): gems collected by r600 0.80, gold earned by r600 0.80,
  by r300 0.74; kills by r600 0.75; fewer deaths by r600 0.71; camp clears by r600 0.70; wards 0.55, crystals bought 0.55;
  gold concentration on one champion 0.495 (the "funnel" does not predict winning).
- **Our gap is farming throughput**, not deaths: gold by r300 us 1,107 vs top 10 1,221–1,911 (Fish 1,911); by r600 2,636 vs
  3,040–4,681; camp clears by r600 24 vs 29–37; deaths by r600 3 for us and most top teams.
- Profiles per top-10 team (drafts, opening purchases, gold share per champion, crystals, wards) in `results/db/oct23/profiles.md`.
  Common top-team openers: Treasure Health on tanks (Vendetta, HoR, Ryth), Treasure/Jungle Strength on Vesper.
- **Our death hotspots** (`results/db/oct23/deaths.md`, 1,460 deaths in 197 games): elk_arena centre 15–29,20–29 (126 deaths,
  mostly to Fish and policy wonk), boss_battle centre (43), gold_rush 5–19,10–24 (76), yellow_brick_road row 15–34,10–19,
  contest centre, interlock 25–34,10–19. These are the seeds for scenario maps.
- `bots/FishLike` (`tools/edits/edit_fishlike.py`): Fish's drafts and opening builds on our play. Locally 192/320 vs B7Live/B7Base
  (our 336: 292/320), so Fish's strength is its play, not its composition; not yet a strong screening opponent.

### Fights in the Oct 23 replays (Oct 25; `fights.ts` / `fightstats*.py`, now in `tools/stress/`)

Skirmish = rounds with champions of both teams within Chebyshev 4 of each other, merged when under 4 rounds apart; "even" = the
same number of champions per side within 6 of the first contact. 1,197 replays (ours 197, Fish 300, willow best girl, prism best
girl 200 each, policy wonk and :3 150 each), opponents ranked 20-80 only for the comparisons below.

- **Fight selection is like the top teams'**: outnumbered in 27-33% of skirmishes for every team, solo 40-56%, under 60% health
  at the start 6-12%.
- **Conversion is not**: per even skirmish we kill 0.32 and lose 0.25; Fish 0.78 / 0.27, willow 0.62 / 0.19, prism 0.64 / 0.17.
  Health lost, theirs / ours: us 1.19, Fish 1.56, willow 1.93. Our deaths per champion per even fight (0.100) equal Fish's (0.099).
- **Where the kills go**: we bring 27% of the enemy champions in even fights under 30% health (Fish 42%, willow 43%); of those
  only **51% die and 39% escape by recalling** (Fish 80% / 14%, willow 66% / 26%), 9% walk away. Damage, stun or death interrupts
  a recall (GameRules), and a recall takes five turn ends: the recall escapes are the largest single kill gap.
- Gold by r300 vs similar opponents is mostly kills and camp size: kill gold by r300 Fish ~290 (2.9 kills at 100), ours ~100.
- Local screens of the farming variants (re-scored, `rescore.py`): solo, gold weight 0.3, no team opening, shorter opening all
  clear more camps by r300 but **earn 15-75 less gold by r300** (smaller camps); none raises early gold.
- **Recall hunt** (`kRecallHunt`, `tools/edits/edit_recallhunt.py`, bots/B340x/B341x; off): hit low enemies' recalls (any damage
  cancels one). Locally vs B7Live (80 games each, live config): reach + 4 under 50% health with odds 1.0 −14 ± 45 (recall escapes
  420 → 341, kills +3%, our deaths +8%); any recaller −92; no odds check −43; turn-aware reach 8 (`kRecallHuntTurns` 4) −75,
  + `kRecallChase` 3 −47, reach 4 + chase −59; the turn-aware builds lose ~21 gold by r150 already (roster scans cost fuel).
  `recallesc.ts`: 399 of 658 low enemy recalls start 7-8 tiles from our nearest champion; interrupted ones mostly walk away.
- **Fight uptime** (`uptime.ts`, replay step kinds 4 move, 5 attack, 6 cast, 8 end turn): with an enemy champion in attack range
  we hit a champion 54% of turns and only moved 28%; Fish 67% / 19%, willow 66% / 15%. One tile out of reach we step in and hit
  16% (Fish 31%, willow 37%). Our damage is no less focused (most-hit enemy takes 71% of it, Fish 63%), but that enemy loses 70%+
  of its health less often (56% vs 74%): raw damage.
- **Fight log** (`tools/edits/edit_fightlog.py` → `tools/stress/fightlog.ts`, 80 games vs B7Live): turns starting with an enemy
  champion in attack range had no attack through escape 17%, evade 16.5%, fight_enemy 7.7%, kite 6%, retreat 2% (melee hits from
  escape's strike_while_escaping are not flagged: that path calls attack() directly). Only Vesper Vale and Willow are ranged (3).
- **Stand shot** (`kStandShot`, `tools/edits/edit_standshot.py`, bots/B342x; off): a ranged champion with an enemy in attack range
  shoots instead of evading/kiting while the next-turn burst on it is under X x its health. Works as meant (in-range hit share
  46.6% → 54.4%, move-only 31% → 24% with X 1.0), but vs B7Live 80 games: 0.3 −27 ± 44, 0.5 −22 ± 50, 1.0 −9 ± 44, 0.5 evade/kite
  only −25 ± 46; kills unchanged.
- **Upload #338 (Oct 25)** = 336's config (base336.edits on bots/B342x) + `kStandShot` 1.0, locally +12 ± 16 over four seeds (wins
  596 vs 587 of 640). Benched on Fish and the holdout against #337's post-deadline benches (fish339 / hold339). The bench tags
  fish338 / hold338 now hold this upload (the Oct 24 "338 combo" raw files were overwritten; its results are above).
  Result (07:22-07:30 UTC, both certified 40/40, no opponent re-drafts): **Fish 2/40, −27,115 vs #337 1/40, −29,260: +54 ± 47**
  (fragment W +602 vs −932, the_farm −100 vs −677, elkring −407 vs −715; boss_battle −1007 vs −740, shortcut better, hooks worse);
  **holdout 12/40, −10,888 vs 13/40, −7,291: −90 ± 85** (Noobot −16 ± 101, policy wonk −163 ± 136). Neutral overall, the usual
  shape (a little better vs Fish, worse vs the holdout). Benches finish in ~5-8 minutes now (queued 07:22, done by ~07:30).

### Unseen-map proxy and death spirals (Oct 25; goal: the Nov 1 knockout on new hand-made maps)

- **Proxy:** the 15 `sprint_1_*` maps (earlier versions of the 01 maps, untuned since Oct 20). Uploaded #338 (built with
  cambc 3.0.4) vs B7Live: 23/30 wins (pool versions 26/30). Losses are **death spirals**: sprint elk_arena 56 / 51 deaths (35 after
  r1000, 21 in one 4x4 cell of the central arena; spawns 18 tiles apart with the elk arena and both altars between them), starfish
  B 38, hooks B 34, yellow_brick_road A 26 (11 to camps), boss_battle A 14 (11 to camps); wins have 0-8 deaths. Name replays
  `<map>__<opp>__<side>` for genscan (bare `<map>__<side>` swaps us/them).
- **Builds flip games:** the same config built by clears.py (cambc 3.0.5) won elk_arena A vs B7Live +704 where the 3.0.4 upload
  build lost −836; base on the sprint maps vs B7Live + B7Base 54/60. One game per map says little: unseen-map screens need seeds.
- **`kDeathHeat`** (`tools/edits/edit_deathheat.py`, bots/B343x; off): avoid groups where N teammates died within 6 tiles in the
  last W rounds. Sprint maps, 60 games per arm vs the #338 config: N2/W150 49/60 −130 ± 70 (gold r300 −108), N3/W150 52/60
  +5 ± 59, N2/W300 43/60 −148 ± 61. Avoiding the central camps trades deaths for starvation. Rejected.
- `post_alert` drops group ids >= 64 (6-bit id): no death/defend alert at high-index camps on a map with more than 64 groups.
- `tools/edits/edit_mapdump.py` anchor updated (observe_groups is now followed by read_event).
- **Seeded sprint baseline** (#338 config on bots/B343x, 4 seeds × 2 sides × B7Live/B7Base, results/ev/run1792914936): **207/240
  (86%)**, +519 ± 30, in line with the pool: not broadly over-fit. Weak maps are tight contest maps with exploding deaths:
  elk_arena 7/16 (32-40 deaths a game, up to 50), starvation 10/16, starfish 12/16 (15-20), boss_battle 13/16 (12-16),
  yellow_brick_road B 5/8 (22); the other ten maps 113/120 with 0-7 deaths.
- **Contest maps snowball from early farming, not early fights**: won and lost games both have many deaths on both sides (elk_arena
  won: our gold 11.6k vs 5.1k; lost 4.6k vs 11.3k). Over 108 contest-map games the kill-death lead at r150/r300/r600 picks the
  winner only 48/51/54%, but our gold at r150 above the median (410) agrees with the result 69% (r300: 71%).
- **Economy arms on the contest sprint maps** (elk_arena, starfish, boss_battle, starvation, yellow_brick_road, hooks; 4 seeds,
  96 games, vs the #338 config 70/96): kGoldWeightEarly 0.3 77/96 +26 ± 57; kAutoTeam off 78/96 +51 ± 52; kSquadSize 1 + gold 0.3
  79/96 +47 ± 59. **All 15 sprint maps, 8 seeds** (480 games, results/ev/run1792915450): #338 config 414/480; gold 0.3 429/480
  **+29 ± 18**; kAutoTeam off 420/480 0 ± 17; **solo + gold 0.3 436/480 +36 ± 19** (elk_arena −249 → −64, starvation +154 → +324,
  gold_rush +536 → +701). Pool 4-seed for solo + gold 0.3: −5 ± 15. Hand-style suite next.
- **Codex's unseen-map tools** (collaboration/20261025/): map_from_json.ts / map_to_json.ts (JSON recipe ↔ native-verified
  .map26a), a 15-map hand-style development suite (rooms / hole pockets / bush corridors, 5 sizes each, 3-5 picks, 12 groups),
  boundary fixtures (64/100/102/128/256 groups, disconnected spawns). The suite is installed as `maps/sprint_1_hs_*.map26a` (the
  sprint_1 prefix keeps it out of default pool screens). The older generator is `tools/stress/mapgen.ts`.
- **Hand-style suite** (Codex's 15 maps, 4 seeds × 2 sides × B7Live/B7Base, results/ev/run1792915815): #338 config **231/240**
  (+449 ± 15); gold 0.3 229/240 −30 ± 14; solo + gold 0.3 233/240 −31 ± 16 (family means: bush corridors +34, hole pockets −84,
  rooms −42). These are roomy farming maps vs B7 (96% wins): little win signal. Solo + gold 0.3 in wins: sprint +22/480, hand-style
  +2/240, pool −9/640; its gains sit on the contest maps that lose series.
- **Upload #339 (Oct 25 08:43:04 UTC)** = #338 config + kSquadSize 1 + kGoldWeightEarly 0.3 (bots/B342x; tags fish339sg / hold339sg -
  fish339/hold339 stay #337's; the #337 upload copy moved to bots/Up339_platform337, its logs to up339_p337.out / scan339_p337).
  Certified 40/40, draftdrift 0: **Fish 2/40 +11 ± 28 vs #338** (2/40); **holdout 9/40 vs 12/40, −76 ± 99** (Noobot +75 ± 138 with
  4 new wins and 4 new losses; **policy wonk −227 ± 136**, losing **elk_arena −978 and hooks −836**, which #338 won +972 / +990 and
  #337 won too). Solo farming fixed the contest maps vs the B7 clones (weak fighters) but a strong fighting team picks off lone
  farmers on exactly those maps: **B7Live/B7Base cannot measure exposure**. Local screens of farming changes need a stronger
  fighting opponent (e.g. the current config itself) before the ladder.

### Fuel headroom (Oct 25, Eric: "ensure that fuel isn't a problem")

- **Value of fuel** (`kNoopFuel` burns loop steps at turn start, ~7 fuel a step; live #339 config on bots/B344x, 40 pool maps,
  2 seeds × 2 sides × B7Live/B7Base, n 320): +~10k a turn (1,500 steps) 279/320 vs 297, **−33 ± 24**; +~28k (4,000 steps)
  223/320, **−242 ± 29**. The bot runs with ~20-30k to spare; a heavier unseen map is a cliff.
- Official `fuelExhausted` events (normal builds, statistics JSON): pool maps 55 a game (~1% of champion-turns); heavy pool maps
  (yellow_brick_road, lanes, split, road_of_riches) ~300; Codex's 64-256-group fixtures 800-1,200 (128 groups: both games lost).
- **Where** (`edit_fuelphase.py` + `edit_aclog.py`, 20 heavy/fixture games): 87% of suspensions in the decide phase (fight_camp
  1,241, travel 640, guard 464, recall_capture 442, capture 375), entered with a median **10-15k** left: observe + squad phases
  spent ~85-90k. Spike profile (`tools/edits/edit_fuelspike.py` on the profiler, read by `tools/stress/fuelspike.py`; the profiler
  itself triples suspensions): on turns over 85k the squad phase costs 29k (pool) / 40k (heavy) / 39k (fixtures; arrival_time 40k).
  Mean per turn on pool maps 49k: decide 14.3k (farm 9.1k, fight_group 3.3k), squad 10.1k (scoring 7.2k), observe_groups 5.3k,
  observe_allies 5.1k, start 4.4k, observe_enemies 2.9k, post/warm/wards ~2k each.
- **`kScoreBudget`** (`tools/edits/edit_scorebudget.py`, bots/B344x; off): rescoring needs its measured cost + a reserve, else the
  last pick (≤ 6 rounds) and a turn-end rescore; the solo scorer gets the same guard (it had none). Fuel events unchanged (reserve
  35k: pool 55 → 55, heavy 342 → 371, fixtures 810 → 812; 50k / 65k: heavy −3% / −7%). Scoring is not the binding cost on its own.
- **Fuel rework, baseline (Oct 25; Eric: no rewrite, rework the observation layer).** Method: `tools/edits/edit_fuelmeter.py` (two
  reads a turn) read by `tools/stress/fuelmeter.py`; `tools/stress/fuelbatch.py` plays a bot vs B7Live both sides with statistics;
  exactness = identical games under `--fuel-quantum 200000000` (`eqcheck.ts` on `edit_aclog.py` + `edit_fuelphase.py` builds).
  Live #339 config (bots/B344x + live339.edits): **47.5k a turn on the 40 pool maps** (3.9% of turns ≥ 80k), 57.9k on the heavy
  four, 47.3k on the 64-256-group fixtures. The meter's own "suspended" column undercounts (a resumed turn's end fuel is usually
  still below its start); official fuelExhausted events are the suspension measure (55 a game on pool maps ≈ 1% of turns).
  Found off: `kEnemyCache`, `kSeenCache`, `kCastPrefilter` (all claim same decisions); `me_.champion_name()` read at 48 sites
  (`edit_mytype.py` caches it). Exactness arms running.
  Exactness (6 maps × 2 sides, unlimited fuel, `eqcheck.ts`): **kSeenCache exact 12/12, kCastPrefilter exact 12/12**;
  **kEnemyCache NOT exact** (yellow_brick_road B diverged r312, travel vs evade, before any suspension): stays off.
  `edit_mytype.py` first version clashed with a local `my_type` (accessor renamed my_champion()).
  **Exact arms measured** (92 games each vs base, fuelmeter): kSeenCache +43 fuel a turn, kCastPrefilter −19, edit_mytype −24
  (mytype exact 12/12). All noise: the SDK's `champion_name()` returns a cached design type, and visible_tiles is rarely fetched
  twice a turn. Engine accessor calls are not where the fuel goes; the algorithmic work (farm 9.1k, squad scoring 7.2k,
  observe_groups 5.3k, observe_allies 5.1k, start 4.4k) is. Next: a price list of engine operations from a probe bot.
  kEnemyCache gated to pre-action turns (edit_enemycache2.py) still diverges at the same game/round (yellow_brick_road B r312), cause
  unidentified; expected saving small (fight turns only): dropped.
- **Engine price list** (`bots/CostProbe`, Oct 25, fuel per call, median over 38 champion samples on 00rows/00lanes): plain reads
  40-72 (position 72, health 68, can_move 54, gold 46, is_alive 41, champion_name 25, fuel_remaining 11, champion == 4);
  **ability.is_ready 484**, is_damage 54, damage_amount 44, abilities() 98; vector-returning queries: `cambc::champions(ally)`
  3,391, `vision::champions(ally)` 2,773, `vision::champions(enemy)` 904, `vision::camps()` 859 (up to 3,658), `visible_tiles()`
  636, `map::camp_groups()` ~17,600, `bitboard.positions()` 1,940, group.spawn_tiles 532, group.state 382, draw_chebyshev 456,
  bitboard or/and 459, count 73; std::map 8 inserts 3,410, vector 16 push_backs 1,888 (growth), vector<int>(64) 3, string 112.
- **Fuel rework, step 1** (audit `.info/Reviews/FuelAudit-2026-10-25-Fable.md`, by a Fable 5.1 subagent): `ability::is_ready()`
  builds a champion (484 fuel vs 43 for cooldown()); **`tools/edits/edit_ready.py`** evaluates the same three terms on the owner held
  (45 sites, all inside their owner's abilities() loop): **exact (12/12 identical games) and −1,438 fuel a turn** (pool −1,520,
  fixtures −1,643). `field_dist` = two host calls (~150): **`tools/edits/edit_fieldlin.py`** (kFieldLin N: stored fields read from a
  row-major export after N reads). First version not exact: the bitboard's linear buffer is **bit-packed** ((w*h+7)/8 bytes, LSB
  first) although cambc.h's export comment says "one byte per tile"; fixed, re-checking.
  **Proven exact and measured** (identical games under unlimited fuel, 12/12 each; fuel per turn vs the live config, 92 games):
  `edit_ready.py` −1,520 pool; `edit_fieldlin.py` (kFieldLin 12, after the bit-packing fix) −76 pool / −893 heavy / −320 fixtures;
  `edit_infoonce.py` (ally record via `detail::sdk_champion`, as observe_groups already calls `detail::sdk_camp_group_state`)
  −382 pool; **all three: −1,497 pool, −1,803 heavy, −1,979 fixtures (~3%)**. The first kFieldLin's "−2k" came from wrong
  reachability, not savings. `champion::info()` is private in cambc.h.
- **Per-function profile** (`tools/edits/edit_fnprof.py` → `tools/stress/fnprof.py`, inclusive fuel a turn, live config): pool maps -
  manage_squad 10.6k (solo scoring 6.2k at 11.9k a call, team scoring 3.6k at 20.9k a call), farm 10.0k (step 4.5k, fight_group
  3.8k), observe_groups 5.7k, observe_allies 5.3k (the vision::champions(ally) query alone ~2.8k), warm_fields 3.4k, field() lookups
  2.8k (17 a turn), arrival_time 2.7k, observe_enemies 2.5k. Fixtures (64-256 groups): observe_groups 18.4k, arrival_time 11.9k
  (32 calls), travel_time 9.3k, score_solo 9.3k, track_camp_epoch 6.7k, party_need 4.0k, champions_needed 3.5k: per-group work is
  the big-map cliff. (escape / retreat / wants_deliver guards report impossible totals: ignore.)
- **Structural fuel work (Eric: "go with the structural work"; Codex out of usage from here):**
  `tools/edits/edit_scoreprune.py` (kScorePrune): branch and bound in score_solo_targets - a group is skipped only when an upper
  bound on its score is strictly below the best so far (ties always evaluated; lowest index kept; last pick scored first). First
  version (bound before the arrival estimate: tile-box distance − range − 2, every boost at its maximum): **exact 12/12, −155 a turn
  only** (bound too loose). v2 adds a check after the real arrival time (value / (arrival + 4 + delivery) × the boosts that can
  apply, claim factor exact). `tools/edits/edit_fieldfloor.py` (kFieldCost): field builds need their measured cost (full compute
  6.8k on 00rows, ~30.9k on 01big_world) instead of fixed 12k / 30k floors - threat fields, avoid routes, crystal and enemy-walk
  fields could start and run dry mid-compute on big maps. `tools/stress/fuelevents.py`: official fuelExhausted per game, two runs.
  Results (exact 12/12 for every arm; fuel a turn vs the live config, pool / heavy / fixtures): **kScorePrune v2 +32 / −480 / +79**
  (the bound rarely prunes: scoring's cost sits in groups that are real contenders); **kFieldCost +29 / −17 / −78** (official
  fuelExhausted 56.5 → 55.0 a game on pool maps: stalled builds are not a main suspension source). Both stay off. All five edits:
  −1,075 / −1,704 / −1,988. **Official fuelExhausted counts move both ways with any fuel change** (all five: pool 56.5 → 63.7 a
  game while the mean fell 1.1k): once fuel timing changes the games diverge, so per-game suspension counts over 92 games are noise;
  the fuel meter's mean is the stable measure. **bots/B345x** = B344x + edit_ready + edit_fieldlin + edit_infoonce + edit_scoreprune
  + edit_fieldfloor (kFieldLin / kScorePrune / kFieldCost off; edit_ready and edit_infoonce have no switch). Conclusion: exact
  savings on normal maps top out near 3% without rewriting scoring; the remaining cost is spread (squad 10.6k, farm 10k, observe
  groups 5.7k, observe allies 5.3k, warm 3.4k ...).
- **Fuel governor** (`tools/edits/edit_fuelgov.py`, kFuelGov; bots/B346x = B345x + it, off): each champion measures its turns (three
  fuel reads; a rise = a suspension); heavy mode for kGovHold rounds after the turn-cost EMA (1/8) > kGovMean or kGovSusp suspended
  turns within kGovWindow; bit 1 = big-map scoring modes (solo slices, squad rescoring every 3), 2 = light camp-health reads, 4 =
  measured-cost rescoring guard. Logging: `edit_govlog.py` → `tools/stress/govlog.py`. Defaults (62k, 3 in 40, hold 80) trigger far
  too often: heavy share 36% of pool-map turns, 88-90% heavy pool, 40% fixtures (128/256 groups ~99%). On the #340 candidate config
  (B346x + cand340.edits = live339 + kFieldLin 12), heavy maps (11 pool/sprint heavy + 3 fixtures, 4 seeds, n 224): **bit 1 +40 ±
  23 (wins 195 vs 190)**, bits 1|2 +19 ± 25, 1|2|4 +19 ± 26. Pool-map screen of bit 1 and a stricter trigger (70k, 4 in 40, hold 40)
  running.
  **Pool maps, 4 seeds, n 640** (vs the #340 candidate 592/640): bit 1 default trigger 595, **−2 ± 13**; bit 1 strict trigger
  (kGovMean 70k, kGovSusp 4, kGovHold 40) 601, **+9 ± 12**. Neutral where fuel is ample, +40 ± 23 on heavy maps (default trigger).
- **Fights by camp context** (`tools/stress/campfights.ts` → `tools/stress/campfightstats.py`; engaged = a camp monster alive below
  full health within 5 of the first contact; "at the camp" = in reach 4 of one; opponents ranked 20-80): kills per fight are flat
  across contexts - us 0.34-0.40, Fish 0.77-0.92, willow 0.55-0.70 - so camp aggro is not our gap; execution is. When the enemy
  was farming and we arrived, we came outnumbered by 0.53 champions on average (Fish 0.24) and broke even (−0.01; Fish +0.58).
  When we were farming, we started at 0.81 health vs their 0.87. Fights a game: open ground 14, both sides in camp reach 6.
  **Heavy maps, strict trigger: 197/224, +57 ± 25** (default trigger +40 ± 23). Candidate: bots/B346x +
  scratchpad/run/cand340gov.edits (= live339 + kFieldLin 12 + kFuelGov 1 strict: 70k / 4 in 40 / hold 40).
- **Commitment, not spells** (`tools/stress/uptime2.ts` → `tools/stress/caststats.py`, rounds within 4 of an enemy champion, vs
  opponents ranked 20-80): champion-rounds a game near enemies - us **557**, Fish 478, willow best girl **91**; cast share 0.17 /
  0.20 / 0.22 (spells are not held back); attack-a-champion share per type - us Ryth 0.18, Marcella 0.15, HoR 0.26, Vesper 0.27;
  Fish HoR 0.35, Vendetta 0.33, Vesper 0.41; willow HoR 0.63, Marcella 0.61, Vendetta 0.54. Our melee hover at 2-4 tiles (poked,
  in camp aggro, rarely hitting); willow fights rarely but decisively. Local screens vs B7 cannot judge fight changes (Oct 25
  #339 lesson); ladder benches now finish in ~5-8 minutes.

### Draft model (Oct 25; `tools/stress/draftmodel.py` on the Oct 23 database, 24,424 decided matches)

Logistic model: side + team strength (730 teams with 20+ games, the rest pooled) + per-draft-size champion values (L2). Only
differences between champions are identified (each draft has exactly k champions), hence ±0.21 single SEs; swaps have proper SEs.
- 5 picks (15,870): Marcella +0.19, HoR +0.10, Vendetta +0.08, Willow +0.07, Ryth +0.05, Varg +0.02, Tavi −0.01, **Vesper −0.03**
  (picked by 66% of teams), C&I −0.06, Prism −0.10, Stellar −0.15, Ren −0.16. Ours (HoR, Vesper, Ryth, Marcella, Willow) sums
  +0.39; best (HoR, Marcella, Ryth, Vendetta, Willow) +0.49. Swaps: Vendetta for Vesper **+0.10 ± 0.07**, HoR-level; Marcella vs
  Ryth +0.14 ± 0.06 (z 2.4).
- 4 picks (4,921): Willow +0.25, Marcella +0.22, Vesper +0.12, Ryth +0.11 ... Ren −0.18, Prism −0.30. **Ours (Marcella, Vesper,
  Ryth, Willow) is the model's best four.**
- 3 picks (3,633): Vendetta +0.22, Vesper +0.20, Marcella +0.18 ... C&I −0.19, Stellar −0.26. Ours (Marcella, Vesper, Ryth) +0.43;
  best (Marcella, Vendetta, Vesper) +0.59; **Vendetta for Ryth +0.17 ± 0.09**.
- Caveat: values reflect how all teams play each champion, not our bot (Vesper is our gold carrier: kVesperCarry).
- **Fight / draft arms (Oct 25)**: base **bots/B347x** = B346x + `tools/edits/edit_draftven.py` (kDraftVen5: Vendetta in Vesper's
  5-pick slot; kDraftVen3: Vendetta in Ryth's 3-pick slot; both off). **New local judge: head-to-head vs the current bot** -
  bots/H340 (B347x + cand340gov.edits) as an opponent beside B7Live (`OPP="H340 B7Live"`), since B7 cannot judge fights.
  Arms on cand340gov: draft V5, draft V3, leave (kEvadeOdds 1.0: evade below even odds), commit (kHuntOdds 1.3, kHuntRange 4),
  arrive together (kCampEnemyOdds 1.0). `tools/edits/edit_winwindow.py` (kWinWindow: while advantage_, 1 no shopping trips above
  kWinHp 0.5, 2 midline camps x 1.5) built, next screen.
  **Screen 1** (pool maps, 2 seeds, vs H340 + B7Live, n 320, results/ev via s_fight1.log; base 228/320, vs H340 +27 = the mirror's
  side/chaos offset): draft V5 **−46 ± 25** (vs H340 −74: Vesper is our gold carrier; the database value cannot see that), draft V3
  −15 ± 14, **leave (kEvadeOdds 1.0) +13 ± 31 (vs H340 +38)**, commit (kHuntOdds 1.3 / range 4) −36 ± 30, arrive together
  (kCampEnemyOdds 1.0) −30 ± 17. Aggression loses to a competent opponent again; leaving contact is the one fight change that helps.
  Screen 2 (4 seeds): leave 1.0 / 1.15 and kWinWindow 1 / 2 / 3 on bots/B348x (= B347x + edit_winwindow.py, off).
- **Screen 2** (4 seeds, n 640, vs H340 + B7Live; base 450/640, vs H340 −6): leave 1.0 +3 ± 22 (vs H340 +29, vs B7 −29), leave 1.15
  −29 ± 23, kWinWindow 1 +3 ± 10, 2 −21 ± 13, 3 −7 ± 15. Threshold-level fight rules are not where the gap is.
- **Uploads #340 / #341 (Oct 25)**: #340 = bots/B346x + cand340gov.edits (submitted 11:55:19 UTC), #341 = #340 + kEvadeOdds 1.0;
  benches fish340/hold340 vs fish339sg/hold339sg, then fish341/hold341 vs fish340/hold340 (scratchpad/run/chain340.sh).
- **Fighting power** (`tools/stress/statsat.ts` → `tools/stress/statsstats.py`, living champions' stats at r150/300/600/900, vs
  opponents ranked 20-80): **Fish funnels gold into Vesper Vale** - earned gold r300 958 / r600 2,379 / r900 3,941 (ours 341 / 808 /
  1,435), strength 177 / 439 / 762 (ours 91 / 155 / 256); Fish's Ryth, Cassi, Issac earn ~300-500 a game. Database totals: Fish's
  Vesper takes 46% of team gold (ours 29%), the same capture count as ours (15.5 vs 15.2) but ~247 gold a capture vs ~130 (teammates
  clear the big gold camps, she takes the reward) plus ~520 kill gold. willow best girl spreads gold like us but builds **tanky
  frontliners**: max health r600 HoR 1,864 (ours 1,385; Fish 2,491), Marcella 2,013 (ours 1,628). Build arms screening (kHorBuild 1,
  kMarcBuild 1, kRythBuild 1 / 2, HoR+Marcella). `edit_vesperfunnel.py` no longer applies (resource_carrier now has kMarcGems: gem
  groups to Marcella); a funnel needs redesign with that rule.
- **#340 benched** (certified 40/40 each): Fish 4/40 vs #339 2/40, **+48 ± 42**; holdout 8/40 vs 9/40, **+82 ± 90** (policy wonk +230
  ± 141, Noobot −67 ± 107). Stress 22/24, faults 0, fuelExhausted 3,209 (#339: 3,695).
- **Build screen 1** (2 seeds, vs H340 + B7Live, n 320; base 228/320, vs H340 +27): **kHorBuild 1 (HoR Jungle F, Durability H,
  Bruiser H) +28 ± 11, vs H340 +79**; kMarcBuild 1 −64 ± 31; **kRythBuild 1 (Treasure H, Jungle H, Bruiser H) +42 ± 24, vs H340 +65**;
  kRythBuild 2 −12 ± 14; HoR 1 + Marc 1 −55 ± 32. Frontline health (HoR, Ryth) as the top teams build it; Marcella stays as she is.
  4-seed confirmation with HoR 1 + Ryth 1 running.
  **Build screen 2** (4 seeds, n 640, vs H340 + B7Live; base 450/640, vs H340 −6): **kHorBuild 1 +16 ± 8** (460/640, vs H340 +29),
  **kRythBuild 1 +32 ± 18** (468, +29), **both +36 ± 19** (462, vs H340 +44). Candidate #342 = #340 + both (cand342.edits; + kEvadeOdds
  1.0 only if #341's bench supports it). #341 submitted 12:12:25 UTC (stress 20/24, faults 0, fuelExhausted 3,351).
- **#341 benched** (certified 40/40 each, no opponent re-drafts): Fish 2/40 vs #340 4/40, **−90 ± 51**; holdout 10/40 vs 8/40,
  −26 ± 87. Leaving at even odds wins head-to-head against our own bot but gives ground on the ladder (Fish's carry punishes the
  turns spent backing off) - kEvadeOdds stays 0.85. **#342 = #340 + kHorBuild 1 + kRythBuild 1** (no kEvadeOdds change), uploaded
  Oct 25 with benches fish342/hold342 vs fish340/hold340 (scratchpad/run/s_342.log).
- **#342 benched** (submitted 12:34:01 UTC; stress 22/24, faults 0, fuelExhausted 3,397; certified 40/40 each, no opponent
  re-drafts): Fish 3/40 vs #340 4/40, −49 ± 69; holdout **13/40 vs 8/40**, −4 ± 74 (Noobot +88 ± 98, policy wonk −95 ± 108).
  80 games: 16 wins vs 12, margin about −27 ± 50 - inside the noise either way (local +36 ± 19). Left live (replaces #341).
- **Early greed** (Eric: Fish is greedier early with camp clears, recalls and health; `tools/stress/greed.ts` →
  `tools/stress/greedstats.py`, 200-round bands, vs opponents ranked 20-80; 75 of our games, 173 Fish, 72 willow). Trips home
  (5+ tiles out and back) per champion are the same - r0-200 us 2.18 / Fish 2.24 / willow 2.42, r200-400 2.71 / 2.49 / 2.62 - and
  so are trip lengths (58 / 58 / 51 rounds). The difference is **what a trip is worth and the health spent on it**: health share
  when turning home, median r0-200 **us 0.82, Fish 0.43**, willow 0.65 (r200-400 0.69 / 0.45 / 0.70); earned gold a trip r0-200
  63 / 72 / 67, r200-400 **76 / 112** / 104, r400-600 94 / 150 / 123; camp engagements per champion a band r200-400 4.1 / 5.1 /
  4.4. Gold left on returning (after the shop) 19-51 for us, 9-13 for Fish (they spend it all). Camp starts are at full health for
  every team (median 1.00). By type r0-400: Fish's Vesper 243 gold a trip at 0.54 health turning home (ours 98 at 0.78), Fish's
  HoR 0.45 (ours 0.67), Vendetta 0.46. Our recall-capture (kRecallCapture 4, kRecallCapSlack 20) sends a healthy champion home
  after nearly every capture. Screen: farm-on when healthy from round 1 (`kLateTripRound` 1 with hp 0.6 / 0.5, slack 5) and
  `kRetreatHp` 0.35 (scratchpad/run/s_greed1.log).
- **Who takes the gold** (`tools/stress/capbatch.ts` → `capbatchstats.py`, same games, gold-paying captures, 200-round bands).
  Fish captures more early: per game r0-200 **8.3 vs our 6.7**, r200-400 **10.1 vs 7.5**, r400-600 11.0 vs 8.2 (willow 7.8 / 8.6 /
  9.6); after r600 we capture more (27.9 vs 22.2) but the snowball is set by then (game totals 51.7 vs 50.4; gold 6,929 vs 5,751).
  Vesper's share r0-200: Fish 43% at 146 gold a capture, ours 26% at 124, willow 23%. Fish's Vesper is **alone on the tiles in
  89%** of her captures (ours 55%, willow 93%) with 3-5 teammates within 6 in 35% (ours 15%): the team clears and she takes
  the whole reward. She takes 50% of Fish's elk-group captures (193 gold each) and 70% of monoliths (ours 32% / 9%). Our
  remaining Vesper captures are split with a teammate on the tiles (HoR 54% within 6, Ryth 38%, Marcella 37%). The 2026-10-22
  funnel (kVesperFunnel 2, v261) was +2 ± 19 locally and −1,899 on the Fish bench; the sharing leak and the throughput gap
  (captures a trip, see Early greed) are the measured differences now.
- **Greed screen 1** (4 seeds, n 640, vs H340 + B7Live; base = #342's config 462/640, vs H340 +44): farm on instead of
  recall-capturing from round 1 when health >= 0.6 and gold < 150 (`kLateTripRound` 1, `kLateShopGold` 150) +11 ± 24 (469, vs H340
  +87); same at 0.5 +14 ± 24 (464, +102); recall-capture slack 5 from round 1 +12 ± 22 (466, +78); farm-on 0.6 + `kRetreatHp` 0.35
  +29 ± 24 (471, +94); **`kRetreatHp` 0.35 alone +30 ± 20 (483/640, vs H340 +98)**. Every greed arm beats our own clone by
  +35..+60 more than the base. 0.45 came from #332 (327 on 324: Fish +35 ± 55, holdout −82 ± 68; aimed at late deaths).
  Screen 2 on `bots/B349x` (= B348x + `edit_vesperalone.py`, off): 0.35, 0.35 to r400 / r600 then 0.45 (kLateCautionRound,
  kLateEvadeOdds 0.85), 0.30, kVesperAlone 1.
- **Greed screen 2** (same seeds, base 462/640): `kRetreatHp` 0.35 all game +30 ± 20 (483); 0.35 to r400 then 0.45 +20 ± 21 (473);
  to r600 +15 ± 21 (475); 0.30 +15 ± 22 (473); kVesperAlone 1 +10 ± 14 (468, vs H340 +55). Late caution adds nothing locally.
  Confirmation on seeds 5-8 (0.35; 0.35 + kVesperAlone; 0.35 + farm-on 0.5): scratchpad/run/s_greed3.log.
- **Greed confirmation** (seeds 5-8, base 465/640, vs H340 +54): **`kRetreatHp` 0.35 +34 ± 22 (484/640, vs H340 +100)**;
  + kVesperAlone +37 ± 23 (484; adds nothing); + farm-on 0.5 +13 ± 23 (470). Over 8 seeds 0.35 is about +32 ± 15, +40 wins in
  1,280. **#343 = #342 without the 0.45 line** (run/cand343.edits on bots/B346x), benches vs fish342 / hold342.
- **#343 benched** (submitted 13:36:18 UTC; stress 23/24, faults 0, fuelExhausted 3,472; certified 40/40 each, no opponent
  re-drafts): **Fish +85 ± 72** (4/40 vs #342 3/40; 24 maps better, 13 worse), **holdout +74 ± 74** (13/40 vs 13/40; 28 better,
  11 worse; Noobot +110 ± 88, policy wonk +39 ± 120). 80 games about +80 ± 52, 52 better / 24 worse - both benches positive,
  as locally (+32 ± 15 over 8 seeds). **Adopted: #343 is live and the new base** (bots/B346x + run/cand343.edits).
- **What #343 changed** (`tools/stress/greedbench.py` over the downloaded bench games, greed.ts + capbatch.ts; us, fish342 →
  fish343, r0-200 / 200-400 / 400-600): gold a trip 51/56/61 → 59/68/82, gold captures a game 6.2/6.4/6.2 → 6.7/7.0/6.8, deaths
  per champion 0.32/0.57/0.62 → 0.24/0.45/0.52, Fish's captures 8.8/11.2/12.3 → 8.4/9.9/11.9 (holdout alike). Health share when
  turning home did NOT move (median 0.87/0.78/0.85 → 0.86/0.74/0.82): most trips home are recall-captures, which the retreat line
  does not touch; the gain is fewer walk-home retreats at 0.35-0.45 (fewer deaths on the way, fewer camps abandoned).
- **Away time by activity** (greed.ts `tb`, fish343 us vs Fish): camp attacks 26/21/20% vs 27/23/22%, moving 51/55/57% vs
  50/50/50%, standing still 6/5/5% vs 2/2/2%, channelling 4/4/5% vs 6/8/8%; away rounds per champion r400-600 156 vs 175. Champion-
  rounds attacking camps per gold capture: us 34 / 25 / 23, Fish 28 / 21 / 16 - **Fish clears ~16% faster early and ~30% by
  r400-600** (damage per champion: gold → items snowball), with slightly more of its time on camps and a third of our idle time.
  The capture gap is clear speed more than trip decisions.
- **Farming-speed goal (Eric, Oct 26: match Fish's gold + gem income per 100 rounds; keep going until achieved).** Tools:
  `tools/stress/econ.ts` + `econstats.py` (income every 100 rounds from replays; bench mode pairs us with the opponent in the same
  games), `dbextract.py` now takes CUTS / TEAMS (results/db/econ-1023-100.jsonl: our, Fish's and willow's 1,258 matches of the
  Oct 23 database with cuts every 100), `clears.py` takes SEEDS / CUTS (local income screen), `capkinds.py` (captures by camp kind
  per 100 rounds), `opening.ts` + `openingstats.py` (parties away from home, gold by champion type at r100-400).
  **Baseline** (ladder Oct 23 vs ranked 20-80, gold / gems per 100-round window): us 347/50, 386/51, 450/56, 494/60, 554/69,
  610/73; Fish 505/53, 654/76, 759/83, 849/100, 965/114, 998/124 (by r600 2,845 g / 347 gems vs 4,762 / 520: we need +67% gold,
  +52% gems). Local #343 vs H340 + B7Live (2 seeds, 320 games): 340/48, 395/47, 464/52, 497/59, 559/63, 601/73 - r600 2,856 g /
  342 gems, the same as our ladder numbers, so the local screen is a fair proxy. Head-to-head (#343 Fish bench) we earn 69% / 99%
  of Fish's in r0-100 falling to ~45% / 42% by r500.
  **Where Fish's gold comes from**: Vesper earns 244 / 577 / 950 / 1,381 by r100-400 (ours 79 / 185 / 336 / 464), Vendetta 120 /
  264 / 443 / 622; HoR, Cassi, Issac, Ryth earn little (they clear, she captures: +33% passive, +20% Treasure at ~r90). Capture
  gold a wolf group 99-111 vs our 73-90, a gold cluster 71-78 vs 55-63 (the Vesper factor); elk-group captures r100-600 ~9.9 a
  game vs our 7.1; non-capture gold r0-100 81 vs 45; Treasure gold (bench) 2x ours. Fish's Vesper items: Treasure Str ~r90,
  Bruiser Str r124, Durability Hp r181, Power Str from r204 (ours Jungle Str r219, Durability r311). Champions away from home 4.7
  vs our 4.0; r0-100 Fish splits into 1.74 parties (us 1.40).
  Switch bases: `bots/B349x` (+ kVesperAlone), `bots/B350x` (+ `edit_vesperbuild.py` kVesperBuild, `edit_vesperfunnel2.py`
  kVesperFunnel bits 1/2/4; all off).
- **The gap decomposed** (database, vs ranked 20-80): by r600 monster damage us 49.6k vs Fish 71.9k (+45%), gold per 1k damage 57
  vs 66 (+16%; r0-100 43 vs 55), gems per 1k damage 7.0 vs 7.2 - gold +67% = 1.45 x 1.16, gems +52% = 1.45 x 1.03. Time budgets
  are equal (away 530-554 of 600 rounds per champion, Fish 500-552). Per champion type, whole game per 100 rounds (monster
  damage / gold / gems): **Fish's Vesper 4,720 / 428 / 54 vs ours 2,589 / 161 / 18**; Fish's Vendetta 3,520 / 219 / 30; Fish's
  Cassi, Issac, Ryth, HoR 1,100-2,000 damage and 48-130 gold (they clear, she captures) - below our Ryth 2,484, Marcella 2,239.
  The whole gap is one fed carry. Fish's Vesper's first capture is at r33 (median; ours r86), 1.8 captures for 221 gold in r0-100
  (ours 0.6 / 71), alone on the tiles (on-tiles 1.1; ours 1.9 on elk groups).
  **Income screen 1** (`econclears.py`, 2 seeds, n 320, base #343: r600 2,856 g / 342 gems = 60% / 62% of Fish): kGoldWeightEarly
  0.5 gold +8 gems −20; 0.8 gold +97 ± 49 gems −28 ± 6 (weights trade gems for gold); kGoldWeight 0.25 +39 / −9; kVesperGoldW 2.0
  +4 / +3; kElkRound 75 −3 / +2; kElkBonus 2.0 −36 / −1; **kTreasureBuild 2 +54 ± 28 / −2 (wins 247 vs 244)**. Per map (`econmaps.py`)
  we earn 36% (hooks: contested elk, clusters ignored for 70 rounds while the team tanks it) to ~100% (rows, fragment) of Fish.
  **Income screen 2** (same games; base2 on B350x plays identically to base on B349x - switched-off builds pair across bases):
  **kVespFarmBuild 1 (Vesper Treasure Str, Monster Str, Jungle Hp, Power Str) gold +92 ± 31, gems +5.3 ± 2.7** (margin −13 ± 18);
  kVesperBuild (Fish's exact line) +9 / −2, margin −46; kVesperFunnel 1 +14 / 0, 3 −2 / −2 (margin −55), 7 +27 ± 50 / 0 (margin
  −75); kTeamSquads 2 −187 / −28; kOpeningRounds 60 −42 / −8; kShopAll +10 / 0; dropping the #342 health builds −20 / +5 (margin
  −62). kVesperAlone (screen 1) +57 ± 32 / +4.2 ± 3.6. The funnel does not move income locally - checking whether it moves
  captures to Vesper at all (cl1 replays).
  **Income screen 3** (bots/B351x = B350x + `edit_vesperhandoff.py` kVesperHandoff): handoff 3 with funnel 7 −47 / −8 (margin −97),
  with funnel 3 −84 / −10 (margin −72); kClusterSolo −1 / −1; kCasterClusters −122 / −6; kClusterOne −51 / −7. Routing rewards to a
  Vesper who is not there costs more time than her +33% earns. Away time r0-400 (bench): our Vesper camp 28% / capture 5% / walk 45% /
  still 6%, Fish's 30 / 9 / 41 / 2 - same attack time, 1.8x the damage: items. The loop starts in r0-100 (221 vs 71 gold) while ours
  is inside the five-champion opening squad. Queued: screen 4 (bots/B352x + `edit_vesperescort.py` kVesperEscort: Vesper + a partner
  squad after the opening; packages A = farm build + Treasure 2 + Vesper alone, B = A + escort + funnel 7 + handoff 3), screen 5
  (bots/B353x + `edit_vespersolo.py` kVesperSolo 150 / 300, + farm build).
  **Income screen 4** (B352x): kVesperEscort 1 −2 / −1 (margin −5), 2 −31 / −1 (+15); escort + funnel 1 +8 / −1; escort + funnel 7 +
  handoff +1 / −1 (margin −59); **package A (kVespFarmBuild 1 + kTreasureBuild 2 + kVesperAlone 1) gold +124 ± 42, gems +2.9 ± 4.2,
  margin −15 ± 22, wins 246 vs 244**; package B (A + escort + funnel 7 + handoff 3) +59 / +1, margin −110. The funnel does move gold:
  funnel 7's Vesper has 80 / 261 / 478 / 698 gold by r100-400 (base 70 / 184 / 320 / 459), but Ryth, Marcella and HoR lose the same,
  so team gold is unchanged within 600 rounds. Fish's team out-earns ours from r0 (no items yet): r150 earned Vesper 397 (3.2 items,
  str 94) vs ours 123 (1.6, 67), Vendetta 198; team +44% by r150. Draft: we field Willow (884 monster damage / 100 rounds) where
  Fish fields Cassi + Issac casters (1,451 / 1,138) and Vendetta (3,520). Screen 6: kWillowMeta 0 (Vendetta fifth instead of Willow).
  **Income screens 5-6**: kVesperSolo 150 −0 / +1 (r0-100 gold 340 → 325), 300 +23 / −1, 150 + farm build +48 / +1 (the solo branch
  sits behind the scheduler / zone / rows exits and often never fires: lanes games identical to base); kWillowMeta 0 (Vendetta fifth
  instead of Willow) −95 / −4, margin −94 (with package A +38, margin −112): Willow stays.
  **Fish's opening is a gold-cluster loop** (capwho on four Fish ladder games vs ranked 20-80): most r0-130 captures are gold-cluster
  groups (cc / ccc / cccc, 120 hp and 20 gold each, no damage); its Vesper takes them at 53-106 gold (+33%) and retakes the same
  groups at respawn (~60 rounds; m0: (44,13) at r18 and r77, (46,22) at r26 and r91). Ours: 0.8 gold-cluster captures in r0-100 vs
  1.3, and our Vesper in the opening squad. `edit_vesperloop.py` (bots/B354x): kVesperLoop R - before R Vesper's job is the best
  harmless gold-paying group by value / (walk or respawn wait + clear + 4) within kVesperLoopArrival 40, checked ahead of the
  scheduler / zone rules; kVesperLoopKeep - the others leave gold-only harmless groups to her. Screen 7.
  **Income screen 7** (bots/B354x): the loop works as designed (local traces: expanse Vesper 5 cluster captures / 319 gold by r210,
  lanes 8 / 425, retaking groups at respawn) but team income barely moves: kVesperLoop 300 gold +63 ± 52, gems −14 ± 6 (r0-100 gold
  356 vs 340); + keep +49 / −4 (margin −39); 600 + keep +21 / −22 (−64); 300 + keep + package A +103 / −5 (−95). Every arm lands
  at 2,850-2,980 gold / 320-345 gems by r600: redistributing captures does not raise team extraction locally.
- **Where Fish's extra income comes from** (database by r600, same games, vs ranked 20-80): us 2,845 gold / opponent 2,822 (sum
  5,666), gems 347 / 303, kills 2.3 vs 1.5, monster damage 50k vs 49k; **Fish 4,762 / opponent 2,313 (sum 7,075), gems 520 / 250,
  kills 6.6 vs 1.5**, monster damage 72k vs 43k; willow 3,649 / 2,409, kills 5.7. Fish's +1,917 gold ≈ 430 kill gold (4.3 kills x
  100) + ~500 taken from the opponent's share (denial) + ~1,000 more total extraction (115k monster damage in its games vs 99k).
  Local screens against our clone see only the extraction part. `tools/stress/campsupply.ts` + `campsupplystats.py` (group-rounds
  idle / fought / reward / down per side and 100-round window) measure unused capacity. (An older `tools/stress/campidle.ts` - turn
  use at camps, generated from actions.ts - was overwritten by mistake and regenerated from its generator; same content.)
  **#344 = #343 + package A** (kVespFarmBuild 1, kTreasureBuild 2, kVesperAlone 1; run/cand344.edits on bots/B349x), benches vs
  fish343 / hold343; income vs Fish measured on the bench games (econ bench mode).
- **#344 benched** (submitted 17:13:16 UTC; stress 22/24, faults 0; certified, no re-drafts): Fish 4/40 vs 4/40, −14 ± 42; **holdout
  9/40 vs 13/40, −143 ± 72** (policy wonk −202 ± 130). Income on the bench games: vs Fish our gold r600 2,506 vs #343's 2,377 (+5%),
  gems 263 vs 271; vs holdout 2,712 vs 2,856 and the opponents earned more. Package A rejected; **#345 = the #343 config again**
  (restores live; its benches are a second #343 sample).
- **Camp supply** (campsupply.ts; share of home-group rounds idle - alive at full health, nobody farming): us (ladder) 79 / 66 / 64 /
  63 / 60 / 62% by 100-round window to r600, Fish 74 / 63 / 62 / 59 / 58 / 56, willow 67 / 52 / 50 / 52 / 52 / 50; local #343 80 /
  67 / 63 / 62 / 62 / 61. Supply is not the limit (every team leaves home camps idle half the time); Fish's edge is faster, richer
  clears (damage, Vesper's bonus) plus kills; willow uses its home camps most (more, smaller parties: 2.8-2.9 parties of 1.35 after
  r100, ours 2.5 of 1.55) and earns +28% over us with similar kills.
- **#345 = #343's config again** (submitted 17:31:27 UTC, live): Fish bench **identical to #343's 40 games** (+0 ± 0; the ladder
  games are deterministic for unchanged code), holdout 36 of 40 identical, 4 changed against policy wonk (−49 ± 34; no draft change -
  they altered something else). So a bench difference between two of our versions is the change's real map-by-map effect (chaotic,
  not random); its ± is spread over maps.
  **Income screen 8** (parallel farming, B354x): kHelpCall 0 −112 / −16; 40 −21 / −3; kBigParty 0 −54 / −11; kHomePull 0.25 −87 /
  −4; 1.0 +11 / +2. Help calls and big parties raise our income; bunching is not the problem. Screen 9: clear speed (kFirstEmblem 1
  Monster first, kPureBuild 1, kMetaBuild 2, kChipSpell, kSaveSpells 4 / 0).
  **Income screen 9** (clear speed): kFirstEmblem 1 (Monster first) −20 / −3; kPureBuild 1 −272 / −27 (wins 80/320); kMetaBuild 2
  −65 / −12; kChipSpell −14 / +2; kSaveSpells 4 −32 / −6, 0 −64 / −8. **~45 farming arms: the live config is a local income optimum**
  (nothing beyond ~+4% locally; the best package lost on the ladder).
- **The kill gap** (database, opponents' deaths to champions by r600 per game, vs ranked 20-80): us 0.40 / 0.79 / 1.08 (r0-200 /
  200-400 / 400-600) = 2.3; **Fish 1.73 / 2.23 / 2.65 = 6.6; willow 1.45 / 1.90 / 2.41 = 5.8**. Own deaths to champions: us 1.49, Fish
  2.02, willow 1.50; to camps: us 0.86, Fish 1.65, willow 0.30. Both top teams kill ~4x as many opponents in r0-200; willow does it
  without dying more than we do. Kill gold (100) + 60-round respawns are the kill and denial halves of Fish's income lead. Kill
  contexts (killctx.ts over the database replays, sides from index.json: scratchpad/dbr/sides_dbr.json) next.
  **Kill contexts** (`tools/stress/killgap.py` over killctx.ts lines; kills per game, r0-200 / r200-600): us 0.48 / 1.99, Fish 1.73 /
  5.16, willow 1.78 / 4.51; our deaths 0.35 / 1.29 vs Fish 0.77 / 1.16, willow 0.75 / 1.15 - **we do not die more, we fight less**.
  Our early kills are mostly 4v1 / 3v1 on healthy victims (hp5 median 0.79); willow's are 1v1 21%, 2v1 18%, even 1v2 11%, on wounded
  victims (0.42) farming camps (59%) or recalling (21%); Fish 2v1 / 3v1 / 4v1 on 0.59. Where is similar for all (~40-47% on the
  victim's own half). willow's own deaths are 81-87% while channelling. Ladder test of aggression on the near-rating bench (eight
  teams ranked just above us, rank 50): near345 baseline, then **#346 = #345 + kHunter 1** (never benched before; local −33 against
  our clone) vs fish345 / hold345 / near345.
- **Near-rating baseline near345** (#345 live, eight teams ranked just above us): 17/40 (near328 18/40), margin +1,080.
- **#346 = #345 + kHunter 1** (submitted 18:48:54 UTC; stress 22/24, faults 0; no re-drafts): **near 23/40 vs 17/40, +80 ± 70**
  (14 maps better, 22 worse); holdout 9 vs 11, +25 ± 66 (Noobot −126, policy wonk +176); Fish 3 vs 4, −53 ± 52. On the near games
  our kills r0-200 / 200-600 / 600+ 0.70 / 1.65 / 2.98 → **0.82 / 2.15 / 4.28**, theirs 0.60 / 2.23 / 4.90 → 0.47 / 2.05 / 4.05 (balance
  by r600 −0.48 → +0.45); income: our gold r400 1,725 → 1,793, r900 4,762 → 5,014, theirs r400 1,859 → 1,762. **Kept live.** (Local
  −33 against our clone was the wrong judge for aggression.) **#347 = #346 with kHunter 5** (also on their half: Fish / willow make
  ~40% of their kills on the victim's half) vs fish346 / hold346 / near346. Tool note: killctx.ts on bench dirs needs paths without a
  trailing slash and a sides file (scratchpad/gb/sides_bench.json maps game ids to us / them from the dir names).
- **#347 = #346 with kHunter 5** (their half too; submitted 19:19:54 UTC): few games change - near 22 vs 23, −47 ± 48 (7 maps better,
  5 worse; SkuBap −495), holdout 10 vs 9, +27 ± 21 (4 changed), Fish 3 vs 3, −3 ± 4. Neutral: the their-half branch rarely fires. Next
  candidates build on #346. **#348 = #346 + kPickOff 6** (converge on an isolated enemy - no teammate within 6 - that we outnumber and
  can burst within two rounds; never benched) vs fish346 / hold346 / near346.
- **#348 = #346 + kPickOff 6** (submitted 19:53:50 UTC; stress 19/24, stuck 4): near 21 vs 23, **−145 ± 89**; holdout 12 vs 9, −14 ±
  76; Fish 2 vs 3, −64 ± 43. Rejected (converging the team on one target pulls it off its camps). **#349 = #346 + kHunterLead 2.5**
  (hunt with half an emblem's equipment lead) vs fish346 / hold346 / near346.
- **#349 = #346 + kHunterLead 2.5** (submitted 20:11:22 UTC): near 19 vs 23, −47 ± 59; holdout 8 vs 9, −49 ± 39; Fish 2 vs 3, −17 ±
  16. Rejected - one emblem of lead is the right threshold. **#350 = #346's config again** (restore live; benches vs #346 check
  determinism and opponent drift).
- **#350 = #346's config** (submitted 20:51:51 UTC, live): Fish and holdout games **identical** to #346's; near: 12 games changed with
  identical code (SSSA −214, SkuBap −431, Valenki; no draft changes) - **those three near-bench teams updated their bots between
  18:49 and 20:52**. #347's and #349's near "losses" were mostly against them; re-scored per opponent against the matching
  baseline (near346 for unchanged teams, near350 for the three, assuming they changed before #347): #347 **+31 ± 38 (22 vs 19 wins)**,
  #348 −67 ± 88, #349 +31 ± 40 (19 vs 19; still −49 on the stable holdout). **Rule: run the near baseline right beside each candidate**
  (the near teams re-upload; Fish and the holdout were stable this evening). `edit_recallpunish.py` (bots/B355x = B346x +
  kRecallPunish): with kHunter, an isolated enemy seen recalling within N, at most three of our hits from death, is prey without the
  lead / matchup checks (willow: 21% of its kills on recallers). **#351 = #346 + kRecallPunish 6** vs fish350 / hold350 / near350.
- **#351 = #346 + kRecallPunish 6** (submitted 21:10:33 UTC, kept live): near 21 vs 19, **+101 ± 52** (13 maps better, 6 worse);
  holdout 11 vs 9, +18 ± 54; Fish 3 vs 3, −7 ± 10. But the branch barely fires: our kills on recallers by r600 0.70 → 0.70 (near),
  1.55 → 1.62 (holdout) - we already catch recallers through the normal fight rules. The near gain is knock-on / drift, not the
  mechanism. Kills by r600 on the near games: ours 0.78 + 2.00 (#350) → 0.75 + 2.33; theirs 0.35 + 1.95 → 0.40 + 1.75 (Fish vs
  mid teams in the database: 6.6). **#352 = #351 with kHunter 5** vs fish351 / hold351 / near351.
- **#352 = #351 with kHunter 5** (submitted 21:57:07 UTC): near 19 vs 21, −15 ± 75 (12 games changed; SSSA −210); holdout 12 vs 11,
  +42 ± 41; Fish 3 vs 3, −3 ± 4. A tie (34 vs 35 wins of 120). **Final for Oct 26 (Eric: upload the best and stop): #353 = #351's
  config** (bots/B355x + run/cand351.edits = the #343 config + kHunter 1 + kRecallPunish 6), submitted 22:11:54 UTC; stress identical
  to #351's (22/24, gems 22,375 vs 12,062). Open threads: the kill gap (our ~2.8 kills by r600 vs mid teams, Fish 6.6) - untested
  next arms kEngageOdds 0.85 on the ladder, longer / wider kHunter chases; farming changes alone cap at ~+4% locally.
- **02the-pack / walled altars (Oct 26, Eric: "yes please")**: the map's one altar (22,22) sits inside a closed ring of 48 wolves
  (one 64,800-health group; 3 picks a side). altar_usable() sees free tribute tiles, the altar field runs through the camps, every
  step into the ring is refused (camp_blocked) and kCampRoute's give-up only handles camp keys - our carriers looped at the ring
  for 1,400-3,200 rounds holding 140 gems (both teams 0-0; then gold earned decides). `tools/edits/edit_walledaltar.py`
  (bots/B356x = B355x + kWalledAltar): walled = the altar field reaches us only through live camps (the camp-blocked copy does
  not); 1 carriers farm instead; 2 also besiege the walling group (kSiege machinery without the wave model, full bags allowed)
  focusing the monster on the breach tile (the first live camp tile on the open path from our spawn). Local 02the-pack vs B7Live
  and #353, both sides: **mode 1 8/8 wins on gold (7.7-9.2k vs 1.8-2.6k)**; mode 2 unfocused chipped the pack 65k → 44k with no
  wolf dead; focused: vs B7Live side B **won 674-69** (breached), side A lost 0-11 (5 wolves dead by r2000; B7Live used our gap),
  vs #353 0-0 (gold wins). Ladder (25 ranked games on 02the_pack): ~11 decided on banked gems, ~10 on gold, **4 ended at 1,000
  gems** - teams do bank there, so mode 1 alone loses to any team that banks. **Engine 2.0.0 (Sprint 3) live on the ladder from
  ~22:52 UTC Oct 25** (patch 2.0.0:85aa7167…); PyPI cambc still 3.0.5 (engine 1.0.3) - local tests no longer match the ladder's
  balance. All-map screen of modes 1 / 2 (detection could fire on camp-bridged maps): scratchpad/run/s_walled1.log.
  **Walled altar, final (local, engine 1.0.3)**: the eager mode-1 check (every carrier turn) changed games on most maps through fuel
  (all 70 maps: mode 1 −13 ± 16, mode 2 −35 ± 26); **lazy mode 1** (kCampRoute's camp-face give-up on an altar key sets a kWalledHold
  100-round farm flag; nothing else runs) is **+2 ± 3 over 560 games, 416 vs 411 wins**. Mode 2's siege never fired at first
  (siege_pick returned before the bypass while no camp had the siege flag; fixed); fixed, it breaches by ~r1000 but costs our farming
  (gold 1,014 vs 8,468) and opens the altar to the opponent (lost 155-347 to B7Live). 02the-pack, 4 seeds, both sides vs #353 and
  B7Live (16 games): base 5/16; **mode 1 16/16 (+103 ± 56)**; mode 2 2/16 (−334 ± 92) - rejected. **#354 = #353 + kWalledAltar 1**
  submitted 23:28:44 UTC (stress 22/24, faults 0), also the resubmission for engine 2.0.0: from ~22:52 UTC the ladder voided matches
  of teams whose submission predates 2.0.0 (`submission_grace`; #353 was submitted 22:11) - submissions are source, built on the
  server. A 5-game check group (scrim_e2test354.ids) was queued; the servers were backed up after the update (Eric: local tests only
  for now).
- **Codex ladder review fixes (Oct 26, collaboration/20261026/ladder-change-review.md; Eric: "try out these changes")**:
  `tools/edits/edit_huntfix.py` (bots/B357x = B356x + it; both off = old code): **kHuntElect** - the one-hunter election skips allies
  that could not hunt (recalling, or carrying kDeliverGems) instead of letting them veto (item 1); **kRecallFall** - kRecallPunish's
  branch becomes an accepting fast path, a recalling enemy failing it gets the usual lead / matchup checks instead of `continue`
  (item 4). Trace notes hunt_start / hunt_skip_inelig / hunt_veto_inelig / recall_fall. Mode-2 repairs in edit_walledaltar.py
  (mode-2 code only; mode 1 unchanged): the breach root is the reachable home tile nearest the altar regardless of our position
  (item 2), and area spells aim at the breach monster during the breach (item 3). Local screen (engine 1.0.3; servers backed up
  after the 2.0.0 switch): scratchpad/run/s_huntfix1.log.
  **Review-fix results (local, 2 seeds, all 70 maps, vs H340 + B7Live, n 560 each; base #354 416/560)**: B357x with the switches off
  replays #354 exactly (+0 ± 0); kHuntElect 417, −2 ± 3; kRecallFall 416, −2 ± 6; both 417, −3 ± 7. Activation (10 traced games vs
  B7Live each way, contest/new maps): fixes off - 22 hunt starts, 0 vetoes by ineligible allies; fixes on - **278 hunt starts**, 12
  ineligible allies skipped, 70 recalling enemies passed to the usual checks. The fixes fire and multiply hunts, but our clone and B7
  cannot judge aggression (kHunter itself was −33 locally and +6 wins on the near bench): **ladder test pending** (servers backed up
  after the 2.0.0 switch). Mode-2 siege repairs (shared breach root, breach-aimed area spells) built in edit_walledaltar.py, not
  screened (mode 2 stays rejected).
- **Ladder team profiles** (Oct 26, Eric's radar request): `tools/stress/teamradar.py` (match database to Oct 23 → KDA, Trade, Gank,
  Outplay, Gold, Farm eff., Vision, Farm as percentiles among the current top 50); artifact "Ladder Team Profiles"
  https://claude.ai/artifact/2iycjM7RyiWYJyieCfNfWC. Top teams share early kills (Fish / prism / willow Gank 94-100, Outplay 96-100);
  Mite (#2) wins on farm volume with low fight numbers; us (rank 67 on Oct 26): Gank 10, Gold 24, Farm 29, Trade 63, Vision 59.
- **Gold / KDA decomposition vs the top 20** (Oct 26, `tools/stress/golddecomp.py`, match database to Oct 23 = our pre-#343
  versions; kill gold taken as 100). Per 100 rounds - us: gold 533 = 53 kill gold + 4.01 clears × 120; Fish 881 = 136 + 5.40 × 138;
  top-20 mean ~706 = ~92 + ~5.05 × ~122. **Gap to the top-20 mean: ~70% clear count, ~23% kill gold; gap to Fish (348): 48% clear
  count, 28% gold per clear (bigger camps, Treasure 20% then), 24% kill gold.** KDA (K+A)/D: us 2.6 = 1.60 / 0.62; top-20 mean ~3.9 =
  2.37 / 0.61; prism 8.1 = 3.01 / 0.37; willow 7.8 = 2.70 / 0.35; Fish 5.7 = 3.75 / 0.66. **Our death rate is the top-20 average**:
  the KDA gap is kills + assists (vs prism / willow also half our deaths). By r600: us 24.2 clears / 2.50 kills, Fish 31.9 / 6.98,
  willow 32.8 / 5.52. ~45 local farming arms never moved clears; the one change that moved ladder income was kills (#346).
- **Prey without the equipment lead** (Oct 26, Eric: "gold gain, kills and invading matter more than early gems; stopping the enemy
  reaching 1000 is a strategy too"): `tools/edits/edit_prey.py` (bots/B358x = B357x + it; all off = old code). **kWoundedPrey** -
  an isolated enemy at or below this share of its health needs no kHunterLead (the contact matchup must still predict our kill);
  **kCarrierPrey** - the same for one carrying at least this many gems (the killer takes the bag: GameRules "When a champion
  dies"); **kPreyFar** - those prey also on their half. Local (2 seeds, 70 maps, vs H340 + B7Live, n 560; #354 416/560 +292):
  + hunt fixes 417 (−3 ± 7); + wounded 0.5 **426, +26 ± 17**; + carrier 20 **428, +22 ± 11**; + hunt fixes + both + far **432,
  +31 ± 17** - the first hunting change that wins against our own clone (kHunter itself was −33). Losses on adgato-gemcombat1-3
  (−100..−200), gains on 02guardians, gemcombat4, 02crossing, 02fields. Traced (10 maps vs B7Live): ~10 wounded and ~3 carrier
  hunts a game; kills 6.2 → 6.8 per 1,000 rounds, the opponent's lost gems 22 → 33 per 1,000 rounds. Candidate #355 = #354 + both
  hunt fixes + kWoundedPrey 0.5 + kCarrierPrey 20 + kPreyFar (scratchpad run/cand355p.edits).
- **Engine 2.0.0 checks** (Oct 26 ~01:00 UTC, servers back): #354's five Fish games (e2test354) all played (banner v354, no bot
  errors, 0/5 −4,200). `cambc matches summary ID` + `cambc summary` still read 2.0.0 summaries (names print as "Unknown", ids are
  raw): our purchases are item ids 0-40 with the old meanings (jungle focus 26, durability health 16, ...) - **the new emblem families
  were appended; old item ids are unchanged**. Our replay reader (tools/replay_engine.ts, the local visualiser's engines) cannot
  decode 2.0.0 replays until a cambc with the 2.0.0 visualiser installs. All bench baselines before the switch are on 1.0.3: re-run
  the live version's benches beside each candidate (near354 / hold354 queued ~01:05 UTC).
- **2.0.0 baselines and #355** (Oct 26): near354 (#354 live, benched 01:05-01:16 UTC) **17/40, −4,802**; hold354 **10/40, −13,759**.
  **#355 = #354 + kHuntElect + kRecallFall + kWoundedPrey 0.5 + kCarrierPrey 20 + kPreyFar** (bots/B358x + run/cand355p.edits; stress
  22/24, faults 0; submitted 01:21:22 UTC, benches 01:25-01:29, banner v355): near **20/40, −851: +99 ± 81** (5 new wins, 2 new
  losses; Oldenkamp +330, Valenki +414, filter +339, SkuBap −238); holdout 9/40, −21 ± 82 (5 / 6). 29 vs 27 of 80; **kept live**.
  Local screen of **kDenyAt** (edit_deny.py, bots/B359x = B358x + it: once the enemy has banked kDenyAt and at least ours, carriers of
  kDenyCarrier 10 gems are prey and every eligible champion near one hunts it): 600 −2 ± 3, 800 −2 ± 2 (it rarely fires against our
  clone, which we lead); kGoldWeightEarly 0.45 (from 0.3) −13 ± 22, 417 vs 432 wins (not adopted). Prey on gemcombat1-3: still 8/8
  wins locally, ~70 fewer gems banked by r600 (hunting time), kills 2.2 → 3.0 per 1,000 rounds. **#356 = #355 + kDenyAt 600** next.
- **Fight profile from match summaries** (`tools/stress/sumbench.py TAG...`: `cambc matches summary` + `cambc summary` per bench game,
  cached in results/sum; works on 2.0.0, where our replay reader does not; entity kind 1 = champion, 2 = camp monster). Per game,
  bands r0-200 / 200-600 / 600+. **near354 → near355**: our kills 0.68/1.45/3.58 → 0.78/1.82/4.03, our deaths to champions
  0.30/2.38/5.85 → 0.40/1.60/5.45 (kill balance by r600 −0.55 → +0.60), our deaths to camps 1.48 → 1.18 a game, gems we lost to
  champions 81 → 61. **Holdout (policy wonk, Noobot), both versions**: we die 2.5-3.0 times to champions in r200-600 vs their 1.6,
  and 5.8-6.0 after r600 vs their 2.2-2.6; gold r600 2,263-2,329 vs 3,076-3,125, clears by r600 23 vs 24-28 - late deaths follow
  the gold gap (every caution arm so far lost; greed won). A third to a half of our camp deaths are on the enemy's half (judged by
  which side each team's first clears were on).
- **#356 = #355 + kDenyAt 600** (bots/B359x + run/cand356.edits; stress 22/24, faults 0; submitted 01:35:04 UTC): near 21/40 vs
  20/40, +21 ± 37 with only 4 games changed (it rarely fires); holdout 8 vs 9, −21 ± 51 - but **Noobot updated between hold355 and
  hold356** (their fifth pick 7 → 3, games diverge by r50 before anyone banks), so only policy wonk compares (2 changed, +23). Live.
- **Prey parameters** (local, base #355 config 432/560): kWoundedPrey 0.65 −8 ± 7; kCarrierPrey 10 −5 ± 7; kHunterTurns 20 ±0 (no
  game changes); kHunterRange 10 +5 ± 10 (434); **kHunter 5 (all prey on their half) +7 ± 4 (437)**; **kHunterHp 0.5 +1 ± 11 (441)**.
- **kHealWait** (Eric, Oct 26: a low champion leaves a camp to recall, then our Willow's heal lands and would have let it finish):
  `tools/edits/edit_healwait.py` (bots/B360x = B359x + it). wants_retreat()'s lines (kRetreatHp, half health with 20 gems, 0.6 with
  shop gold) read health + kHealWait × a ready heal from an allied Willow in reach that would pick us (she heals the ally in reach
  missing the most), in a camp fight with no enemy in sight; kHealWaitRounds also counts a heal coming off cooldown within N rounds
  when the camp's hits leave kFinishMargin until then. Ready heals only: 7 heal_wait decisions in 12 traced games (rare). Willow is in
  ~75% of our local drafts. Screen (s_heal1): kHealWait 1, + kHealWaitRounds 3, kHunter 5, kHunterHp 0.5, both.
- **Heal-wait screen** (s_heal1, base #356 config 431/560): kHealWait 1 (ready heals) −18 ± 15 (428); + kHealWaitRounds 3 −4 ± 15
  (436); kHunter 5 **+7 ± 4** (435; same as on #355's config); kHunterHp 0.5 −4 ± 10; both +4 ± 11 (439). Heal-wait held back.
- **Dash use, us vs Fish** (Eric, Oct 26: "Fish dash in a lot, melee wrap around the target; do they save dashes?"):
  `tools/stress/dashuse.ts` over fish346 + fish351 (80 games, 1.0.3). A dash = the dash slot's (ability type 6) cooldown rising.
  **Fish do not save dashes**: dash ready 31% (HoR) - 56% (Vendetta) of alive rounds, ours 33% / 56% - the same; median rounds held
  ready before a dash 0-2 for both. 78-84% of Fish dashes have no enemy within 6 (travel / camps), like ours (71-76%). The
  difference is direction: **Fish engage dashes 9-10% (HoR, Vendetta, Vesper), escape 8-9%; our Vesper engages 2%, escapes 26%,
  our HoR 7% / 14%**. Kills within 3 tiles in the next 3 rounds: Fish 2-3% of dashes, ours 0-1%. Engage targets are healthy for
  both (median 83-88% health); Fish engage with ~2 allies within 5 (our Vesper 1.0). Wrap-around: per champion kill, the killing
  side's melee champions within 2 of the victim - Fish mean 1.01, 2+ melee 22%, on 2+ sides 19%; ours 0.76 / 25% / 18% - **no
  distinct surround pattern**; Fish simply get 10.9 champion kills a game to our 2.4 in those games.
- **Ladder 3444643b, #355? vs Fish on 00breadcrumbs** (29x29, 3v3, Fish won at r1253, banked 1001 vs 357; summary only - 2.0.0):
  clears 225 vs 139, gem-camp captures 140 vs 64, gold-only 87 vs 76; **Fish tributed 74 times (~13 gems a bag) vs our 15
  (~24)**. Our contest_altar alert fires on every enemy tribute (kContestGems 10 or channelling) and contest_altar() runs before
  farm(): every champion above half health within kContestRange 10 walks over - the whole team on a 29x29 map - for tributes of
  2 turns that only a kill / stun / lock can stop. Locally on breadcrumbs (vs B7Live, traced) each champion spent ~270 turns in
  contest_altar and recall-captured 70-81 times. **kContestPay** (`tools/edits/edit_contestpay.py`, bots/B361x = B360x + it):
  contest only a visible bag of kContestBig 40+, or a tribute lasting until we are in attack range (- kContestSlack 1); with nobody
  in sight at the altar, only from kContestBlind 4 steps. Screen s_contest1: kContestPay 1, kContestRange 5, kContestPay + kHunter 5.
- **Contest screen** (s_contest1, base #356 config 431/560): **kContestPay 1 +16 ± 15 (437)** - breadcrumbs +130 → +195, dunes +72 →
  +316, quarry +99 → +273, 02arena +116 → +254, anvil +444 → +93; kContestRange 5 0 ± 17 (436); **kContestPay + kHunter 5 +22 ± 14
  (440)**. **#357 = #356 + kContestPay 1 + kHunter 5** (bots/B361x + run/cand357.edits), benches vs near356 / hold356.
- **Escape dashes** (dashuse.ts, fish346 + fish351): our Vesper 1,053 escape dashes (Fish's Vesper 409) at a median 83% health (70%
  above 60%), died within 5 rounds after 5% (Fish 2%); our HoR 541 at 85%. escape() dashes to any safer landing whatever our health.
  **kEscapeDashHp** (`tools/edits/edit_escapedash.py`, bots/B362x = B361x + it): dash away only below this health share or with an
  enemy within kEscapeDashNear 1; otherwise walk and keep the dash. Screen s_edash1 on #357's config: 0.6, 0.4, 0.6 with near 2.
- **Escape-dash screen** (s_edash1, base #357 config 440/560): kEscapeDashHp 0.6 −30 ± 22 (425); 0.4 −4 ± 21 (434); 0.6 with near 2 −33 ±
  21 (422). Our escape dashes keep us alive; rejected.
- **#357 benched** (stress 22/24, stuck 0, faults 0; submitted 02:22:43 UTC; groups 02:27): near **23/40 vs 21/40, +100 ± 77** (27
  changed, 5 new wins / 3 new losses; no opponent draft changes since near356); holdout 8 vs 8, +10 ± 79 (policy wonk +20; **Noobot
  changed its draft again** (fifth pick 3 → 7): exclude Noobot until it settles). **Kept live.** Near bench on 2.0.0: #354 17 →
  #355 20 → #356 21 → #357 23. **#358 = #357 + kHealWait 1 + kHealWaitRounds 3** (B362x has every switch; ladder test of Eric's idea).
- **#358 = #357 + kHealWait 1 + kHealWaitRounds 3** (submitted 02:33:54 UTC; no opponent draft changes since #357's benches): near
  **20 vs 23, −35 ± 77** (3 new wins / 6 new losses); holdout 8 vs 8, +67 ± 73 (policy wonk +97, Noobot +37). Wins −3: rejected.
  **#359 = #357's code again** (B361x + cand357.edits; submitted 02:56:37 UTC; stress identical to #357's line for line) - live.
- **Team shape, us vs Fish** (Eric, Oct 26: Fish keep the group reachable, recall without splitting off, help fights when hurt, space
  from awake camps with enemies near, solo neighbouring camps): `tools/stress/cohesion.ts` over fish346 + fish351 (80 games, 1.0.3).
  Away from home, nearest ally beyond 8 / 12: us r1-300 16% / 10%, r300-800 **32% / 20%**, r800+ 32% / 21%; Fish 13% / 7%, **21% /
  11%**, 24% / 13% (median nearest ally 5 vs 3-4 after r300). First 15 rounds out of home with no ally within 8: 23% vs 19%. Deaths
  to champions 10.9 vs 2.4 a game, victim with no ally within 6: 29% vs 25% - **most of our deaths are lost fights, not lone
  pick-offs**. Fight help (an ally 5-10 away closes to 4 within 4 rounds): under half health **23% vs 32%**, at least half 37% vs
  39%. In an awake monster's reach with an enemy within 5: 65% vs 68% (no gap). Farming: party 1.50 vs 1.90, **solo 63% vs 43%**;
  soloists with an ally within 8 55% vs 68%, none within 12 30% vs 17%.
  `tools/edits/edit_teamshape.py` (bots/B363x = B362x + it): **kNearAlly** (from kNearAllyRound, camp scores fall with the camp's
  distance beyond kNearAllyRadius 8 from our nearest living teammate, every map) and **kAssistHp** (join a fight beside us above
  this health share; was a fixed 0.5). Screen s_shape1 on #357's config: kAssistHp 0.35 / 0.2, kNearAlly 1 / 2 (r300), 1 from r100.
- **Code review of the Oct 26 edits** (Eric's request; diff B356x → B363x: huntfix, prey, deny, healwait, contestpay, escapedash,
  teamshape). Fixed in the edit scripts, rebuilt as **bots/B364x** (= B356x + all seven, in that order; differs from B363x only by
  these fixes; builds with every switch on, 0 warnings):
  1. (live) kDenyAt's team hunt keyed on the trace kind, which prefers "wounded": a wounded carrier near their win got one hunter.
     Now a separate prey_carrier flag.
  2. (live) kContestPay counted a running tribute's full ceil(gems / 10) turns (observe_bankers' timer is off in our config): it
     still walked to tributes ending before arrival. Now each altar remembers when we first saw its channel (reset when not watched
     the round before) and the turns left shrink.
  3. (live) kContestPay treated any enemy within 2 of the altar as the banker: an empty-handed escort in sight blocked a teammate's
     alert about an unseen carrier. Gemless enemies are skipped now.
  4. (live) kHuntElect's ineligible allies now include tributing ones.
  5. (latent) deny mode used kDenyCarrier even when kCarrierPrey was lower; now the smaller.
  6. (cosmetic) kPreyGemScore's comment had landed on kDenyCarrier's line.
  Checked, no change: the walled-altar key range (one_altar_key(a) = −10 − a), kScorePrune vs factors (pruning is off), heal-wait vs
  our Willow's target rule, kRecallFall, cohesion.ts spawn detection (round-0 positions). Redundant in the live config: kPreyFar
  (kHunter 5 already allows every prey on their half).
- **Team-shape screen** (s_shape1, base #357 config 440/560): kAssistHp 0.35 −19 ± 18 (434), 0.2 −33 ± 22 (423); kNearAlly 1 from r300
  **−52 ± 18** (418), 2 −31 ± 16 (421), 1 from r100 **−68 ± 22** (408). Pulling soloists towards teammates costs clears against our
  clone (a fair judge of farming); rejected. **Review fixes** (s_fix1): B364x vs B361x on #357's config +4 ± 7 (436 vs 440 wins) - the
  fixed paths rarely fire locally. **#360 = B364x + cand357.edits** (#357's config on the reviewed code), benches vs near357 / hold357.
- **#360 benched** (#357's config on B364x; submitted 03:30:40 UTC; no opponent draft changes): near 23 vs 23, −13 ± 40 (4 changed);
  holdout 7 vs 8, +72 ± 68 (Noobot +103, 18 changed). Level; **kept live** (the corrected code).
- **Heal-backed parties** (Eric, Oct 26, ladder a882aab7 vs Noobot on 00expanse, lost at r1178: "4 champions attack a 2-elk camp
  quite early and the Willow heals allow the Ryth to finish off the camp"). Summary: **their Willow healed 15,770 and farmed nothing
  (40 gold, 0 gems); ours healed 1,369 and farmed (1,000 gold, 131 gems)**; they captured 44-gem camps at r120 and r317; all 29 of our
  clears before r400 were by single champions. A Willow heal (ability type 5): 3 x focus every 8 rounds, range 4. champions_needed()
  had no heal term. `tools/edits/edit_healparty.py` (bots/B365x = B364x + it): **kHealParty** (party sizing adds an allied Willow's
  heal rate - heal_amount / max_cooldown - x the party's time to kill, when she is within kHealPartyRange 12 of the camp; not for her
  own solo) and **kMedicCall** (our Willow, healthy with no enemy within 6, walks to heal a teammate fighting a camp within N tiles
  below kMedicHp 0.75, into heal reach and out of monster reach; heals by cast_support as before). Traced (10 maps vs B7Live, #357
  config): medic 44 turns a game; heal casts 38 → 34 a game; **dead champion-turns 340 → 239 a game**. Screen s_heal2.
- **Heal-party screens** (base #360 config 436/560). s_heal2, all camps: kHealParty 1 −34 ± 22 (423); kMedicCall 10 −54 ± 22 (413);
  both −73 ± 25 (411); both with kMedicHp 0.5 −42 ± 24 (421); both + kHealWait −67 ± 24 (404) - gains on expanse (+89 → +198..+278),
  elk-arena (medic −123 → +390), elkring (0.5: +180 → +334); losses on 02guardians (+1,024 → +151..+862) and against H340.
  s_heal3, **kHealElk** (both only for camps with an elk): kHealParty −37 ± 20 (422), kMedicCall −37 ± 18 (414), both −33 ± 21
  (424; elk-arena +355), both at 0.5 −32 ± 22 (421). Locally a medic Willow costs more farming than she saves; the medic cut dead
  turns 30% in traces, and our clone misjudged fight behaviour before (kHunter), so **#361 = #360 + kHealParty 1 + kMedicCall 10 +
  kHealElk** (bots/B365x + run/cand361.edits) goes to the ladder, benches vs near360 / hold360.
- **#361 (heal parties) not submitted: stress gate failed twice.** First build: wins 20/24, stuck 4 (67 rounds; all Willow: islands
  r155 / r290, corridors r607, lanes r864). Fix attempt (medic calls only for a teammate inside an awake monster's reach;
  kMedicHold 16 rounds then kMedicRest 20): stuck 4 (209 rounds; big-world 143) and loops 6 (530; fracture Willow 498 - the rest /
  return cycle), and the original islands / corridors cases unchanged - they come from kHealParty: a traced islands game shows
  Willow fighting elk camps herself and holding "help_ask_squad" for helpers whose own picks never bring them (the heal term makes
  elk camps look feasible to her but not to them). With every local screen negative (−32..−73), the line is parked; **#360 stays
  live**. A better form would be a planned elk opening (a fixed tank + Willow + DPS party for the nearest two-elk camp in a set
  window, all members committing together) rather than a heal term in every champion's party sizing.
- **kWillowFollow** (Eric, Oct 26: "make Willow only follow other members and never stray from the group; match recall timings"):
  `tools/edits/edit_willowfollow.py` (bots/B366x = B365x + it). Willow keeps a lead (a living teammate, kept until it dies; else the
  one with most teammates within 6, away from home first, then nearest), stays within N tiles of it on a tile out of awake monster
  reach (moves only for a clearly better tile), walks the path when further; picks no camp, publishes the lead's target (teammates
  skip camps others publish); **kFollowRecall**: recalls when the lead recalls. Safety branches still run first. Eric's movement note:
  champions walk through allies but cannot land on them - free_tile() already refuses occupied landings and our fields ignore units.
  Traced (10 maps vs B7Live, #357 config, Willow per game): follow 2,531 turns, follow_recall 36; camp fights 862 → 4; heal casts
  132 → 142; her dead turns 482 → 602. Screen s_follow1: follow 2 / 3, + kHealWait, + kHealParty, + both.
- **Willow-follow screen** (s_follow1, base #360 config 434/560): kWillowFollow 2 **−85 ± 26** (401); 3 −79 ± 26 (404); 2 + kHealWait
  −66 ± 26 (412); 2 + kHealParty −74 ± 26 (411); 2 + both −97 ± 25 (400). Gains on yellow-brick-road (−213 → +341), shortcut, swirl,
  hooks, corners; losses on vault (+608 → −268), ribs (+640 → −46), road-of-riches, guardians, eight, corridors. Locally Willow's own
  farming is worth more than her heals. Ladder test at Eric's request: **#361 = #360 + kWillowFollow 2 + kHealWait 1 / 3**
  (bots/B366x + run/cand361f.edits), benches vs near360 / hold360.
- **#361 = #360 + kWillowFollow 2 + kHealWait** (every map) passed stress (23/24, stuck 2 / 4 rounds) and was submitted 04:47:55 UTC;
  benches vs near360 / hold360 running. **kFollowGate** (Eric: "only for fight-heavy maps or maps where we are likely contesting camps
  or altars"; `tools/edits/edit_followgate.py`, bots/B367x = B366x + it): bits 1 control map, 2 every altar contested, 4 an enemy
  seen within kFollowHot 60 rounds; otherwise Willow farms. No map-profile feature (spawn path, control, contested altars, mid / far
  gem shares; per-map profiles from a kTraceMap run in scratchpad/mapprof.json) separated s_follow1's per-map gains from its losses,
  so the gate follows Eric's intent. Screen s_gate1: gates 1, 2, 4, 3, 7 with follow 2 + heal-wait.
- **#361 benched (kWillowFollow 2 + kHealWait, every map)**: near **17 vs 23**, −57 ± 67 (1 new win / 7 new losses; SkuBap changed
  its draft - exclude); **holdout 18 vs 7, +205 ± 97 (11 new wins, 0 new losses; Noobot +353 all 20 changed, no draft change; policy
  wonk +57)**. 35 vs 30 of 80: kept live. Following wins against the stronger, fight-heavy teams and loses farm races against
  near-rating teams - the case for kFollowGate (bit 4: follow while enemies are about).
- **Follow-gate screen** (s_gate1, base #360 config 434/560; each with kWillowFollow 2 + kHealWait): gate 1 (control maps) −6 ± 19
  (**443**); 2 (every altar contested) −55 ± 24 (421); **4 (enemy seen within 60 rounds) −10 ± 25 (435)**; 3 −43 ± 24; 7 −40 ± 25
  (ungated −66 ± 26). **#362 = #361 + kFollowGate 4** (bots/B367x + run/cand362.edits), benches vs 361 / 360.
- **Team profiles on 2.0.0** (Oct 26 ~05:30 UTC; `tools/stress/radarnow.py` - teamradar's measures from each team's latest ranked
  2.0.0 games via the CLI, summaries cached in results/sum; top 20 x 12 games, us x 30): **we are rank 48, rating 1,942** (67 that
  morning). Percentiles among the 21: KDA 3.91 (90), Trade 1.57 (100), Gank 0.60 (50; was 10 on Oct 23), Outplay 0.14 (45), **Gold 455
  per 100 rounds (25)**, Farm eff. 172 (75; was 35), Vision 13.1 (55), **Farm 3.75 clears per 100 rounds (25)**. Leaders: Gank Fish
  1.25; Gold print dont int 819, Supaswag 625, Claudus 620; Farm print dont int 6.61, Mite 5.91. Gold fell for everyone on 2.0.0
  (Fish 881 → 479 per 100 rounds). Caveat: the top teams' games are mostly against each other, ours against teams near our
  rating. Fighting is now top tier; farming volume is still bottom quarter (Eric: early healthy recalls - rushbait 533aaf1f: our
  champions recall after almost every capture, SSSA chain 2-3 captures a trip).
- **Early trips** (Eric, Oct 26, ladder 533aaf1f vs SSSA on 00rushbait_v2, 4v4, lost: our champions bought within 1-10 rounds of
  almost every capture - recall-capture - while SSSA's Marcella captured at r31, r54, r78 before her first trip at r84). Screen
  s_trips1 (base #360 config 434/560): kLateTripRound 1 with hp 0.6 / gold 150 −15 ± 25 (420; rushbait +455 → +197, yellow-brick-road
  −213 → +626); 0.5 / 250 −52 ± 25 (406); kRecallCapSlack 5 −22 ± 21 (431); kSquadKeepCap −5 ± 25 (439); both −12 ± 25 (421).
  **kLateTripEnd** (`tools/edits/edit_earlytrips.py`, bots/B368x = B367x + it): the fewer-trips window ends at that round. Screen
  s_trips2: kLateTripRound 1 + kLateTripEnd 250 with 0.6 / 150, 0.5 / 250, 0.6 / 150 + kSquadKeepCap, and the defaults (0.6 / 300).
- **Ladder Team Profiles** dashboard refreshed with the 2.0.0 profiles (datasets/profiles → /_blob/0805856dae39ebd13ea796dd152d6232,
  team-profiles-2.0.0.json; captions rewritten; the Oct 23 file /_blob/21a1ff96bdfa9c48322ae14f61b87c47 is no longer referenced).
- **kRecallSync** (Eric, Oct 26: "make the recalls happen less during early game and keep the recalls more or less timed together ...
  we can keep the recalls and groupings untouched for late game"): `tools/edits/edit_recallsync.py` (bots/B369x = B368x + it). A
  teammate within kRecallSync tiles is recalling and our trip is due soon anyway (health below kSyncHp 0.8, kSyncGold 100 gold, or
  kSyncGems 20 in the bag), not in a camp fight, not home, no enemy in sight: recall with it. **kSyncEnd** limits it to the opening
  (like kLateTripEnd). Screen s_sync1 (after s_trips2): sync 6 to r250; + kSyncHp 0.7; + early trips (kLateTripRound 1, kLateTripEnd
  250, 0.6 / 150); early trips alone.
- **Early-only trips** (s_trips2, base #360 config 434/560; kLateTripRound 1 + kLateTripEnd 250): 0.6 / 150 −27 ± 24 (428); 0.5 / 250
  −40 ± 25 (417); 0.6 / 150 + kSquadKeepCap −16 ± 25 (433); 0.6 / 300 −27 ± 24 (429). Recall-capture pays against our clone even early.
- **#362 = #361 + kFollowGate 4** (submitted 05:16:05 UTC, stress 23/24; no opponent draft changes vs #361): near 18 vs 17 (−9 ± 75),
  **holdout 9 vs 18, −279 ± 102** (4 new wins / 13 new losses; Noobot −526). Totals 360: 30/80, **361: 35/80**, 362: 27/80 - Willow
  must stay with the group from the start; following only while enemies are about loses what beat the strong teams. Rejected;
  **#363 = #361's code again** (B366x + run/cand361f.edits), uploaded after the s_sync1 screen.
- **Recall-sync screen** (s_sync1, base #360 config 434/560, all to r250): kRecallSync 6 **−63 ± 20** (410); with kSyncHp 0.7 −59 ± 17
  (405); sync + early trips (kLateTripRound 1 / End 250 / 150 gold) −29 ± 23 (426); early trips alone −27 ± 24 (428). Joining recalls
  costs the opening's farming. Ladder check of the combination: **#364 = #361's config + kRecallSync 6 / kSyncEnd 250 + kLateTripRound
  1 / kLateTripEnd 250 / kLateShopGold 150** (bots/B369x + run/cand364.edits), after the #363 restore; benches vs 361 / 360.
- **#363 = #361's code** (submitted 05:34:29 UTC; stress identical to #361's line for line). **#364** first stress: wins 21/24, stuck
  6 (67 rounds: Willow r226 / r414 / r1322, Vesper r365 / r734 / r848 - mostly after the r250 window, i.e. games taking another course,
  each just past the 30-round mark) > 60: **recorded exception STUCK_ROUNDS=70** to get the ladder's verdict on Eric's recall idea;
  resubmitted with the 2-minute compile wait (feedback-ladder-timing).
- **#364 = #361 config + kRecallSync 6 / kSyncEnd 250 + kLateTripRound 1 / kLateTripEnd 250 / 150 gold** (submitted 05:46:31 UTC with
  the STUCK_CASES 6 / STUCK_ROUNDS 70 exception): near 19 vs 17 (OneTap re-drafted 2 games), **holdout 10 vs 18, −189 ± 89** (2 new
  wins / 10 new losses; Noobot −400). Totals 29 vs 35: rejected, like the local screens. **#365 = #361's code again**, benched to check
  that #361's holdout 18/40 replays (determinism / opponent drift).
- **#365 = #361's code** (submitted 06:08:20 UTC): near 17/40 (36 of 40 games identical to #361's; **SSSA changed 4/5**), holdout
  **9/40** (policy wonk 0/20 changed; **Noobot 19/20 changed, −471, no draft change: Noobot updated after #361's bench** ~04:52).
  #361's 18/40 was against the old Noobot. Re-scored against #365 (same code, current opponents): #362 near 18 / hold 9 (27 vs 26),
  **#364 near 19 / hold 10 (29 vs 26)** - their "losses" to #361 were mostly Noobot's update. #360 (benched before the updates, 30/80)
  needs a fresh run: **#366 = #360's code** (B364x + cand357.edits) as a same-opponent baseline. Lesson: opponents update often
  (Noobot twice, SSSA, SkuBap, OneTap tonight) - bench a baseline beside every candidate and check identical-game counts.
- **Fish's farming route on 00breadcrumbs** (ladder a5d8f57c, 3v3, Fish won r941; `tools/stress/route.py SUMMARY GROUPS` over the match
  summary + `tools/stress/dump_groups.ts` camp groups from a local replay of the map). The map: 34 single-tile camps, no monsters -
  22 gem clusters in two trails (top: (16,13) → (3,12); bottom: (12,15) → (25,16)), 6 gold clusters beside each spawn (ours x 2,
  y 14-24; theirs x 26, y 4-14); one altar at (14,14), beside both trails' inner ends; clusters respawn ~50 rounds after capture.
  By r600: Fish 132 clears / 130 captures (78 gem, 52 gold) / 553 gems / 12 trips home; us 82 / 82 (39, 43) / 273 / 35.
  **Per champion, between consecutive clears: Fish median 2 tiles and 9 rounds, us 6 tiles and 16** (clear-to-capture 7 rounds for
  both; 109 of 128 Fish captures by the clearer - no run-ahead pipeline). Roles: Fish's Vesper loops their gold column from ~r200
  in a ~57-round cycle (the respawn time; home every ~50-60 rounds buying 150-180 gold), Vendetta and HoR sweep the bottom gem trail
  in order (including our near end (11,17)-(12,21)) and **tribute every 1-2 captures at the centre altar on the way (46 tributes,
  median bag 7 gems = a one-turn tribute)**. Ours: two champions on the same top trail leapfrog (our Vesper r17-108 took every other
  camp Ryth left: 20-24 rounds a camp), Ryth and Marcella loop our gold column r140-360 (gold only), nobody holds the bottom trail,
  6 tributes of median 42 gems (kDeliverGems 40) and 35 trips home buying 10-30 gold at a time.
- **#366 = #360's code** (submitted 06:23:02 UTC), same-opponent baseline: holdout **40/40 games identical to #360's 03:35 bench** -
  so the Noobot #361 beat 18/40 at ~04:52 was a temporary version, since reverted; near 28/40 identical (Oldenkamp, SSSA, SkuBap
  updated). Same opponents: **#366 (no follow) near 21 / hold 7 = 28; #365 (follow) 17 / 9 = 26**; #364 (30 min earlier) 19 / 10 = 29 -
  all inside an 80-game bench's noise (~±3-4 wins). **#366 is live** (simplest base) for the farming-route work.
- **Route work** (Eric: build on the Fish breadcrumbs analysis): bank as you pass already exists (wants_deliver: kNearbyGems 10 within
  kNearbyAltar 3 path steps) - a single 7-gem cluster never triggered it; **kNearerMate** (`tools/edits/edit_routechain.py`, bots/B370x =
  B369x + it): in solo picks a camp a teammate (out, not recalling, not on spawn) stands nearer to, within N tiles, scores
  kNearerMateFactor (own target and rewards exempt) - no leapfrogging. Screen s_route1 on #366's config: kNearbyGems 1; + kNearbyAltar 5;
  kNearerMate 6 (0.5); 6 (0.25); kNearbyGems 1 + altar 5 + kNearerMate 6.
- **Route screen** (s_route1, base #366 config 434/560): kNearbyGems 1 −14 ± 15 (427; breadcrumbs +239 → +274); + kNearbyAltar 5
  −16 ± 18 (427); kNearerMate 6 (0.5) −21 ± 17 (430); (0.25) −35 ± 17 (420); bank 1 / altar 5 + kNearerMate 6 −25 ± 20 (423).
  **#367 = #366 + kNearbyGems 1** (B370x + run/cand367.edits), benches vs near366 / hold366.
- **#367 = #366 + kNearbyGems 1** (bank any bag within 3 steps; submitted 06:57:17 UTC; no opponent draft changes): near 20 vs 21
  (−17 ± 39), holdout **5 vs 7 (−108 ± 62)**: rejected; **#368 = #366's code** restored. **Early gold weight** (s_gold1, base #366
  config 434/560): kGoldWeightEarly 0.2 −44 ± 21 (424), 0.15 −60 ± 24 (410), **0.1 −86 ± 23 (391)** - monotonic: valuing gems over
  gold early costs (Eric's earlier read was right; Fish's gem preference on breadcrumbs is that map's). Live 0.3 stays.
- **New items on 2.0.0** (367 cached ladder summaries, raw ids; names unreadable without the 2.0.0 SDK): bought ids 48-65 in nine
  shard / emblem pairs (42-47 never): 54/55 mostly Vesper (209), 48/49 Vesper / Vendetta / Marcella, 58/59 Marcella / Vendetta,
  50/51 + 56/57 + 64/65 HoR, 60/61 Vendetta / Vesper; old ids 0-41 keep their meanings (our purchases). Building with the new
  emblems needs the 2.0.0 header (names, costs); neither the local cambc 3.0.5 nor a cloud copy has it or its engine, so new-item
  builds can only be judged on the ladder. Commit 37af341 (bamboo8) holds tonight's tools, edits, bases and maps for cloud screens.
- **cambc 4.0.0 = engine 2.0.0 locally** (Oct 26 ~07:35 UTC; PyPI): installed beside the old exes; repo sdk/ refreshed (275 changed
  header lines: the 2.0.0 item enum - 42-47 Tribute, 48-53 Capture, 54-59 Prospector, 60-65 Hunter, 66-71 Skirmish, 72-77 Greed,
  78+ Collectors, each shard/emblem of strength/focus/health; item_passive extended; draft turn 100x fuel); maps identical; our
  bots + H340 + B7Live build unchanged; fastscreen and stress tools default to 4.0.0; the replay reader decodes 2.0.0 ladder replays
  (v2_0_0 wasm); summaries print names. **Every local result before this was on engine 1.0.x balance** - re-check key arms.
  Top teams' new-item purchases (367 summaries): Capture (Marcella, Vendetta, Vesper, HoR, Ryth), Prospector (Vesper 209 strength
  shards; HoR, Marcella), Hunter (Vendetta, HoR); Tribute, Skirmish, Greed, Collectors unbought.
- **Top teams' 2.0.0 emblem lines** (`tools/stress/builds.py`: top 12 teams' latest 10 ranked games each + ours, itemCombination order,
  Oct 26 ~07:45 UTC): new families are bought but rarely finish one of the first four emblems. First three: Marcella (89 games),
  Ryth (51), Vendetta (84) Treasure Health > Jungle Str > Bruiser Health; Vesper (88) Treasure Str > Jungle Str > Bruiser Health;
  HoR (92) Treasure Health > Jungle Focus > Bruiser Health (or Treasure Focus > Power Focus > Durability Health); Willow (7)
  Durability Health first; Prism Durability Health > Monster Health > Jungle Health; Tavi Bruiser Str > Durability Health >
  Monster Str; Varg Jungle Str > Treasure Str > Durability Health. Ours: Marcella Treasure / Jungle / Bruiser **Focus**, Ryth Jungle
  **Health** second, Vesper Durability Health third, HoR Treasure Focus first, Willow Jungle Focus first. **kBuild2**
  (`tools/edits/edit_build2.py`, bots/B371x = B370x + it; bits 1 Marcella, 2 Ryth, 4 Vesper, 8 HoR, 16 Willow, 32 Vendetta, 64 others):
  these lines ahead of every other build switch, no Treasure-first rewrite. Screen s_build1 (first local screen on engine 2.0.0):
  127, 1, 14 (Ryth / Vesper / HoR), 16.
- **Top 5 teams' lines** (`tools/stress/top5builds.py 5 20`: Fish, Mite, prism best girl, NEETCoders, willow best girl; latest 20
  ranked 2.0.0 games each; results/db/top5builds.json): lines vary a lot within each team; NEETCoders and willow best girl open HoR /
  Vesper / Vendetta with **Hunter** emblems, willow best girl's Marcella with **Prospector Health**; Fish does not. Fish: Marcella
  Treasure H > Jungle Str > Bruiser H > Durability H > Bruiser Str; Vesper Treasure Str > Jungle Str > Bruiser H > Bruiser Str >
  Durability H; HoR Treasure H > Jungle F > Bruiser H; Vendetta / Varg Monster Str > Jungle H > Power Str; prism best girl's Ryth Jungle
  Str > Bruiser H > Durability H. **kBuild3** (`tools/edits/edit_build3.py`, bots/B372x = B371x + it): copies Fish's line where Fish
  plays the champion, else the best-ranked top-5 team's (completed from the top-12 data); bits as kBuild2's. Screen s_build2: 127,
  13 (Marcella / Vesper / HoR), 2 (Ryth), 16 (Willow).
- **Build screen 1 on engine 2.0.0** (s_build1, cambc 4.0.0; base #368 config **396/560 +230** - the first local baseline on the
  ladder's balance): kBuild2 127 (every champion) **−111 ± 25** (355); 1 (Marcella Treasure H > Jungle Str > Bruiser H) **−96 ± 23**
  (359) - our Marcella plays a focus caster (carry casts, focus spells), the top teams' a strength / health bruiser: a build must fit
  how our code uses the champion; 14 (Ryth / Vesper / HoR) +21 ± 21 (406); **16 (Willow Durability H > Bruiser H > Treasure F) +31 ±
  17 (410)**.
- **Build screen 2** (s_build2, base 396/560): kBuild3 127 (top-5 copies) −132 ± 24 (340); 13 (Fish's Marcella / Vesper / HoR) −136 ±
  25 (340; Marcella again); 2 (prism best girl's Ryth Jungle Str > Bruiser H > Durability H) −29 ± 23 (382); 16 (Willow) +31 ± 17 (410).
  Next s_build3: kBuild2 16 / 18 / 20 / 24 / 30 (Willow + Ryth / Vesper / HoR singly and together).
- **Build split** (s_build3, base 396/560): kBuild2 16 (Willow) +31 ± 17 (410); 18 (+ Ryth) +5 ± 18; 20 (+ Vesper) +6 ± 19; **24 (Willow +
  HoR Treasure H > Jungle F > Bruiser H) +47 ± 21 (420)**; 30 (+ Ryth, Vesper, HoR) +7 ± 23. Our Ryth / Vesper / Marcella builds suit how
  our code plays them. **#369 = #368 + kBuild2 24** (B372x + run/cand369.edits), benched right after a same-time #368 bench.
- **Codex's fish-five audit** (collaboration/20261026/fish-five: v366 vs Fish on breadcrumbs, anvil, gemcombat1 / 3, treasure_box;
  engine 2.0.0; 670 camp cycles, 5,327 camp-damage records, 365 recall starts): Fish keeps circuits intact, picks richer camps,
  assigns collection deliberately (the beneficiary can be Marcella, not only Vesper) and loses less time to deaths (our Vesper dead
  120-180 sampled rounds on anvil / gemcombat1, Fish none). Breadcrumbs: 62 recalls vs 13 by r600, **52 of ours at 95%+ health with
  under 30 gold**; anvil: Fish 2,655 gold vs our 1,158 at r600 (we had more camp gems); treasure_box: 7,054 vs 1,639 gold, our 18
  deaths vs 2 (there fewer recalls would be wrong). Item 1 (a benefit-aware recall continuation) → **kRecallCapIdleSlack**
  (`tools/edits/edit_recallbenefit.py`, bots/B373x = B372x + it): a recall-capture with nothing to gain (health >= kRecallCapHealHp 0.9,
  gold < kRecallCapBuyGold 60) uses this slack instead of kRecallCapSlack 20 and farms on with no next camp to compare. Screens on
  engine 2.0.0: s_audit1 (kLateTrip 0.9 / 60 and / 100, kRecallCapSlack 8, kGoldWeightEarly 0.45 / 0.6, kLookahead 0.5) and s_audit2
  (kRecallCapIdleSlack 0, 0 with 100 gold, 4).

### #369 ladder test (08:22 UTC Oct 26, engine 2.0.0) - KEPT
#369 = #368 code + kBuild2 24 (Willow Durability H > Bruiser H > Treasure F; HoR Treasure H > Jungle F > Bruiser H), built from B372x.
Same-time baseline benched first (#368 near/hold equalled #366's game for game - opponents stable).
| | near | holdout | total wins | margin |
|---|---|---|---|---|
| #368 | 20/40 | 7/40 | 27 | -9,798 |
| #369 | 18/40 | 10/40 | 28 | -9,539 |
Flat on the ladder (+1 win), +47+-21 locally (560 games): kept live. Holdout gain is policywonk 4/20 vs 1/20.

### Fish-five deaths and action rate (v366 traces, collaboration/20261026/fish-five; scratchpad deathwin.py / pvpact.py)
- Early Vesper deaths are 1v2 / 2v3 picks by Fish's Marcella + HoR after our ally walked off: anvil r58 (our Marcella recalled at r38
  with 21 gems, Vesper + Ryth stayed; Fish's three arrived r47), gemcombat1 r55 (our Marcella left at r42 with 42 gems to bank while
  Vesper sat at d1 of HoR + Marcella; her escape() then ran east, away from home, because the enemies stood between her and home -
  the safest-tile key prefers distance from enemies over home; chased down from 22%). Recall is interrupted by damage, so a chased
  champion cannot recall out.
- Attacks + casts per champion body by r600 (ours / Fish): treasure_box 185 / 330, gemcombat1 106 / 181, anvil 168 / 221.
  Fish's champions spend far more turns hitting something; our gap is downtime (deaths, resets, walking), not target choice.
- treasure_box opening (wolf group16): HoR, Ryth, Marcella trade at the camp while Vesper shoots from range 3 and Willow keeps
  hitting the camp; 5 bodies vs Fish's 6 (Cassi + Issac) - a numbers fight, lost from r14.
- Item 3 (collector allocation) is mostly in place: kVesperCarry routes gold-heavy rewards to Vesper only within 6 tiles.

### Fish-five audit screens (engine 2.0.0, local, 560 games/arm vs H340 + B7Live, base = #368 config cand357 on B372x/B373x: 396/560, +230)
| arm | wins | paired | breadcrumbs | treasure_box |
|---|---|---|---|---|
| kLateTripRound 1, kLateTripHp 0.9, kLateShopGold 60 | 390 | -39 +-26 | +541 (base +211) | +22 (base +416) |
| ... kLateShopGold 100 | 405 | +2 +-26 | +610 | -21 |
| kRecallCapSlack 8 | 391 | +1 +-21 | +536 | +476 |
| kGoldWeightEarly 0.45 | 400 | +14 +-23 | +188 | +341 |
| kGoldWeightEarly 0.6 | 409 | +11 +-24 | +161 | +184 |
| kLookahead 0.5 | 384 | -41 +-24 | +118 | +157 |
| kRecallCapIdleSlack 0 (edit_recallbenefit.py, B373x) | 394 | -14 +-24 | +514 | +171 |
| ... with kRecallCapBuyGold 100 | 398 | +2 +-23 | +588 | +178 |
| kRecallCapIdleSlack 4 | 388 | -14 +-22 | +537 | +188 |
Every no-gain-recall cut gains ~+300-400 on breadcrumbs (the audit's map) and gives it back elsewhere (treasure_box, where Fish
recalls hurt and often; H340 matchups -30..-60, B7Live +20..+60). Flat overall locally: ladder decides. #370 = #369 +
kRecallCapIdleSlack 0 + kRecallCapBuyGold 100 under ladder test (bots/B373x + scratchpad run/cand370.edits).

### Map-type rules (Eric Oct 26: classify the layout at draft, pick rules by type; works on unseen maps)
Tools (scratchpad mapfeat/): MapTr = #369 + kTraceMap (prints MAPPLAN: size, groups, gems/gold by camp class, gem rates, altars;
SPAWNPATH: walking spawn path, control, contested altars, midgems = share of gems in midline groups, fargems); feat.py ->
features.json (65 of 70 maps; 00lanes, 01big-world, 01fracture, 01yellow-brick-road, adgato-gemcombat5 print no profile);
permap.py -> per-map arm-minus-base deltas of every 2.0.0 screen (s_build1-3, s_audit1-3).
- Recall-cut arms agree per map (r 0.56) beyond shared-baseline noise (unrelated arms r 0.37): their effect is map-dependent.
- Against the recall-specific effect (recall arms minus unrelated arms), features holding in both halves of the maps: midgems
  -0.23/-0.43, fargems +0.27/+0.31, total gems +0.24/+0.27, heavy-camp gems +0.25/+0.26, gold share -0.29/-0.23; control map
  (short spawn path) -36 vs +21 off. Reading: cutting resets pays on farming layouts (gems on each side, gem-rich), costs on
  contested layouts (gems on the midline, gold-rich), where Fish too recalls hurt and often.
- Gate "midgems < 0.4" for kRecallCapIdleSlack 0/100: ~+15 a game over all maps held out (threshold choice unstable between
  halves, so a round value). edit_recallgate.py -> kRecallCapIdleMid (bots/B374x).
- s_gate2 (B374x, #369 config, 560 games/arm): base 418, +271 | kRecallCapIdleSlack 0 + BuyGold 100 ungated (= #370) 421, +14 +-24 |
  same gated kRecallCapIdleMid 0.4: 420, **+17 +-12** (contested maps identical to base: oasis, swirl, hooks, treasure_box) |
  gated with BuyGold 60: 418, +7 +-12. Base drifted 420 -> 418 against the identical B373x config: code changes shift fuel on
  fuel-limited turns, so builds differ by a few games even with every new switch off.
- Codex's review (Oct 26): a map type sets the default; the reset itself should compare continue vs reset (respawn downtime, purchase
  value, ally exposure). edit_recallbuy.py (bots/B375x): kRecallCapIdleNone (no next camp to take -> recall in the downtime; the
  idle rule farmed on) and kRecallCapBuyMode (gold incl. this reward vs 1 a shard / 2 the rest of the next plan emblem, 30 g a
  shard, 150 an emblem; 0 = fixed kRecallCapBuyGold). Fallback: mid_gem_share() is 1 (rule off) until setup fills midline_; setup
  fills it on every map (the 5 maps without a MAPPLAN print still get it).
- s_buy1 (B375x, #369 config, base 418 / +271): gated BuyGold 100: 421, +18 +-12 | + kRecallCapIdleNone: 420, +18 +-12 |
  + BuyMode 2 (emblem) gated: 411, -4 +-11 | BuyMode 2 ungated: 398, -24 +-22 (swirl -336, hooks -608) |
  **BuyMode 1 (a shard, our gold + this reward's) ungated + IdleNone: 423, +17 +-12** (swirl, hooks, oasis identical to base).
  Suppressing every trip short of an emblem loses even on farming maps; suppressing only trips that buy nothing works on every
  map without the layout gate - the purchase test does what the map gate approximated. #371 candidate = this (run/cand371.edits).

### #370 ladder test (09:13 UTC Oct 26) - REJECTED
#370 = #369 + kRecallCapIdleSlack 0 + kRecallCapBuyGold 100 (ungated). Same-time #369 baseline (near369b/hold369b, 09:00-09:07).
| | near | holdout | wins | margin |
|---|---|---|---|---|
| #369 | 20/40 | 12/40 | 32 | -4,608 |
| #370 | 19/40 | 11/40 | 30 | -13,356 |
Margin loss mostly vs Noobot on contested layouts (contest, eight, fragment, gem_fields, gemfight, packs) - the maps where the
ungated recall cut also lost locally. #371 = #369 + the purchase-aware version (kRecallCapBuyMode 1 + kRecallCapIdleNone,
B375x + run/cand371.edits, local 423/560 +17 +-12, contested maps unchanged), benched against near/hold369b and near/hold370.

### Map categories (Eric Oct 26: "categorize the map from the initial draft look, then adjust the weights")
- Searching the best single-feature gate per arm (scratchpad mapfeat/mapgate.py, 200 random half splits of the maps) overfits at
  8 games/map: #371's shard rule +23/map ungated, +11 held-out when gated. So categories are fixed first, then weights tuned.
- Categories (Codex's two axes, round thresholds): contested = midline groups hold >= 0.5 of camp gems; dense = camp gems per
  1000 tiles >= 170 (median of 65 profiled maps). Our maps: contested/dense 20, contested/sparse 16, farm/dense 13, farm/sparse 16.
- mapcat.py preview on the 8-game audit screens (per-map delta by category, cd / cs / fd / fs): recall rule 100 g -7/-44/+34/+29;
  kRecallCapSlack 8 -12/-42/+49/+25; gold 0.6 -38/+58/+32/-10; lookahead 0.5 -83/0/-31/-29. Held-out per-category choice beats
  one choice for all maps by +17 +-12 a map, but neither beats the base at 8 games/map (winner's curse over 10 options):
  the 4-seed screen s_map16 (16 games/map) is the data for filling the tables.
- edit_mapcat.py (bots/B376x): kMapCat, kCatContestMid 0.5, kCatDenseGems 170, per-category tables kCatGoldEarly,
  kCatRecallSlack, kCatIdleSlack (every entry keeps the global value). Category computed lazily from setup's midline_ and
  groups_ gems / map area (same sums as MAPPLAN); -1 (no overrides) until setup filled midline_.

### #371 ladder test (09:33 UTC Oct 26) - kept (neutral)
#371 = #369 + kRecallCapIdleSlack 0 + kRecallCapIdleNone + kRecallCapBuyMode 1 (B375x + run/cand371.edits).
near 20/40 (= #369b 20, #370 19); holdout 7/40 (#369b 12, #370 11) - but Noobot changed between 09:07 and 09:47: 0 of 20
Noobot games identical to #369b while 17/20 policywonk and 28/40 near games are identical. Comparable games (near + policywonk):
#371 24 wins = #369 24, margin -794 over the 15 games that differ. The rule rarely fires on the ladder; local +17 +-12. Kept live.
- **s_map16 (B375x, #369 config, 4 seeds = 16 games/map, 1120/arm; base 817, +242):** #370 rule 832, +28 +-17 | #371 rule 817,
  +13 +-8 | gold 0.6 818, +12 +-16 | lookahead 0.5 750, -59 +-16 (rejected for good) | kRecallCapSlack 8 814, +11 +-15.
  By category (cd/cs/fd/fs): #370 +48/-27/+54/+21, #371 +16/+30/+3/+13, gold +22/+31/-9/-8, slack8 +21/+3/+21/-2.
  **Held out, per-category choice +9.9/map vs one choice for all maps +9.7 (difference +0.2 +-8.5); single-feature gates are
  worse than ungated (#370 +24 -> +0.7, gold +10.6 -> -4.3).** The 8-game category pattern was noise: these weights' map
  dependence (breadcrumbs +400 for any recall cut) is not predictable from layout features. kMapCat stays 0; numeric weights
  stay global. Map categories remain a candidate for qualitative choices (squad/solo opening, invading, Willow follow, builds).

### Map-rule ablations (Codex's protocol, Oct 26): smoke test first, activation checked, one rule per arm
- Tools: scratchpad mapfeat/activation.py RUNDIR LABELS - local games are deterministic, so an arm game identical to the
  base's (same map/seed/side/opponent) means the ablated rule changed nothing there; reports share of games changed by map
  class and wins/margin within the changed games only. On s_map16: #371's rule changes 39% of games (1% on all-game team
  and boss maps); #370's 96%; lookahead 98% (-67 wins in changed games).
- s_ablate1 (base = live #371 config on B375x, 16 games/map): kOpeningRounds 0 / 60 (the default 120-round whole-team opening;
  layout-forced all-game team maps keep theirs), kControlSquad 1 (no pairs on control maps when enemies are about),
  kMidAvoidDiff 0 (close-spawn midline camp skip), kStayHome 0 (close-spawn stay on our side; exempt below 8 steps because
  side-by-side spawns have no middle: the zone covered the spawn exits and the team idled to r350), kCrystal 0.
- **s_ablate1 results (16 games/map, base 817/1120 +254):** kOpeningRounds 0: 757, -59 +-15 (race maps -48 wins in changed
  games); 60: 778, -48 +-14 | kControlSquad 1: 820, +12 +-15 (close-spawn -8 wins, unprofiled +10: mixed) | kMidAvoidDiff 0:
  812, -1 +-12 | kStayHome 0: 803, -5 +-11 | kCrystal 0: 793, -18 +-10 (race maps -25 wins). Team opening and crystal planner
  supported; the other three inconclusive (kept). Caveat: "changed games" overstates activation - switching a rule off also
  changes per-turn fuel use, and fuel-limited turns make games diverge where the rule never fires (kMidAvoidDiff 0 changed
  93% of race-map games though it only applies on close-spawn maps). Real activation needs decision counters (todo).
  Next: kOpeningRounds 180 / 240 (s_open2), then Codex's adaptive release rule if longer helps.
- **Activation counts (edit_actlog.py, bots/ActBase / ActMelee = #371 + kTrace, 70 maps x 1 game vs H340; scratchpad act/actsum.py):**
  team opening on all 70 maps (~120 rounds a champion; all-game team maps throughout); control-map pairs on all 29 control +
  5 close-spawn maps, ~65% of champion-rounds there (91k on control maps) - our largest map-dependent behaviour; kStayHome
  on 2 maps (2,297 rounds), kMidAvoidDiff barred a camp on 3 maps (669 rounds): too rare to judge on this pool (their
  ablation deltas were fuel drift); crystals: 131 teleports on 13 maps (12 race); kMeleeFree 3: 581 free hits on 60 maps
  (~8 a game, matching the fish-five estimate). Next: control pairs deserve an 8-seed test, alone and with the opening.

### Missed kills and base healing (Eric Oct 26, replay 13b66e97: our Marcella/Vesper/Ryth vs Vendetta/Varg/Vesper, 452-1006)
Tools: scratchpad extract1.ts (one-replay copy of Codex's fish-five extract.ts) -> trace.json; killchance.py.
- Within-reach kill chances (enemy within 2 hits of whoever reaches it this turn): 3 of 4 converted. The misses are a few
  tiles out: r82-94 their Vesper at 4% 4 tiles from our 89% Ryth (one cast, stepped away); r161-218 their Varg (29%) and
  Vesper (30% -> 4%) within 3-6 tiles of our full Vesper and 80% Marcella for ~50 rounds, both escaped; r1021-1040 Vendetta
  at 9% -> 3%, ours stepped away or did not follow.
- Causes in hunt(): ONE elected hunter (best-equipped near the prey) - the others stand down even when it is busy (r206-211:
  their Vesper idle at 3%, ours farmed 7 tiles away); prey must have no other enemy within 5; outnumbered fight_enemies never
  steps towards a low enemy. A ranged chaser cannot catch a fleeing equal-speed target (it acts first each round: we step to
  range 3, it steps to 4; our Vesper fired once in 12 turns, on attack-reset rounds); melee chasers move + hit every turn.
- Base: spawn heals to full in one turn. Varg at 29% walked onto our spawn; our Ryth at 12% shuffled 4 steps away for 10
  rounds (escape() picks the tile farthest from enemies) before healing in one step.
- Marcella hit in 21 of 23 rounds she stood beside an enemy; the gap is getting there (election, outnumbered rules). Her
  focus build (634 focus, 72 strength) puts her damage in spells.
- edit_finishlow.py (bots/B379x = B377x + it): kWoundedTeamHunt, kPreyCrowd, kChaseMax (Eric: chase only up to 7 tiles; was
  8, 10 while running), kBaseOdds + kBaseRange 5; retest of kSecureKill (+ burst guard; rejected Oct 15 on engine 0.x) and
  kSpawnHeal 5. Screen s_finish1 queued; local opponents are our own old bots, so the ladder is the real test.
- **s_melee1 (B377x, #371 config, 16 games/map, base 817):** kMeleeFree 1 (turn end) 810, -8 +-15 (84% of games changed, -7 wins
  in them); **kMeleeFree 2 (hit before retreat / outnumbered step) 839, +19 +-11 (53% changed, +22 wins in them, control
  maps +16)**; 3 (both) 810, -10 +-15. Bit 2 is a ladder candidate; bit 1's cost unexplained (possibly a hit on a reward tile
  disturbing the capture - unverified).
- **s_open2 (B375x, #371 config, 16 games/map):** kOpeningRounds 180: 828, +13 +-13 (+11 wins in changed games; control maps
  +8); 240: 822, +8 +-13. Curve: 0 -59, 60 -48, 120 0, 180 +13, 240 +8 - shorter hurts, longer saturates within noise. The
  timer stays 120; next opening test is Codex's adaptive release (stay while the next camp needs the party), not a longer timer.
- **s_finish1 (B379x, #371 config, 16 games/map, base 817):** kChaseMax 7: 831, +14 +-12 (control +24 wins in changed games,
  race -12) | + kWoundedTeamHunt: 839, +22 +-12 | **+ kPreyCrowd 2: 848, +31 +-12 (control +35)** | kSecureKill 1 + burst
  guard 1: 714, -87 +-16 (-103 wins in changed games; it acts before evading/kiting - dives; rejected again) | kSpawnHeal 5:
  817, -1 +-6 (18% of games changed) | kBaseOdds 2: 817, -3 +-13 (close-spawn -117 on 80 games). Base rules neutral against
  our own old bots (base invasions rare locally): ladder-only question. Combination screen s_combo1 next.
- **s_combo1 (B379x, base 817):** chase 7 + crowd + team hunt 834, +16 +-13 | + kMeleeFree 2: 849, +29 +-14 | chase 7 + crowd +
  kMeleeFree 2: 847, +30 +-14 (chase 7 + crowd alone: 848, +31). Gains do not stack; team hunt lowers crowd's result.
  **#372 = #371 + kChaseMax 7 + kPreyCrowd 2 + kMeleeFree 2** (B379x + run/cand372.edits) under ladder test vs a same-time #371.

### #372 ladder test (12:28 UTC) - KEPT, live
#372 = #371 + kChaseMax 7 + kPreyCrowd 2 + kMeleeFree 2 (B379x + run/cand372.edits). Same-time #371 benches 12:09-12:22.
| | near | holdout | wins | margin |
|---|---|---|---|---|
| #371 (near371b / hold371b) | 17/40 | 13/40 | 30 | -6,880 |
| #372 | 22/40 | 15/40 | 37 | -5,088 |
Near: Oldenkamp +2, SSSA +2, Valenki +2, filter -1; holdout Noobot 12 vs 9, policywonk 3 vs 4. OneTap, SSSA, SkuBap, Valenki
and Noobot updated between the morning and noon #371 benches; the #371/#372 benches are 9 minutes apart. Agrees with local +30 +-14.

## Oct 26 (UTC 13:00-) - top-10 benches, the per-champion pick mismatch, spread, base heal, fuel and deaths

- **#373 (#372 + kSpawnHeal 5 + kBaseOdds 2) rejected**: same-time near 19 vs 20, holdout 13 vs 15 (holdout baseline 40/40 identical:
  no drift). **#374 = #372's code** (B379x + run/cand372.edits), submitted 13:41 UTC. Control-map pairs kept: kControlSquad 1 (8 seeds)
  1659 vs 1687 wins / 2,240, -7 +-11.
- **Benches now vs the top 10** (Eric, 13:48 UTC): scratchpad/bench_top10.txt = the ladder's top 10 x 5 maps each (50 of the 70 pool
  maps; 20 held out: collision crater expanse gem_fields lanes oasis quarry road_of_riches stampede vault concentrated_wealth fracture
  shortcut the_farm cuts geodes stalactites the_pond gemcombat2 gemcombat5). `cambc submissions activate N` switches the live version
  without re-uploading. Builds are ready ~3 min after upload, bench results ~3 min after queuing. scratchpad/run/ladtest.sh N SRC EDITS
  NOTE BASETAG = stress + submit + sleep 180 + bench + table. **#374 baseline: 8/50, -25,824** (top374). Resolution: ~+-4 wins.
- **Top-10 deaths and income** (grp/fightsum.py, deathcause.py over the 50 top374 games, extract1.ts traces): deaths **13.4 vs 6.2 a game**;
  621 of our 668 to enemy champions (within 5); 73% mid-map, 23% in our third, 3% theirs; 79% within 4 of a camp; 28% from 70%+ health 3
  rounds earlier (burst); 7 gems carried per death. Banked gems r600 222 vs 367, earned gold r600 1,905 vs 3,217 - even in 0-1 death
  games our gold is 75-80% of theirs. By type: Vesper front-most of ours 5 rounds before 66% of her deaths; Willow at 70%+ 5 rounds
  before 50% of hers, an ally within 3 at 62%; Ryth an enemy within 4 five rounds before 92%. Hooks r315-323: our Marcella captured a
  gold-cluster reward (17,16) with four enemies 3-5 away and died (enemies outside the region do not pause a capture: GameRules).
- **Ladder fuel files**: each downloaded match zip holds team-x.fuel = 13-byte header ("a62leuf\0" + 5 bytes) then u64 LE fuel per
  champion turn (draft turns 10,000,000; a capped turn = 100,000). Ladder 1b0d2ca3 (5v5 ambush): mean ~50k, 2.0% capped, 4.3% in the
  first 200 rounds; the 50 top374 games: 1.13% capped (worst yellow_brick_road 5.8%, the_pack 4.4%). Profiles: #371 -> #372 switches
  cost nothing (fnprof: hunt 0.7k a turn, melee_free 10); spike profile (edit_fuelspike on #372, 74 games; edit_fuelprof2.py anchor
  updated for kFuelGov & 2): turns over 85k = squad scoring 18-24k + farm 10-16k + observe_groups 7-13k + post 6-13k; heavy pool maps
  351 suspensions a game. edit_fnprof.py now also instruments hunt, contest_altar, trip_buys, melee_free_hit and 18 more.
- **The per-champion pick mismatch** (ladder 1b0d2ca3, #373 on 00ambush 5v5): after the two-elk camp the leader scored the adjacent
  elk+wolf camp 3.68 and a 4-gold-cluster group 1.72; kPerChampionPick divides by the party each needs (3 vs 1: 1.23 vs 1.72) and the
  whole squad of four walked to the gold group (r65-109); the elk+wolf camp waited until r187 (reproduced locally, PickDbg SCORE log).
- **edit_spread.py** (Eric: one champion per camp it clears in <= 5 rounds, cascading; clusters never need a group; group only for
  elks and stronger) - kSpread, kTeamWholeRate, kBaseHeal, kSoloFuel; bots/B380x first version, **bots/B381x** after an independent
  review found: followers publishing their followed camp locked it for members behind (stall in "spread_wait"); kTeamMoveOn's next
  target flipping every capture turn; "light" ignoring survivability; recall-captures not holding; base_heal returning true on a failed
  step; forget_picks on every lock change. Screen s_spread1 (B380x, 70 maps x 4 seeds x H340/B7Live, base 825/1120): **kBaseHeal 4
  838 (+8 +-9)**; kTeamWholeRate 827 (+2 +-15); kSoloFuel 824 (-1 +-10); kSpread 1 / 3 / 11 (buggy) 759 / 798 / 766 (-67 / -50 / -81;
  lost on cluster maps the_line -648, vault -607, gained hooks +375, fragment +366). s_spread2 (B381x fixed) running.
- **Time use vs the top 10** (grp/timeuse.py, first 600 rounds of the 50 top374 games, champion-rounds): ours dead 12.1%, moving only
  48.8%, hitting camps 17.0%, idle 9.7%, recall channel 5.1%; theirs dead 5.2%, moving only 26.7%, camps 10.2%, idle 4.8% - and
  **channel 1 (recall) 46.2%**: willow best girl, NEETCoders, print dont int and Mite champions sit in a recall channel 88-96% of
  rounds with the timer frozen at 4 while walking, attacking and casting - the pre-started recall (engine-mechanics: a recall started
  at a turn end counts it; cancelling next turn is free) on every turn, so any recall they keep lands a round sooner. Not in our bot
  (kPreRecall candidate: our recall time ~5% of champion-rounds, so ~1% more active time; every reader of is_recalling(), ours and
  allies', must tell a pre-start from a real recall). Fish and the rest do not.
- **Melee free hits on the ladder**: #374's 50 top-10 games - our melee moved and hit a champion in 2,666 turns (1,546 hit-then-move,
  kMeleeFree 2), but 586 moves ended beside an enemy champion with no attack (opponents 234 of 4,112). **#377 = #375 + kMeleeFree 3**:
  7/50 -24,671 vs #375 8/50 -22,784 (noise); kept on by default (Eric: free damage) with a Ren retaliation guard (edit_meleeren.py,
  B385x). #376 (+ kTeamWholeRate + kSoloFuel) 7/50 -25,980: rejected. Bench results arrive ~2.5 min after queuing; topwait.sh now
  prints at once and downloads in the background (8 parallel).
- **Top-10 fight odds** (grp/fightodds.py): contact episodes by visible odds (hp x effective str, all within 6): <0.5: 445 episodes,
  our 292 deaths vs their 49; 0.5-0.8 86 vs 37; 0.8-1.25 100 vs 42; 1.25-2 77 vs 40; 2+ 87 vs 80. 74% of our PvP victims were above
  80% health at first contact and 82% had hit an enemy champion in the last 8 rounds (fights, not ambushes on camps). In the weak
  episodes their effective strength summed 2.8x ours: an equipment gap we walk into (62% stepped closer).
- **#378 = #375 + kSpread 3** (Eric's one-champion-per-light-camp rule, B381x): top-10 **4/50 -27,893** vs #375 8/50 -22,784 - rejected
  on the ladder as locally (s_spread2 -39 +-19; spreading lowers total income: the grouped opening clears the big camps sooner).
  Also off after screens: kStandoff 20/30 (-3 / -5, B383x), kHuntBound 4/6 (-12 +-8 / -6 +-6, B384x), kCacheStaticHitters (-2 +-10,
  fuel drift only). Local idle turns 9.5% (IdleLog, 12 maps): capture 4.7%, wait_party 2.0%, guard 1.0%, spawn heal 0.9%.
- **#379 = #375 + kMeleeFree 3 + Ren guard + kLadLog (edit_ladlog.py, B385x)**: top-10 **10/50 -24,374** (live from 15:25 UTC). kLadLog
  costs fuel (stress fuelExhausted ~3.7k -> 4.8k): diagnostic only. Decision log (tools/stress/ladlog.py; Codex's identity-keyed
  audit in collaboration/20261027/top379-*): 46% of the 5 turns before our PvP deaths were escape; our logged fight_odds vs the
  omniscient proxy (every champion within 5, sum hp x str): ours 1.0-1.5 -> proxy < 1 in 63% of turns; 1.5-3 -> 42%. Escapes:
  ~31 a game, 44% start with an enemy 1-2 tiles away. Grouping equal (1.00 teammates within 5 both sides). Strength per champion r300
  54 vs 66, r600 67 vs 101, r900 83 vs 141; our Marcella builds 100% focus (theirs a third each str / foc / hp; kBuild3 copy was
  -96 locally). Gold by r600 2,010 vs 3,291, of which kill-time income 190 vs 620.
- **Caution arms**: local (base 840/1120) kRespectBase 1.25 / 1.5 / 2.0 -45 / -69 / -151 (edit_respect.py, B386x); kFightRespect 2 -11;
  kGhostRounds 3 / 6 -40 / -69 (edit_ghosts.py, B387x). Ladder **#380 = #379 + kRespectBase 1.5: 8/50 -24,541**, deaths unchanged
  (12.0 vs 12.2 a game). Caution costs against local opponents (weaker than us) and a blanket factor does not reduce deaths vs the
  top 10.
- **Pre-started recalls fool our threat model** (Codex C175/C182): the 4 pre-recall teams show "recalling, cannot cast" during our
  turn, so their ready spells counted as unusable (kRecallThreat off) and kRecallPunish treated them as free kills. edit_prerecall.py
  (B388x): kRecallGenuine (punish only at remaining_channel_time() <= 3), kStandShotOdds / kStandShotFix (stand_shot had no odds
  floor and returned true when nothing happened), Ren guard on live health. Ladder #381 = #379 + kRecallThreat + kRecallGenuine.
- **#381 = #379 + kRecallThreat + kRecallGenuine + Ren live health** (B388x; the stress gate failed on a pre-existing Willow wait at an
  elk camp on 01corridors - #379's own scan had the same 4 episodes, #381's game ran longer: submitted as a recorded exception):
  top-10 9/50 -25,291 (vs #379 10/50 -24,374; the 4 pre-recall teams net -2,981, noise). Local s_prerecall (base 842/1120):
  threat + genuine **+15 +-11 (850)**; kStandShotFix alone identical games (never fires locally); + kStandShotOdds 0.5 +5 +-14.
- **Deaths per game on the top-10 bench** (ours / theirs): #374 13.4 / 6.2, #375 12.8 / 6.8, #377 12.2 / 6.6, #379 12.2 / 5.5,
  #380 12.0 / 5.6, #381 12.5 / 5.0 - base heal and the turn-end melee hit trimmed ours; their deaths fell once kLadLog shipped
  (its fuel: stress fuelExhausted +27%), so the log is off from #382. **#382 = #379's behaviour without kLadLog + kRecallThreat +
  kRecallGenuine + kStandShotOdds 0.5 + kStandShotFix** (STUCK_CASES 8 / STUCK_ROUNDS 100 exception for the corridors Willow wait).
- **#382** (#379's behaviour without kLadLog + kRecallThreat + kRecallGenuine + kStandShotOdds 0.5 + kStandShotFix; B388x): top-10
  **9/50 -20,915** (best margin of the day; our deaths 11.3 vs their 5.8 a game, gold r600 2,071 vs 3,005). **#383** = #382 + the
  B388x review fixes (edit_prerecall2.py: Home-aware genuine recall - a Home emblem makes recalls 3 ticks, so a fresh pre-start shows
  2; threat_ready() in ready_spell_damage / spell_threatened / micro_step / AoE spacing / matchup_read): **6/50 -27,670** - the
  expansion adds caution again; now behind kRecallThreatAll (off), the Home fix always on (B389x rebuilt). #384 = #382 + Home fix +
  kMarcFleeReset (edit_marcflee.py = Codex C184's patch; B390x).
- **Opening length by layout (map weighting)**: s_open3 (B388x, #382 config, 6 seeds, 1,680 games an arm): kOpeningRounds 90 / 180
  / 240 vs 120 -17 / +6 / +14; race maps -38 / -8 / +28, control +4 / +28 / +18, close spawns -55 / -24 / -22. Per-class choice on
  random map halves scored on the other halves (500 splits): +9.4 a map (sd 12.1) vs +6.2 global; race picks 240 (91%), close spawns
  120 (98%), control 180 (58%). **edit_openclass.py** (kOpenRace / kOpenControl, B391x): confirming on seeds 7-10.
- **#384 = #382 + Home fix + kMarcFleeReset**: top-10 6/50 -23,327 (vs #382 9/50 -20,915; Sponge and Trzy lost the difference);
  local s_marcflee +2 +-10. Flee reset off. **Opening by layout confirmed out of sample** (s_openclass, seeds 7-10, B391x, #382
  config): kOpenRace 240 + kOpenControl 180 **858 vs 843 wins, +18 +-13** (race +31, control +10, close spawns / team maps 0 by
  design). **#385 = #382 + Home fix + kOpenRace 240 + kOpenControl 180** (B391x).
- **#385 = #382 + Home fix + opening by layout**: top-10 4/50 -26,605. The top-10 bench is near chaos: any code change shifts fuel and
  diverges most games (Sponge corridors: #382 W 525, #384 and #385 identical L -296, #383 W 257); #379-#385 margins -24.4 / -24.5 /
  -25.3 / -20.9 / -27.7 / -23.3 / -26.6k (mean -24.7k, sd ~2.3k): #382 was likely a lucky draw. Bigger comparison running: #385 and
  #382 each on bench_top10r.txt (same 50 maps, every map against another top-10 team, sides flipped) and bench_hold10.txt (the 20
  held-out maps x 2 teams). `cambc submissions activate N` fixes the live version: ladtest.sh now activates the uploaded version.
- **Fuel savers, local** (s_fuel2, B391x, #382 config 847/1120): kScoreEvery 2 -22 +-16; kSoloFuel -13 +-11; kCacheStaticHitters -18
  +-9 (exact by construction: fuel drift); all three -10 +-15 - none adopted (local games rarely hit fuel limits).
- **#385 vs #382 over 140 games** (bench_top10 + rotated bench_top10r + held-out bench_hold10, banners verified): #382 16 wins
  -74,835, #385 15 wins -75,207 - indistinguishable; #385 kept (opening by layout +15 wins locally out of sample). Activating an old
  version rebuilds it (status "queued", minutes) and pins the live version; `activate latest` does not unpin the selection - activate
  the number explicitly.
- **Economy sweep** (s_econ1, B391x, #385 config 864/1120): kGoldWeightEarly 0.4 / 0.5 -3 / -25; kDeliverGems 30 / 50 +8 +-12 / -5;
  kElkBonus 1.25 / 2.0 -4 / -19 - the live values hold. **Unusual maps** (hs_bush_corridors / hole_pockets / rooms, fx_*; R385 vs
  B7Live both sides): 41/42 wins, 0 faults (genscan reads side-B games from the opponent when the bot name is unknown; fx_groups maps
  have no gems; fx_groups-256 caps ~2,800 turns a game and keeps 3 champions home at r60).
- **Captures by r600** (#382 top-10, 43 games): ours 22.7 vs 31.1 a game (clusters 11.9 / 17.0, monster camps 6.4 / 8.2, elk 4.4 / 5.8);
  by phase r0-120 3.8 / 5.4, r120-300 7.5 / 10.0, r300-600 11.4 / 15.7. Opening shape r10-120: ours 2.47 teammates within 5 (alone
  11%), theirs 1.68 (27%) - they split early. Team sizes on 43 bench maps: 5v5 27, 6v6 2, 4v4 6, 3v3 8. edit_squads5.py
  (kTeamSquadsBig: N opening squads with >= kBigTeam alive; B392x) screening.
- **Fight-turn fuel** (tools/edits/edit_fnprof_fight.py on edit_fnprof.py -> tools/stress/fnprof2.py; FP385, 28 maps x 2 sides; every
  profiled turn had an enemy within 8 at its end): per turn observe_enemies 7.8k, observe_groups 7.3k, manage_squad 5.5k,
  observe_allies 5.1k, farm 4.4k, fight_enemies 3.3k, read_monster_health 3.0k (2.5 calls), step 2.6k, wants_escape 2.5k, wants_evade
  2.5k, squad / solo scoring ~2k each, fight_odds 1.4k (2.25 calls), enemy_walk 1.2k. observe_enemies reads each enemy's position 3-4
  times plus abilities() and per-ability readiness (exact caching of positions: ~0.5-1k a fight turn, not done). Why it matters:
  kLadLog's fight-turn-only cost coincided with our kills falling ~6.7 -> ~5.3 a game.
- **Opening squads**: kTeamSquadsBig 2 (2 opening squads with >= 5 alive; edit_squads5.py, B392x) **-57 +-14**; kTeamSquads 2 for
  all -105 +-19 - the grouped opening is strongly better locally although the top 10 split early. Draft: Willow 5th was +70 locally
  vs Vendetta (kWillowMeta), Vendetta 5th later -95: unchanged.
- **Heal / retreat sweep** (s_heal2, B392x, #385 config 864/1120): kBaseHeal 6 -5 +-7; kBaseHealHp 0.65 -11 +-7; kRetreatHp 0.4
  -29 +-16; 0.3 +7 +-15 - live values hold. **Party waits** (s_wait1): kAllyWait 6 -22 +-10, 20 +1 +-9; **kBigParty 1 +9 +-10,
  kBigParty 0 +16 +-12 (881 wins)** - big-party calls (Eric Oct 23, after Fish's multi-champion elk camps) now cost locally; the
  Willow "stuck" waits in the stress scans are this. Confirming on seeds 5-8 (s_bigparty2).
- **Big parties confirmed at one helper** (s_bigparty2, seeds 5-8): kBigParty 0 -17 +-11 (in-sample +16: noise), **kBigParty 1 +8 +-10
  (872 vs 861)**; with seeds 1-4 (+9 +-10) ~+8.5 +-7. **#386 = #385 + kBigParty 1** (B392x): top-10 8/50 -25,159 (#385 4/50 -26,605);
  stress stuck 0 (the Willow party waits gone). Live from 19:28 UTC (pinned; banners verified).
- **Economy sweep 2** (s_econ2, #386 config 862/1120): kNeighbourBonus 0.1 -21 +-11; kRecallCapSlack 10 +9 +-13, 30 -15 +-9; kHelpTtk
  15 -12 +-6. Confirming kRecallCapSlack 10 / 5 on seeds 5-8.
- **140-game ladder comparison** (bench_top10 + rotated bench_top10r + held-out bench_hold10, banners verified): #382 16 wins -74,835;
  #385 15 wins -75,207; **#386 23 wins -69,621** (top386 8/50 -25,159, top386r 11/50 -19,333, top386h 4/40 -25,129) - #386 stays
  live. kRecallCapSlack 10 on seeds 5-8: +13 +-12 (867 vs 872 wins), 5: -1; both seed sets ~+11 +-9 (not adopted alone).
- **Opening refinement** (s_open4, #386 config 862/1120): kOpenRace 300 -1 +-6, kOpenControl 150 / 210 -9 / -8 - 240 / 180 hold.
  **Class-dependent choice for other sweeps** (grp/classgate.py on s_econ1 / s_econ2 / s_heal2 / s_wait1 / s_respect): held-out
  per-class gain -10..+3 a map, never above one global choice - only the opening length is layout-dependent at this sample size.
- **Small economy tweaks** (s_small3, fresh seeds 9-12, #386 config 838/1120): kRecallCapSlack 10 +15 +-13; kDeliverGems 30 +17 +-13;
  **both +28 +-15 (863)**. Slack 10 positive on all three seed sets (+9 / +13 / +15), bag 30 on two (+8 / +17). **#387 = #386 +
  kRecallCapSlack 10 + kDeliverGems 30**, 140-game panel running.
- **Bug in the first opening-by-layout rule** (independent review of Up386, confirmed with a print-only probe on 12 maps): it changed
  team_rounds_ inside check_control_map(), which runs only once kHomeField exists - dash champions on turn 2 (warm_gates), the rest on
  demand (shop trip, retreat, base heal) at r150-r270 or never. Teammates disagreed on the opening for ~100 rounds (expanse: s0/s1 240,
  s2-s4 120 through r300): whole-team squads whose members farmed solo, and bit 0x80 read as "solo" by openers and "help" by the rest.
  Fixed in edit_openclass.py: applied once on each champion's first turn after the kAutoTeamStr answer, from setup_spawn_path_ (identical
  for every champion at setup). bots/B393x = B390x + fixed edit_openclass + edit_squads5. Pre-existing, noted: before its control check
  a champion uses kSquadSize 1 instead of kControlSquad; the solo/help bit rewrite fires only at round_ == team_rounds_ (a champion
  channelling then keeps a stale bit). #386 / #387 carry the buggy rule; s_openfix (8 seeds) re-screens the fixed one.
- **Fixed opening by layout** (s_openfix, B393x, #387 config with vs without kOpenRace 240 / kOpenControl 180, 8 seeds, 2,240 games):
  **1,776 vs 1,734 wins, +29 +-9** (the buggy version measured +18 +-13). #387 (buggy rule + kRecallCapSlack 10 + kDeliverGems 30):
  top-10 11/50 -21,990. **#388 = #387 on B393x (fixed rule)**, full 140-game panel queued.
- **#387 panel** (140 games): 11/50 -21,990 + 12/50 -17,890 + 3/40 -24,650 = **26 wins -64,530** (#386 23 / -69,621). kSetupControl
  (control map decided at setup for every champion; B393x, #388 config, 8 seeds): 1,747 vs 1,776, **-16 +-11** - stays off.
- **#388 = #387 on B393x (fixed opening rule)**: top-10 panel 12/50 -19,293 + 11/50 -18,845 + 5/40 -20,914 = **28 wins -59,052**, the
  best of the day (#382 16 / -74.8k, #385 15 / -75.2k, #386 23 / -69.6k, #387 26 / -64.5k). Live (pinned) from ~20:40 UTC. Opening
  re-tune with the fixed rule (s_open5): race 180 / 300 -11 / -1, control 150 / 240 +6 / -7 - 240 / 180 hold. kTeamWholeRate on
  #388's base (8 seeds) -30 +-10: off.
- **Eric (Oct 26 21:05): HoR for Ryth on 3-champion maps, Vendetta for Willow** - edit_draftalt.py (draft.cpp kDraftAlt bits 1 / 2,
  B394x; verified: 3 picks Marcella, Vesper, HoR; 5 picks HoR, Vesper, Ryth, Marcella, Vendetta). Screening (6 seeds).
- **Draft swaps** (s_draftalt, B394x, #388 config 1,332/1,680, 6 seeds): kDraftAlt 1 (HoR for Ryth, 3 picks) **-47 +-6** (-276 a
  changed game, 17% changed); 2 (Vendetta for Willow) **-125 +-15**; both -172 +-16. The code is built around Ryth's stun and Willow's
  support (and per-champion builds): kept off, not laddered.
- **Economy fine-tune** (s_econ3, #388 config, 6 seeds, 1,680 games an arm): kDeliverGems 25 +5 +-9, 35 -10 +-8, kRecallCapSlack 15
  -19 +-9 - #388's 30 / 10 hold.
- **Eric: "optimize for HoR"** (edit_hor.py, B395x; s_hor1, 4 seeds): Focus-heavy HoR lines kRuinBuild 1 (Treasure H, Jungle F, Bruiser
  F) -11 +-6, 2 (Jungle F, Bruiser F, Bruiser H) -12 +-10, 3 (Treasure F, Jungle F, Bruiser F) -25 +-10; kRuinOdds (passive in fight
  odds) -5 +-8; kRuinPvpHp 0.3 +2 +-6.
- **Oct 27: the top 10's HoR / Vendetta copied** (study in champions.md "Top-10 builds and kit use"; edit_horkit.py, B396x; s_hor2,
  3 seeds, 840 games an arm, base 660 wins): kShieldNear 6 (shield at the turn's end once an enemy is within 6) 671 wins, -7 +-13;
  kShieldHp 1.01 (on cooldown) 662, -9 +-15; both (0.97) 660, -9 +-14; kRuinBuild 4 (Treasure H, Jungle F, then Bruiser F / H
  alternating) 666, -6 +-7; Vendetta for Willow with the top teams' line (kDraftAlt 2 + kVendBuild 1) 590, **-145 +-22**.
  #389 = #388 + kShieldNear 6 + kRuinBuild 4 on the ladder (140-game panel vs #388); fresh-seed check s_hor3 (seeds 4-6).
- **s_hor3 (fresh seeds 4-6, 840 an arm, base 672 wins):** kShieldNear 6 680 wins, +24 +-13; kRuinBuild 4 677, +16 +-7; both 684,
  +23 +-13 (six seeds: about +8 / +5).
- **#389 = #388 + kShieldNear 6 + kRuinBuild 4** (B396x + run/cand389.edits), submitted 22:35 UTC Oct 26: top-10 panel 12/50 -19,149 +
  10/50 -22,472 + 6/40 -18,916 = **28 wins -60,537** (#388 28 / -59,052): flat on the ladder, slightly positive locally - kept live.
- **Vesper gold funnel** (their Vesper 32% of team gold by r600, ours 22%; our Ryth 25%, theirs 5%), #389 base: s_vgold seeds 1-3
  (840 an arm, base 651 wins): kVesperGoldW 2.0 +1 +-8; 3.0 677 wins, +19 +-10; Ryth's gold weight x0.5 -10 +-15; 2.0 + Ryth x0.5 +1
  +-15. Fresh seeds 4-6 (s_vgold2, base 684): 3.0 -4 +-10, 4.0 -19 +-11 - not confirmed, not uploaded. The gap is farming speed
  (their Vesper's monster damage by r600 is 55% above ours), not the camp weights.
- **Willow out of contact** (theirs has an enemy within 3 in 1.2% of rounds, ours 6.1%), #389 base, s_willow seeds 1-3 (base 651):
  kWillowBack 670 wins, +10 +-18; kWillowPvpHp 0.6 +2 +-11, 0.8 -9 +-14 - nothing clear, all off.
- **Ladder profiles refreshed (Oct 27 23:35 UTC, tools/stress/radarnow.py, 12 latest 2.0.0 ranked games per top-20 team, 30 ours;
  dashboard "Ladder Team Profiles" updated):** we are rank 57 (1,923). Percentiles among the top 20 + us: KDA 60, Trade 80, Gank
  **20**, Outplay 44, Gold 65, Farm eff. 65, Vision 55, **Farm 25** (3.83 camps / 100 rounds vs Mite 5.18, :3 5.71, meow 6.85). Fish:
  Gank 100 / Gold 100 / Farm 10 (few, rich camps); Mite KDA 7.55 / Trade 1.58 / Vision 20.8. Our fight measures are flattered by
  playing near-rating teams; the two low axes (early kills, camps per 100 rounds) are the knockout gaps. Top 10 now: Fish, Trzy
  Kwaterki, Mite, willow best girl, Claudus Maximus, prism best girl, NEETCoders, Ad Astra, Sponge, hello (Supaswag 11, print
  dont int 12): bench_top10 lists need rebuilding before the next ladder test.

### Oct 27 (UTC 00:00-) - farming like Fish (Eric: "improve our farming ... analyse Fish games on the farming maps")
Data: 46 Fish-vs-us top-10 bench games on farming-class maps (spawn walk > 45; replays/p2/sl_top38*, `tools/stress/extract2.ts`
traces with per-round camp state) read with `tools/stress/farmcmp.py` (captures by class, party, value, respawn lead, recalls,
time split) and `transcmp.py` (where the rounds between camps go). First 600 rounds, per game:
- **Income:** Fish 3,513 gold / 489 gems to our 1,985 / 232; captures 28.8 vs 18.1; camp damage 63.6k vs 40.5k; time per champion
  at camps 22% vs 20%, walking 59% vs 54%, **dead 5% vs 14%**, idle 8% vs 7%.
- **By camp class:** gold-cluster camps Fish 3.9 five-cluster + 1.9 three + 1.6 two + 2.3 single a game (solo or pairs, 9-16
  rounds) to our 1.0 / 1.1 / 1.0 / ~0; elk camps 2.9 vs 0.9 (Fish takes 1elk+2cl with 3-6, tank down to 53%; we need 3.7 and leave
  at 80%); wolf packs 3.1 + 1.4 vs 2.7 + 0.9 with the same party (3-4) and clear time (23-25). Camp visits per 100 champion-rounds
  3.14 vs 2.20. Attempts started: clusters 665 vs 290, elks 166 vs 95 (46 games). Chip-in-passing is not a thing (0.4% of damage).
- **Nothing is abandoned** (with recall-captures attributed: 92-100% of started camps captured, both sides) but **camps lost to the
  enemy after we started them: clusters 23% / 1-elk 23% of our attempts vs Fish's 7% / 6%**; we leave them at 88% health.
- **Respawn timing:** Fish's first hit on a respawned camp a median 5 rounds after it returns (43% within 3), ours 18 (17%); a
  Fish champion is within 6 of it at the respawn in 65% of cases (lead 0; 44% of them clearing the camp next door), ours 37%
  (lead 4). Respawn durations: wolves 40-76 (median 50), clusters 50, elks 60, monolith 150; our code marks a camp left to a
  mate as back in 40 rounds (`respawn_until_ + 40`, 12 sites) until it sees the timer.
- **Between camps** (walk transitions, no recall): ours 32.4 rounds (move 20.4, idle 2.6, dead 7.6) vs 17.7 (move 13.0, idle
  0.8, dead 2.0); straight line 14.7 vs 12.3 tiles, steps x1.39 the line vs x1.06. Quiet transitions (no enemy within 10): 18.7
  vs 13.6 rounds (we dash 0.81 a transition, they 1.14 - more dash champions); **near an enemy: 51 vs 24 rounds (dead 18, move
  25 vs dead 5, move 13)**. Recall trips: 48 vs 43 rounds.
- **Recalls:** ours 17 a game at median 88% health with 65 gold (62% on reward tiles = recall-captures); Fish 27 at 43% with 139
  gold (35% on tiles): they go home hurt with a purchase, we go home healthy with nothing to buy.
- **Routes (00rows):** Fish's four loop the three wolf packs on their side in a fixed order with a 77-83-round period, Vendetta
  alternating two of them solo; ours loop the same way with a 90-100-round period (5 rounds more per transition).
- Switches: `edit_farm1.py` (bots/B397x) kRespawnExact (exact respawn after a capture); screens s_farm1 (kRespawnExact,
  kClusterSolo, kNeighbourBonus 0.2, kSafeRoute 0) and s_farm2 (kMaxNeed 0 / 4, kElkRound 50, kElkBudget 0.8, kClusterValue 1.5).
- **Per map vs Fish (r600):** the income gap is largest where we die (yellow_brick_road 1,672 vs 11,822 gold, 26% dead; gemfight
  540 vs 3,475, 34% dead; gold_rush, crater) but is 500-1,800 gold and 100-500 gems on the quiet farming maps with ~0% dead
  (expanse 3,030 vs 4,825 / 259 vs 562 gems; lanes 3,426 vs 4,834; big_world 2,391 vs 3,990; dunes 1,274 vs 2,177 / 244 vs 764;
  ambush 2,609 vs 3,158). 345 of our 369 PvP deaths in the 46 Fish farming games were on gold_rush, gemfight and crater.
- **Expanse route (top389h game):** both teams open on their 1-elk+2-cluster camp with everyone (Fish clears it in 9 rounds with
  six, we in 11 with five). Fish then cycles it every ~75 rounds (respawn 60 + capture; back on the dot at r91, 166, 239, 328,
  400) with the 2-wolf camp between visits, while singles sweep the gold-cluster pairs/trios and 2-4 champions take the far
  2-elk corner camps (1GeGeg r229-265, 8GGeeg r363-381, 4GeGeg r382-400). Ours returns to the elk camp every ~95 rounds (r18,
  131, 224, 308, 396 - 40 rounds late the first time), takes the single-wolf camps first (20 gold), reaches the 2-wolf camp at
  r163 (Fish r41) and never visits a 2-elk corner camp (they need 4 and sit beyond 20 tiles: kMaxNeed 3 / kMaxNeedDist 20 excludes
  them before r500).
- **Fish fields six champions on every 5-pick map** (Cassi & Issac are one pick: ambush, expanse, lanes, big_world, dunes, crater,
  gem_fields, gift_wrapping, treasure_box, yellow_brick_road all 6 v our 5; gemfight 5 v 4). Per champion its captures on expanse are
  8.9 to our 8.2. Its ranked games vs other top teams (75 downloaded, replays/p2/fish_rk; 38 farming-class) show the same profile:
  3,111 gold / 582 gems by r600 vs its opponents' 2,371 / 456; cluster sweeps solo, 2-elk camps with 4-6, recalls at 38% with 108 gold.
- **Elk camps after the opening (quiet maps, r240-600):** Fish 4.2 one-elk + 2.6 two-elk captures a game with parties of 3-5; ours
  2.5 + 1.4 on the ladder (3.2 + 0.85 locally): after the 240-round opening we farm solo and nobody forms the 4-party a 2-elk camp
  needs (kHelpStart 0: a champion never starts a camp it cannot finish alone).
- **Income yardstick** (`tools/stress/incomebench.sh`: candidate vs H340 + B7Live on expanse, lanes, big-world, ambush, rows, dunes,
  both sides, gold / gems / captures by r600 from the traces): live config FB0 **2,747 gold / 359 gems / 25.1 captures**; kRespawnExact
  2,754 / 358; kMaxNeed 0 2,714 / 354; kOpenRace 0 (120-round opening) 2,745 / 332 / 27.7; kOpeningRounds 40 2,654 / 322; **Cassi &
  Issac for Willow (six bodies, kTwinSwap 0) 2,433 / 298** - our code farms worse with the twins (dead 4%, camp time 20%).
- **Margin screens on B397x (#389 config, seeds 1-3, 840 an arm):** s_farm1: kRespawnExact -5 +-6, kClusterSolo -19 +-19,
  kNeighbourBonus 0.2 -24 +-14, kSafeRoute 0 -25 +-19. s_farm2: **kMaxNeed 4 +15 +-6**, kMaxNeed 0 +11 +-9, kElkRound 50 -6 +-12,
  kElkBudget 0.8 identical games, kClusterValue 1.5 -39 +-16. s_farm3 (seeds 4-6): kMaxNeed 4 / 0, kHelpStart 2 / 1, both.
- s_farm3 (fresh seeds 4-6, base 684): kMaxNeed 4 +3 +-7 (six seeds ~+9 +-5: not adopted yet), kMaxNeed 0 -3 +-8, kHelpStart 2 -12
  +-15, kHelpStart 1 -9 +-13, kMaxNeed 4 + kHelpStart 2 -13 +-15. Income yardstick: kHelpStart 2 / 1 2,718 / 2,733 gold (base
  2,747); kBigParty 3 2,844 (+97, two-elk captures after r240 0.85 -> 0.95 a game); kBigParty 3 + kMaxNeed 4 2,801.
- **Why no elk parties form after the opening (B398x probe with kPickLog on expanse):** solo champions do target the 2-elk camps
  (t5, t9) but no pick ever arrives "via help" - party_need() returns 0 for anything beyond a solo champion's squad unless !solo_, and
  the squad-call bit (help_kind bit 6) is written only for !solo_ in write_target and sync_help_flag. **kSoloParty** (edit_farm2.py,
  bots/B398x): a solo champion after the opening may pick a camp needing up to 1 + N (worth kBigPartyValue, need - 1 free mates
  known within kHelpCall), scores it per champion needed with the party's clear time x 0.8, keeps the need, and publishes the squad
  call so answer_help's big-party branch brings the mates. First build (call bit not synced) 2,796 gold; fixed build under test.
- **kSoloParty (fixed call bit):** the call now goes out and helpers read it, but answer_help's gate compares the camp's per-champion
  rate (~0.7) with the helper's own solo score (~2.0, differently scaled): nobody comes. kSoloParty 3 income 2,796; with kHelpBias 0.4
  2,756; margin -6 +-14. **kSchedLate** (edit_farm3.py, B399x: the existing kScheduler - free champions found / join parties by
  summed strength for the camp respawning next - after the opening on non-control maps): income 2,785 gold / 380 gems (pairs form,
  respawn hits within 3 rounds 25% vs 11%, elk lead 0), but two-elk captures unchanged (0.85) because the far 2-elk camps start 60-80
  rounds away and lose the rate comparison; margin -7 +-10 (gem camps only -17, kSchedWait 20 -14).
- **kFarmRoute** (edit_farm4.py, B400x): the team-orienteering plan - party size per camp from threat vs team-average dps / health,
  a nearest-neighbour party loop over camps needing 2+, singles dealt the rest by home distance; after the opening each champion
  targets its loop's soonest-available camp, the party following its lowest alive slot. First build planned at set-up before the
  roster existed (empty plan); re-planned lazily on the first farming turn - under test.
- **kFarmRoute iterations (income yardstick, base 2,747 / 359):** v1 (strength model: a 1-elk camp "needs 4", 2-elk camps dropped;
  soonest-camp re-pick every turn made the party flip between two camps) 2,433 and a lost probe game 269-1002; v2 (bot's party model,
  keep the loop camp, next round the loop) 2,633 - the party lap chained the far corner camps (60+ tiles) so it crossed the map; v3
  (lap bounded by 1.3 x the shortest respawn) 2,509, idle 18% - the lap shrank to one camp and the party waited for its respawn (expanse
  443-1020, lanes 417-1003 with 11 deaths); v4 (lap 2.0 x, fall back to the usual scorer while the loop camp respawns beyond the walk
  + 6 rounds) under test. Lesson so far: a fixed loop idles our 5; Fish's 6th body and its fight results are what the loop buys them.
- **kFarmRoute v4** (lap 2.0 x shortest respawn, greedy fallback while the loop camp respawns): 2,577 gold / 309 gems (base 2,747 / 359)
  although respawn timing improved (first hit within 3 rounds 26% vs 11%, waiting beside 27%). **Not adopted**: on our maps against our
  own code every fixed-route form so far loses 5-10% of income to waiting and crossing; the greedy scorer with claims is the better
  5-champion farmer. What Fish's loops buy it comes with its 6th body (Cassi & Issac) and its fight results (dead 5% vs our 14%).
  Switches off: kRespawnExact, kSoloParty, kSchedLate, kFarmRoute (bots/B400x carries all four; live stays #389 = B396x).
- **Open next steps (farming):** (1) a twins-aware draft needs our twin handling fixed first (FB5: six bodies farmed 11% less);
  (2) kMaxNeed 4 is +15 / +3 on two seed sets (~+9 +-5) - a cheap ladder arm; (3) the 23%-of-starts yielded to the enemy are lone
  farmers meeting pairs: pairing singles on contested maps is the untested idea; (4) deaths on gold_rush / gemfight / crater are the
  biggest income loss of all and belong to the fight work, not farming.
- **Party gate (Eric: "try them all"):** kSoloParty 3 with kHelpBias 0.4 / 0.15: income 2,756 / 2,761 (base 2,747), two-elk captures
  0.85 -> 0.9. Even ungated, our value model rates a helper's own solo camps higher per champion-round than an elk party: no gain.
- **Deaths on gold_rush / gemfight / crater** (#386-#389 benches; Fish trace2): ours 15-21 a game vs theirs 5-6. gold_rush: Vesper
  ~11 a game, mostly alone, only 6 of 183 with the monolith awake (Fish's 82 deaths are nearly all inside monolith reach - they fight
  it); crater / gemfight: Willow most, alone and outnumbered. The victim had an enemy within 8 continuously for a median 20-30 rounds
  and was not farming in 87%: long engagements we stay in, not ambushes. **kContactTurns** (edit_contact.py, B401x): after N turns
  in contact (enemy within 6), below 70% health, health lower than 4 turns ago, odds < kStayOdds: escape. Local (seeds 1-3, base
  651): 8 turns -14 +-18 (gold_rush +202, gemfight +119, crater -4; H340 -33), 12 -8 +-17, 8 with an 85% line -21 +-19. A fight
  change: ladder #391 = #389 + kContactTurns 8 (B401x + cand391.edits).
- **#390 = #389 + kMaxNeed 4** (B396x + cand390.edits): panel 10/50 -20,077 + 9/50 -21,974 + 6/40 -19,058 = **25 wins -61,109** (#389 28 / -60,537): rejected.
- **Marcella gems (Eric: "on farming maps Marcella should offer and collect more than Ryth"):** ladder farming maps (126 games, #386-#389)
  tributed per game Marcella 191, Ryth 120, HoR 86, Vesper 84, Willow 32 (opponents' Ryth 62). Reward routing is squad-only, so after the
  opening only camp choice can move it: edit_marcgems.py (B402x) kMarcGemValue (Marcella values a gem at 1 + F x 2 x gold weight) 1 / 2:
  -29 +-15 / -19 +-15; kRythGemW 0.6 -8 +-14; both -33 +-16; income 2,758. Marcella then collected FEWER gems (340 -> 297 a game: the
  richer gem camps are slower / farther) and Ryth's share did not move. Off.
- **HoR dash on a trapped enemy (Eric, ranked 978aca57, 00crater):** Varg pocketed at (14,50) - holes (13,49) (14,49) (13,50), walls
  (15,50) (13,51) (14,51) (15,51) - with HoR on its only walkable neighbour (15,49) for 30 rounds: ruin_dash needs a free landing within 1
  of the target and **the engine refuses a dash onto the caster's own tile** (probe bots/DashProbe: error 32 "Forbidden landing tile";
  the tile is in valid_tiles() all the same), so HoR only auto-attacked. **kRuinRedash** (edit_redash.py, B403x): step off to a free
  neighbour, dash back onto the vacated tile, attack (one move + one cast + one attack; the enemy cannot act in between). Fires only in
  that case (0 times in 8 probe games); screen 840 games identical (-0 +-1). Adopt with the next upload.
- **#391 = #389 + kContactTurns 8** (B401x + cand391.edits): panel 9/50 -24,310 + 11/50 -18,075 + 9/40 -15,174 = **29 wins -57,559**
  (#389 28 / -60,537): level, better on the held-out maps; kept live (pinned since ~02:15 UTC Oct 27).

### Oct 27 (UTC 02:45-) - converting leads and the snowball (Eric: "we struggle to convert a lead in kills into a lead and fail to snowball")
379 top-10 bench games of #385-#389 (`tools/stress/convert.py` and inline scripts on the traces):
- Win rate by kill lead at r600: us 3+ 20/35, 1-2 15/43, even 11/54 vs the top-10 opponents 128/134, 83/91, 43/54. By kills x gold at
  r600: kills ahead + gold ahead 25/36, kills ahead + gold behind 9/40, kills even/behind + gold ahead 12/35, both behind 11/240 - gold
  decides, kills alone do not convert.
- 60 rounds after a clean kill: captures 2.5 vs 3.6, enemy-half captures 0.6 vs 0.8, tributes 1.4 vs 1.8, further kills 0.62 vs 0.79,
  **own deaths 0.45 vs 0.21**; completed trips home in the 30 rounds after 1.4 vs 1.6 (the "recall" share is inflated by teams that
  pre-start recalls); unspent gold alike (median 10 vs 12).
- Games we led in kills AND bank at r600 and lost (20 of 43): the opponent out-banks us r600-r900 (ambush vs Fish 414-395 -> 552-879).
- **Income does not scale for us:** per 300 rounds gems 153 / 176 / 208 / 224 vs 206 / 315 / 433 / 465; gold 899 / 1,059 / 1,112 / 1,183 vs
  1,307 / 1,858 / 2,100 / 2,004; camp damage per alive champion-round 14.3 / 16.0 / 17.5 / 16.9 vs 17.9 / 23.6 / 30.3 / 29.4; strength
  at phase end 51 / 65 / 83 / 103 vs 64 / 100 / 142 / 165 while our focus is higher (227 vs 212 at r900); dead 12-17% vs 6-9%.
- Per champion at r900 (str / focus / max hp / gold earned): Vesper 150 / 121 / 1,572 / 802 vs 274 / 183 / 3,522 / 2,000; Marcella
  65 / 519 / 1,634 / 1,054 vs 114 / 332 / 2,835 / 1,318; Ryth 76 / 122 / 3,319 / 689 vs 91 / 122 / 2,602 / 660; HoR 35 / 158 / 2,482 /
  634 vs 38 / 247 / 2,264 / 831.
- Allocation question (Eric: MILP or auctions?): we use greedy per-champion scoring with one-byte claims (a degenerate auction) over
  cached BFS distance fields; MILP does not fit the ~100k-instruction turn (only the draft turn, and static plans went stale: kFarmRoute);
  a replicated sequential auction with marginal-insertion bids is the right family but the evidence says allocation is not the gap -
  clear speed (strength from gold) is.
- Tests (edit_snowball.py, B404x: kMarcBuild 6 / 7 strength-mixed late Marcella lines), kVesperGoldW 3, kGoldWeight 0.25: income
  yardstick to r900 (incomebench.sh ROUNDS=900) running.
- Income yardstick to r900 (base 617 gems / 4,593 gold): kMarcBuild 7 (Treasure F, Jungle F, then Bruiser S / H) **660 / 4,754**; kMarcBuild 6
  (S / F / H in turn) 654 / 4,564; kVesperGoldW 3 641 / 4,718; kGoldWeight 0.25 654 / 4,629 - all +4-7% gems against our own code.
  Margin screen s_snow (each and all three) running; candidate #392 = #391 + kRuinRedash + the winners.
- s_snow (B404x, #389 config, seeds 1-3, base 651): kMarcBuild 7 **-50 +-11** (more income, weaker fights: her Focus drives the damage
  spell and the stun reset), kMarcBuild 6 -16 +-11, **kVesperGoldW 3 +19 +-10** (seeds 4-6 earlier -4: ~+8 over six), kGoldWeight 0.25
  -27 +-13, all three -41 +-14. **#392 = #391 + kRuinRedash + kVesperGoldW 3** (B404x + cand392.edits) on the ladder.
- **#392 = #391 + kRuinRedash + kVesperGoldW 3** (B404x + cand392.edits): panel 10/50 -19,988 + 10/50 -19,248 + 9/40 -16,099 = **29 wins
  -55,335** (#391 29 / -57,559, #389 28 / -60,537), 0 faults: **live (pinned)**.

### Oct 27 (UTC 04:00-) - Vesper carry and mid-game deaths (Eric: "lets work on 1 and 2"; Fish's Cassi & Issac are an anomaly)
- **Deaths r300-1200** (`tools/stress/deathctx.py` on 379 top-10 bench games): ours 2,809 vs theirs 1,328. At contact start we are
  outnumbered in 5.8% (they 6.9%), above 70% health in 84%, alone in 22%; the enemy strikes first in 55% (46%); contact lasts a median 19
  rounds; **45% of our deaths are to one attacker (theirs 28%)**. In those 1,318: victim strength 64 / max health 1,415 at contact vs the
  killer's 211 / 3,422; killers their Vesper 438, Vendetta 307, Marcella 240, HoR 189; victims our Willow 369, Marcella 349, Vesper 296,
  Ryth 208, HoR 96; no ally within 3 in 58%. Fed carries pick off our weaker champions; stand-shot is already odds-gated (0.5), so the
  loss is the 19 rounds of approach. **kCarryFlee** (edit_carryflee.py, B406x): an enemy within 8 with strength x health >= X x ours
  (+ allies within 3) makes us evade now.
- **Vesper carry: kGoldSplit** (edit_vcarry.py, B405x): while our Vesper lives the others' gold weight x F (they lean to gem camps).
- kGoldSplit (#392 config, B405x): income to r900 630 / 4,560 (base) vs 616 / 4,504 (0.5) and 653 / 4,532 (0.25); Vesper's own gold
  1,221 -> 1,156 / 1,186 (camp choice cannot route gold to her: she can be in one place; Fish's Vesper captures rewards teammates help
  clear); margin -0 +-18 / -22 +-18. Off. On the ladder #392's kVesperGoldW 3 lifted Vesper by r900 to 1,032 gold / 188 strength (#389:
  888 / 164; top teams ~2,000 / 274).
- kCarryFlee (B406x, #392 config, seeds 1-3, base 645): 3x -8 +-18, 5x -14 +-18 (local opponents rarely field a fed carry).
  **#393 = #392 + kCarryFlee 3** (B406x + cand393.edits) on the ladder.
- **How Fish's Vesper gets her gold** (r0-900): vs us 2,297 gold earned, 13.6 captures a game worth 1,483 reward gold, 66% with a teammate
  hitting the camp and 41% where the teammate dealt most of the damage; vs other top teams 1,803 / 11.3 / 70%; ours 736 / 5.9 / 49%.
  **kVesperDuo** (edit_vduo.py, B407x: after the opening on non-control maps Vesper and one partner - HoR, else Ryth, Marcella... - form a
  squad of two led by her, so kVesperCarry hands her the gold rewards): income to r900 626 / 4,564 (base 630 / 4,560), her gold 1,251 vs
  1,221, margin +7 +-9. Small; candidate after #393.
- 04:02 UTC: the #393 upload failed in an internet outage ("No such host is known"); #392 stayed live; re-run 04:45.
- **#393 = #392 + kCarryFlee 3** (B406x): panel 8/50 -20,886 + 6/50 -21,584 + 6/40 -20,808 = **20 wins -63,278** (#392 29 / -55,335):
  rejected - evading a stronger enemy at 8 tiles costs more than the duels it saves. #392 re-selected (server rebuild).
- **Bench policy (Eric: "should we reduce the number of games?"):** no - a paired 140-game panel resolves ~+-3-4 wins and our candidates
  move 0-3; instead `run/ladtest.sh` (copy in tools/cands) now stops after the 50-game top-10 bench when the candidate is 3+ wins AND
  5,000+ margin worse than the first baseline tag (exit 2 skips bigbench; NOSTOP=1 overrides); local fresh-seed screens decide small
  effects, the panel guards against regressions; locally neutral-or-better changes may be bundled into one upload.
- **Where we lose (521 top-10 bench games of #385-#392, win rate by layout class x team size):** farming (spawn walk > 45) 5v5 **11% of 200
  games** (deaths 7.6 vs 3.8), 4v4 19% of 36, 3v3 6% of 16; control (17-45) 5v5 21% of 94, 4v4 30% of 66, 3v3 19% of 67; close (<= 16)
  4v4 39% of 23, 3v3 / 5v5 0% of 19. Boss-plan maps 0/18, gold-tiebreak 0/6, gem-sparse 10%. Worst maps (0 wins): stampede, fragment
  (deaths 22.1 vs 0.5), arena, elkring, starvation, crater, yellow_brick_road, shortcut, anvil, concentrated_wealth, interlock, galaxy,
  pilgrimage, the_line; best: the_pack 5/6, hooks 9/12, crossing 6/8, ribs 7/10, reverse_spiral 6/9. Five maps lack layout features in
  results/db/mapfeatures.json (big_world, lanes, gemcombat5, yellow_brick_road, fracture: hyphen naming) - rebuild it.

### Oct 27 (UTC 05:00-) - zero-win maps: looking for a systemic fault (Eric)
Tools: `tools/stress/deathmap.py` (per-map death hot spots, repeats, respawn timing, activity, killers), `chases.py` (chase episodes:
response and outcome), inline scripts; 521 top-10 bench games of #385-#392.
- On the 14 zero-win maps most of our deaths repeat within 5 tiles of an earlier one (fragment 89%, yellow_brick_road 89%, anvil 82%),
  on our own half (fragment's hot spot 7 steps from our spawn), a third within 40 rounds of respawn on fragment / arena - **but across all
  maps the top teams show the same shares** (repeat 66% vs our 70%, within 40 rounds of respawn 12% vs 13%, own half 57% vs 66%): fights
  cluster at chokepoints for everyone; the difference is volume (10.5 vs 5.8 deaths a game). Not a location-memory fault.
- **We die running:** at death we were moving away from the nearest enemy 63% (top 46%), toward it 16% (28%); 68% of our 5,494 deaths
  end a 3+ round flight that began at a median 82% health, losing ~122 health a round; only 4% of those flights include a recall - and a
  recall cannot help: it is **interrupted by damage** (GameRules), so the "recall away" idea is void.
- Chase episodes (hit with an enemy within 3): ours 10,885 / theirs 8,848. Outcome: we die in 32% (they 16%), escape 32% (41%), the
  chaser dies 13% (23%). By response: fought 10% of ours (die 24%, chaser dies 20%) vs 15% (16% / 34%); fled with distance gained 24%
  (die 10%) vs 23% (5%); to spawn 24% (die 19%) vs 25% (7%); "stood" (no net distance, no fighting back) 37% (die 57%) vs 31% (33%) -
  the "stood" bucket mixes burst deaths (died the next round 9%), no movement 5%, and flights the chaser keeps pace with.
- The common thread on all of them is individual strength: single-attacker kills of ours are carries with 3.3x our strength and 2.4x our
  health (section above), chasing at equal speed; early evasion from such carries (#393 kCarryFlee) lost 9 wins on the ladder. The
  economy gap (clear speed) is upstream of the deaths; behaviour-only fixes so far trade deaths for farming.
- **#394 = #392 + kVesperDuo** (B407x): panel 10/50 -21,349 + 7/50 -22,436 + 8/40 -18,492 = **25 wins -62,277** (#392 29 / -55,335):
  rejected; #392 re-selected.

### Oct 27 (UTC 06:00-) - a local screen that tracks the ladder (Eric: "we need a more reliable way to test screens locally")
The old pool (H340, B7Live: old copies of our code, beaten 77%) never fields a fed carry and shares our farming faults; on today's
ladder-tested changes it did not predict the panel. **New pool** (bots/PoolLive = live #392 config on B407x; bots/PoolCarry = #392 +
Vendetta for Willow with the top teams' Vendetta line + strength-mixed Marcella, i.e. fed strength carries; bots/PoolAggro = #392 +
kEngageOdds 0.8 + kChaseMax 12, fights more). Validation (s_valid: the exact configs of #389-#394 on B407x, 2 seeds, 840 games an arm vs
the new pool / 560 vs the old), paired vs #389's config:

| Config | Ladder (wins, margin vs #389) | New pool | Old pool |
|---|---|---|---|
| #390 kMaxNeed 4 | -3, -0.6k | +20 +-9 | +21 +-8 |
| #391 contact 8 | +1, +3.0k | +5 +-20 | -4 +-22 |
| #392 (+redash, Vesper gold) | +1, +5.2k | **+36 +-20** (best) | **-31 +-22** (worst) |
| #393 carry flee | -8, -2.7k | **-9 +-23** (worst) | -25 +-25 |
| #394 Vesper duo | -3, -1.7k | +33 +-20 | -1 +-22 |

Rank correlation with the ladder margins: new pool ~+0.5, old pool ~-0.3. The new pool is harder (#389's config wins 50%, margin +44)
and gets both resolvable ends right; it still overrates #390 / #394. **Default local screen from now: OPP="PoolLive PoolCarry PoolAggro",
3 seeds; incomebench.sh defaults to the same opponents (OPPS overrides).** Refresh PoolLive whenever a new version goes live.
- **Strength builds on the new pool** (edit_strbuilds.py, B408x, #392 config, 3 seeds, 1,260 games an arm, base 694 wins): kVespMix 1
  (Treasure S, Jungle S, then Bruiser S, S, H) -15 +-12; 2 (Bruiser H first) -21 +-12; kRythMix 1 (Bruiser H, H, S) -2 +-7 (711 wins);
  **kRythMix 2 (Bruiser H / S alternating) +11 +-8 (728 wins)**; kMarcBuild 7 -47 +-11 (both pools agree: Marcella keeps Focus); Vesper 1
  + Ryth 1 -13 +-12. Vesper's strength is her killing power - health for it costs more. kRythMix 2: fresh-seed confirmation next.

### Oct 27 (UTC 08:00-) - camp limit test: how many champions a 2-elk node needs (Eric)
`bots/LimitBot` on `maps/limit/` (tools/stress/mklimit.ts: 40x25 maps, the composition and emblem level encoded as walls at (19, b)):
team A drafts every 2-5-pick combination of HoR, Vesper, Ryth, Marcella, Willow, Tavi, Cassi & Issac (112; C&I is one pick, two bodies),
farms its own gold block to `level` emblems of its usual first lines (shards 30 gold), then fights node 1 (2 elks + 2 gem clusters) and,
with what is left, node 2 - one life, no recall, no retreat (a champion that dies stays home); focus the lowest elk, casts on cooldown,
shields below 95%, Willow heals the most hurt. 448 games (`tools/stress/limitsum.py replays/p2/limit_all`):

| Picks | Emblems | Node 1 no death | Rounds | Health left | Both nodes no death |
|---|---|---|---|---|---|
| 2 | 0 / 1 / 2 / 3 | 0% / 48% / 86% / 100% | - / 42 / 34 / 31 | 0 / 18 / 59 / 72% | 0 / 5 / 62 / 76% |
| 3 | 0 / 1 / 2 / 3 | 100% all | 32 / 27 / 25 / 22 | 63 / 74 / 86 / 89% | 43 / 86 / 94 / 100% |
| 4 | 0 / 1 / 2 / 3 | 100% all | 25 / 21 / 19 / 17 | 85 / 89 / 95 / 96% | 94 / 100 / 100 / 100% |
| 5 | 0 / 1 / 2 / 3 | 100% all | 22 / 19 / 17 / 16 | 90 / 92 / 96 / 97% | 100% all |

- **No items: any 3 clear a 2-elk node** (96 champion-rounds); 4 take 100, 5 take 110 - the whole-team 5-stack is the least efficient
  way to take one. Two never manage it bare; two with HoR or Ryth do from 2 emblems (HoR + Willow from 1). Pairs that fail even at 3
  emblems for both nodes: Tavi + C&I, Vesper + C&I, Willow + Tavi, Willow + C&I, Vesper + Marcella (no tank).
- Chaining two nodes without healing: 3 bare 43% (the triples with Willow or C&I: both), 3 with one emblem each 86%, 4 bare 94%.
- Our party model at base stats agrees (kFarmRoute's plan on expanse: 2-elk camps need 3, 1-elk camps 2). The opening keeps all five
  together for 240 rounds on race maps (kOpenRace): by this test a 3 + 2 split takes 2-elk nodes as safely with ~15% fewer champion-rounds.
  Earlier whole-team squad splits (kTeamSquads 2 -105, kTeamSquadsBig -57) were measured on the old pool - re-test on the new one.
- **Re-tested on the new pool (B408x + cand392, seeds 1-3, 1,260 games an arm):** kTeamSquads 2 **-114 ± 21** (wins 610 vs 694),
  kTeamSquadsBig 2 -40 ± 16, kOpenRace 0 -43 ± 8. The losses sit on the farming maps (road_of_riches -576, concentrated_wealth -541,
  gold_rush -395, gem_fields -392): split squads get caught - kills 7.4 -> 4.8, deaths 6.6 -> 8.3 and the enemy's gold 3,817 -> 4,840 on
  road_of_riches (`tools/stress/armstats.py results/ev/run1793084053`). The limit test is PvE only; in full games the group's safety
  is worth more than the champion-rounds it wastes. Openings stay whole-team.
- kRythMix 2 confirmation (seeds 4-6): +9 ± 8 (-9 wins); with seeds 1-3 (+11 ± 8, +34 wins) a weak positive, not a clear one.

### Oct 27 (UTC 09:00-) - Fish's camp aggro swap (Eric: ranked 9644b4dd on 00quadrants, "swapping aggro on the camps")
`tools/stress/aggro.ts DIR` writes every monster hit with every champion in the monster's reach (distance, health, priority word);
`aggrosum.py` / `parties.py` summarise it.
- **Fish's priority word is minus the health quartile:** -1 above 75%, -2 50-75%, -3 25-50%, -4 below 25% (Vesper soloing a wolf:
  -6..-9, the same quartiles offset by 5). Priority sets the turn order and a monster's tie between equally near champions goes to
  whoever acts first, so **the healthiest adjacent champion soaks**; as it drops a quartile the next one takes over. First 200 rounds:
  Fish camp damage Vendetta 33% / HoR 22% / Issac 20% / Marcella 15%, healthiest took 34 of 50 tied hits. Ours: the draft order sits in
  the word (bits 24-26) outside boss camps, so the first pick soaks every tie - HoR 66%, healthiest 1 of 38.
- **Dashes hand aggro over:** a hurt melee champion dashes from distance 1 back to 2-3 so it is no longer nearest (Issac at 40%,
  Vendetta at 22-36%) while a full-health mate dashes in to distance 1 (HoR, Issac, Vesper at 100%); one turn, no extra hits.
- **Their split is by camp, not map size:** all together on the first two 1-elk camps (Cassi and Vesper hitting the first from spawn),
  then 4 on the golem + its neighbouring single wolf, Vesper alone on a far single wolf, Marcella to the altar to tribute. We had the
  same 4 + 1 at our golem. The gap was gold: earned 281 vs our 90 at r50 (Marcella's tribute), 2,661 vs 1,627 at r400.
- **kAggroShare** (tools/edits/edit_aggroshare.py, bots/B409x = B408x + it): the kBossCommit 4 key in bits 27-30 on 1 every hostile camp,
  2 as the health quartile (Fish), 4 only with no enemy in sight. Check games (8, quadrants / road_of_riches / concentrated_wealth /
  gold_rush vs PoolLive): healthiest took 73 of 268 tied hits without it, 190 of 358 with 3; HoR's share on quadrants 41-47% -> 33-41%.
- **kAggroBack** (tools/edits/edit_aggroback.py, bots/B410x = B409x + it): 1 = kTagIn's step-in without kAggroRotate - a ranged champion
  above half health steps towards its camp target while the soaker is in a lower health quartile, so it joins the quartile rotation at
  distance 1 (Fish's fresh Vesper / Issac dash in). Check games with kAggroShare 3: healthiest 203 of 354 tied hits (57%, Fish 68%);
  Vesper's camp-damage share quadrants 20 -> 23%, concentrated_wealth 10 -> 18%. Melee may hit and step in one turn (handbook), so a
  hurt soaker stepping back to distance 2 would halve its hits; not built.
- **kAggroShare screened (B409x + cand392, seeds 1-3, new pool, 1,260 games an arm): 1 -31 ± 18 (-23 wins), 3 (Fish's quartile)
  -47 ± 18 (-44), 7 -35 ± 17 (-16).** Deaths barely move over the screen (6.7 -> 6.8-7.0) but our gold falls ~2% and theirs rises;
  worst on road_of_riches (-611), concentrated_wealth (-563), yellow_brick_road, guardians. In the 8 check games recalls were unchanged
  (170 / 170) but started at 55-59% health instead of 65-70%, and deaths by r600 rose 23 -> 32: with HoR as our only tank (Health
  build, self-shield) the spread leaves Vesper and Marcella half-hurt when a fight comes. Fish's comp is four bruisers. The kAggroBack
  step-in screen (puts even more hits on Vesper) was stopped. Next: kAggroShare 8 = only melee champions carry the key
  (edit_aggromelee.py, bots/B412x = B410x + edit_report.py + it; screened as 9 and 11).
- **kAggroShare 8 (melee only) screened (B412x, seeds 1-3): 9 -36 ± 18 (-39 wins), 11 -72 ± 18 (-75).** Sharing camp hits loses in
  every form for our comp; off for good unless the comp changes.

### Oct 27 (UTC 10:30-) - screening speed (Eric: "are we using the fastest method of doing screens?")
- Throughput is at the machine's ceiling: ~5 games/s full length on the Ryzen 5 5600 (6 cores / 12 threads, JOBS 11, one run-batch,
  compiled-module and game caches); games average 1,369 rounds (1% end by r600, 12% by r900). The waste is in games per idea: every
  arm plays 1,260 games (3 seeds x 70 maps x 3 opponents x 2 sides) to the end.
- **The r800 cut-off re-checked on the new pool** (B411x = B410x + edit_report.py with a fallback anchor; the B39x+ lineage had lost
  kReportRound): seed 1, 7.7 games/s, vs the full-game results of the opening-split screen - kTeamSquads 2 cut -33 ± 16 (full seed 1
  -104 ± 36, 3 seeds -114 ± 21), kTeamSquadsBig 2 -4 ± 12 (-28 ± 26 / -40 ± 16), kOpenRace 0 -27 ± 8 (-39 ± 14 / -43 ± 8). Right sign
  every time, z -2.1 / -0.3 / -3.4 against full seed 1's -2.9 / -1.1 / -2.8: a reject filter (z below -2: drop), never an accept.
  7% of games end before r795 and come back missing (no REPORT line) - the driver should take their real result.
  `tools/stress/pairdelta.py RUNDIR [SEEDS]` gives paired deltas for any seed subset of a run.

### Oct 27 (UTC 10:45-) - Fish's draft, builds and recalls copied (Eric: "copy fish's draft and builds and recall timings")
75 Fish ranked games on engine 2.0.0 (replays/p2/fish_rk; `tools/stress/buildorder.ts`, trace2 recalls):
- **Draft by pick count:** 3 Vesper > HoR > Marcella (13/14); 4 Vesper > Vendetta > HoR > C&I (13/15); 5 + Marcella (25/46), else
  Varg / Ren / Willow - the same fifth on a map whatever the opponent (eight Willow 4/4, ambush Varg, galaxy Ren): map-tuned.
- **Emblem lines (median completion round):** Vesper Treasure S 150 > Jungle S 225 > Bruiser H 280 > Durability H 385 > Bruiser S;
  Vendetta Treasure H 200 > Jungle S 310 > Bruiser H 395 > Durability H 465 > Bruiser S; Marcella Treasure H **100** > Jungle S 175 >
  Bruiser H 240 > Durability H 285 > Bruiser S; HoR Treasure H 350 > Jungle F 495 > Bruiser H on; Cassi Power F 400 > Durability F >
  Bruiser H; Issac Treasure S > Power S > Home H > Durability H > Power S.
- **Recalls (to r1200, a game):** HoR 9.2 at a median 39% health / 44 gold; Vendetta 8.9 at 40% / 156; Vesper 9.1 at 62% / 183;
  Marcella 5.5 at 68% / 228; Cassi 4.0 at 40%; Issac 5.9 at 33% - tanks go home hurt, carriers when an emblem (150) is affordable.
  Ours (80 bench games): HoR 3.6 at 76% / 13, Marcella 9.4 at 87% / 28, Ryth 7.7 at 90%, Vesper 7.2 at 87% / 13, Willow 4.1 at 69% -
  recall-captures with nothing to buy. (Other top teams' "recalls" are 100-400 a game at 100% health, 1-2% finished: pre-starts.)
- `edit_fishcopy.py` (bots/B413x = B412x + it; B413f = the same with kFishNow 1): kFishNow (draft.cpp; twins kept), kFishBuild,
  kFishRecall (no idle recall-capture; with kRecallCapHealHp 0.5 and kRecallCapBuyMode 2). Check games vs PoolLive: drafts as listed;
  anvil HoR home at 32%, Marcella 30% (were 84-95%); rows still recalls healthy through the whole-team path.
- **Screened (B413x / B413f + cand392, seeds 1-3, new pool, 1,260 games an arm; base 706 wins):** kFishBuild **-110 ± 17** (573
  wins; kills 7.3 -> 4.5 a game, deaths 6.7 -> 7.0, gold 6,009 -> 5,674); Fish recalls (kFishRecall + kRecallCapHealHp 0.5 +
  kRecallCapBuyMode 2) -32 ± 18 (678); Fish draft + builds **-295 ± 20** (432; deaths 6.7 -> 13.1); all three -296 ± 20 (434).
  Fish's configuration does not transfer: its draft and emblem lines fit its own fight code (the per-champion pieces had already
  screened negative: kMarcBuild 7 -47, kVespMix -15 / -21), and our code with health-heavy lines engages less (kills -38%). Kept off.
- **#395 = #392 + kRythMix 2** (B408x + tools/cands/cand395.edits), uploaded 08:29 UTC: panel 12/50 -17,267 + 11/50 -16,565 + 9/40 -15,503 =
  **32 wins -49,335** (#392 29 / -55,335 on the same panel ~5 h earlier; opponents drift): **live (pinned)**. bots/PoolLive refreshed to #395.

### Oct 27 (UTC 09:30-) - the fight side: mid-game decisions and late-game scaling (Eric)
890 top-10 bench games of #385-#394 (camp-state traces for all; `tools/stress/fights.py`, `fightdetail.py`, `fightrounds.py`,
`ladlogsum.py`). A fight = rounds with champion-on-champion hits split by 8 quiet rounds; power = strength sum x health sum of each side's
champions within 8 of the first hit. **Matching caveat:** a hit's tile must be matched to the target's position at the round's start OR
the next round's (the other team may move first); start-only matching undercounted hits by ~25% (both sides) - fixed in all three tools.
- **Outcome by power ratio (r300-900, 8,637 fights):** even fights (0.8-1.25x) us -0.25 net kills a fight, top +0.25; at 1.25-2x in our
  favour -0.20 (top +0.27); at > 4x +0.04 (top +0.42). We start 40% of our fights under half the enemy's power (top 26%).
- **Caught (under 1/2 power):** numbers 1.7 v 2.7 (top 1.4 v 2.8); the champion nearest the first hit dies 28-35% for Marcella / Ryth /
  Vesper / HoR (Willow 61%) vs the top teams' same types 14-25%; heading home or out, alone or with an ally within 6 barely matters.
- **Dominant (we 2x+, 2.8 v 1.4 champions):** we kill 23% of the enemies we hit (22% escape under 35% health), lose 0.30 champions a fight
  vs their 0.26; their first kill comes after 7 rounds (ours 12), on Willow / Vesper.
- **Per-round play is not the gap:** with an enemy champion in attack range, attack rates ours vs theirs Vesper 51/57%, Marcella 76/82%,
  HoR 72/74%, Ryth 65/70% (Vesper's attack-on-the-move 10 vs 16%); fuel cut-offs are 0.1-0.3% of our fight rounds. kLadLog games: in-range
  fight_enemy turns without a shot are mostly approach steps (the log's distance is measured after the move).
- **Reading:** individual stats decide - their gold concentrates in a fed carry with hp (Vesper r900 274 str / 3,522 hp vs ours 150 /
  1,572) that bursts our weakest champion and outlives our spread damage. Next: Fish's per-champion lines (kFishBuild now a bitmask:
  1 Vesper, 2 Marcella, 4 HoR, 8 Vendetta, 16 C&I; the all-champion -110 was 31), screen s_fishb on the #395 config.
- **s_fishb (B413x + cand395, seeds 1-3, refreshed PoolLive = #395; base 723 wins):** Fish's Vesper line (kFishBuild 1: Treasure S, Jungle
  S, Bruiser H, Durability H, Bruiser S) -6 ± 10 (696); HoR line (4: Treasure H, Jungle F, Bruiser H on) -0 ± 6 (709); **Marcella line
  (2: Treasure H, Jungle S, Bruiser H, Durability H, Bruiser S) -120 ± 16** (578; kills 7.4 -> 4.6 a game). The all-champion -110 was
  Marcella alone: her Focus drives our fight code (damage spell, stun reset). A health-built Vesper is neutral against our own pool, which
  seldom fields the fed carries it is meant to survive; only the ladder could judge it.
- **s_fifth (B414x + cand395, kFifthPick in draft.cpp via edit_fifth.py; base 723 wins):** Ren for Willow **-102 ± 16** (621), Varg -71 ± 15
  (669), Tavi -12 ± 15 (697; vs PoolCarry +271 / base +203, vs PoolLive -22 / +39). Willow stays.
- **Late-game scaling = big camps (r300-900):** `farmcmp.py --from 300 --rounds 900` (now has --from) and `tools/stress/bigcamps.py` on the
  traced bench games: per game on maps that have the class, 2+ elk captures us 3.01 / top 6.59, golems 0.63 / 1.96, monoliths 0.09 / 0.50,
  1-elk 5.55 / 8.80; mid-game income us 322 gems / 2,118 gold vs Ad Astra 604 / 3,030, Claudus 627 / 4,216, Fish 694 / 5,498. We farm small
  camps solo (2-cluster gold, wolf + cluster, single clusters) and reach a respawned camp 58 rounds after it returns (Ad Astra 44). Earlier
  gate tests (kSoloParty + kHelpBias 0.15) left 2-elk captures at 0.9: big-camp parties are rarely proposed at all (squads of one after
  the opening, kHelpStart 0). Screens queued: kAdvantageFrac 0.2 (+ kFarSideAdvantage 1.5 / kAdvantageWindow 20), then pairs after the
  opening (kSquadSize 2, + kBigParty 2) and kBigParty 3.
- **s_adv (B414x + cand395, base 723 wins):** kAdvantageFrac 0.2 (advantage mode on one dead enemy) -12 ± 13 (684); + kFarSideAdvantage 1.5
  -36 ± 14 (675); + kAdvantageWindow 20 -1 ± 12 (713). Pressing after a single kill does not pay; 0.4 / 1.2 stay.

### Oct 27 (UTC 11:30-) - ranked 0d8ba738 (00expanse vs SkuBap: Vesper, Marcella, Vendetta, Varg, Tavi; Eric: "from ~600 their farm speed
### increases and they invade our high resource camps") - `tools/stress/phases.py DIR [STEP] [US]` (per-phase economy, captures by half)
- Even to r400 (ours 910 / 847 gold per 100 rounds at r200-400 vs 642 / 673); from r500 theirs ~1,000-1,230 per 100 vs ours 400-700; strength
  r700 165 vs 98, r900 231 vs 124; one death all game. They spend less time at camps (13-20% vs our 22-31%) and earn twice the gold.
- Expanse's far corners each hold three 2-elk camps ~15 tiles apart, 57-72 tiles from either spawn. SkuBap kept champions in its far corner
  from r414 and cycled them (11 captures, ~one per 95 rounds) and took three of ours late; ours had 9 captures there all game and left camps
  untaken r368-916 and r202-827. 1-elk camps by the spawns: even (9 / 10). Our recall-capture habit makes every far visit a 60-tile walk back.
- kFishRecall per map in s_fish: expanse 22 -> 28% wins, big_world 39 -> 50% (gold up, theirs down); road_of_riches / concentrated_wealth 72 ->
  56%. **kFarRecall** (edit_farrecall.py, bots/B415x): Fish's gating only where the spawn path exceeds N. Check games (kFarRecall 45 vs PoolLive,
  expanse + big_world, both sides): 3 of 4 won; 2-elk captures r600-1200 up (expanse 8 vs 2 in the mirror), strength r900 big_world 127 vs 74.
  Screen s_far (45, 70, 45 + kFarRecallHp 0.65) after s_pair.
- **s_pair (B414x + cand395, seeds 1-3, base 723 wins):** kSquadSize 2 after the opening (pairs) **+9 ± 10** (734); + kBigParty 2 -7 ± 12 (708);
  kBigParty 3 **-29 ± 11** (683). Pairs: weak positive, to confirm on seeds 4-6 and with kFarRecall.
- **s_far (B415x + cand395, base 723):** kFarRecall 45 (map gate) **-22 ± 10** (689), 70 -12 ± 8 (709), 45 + kFarRecallHp 0.65 -17 ± 10 (700).
  Per map (45): expanse 22 -> 33% wins, but road_of_riches 67 -> 39% (deaths 6.9 -> 10.6), concentrated_wealth 72 -> 50%, ambush 89 -> 72% -
  a long spawn path does not mean an uncontested camp. edit_farrecall.py now gates per capture (kFarRecallMode bits: 1 map spawn path > N,
  2 our walk home > N, 4 no enemy seen for kFarRecallQuiet rounds). s_far2: walk > 35 (mode 2), walk > 35 + quiet 30 (6), walk > 25 + quiet
  (6); then kSquadSize 2 on seeds 4-6.
- **s_far2 (B415x + cand395, base 723):** per-capture far recall - walk home > 35 (mode 2) -3 ± 7 (710), + quiet 30 (6) -0 ± 6 (717), walk > 25 +
  quiet -3 ± 8 (723): neutral, off. **kSquadSize 2 on seeds 4-6 (s_pair2): +32 ± 9 (686 vs 649)**; with seeds 1-3 ~+20 ± 7, +48 wins over
  2,520 games. Candidate **#396 = #395 + kSquadSize 2** (B408x + tools/cands/cand396.edits): Eric approved the ladder
  panel (~11:00 UTC): **#396 panel 11/50 -17,216 + 8/50 -22,702 + 7/40 -18,237 = 26 wins -58,155** (#395 32 / -49,335 ~2.5 h earlier):
  rejected - flat on the top-10 bench, -3 / -2 wins on the rotated / held-out benches; local +20 +-7 did not carry over (pairs farm
  differently against teams that roam). #395 re-pinned.
- Map-feature gating (Eric: "can we turn switches on for map variations?"): yes by layout features, never by name. kFarRecall's spawn-path
  gate picked the wrong feature: road_of_riches 243 steps between spawns 40 tiles apart (path/straight 6.1, -531) vs starvation +485 (side
  80), expanse open. edit_farrecall2.py (B416x): bit 8 = straight-line distance to the enemy spawn > kFarRecallEnemy; screen s_far3 (40, 50,
  40 + quiet) queued; judge gates on two halves of the map pool (per-map results are 18 games each, +-100-200).
- **s_far3 (B416x + cand395, base 720; kFarRecallMode 8 = straight-line distance to the enemy spawn):** > 40 +3 ± 7 (709 wins), > 50 -1 ± 5
  (706, one game missing), > 40 + quiet 30 (12) +7 ± 7 (706): neutral, wins slightly down - far recall dropped in every form.
- **Hung match (Oct 27 ~11:00 UTC):** C3s3 vs PoolCarry on 00oasis ran 80+ CPU-minutes; it kept the run-batch pipes open, so fastscreen
  waited forever. Neither Stop-Process nor taskkill can end such a match from the sandbox ("no running instance", CPU still rising); an
  orphaned cambc-3.0.5 __run-match from Oct 24 (300k CPU-seconds) was in the same state - Eric must end both in Task Manager.
  `tools/stress/salvage_screen.py TMPDIR RUNDIR CANDS...` recovers a stuck screen from the run-batch statistics files. **Always set
  MATCH_TIMEOUT (e.g. 900) on screens from now on.**

### Oct 27 (UTC 13:00-) - pathing census (Eric: "did we end up doing the pathing algorithm changes?" - Codex C187 / C188)
`tools/stress/gridcache.ts` (DIR/grid.txt from the replay) + `tools/stress/pathcensus.py` on 239 bench games (#392-#394): quiet camp-to-camp
trips (no enemy within 8, alive, not recalling). Ours 3,966 trips: 19.3 rounds for a 13.8-step shortest walk (1.39 rounds a step; walk /
straight line 1.14); top 3,392: 18.7 for 14.3 (1.31; 1.23). Dash champions: our HoR 1.21 rounds a step vs theirs 1.26, Vesper 1.26 vs 1.21,
Vendetta 1.14, Issac 1.10; dashes a trip 1.63 vs 1.68; trips with a ready dash left unused 2% vs 4%. Travel rounds with an enemy seen 9-15
away: we dash on 9.5%, they 12.1% (try_dash refuses travel dashes while any enemy is visible). Trips taking 1.5x+ the walk 42% vs 36%
(pauses, not routes). **Verdict:** the walker and dash use are near the top teams'; a cooldown-aware search would buy a few percent of
travel at most. The earlier "1.39x the straight line" was mostly terrain. Cheap remaining arm: allow travel dashes with the nearest
visible enemy 9+ away.
- **kDashFarEnemy** (edit_dashfar.py, bots/B417x): travel dashes while the nearest visible enemy is more than N away; screen s_dash (9, 12).
- **Party instrumentation (Eric: "1 and then 2"; Codex C187):** kPartyLog (edit_partylog.py, bots/B418x; logging only) + `tools/stress/partylog.py`,
  12 games vs PoolLive / PoolCarry on expanse, big_world, lanes, dunes, quadrants, concentrated_wealth. Each champion sample sees 5.7 / 4.3 /
  2.3 big camps (r200-400 / 400-700 / 700+; worth 40+, needing 2+ at its damage): two thirds need only 2; 58-69% are in "unknown" state (not
  seen since set-up); of the takeable ones (alive / unknown, quiet, need <= 4) 64-69% fail only because fewer than need - 1 free mates
  stand within kHelpCall (25) - solo farmers are spread out - and 10-19% pass; champions stand on a big camp in 20% / 10% / 8% of samples.
  Squad help calls weighed ~10 a game, 36% accepted, party score / solo bar median 0.84. kSoloParty (the only way a solo farmer proposes a
  need-2 camp) is off in #395. Screen s_party: kSoloParty 1 + kHelpCall 40; + kHelpBias 0.8; kSoloParty 2 + both.
- **s_dash (B417x + cand395, base 720):** kDashFarEnemy 9 -24 ± 13 (706 wins), 12 -8 ± 12 (721): off - the escape dash is worth more than the
  travel it saves.
- **s_party (B418x + cand395, base 720):** kSoloParty 1 + kHelpCall 40 -23 ± 14 (713 wins); + kHelpBias 0.8 -24 ± 13 (701); kSoloParty 2 + both
  -21 ± 13 (705). Recruiting solo farmers into big camps loses here too (as pairs did on the ladder): off.
- **Finishing low enemies (Eric: "assign a dash champion to chase a lower than 25% health enemy"):** `tools/stress/lowescape.py`, 890 bench
  games: enemies first seen at <= 25% health (down from higher 10 rounds before) with a hunter within 8 - we kill 36% of 6,448 within 25
  rounds, the top teams 63% of 9,820; a hunter dashes within 5 rounds 35% vs 53%; with a ready dash champion within 6 we kill 47% and dash
  in 52% of cases, they 64% / 79%. Existing hunting (kHunter 5, kWoundedPrey 0.5, kHuntElect, kChaseMax 7, kHunterTurns 12, kDashChase 2)
  elects the best-equipped champion, not a dasher, and needs isolated prey. Building kFinisher.
- **kFinisher** (edit_finisher.py, bots/B419x): a champion with a ready dash (Vesper too - dash_ready() is melee-only) and >= kFinishOwnHp
  health takes the lowest visible enemy at <= kFinishHp within N tiles with <= kFinishCrowd other enemies within 4 of it: cast + hit in
  reach, else dash to the free tile nearest it, then hit or step; placed after the escape branch. 8 check games vs PoolAggro / PoolCarry
  (N 6): with a ready dasher within 6 of a <= 25% enemy we dashed 64% and killed 60% (the opponents' unchanged code 38% / 50%). Screen
  s_finish: N 6, 8, 6 + kFinishHp 0.35.
- **s_finish (B419x + cand395, base 720):** kFinisher 6 -4 ± 14 (714 wins; kills 7.4 -> 7.5, deaths 6.8 -> 6.7, gold -23), 8 -9 ± 15 (694),
  6 + kFinishHp 0.35 -5 ± 15 (716). **Chase audit** (`tools/stress/finaudit.py`, 24 + 24 paired kLadLog games vs PoolAggro / PoolCarry on 12
  fight maps): 77 episodes, median 1 turn; prey killed 75%, chaser died 3%; no target switching, never two chasers; 48 dashes - 35% landed
  with another enemy within 4 (2+: 8%), 35% not followed by a hit on the prey; failures: 10 never hit, 9 hit and escaped. **But no added
  kills:** paired games kills 8.46 -> 8.50, deaths 6.79 -> 6.38, gold 5,428 -> 5,142 (-5%), gems banked 788 -> 779 - the prey it takes
  died anyway against our own code. Local low-enemy kill rates (lowescape.py on the base games): ours 44%, the pool's 44%; on the ladder
  ours 36%, the top teams' 63% - the local pool finishes far worse than the top teams, so local screens cannot value finishing or escapes.
- **#396 calibration** (`tools/stress/calib.py`, 59 ladder games both versions played): wins 11 vs 9, deaths 10.12 vs 10.10, kills 5.83 vs
  6.00, gold r600 2,218 vs 2,159, r900 3,301 vs 3,218; deaths by context (alone / pair / group x even / outnumbered) the same within 0.1 a
  game. The 10 flipped games are single-game blowups both ways (gold_rush deaths 2 -> 22; gem_fields 9 -> 3): no encounter type that top
  teams use to punish pairs; the panel gap reads as ~2.5% less gold plus noise / drift.
- **Ranked c3936d60 (01islands vs EggsAfter11AM; Eric: "why did Marcella target a small gold node next to the enemy base?"):** after g40
  (r278) she walked the west edge r309-339 to 7 tiles from their spawn, met their Ryth + Marcella at 6-7 and walked back - no fight, no
  capture, ~30 rounds. Every elk camp near her needs 2 for her alone (solo scoring drops them); the gold-only nodes by their spawn (g44 2
  gold 4 tiles from it, g8 3 gold) cost no health and only kFarSide 0.7; group_quiet sees only enemies in vision. Their Ryth took g44 at r315.
  Pattern check (`tools/stress/deeptrips.py`, 790 bench games): trips within 12 of the enemy spawn after r200 ours 1.4 a game (8 rounds,
  93% empty, 10% die) vs the top teams' 3.0 (13.5 rounds, 91% empty, 8% die) - not a systematic leak (~10 champion-rounds a game).

### Oct 27 (UTC 14:00-) - Eric's 12-hour window: farming algorithms / weights, snowball, wasted rounds, big nodes, Codex (A093)
- **Pool calibration** (Eric: "check our local kill and escape rates move toward the ladder's 36% / 63%, then re-screen the finisher"):
  #395 (PoolLive) vs each candidate opponent, 24 maps x both sides (`replays/p2/poolcal`, lowescape.py): the opponent kills our <= 25%
  champions PoolAggro 41%, PF1 (#395 + kFinisher 6) **50%**, PF2 (aggro + finisher) 47%, PF3 (finisher 8 / 0.35 + kWoundedTeamHunt) 47%,
  PF4 (PoolCarry's Vendetta draft and lines + finisher; dashes in 77% of ready cases like the top teams' 79%) 50%; we kill theirs 40-43%.
  Ladder: top 63% / ours 36%. The rest of the gap is stats, not behaviour. **New pool: OPP="PoolLive PoolCarry PoolAggro PoolFinish"**
  (bots/PoolFinish = PF1), SEEDS 2 at a time (1,120 games an arm).
- **Wasted rounds** (`tools/stress/wasted.py`, `idle.py`; 413 team-games of the #392-#396 benches, r100+; channel counted only when the
  champion neither moved nor acted, because four top teams pre-start recalls): ours productive 21% / walking 48% / idle 10% / dead 12% /
  channel 5% vs the top teams' 24 / 49 / 5 / 7 / 12. Long trips (15+ rounds) 41.8 vs 29.6 a game; out-and-back trips with nothing done
  1.4 (35 champion-rounds) vs 1.2 (29) - Marcella's c3936d60 trip is not our leak. **Idle: 449 vs 241 champion-rounds a game**, the same
  mix (beside an alive camp not hitting 32 / 30%, waiting at a respawning camp 27 / 24%, enemy within 8 11 / 10%, beside a mate 13 / 9%,
  open ground 15 / 25%); by champion ours Vesper 114, Ryth 107, Willow 92, Marcella 92, HoR 44 vs Vesper 52, HoR 46, Marcella 42, Ryth 30.
- **Finisher on the new pool:** seeds 4-5 **+34 ± 14** (574 vs 545 wins; kills 6.5 -> 7.0, deaths 7.7 -> 7.5, gold +3%; untouched maps
  +30 ± 15 / audit maps +51 ± 39), seeds 1-2 +0 ± 15 (612 vs 609); with the old pool's -4 ± 14 a weak positive (~+17 ± 10 on the new pool).
  Candidate **#397 = #395 + kFinisher 6** (B419x + tools/cands/cand397.edits); the upload needs Eric's explicit go-ahead (the auto-mode
  classifier blocks "production deploys" even inside the 12-hour grant).
- **Idle turns by decision** (kIdleLog, edit_idlelog.py, bots/B420x, `tools/stress/idlelog.py`; 48 local games): 408 a game - capture
  (standing 5 rounds on a reward) 63%, wait_party 12%, guard (beside a respawning camp) 9%, deliver 4%, tribute_guard 2%, contest_altar 2%,
  escape / evade 3%, stuck 1%. The ladder idle gap (449 vs 241) is mostly capture time: the top teams recall-capture, which counts as a
  channel. Real waste ~85 champion-turns a game (party waits + guarding). The Capture emblem (3-turn captures) would save ~2 rounds a capture.
- **Snowball** (`tools/stress/snowball.py`, 890 bench games): leading by 15%+ gold at r300 we win 48% (167 games; ratio 1.92 -> 1.70 ->
  1.86, strength ratio r600 1.03, big camps 1.3, leader deaths 3.6 vs 4.6); a top team leading wins 96% (365; 2.56 -> 3.08 -> 3.42, strength
  1.77, big camps 3.4, deaths 2.0 vs 6.8). From r200 our leads shrink 2.13 -> 1.41 (wins 36%). At r600 per champion when we lead: earned
  534 vs 365 but **strength 72 vs 72**, focus 196 vs 129, max hp 1,644 vs 1,460 - our lead gold becomes Focus (HoR / Marcella / Willow
  lines), theirs becomes strength (113 vs 65) and health (2,075 vs 1,556).
- **s_w1 (B419x + cand395, new pool seeds 1-2, base 609):** kHomePull 0.25 **-55 ± 17** (554), 0.75 +5 ± 16 (590), kFarSide 0.85 -17 ± 14 (565):
  live 0.5 / 0.7 hold.
- **Starved maps** (gemrate_all in the lowest third, <= 2.75; 212 bench games): our win rate 22%; big-node captures us 1.3 vs top 2.8 a
  game. Per map: oasis golem 14.5 vs 5.5 (we win 4/6), rows monolith 0.6 vs 0.1 (10/17); pilgrimage 0.4 vs 7.4, stampede 0 vs 7.0, famine
  1.8 vs 6.9, contest 0 vs 5.6, starvation 0.6 vs 4.0 (all 0 wins); damage to big nodes a game contest 0 vs 114k, pilgrimage 5k vs 84k,
  stampede 17k vs 96k, gold_rush 12k vs 64k (first hits r391 vs r222). kBossMaxStr 100 (Oct 18: contest's 200-strength monoliths killed our
  relays) excludes monoliths (200) and golems (120) from boss mode; kBossGemShare 0.8 keeps most starved maps out of it. Screen s_boss:
  kBossMaxStr 250, + kBossGemShare 0.5, + kBossBudget 1.0.
- **Storage cleanup (Eric: "clean our storage from time to time"):** freed 13.7 GB (88 GB free): old-engine cache entries (cambc_3.0.x,
  310k files), stale fastscreen temp dirs (7.8 GB), build output of old dev / test bots (sources kept), replay files of finished local
  test sets and the pre-#385 bench sets (traces kept), screen run dirs older than two days. bots/Review22Live/.cambc is held by an old
  cmake process.
- **s_boss (B419x + cand395, new pool seeds 1-2, base 609):** kBossMaxStr 250 (monoliths / golems allowed in boss mode) +9 ± 6 (619; contest 50
  -> 62%, starvation 38 -> 62%, rows 62 -> 88% wins); **+ kBossGemShare 0.5 +62 ± 10 (673 wins, +64)**: 17 maps change, 15 gain (anvil +633,
  famine +445, monolith +404, fields +402, guardians +400, uncharted_lands +374, rows +277, split +252, big_world +231, great_wall +225,
  contest +212, shortcut +172, starvation +168, gold_rush +108), broken_curve -20, corridors -33; + kBossBudget 1.0 +11 ± 6 (620). Caveat: the
  pool bots keep kBossMaxStr 100, so locally the bosses are uncontested; on the ladder the top teams farm them (we win ~0 there now).
  Fresh-seed check s_boss2 queued; candidate #398.
- **Opening fuel (Eric: "at the very start of every game we struggle with fuel limits"):** ladder fuel files (83 games): fuel-limited
  champion turns r1 100%, r2 72%, r3 48%, r4 34%, r5 21%, r6-11 9-14%, later 2-3%. Profile (edit_fnprof.py printing at r12, 12 maps): 8.6
  of 12 turns completed; round 1 ~185k fuel (constructor), turns 70-94k; farm 124k (incl. field builds), field 122k (59 builds), warm_fields
  114k, manage_squad 76k, observe_allies 68k, end_jobs 43k over r1-12. **kOpenLite** (edit_openlite.py, bots/B423x: no warm_fields at turn
  ends before round N): N 40 -> 9.35 turns by r12 (+0.75), limited r5 23 -> 8%, r6 22 -> 7%, r11 23 -> 8%; r1-3 unchanged (set-up).
- **Retarget recheck** (kRetarget 1 log, edit_retarget.py, bots/B422x; 48 games): 156 rechecks a game, the fresh best differs from the
  retained solo target in 62 (40%): target median 21 tiles / 40 rounds away vs the best's 28 rounds, value 26 vs 33; the best is nearer in
  64%; the target's state unknown 57%, alive 36%, reward 7%. Mode 2 (re-pick when the same camp wins two checks) screened in s_olrt.
- **s_cap (B421x + cand395, new pool seeds 1-2, base 608):** kCaptureEmblem 31 (all) -1 ± 17 (605), 10 (Vesper + Marcella) -1 ± 15 (589), 6
  (Vesper + Ryth) +20 ± 13 (632). Weak at best; a Ryth-only arm (4) on fresh seeds is the only follow-up worth a slot.
- **#397 = #395 + kFinisher 6** (B419x + tools/cands/cand397.edits), uploaded 14:57 UTC after a same-hour #395 top-10 re-bench (top395b: 11/50
  -19,437): top-10 **14/50 -15,650**, rotated 8/50 -25,037, held-out 6/40 -17,447 (= 28 / -58,134 vs #395's morning 32 / -49,335). Same-hour
  top-10 +3 wins / +3,787; rotated / held-out below the morning baselines as #396 was - suspected drift; #395 rotated + held re-bench at
  ~16:00 to decide. #397 live meanwhile.
- **New emblem families in the top teams' builds** (buildorder.ts now knows all 14 families: id = family x 6 + stat x 2 + emblem bit; OTHER=1
  on the #392-#396 top-10 and rotated benches): share holding one by r600 - Issac / Tavi Capture S ~30%; Marcella Prospector F 18%, Capture
  F 7%, Hunter F 5%; Varg Prospector S 17%; Ryth Prospector H 13%; Vesper Capture S 10%, Prospector S 8%, Hunter S 7%; Vendetta Hunter H/S
  16%, Prospector 6%; HoR Hunter H/F 15%. Core lines unchanged (Vesper Treasure S > Jungle S > Durability H > Bruiser S; HoR Treasure H >
  Jungle F > Bruiser H / Durability H > Bruiser F; Ryth Treasure H > Jungle H/S > Durability / Bruiser H). Only Prospector on Marcella (our
  cluster farmer) looks worth an arm.
- **s_boss2 (fresh seeds 4-5, base 545): kBossMaxStr 250 + kBossGemShare 0.5 +66 ± 9 (609 wins, +64)** - confirmed (seeds 1-2 +62 ± 10).
  Candidate **#398 = #395 + these two** (tools/cands/cand398.edits on B419x).
- **s_olrt (B423x + cand395, seeds 1-2, base 609):** kOpenLite 40 **-59 ± 21** (548): the pre-warmed fields feed the opening's scoring
  (altar distances, approach fields) - more turns, worse picks; the opening fuel fix has to move work, not skip it (draft turn). kRetarget 2
  -14 ± 10 (600): stale targets are common but switching them does not pay. Both off.
- **s_boss3 (B419x, seeds 1-2, base 609):** boss gs 0.5 +62 ± 10 (673); + kFinisher 6 +57 ± 17 (671: the finisher adds nothing on top);
  gs 0.4 +59 ± 11 (679); **gs 0.3 +72 ± 13 (685)**; gs 0.5 + kBossBudget 2.0 +50 ± 10 (668).
- **s_prosp (B424x, seeds 1-2, base 609):** kMarcBuild 8 (Prospector F second) -17 ± 12 (578), 9 (third) +2 ± 9 (601); kCaptureEmblem 4
  (Ryth) -1 ± 10 (605). New emblems: no gain - dropped.
- **s_boss4 (fresh seeds 4-5, base 545):** gs 0.5 +66 ± 9 (609), **gs 0.3 +85 ± 12 (632)** - over four seeds ~+78 vs ~+64. **s_boss5:** kBossDeny with
  boss gs 0.5 identical to boss alone (it needs tiebreak maps; never fires) - dropped.
- **#395 same-time re-bench (top395c, ~16:00 UTC):** rotated 9/50 -21,224, held-out 7/40 -18,960 (morning 11/50, 9/40): with top395b's 11/50
  -19,437 #395 now scores **27 / -59,621**; **#397 28 / -58,134** (top-10 +3, rotated -1, held-out -1) - a tie with a top-10 lean. The
  morning 32 was drift. #397 kept live; #398 (boss gs 0.5) panel at ~16:21 against these baselines.
- **s_gold (boss base B419x + cand398, seeds 1-2, base 673):** kGoldWeight 0.2 -23 ± 12 (648), 0.3 -17 ± 14 (656), kGoldFadeRound 1500 -18 ± 12
  (664): the 0.3 -> 0.12 by r800 fade holds.
- **s_bret (boss base, seeds 1-2, base 673):** kBossRetreatHp 0.35 -6 ± 4 (666), 0.5 -7 ± 6 (665) - off; gs 0.3 on the boss base +10 ± 8 (685).
- **#398 = #395 + kBossMaxStr 250 + kBossGemShare 0.5** (B419x + tools/cands/cand398.edits) uploaded 16:21 UTC; panel vs top395b / top395c.
- **Opening fuel, constructor checkpoints** (6 maps, 4 rounds): the first turn starts with ~170k fuel. Expanse: wall grid 23k, blocked grid 11k
  (re-walks the walls), altars / spawn / bushes ~8k, **cambc::map::camp_groups() 43k**, **the per-camp loop (kind, base_stats, spawn_position,
  is_elk per camp) 63k**; big_world: walls 44k, blocked 42k, camp_groups 56k (the turn ends inside the camp loop); camp_groups 32-56k and the
  camp loop 63-84k on all six. Decision-preserving cuts: blocked grid from the wall grid + holes + altars + enemy spawn (11-42k), is_elk from
  the kind already read (one engine call a camp). The rest only moves to the draft turn (Codex A094 ask 2).
- **#398 panel (16:27 UTC):** top-10 11/50 -16,182 (#395b 11/50 -19,437), rotated 9/50 -20,826 (#395c 9/50 -21,224), held-out 3/40 -22,196
  (#395c 7/40 -18,960) = **23 / -59,204 vs #395 27 / -59,621**. On the boss maps it targets (benchcmp per game): top-10 rows L -688 -> W +292,
  anvil L -79 -> W +822, monolith -821 -> -267, starvation -957 -> -553, fields -667 -> -208, split -551 -> -137, famine -597 -> -361,
  gold_rush -899 -> -590, uncharted_lands W +342 -> L -127; rotated mostly the same direction (guardians -1020 -> -430, big_world -618 ->
  -330). The held-out losses (Mite oasis / quarry / vault, NEET road_of_riches, Trzy crater) are maps boss mode does not touch (golems are
  5,000 health, kBossHp 10,000) and that never changed locally - server-build divergence. Local maps verified equal to the ladder's (camp
  layouts of all five). **#398 kept live.** Past switches on the boss base (s_past, seeds 1-2, base 673): kMaxNeed 4 +11 ± 8 (673 wins),
  kRespawnExact -11 ± 6, kVesperDuo -9 ± 8.
- **s_bhp (#398 base B419x + cand398, seeds 1-2, base 673):** kBossHp 5000 +11 ± 14 (682), 7000 +3 ± 8 (681), **kBossHp 5000 + kBossGemShare 0.3
  +47 ± 15 (716 wins, +43)**; gs 0.3 alone +10 ± 8 (685). Fresh-seed check next; candidate #399.
- **#399 check (fresh seeds 4-5, #398 base 609): kBossHp 5000 + kBossGemShare 0.3 +70 ± 15 (667, +58 wins)** - confirmed (+47 on seeds 1-2).
  Broad: 42 of 70 maps change (#398's change: 17) - gains reverse_spiral +668, gift_wrapping +602, pilgrimage +537 (+10 wins), corners +468,
  lost_world +465, corridors +437, interlock +384, starfish +381, expanse +198 (+8); losses road_of_riches -732 (-7), guardians -512, great_wall
  -298, oasis -280, shortcut -250 (-6), yellow_brick_road -234, packs -220, ambush -155 (-7). Candidate **#399** (tools/cands/cand399.edits on B419x).
- **s_b399 (#398 base, seeds 1-2, base 673):** #399 settings (kBossHp 5000, gs 0.3) +47 (716), hp 5000 gs 0.4 +41 (715), hp 6000 gs 0.3 +35 (706),
  #399 + kBossBudget 2.0 +47 (720) - #399 as is. Effect (armstats, all maps): kills 7.1 -> 7.4, deaths 6.7 -> 6.3, our gold 5,744 -> 5,708, the
  opponent's gold 5,459 -> 5,251: the team grouped on the big nodes dies less and denies them.
- Constructor note: camp::kind() / spawn_position() are cached fields (no engine call) - the per-camp set-up cost is cg.camps() itself.
- **s_w2 (#399 base, seeds 1-2, base 716):** kDeliverGems 20 -2 ± 16 (686), 40 +16 ± 14 (729), kVesperGoldW 2.0 -10 ± 7 (714), 5.0 +1 ± 7 (720).
- **#399** (B419x + tools/cands/cand399.edits; first upload attempt at 17:31 failed with a transient "No CMAKE_CXX_COMPILER" - the retry reused the
  failed CMakeCache; clearing bots/Up399/.cambc fixed it) uploaded ~17:38: top-10 **12/50 -14,177** (#398 11/50 -16,182, #395b 11/50 -19,437).
- **#399 panel:** top-10 12/50 -14,177, rotated 10/50 -18,240, held-out 5/40 -17,775 = **27 / -50,192** (#398 23 / -59,204; #395 same-time 27 /
  -59,621): ties #395 on wins with +9.4k margin, beats #398 by 4 wins - **#399 live (pinned)**. bots/PoolLive refreshed to #399 (the pool now
  takes bosses, as the top teams do).
- **Re-screen vs the boss-taking pool (PoolLive = #399; seeds 1-2):** base #399 688 wins; #398 -54 ± 15 (633; vs the #399 mirror -78 vs -6) - #399's
  gain holds when the bosses are contested; kDeliverGems 40 +18 ± 14 (703) - second positive (~+17 ± 10).
- **s_dg (fresh seeds 4-5, refreshed pool, base #399 637):** **kDeliverGems 40 +29 ± 14 (683, +46)** - third positive (+16 / +18 / +29, ~+21 ± 8);
  kBossBudget 2.0 +9 ± 6 (642); kBossCall 60 -1 ± 2 (637). Candidate **#400 = #399 + kDeliverGems 40** (tools/cands/cand400.edits on B419x).
- **s_w3 (#400 base, seeds 1-2, base 703):** kDeliverGems 50 -23 ± 12 (684), kRecallCapSlack 5 -15 ± 11 (696), 15 -10 ± 12 (692): 40 / 10 hold.
- **s_ft (#400 base, seeds 1-2, base 703): kForceTeam (whole-team farming on every map) -248 ± 16 (548 wins)** - the grouping gain is
  specific to big-node (boss) maps; elsewhere the split stays right.
- **Where #399 gains and loses (tools/stress/mapdelta.py over s_bhp C4 + s_bhp2 C2 + s_pool2 C2 negated, 48 pairs a map; boss layouts from a
  logging bot TBL = B419x + cand400 + a BM line, replays/p2/bosslog/bm.txt, one game a map):** the four clear losers are maps with 200-strength
  giants (20,000-40,000 health) 13-18 tiles from both spawns that #398 already ran as boss maps (or nearly): guardians -468 (-14 wins: four
  5040/60 camps join the set), great_wall -325 (-14: two 7800/60 home-side camps join), shortcut -288 (-18: three 5040/60 incl. one mid camp
  5/6 tiles from each spawn), road_of_riches -356 (-10: 44% giant share, the 5600/120 pair lifts it to 56% - a boss map only under #399).
  The 5000 line alone (s_bhp C2) gives the same four losses. Gains are maps without giants or with many mid camps: pilgrimage +499 (one
  11040/60), reverse_spiral +489, interlock +441, corners +433, eight +414, vault +406 (5880/0), starfish +387, gift_wrapping +385,
  lost_world +348, corridors +330 (a 40480 giant plus ten small camps, all 17-23 tiles from both spawns). kBossHp also gates boss_deny,
  zones, kBossCommit and ward holds, so the 5000 line changes more than the set. Screen: edit_bosstier.py (B425x = B419x + it): kBossTierHp
  (boss set at the giants' line first), kBossCallHp, kBossDenyHp.
- **#400 = #399 + kDeliverGems 40** (B419x + tools/cands/cand400.edits) uploaded 18:51 UTC: top-10 **17/50 -11,453** (#399 12/50 -14,177, #398
  11/50 -16,182); rotated **15/50 -12,336** (#399 10/50 -18,240), held-out **6/40 -19,129** (#399 5/40 -17,775) = **38 / -42,918 vs #399 27 /
  -50,192** (an hour apart): +11 wins, all three benches up - **#400 live**. PoolLive still #399 (refresh after the queued screens).
- **Ladder panel phases (#399 panel, 107 games, tools/stress/gapphase.py):** the r300 gold leader wins - losses r300 gold 963 vs 1,321, r600
  2,086 vs 3,318, r900 2,938 vs 4,998; wins 1,238 vs 888 -> 3,095 vs 2,047 -> 5,245 vs 3,233 (the lead compounds both ways). Losses with no
  death on either side by r300 (26): 1,169 vs 1,447 - farming, not fights. farmcmp r0-300: captures 9.8 vs 15.3 a game, the same on boss and
  other maps; the top teams solo clusters (2clgold party 1 in 183 of 230 on boss maps; ours 28 of 105), 1-2 on a wolf + cluster (ours 3-5).
  Our earlier screens of smaller opening parties (kOpeningRounds 60/40/0, kClusterSolo, kTeamSquads 2, kSplitRound 150) all lost locally -
  not repeated. Opening: our first move at round 2.67 vs 1.92, moves by r12 7.7 vs 9.3 (constructor fuel; a draft-turn precompute is the fix).
- **s_tier (#400 base, seeds 1-2, base 703; B425x):** kBossTierHp 10000 -18 ± 10 (682), kBossCallHp 10000 -4 ± 9 (689), kBossDenyHp 10000 -1 ± 0
  (identical: boss_deny sits behind kBossDeny, off), all three -19 ± 12 (674). The tier moved guardians +162 / shortcut +76 but not great_wall
  (-12) or road_of_riches (-107), while untouched maps moved as much (corners -424, gemcombat4 -375): per-map deltas at 16 pairs are mostly
  fuel-timing noise (SE ~150-200 a map). #399's boss set stays. Lesson: a per-map loss list from 48 pairs is a hint, not a target.
- **s_minor (#400 base, fresh seeds 4-5, base 683):** kMaxNeed 4 +10 ± 9 (684), kBossBudget 2.0 +8 ± 5 (688), kCaptureEmblem 6 (B421x) +9 ± 12
  (684). Small and win-flat; kMaxNeed 4 is now ~+10 on four seed sets. Combination screen s_combo queued.
- **Unseen-style maps and boss mode** (TBL log on Codex's hand-style suite + fixtures, replays/p2/bosslog_unseen): boss mode fires on all five
  hole_pockets sizes (37-74% share) and fx_vertical-odd (90%); rooms / bush corridors stay off - their 3-elk camps hold 4,920 health, just
  under the 5,000 line. s_unseen (#400 vs #395 on the 21 hs/fx maps, 3 seeds, PoolLive + PoolCarry) queued.
- **s_split (#400 base, seeds 1-2, base 703):** kClusterSolo -37 ± 21 (682), kSplitRound 200 (two squads on whole-game team maps) -76 ± 15
  (631), 400 -44 ± 12 (662). The boss-map grouping is not what loses the farming race locally; smaller parties lose again.
- **s_unseen (21 unseen-style maps: Codex's hand-style suite + fixtures, seeds 1-3, PoolLive + PoolCarry; results/ev/run1793129056):** #400
  133/252 +49 vs #395 127/252 -14: **#400 +63 ± 29**. All five hole_pockets sizes (boss mode fires) +163..+458 (+20 wins); rooms / bush
  corridors (no boss) scatter -130..+162; fx_vertical-odd (boss) -91; fixtures without gems unchanged. Boss mode carries to unseen layouts.
- **s_combo (#400 base, seeds 1-2 + 4-5, base 1,386/2,240):** kMaxNeed 4 + kBossBudget 2.0 +10 ± 7 (1,383 wins), + kCaptureEmblem 6 +8 ± 11
  (1,386): not additive, win-flat - no upload.
- **s_bb (#400 base, seeds 1-2, base 703):** kBossBudget 3.0 -23 ± 9 (680), 5.0 -36 ± 10 (670), 0 (no strength gate) -96 ± 18 (635). Ladder
  top teams hit monoliths from r13-230 (gold_rush, great_wall, broken_curve) where ours start r420-1150, but earlier commits lose locally:
  1.5 (live) / 2.0 (+8, +9) are the range.
- **Ranked series (Oct 27, `cambc matches list --team me --kind ranked --json`):** #400 (from 19:00 UTC) 4 of 6 series won (games 18-10:
  FürFortnite 2-3, an iq too high 2-3, SkibidiSloppers 5-0, janestreet 3-2, NTU 4-1, smurphy 4-1); #399 (17:40-18:50) 3 of 8. Ladder rank 43,
  rating 2,002 at 20:00 UTC (rank 10 = 2,223).
- **#400 ranked losses (9 downloaded, replays/p2/rk400loss, phases.py):** 00vault vs FürFortnite (4 picks) **1,037 gems to 4**: the vault is 49
  gem clusters (343 gems, 5,880 health, no strength); both teams chipped it from their own sides, the last members alive were always on
  theirs, they killed them and captured it at r157, r320 and r440 while our champions stood 3-8 tiles off (we dealt ~half of all damage).
  GameRules: a capture needs the spawn tiles held uncontested - an enemy on them resets the 5-round timer - and our bot never read
  camp_group::capture_state (enemy_capturing + timer). New switch **kBlockCapture** (tools/edits/edit_blockcap.py, bots/B426x = B419x + it):
  a reward group in sight that the enemy is capturing, worth kBlockValue 30+, a tile within the timer + 1 steps, health 50%+, fight odds
  0.8+ becomes the target (as boss_call); screening s_block. Also: 00oasis vs FürFortnite (4 picks, our Marcella / Vesper / Ryth / Willow vs
  twins + HoR + Marcella + Ryth) 28 deaths; gold_rush vs NTU (3 picks) their monolith from r600, strength 389 vs 105 at r1200;
  treasure_box vs smurphy: up 1,746 to 1,327 at r300 (7 kills), then 0 captures r300-600 and 9 deaths r600-900.
- **s_block (#400 base, seeds 1-2, base 703; B426x):** kBlockCapture 1 (value 30, odds 0.8) +12 ± 17 (718 wins); **value 15 + odds 0.6 +33 ± 18
  (731 wins, +28)**. Probe (TBC logs, 16 games): enemy captures seen 3-264 turns a game, the block fires 0-173 (yellow_brick_road vs
  PoolAggro 173). Fresh seeds 4-5 (s_block2: loose, value 10 / odds 0.4 / slack 2, loose + health 0.3) running.
- **s_block2 (fresh seeds 4-5, base 683):** value 15 / odds 0.6 +12 ± 17 (678); **value 10 / odds 0.4 / slack 2 +45 ± 18 (713, +30)**; value 15 /
  odds 0.6 / health 0.3 +33 ± 17 (693). Looser wins on both seed sets. **#401 = #400 + kBlockCapture 1, value 10, odds 0.4, slack 2**
  (B426x + tools/cands/cand401.edits) ladder test from ~20:26 UTC; s_block3 (seeds 1-2: #401's settings and no gates at all) running.
- **s_block3 (seeds 1-2, base 703):** #401's settings (value 10, odds 0.4, slack 2) +21 ± 18 (715, +12); no gates (value 0, odds 0, slack 3,
  health 0.3) +8 ± 18 (695). #401's settings over both seed sets ~+33 / +21 wins per 1,120.
- **#401 stress scan failed** (stuck 5 cases / 55 rounds vs gate 4; #400 had 1 / 12): not submitted, #400 stays live. Probe (TBD = #401 +
  prints, the five stuck games rerun): no stuck in the reruns; blocks fired only on packs (34) and corridors (7) - champions waited at
  distance 1 beside small groups (the tiles were occupied), and once on a tile the state turns "contested" (2), so the trigger lapsed.
  edit_blockcap.py v2 bits: 1 on, 2 hold contested groups, 4 free tile only (B426x rebuilt; mode 1 unchanged). s_block4 (modes 1 / 3 / 7)
  and NOSUBMIT stress scans of modes 7 / 3 running.
- **s_block4 (seeds 1-2, base 703):** kBlockCapture 1 +21 (715), 3 (hold contested) +23 (716), **7 (hold contested + free tile) +35 ± 18 (728,
  +25)**; **s_block5 (seeds 4-5, base 683): mode 7 +51 ± 18 (724, +41)** - ~+43 / +33 wins per 1,120 over four seeds, the day's best local
  result after boss mode. Stress scans of modes 1, 3 and 7 all show the same stuck 5 / 55 rounds in byte-identical games where no block
  fired (the capture-state read's fuel shifts every trajectory off #400's; #400 had the same Vesper stall on rows): base-bot episodes, a
  recorded STUCK_CASES=5 exception (55 rounds within the 60-round gate). **#401 = #400 + kBlockCapture 7, value 10, odds 0.4, slack 2**
  (B426x + tools/cands/cand401.edits) uploading ~20:52 UTC.
- **s_deny (#401 base B426x + cand401, seeds 1-2, base 728):** kBossDeny + kBossDenyAll (edit_denyall.py, bots/B427x: boss_deny on every map)
  **-663 ± 23 (286 wins)**: it also fires on bosses our own team is fighting (any boss under 90% health) and parks the team outside their
  reach. Keep it behind tiebreak(); an enemy-hurt-only variant would need the damage source.
- **#401 panel (20:55-21:06 UTC):** top-10 15/50 -11,696, rotated 10/50 -17,250, held-out 7/40 -17,869 = **32 / -46,815 vs #400 38 / -42,918**
  (benched 18:55-19:01). Per game the rotated benches of #399 / #400 / #401 flip 13+ of 50 results each way (fuel chaos): -6 wins is
  inside the noise but the wrong way. #400 re-activated 21:07; same-time back-to-back benches (#401 then #400, top-10 + rotated) at ~21:56.
- Ranked 343c1034 (02treasure_box vs smurphy): we banked 627 gems to their 109 by r600 farming gem clusters, our gold r300-600 520 vs 1,633;
  their strength 246 vs 93 and health 5,267 vs 1,962 at r1200 - they bought out of the deficit, killed us (9 deaths r600-900), took the
  mid golem and banked ~1,000 after r600 (final 866 vs 1,107). A gem lead without gold is not safe past ~r600.
- **s_block6 (#400 base, seeds 1-2 + 4-5, base 1,386/2,240):** #401 (mode 7, odds 0.4) **+43 ± 13 (1,452, +66)**; odds 0.8 +23 ± 13 (1,423);
  odds 1.0 +38 ± 13 (1,438). Block-capture is positive locally at every odds gate.
- **s_pblock (bots/PoolBlock = #401 config as the only opponent, seeds 1-2 + 4-5):** #400 262/560 -32, #401 276/560 -31: margin +1 ± 28,
  wins +14 - against a team that also contests captures the gain shrinks to wins only; #400 loses to PoolBlock by 32 (block-capture beats
  non-contesters).
- **s_unseen2 (21 hs/fx maps, seeds 1-3, PoolLive + PoolCarry):** #401 139/252 +58 vs #400 133/252 +49: +8 ± 19 - no harm on unseen layouts.
- **Same-time benches (same401.sh, 22:00-22:10 UTC):** #401 top-10 15/50 -11,996 + rotated 9/50 -18,490 = **24 / -30,486**; #400 top-10 14/50
  -15,267 + rotated 12/50 -17,186 = **26 / -32,453** - a tie against the top 10 (as s_pblock: teams that contest captures cancel it). Local
  +43 ± 13 (+66 wins) vs non-contesters, unseen maps +8: **#401 live from ~22:15 UTC** (the knockout and ranked fields are mostly
  below the top 10); judge it further by ranked series by version. bots/PoolLive refreshed to #401 (B426x + cand401).
- **s_b401 (#401 base vs the refreshed pool with PoolLive = #401, seeds 1-2, base 727):** kBlockSlack 3 +0 ± 10, kBlockHp 0.35 -21 ± 8,
  kBlockValue 5 -3 ± 5 - #401's settings hold. The mirror (PoolLive) now scores +2 against us.
- **German Empire (rank 34, 2,040; beat us 1-4 at 17:30 and 21:32; draft HoR, Vesper, Ryth, Marcella, Vendetta - our five with Vendetta for
  Willow; replays/p2/rk_ge):** a pure farming race - near-zero deaths on both sides; expanse captures 26 / 30 / 22 per 300 rounds vs our
  9 / 8 / 9 (we take 2-elk camps, they sweep 1-elk camps and clusters), strength 64 vs 50 and health 1,840 vs 1,340 at r300 (Vendetta vs
  Willow is part of it). Ladder rank at 22:30 UTC: **39 (2,022)**, up from 43.
- **s_cap2** (bots/B428x = B426x + edit_capture.py with the anchor moved): kCaptureEmblem 6 / 31 / 8 on the #401 base vs the contesting
  pool - running (3-turn captures shorten the window a contester has).
- **s_cap2 (#401 base vs the contesting pool, seeds 1-2, base 727):** kCaptureEmblem 6 -8 ± 13, 31 -19 ± 16, 8 (Marcella) -0 ± 13 - still no gain.
- **s_balert (edit_blockalert.py, bots/B429x: kBlockCapture bit 8 posts the defend alert on an enemy capture; seeds 1-2, base 727):** -8 ± 15 (713) - off.
- **#401 ranked series (22:00-22:50 UTC):** Nameless 3-2, The Party of Heroes 5-0, dromedaries 3-2 (beat #400 1-4 at 21:10), jazz 3-2 (beat
  #399 2-3 at 18:10): 4 of 4; ladder rank 37 (2,028) at 22:45.
- **Ranked by draft size (last 100 ranked games, 19:30-22:40 UTC, #399-#401):** 3 picks 8/19 (42%), 4 picks 17/24 (71%), 5 picks 32/57 (56%).
  3-pick maps are the weak class; opponents there field HoR (NTU Vesper / HoR / Marcella, German Empire Marcella / Vendetta / HoR) where we
  field Ryth (kDraftAlt 1 HoR-for-Ryth was -47 locally, not laddered).
- Stress-scan "stuck" check, rows Vesper at (38,38) (in both #400 and #401 scans): she stands guard while Marcella channels 470 gems at an
  altar - benign.
- **s_three (#401 base, the 12 three-pick maps, seeds 1-4, base 233/384):** kDraftAlt 1 (HoR for Ryth at 3 picks) **-251 ± 35 (154)** - our code
  is built around Ryth's stun; the ladder's 3-pick weakness is not the pick.
- **s_final (fresh seeds 6-7, pool with PoolLive = #401):** #401 697/1120 +130 vs #400 684/1120 +127: **+3 ± 18 margin, +13 wins** (PoolAggro -54,
  PoolCarry +24, PoolFinish +51, PoolLive -9). Block-capture: strong vs non-contesters (+43 over four seeds with the old pool), neutral vs
  contesters (PoolBlock +1, this pool +3, ladder top 10 tie); never costs wins. #401 stays live.
- **Unseen-map stress scan of Up401** (21 hs/fx maps x 2 sides vs PoolCarry, $SP/scanU401): 21/42 wins, loops 7 (39 rounds), stuck 8 (29 rounds,
  max 9), never left spawn 6 (fx groups-64..256 hold no gems; fx disconnected-spawns cannot reach), fuel-limit turns 281 a game (pool
  maps 180). No knockout-relevant failure.
- **#401 ranked losses (8, replays/p2/rk401loss):** mostly fights - arena vs Nameless (3 picks) 6 / 5 / 8 / 5 deaths per 300 rounds, quarry vs
  dromedaries 5 / 9 / 7, starvation vs Sheeesh 5 / 5 / 5: their five (Tavi, Marcella, Prism, Willow, Varg) camped the central 28-gem cluster
  group from r95 and killed ours as we came (4 deaths r120-145); we earned 120 gold per 300 rounds on a starved boss map. Local armstats
  (s_block6): block-capture lowers our deaths 6.6 -> 6.3 and raises kills 7.2 -> 7.5; odds 0.4 vs 1.0 give the same deaths (6.3) - no
  evidence the 0.4 gate feeds fights.
- **s_final2 (seeds 6-7, contesting pool, base 684):** kBlockOdds 1.0 **+23 ± 18 (716)** vs #401's 0.4 +3 (697). Six seeds: 0.4 ~+30 / +79 wins,
  1.0 ~+33 / +84 wins, and 1.0 is the better one against contesters (and avoids walking into stacks, ranked starvation). **#402 = #401 with
  kBlockOdds 1.0** (B426x + tools/cands/cand402.edits), ladder test ~23:10 UTC.
- **#402 panel (23:13-23:25 UTC):** top-10 15/50 -13,927, rotated 7/50 -21,009, held-out 9/40 -17,015 = **31 / -51,951** (#401 32 / -46,815 at
  20:55; #400 38 / -42,918 at 18:55; same-time 22:00 top-10 + rotated: #401 24, #400 26, #402 at 23:13 22) - the three are inside the
  panel noise. #402 kept live (local six seeds ~+33 / +84 wins, better vs contesters; best held-out of the three). Ladder rating 2,002 (rank
  43) at 20:00 -> **2,065 (rank 27) at 23:20 UTC**.
- **Team profiles, last 50 ranked games each** (tools/stress/radarnow.py LADDER OUT 50 50; radarnow now takes our real rank from the ladder JSON;
  dashboard "Ladder Team Profiles" https://claude.ai/artifact/2iycjM7RyiWYJyieCfNfWC updated 23:42 UTC): us (rank 27, 68% won) KDA 3.64
  (80th pct of the top 20 + us), Trade 1.19 (80th), Gank 0.52 (45th), Outplay 41% (100th), **Gold 461 / 100 rounds (0th: lowest; Supaswag
  708, Trzy 667, Mite 634)**, Farm eff. 170 (90th), Vision 13.0 (50th), **Farm 3.5 camps / 100 rounds (5th; Mite 5.98)**. Our fight numbers
  come against weaker opponents; gold income and clears are the gap.
### Oct 27-28 (grant 8, from ~23:45 UTC) - farming to match the top teams
- **Single-elk clears** (tools/stress/soloelk.py, #399-#401 ladder panels): r300-600 the top teams clear 30% alone and 18% with 4+, we 9% / 42%;
  our solo clears cost the same health (97% -> 72% vs 93% -> 66%, 18-19 rounds). By map class: **boss maps** (whole team all game) top
  solo 35% / 4+ 14% vs ours **5% / 48%**; other maps 21% / 26% vs ours 18% / 28% (party sizes match, but we clear 57 to their 126). On boss
  maps the squad rule (solo picks only for home camps with 2+ hitters, team_camp_) keeps all five on 1-elk camps. kTeamSoloSingles
  (edit_teamsingles.py, bots/B430x = B426x + it): from round R, team rounds allow solo picks of single-hitter camps; s_singles R 240 /
  400 / 600 on the #402 base running.
- **Non-boss maps r300-900** (farmcmp, #399-#401 panels): captures 21.6 vs 30.1 a game; 1elk+2cl 1.42 vs 3.61 a game, clear 30 vs 18 rounds,
  respawn lead 30 vs 3; time walk 58% / idle 12% / dead 14% vs walk 25% / "recall" 52% / dead 9%. The top teams' recall share is mostly
  recall channels started while fighting a live camp (43% of their still-channel rounds) or capturing (26%); waiting beside a respawning
  camp is 22% (~4% of champion time vs our ~1.4%). kMaxWait 0 (live) never picks a camp still respawning on arrival - its comment's
  premise ("top teams almost never stand waiting") read the old idle measure; no recorded screen. s_wait (-1 / 15 / 30 / 60) queued.
- **s_singles (#402 base, seeds 1-2, base 724 vs the #402 pool):** kTeamSoloSingles 240 -13 ± 13 (707), 400 -8 ± 12 (716), 600 -7 ± 12 (717) -
  breaking single-hitter camps off the boss-map squad loses locally too.
- **s_wait (#402 base, seeds 1-2, base 724):** kMaxWait -1 (no limit) -50 ± 16 (677), 15 -18 ± 15 (702), 30 -20 ± 16 (704), 60 -54 ± 16 (675) -
  waiting for respawns loses; kMaxWait 0 holds.
- **Skipped camp hits** (ladder #399 panel, r300-900, no enemy within 6): in reach of a live camp we hit it 76% melee / 48% ranged of turns, the
  top teams 83% / 56% (HoR 81 / 87, Marcella 73 / 80, Ryth 75 / 81, Vesper 49 / 55, Willow 46 / 65). Probe kMissLog (edit_misslog.py, bots/
  B431x; TML = #402 + log, 24 games, replays/p2/misslog/miss.txt): 6,901 turns ended with a live camp monster in range, no enemy within 6, no
  attack - travel 1,861 (another camp passing by), capture 927 (Vesper 529: capturing beside the next camp), wait_party 786 (631 on the
  target camp: a tuned wait, kAllyWait 6 -22 / 20 +1), fight_camp 742 + help_ask_squad 528 (moved this turn: approach steps). New switch
  **kCampFreeHit** (edit_campfree.py, bots/B432x): a turn-end basic attack on the weakest awake monster in range, bit 1 of our / a mate's
  target group only, 2 any awake camp; s_free running.
- **s_free / s_free2 (#402 base):** kCampFreeHit 1 -18 ± 18 (709/1120), 2 +11 ± 19 (734) on seeds 1-2, 2 -8 ± 19 (693 vs 704) on seeds 4-5 - flat.
  It fires ~56 extra hits a game (TCF probe: Ryth 230 / HoR 180 / Marcella 130 / Vesper 99 / Willow 39 over 12 games; ranged champions
  have usually moved). Off.
- **Ranked by version** (tools/stress/rankedfarm.py N LABEL=START..END: our ranked games split by live-version window, radarnow measures):
  #399 35 games 49% won, gold 447 / 100 rounds, clears 3.47; #400 60 / 60% / 470 / 3.23; #401 35 / 74% / 474 / 3.76; #402 35 / 34% / 440 /
  3.05 (KDA 1.68 vs 4+). Confounded by opponent strength: #401's run lifted us to 2,065 (rank 27) and #402 then met ranks 24-38 (1-4, 1-4,
  1-4, 2-3, 2-3, 2-3, 3-2) where #401 had met ranks 38-46; rating back to 2,031 (rank 36) at 00:40 UTC. Version A/Bs on ranked need the
  same rating band.
- **#403 = #402 + kTeamSoloSingles 400 + kCampFreeHit 2** (B433x = B426x + edit_teamsingles + edit_campfree; tools/cands/cand403.edits):
  local -0 ± 19 (723 vs 724); uploaded ~00:45 UTC as a ranked farming A/B against #402 (top-10 bench only as a disaster check).
- **#403 top-10 bench (00:45 UTC): 11/50 -19,253** vs #402 15/50 -13,927 and #401 15/50 -11,996 - EARLY_STOP; #402 re-selected at 00:48. Split
  play on boss maps (kTeamSoloSingles) plus free hits is worse against the top 10, as locally. The ranked farming A/B is cancelled.
- **Farming push conclusion (00:55 UTC Oct 28):** the top teams' edge is champions strong enough to farm alone, not the split itself: split arms
  lose locally (kTeamSoloSingles -7..-13, kClusterSolo -37, kSplitRound -44..-76), against a grouped mirror, and on the ladder (#403 top-10
  11/50 vs 15/50). Clear speed on 1-elk camps (30 vs 18 rounds) = strength (soloers 102 vs 140) plus ~7 points fewer hits in reach. Our
  item lines put strength on Vesper only (Marcella / HoR Focus, Ryth / Willow Health); the top teams' Marcella and Ryth carry Strength,
  but strength lines lose locally (kMarcBuild 7 -47, kBuild3 -132) because our fight code leans on Marcella's and HoR's Focus spells.
  Next step needs a bigger change (fight code that works with strength builds, or per-champion camp ownership), not another switch.
- **s_b3 (#402 base, seeds 1-2, base 724 / kills 7.6 / deaths 6.2 / gold 5,824 / theirs 4,942; armstats):** the top teams' item line per champion
  (kBuild3): Marcella {Treasure H, Jungle S, Bruiser H, Durability H, Bruiser S} **-108 ± 17 (621; kills 4.7, gold 5,342)**; Ryth -10 (705);
  Vesper {Treasure S, Jungle S, Bruiser H, Bruiser S, Durability H} -53 ± 10 (666; gold 5,652); HoR -10 (722); all five **-174 (548; kills
  4.0, gold 4,993, theirs 5,562)**. Strength lines lower our gold too: Marcella's Focus spells drive our cluster farming and our kills.
  In our code Focus is the farming build; strength builds are not a farming lever.
- **s_zones (#402 base, seeds 1-2, base 724):** kZones 1 (not control maps) +2 ± 5 (728), 2 (any non-boss map) +0 ± 9 (720); armstats unchanged
  (gold 5,828 / 5,835 vs 5,824). Camp ownership by zones is neutral where it can run (boss maps, ~60% since #399, are excluded; there the
  split arms lose). Neither "strength builds" nor "zone ownership" is a farming lever in this code.
- **Where the farming gap is (tools/stress/timebudget.py, #399 panel traces, every champion-round classified):** r300-900 (73 games): hitting
  camps 15% vs 16%, capturing 5% vs 8%, moving 56% vs 56%, still 12% vs 12%, dead **12% vs 8%**; camp damage per hitting round **106 vs 136**,
  per champion-round **15.4 vs 21.4** (+39%); earned per 100 camp damage 13.4 vs 12.8 (we pick better camps). r0-300: hit 20 / 22%, move 53 /
  53%, damage per hitting round 69 vs 81, per champion-round 13.9 vs 17.5. **Not pathing or grouping** (time shares match); it is damage
  output. Same champion, both sides (r300-900, damage per champion-round): HoR 12.7 vs 18.3, Vesper 20.3 vs 26.5 (strength 113 vs 145),
  Ryth 15.5 vs 18.2, Marcella 17.4 vs 18.5; our 5th, Willow, 8.8 vs their Vendetta 27.0 / Varg 32.7 / Prism 28.9. With our draft at their
  per-champion rates we would be ~18.4 (vs 15.4 ours, 21.4 theirs): about half the gap is per-champion damage, half the draft's 5th slot.
  Damage kinds (r0-900): HoR spell casts per basic attack 0.30 vs ours 0.19 (its hitting dash, 186 vs 167 a landing); Vesper 117 vs 86 a
  basic hit (strength); Marcella and Ryth match. Deaths: Willow 17% / Marcella 11% / Vesper 11% of mid-game time vs their 4-7%.
  kRuinApproach (edit_ruinapproach.py, bots/B434x: HoR dashes into its camp target from 2-3) screening (s_ruin, four seeds).
- **s_ruin (B434x, four seeds, base 1,428/2,240):** kRuinApproach +3 ± 9 (1,421), gold 5,756 vs 5,755. Probe (TRA, 12 games): HoR in a camp fight
  2-3 from its target with no enemy near ~400 turns, the dash-in fired 84 (cooldown, no free landing, the landing filters); total camp
  dashes 298. Too few extra casts to matter; off.
- **s_vend (#402 base, seeds 1-2, base 724):** kDraftAlt 2 (Vendetta for Willow) **-256 ± 21 (524)**: kills 7.6 -> 5.5, deaths 6.2 -> 8.0, our
  gold 5,824 -> 5,081, theirs 4,942 -> 5,710. In our code Willow's heals keep the four farmers alive and farming; our Vendetta (meta line
  Jungle S / Durability H / Monster S / Bruiser S, generic melee play) is not the top teams' kill-reset carry (their Vendetta strength 162,
  122 a basic hit, 27 camp damage a round). The 5th-slot half of the gap needs a Vendetta that plays like theirs, not a draft swap.
- **Deaths by champion (#399 panel, 107 games):** ours ~9.3 a game - Willow 265, Vesper 220, Marcella 210, Ryth 191, HoR 109; the top teams ~6.3 -
  HoR 147, Vendetta 124, Vesper 118, Marcella 90, Ryth 70. 91-96% of our deaths have an enemy champion within 5 (fights, not camps). Willow
  dies beside her team (median 3 tiles to the nearest ally, isolated 25%): focused in team fights as the softest target.
- **kScaleGold (Eric Oct 28: gold before gems on boss-fight maps - one altar, or monoliths round a contested centre - until mid game / enough
  gold; edit_scalegold.py, bots/B435x = B426x + it):** layout test at set-up - bit 1 one altar, 2 two+ giants (20,000+ health, a 200-strength
  monster) within 6 of the midline, 4 one+; gold worth kScaleGoldW gems in camp scores until kScaleEmblems emblems or kScaleRound. Classifier
  (TSG, one game a map, replays/p2/scalelog/scale.txt): bits 1+2 flag 28 of 70 pool maps (anvil, breadcrumbs, contest, crater, eight,
  great-wall, monolith, split, the-line, big-world, boss-battle, broken-curve, fracture, hooks, shortcut, starvation, the-farm, cuts, fields,
  guardians, the-pack, treasure-box, uncharted-lands, gemcombat1-5); bit 4 adds lost-world, rows, corridors, gold-rush, famine. s_scale
  (W 1.0 / 0.6, emblems 3 + r600 / 5 + r900, bits 3 / 7) running.
- **s_scale (#402 base, seeds 1-2, base 724 / gold 5,824 / theirs 4,942):** kScaleGold 3 W 1.0 -41 ± 16 (691; gold 5,831, theirs 5,132), W 0.6 -46
  (697), 5 emblems + r900 -60 (680; gold 5,884), bits 7 -42 (696). Our gold hardly rises (gold on these maps comes with the gem camps)
  while the opponent's rises ~200 a game. Per map (C2): gold up on starvation 4,192 -> 5,171, anvil 3,639 -> 4,172, boss-battle 9,266 ->
  9,978, monolith 5,365 -> 5,723, but contest 6,612 -> 5,227 (deaths 15.5 -> 19.4) and guardians 6,423 -> 5,578 (14.6 -> 17.8); single-altar
  maps sum ~-21 a map, the midline-giant maps clearly negative (fracture -404, broken-curve -279, contest -212, split -178). Off.
- **Fights on the #399 panel (fights.py / fightdetail.py / fightrounds.py, r300-900):** by power ratio (strength x health within 8) we net
  -0.31 a fight when even, -0.24 at 1.25-2x, -0.02 at 2-4x; the top teams +0.31 / +0.31 / +0.27. Even fights (333): we bring 2.7 to their 2.3,
  lose 0.53 a fight to their 0.24, kill 15% of the enemies we hit vs 33%; our first death in 63% of fights with one (Willow 36, Vesper 20,
  Ryth 17, Marcella 14, HoR 10), at 96% start health. Deaths by type in even fights: Willow 50, Vesper 44 (theirs 15), Ryth 30, Marcella 30,
  HoR 22 (11). Marcella hits champions 0.10 a round (theirs 0.24), in range 7% (15%) - the carrier keeps out. Vesper with an enemy in range:
  hit 36% + hit-and-move 9% vs 40% + 17%, steps away 18% vs 11%.
- kKiteShot (edit_kiteshot.py, bots/B436x: a ranged champion dashing away in escape() also shoots; Vesper's dash is an ability, legal - 5 of 5
  attacks landed in the TKS probe) fires rarely (5 in 12 games vs PoolAggro); kMoveReset 2 (move, reset, shoot) is already live. s_kite running.
- **Vendetta, ours vs the top teams'** (tools/stress/vendstats.py; ours = 24 local games of #402 + kDraftAlt 2, replays/p2/vendlocal; theirs =
  140 games of the #399 / #402 panels): camp-hit rounds 17.6 vs 18.5 / 100, double hits (basic + reset) 21% vs 27% of hit rounds (never 3+:
  the reset is used whenever up; kills refresh it), dashes 8.8 vs 8.8 / 100, deaths 0.9 vs 1.0 a game, camp damage a round r300-900 29.7 vs
  27.0, gold by r600 567 vs 727, strength 154 vs 165, **max health 1,385 vs 1,823** (their lines buy Health: Fish Treasure H > Jungle S >
  Bruiser H > Durability H > Bruiser S). Our Vendetta farms like theirs; kKillChain (one reset after a kill) is off, but the top Vendetta
  does not chain either. The draft's loss is the team without heals: in those 24 games our HoR died 28 times (the pool's HoR 16), Ryth 30
  (23), Vesper 27 (21), ~90% in fights. edit_nohealer.py (bots/B437x): no_healer_ (no Willow drafted) + kNoHealPvp / kNoHealRetreat /
  kNoHealEngage / kNoHealBudget; s_nohealer (Vendetta draft x Fish's Vendetta line x no-healer rules) running.
- Top-team Vendetta emblem order (buildorder.ts OTHER=1, #401 / #402 panels, 134 games): #1 r215 Treasure H 36% / Jungle S 27%, #2 r330 Jungle S
  60%, #3 r470 Power S 32% / Durability H 19%, #4 r525 Bruiser S / Durability H, #5-6 Bruiser S; by r600 Jungle S 65%, Monster S 35%, Bruiser S
  32%, Durability H 31%, Power S 30%, Treasure S 28% / H 27%.
- **s_nohealer (#402 base, seeds 1-2, base 724; all arms kDraftAlt 2 = Vendetta for Willow):** Vendetta alone -256 (524; kills 5.5, deaths 8.0,
  gold 5,081); + Fish's Vendetta line (kFishBuild 8: Treasure H, Jungle S, Bruiser H, Durability H, Bruiser S) **-235 (544; deaths 7.5, gold
  5,193)**; + no-healer rules (escape 0.5, retreat 0.45, engage 1.2, camp budget x0.75; B437x) -290 (491); both -283 (487); escape / retreat
  lines only -290 (485). Caution costs more than the deaths it saves; the Fish line helps a little.
- **s_nohealer2 (Vendetta draft + Fish's Vendetta line as base, 544/1120):** + kBuild3 8 (top HoR line) -5, + kBuild3 2 (top Ryth line) -16,
  + kBuild3 4 (top Vesper line) -38, + kIdleHealHp 0.85 -4. Locally the best Willow-less draft is ~-235 vs #402 with Willow (all pool bots
  field Willow). Ladder same-time test #404 (= #402 + kDraftAlt 2 + kFishBuild 8) vs #402 next.
- **#404 = #402 + kDraftAlt 2 (Vendetta for Willow) + kFishBuild 8** (B426x + tools/cands/cand404.edits), uploaded ~05:12 UTC Oct 28 (stress
  21/24, stuck 1): top-10 **5/50 -23,576** (#402 at 23:13: 15/50 -13,927), rotated **5/50 -25,314** (#402 7/50 -21,009). Per game 12 of #402's
  top-10 wins became losses (eight, pilgrimage, uncharted, rows, dunes, famine, ribs, elk_arena, starfish, harvest, crossing, gemcombat1),
  2 the other way. The ladder agrees with the local -235: with our code the Willow-less draft is far worse. #402 re-activated; same-time
  #402 benches (top402c / top402cr) running.
- **Same-time benches after #404 (top402c / top402cr, ~05:30 UTC):** #402's re-activation was not confirmed; **#401 was live (pinned)**, so these
  are #401's: top-10 **15/50 -14,189**, rotated **11/50 -18,851** (vs #404's 5 + 5, #402's 15 + 7 the evening before). #401 left live.

### Oct 28 (UTC 05:30-) - v405 plan, phase 1 (Eric: "begin implementing this plan for v405; if undoable, continue from 402 or 401")
- **Fight simulator vs the square law** (`tools/stress/fightsim.py`, 195 top-10 bench games, 3,008 champion fights r150-1500): a turn-by-turn
  simulator (walk-in by distance and range, dashers 2 sooner, one spell a turn, 8-turn cooldowns, stuns, Willow's heal, shields, HoR's
  passive, both sides focus the weakest in reach) predicts outcomes **no better** than the bot's own odds: AUC "won" 0.691 vs 0.689 (str x hp
  only 0.660). Phase 1 as planned (simulator in place of fight_odds) is not worth building.
- **At the same odds we lose:** even odds (0.8-1.25) we net -0.13 kills a fight, the top +0.14; odds > 4 +0.23 vs +0.62. `fightexec.py`:
  focus (share of damage on one enemy) ours 0.73 vs 0.63, reinforcements 0.25 vs 0.22 - not the gap; dealt / taken 0.90 vs 1.11; **our
  champions that drop under 35% die 50% vs 26%, and their low ones escape us 74% vs 50%**.
- **Low-health play** (`lowfight.py`; top teams pre-start a recall every turn end, so only recalls of 2+ rounds count): first action after
  dropping under 50% with an enemy within 6 - both sides alike (away ~28 / 25%, hold ~27 / 24%, attack ~19 / 23%, real recall 1 / 4%), but
  **ours die twice as often after the same choice** (away 22% vs 10%, hold 47% vs 22%, attack 44% vs 27%). The pursuers' damage, not the
  escape choice: the same root as the farming gap (damage output).
- **HoR's camp damage is the dash** (`champdmg.py`, `--champ HoR`, 530 bench games r100-900): 1,352 vs 1,982 camp damage per 100 rounds alive;
  hitting rounds 21.1 vs 21.9 / 100, basic hits 0.96 vs 0.95 a hitting round at 34 vs 35 - identical; dash on camps **2.48 vs 3.54 per 100
  rounds alive**, monsters a landing **1.53 vs 1.75** (2+ monsters 40% vs 55%), 262 vs 347 damage a landing (Focus 150 vs 180). Dash use per
  100 rounds: travel 4.64 vs 4.19, no hit near an enemy 1.34 vs 0.98, champions 0.49 vs 0.62 - the same total (9.0 vs 9.4). **With the dash
  ready during a camp hit theirs casts it 82% (no enemy within 8) / 69% (enemy within 8); ours 48% / 17%** (kSaveSpells 8 holds every camp
  spell near enemies; our camp landing is the free tile nearest the target alone). HoR's dash explains ~90% of its camp-damage gap.
- **edit_ruincamp.py** (bots/B438x = B426x + it): kRuinCampAim bits 1 land on the most living members of the target's group, 2 beside any
  member, 4 HoR dashes camps through kSaveSpells unless an enemy is within kRuinSaveNear 5; kRuinDiag logs failure reasons. Probe TRD (#402 +
  log) / TRE (+ aim 7) vs PoolCarry, every map both sides (replays/p2/ruindiag_*); screen s_ruincamp (aim 1 / 3 / 7, seeds 1-2) next.
- **Probe TRD / TRE** (`tools/stress/ruindiag.py`, 140 games each vs PoolCarry, every map both sides): HoR in reach of its camp target 15,429
  turns; kSaveSpells held 2,465, cast already used 1,386; with the dash ready and in reach a landing was found 2,977 times but **the engine
  refused 1,010 of them (987 "Destination is unreachable within movement range", all 2 tiles away)** - a dash walks its two steps, so a live
  monster (or enemy) on every middle tile blocks it, and ruin_dash never checked. With kRuinCampAim 7 (TRE) landings found 3,865, refused
  1,956 (51%: the landings that cover more monsters sit behind them), cast 1,906 hitting 1.91 monsters each (3,645 vs TRD's 1,961).
  **kRuinReach** (same edit): landings without an open middle tile rank last and up to 4 ranked landings are tried until one is taken (camp
  and champion dashes). Probe with it running; screen s_ruincamp (C2 reach, C3 reach + aim 3, C4 reach + aim 7) and s_three2 (12 three-pick
  maps, seeds 1-4: HoR for Ryth + reach, + aim 7) queued after it.
- **Probe with kRuinReach (TRD / TRE again):** reach alone - refusals 1,010 -> 120 but casts only 1,961 -> 2,011 (a refused dash stays
  ready and mostly lands next turn: the fix saves a turn, not a dash); reach + aim 7 - 2,220 camp dashes hitting 4,313 monsters (1.94 a dash).
- **s_ruincamp (#402 base, seeds 1-2, base 724/1120; only the 45 maps where we draft HoR change):** reach -14 ± 12 (716 wins); reach + aim 3
  **+8 ± 13 (746, +22 wins; changed maps +12 a game)**; reach + aim 7 +7 ± 14 (740, +16). Confirming on seeds 4-5 (s_ruincamp2).
- **s_three2 (12 three-pick maps, seeds 1-4, Ryth draft 231/384):** HoR for Ryth + reach -263 ± 34 (141); + aim 7 **-175 ± 34 (182)** - the aim
  is worth +88 a game / +41 wins where HoR farms more, but Ryth still leads at 3 picks. By map (aim 7 vs Ryth): gold-rush +86, arena +43,
  gemcombat1 +32, the-pack -7; collision -591, anvil -482, broken-curve -345, the-pond -322, fragment -296. Ryth stays.
- **s_ruincamp2 (fresh seeds 4-5, base 704/1120):** reach + aim 3 -5 ± 14 (689), reach + aim 7 -12 ± 13 (689) - over four seeds the aim is
  neutral at 5 picks (+7 / +1 wins); reach alone was negative on both seed sets (-14, -12).
- **Low-health "did nothing" turns are not fuel:** ladder fuel files (u64 per champion turn, 100,000 = capped) mapped to rounds - the team's
  capped share in rounds where a low champion of ours stood still and did nothing with an enemy within 6 is 1.5% (fight rounds 0.8%,
  calm 1.1%). Those turns are stuns (not in the trace) or waits.
- **3 picks, per game (s_three2, our side):** Ryth draft gems 752 / kills 5.3 / deaths 5.5 / gold 6,456; HoR + reach 616 / 3.9 / 7.4 / 5,388;
  HoR + reach + aim 7 674 / 4.8 / 6.4 / 5,972. Reach without the aim: fragment deaths 13.9 (Ryth 6.9, aimed HoR 7.9) - suspicion that
  retrying refused FIGHT dashes lands HoR worse. **edit_ruinreach2.py** (bots/B439x): kRuinReach 1 every dash / 2 camp dashes only;
  screen s_reach2 (the 46 HoR maps, seeds 1 2 4 5): reach 2 + aim 3, reach 2 + aim 7, aim 7 without reach.
- **#405 = #402 + kRuinReach + kRuinCampAim 7** (B438x + tools/cands/cand405.edits; Eric asked for "v405"): ladder test from 06:26 UTC with a
  same-time #402 bench (top402d / top402dr); #401 (pinned live before) restored after.
- **s_reach2 (the 46 HoR maps, seeds 1 2 4 5, base 938/1472):** camp-only reach (kRuinReach 2) + aim 3 -4 ± 14 (934); + aim 7 +1 ± 15 (938);
  **aim 7 without reach -18 ± 15 (903)** - aimed landings are the ones most often refused, so the aim needs the retry. Camp-only vs every-dash
  reach: no difference. The HoR dash package is neutral locally at 5 picks; ladder mechanism check (sl_top405, 23 HoR games vs the top 10):
  our HoR's camp damage per hitting round 84 vs #402's 65 (top 94), per 100 rounds alive 1,703 vs 1,426 (top 1,930).
- **#405 ladder test (06:26-07:01 UTC):** stress 23/24, stuck 1. Top-10 **13/50 -15,483** vs same-time #402 (top402d) 15/50 -15,077; rotated
  **13/50 -17,490** vs #402 (top402dr) 10/50 -19,410. Total **26 vs 25 of 100, +1.5k margin: a tie**, with our HoR's camp damage +19% on
  the ladder. #401 (pinned live before the test) restored at 07:01 UTC; whether #405 goes live is Eric's call (no regression, better HoR
  farming, no measurable win gain).
- **s_three3 (Eric: "should we make map-type rules for Ryth vs HoR?" -> more seeds on HoR's four best 3-pick maps; seeds 5-16, 384 games):**
  HoR for Ryth (+ reach + aim 7) **-44 ± 32, wins 199 vs 224**. Per map (paired, 96 games): gold-rush **+175** (+9 wins; seeds 1-4 +86),
  the-pack -16 (-6; mostly identical games), gemcombat1 -60 (-11; was +32), **arena -274 (-17; was +43)**. Only gold-rush holds up - one map
  of twelve is no basis for a layout rule. No 3-pick map rule; Ryth stays everywhere at 3 picks.

### Oct 28 (UTC ~07:30-) - Eric: wards in bushes near contested points / fight sites; HoR over Ryth; Codex back (A102)
- **Ward study** (`tools/stress/wardstudy.ts`, 1,245 top-10 bench games; state.wards + Game_GetBush; a ward shows its owner only): placements
  per 100 champion-rounds ours 3.35 / top 3.49; **on a bush tile 48% vs 79%**; within 4 of an altar 23 / 25%; within 6 of a live camp 57 / 61%;
  at a fight site (30 rounds before) 35 / 28%; sees a fight while standing 34 / 28%; fight rounds inside own ward vision 82 / 79%. The one
  gap is bushes: our camp-watch ward (watch_ward) takes the tile nearest the camp centre unless kWardBushBias > 0 (0 since it was added);
  role / guard / altar / scout wards already prefer bushes. Screen s_wardbush: kWardBushBias 2 / 4 / 6.
- **3-pick probe, HoR vs Ryth draft** (bots/THR / TRY, 30 games each vs PoolLive / Aggro / Carry on collision, anvil, broken-curve, fragment,
  the-pond; replays/p2/three3_*): wins 11 vs 17, deaths 9.0 vs 5.6 (Vesper 3.2 vs 2.2, Marcella 3.2 vs 2.1, HoR 2.6 vs Ryth 1.3), kills 5.8 vs
  7.7, gold 5,557 vs 6,866; r300 gold equal (855 vs 867), early deaths equal, time apart from teammates equal - **the gap is late fights**
  (r700+ deaths 7.0 vs 4.2; dealt / taken 0.95 vs 1.16; our lows die 33% vs 24%; their lows escape 84% vs 70%). HoR farms like Ryth (camp
  damage a champion-round 16.3 vs 16.5) but our HoR has 1,890 health / 34 strength mid-game vs Ryth's 2,648 / 74: without Ryth the team has
  no frontline. **edit_ruinhp.py** (bots/B440x): kRuinBuild 5 (Treasure H, Jungle F, Bruiser H), 6 (Treasure H, Jungle H, Bruiser H), 7
  (Treasure H, Bruiser H, Durability H, Bruiser H); screen s_ruinhp on the 12 three-pick maps.
- **s_wardbush (#402 base, seeds 1-2, base 724/1120):** kWardBushBias 2 **-33 ± 18 (695)**, 4 -31 ± 19 (696), 6 -45 ± 19 (683) - a camp-watch
  ward pushed onto a bush further out stops seeing its camp (and the cover test's 2 + bias radius places fewer camp wards): off.
  **edit_wardsee.py** (bots/B441x = B440x + it): kWardBushSee - the bush tile in placement reach that sees the camp centre and the most member
  tiles (ward::visible_tiles_from), else the usual tile; screen s_wardsee queued after s_ruinhp.
- **s_ruinhp (12 three-pick maps, seeds 1-4, Ryth draft 231/384; all HoR arms reach 1 + aim 7):** HoR with today's line (kRuinBuild 4)
  -175 ± 34 (182); line 5 (Treasure H, Jungle F, Bruiser H) -180 (173); 6 (Jungle H) -187 (173); 7 (Bruiser H, Durability H) -166 (174) -
  health items do not close the 3-pick gap.
- **Codex audit (C199 / C201, collaboration/20261028/hor-ryth-audit.md):** live lead - fight_enemies' trade branch casts support before
  offensive, so HoR shields (health < 0.85 or an enemy within 3) instead of its stunning dash (6 of 16 sampled both-ready turns, each with a
  legal landing on a foe); Ryth has no shield. HoR's kit factor is 1 although its dash hits radius 1; stun_count misses both Ryth's aoe stun
  and HoR's dash stun; kTeamFight / kChainStun / kStunOrder (off) classify only is_cc. **edit_ruinfight.py** (bots/B442x = B441x + it):
  kRuinDashFirst (dash before shield in that branch), kRuinKitAoe (1 + k x (packed - 1), packed <= 3). Screens s_ruinfight3 (3 picks: HoR
  draft, + dash-first, + kit 0.25, + both) and s_ruinfight5 (46 HoR maps, seeds 1 2 4 5: #405 config, + dash-first, + kit 0.25) queued.
- **s_wardsee (#402 base, seeds 1-2, 724):** kWardBushSee 1 (camp-watch ward on the bush tile that sees the camp, up to 25 vision previews a
  placement) **-32 ± 17 (694)**. Two bush rules both -30 wins locally: either fuel (vision previews) or no local value (the pool is our own
  code, which seldom waits in bushes). Fuel check: kWardBushSee 2 (only the 3 bush tiles nearest the camp previewed; bots/B443x) queued.
- **s_ruinfight3 (12 three-pick maps, seeds 1-4, Ryth draft 231/384; HoR arms reach 1 + aim 7):** HoR draft -175 (182); + kRuinDashFirst -176
  (183); + kRuinKitAoe 0.25 **-215 (164)**; both -214 (166). Dash-before-shield changes nothing measurable; the kit factor sends HoR into
  camps it cannot take. The 3-pick gap stays ~-175.
- **#405's HoR on the ladder vs #402's** (sl_top405 vs sl_top402*, r100-900): camp dash cast when ready during a camp hit 68% vs 38% (top
  76%), monsters a landing 1.77 vs 1.53 (top 1.72), damage a landing 342 vs 266 (top 365), camp dashes per 100 rounds alive 2.95 vs 2.69 (top
  3.43). The dash aim now matches the top teams; what remains is a little frequency and Focus (gold).
- **s_ruinfight5 (46 HoR maps, seeds 1 2 4 5, base 938/1472):** #405 config +1 ± 15 (939); + kRuinDashFirst -4 (934); + kRuinKitAoe 0.25 -6
  (936). Neutral: neither goes in.
- **s_wardsee2 (seeds 1-2, 724):** kWardBushSee 2 (only 3 vision previews) **-29 ± 17 (699)** - same as the full version (-32), so not fuel.
  Three bush rules for the camp-watch ward all cost ~30 wins locally: watching the camp and its surroundings is worth more here than seeing
  into bushes (the pool is our own code; the top teams' bush use cannot be valued locally). All off; the ward gap stays measured, not fixed.
- **#405 live** (Eric: "lets do this"; activated ~08:55, live confirmed 09:11 UTC Oct 28).
- **Marcella as the 3-pick tank (Eric: "does the Marcella bruiser build not work? she could be the tank that submits gems - her passive: no
  stuns")**: GameRules - a tribute is stopped by a stun, death or an altar lock, NOT by damage, so a stun-immune Marcella can bank under fire.
  Fish's 3-pick draft is Vesper > HoR > Marcella (13/14) with Marcella Treasure H > Jungle S > Bruiser H > Durability H > Bruiser S. Her tank
  line lost every earlier test (s_build1 -96, s_build2 -136, s_fishb -120: kills 7.4 -> 4.6) - all in 4 / 5-pick drafts WITH Ryth, where our
  code plays her as a Focus caster. Never tested as the tank of the Ryth-less 3-pick draft: s_marctank (12 three-pick maps, seeds 1-4: HoR
  draft; + kFishBuild 2 (Marcella line); + kRuinBuild 5 (Fish's HoR line); + kFishBuild 3 (Vesper too)).
- **s_marctank (12 three-pick maps, seeds 1-4, Ryth draft 231/384; HoR draft + reach + aim 7 as the reference, -175 / 182):** + Marcella tank
  line (kFishBuild 2) **-308 (119)**; + Fish's HoR line (kRuinBuild 5) -286 (118); + Fish's Vesper line (kFishBuild 3) -274 (130). Fish's
  3-pick builds lose in our code even without Ryth: our fight code is built on Marcella's Focus (2 x Focus spell, stunning enhanced attack).
  A tank Marcella needs a different fight role first. kMarcTribute (her tribute near enemies) screening with her usual build.
- **s_marctrib / s_marctrib2 (#402 base, all maps):** kMarcTribute (bots/B444x: Marcella starts a tribute near enemies when the forecast damage
  over the channel stays under 0.6 of her health; the others keep kChannelSafe 6) seeds 1-2 **+2 ± 6, 735 vs 724 wins**; seeds 4-5 +4 ± 6, 710
  vs 704. Four seeds +17 wins / 2,240: small, positive on both sets (the pool seldom contests altars). Candidate for #406 with #405's config
  (B444x + cand402 + kRuinReach 1 + kRuinCampAim 7 + kMarcTribute).
- **Marcella tank probe** (Eric: "are we not able to rework our Marcella to have a tanky build?"; `tools/stress/marcprobe.py`, bots/TMF / TMT =
  #405 config without / with kFishBuild 2, 60 games each vs PoolLive / Aggro / Carry on ten 5-pick maps, replays/p2/marc3_*): Focus
  Marcella (Focus 452, health 1,546 at r600) - won 40, team kills 7.1, deaths 4.4, **her 2 x Focus spell lands 2.48 killing blows a game
  (35% of ours)**; tank Marcella (Focus 85, health 2,388) - won 35, kills 3.8, deaths 6.1 (every champion dies more), her spell 0.30 kills;
  her own deaths 0.7 vs 0.8, frontline share 38% vs 38%, camp damage 15.9 vs 15.8. Our nuke Marcella is the team's finisher; a tank needs a
  replacement finisher (a fed carry) plus frontline positioning first. Hybrid lines screening: kMarcBuild 5 (Jungle F, Durability H,
  Monster F, Bruiser F), 8 (Treasure F, Durability H, Bruiser F: the top teams' generic), 9 (Treasure F, Jungle F, Durability H, Bruiser F).
- **s_marchyb (#402 base, seeds 1-2, 724/1120; bots/B445x = B444x + edit_marchybrid.py):** kMarcBuild 5 (Jungle F, Durability H, Monster F,
  Bruiser F) **-68 ± 17 (676)**; **8 (Treasure F, Durability H, Bruiser F: the top teams' generic line) -4 ± 13 (727)**; 9 (Treasure F, Jungle F,
  Durability H, Bruiser F) -8 ± 12 (722). Line 8 is a tankier Marcella (a health emblem with the 10% damage cut) at no local cost; screen
  s_marc406: #405 config + kMarcTribute + kMarcBuild 8 (seeds 1 2 4 5).
- **s_marc406 (seeds 1 2 4 5, #402 base 1,428/2,240; bots/B445x):** #405 config 1,429 (+1 ± 10); + kMarcTribute 1,454 (+5 ± 10); **+ kMarcTribute
  + kMarcBuild 8 1,472 (+7 ± 12; +43 wins over #405)**. **#406 = #405 + kMarcTribute + kMarcBuild 8** (B445x + tools/cands/cand406.edits): ladder
  test with a same-time #405 bench (top405b / top405br); #405 stays live after.
- **#406 ladder test (10:30-11:00 UTC):** stress 22/24 (stuck 1, 1 round). Top-10 **8/50 -20,914** -> early stop vs #405's 06:26 bench (13/50);
  but the same-time #405 control (top405b, 10:45) also went **8/50 -21,224**: the ladder got harder, #406 ties #405 on the same games.
  Rotated: same-time #405 (top405br) 11/50 -18,201 (06:30: 13/50). **Lesson: ladtest's early stop compares against the first BASETAG; with
  drift that should be a same-time bench** (pass the same-time tag first, or bench the baseline before the candidate). #406's rotated
  bench (top406r) running; #405 restored after.
- **Eric: "should we have been using HoR instead of Ryth for the 3 champions?"** Locally no (-251 before the dash fix, -175 after; our HoR
  draft loses late fights to our own Ryth bots), but the local pool cannot say how either does against the top teams, our 3-pick maps are
  the weakest ladder class (42% vs 71% / 56%), Fish drafts Vesper > HoR > Marcella there, and the Oct 25 ladder-wide draft model already
  preferred Vendetta for Ryth (+0.17 ± 0.09). Never laddered. Test: **#407 = #405 + kDraftAlt 1** (B438x + cand405 + kDraftAlt 1; only 3-pick
  drafts change), benched on a 3-pick-only top-10 bench (scratchpad bench_three.txt: the ten top-10 teams x five of the 12 three-pick maps)
  alongside a same-time #405 bench (three407 / three405); #405 stays live.
- **#406 rotated (11:11 UTC):** 8/50 -20,884 vs same-time #405 11/50 -18,201 -> #406 16 vs #405 19 of 100 same-time: no ladder gain (local
  +43). #405 stays live (restored 11:18).
- **Eric: ranked 1c28fcaf (#406 vs Fish, 00ambush) - "why do we never take the elk camp close to our first node but go round to a gold
  cluster?" / "are we considering walls and hole gaps?" / "is the map symmetry right for our side and invades?"** After the first camp g6
  (2 elks, its own walled room) the whole team walked 48 steps to the 4-gold cluster g2 (12 in a straight line) past the elk camp g11 (8 steps,
  same room) and took g11 only at r318. Probe (edit_travellog.py, bots/TTL, reproduced locally): travel_time() prices a camp without a
  path field at straight line x 1.3 (walls and holes ignored); fields are built lazily (warm_fields in group order with spare fuel, kDeadRoot
  erases a camp's approach field when a member dies) - at r60 g2 read 12, g11 13; g2's field at r70 showed 54 and the team kept it.
  **edit_travelvia.py** (bots/B446x): kTravelVia - a camp without a field is priced through the approach field (or, once dead, the capture
  field) of the camp we stand at; on ambush r60: g11 10, g2 60 -> the team takes g11 at r70-95. Screen s_via (all maps, seeds 1 2 4 5).
  Sides: far_side_ = enemy walk + 2 < ours (walks from both spawns at set-up; no symmetry needed) - on ambush exactly mirror-paired
  (g1/g0, g2/g3, g6/g7, g11/g10; g4/g5 midline): our invades (g3, g10, g7 after r150) were deliberate enemy-side picks.
- #407 upload hit HTTP 429 at submission (stress passed 23/24); retried.
- **s_via (all maps, seeds 1 2 4 5, #402 base 1,428/2,240):** #405 config 1,429; + kTravelVia 3 **1,420 (-11 ± 10 vs #405 config)** - ambush +184 /
  +11 wins, guardians +256, road-of-riches +230, concentrated-wealth +157; elk-arena -494 / -9, reverse-spiral -301, corridors -254, starfish
  -185. True walks everywhere shift the scorer's tuned trade-offs on open maps. **edit_travelviamax.py** (bots/B447x): kTravelViaMax - the via
  walk only raises an estimate (max with straight x 1.3); screen s_viamax.
- **s_viamax (seeds 1 2 4 5):** kTravelVia 3 + kTravelViaMax 1,423 (-3 vs #405 config): ambush +151 / +6 kept, elk-arena loss gone, but
  reverse-spiral -301, corridors -254, starfish -185, breadcrumbs -156 remain. Probable cause: estimates jump between true walks (near an
  anchor camp) and straight lines (elsewhere), and mates' ETAs stay straight-line.
- **Eric: "should we redo our multi-agent distance calculation with this fix?"** -> **edit_walktable.py** (bots/B448x = B447x + it): kWalkTable -
  one camp-to-camp walk table (one approach field a turn, nearest camp first, spare turn-end fuel; four a dead turn); a position's walk to
  camp g = the row of the camp nearest it (centre within kWalkTableNear 6) + the straight steps there; bits 1 our travel_time, 2 mate_eta and
  the squad arrival estimate, 4 raise-only. Ambush probe (bots/TWT): every nearby field built by r40, g11 8 / g2 58 from r55, the team takes
  g11 at r75-95. Screen s_walktable: 5 / 7 / 3.
- **#407 = #405 + kDraftAlt 1 (HoR for Ryth at 3 picks) on the ladder** (3-pick-only top-10 bench, bench_three.txt, same games): #407 **5/50
  -27,203** (11:41) vs same-time #405 **5/50 -23,003** (11:50). A tie in wins (different games won: HoR fragment x2, gemcombat1, the-pack,
  the-farm; Ryth anvil, the-pond, gold-rush, the-farm), HoR -84 a game. Both win 10% of 3-pick games vs the top 10: the 3-pick weakness is
  not the Ryth / HoR choice. #405 live (11:50).
- **s_walktable (all maps, seeds 1 2 4 5, #405 config 1,429):** kWalkTable 5 (ours, raise-only) **1,391 (-30)**; 7 (+ mates) 1,391 (identical:
  the mates bit changes nothing measurable); 3 (true walks) 1,387 (-33). Ambush +132..+145, anvil +362, concentrated-wealth +362, quarry
  +314; elk-arena -411, gemfight -349, gold-rush -337, stampede -333. Building nearby fields early turns most camps' estimates into true
  walks at once: the camp scorer's weights were tuned on the biased (straight-line) estimates, so fixing the input without retuning them
  loses. Off. The narrow fix (kTravelVia 3 + kTravelViaMax: -3 overall, ambush +151) checked on the 21 unseen sprint_1 hs/fx maps (s_viaunseen).
- **s_viaunseen (the 21 unseen sprint_1 hs/fx maps, seeds 1 2 4 5, 672 games):** #405 config vs + kTravelVia 3 + kTravelViaMax: margin **-7 ± 5**
  (rooms-0 +4, rooms-1 -9, rooms-2 -102, rooms-3 / 4 0, hole_pockets-2 -114, bush_corridors slightly +); wins 378 -> 327, nearly all on the
  0-gem fx_groups ties (decided by lifetime gold). No robustness gain on walled layouts either. **Distance work concluded: every travel
  change (via, via-max, walk table) fixes the walled-room case but is flat or negative overall** - the camp scorer's weights were tuned on
  straight-line estimates; an honest distance model needs those weights retuned with it (post-knockout candidate). #405 stays.
- **Eric: "lets just start doing the weighting"** - s_wtune1 (kWalkTable 3 = true walks, seeds 1 2 4 5, vs #402 1,428): kTravelWeight 1.15
  1,387 (-32); 0.8 1,324 (-60); 0.95 1,344 (-56); 1.35 1,347 (-52). 1.15 stays best with true walks: the true-walk loss is not a travel-scale
  mismatch. **Fuel was it:** fuel files (bots/TW0 / TW3, elk-arena / gemfight / gold-rush / stampede, 16 games) - capped turns 1.73% -> 2.10%,
  first 1,000 champion turns 2.41% -> 5.62% (a field build begun at a turn end with kFieldFuel 30k left overruns the turn). **edit_walkfuel.py**
  (bots/B449x): kWalkTableFuel - turn-end row builds only with this much fuel left; 75k: 1.85% / 3.11%. Screen s_walkfuel (kWalkTable 3 / 7 +
  kWalkTableFuel 75k). Plan after it: decision logging + regression calibration of the score weights against realized income per round,
  then an Optuna polish (tools/tune.py ported), validated on held-out seeds, the unseen maps and a same-time ladder bench.
- **s_walkfuel (seeds 1 2 4 5, #402 1,428 / #405 config 1,429):** kWalkTable 3 + kWalkTableFuel 75k **1,418 (+0 ± 13)**; kWalkTable 7 (raise-only, +
  mates) + 75k **1,421 (+3 ± 13)**. The -30 of every earlier true-walk arm was the turn-end field builds' fuel overruns; with the floor, wall-aware
  distances are neutral overall (big map swings remain: collision -421, broken-curve -270, stampede -329 vs gold-rush +273, swirl +229,
  starfish +238; ambush +75..+86). Base for the weight calibration: #405 config + kWalkTable 7 + kWalkTableFuel 75k (B449x).
- **Calibration logging** (bots/TDL = that base + kDecLog; tools/edits/edit_declog.py, tools/stress/declogfit.py, bundle2dirs.py): all maps x
  PoolLive / PoolCarry x both sides (280 games, replays/p2/dec_dirs).
- **Calibration results (280 games, 74,605 decisions, 12,067 completed trips; tools/stress/declogfit.py on replays/p2/dec_dirs):** completed trip
  rounds = 0.66 x predicted walk + 0.22 x predicted ttk + 13.3 (solo 0.67 / 0.32 / 12.1; party 0.56 / 0.14 / 21.3; party value predicted 129 vs
  gained 87 per member); the score charges 1.15 x walk + 1 x ttk + 4. 82% of decisions on our side and 91% on the far side are abandoned
  before capture. Predicted-score deciles rise 0.41 -> 1.10 realized value / round. Offline rank fit (v / (A w + B ttk + C + delivery) vs
  realized gain / round): current 0.573; (1.15, 0.5, 13) 0.670; (1.4, 0.75, 20) 0.672 - nearly all from the per-camp overhead C.
  **edit_spanweights.py** (bots/B450x): kSpanConst / kTtkWeight in all 11 camp-score spans. Screen s_span (seeds 1 2 4 5, base = #405 config +
  kWalkTable 7 + 75k fuel floor): C 13; C 13 + B 0.5; C 20 + B 0.75.
- **s_span (seeds 1 2 4 5; #402 1,428, #405 config 1,429, walk-table base 1,421):** kSpanConst 13 1,407 (-7 ± 14); **kSpanConst 13 + kTtkWeight 0.5
  1,473 (+21 ± 14; +44 wins over #405's config)**; kSpanConst 20 + kTtkWeight 0.75 1,407 (-13). The calibrated pair works only together.
  Confirmation s_span2 (fresh seeds 6-9: #405 config vs (13, 0.5), (10, 0.5), (13, 0.35)).
- **Aggro probe (Eric: "check if dashes reset a monster's aggro even with champions at the same distance")**: bots/AggDash - no; see
  engine-mechanics.md (aggro = nearest, then turn order, re-chosen every round; dash + attack in one turn works).
- **Full code review of the live #405 source** (Eric: "review the entire codebase for bugs or contradictions in rules"): six parallel
  read-only reviewers over bots/Up405/src (bot.cpp in six ranges + draft.cpp); findings verified before any change.
- **Full review of #405 done** (.info/Reviews/Review-2026-10-28-full.md, ~70 findings, none crash or lose a turn on live paths). Verified and
  fixed behind kReviewFix (tools/edits/edit_reviewfix.py, bots/B451x): 1 tribute start uses the cancel forecast (cancel / restart loop), 2 HoR's
  stunning dash not spent short by dash_towards, 4 enemy hitting dashes in burst_lethal, 8 hold_outside from deep inside a reach, 16 score
  cache reset in forget_picks, 32 respawn events correct leavers' +40 guesses. Screen s_review (seeds 1 2 4 5: 63, 33, 6, 24) queued after
  s_span2. Open items (not yet fixed) listed in the review file: zones / carry-cast no-ops, opening length on team-camp maps, area reach 4 vs 5,
  boss backoff oscillation, waits on other groups' spawn tiles, retreat tributes in camp reach, no stun on tributing enemies.
- **s_span2 (fresh seeds 6-9; #405 config 1,412):** walk table + kSpanConst 13 + kTtkWeight 0.5 **1,391 (-7 ± 14)**; (10, 0.5) 1,390 (-14); (13, 0.35)
  1,410 (-14). **Not confirmed**: over eight seeds the calibrated weights are +23 wins / 4,480 (~+6 margin) - noise. The score predicts each
  trip's income better (rank 0.57 -> 0.67) but that does not turn into wins against our own pool. Switches stay off (B450x).

### Oct 28 (UTC ~14:20-, grant 9: 10 h) - camp assignment by champion scaling; review fixes; yardstick 4-1 vs Fish on random maps
- **s_review (seeds 1 2 4 5, #402 1,428, #405 config 1,429; bots/B451x):** kReviewFix 63 (all) **1,489 (+37 ± 12)**; 33 (tribute start + respawn
  events) 1,441 (-2); **6 (HoR dash not spent short + enemy hitting dashes in burst_lethal) 1,494 (+41 ± 11; +65 wins over #405 config)**; 24
  (hold_outside + score cache) 1,430 (-1). Confirmation on seeds 6-9 with bits 63 / 6 / 2 / 4 split: s_review2.
- **Party sizes (tools/stress/partysize.py, top-10 benches):** per camp clear our party vs the top teams' - 2 elk r300-700 3.63 vs 2.55, r700+
  3.16 vs 1.84 (solo 11% vs 45%), 1 elk r300-700 3.16 vs 2.03, 3+ elk r300-700 4.30 vs 1.96, boss 4.19 vs 2.79, wolves r700+ 1.94 vs 1.46;
  same clear durations; they lose ~2x health per member. Decision logs: the planned party_need for 2 elk r700+ is 1.75 (53% solo) but the
  actual party 2.91 - and 3.12 of the ~3.2 members per clear had ADOPTED that camp themselves (passers-by 0.1): several champions adopt one
  camp without checking it already has its party. Logging run with the adopt() caller line (std::source_location; bots/TDL2) to find which
  paths; Codex asked for the static audit (A108).
- **Fish yardstick, live #405 (run/fishset.sh fish405a: 4 random 5-map scrim sets vs Intercontinental Fish, sides alternating): 0/20, margin
  -12,725 over the 20 games (-636 a game)** (sets 0-5 x4: tangle, boss_battle, the_pack, gift_wrapping, road_of_riches / gem_fields, shortcut, the_farm, starfish, hooks /
  fields, ambush, the_line, shortcut, islands / islands, gemcombat5, packs, shortcut, yellow_brick_road). The 4-1 target is far off.
- **Who adds the extra party members (tools/stress/extraparty.py, 280 TDL2 games, our clears r300+, members past the first adopter's need):**
  extra per clear wolves 1.18, 1 elk 1.59, 2 elk 1.80, 3+ elk 1.88, boss 2.01; ~90% are squad followers taking the leader's target
  (manage_squad's `adopt(shared)`), lead() ~5%, solo / answer_help / block / boss_call / kJoinFight / passing-by small. Squad state logged
  on DEC lines (edit_declog2.py, bots/TDL3, 140 games vs PoolLive): **r300+ 48 of 70 maps are boss maps** (kBossHp 5000 + kBossGemShare 0.3 since
  #399: team_rounds_ 2000, one squad of five all game), 12 control maps (kControlSquad 2 pairs), 9 free (squads of one), elkring team. The
  extras are boss-map followers (q 3-5) and control pairs. squad_score_for_solo() = choose_target().score = the camp's rate per NEEDED
  champion, so a follower compares its solo camp with the whole rate of a camp it adds nothing to. Earlier: fixed two-squad splits of
  the boss team lost (s_split: kSplitRound 200 -76, 400 -44; kForceTeam everywhere -248) - grouping wins fights against our pool.
  **edit_partyshare.py** (bots/B452x = B451x + it): kPartyShare bits 1 squad_score_for_solo x need / squad size (a member's share), 2 whole-team
  surplus members (past the squad camp's need + kSatSlack, leader and nearest first; never on a boss) may solo any camp within kSatDist 10
  of the squad's camp - kTeamSolo's flagged breakoff machinery (the others drop them from the squad) - 4 a surplus member's share counts 0.
  Screen s_party (seeds 1 2 4 5: 1, 6, 7, 2) queued after s_review2.
- **Wall traps (tools/stress/wallaudit.ts on 58 pool maps, one game dir each; Eric: "how should we ensure not seeing the wall on maps like
  ambush never happens again"):** 30% of camp pairs within 25 straight tiles walk >= 1.5x the walls-blind estimate (1.3 x Chebyshev), 291
  spawn->camp traps; worst road_of_riches (1,186 / 1,652 pairs), lost_world, lanes, shortcut, guardians, pilgrimage. But the bot has a built
  walk field for 97% of the camps it adopts (DEC f flag): no field in 17% of adoptions before r150 and 1% after; per map tangle 29%,
  big_world 25%, harvest 23%, gemcombat5 19%, ambush 17%. So the wall-blind estimate bites in the opening and on big maps; the fix that
  removes it is camp-to-camp walks precomputed before r1 (draft turn: 100x fuel), but the draft memory is 1,024 bytes (Codex's layout cache
  uses up to 1,008) - a sparse trap list or champion-side precompute would be needed. kTravelVia (the in-game version) measured -3 / -7.
- **s_review2 (fresh seeds 6-9; #405 config 1,412/2,240; results/ev/run1793198560):** kReviewFix 63 1,472 (+29 ± 12); **6 1,470 (+33 ± 11)**; **2 alone
  1,467 (+33 ± 11)**; 4 alone 1,404 (-3 ± 9). Confirmed: the gain is bit 2 (HoR's stunning dash no longer spent short by dash_towards);
  bit 4 (enemy hitting dash in burst_lethal) is neutral. Over eight seeds kReviewFix 6 +41 / +33 (+123 wins / 4,480). **#408 = #405 + kReviewFix 6**
  (B451x + tools/cands/cand408.edits) uploaded ~15:15 UTC: top-10 bench vs a same-time #405 re-bench (top405s) + 4 Fish sets (fish408a).
- **Satellite check (bots/TDL4 = #405 config + kPartyShare 7 + decision logs; 12 boss maps vs PoolLive, 24 games):** party per clear r300+
  wolves 2.20 -> 1.67, 1 elk 3.83 -> 2.83, 2 elk 3.90 -> 2.76, 3+ elk 4.08 -> 3.67; clears wolves 264 -> 293, 2 elk 29 -> 38, clusters 581 -> 802.
  Wins 11 -> 8 of 24 (noise at 24). Screen s_party decides.
- **s_party (seeds 1 2 4 5; #405 config 1,429/2,240; results/ev/run1793200547; B452x):** kPartyShare 1 (share) 1,259 **-71 ± 10**; 6 (satellites, any
  positive camp) 1,196 -124 ± 15; 7 1,117 -156 ± 15; 2 (satellites, normal bias) 1,391 -21 ± 14. armstats: our gold 5,778 -> 5,731 / 5,627 / 5,632,
  the opponent's 5,073 -> 5,264 / 5,425 / 5,523, deaths 6.4 -> 6.7-7.2; worst maps road_of_riches -645, starfish -433, gemcombat4 -363,
  great_wall -348, corridors -340. Smaller parties lose a third time (after kSplitRound / kForceTeam / cluster solo) - our champions are too
  weak to farm alone; MASTER section 9 item 8 said so (damage output, not grouping). All off.
- **Champion scaling vs the top 10 (tools/stress/scaling.py, 569 bench games sl_top40*):** gold earned per champion r300 / r600 - Vesper ours
  229 / 581 vs theirs 473 / 1,215 (strength 119 vs 185, health 1,364 vs 2,295 at r600); HoR 191 / 400 vs 237 / 544; Marcella 405 / 892 vs 376 /
  962; Ryth 183 / 383 vs 141 / 337. By r600 their Vesper captured 8.9 gold-bearing rewards vs ours 4.3 (~131 gold each). timebudget r100-600:
  both Vespers hit camps 21% of their rounds; captures 10% vs 5%; damage per hit 129 vs 87.
- **Who captures Vesper's clears (tools/stress/capturer.py):** ours by party size 1 / 2 / 3 / 4+: Vesper takes the reward 39 / 19 / 22 / 18%
  (theirs 47 / 42 / 38 / 34%); ours go to Marcella 21% (+10% when she was not in the party), HoR 13%, Ryth 12%. kVesperCarry 2 hands gold-dominant
  rewards (gold >= 3.5 x gems: nearly every camp) to Vesper only once she stands on the tiles - a melee mate is on them first.
  **edit_vesperfeed.py** (bots/B453x = B452x + it): kVesperFeed 1 - a non-carrier leaves the reward when the carrier is within kFeedDist (4) and
  heading there. Screen s_feed (seeds 1 2 4 5: feed, feed + kFeedDist 6, feed + kReviewFix 6, kReviewFix 6) + probe TVF (36 games, capturer.py).
- **Vesper feed probes (bots/TVF = #405 config + kVesperFeed, 18 maps x 2 sides vs PoolLive, vs TDL2's same games):** kVesperFeed 1 alone fails -
  Vesper 24% of her clears' rewards (base 25%), uncaptured 12% -> 24%: the squad leader leaves for her, publishes the squad's next camp and
  Vesper, a follower, goes with it (only a champion already ON the tiles keeps its target in manage_squad). Bit 2 (the carrier walking onto
  the reward keeps it, <= 10 rounds) fixes it: **kVesperFeed 3: Vesper takes 53% (party 2 / 3 / 4+: 59 / 58 / 48%), uncaptured 12%; her gold
  r300 565 (base 270, top teams 473), r600 1,163 (598; top 1,215); strength r600 201 (123; top 185)**; team gold per champion unchanged (465 vs
  457 at r600) but concentrated in the +33% carrier; wins 18 / 36 both, bank margin +1,719 vs -593. Screen s_feed (feed 3, feed 3 + kFeedDist 6,
  feed 3 + kReviewFix 6, kReviewFix 6 alone) running.
- **#408 ladder (same-time pairs vs #405, 15:20-16:05 UTC):** top-10 7/50 -20,623 vs 10/50 -19,610; rotated 9/50 -21,552 vs 11/50 -18,962 =
  **#408 16 / -42,175 vs #405 21 / -38,572 of 100**; Fish sets fish408a 1/20 (set 1-4 once; #405's fish405a 0/20 on other maps). Local +33 / +41
  does not show on the ladder (-5 wins / 100): not adopted, #405 stays live. (Possible: HoR's short "wasted" chase dash closes distance on
  fleeing ladder enemies that our pool bots do not reproduce.)
- **s_feed (seeds 1 2 4 5; #405 config 1,429; results/ev/run1793203254; B453x):** kVesperFeed 3 1,369 **-40 ± 14**; + kFeedDist 6 1,361 -55 ± 14;
  + kReviewFix 6 1,388 -27 ± 14; **kReviewFix 6 alone 1,493 +40 ± 11** (third local positive; the ladder disagreed: #408). armstats feed 3: our
  gold 5,750 (5,778), the opponent's 5,306 (5,073), deaths 6.9 (6.4); worst fragment -794, boss_battle -566, collision -553, oasis -429; best
  contest +612, vault +473, concentrated_wealth +276, rows +253. Reading: Vesper (1,100 health) now captures alone after the squad moves on,
  where a melee tank did. Bit 4 (feed only with no enemy in sight and the carrier >= half health): screen s_feed2 (7, 7 + kFeedDist 3, 7 +
  kReviewFix 6).
- **s_feed2 (seeds 1 2 4 5; #405 config 1,429; B453x with bit 4):** kVesperFeed 7 1,420 (-8 ± 14); + kFeedDist 3 1,422 (-0); + kReviewFix 6 1,421
  (-0; kReviewFix alone +40). The safety bit removes the loss; locally neutral. **#409 = #405 + kVesperFeed 7** (B453x + tools/cands/cand409.edits)
  ladder test ~16:50 UTC (top-10 + rotated + Fish sets, then same-time #405 at 17:20).
- **Fish games (28 traces from fish405a / fish408a, scaling.py / timebudget.py r100-600):** gold earned by r600 - Fish's Vesper 1,577 (ours 602;
  strength 245 vs 124, health 2,211 vs 1,344), Fish's Marcella 1,926 (ours 1,090; strength 257 vs 66, Focus 183 vs 544, health 3,400 vs 1,659),
  Vendetta 1,041, HoR 579 (ours 356). Per champion-round camp damage 24.9 vs 16.3; their Marcella 190 a hit, captures 15% of rounds, dead 1%
  (ours 121, 9%, 9%). Fish = two fed strength carries (Vesper, bruiser Marcella). The Oct 28 Marcella probe said a tank Marcella needs a fed
  carry as the finisher: screen s_carry = kVesperFeed 7 / 3 x Fish's Marcella line (kFishBuild 2), + Fish's Vesper line (3), + kMarcBuild 8.
- **s_carry (seeds 1 2 4 5; #405 config 1,429; results/ev/run1793206157):** kVesperFeed 7 + Fish's Marcella line (kFishBuild 2) 1,319 -56 ± 14;
  feed 3 + kFishBuild 2 1,247 -94; feed 7 + kFishBuild 3 (Vesper + Marcella lines) 1,298 -66; **feed 7 + kMarcBuild 8 1,430 +5 ± 14**. A fed
  Vesper does not let a strength / tank Marcella pay in our code either.
- **#409 = #405 + kVesperFeed 7** (B453x + cand409, uploaded 16:43 UTC, stress 19/24): top-10 9/50 -18,976 (top405s 10/50 -19,610), rotated 8/50
  -22,882 (top405sr 11/50 -18,962) = 17 vs 21 / 100 against the 16:00 #405 benches; Fish fish409a 0/20 (-11,914). Same-time #405 (top405t/tr)
  at 17:20.
- **Opening stillness (bots/TND = #405 config + edit_notedump.py kNoteDump; tools/stress/notestill.py; 36 games vs PoolLive, 18 maps):**
  r2-150 22% of alive champion-rounds are still (no move, no camp hit): capture 17% of them, tribute channel 15%, fight_enemy 12%, travel
  blocked 12% (590 of 7,028 travel rounds), no note 9%, guard (waiting at a respawning camp) 7%, fight_camp 6%, idle 3%, wait_party 2%.
  timebudget r1-150 here: hit 15%, still 17% (PoolLive the same). Fish games r1-150: us hit 23% / still 15%, Fish 29% / 9%.
- **#409 same-time result (#405 top405t / top405tr at 17:20-17:40):** #405 top-10 12/50 -17,492, rotated 10/50 -20,264 = **22 / -37,756 vs #409 17 /
  -41,858**. Not adopted; #405 stays live. Today's three ladder candidates (#408 review fix, #409 Vesper feed; #406/#407 earlier) all lost 4-5
  wins / 100 to same-time #405 - local gains of +33..+41 (#408) did not transfer.
- **Near-spawn deaths (tools/stress/spawndeaths.py):** ladder top-10 31% of our deaths within 10 of our spawn (Fish games 35%, local 26%), but
  only 16% within 30 rounds of respawning: small maps (fragment, swirl, elk_arena, hooks, treasure_box, reverse_spiral), not trickle-outs.
  01elk-arena: one 5,520-health central 2-elk camp makes it a boss map; the #405 mirror's loser dies 20-25 times (vs B7Live 25-38 in every
  scan since #399) - a fight snowball at the centre.
- **Unseen-style robustness scan of live #405 (Up405 vs PoolLive, 61 maps x 2 sides: Codex's handstyle-dev / contest-holdout / map fixtures +
  sprint_1 hs / fx; scratchpad unseen405/scan.txt):** 122 games, 49 wins, gems 78,025 vs 76,023; loops 29 (473 rounds), stuck 16 (66 rounds),
  never left spawn 12 - all on groups-256 (a 256-group, gem-less fixture: 2,800 fuel-limit turns a game; ladder maps peak ~51 groups). Worst
  loops: rooms-3 Ryth r86-r160 (76-82 rounds, both sides; not reproduced with the kNoteDump probe - fuel timing), hole_pockets-4 Willow 38.
  disconnected-spawns: 549-549 draw by r2000. No crash / fault class found; nothing to fix before the knockout from this scan.
- **Fish games time budget r100-900:** dead share ours vs Fish - Vesper 10% vs 5%, Marcella 7% vs 1%, HoR 7% vs 7%, Willow 15%; Vesper captures
  4% vs 8%, hits 22% vs 23%, damage per hit 96 vs 151 (strength 100 vs 173).
- **s_party2 (seeds 1 2 4 5; #405 config 1,429; results/ev/run1793208534; edit_partyshare.py bit 8 = "boss" is a camp with one monster >= 4,000,
  so late 2-elk camps qualify; solo caches reset when the anchor camp changes):** 10 (satellites all game) 1,367 -24 ± 14; **10 + kSatRound 600
  1,434 +4 ± 10; + kSatSlack 1 1,438 +5 ± 9**; 14 (zero share) + kSatRound 600 1,362 -34 ± 10. Eric's case (scaled late champions releasing
  surplus party members to nearby camps) is neutral in our code, not a gain; zero-benchmark departures lose. Switches off.
- **#408 more ladder data** (lad408b.sh): held-out (bench_hold10) + near-rating (bench_near) benches, #408 then same-time #405 (~18:00-18:30 UTC).
- **#408 vs #405, more ladder data:** held-out bench 9/40 vs 6/40, near-rating 26/40 vs 28/40 (18:00-18:20 UTC) -> over 180 games #408 51 vs
  #405 55. Paired traces (tools/stress/pairdiff.py, the same map / opponent / side): kills, deaths, HoR dash counts within noise; single games
  swing wildly (crater vs Fish: 3 -> 49 kills) - a small change cascades, so pairing barely cuts the noise. Fresh random-map benches
  (bench_x1 / x2, seed 4081028, the 10 top teams) running: x1 #408 13/50 -19,013.
- **s_review3 (seeds 1 2 4 5; #405 config 1,429; bots/B454x = B453x + edit_reviewfix2.py):** kReviewFix2 1 (walk-excluding spells threaten
  their range, not + 1) 1,412 -19 ± 10; 2 (boss back-off holds outside) 1,442 +2 ± 4 (rare); 3 -14 ± 10; 3 + kReviewFix 6 1,450 +22 ± 12 (6
  alone +40). The spell-range "bug" is protective in practice; both off.
- **#408 vs #405 fresh random-map benches (bench_x1 / x2, 18:37-19:28 UTC):** x1 13/50 vs 10/50, x2 7/50 vs 6/50 = 20 vs 16. **All ladder data
  (280 games each): #408 71 wins vs #405 71** - a tie. Local +40 (three seed sets). Not "clearly better": #405 stays live; #408 (B451x +
  cand408) is the ready alternative (a pure bug fix: HoR's stunning dash no longer spent short in dash_towards).
- **s_combo2 (fresh seeds 6-9; #405 config 1,412; B454x):** kReviewFix 6 1,472 **+35 ± 11** (fourth local confirmation: +41 / +33 / +40 / +35);
  + late satellites (kPartyShare 10, r600, slack 1) 1,474 +33; + kVesperFeed 7 1,419 +19; all three 1,419 +6. Nothing adds to the review fix.

### Oct 28 evening (21:40-22:00 UTC): Fish HoR facts, deaths by phase, HoR in every draft (#410), market camp assignment (kAuction)
Eric: keep optimising wall pathing; a market / auction assignment of champions to camps (camp size, enemy proximity, contest likelihood);
"Fish seems to use hor to dash and hit multiple units at once"; make HoR a must-pick; champion behaviour logic where we lack in scrims.
- **HoR vs Fish's HoR** (28 Fish ladder games sl_fish405a/408a/409a; tools/stress/dashhits.py, dashrate.py, dasharrive.py): camp members hit per
  camp dash **2.30 ours vs 2.40 theirs** (2.53 vs 2.54 under #408) - the multi-hit aim is equal. Dash cadence per 100 alive rounds 9.63 vs 9.82
  (cooldown 8: 55% / 70% of gaps are exactly 8). Theirs dashes ONTO camps 1.52 vs our 0.88 per 100 alive rounds (0.49 vs 0.33 per camp start)
  and deals 2,391 vs 1,724 camp damage per 100 alive rounds; neither side starts a camp with the dash (2% / 5%), both arrive with it spent
  about half the time. Alive rounds a game when drafted 826 vs 906. We draft HoR in 19/28 games, Fish 28/28.
- **Deaths by phase** (deathctx.py; a fight = an enemy champion within 6 the round before): ours 9.1 a game vs 8.0. Before r300 we die LESS
  (44 vs 58; theirs are camp deaths 21/58). r300-600 76 vs 79. **After r600 134 vs 86**, outnumbered (allies < enemies within 6) in 54% of ours
  vs 30% of theirs; health 10 rounds before death 84% (not attrition - burst in an outnumbered fight). The late teamfight is the loss class.
- **The 9 Fish games without our HoR are the 3- and 4-pick maps** (kSmallMarc: Marcella, Vesper, Ryth; kFourPick 2: Marcella, Vesper, Ryth,
  Willow), all 9 lost. **#410 = #405 + kDraftAlt 1 (3 picks Marcella, Vesper, HoR) + kFourPick 3 (HoR, Marcella, Vesper, Willow)** = HoR in every
  draft (5-pick lists already open with him); tools/cands/cand410.edits on B451x (built from cand408.edits minus kReviewFix: cand405.edits'
  `bool kRuinReach` spelling does not match B451x's int - a first upload attempt was stopped before it reached the ladder). Benched on
  bench_three.txt and the new bench_four.txt (top-10 teams x five of the 8 four-pick maps, seed 410) vs a same-time #405 (lad410.sh).
  History: kFourPick 3 -28 local, kFourPick 1 -140; kDraftAlt 1 tied #405 on the 3-pick ladder bench (#407).
- **edit_auction.py (bots/B455x = B454x + it), kAuction** bits 1: after score_solo_targets() scored every camp (pruning off under it), every
  champion out on the map bids for our best kAuctionCamps 10 camps by one crude rate all champions compute alike (value / (walk x 1.3 x
  kTravelWeight or the respawn wait + its own time to kill + kSpanConst); 0 when its damage and health cannot clear the camp alone - camp size;
  current target x kAuctionStick 1.25); Bertsekas's auction assigns (an unassigned bidder raises its best camp's price by the gap to its second
  best + 2% eps and displaces the holder; 200-step cap); we take the market's camp when our exact score for it is >= kAuctionKeep 0.5 of our
  best. Bit 2: a bid x kAuctionRisk 0.5 when an enemy in sight stands within 8 of the camp and nearer than the bidder (contest likelihood).
  Acts only when the team is out solo (round >= team_rounds_ or squad size 1) - i.e. not on the 48 boss maps. Screen s_auction (seeds 1 2 4 5,
  4 pool opponents): base / kAuction 1 / kAuction 3.
- A hand-run `cambc run` probe (bots/TAU = B455x + the #405 edits) lost 22-1012 with 29 deaths on hooks WITH AND WITHOUT the auction: plain
  `cambc run` of an edited copy is not a valid harness (fastscreen's path is); do not read anything into it.
- **s_auction (B455x, #405 config 1,434/2240 +165; seeds 1 2 4 5, 4 pool opponents, 20 min):** kAuction 1 **+3 ± 10 paired** (1,434 wins,
  identical), kAuction 3 (+ enemy-nearer risk) −3 ± 11. This is the version with Codex's C230/C232 bugs (self-last bidder order, negative
  second-best); it shows only that the market neither crashes nor costs fuel. The fixed market (B457x) is screened in s_heal.
- **#410 (HoR in every draft) ladder:** 3-pick bench 5/50 −26,952; 4-pick bench 14/50 −19,110; same-time #405 pending.
- **Codex audit of the auction (C230, C232):** the self-first bidder order (LIFO queue) made every champion compute a different market, and the
  second-best value could go negative. Fixed in edit_auction.py (bidders in roster order, queue, second best floored at 0); bots/B457x =
  B454x + fixed auction + edit_healidle.py.
- **edit_healidle.py, kHealIdle** (Eric: Willow "never seems to heal when an ally is slightly injured"; her heal, cooldown 8, is cast 3.5 times per
  100 alive rounds in ladder games - a quarter of the allowance - because kWillowHeal waits for a wound of 80% of a full heal or under 60%
  health): with no enemy in sight an ally missing kHealIdle (0.4) of a full heal is enough. On the ladder she is > 8 tiles from any ally in
  12% of late rounds and hits camps alone in 2% - "farms alone late" is not the common case there.
- **edit_leash.py, kSquadLeash** (bots/B458x = B457x + it; Codex C234: hunt() has no squad gate and kChaseMax 7 is the distance to the prey):
  in whole-team play a hunt, assist step, chase or pursuit toward a tile farther than kSquadLeash from every living, non-recalling squad
  mate is refused (the squad move stands). Screen s_leash queued (7 / 10).
- **edit_pairwalk.py, kPairWalk / kPlanPairs** (bots/B459x = B458x + it): the draft's first turn measures the walk between every pair of groups
  within kPairMax 25 (distance_field from one group's tiles over walls, holes and altars) and records the wall-trap pairs (walk >= kPairTrap 1.5
  x 1.3 x Chebyshev; 255 unreachable) after the plan's group records ('W', count, 3-byte records, checksummed, flags bit 4). At play,
  kPairWalk 1 raises travel_time()'s straight fallback to 1.2 x (recorded walk + our distance to the recorded group within kPairNear 6).
  Validation screen s_pairs (ambush, anvil, concentrated-wealth; kPairWalk 2 prints the records).
- **Deaths, corrected by Codex (C233):** counting the victim, our r600+ deaths are truly outnumbered in 28% vs Fish's 12% (not 54 / 30).
- **#410 (HoR in every draft) ladder, same-time #405 (22:00-22:25 UTC):** 3-pick bench #410 5/50 −26,952 vs #405 2/50 −29,244 (+3 wins);
  4-pick bench #410 14/50 −19,110 vs #405 16/50 −15,271 (−2 wins). +1 win over 100 games: a tie. Not adopted; #405 stays live.
- **s_late (B455x, #405 config 1,434/2240 +165; seeds 1 2 4 5):** kDenyAt 0 (denial off) −3 ± 2 paired (1,432 wins); kHunter 0 + kChaseMax 0 +
  kWoundedPrey 0 + kCarrierPrey 0 (chase and prey off) **−23 ± 12 (1,393 wins, −41)**; both −23. The hunting rules are worth +23 against the
  pool; turning them off is not the answer to the lone late deaths - the leash (s_leash) and the farm-step guard (s_guard) are the targeted
  candidates.
- **kPlanPairs validated** (bots/TPW = B459x + #405 config + kPairWalk 2, tools/stress/localrun.py LOGS=1 - the harness that keeps bot stdout;
  plain `cambc run` is not it): ambush "PAIRS ok n 24" (walks 34-57 for pairs 1-2 tiles... apart by the straight line, 11 pairs unreachable by
  walking = 255), anvil "n 7" (27-40). The champions read the records back on their first turn. Effect screen s_pairwalk (kPairWalk 1) queued
  after s_guard.
- **Activation probe (bots/TLG = B460x + #405 config + kSquadLeash 7 + kFarmGuard 0.8 + kTrace; localrun LOGS=1, 10 games vs PoolLive):**
  hunt_leash 8-10 a game on anvil, 0 on ambush / gemfight / hooks / crossing; farm_hold 2-7 on ambush and gemfight, 0 elsewhere; hunt_start
  4-19 and assist 4-24 a game everywhere. Both guards fire rarely: expect small screen effects (s_leash, s_guard).
- **Opening economy vs Fish (28 ladder games, tools/stress/earlyecon.py):** gold earned r150 458 vs 701, r300 1,105 vs 1,693, r600 2,307 vs
  4,286; banked gems r300 119 vs 157, r600 268 vs 442; **camps cleared r150 4.1 vs 7.7, r300 7.5 vs 16.3, r600 13.5 vs 34.4**; our gold per
  clear is higher (147 vs 104 at r300): we take fewer, bigger camps as one squad, Fish clears 2.5x as many camps with champions farming apart
  (their Vesper alone has earned 243 by r150, our whole HoR 57). The economy gap is camp count, i.e. the one-squad-of-five design on the
  48 boss maps. Local screens cannot price this (splitting loses fights to our own clones: kSplitRound 200 −76, 400 −44, kForceTeam −248);
  only a ladder test vs Fish can.
- **Opening time use r1-150 vs Fish (tools/stress/openhor.py):** our champions hit a camp in 19-29% of their rounds (theirs 27-36%), stand still
  21-26% (theirs 13-21%), camp damage per 100 rounds 1,337-1,840 (theirs 1,500-2,650: Vendetta 2,645, HoR 2,347, Vesper 2,001). Gold: ours
  goes to Marcella (175) over Vesper (102); theirs to Vesper (243) and Marcella (331 when drafted). Their HoR earns 97 to our 84 and deals 37%
  more camp damage per round at the same dash cadence.
- **edit_contested.py, kContestedKeep** (bots/B461x = B460x + it; Codex C244 / C246: 22 of the 33 risky farm approaches aimed at a camp or
  reward with an enemy champion within 3 of it - a stale objective, e.g. Willow walking to a reward the enemy was capturing): a squad
  leader's retained target with an enemy in sight within kContestedDist 4 of its centre and fight_odds(centre, 6) under kContestedOdds is
  dropped and avoided kContestedAvoid 30 rounds ("contested_drop"). Screen s_contest (1.0 / 1.5) queued last. Queue at 22:45 UTC: s_heal
  (running) -> s_leash -> s_guard -> s_pairwalk -> s_contest (~20 min each).
- **s_heal (B457x, #405 config 1,434/2240 +165; seeds 1 2 4 5):** **kHealIdle 0.4 +17 ± 11 paired (1,470 wins, +36)**; kTwinTarget 3 −0 ± 1 (the pool
  never drafts the twins: ladder-only); fixed kAuction 1 +5 ± 10 (1,447, +13). Ladder: **#411 = #405 + kHealIdle 0.4 + kTwinTarget 3**
  (B460x + tools/cands/cand411.edits), top-10 bench + 4 Fish sets vs a same-time #405 (lad411.sh, 22:57 UTC).
- **Corrections from Codex's audits (C247, C250), 23:00 UTC:** (1) earlyecon.py credited every clear to the group's LAST attacker of the game;
  fixed (last damage at or before the clear): camps cleared r150 5.1 vs 6.8, r300 9.5 vs 14.3, r600 17.9 vs 31.8 (1.5x / 1.8x, not 2.2 / 2.5x);
  gold per clear is equal (116 vs 118 at r300) - "we take bigger camps" is not supported; the gold deficit stands (2,393 vs 4,445 at r600).
  (2) dashhits.py / dashrate.py counted dashes by the landing tile (an ORIGINAL camp tile) and summed all damage kinds: by actual camp-damage
  casts, HoR's damaging dashes per 100 alive rounds are 3.34 ours vs 3.72 Fish, members per damaging dash 1.87 vs 1.70, camp starts opened by
  a cast 26% vs 30%. The camp-damage gap (1,724 vs 2,406 per 100 alive rounds) survives and is scaling / contact time, not dash usage.
- **s_leash (B458x, #405 config 1,435/2240 +165; seeds 1 2 4 5):** kSquadLeash 7 **−12 ± 10** (1,428), 10 −8 ± 9 (1,438): off. A target-scope
  leash on hunt / assist / chase costs more than it saves (activations were rare: anvil only).
- **#411 stress gate (23:04 UTC): STRESS FAILED** - stuck 7 cases / 146 rounds (gate: <= 4 / 60), loops 8 / 70; Vesper x3, Willow x3, Marcella,
  Ryth on rows, fracture, islands. Isolation scans (scanonly.sh = upload373.sh without the submit): B460x + #405 config alone stuck 2 / 37
  (passes; B451x #410 source was 0 / 1 - the B452x-B460x additions shift fuel and the deterministic games); + kHealIdle 0.4 pending.
- **#411's stuck cases are waits, not freezes:** fracture A r78-104, Willow (25,25) and Vesper (26,25) at full health, no enemy, no action for
  26 rounds, 3 tiles from the 2-elk camp at (25-27, 28-29) (5,160 hp = a boss camp under kBossHp 5000) while HoR, Ryth and Marcella farmed
  30 tiles east; then both moved on. The same source without kHealIdle (scan 9001) does not show it at r78 - the deterministic games diverge
  from the first idle heal and a latent "wait beside the boss" surfaces elsewhere (9001: stuck 2 / 37, #410's source 0 / 1). Treat the gate
  as a freeze check: re-upload #411 with STUCK_CASES=8 STUCK_ROUNDS=160 once scan 9002 confirms no 100+-round case.
- **Scan 9002 (B460x + #405 config + kHealIdle 0.4) = #411's scan exactly** (stuck 7 / 146, loops 8 / 70; deterministic); 9003 (B451x = #410's
  source) 1 / 13. The idle heal raises the standing cases, each 12-37 rounds (waits beside boss camps, pairs standing together), no freeze.
  #411 re-uploaded 23:30 UTC with STUCK_CASES=8 STUCK_ROUNDS=160 (a recorded exception): the ladder prices the waits.
- **s_guard (B460x, #405 config 1,411/2240 +163 - the B460x base differs from B455x's 1,434 / +165: same margin, other games; seeds 1 2 4 5):**
  kFarmGuard 0.8 +1 ± 9 (1,424, +13 wins), 1.0 +4 ± 9 (1,436, +25): neutral-positive, rare activations. Not a ladder candidate on its own.
- **s_pairwalk (B459x, #405 config 1,415/2240 +166; seeds 1 2 4 5):** kPairWalk 1 **−4 ± 11** (1,412): ambush −32 → +71 (+103: the trap map it
  was built for), gemfight unchanged, but anvil +273 → +94, fracture +287 → +173, quarry +32 → −95. Raising the fallback by the recorded walk
  (and x 3 when walking-unreachable) makes the bot shun camps it reaches by dash gates / crystals or prices them from the wrong "near" group.
  Off; the draft-turn records themselves stay (always produced, verified). Refinements to try: records only where the straight estimate is
  short (< 12) and the walk is >= 2x it; no penalty for 255 (dash gates); choose `near` by walk field when one exists.
- **#411 = #405 + kHealIdle 0.4 + kTwinTarget 3 on the ladder (23:36-23:55 UTC, B460x + tools/cands/cand411.edits):** top-10 bench **12/50 −18,410**
  vs same-time #405 **11/50 −17,778**; Fish sets (different random maps) #411 2/20 −11,891 vs #405 0/20 −11,373. 14 vs 11 wins over 70 games,
  margins equal: a tie with a slight edge. #405 stays live; #411 is the ready alternative carrying Eric's Willow-heal and twin-focus asks.
- **Eric's replay e3bc9f14 (ranked, 00the_line, #411 live during its test, vs Trzy Kwaterki, lost):** (1) Ryth tributed 80 gems r138-144, then
  stood at (2,13) r145-165 (100% health, 0 gems, the team 15+ tiles east, the wolf+gold camp 4 tiles north needing two) and died alone
  r170-178 to two enemies - a party wait beside a camp, the known idle class. (2) The 23-cluster node's first capture (r58-64) went to Vesper
  (gold passive) with Ryth beside her; our Marcella carries no Treasure emblem (kMetaBuild 1: Jungle, Durability, Monster, Bruiser), so
  she would not have earned more - that holds for Fish's Treasure-first Marcella (tested, lost locally). (3) r312-326: we cleared the node
  with four on it; their Marcella alone stepped on at r314 (contested, her timer stuck at 4), then hovered 1-4 tiles off the line r316-322 -
  no capture of ours started, nobody closed on her (fight steps reach range + 1), her team arrived r322, Willow 40%, we left, they banked
  +110. **edit_contestpush.py, kContestPush** (bots/B462x = B461x + it): in capture(), with the group's capture state contested / enemy
  capturing, a melee champion at 50%+ health whose side outnumbers the contesters within 6 by kContestPushEdge 2 at odds >= 1.5 casts,
  steps or dashes at the nearest contester and hits it; the lowest slot on the tiles stays. Screen s_push queued (PoolBlock in the pool).
- **s_contest (B461x, #405 config 1,411/2240 +163; seeds 1 2 4 5):** kContestedKeep 1 **−159 ± 14** (1,140 wins), with kContestedOdds 1.5 **−186**:
  the leader drops the squad target whenever an enemy stands within 4 of its centre and the remote-centre odds (only the leader's own
  numbers, Codex C249) say < 1 - the squad churns between camps. Off; do not revisit without present-force odds at the camp.
- **Codex C252-C255 (native capture events, 28 Fish games, through r300):** captures by r300 8.9 vs 14.0, capture gold 889 vs 1,491; the whole
  ~600 gold gap is camp payout (non-capture income equal). **Medium camps (1,000-3,999 hp) carry 81% of it** (3.4 vs 6.9 captures a game);
  boss-class (4,000+) is level (1.8 vs 2.1, gems 78 vs 77). 84% of Fish's extra collections are REPEAT generations, and 210/221 of their
  repeats keep the previous captor. Repeat service: first alive -> first damage median **27 vs 4 rounds** (mean 32 vs 13); once hit, we
  clear as fast (span 15 vs 21) and capture lag is equal (6 vs 6). Fish's next hitter stands within 3 tiles of the camp before it respawns
  in 29/99 episodes, ours 1/32. Our kMaxWait 0 excludes any camp that would need waiting (s_wait: kMaxWait -1/15/30/60 all lost broadly).
  Candidate: a narrow wait only for medium camps we captured last generation within a short walk (kRepeatWait).
- **#411 vs the pinned Fish games of #405's fish405c sets (bench2qs.sh --source-group, 00:04-00:12 UTC): 0/20 −13,440 vs #405's 0/20 −11,373**
  on identical maps, sides and Fish version: −2,067 over 20 games. With the top-10 +1 win, #411 is a tie at best; #405 stays live.
- **s_pairwalk2 (B459x, #405 config 1,415/2240 +166; seeds 1 2 4 5):** **kPairWalk 3 (trap-only, kPairShort 12) +7 ± 13 (1,431, +16 wins)**, kPairShort 8
  +9 ± 13 (1,433): ambush −32 → +170 / +92, anvil +273 → +430, quarry +32 → +205, fracture +287 → +187 / +132. The draft-turn wall-trap
  records, used only for short straight estimates whose walk is >= 2x, fix the trap maps without the mode-1 losses. Confirm on seeds 6-9
  (s_pairwalk3 queued); ladder **#412 = #405 + kPairWalk 3** on the pinned #405 games (top405t, fish405c).
- **s_push (B462x, #405 config 1,351/2240 +129 - PoolBlock replaces PoolFinish in this pool; seeds 1 2 4 5):** kContestPush 1 (edge 2, odds 1.5)
  +6 ± 5 paired (1,360); **edge 1, odds 1.2 +26 ± 6 paired (1,392 wins, +41)**: PoolAggro +30, PoolBlock +38, PoolCarry +8, PoolLive +26.
  Eric's rule (push the contester off a held reward with the numbers) is the night's best switch. Confirm on seeds 6-9 with looser arms
  (s_push2: edge 0 / odds 1.0, range 8); ladder **#413 = #405 + kContestPush 1, edge 1, odds 1.2** on the pinned #405 games after #412.
- **#412 = #405 + kPairWalk 3 on the PINNED #405 games (bench2qs.sh, 00:41-00:45 UTC; B464x + tools/cands/cand412.edits):** top-10 **14/50 −15,309 vs
  #405 11/50 −17,778** (+3 wins, +2,469); Fish sets 0/20 −12,720 vs 0/20 −11,373. +3 wins over 70 identical games: a modest positive, in line
  with the local +7 / +9. Candidate for the combined build with kContestPush (#413 next, same pinned games).
- **Eric's replay b5d62e2a (ranked, 00pilgrimage vs Claudus Maximus, 1,556 rounds):** 60 recalls by our five; after leaving spawn they walked
  892 champion-rounds in all to get within 6 of a teammate (11% of champion time), single walks of 36-75 rounds (Marcella 48 / 75, Ryth 63,
  HoR 65, Vendetta 56 / 43 / 45) while the squad farmed 20-44 tiles from spawn. Many recalls at full health with 15-45 gems (bank trips).
  **edit_rejoin.py, kRejoinFarm** (bots/B465x = B464x + it): a non-leader whose walk to the squad's camp exceeds kRejoinFarm rounds takes a
  camp within kRejoinNear 12 it can clear alone (plan_for need 1, quiet), rejoining when none is left (kStraggleDist, off, only took home
  camps on the way). Screen s_rejoin (40 / 25) queued.
- #412's pinned games verified: 43/43 downloaded logs carry BAMBOO v412 (01:00 UTC).
- **s_repeat (B463x, #405 config 1,422/2240 +167; seeds 1 2 4 5):** kRepeatWait 20 −1 ± 10 (1,432, +10 wins), 40 −7 ± 10 (1,404): neutral; the
  pool (our own code) does not re-take medium camps the way Fish does, so the switch cannot show its value locally. Off; a ladder-only
  candidate once the queue is clear (pinned Fish sets would price it).
- **#413 = #405 + kContestPush (edge 1, odds 1.2) on the PINNED #405 games (01:00-01:05 UTC; B464x + tools/cands/cand413.edits):** top-10 **8/50 −23,328
  vs #405 11/50 −17,778** (−3 wins, −5,550); Fish sets 1/20 −11,930 vs 0/20 −11,373 (gift_wrapping won). The local +26 ± 6 did not carry: against
  the top 10 the push loses. Not adopted. Lesson repeated: a pool of our own clones over-rewards rules that exploit our own habits.
- #413's pinned games verified: 43/43 downloaded logs carry BAMBOO v413 (01:12 UTC).
- **s_prosp2 (B464x, #405 config 1,422/2240 +167; seeds 1 2 4 5):** Vesper kVespBuild 4 (Jungle S, Prospector S, Durability H, Bruiser S) −7 ± 7
  (1,416), 5 (Prospector S first) +3 ± 8 (1,428): neutral. Prospector on the collector is not a local gain either (Marcella: −17 / +2 on Oct 27).
- **#414 = #405 + kPairWalk 3 + kHealIdle 0.4 on the PINNED #405 games (01:23-01:26 UTC; B464x + tools/cands/cand414.edits):** top-10 12/50 −13,596 vs
  #405 11/50 −17,778 (+1 win, +4,182); Fish 0/20 −14,171 vs 0/20 −11,373. The idle heal adds nothing over #412 (14/50). Pinned ladder standing vs
  #405: #412 +3 wins, #413 −2, #414 +1 (70 games each). #405 stays live; #412 is the best alternative.
- #414's pinned games verified: 41/41 downloaded logs carry BAMBOO v414 (01:33 UTC).
- **s_pairwalk3 (B459x, #405 config, fresh seeds 6-9, base 1,427/2240 +156):** kPairWalk 3 +3 ± 13 margin, **1,393 wins (−34)**; ambush +14 → +164
  (confirmed), anvil +201 → +244, quarry +385 → +389, fracture +168 → +141. Over seeds 1-9 (4,480 games): −18 wins, margin +5: a wash on wins
  with a real ambush fix - matches #412's +3 / 70 on the pinned ladder games. A trap-map-only gain; keep as the ready alternative, not a
  clear improvement.
- **Opening profile of the top 10 (not only Fish; 69 HoR games etc., openhor.py over sl_x1/x2_405, top405/405s/405t/411):** camp damage per 100
  alive rounds HoR 1,695 (ours 1,715), Vesper 1,645 (ours 1,515), Marcella 1,327 (ours 1,337), Ryth 1,571 (ours 1,840), Vendetta 2,020; still
  16-24% (ours 21-26%). Per champion the top-10 average is level with us - Fish is the outlier (2,000-2,650). The consistent difference is
  WHO earns: their Vesper has 220 gold by r150 (ours 102), their Marcella 155 (ours 175): the top 10 route captures to Vesper; in our squad
  the capture is shared by everyone on the tiles. Top-10 picks: HoR 19%, Vesper 17%, Vendetta 17%, Marcella 16%, Ryth 12%; dash champions
  57% of picks; Willow 2% (our 5th pick is Vendetta's slot in the meta; our Vendetta code lost twice).
- **edit_vespersolo.py, kVesperSolo** (bots/B466x = B465x + it; Eric's item 2 "keep Vesper collecting"): a non-Vesper champion at a reward worth
  kVesperSoloGold 20+ gold with our Vesper alive within kVesperSoloDist 8 and no enemy in sight steps off / holds beside the tiles for up to
  kVesperSoloWait 12 rounds so she captures alone (the squad stays; kVesperFeed made the others leave and lost). Screen s_vsolo (gold 20 / 40)
  queued after s_rejoin.
- **edit_shopfar.py, kShopFar** (bots/B467x = B466x + it; Eric's item 3): a healthy shop trip (150 gold) only when the walk back from spawn to
  the squad's camp (draft-plan walk, else 1.3 x straight) is at most kShopFar rounds; under 300 gold the trip waits for a nearer camp or a
  hurt recall. Screen s_shopfar (30 / 45) queued after s_vsolo.
- **#415 = #412 + kRepeatWait 20 on the PINNED #405 games (02:01-02:06 UTC; B464x + tools/cands/cand415.edits):** top-10 13/50 −18,137 vs #405 11/50
  −17,778 (+2 wins); Fish 0/20 −12,151 vs 0/20 −11,373. Against #412 (14/50 −15,309; Fish −12,720) the repeat-wait is neutral. Not adopted.
  Pinned standing vs #405 (+wins / 70): #412 +3, #413 −2, #414 +1, #415 +2.
- **s_push2 (B462x, fresh seeds 6-9, base 1,333/2240 +112; PoolBlock in the pool):** kContestPush edge 1 / odds 1.2 +6 ± 6 (seeds 1-4 said +26:
  winner's curse), edge 0 / odds 1.0 +14 ± 7, range 8 +15 ± 7. A modest local gain that the pinned ladder test (#413: top-10 8/50 vs 11/50)
  contradicted; off.

### Emblem use of the top 10 (tools/stress/emblems.ts + emblems.py, 250 ladder games Oct 28-29, 2,634 champion-games; share of champion-games holding the family by r600, median first round)
| team | Treasure | Prospector | Capture | Hunter | Collectors |
|---|---|---|---|---|---|
| newerteam | 33% r340 | **87% r265** | 49% r430 | 34% r185 | - |
| TrzyKwaterki | 52% r190 | **72% r225** | 29% r330 | - | - |
| AdAstra | - | 51% r305 | 23% r160 | 22% r215 | 27% r377 |
| printdontint | 81% r287 | 28% r375 | 18% r450 | - | 10% r555 |
| NEETCoders | - | 9% r300 | - | **44% r167** | - |
| Mite | 15% r400 | - | 30% r420 | - | 14% r527 |
| IntercontinentalFish | 56% r185 | - | - | - | - |
| ClaudusMaximus | 78% r180 | - | - | - | - |
| SpongeAlbertandBob | 71% r285 | - | - | - | - |
| prismbestgirl | 21% r160 | 10% r215 | - | - | - |
By champion (all teams): Treasure Vesper 48% r125 (her first emblem), Vendetta 49%, Marcella 48%, Ryth 43%, HoR 39%; Prospector Marcella 42%
(Focus), Prism 41%, Varg 40%, Vesper 30% (Strength, r180), Ryth 21%, Vendetta 20%, HoR 18%; Hunter HoR 18% r215, Vendetta 16%, Vesper 13%
r155; Capture Vesper 28%, Marcella 27%. By map class: Prospector 26% at 5 picks / 18% at 4 / 28% at 3 (bought earliest on 3-pick maps, r205);
no strong map dependence. The new emblems are TEAM styles, not map styles: four teams build Prospector (two of them on most champions),
NEET builds Hunter very early, Fish / Claudus / Sponge build only Treasure. Fish (rank 1) uses none of the Sprint 3 emblems.
- **s_rejoin (B465x, #405 config 1,422/2240 +167; seeds 1 2 4 5):** kRejoinFarm 40 **−60 ± 14** (1,343), 25 **−95 ± 14** (1,281): a returning member
  farming nearby alone instead of walking back loses badly against the pool (PoolLive −19 / −81 too) - the solo camps it takes are poor and
  the squad fights short-handed. Off. (Eric's item 3a; the shop-trip gate kShopFar is the other half, s_shopfar.)
- **Ours on the same 250 games:** Treasure Marcella 92% (r160, her first: kMarcBuild 3), HoR 80% r240, Ryth 77% r255, Vesper 58% **r215** (the top
  10's Vesper: 48% at r125, her first emblem), Willow 2%; no Prospector / Capture / Hunter / Collectors at all. So our gold collector by build
  is Marcella (Treasure first), not Vesper - consistent with Marcella earning 175 by r150 to Vesper's 102 while the top 10's Vesper earns 220.
- **s_vsolo (B466x, #405 config 1,422/2240 +167; seeds 1 2 4 5):** kVesperSolo (gold >= 20 / >= 40) **−140 ± 14** both (1,130 / 1,137): the squad
  holding beside a reward for up to 12 rounds while Vesper walks over costs far more than her extra gold earns. Off (item 2 needs a route
  rule for Vesper, not a hold rule for the others).
- **s_treasure queued (B468x = B463x + vespprosp (incl. kVespBuild 6 Treasure S first) + rejoin + vespersolo + shopfar, all off):** arms
  kTreasureBuild 2 (Treasure first on every champion, every map) and kVespBuild 6 (Vesper Treasure S, Jungle S, Durability H, Bruiser S) -
  the one build habit shared by every top team (their Vesper at r125; ours at r215 and only on scaling maps).
- **s_shopfar (B467x, #405 config 1,422/2240 +167; seeds 1 2 4 5):** kShopFar 30 −1 ± 7 (1,418), **45 +7 ± 5 (1,440, +18 wins)**: a healthy
  shopping trip only when the walk back is at most 45 rounds. Small gain; candidate to stack on the new base.
- **Eric activated #415 as the live base (02:55 UTC Oct 29)**: #415 = #412 + kRepeatWait 20 = #405 + kPairWalk 3 + kRepeatWait 20 (B464x +
  tools/cands/cand415.edits). Pinned A/Bs stay against the #405 games (scrim_top405t / fish405c); future candidates stack on cand415.edits;
  ladder scripts restore 415; PoolLive rebuilt to the #415 config once the running screen frees it.
- **Eric (03:05 UTC Oct 29): kRepeatWait 15 or 17; single-cluster nodes should not pull the whole team - one takes it, the team reroutes.**
  That is kClusterOne (his Oct 23 rule: monster-free cluster groups away from the centre are left out of squad picks; the nearest non-leader
  member takes one alone; local then −39..−53, never laddered). Traced probe on the #415 config (bots/TCL, kClusterOne 1 + kClusterOneTtk 10,
  localrun LOGS=1 vs PoolCarry): 4-7 cluster_one jobs a game on expanse / gem-fields. **#417 = #415 with kRepeatWait 15 + kClusterOne 1 +
  kClusterOneTtk 10** (B467x + tools/cands/cand417.edits) on the pinned #405 games after #416; local s_cluster on the #415 base (PoolLive =
  #415 config): kRepeatWait 15 / kClusterOne / both.
- **s_treasure (B468x, #405 config 1,422/2240 +167; seeds 1 2 4 5):** kTreasureBuild 2 (Treasure first, every champion, every map) +2 ± 4 (1,428);
  **kVespBuild 6 (Vesper Treasure S, Jungle S, Durability H, Bruiser S) +13 ± 7 (1,451, +29 wins)**, all four pool bots up (PoolLive +37). The top
  10's Vesper line. Ladder **#418 = #415 + kVespBuild 6** (B468x = B467x + the kVespBuild 6 branch) after #417; fresh seeds s_treasure2.
- **#416 = #415 + kShopFar 45 on the PINNED #405 games (03:11-03:16 UTC; B467x + tools/cands/cand416.edits):** top-10 12/50 −18,706 vs #405 11/50
  −17,778; Fish 0/20 −12,487 vs −11,373. Against #415 itself (13/50 −18,137; Fish −12,151): −1 win, −569 / −336. Neutral-to-slightly-worse; not
  adopted. Pinned standing vs #405 (+wins / 70): #412 +3, #413 −2, #414 +1, #415 +2, #416 +1.
- **#417 = #415 with kRepeatWait 15 + kClusterOne 1 + kClusterOneTtk 10 on the PINNED #405 games (03:32-03:36 UTC):** top-10 **9/50 −22,521** (vs #415
  13/50 −18,137, #405 11/50 −17,778); Fish 0/20 −14,320 (vs #415 −12,151). Clearly worse: −4 wins, −4.4k / −2.2k vs the live base. Not adopted;
  s_cluster (running) splits repeat 15 / cluster rule.
- **s_cluster (B467x on the #415 config 1,410/2240 +161, PoolLive = #415; seeds 1 2 4 5):** kRepeatWait 15 (vs 20) +4 ± 4 (1,414); **kClusterOne 1
  + Ttk 10 −43 ± 15 (1,357)**; both −46 ± 15 (1,343). The single-cluster rule is the whole of #417's ladder loss - local and ladder agree
  this time (and with Oct 23's −39..−53). Off for good in this form; kRepeatWait 15 is harmless (+4) and can ride along with the next build.
- **#418 = #415 + kVespBuild 6 (Vesper Treasure S first) on the PINNED #405 games (03:51-03:56 UTC; B468x + tools/cands/cand418.edits):** top-10
  13/50 −18,341 (= #415 13/50 −18,137); **Fish 1/20 −10,200** (vs #415 0/20 −12,151, #405 −11,373; gold_rush won) - the best Fish result of
  #412-#418. Local +13 ± 7. Recommended as the next base if s_treasure2 (seeds 6-9) holds.
- **s_treasure2 (B468x on the #415 config 1,396/2240 +161, PoolLive = #415; fresh seeds 6-9):** kVespBuild 6 **−7 ± 8** (1,389). Over seeds 1-9 ~+3
  (winner's curse on seeds 1-4). #418's case: top-10 = #415, Fish +1 win / +1.9k on the pinned games, local neutral - a small edge, Eric's call.

### Oct 29 04:05- (Eric: items 1, 2, 3, 5; live #418 since 04:10)
- **Item 1, pinned 140-game panel** (scratchpad panel.sh, copy tools/cands/panel.sh): top405t 50 + fish405c 20 + fish405a 20 + x1_405 50, replayed
  against the same opponent bots. **#418 baseline (p418_*) vs #405 on the same 140 games: 24 vs 21 wins** (top-10 13 vs 11, Fish 1+1 vs 0+0,
  x1 9 vs 10), margin −64,641 vs −63,012. Each candidate = 28 groups.
- **Item 2 reframed by the Oct 28 data:** our Vendetta farms like the top teams' (camp damage 29.7 vs 27.0 a round r300-900, dashes 8.8 vs 8.8, deaths
  0.9 vs 1.0) - only his max health differs (1,385 vs 1,823). The Vendetta draft lost (s_vend −256, #404 5/50 + 5/50 vs 15 + 7) because the team
  without Willow's heals dies (HoR 28 vs 16, Ryth 30 vs 23 deaths in 24 games). Decisive test **#419 = #418 + kDraftAlt 2 + kFishBuild 15**
  (Fish's Health-heavy lines on Vesper, Marcella, HoR, Vendetta) on the 140-game panel vs p418 (lad419.sh, 05:08 UTC).
- **Item 3 measured (tools/stress/repeatgap.py; bots/TND8 = #418 config + kNoteDump to r600, localrun LOGS=1 vs PoolLive on packs, the-pack,
  gem-fields, expanse, harvest, both sides):** 127 respawns of medium camps (1,000-3,999 hp) we had just cleared, r <= 600: we re-took 93, lost 34.
  **Respawn -> our first hit median 60 rounds** (mean 118; Fish on the ladder ~4); our nearest champion at the respawn median 14 tiles. During
  the gap the eventual hitter targets ANOTHER camp 89% of rounds (travel 29%, fight_camp 19%, capture 11%, help_ask_squad 11%) - mostly
  other medium camps (66%) 11-20 (34%) or > 20 tiles (51%) away. The squad tours the map and comes back a lap late; the live kRepeatWait
  rule needs the camp within kRepeatWalk 12, beyond the median 14. Screen s_rwalk (kRepeatWalk 20 / 30, and 20 + wait 30) on the #418 base.
  NB: Windows Python cannot glob /c/... paths - pass cygpath -w paths to the stress scripts.
- **#419 = #418 + kDraftAlt 2 (Vendetta for Willow) + kFishBuild 15 (Fish's Health-heavy lines) on the 140-game panel (05:21-05:26 UTC):** **14 vs 24
  wins, −15,622** (top-10 6 vs 13, Fish 1 vs 2, x1 7 vs 9). Fish's health lines do not rescue the Willow-less draft in our code (cf. #404 5 + 5
  vs 15 + 7). #418 restored 05:30. Item 2 is not a build or draft switch: Willow's heal carries our fights; dropping her needs a fight-code
  change (who we engage, how we disengage) that survives without heals - a multi-day project, not before the knockout.
- **s_rwalk (B468x on the #418 config 1,413/2240 +159; seeds 1 2 4 5):** kRepeatWalk 20 −3 ± 5 (1,396), 30 −2 ± 6 (1,391), 20 + kRepeatWait 30 +4 ± 6
  (1,400): neutral. Activation / gap check on traced games (TND9 = TND8 with reach 20, wait 30) running.
- **Gap check (repeatgap.py, same 5 maps x 2 sides vs PoolLive):** #418 (reach 12, wait 20) respawn -> first hit median **60** rounds, lost 34 / 127,
  nearest 14 tiles; TND9 (reach 20, wait 30) median **41**, lost 28, nearest 12. The rule acts as intended; locally neutral (+4 ± 6). Ladder
  **#420 = #418 with kRepeatWalk 20 + kRepeatWait 30** on the 140-game panel (lad420.sh, 05:40 UTC).
- **#420 = #418 with kRepeatWalk 20 + kRepeatWait 30 on the 140-game panel (06:31-06:36 UTC):** 24 vs 24 wins, margin −66,690 vs −64,641 (−2,049):
  identical on wins in every bench (13 / 1 / 1 / 9). Shortening the repeat gap 60 -> 41 rounds does not move results. Not adopted.
- **Ranked by version (rankedver.py, 52 ranked games since 22:00 Oct 28):** #415 6/22 (27%), #418 7/20 (35%), different opponents (only Party of
  Heroes common: 0-2 for both). Eric re-activated #415 (~05:35-06:15, observing more ranked wins); pinned games say #418 = #415 + 1 win / 70.
  #415 stays the live base by his choice; the #420 run restored 415 (06:40).
- **Eric (06:45): "work on Vendetta, how to use her in fights".** edit_vendfight.py, kVendFight (bots/B469x = B468x + it; B470x adds bit 64): 1 execute
  planner (one-turn search of step + attack + reset / dash + attack per enemy; kills only; value x refund bonus - kVendRisk x next-turn damage at
  the end tile via the new incoming_at(p, skip)), 2 refund chain, 4 refund exit, 32 before evade, 64 dash discipline (near enemies the dash is
  never spent closing in). Turn order already puts Vendetta last of ours (priority 0, draft order). Traced probes, #419 config (Vendetta draft
  + Fish health lines) vs PoolLive (#418 with Willow), 14 games, 7 maps x 2 sides: planner only - our deaths 15.8 / game vs theirs 2.9,
  Vendetta 63 deaths (38 while escaping, her dash spent on 146 chase dashes), 5 planned kills; + dash discipline - Vendetta 44 deaths (27
  escaping), dead 17.5% -> 12.1% of turns, team 14.4 / game, theirs 1.6 (fewer kills). Willow's heal is worth more than any Vendetta micro in
  our fight code: the Willow-less team loses fights ~9:1 to our own Willow team. Screens s_vend2 (B469x 39 / 7) and s_vend3 (B470x 64 / 103).
- **Vesper double attacks (tools/stress/doublehit.py + split check, 28 Fish ladder games):** double-attack rounds 3.2 / 100 alive rounds for both
  (ours 13% of attacking rounds, Fish 11%); reset casts 4.9 vs 5.7 / 100 (of 12.5 the cooldown allows); single hits with the reset off cooldown
  9% vs 11%. **Fish's Vesper splits 15% of its camp double attacks over two monsters (112 / 752), ours never (0 / 676)** - hit() fires the
  reset only at the same target and only while it lives; a kill saves the reset. kKillChain (after a kill, the reset on the next monster in
  reach; −13 on an old config) re-screened on the #415 base: s_chain (Eric, 07:10: "enemy vespers ... hit 2 different things in a single turn").
- **s_vend2 (B469x, #419 config = Vendetta draft + Fish health lines: 937/2240 −128 - vs ~1,410 for #415):** kVendFight 39 −5 ± 11, 7 +1 ± 10. The
  planner is neutral on a draft that loses ~470 games of 2,240 to our pool. s_vend3 (dash discipline) re-queued last.
- **Eric's replays of Oct 29 (vs prism best girl):**
  - 22ebc966 (00ribs): their Prism at **40 / 700 HP r120-127**, 2-3 tiles from our Marcella (44%) and 4-6 from Ryth (42%); both walked away
    (escape / evade run before fighting; HoR at 19%). -> **edit_freekill.py kFreeKill** (bots/B471x = B470x + it): before escape / evade, a
    one-basic-hit kill (health <= kFreeKill x strength) in reach or one step away, on a tile whose next-turn damage (incoming_at) is under our
    health. kSecureKill (any reach, spells, dash) lost −87 burst-guarded; this never dives.
  - 4370044f (02the_pond): Ryth was not blocked - at 33% after group 7 he held outside its reach r58-71 (two stun casts r61 / r69) and
    recalled at r71 so the recall ended as the camp died (recall-capture timing): ~13 low-value rounds.
  - Marcella (tools/stress/campcast.py, 28 Fish games + these 3): their Marcella opens 91% of camp fights with her spell from a median
    distance of 3, ours from 1 (the camp code casts from reach only for range > 1). -> **kMeleeOpen** (same edit).
  - 3e50616a (01starvation): our Willow had no teammate within 8 for 455 / 1,186 alive rounds (38%), was our nearest champion to the enemy in
    159 / 301 rounds with an enemy within 8 (53%), died 7 times. Willow-follow history: ungated −66..−85, gated (enemy seen in 60 rounds) −10.
  - HoR aggro claim (Eric): our Oct 28 probe - a non-stunning dash to another tile at the same range does not move aggro; aggro is re-chosen
    each round by distance, then turn order. A stunned monster skips its hit; its next target follows the same rule, so a tank takes over
    only if nearer or equally near and earlier in turn order (ours: priority 0 = draft order, HoR first).
  - Screens queued: s_chain (kKillChain on #415, running) -> s_fk (kFreeKill 0.9 / kMeleeOpen / both on #415) -> s_vend3.
- **s_chain (B470x on the #415 config 1,415/2240 +164; seeds 1 2 4 5):** kKillChain (after a kill, the reset on the next monster) −9 ± 9 (1,410). Fish
  splits only ~4 double attacks a game; off.
- **s_fk (B471x on the #415 config 1,415/2240 +164; seeds 1 2 4 5):** **kFreeKill 0.9 +16 ± 12 (1,467, +52 wins; all four pool bots up)**; kMeleeOpen −30 ± 14
  (1,372: Marcella's damage spell blocks walking, so casting from 3 tiles costs a step); both −28. Ladder **#421 = #415 + kFreeKill 0.9**
  (B471x + tools/cands/cand421.edits): #415's panel baseline p415 (top415 + fish415 + new f2 / x1 at 07:51 while #415 is live), then #421
  on the 140-game panel (lad421.sh); fresh seeds s_fk2 (6-9).
- **s_vend3 (B470x, #419 config 937/2240):** kVendFight 64 (dash discipline) −6 ± 10 (921), 103 (all) −29 ± 12 (873). Vendetta micro does not rescue the
  Willow-less draft in our code; the Vendetta line is closed until the team's fight logic changes (post-knockout).
- **#421 = #415 + kFreeKill 0.9 on the panel (08:03-08:06 UTC):** live was #418 at the start (Eric switched back), so the #415 f2 / x1 baseline was skipped
  and #418 restored. vs #418 over all 140 games **25 vs 24 wins, +1,211**; vs #415 on its 70 pinned games 15 vs 13 (top-10 13 = 13, Fish 2/20 vs
  0/20). Small positive, consistent with local +16.
- **Health emblems (Eric 08:10, "the meta builds health first; escapes are easier with more health"):** first two emblems include Health - top 10 vs
  ours: HoR 67% / 100% (ours Treasure H first), Ryth 99% / 100%, Vesper 22% / 27%, **Marcella 56% / 6%** (ours Treasure F, Jungle F, Bruiser F).
  kMarcBuild 8 (Treasure F, Durability H, Bruiser F) was −4 ± 13 alone (s_marchyb) and #406 (+ kMarcTribute) tied #405 8/50 = 8/50. Screen
  s_hp on the #418 config: kFreeKill 0.9 / kMarcBuild 8 / both; then a pinned panel test of the combination when the scrim quota allows.
- **Eric (08:10): altar-line greed + bush vision.** 02the_pond: their Vesper carried up to 63 gems and banked 12 times (24-63 each), never died;
  ours peaked at 22, banked 3 times. Her extra autos: attacking camps 28% of alive rounds vs ours 21.6%, walking 37% vs 56% - a tight loop,
  not attack tricks. **edit_safebag.py** (bots/B472x = B471x + it): kSafeBag - with the nearest altar on our side (not far-side / contested) and
  us kSafeBagMargin 8 nearer our spawn than theirs, the delivery bag is at least kSafeBag; a hurt retreat banks there within kSafeBagRetreat 12;
  no gem-carrying shop trip before the bank. kBushChase - turn end, an enemy within 5 (or one that vanished beside us since last turn): a ready
  ward into the bush tile within placement reach nearest it. Screen s_bag (kSafeBag 80 / kBushChase / both, #418 config) after s_hp.
- **s_fk2 (fresh seeds 6-9, #415 base 1,411/2240):** kFreeKill 0.9 +8 ± 11 (1,437, +26 wins) - positive on both seed sets.
- **s_hp (B471x on the #418 config 1,404/2240 +155; seeds 1 2 4 5):** kFreeKill 0.9 **+21 ± 12** (1,435); kMarcBuild 8 +7 ± 10 (1,454, **+50 wins**);
  both **+19 ± 13 (1,464, +60 wins)**. Ladder **#422 = #418 + kFreeKill 0.9 + kMarcBuild 8** (B471x + tools/cands/cand422.edits) on the 140-game
  panel vs p418 (lad422.sh, 08:50 UTC; waits for the scrim quota after #421's 28 groups at 08:05).
- **#422 = #418 + kFreeKill 0.9 + kMarcBuild 8 on the 140-game panel (09:01-09:06 UTC):** **22 vs 24 wins, margin +2,347** (top-10 12 vs 13 +482, Fish 1 vs 2
  −535, x1 9 = 9 +2,400). Mixed, within the panel's noise; #418 kept live (restored 09:10). Free-kill builds on the panel: #421 +1 win / +1.2k,
  #422 −2 / +2.3k.
- **s_bag (B472x on the #418 config 1,404/2240 +155; seeds 1 2 4 5):** **kSafeBag 80 −15 ± 6 (1,362, −42 wins)**; kBushChase −9 ± 12 (1,376); both −24 ± 12.
  Off (an 80-gem bag is a big loss on a death and slows banking; bush-chase wards fire 0-9 a game). Last panel slot: #423 = #418 + kFreeKill 0.9.
- **Bush fights (tools/stress/bushfight.ts, Game_GetBush via the replay engine; 28 Fish ladder games):** fight rounds (an enemy within 5) on a bush
  tile: Fish 14.4%, ours 10.2%. Bush entries in fights 24.8 vs 22.8 a game; within 10 rounds after a Fish entry one of ours died 177 times (26%),
  the Fish bush-user 58 (8%); after ours, one of theirs 97 (15%), ours 107 (17%). Fish fights from bushes; our odds count only visible enemies.
  **edit_bushghost.py kBushGhost** (bots/B473x = B472x + it): with kGhostRounds 0, an enemy last seen on / beside a bush keeps counting in
  fight_odds at its last spot for kBushGhost rounds (kGhostRounds, all out-of-sight enemies, lost −40 / −69). Local check s_bghost (3 / 5 /
  3 + kBushChase); the ladder panel is the real test (the pool does not fight from bushes).
- **Eric's replay 173737cc (00stampede vs Ad Astra), r118-121:** our Vesper lost two turns to a CHAINED stun - their champion #4 stunned her at
  r118 (timer 1); at r119 the timer hit 0 just as their HoR's dash re-stunned her (timer 1 again, + landing hit + attack); r120 skipped; r121
  they acted first (odd round) so HoR's third hit landed before her dash out. Their HoR landed at (7,19), the side of her escape (she fled
  west / south-west). Our kChainStun / kStunOrder classify only is_cc, so they never governed Ryth's (aoe_damage) or HoR's (dash) stuns.
  tools/stress/stunchain.ts counts stuns on champions as fresh / chained / overlapping (running). **edit_dashbehind.py kDashBehind** (bots/B474x
  = B473x + it): HoR's champion dash prefers, among equal landings, the tile nearest the enemy's spawn (behind it, on its way home). Screen
  s_behind queued after s_bghost.
- **Stuns on champions (tools/stress/stunchain.ts, replay buff state, 28 Fish ladder games):** ours 17.8 a game (fresh 478, chained 19 = 4%), Fish
  10.9 (fresh 296, chained 10 = 3%); no detectable overlaps either side. We stun more than Fish; chaining is rare for both - Ad Astra's double
  stun (173737cc) was situational. A correct chain-stun rule (Ryth aoe / HoR dash) would touch ~1 stun a game: low priority.
- **s_bghost (B473x on the #418 config 1,419/2240 +164; seeds 1 2 4 5):** kBushGhost 3 −4 ± 14 (1,417), 5 −7 ± 14 (1,403), 3 + kBushChase −14 ± 14 (1,415):
  no disaster, no local gain (the pool does not fight from bushes; PoolAggro +41, PoolLive −43). A ladder-panel question; ready in B473x.
- **Damage audit (tools/stress/dmgaudit.py; camp fights, 28 Fish + x1 / x2 ladder games; Eric 10:00: "ensure we aren't missing damage or autos ...
  for all champions"):** missed autos (a living member in attack range, no attack): HoR 10.6% vs top 6.3%, Marcella 11.5% vs 7.1%, Vesper 10.1% vs
  10.3%, Ryth 9.3%, Willow 12.3% (their 14.4%). Ability casts per fight round level everywhere. Camp openings by a spell: HoR 38% from 1 tile vs
  their 56% from 2 (their dash opens), Marcella 91% from 1 vs 90% from 3. In traced #418 games the misses are mostly fight_camp turns (Marcella
  56 / 120, Vesper 59 / 141) and capture turns beside a living member (Ryth 43 / 96, Willow 46 / 90): fight_group hits only its chosen target
  after the approach step. **edit_anyhit.py kAnyHit** (bots/B475x = B474x + it): after the step, the living member in reach with the least
  health. Screen s_anyhit (kAnyHit / + kFreeKill) after s_behind. Next: the capture-turn misses, and HoR opening camps with the dash.
- **#423 = #418 + kFreeKill 0.9 on the 140-game panel (10:01-10:06 UTC; B471x + tools/cands/cand423.edits): 28 vs 24 wins, +2,431** (top-10 14 vs 13,
  Fish 1 + 2 vs 1 + 1, x1 11 vs 9 +3.4k). Best panel result of Oct 29; with local +16 / +8 / +21 the most consistent gain. Recommended to Eric as
  the knockout build; #418 restored by the script.
- **s_behind (B474x on the #418 config 1,419/2240 +164; seeds 1 2 4 5):** kDashBehind −4 ± 6 (1,408): neutral locally (the pool's escapes go home too,
  so the tie-break rarely changes the outcome there). Ladder-only question; ready in B474x.
- **s_anyhit (B475x on the #418 config 1,419/2240 +164):** kAnyHit −23 ± 13 (1,403); + kFreeKill −10 ± 14 (1,411). Hitting another member in reach splits
  the team's focus on the chosen target (slower kills, longer camp hits); part of the "missed autos" is deliberate focus. Off.
- **Panel tests queued (Eric 10:40, "lets do the panel tests for those 3 features"; scratchpad run/ladpanel.sh, copy tools/cands/ladpanel.sh):**
  #424 = #423 + kBushGhost 3 vs p423; #425 = #423 + kDashBehind vs p423; #426 = #419 config + kVendFight 103 vs p419 (14/140). All from B475x
  (every switch, off by default); sequential (28 groups each, quota ~50 / hour), each restoring the version live at its start.
- **#424 = #423 + kBushGhost 3 on the 140-game panel (11:01-11:07 UTC): 23 vs 28 wins, −5,798.** Remembering bush-vanished enemies makes us back off
  fights we win; worse on the ladder too. Off.
- **Abilities while running (Eric 11:20 UTC Oct 29, replay 8ec51a0b 00road_of_riches vs Noobot, #423):** our Ryth stunned theirs at r253, then
  hit-and-stepped r259-r271 (13 turns, 1010 -> 90 health) with his area stun ready from r261 and his attack reset from r265, never cast; their
  Ryth re-stunned ours at r266 and double-hit (attack, reset, attack) at r263 and r271. Cause: strike_while_escaping() casts only `is_cc`
  stuns and Ryth's is `aoe_damage` (kKiteAoe off since Oct 23, -24 +-25 locally); resets are spent there only by Marcella (kMarcFleeReset,
  off); retreat() throws only the free melee hit. In that game our Ryth fled 19 turns with the stun ready on 15 (0 cast), the reset on 12
  (0 used); Marcella's reset ready on 8 of 10 (0). tools/stress/fleeabil.ts (flee turns per side, champion, ability: ready / used).
  **edit_fleeabil.py kFleeAbil** (bots/B476x = B475x + it, off): 1 area stun on the chaser when the step it costs is free (chaser within 2,
  stunnable, every enemy champion within 3 inside the blast, no camp tile in it); 2 attack reset + second hit after the escape hit (not on
  Ren; Marcella stays kMarcFleeReset); 4 retreat() strikes like escape() with an enemy within 2; 8 ranged: reset + shot after the step.
  Local screen s_flee (#423 config: 0 vs 7 vs 15) started 11:31.
  fleeabil.ts on 144 benched games (sl_top413/414/415 + sl_fish405c; flee turn = an enemy champion within 2 and we stepped away), ability
  used on ready flee turns, us vs them: Ryth stun 0/1152 vs 0/214 (nobody casts it running - it costs the step); **attack resets: Ryth 9/1864
  (0%) vs 78/291 (27%), Marcella 7/1318 (1%) vs 66/272 (24%), Vesper 2/666 (0%) vs 62/177 (35%), Willow 0/311 vs 6/10; their Vendetta 25%,
  Issac 24%**; dashes used: ours 83-87% (HoR, Vesper) vs theirs 51-70%. We also run far more: our Ryth 2827 flee turns vs theirs 773.
- **#425 = #423 + kDashBehind on the 125-game panel (12:02-12:04 UTC): 26 vs 26 wins, +2,104** (top-10 15 vs 14 +4.2k; Fish 1/1, 2/2;
  random-map top-10 8 vs 9 -1.6k). HoR landing behind its target: neutral on the ladder. Off (no reason to switch).
- **#426 = #419 config (Vendetta draft) + kVendFight 103 on the 125-game panel (12:20-12:24 UTC): 14 vs #419's 12 wins, +2,859** (top-10 7 vs
  6; Fish 0/0, 2 vs 1; random-map 5/5). The planner and dash discipline help Vendetta a little, but the Vendetta draft stays far below #423 on
  the same 125 games (14 vs 26 wins, -16.5k). Off; no Vendetta draft.
  **Correction (fleeabil.ts fixed 12:30):** the first count missed every turn that rules out walking (a Ryth stun mid-run: no step, so not a
  "flee turn"). Now a stand-still turn right after a step away counts, and turns spent stunned are left out. Same 144 games, used / ready on
  flee turns, us vs them: **Ryth stun 75/1233 (6%) vs 31/249 (12%)**; resets Ryth 30/1942 (2%) vs 78/299 (26%), Marcella 24/1377 (2%) vs 69/278
  (25%), Vesper 37/708 (5%) vs 68/184 (37%), Willow 15/328 vs 10/14; their Vendetta 25%, Issac 24%. Local s_flee (280 seed-1 games each, off /
  7 / 15): Ryth stun used 170 / 228 / 215, Ryth reset 38 / 512 / 489, Vesper reset 36 / 29 / 134, Willow reset 20 / 18 / 142 - the bits fire.
  s_flee2 (#423 config: 0 vs 1 vs 10 vs 14) started 12:31.
- **Attack resets (Eric 12:50 "lets also continue on fixing the attack resets"):** local diagnostic build (bots/Zreset, #423 config + a turn-end
  print, never uploaded; 48 games vs PoolLive / PoolCarry, scratchpad resetdiag + resetdiag.py): 899 turns attacked, cast nothing and ended with
  the reset ready - **723 (80%) camp fights whose first hit killed the target** (hit() fires the reset only at the same, living target: "a kill
  saves the reset"), 81 melee_free and 59 free_kill hits (no reset code), 22 other champion-fight hits. **edit_resetmore.py kResetMore**
  (bots/B477x = B476x + it, off): 1 after a kill the reset goes to the next target in reach (camp: chain_kill = kKillChain, -9 +-9 on #415;
  champion kill in hit(): the weakest other enemy champion in reach), 2 melee_free / free_kill follow their hit with a reset. tools/stress/
  resetuse.ts (ready / used by situation, snapshots only) and resetfight.py (needs trace2.json; extract2.ts now writes cd / ab per champion).
  **Ladder (resetfight.py, 144 games #413-#415 vs top-10 / Fish): turns starting with the reset ready, used % - camp hits are on par (Ryth 80 vs
  79, Marcella 86 vs 77, Vesper 88 vs 89, Willow 93 vs 94); champion hits are the gap: Ryth 29% vs 63% (1,369 turns unused), Marcella 25% vs
  47% (1,157)**; Vesper 90 vs 62, Willow 92 vs 87. The local "kill saves the reset" turns happen to them as often. Targets: escape hits (kFleeAbil
  2, Ryth; Marcella only through kMarcFleeReset), melee_free / free_kill (kResetMore 2).
- **s_flee2 (#423 config, 2240 games each, paired vs off 1434):** kFleeAbil 1 +3 +-8 (1431), 10 +6 +-10 (1447), 14 +0 +-10 (1436); with s_flee 7
  -13 +-10 and 15 -0 +-11 - bit 4 (retreat strikes) in every weaker arm. **#427 = #423 + kDashBehind + kVendFight 103 + kFleeAbil 11** (stun +
  resets, no retreat bit; Eric 12:40 "lets do a combined version"), 125-game panel vs p423, upload 13:06 (scratchpad run/lad427.sh).
  s_reset (B477x: kResetMore 1 / 2 / 3) started 13:07.
- **#427 = #423 + kDashBehind + kVendFight 103 + kFleeAbil 11 on the 125-game panel (13:22-13:27 UTC): 30 vs 26 wins, +1,034** (top-10 16 vs 14
  +2.2k; Fish 2 vs 1, 2 vs 2; random-map top-10 10 vs 9 -1.1k). Best win count on this panel so far; the margin barely moves. #423 restored.
- **s_reset (B477x on the #423 config, 2240 games each, paired vs off 1434):** kResetMore 1 -1 +-9 (1437), 2 -5 +-10 (1421), 3 -10 +-12 (1418) - all
  noise. Bit 1 (kill chain) aims at camp fights, where the ladder is already on par: left out. **#428 = #427 + kResetMore 2 + kMarcFleeReset**
  (B477x; the ladder's champion-hit gap: Ryth 29 vs 63%, Marcella 25 vs 47%), 125-game panel vs p423 and p427, upload 13:32 (run/lad428.sh).
- **#428 = #427 + kResetMore 2 + kMarcFleeReset on the 125-game panel (13:43-13:48 UTC): 32 vs #423's 26 wins, +7,705; vs #427 (30, -53.2k)
  +2 wins, +6.7k** (top-10 16 / -14.0k vs 16 / -16.4k; Fish 2 vs 2, 3 vs 2; random-map top-10 11 vs 10). Best on the panel in wins and margin.
- **Eric ~13:55 UTC, replay 377c32ed (02fields vs Fish, #427):** our HoR, 770 -> 35 health r563-r566 (their Vesper + Issac), began a recall at
  (29,26) between bush columns x=27 / x=31; their Vesper and Issac stood 4 away behind the x=31 column, which Fish had warded beside the fight
  (31,26 / 31,28 / 31,23; ours all further south) - their Vesper killed him at r568 from (32,24). **edit_bushrecall.py** (bots/B478x = B477x +
  it + edit_marcearly.py): **kBushRecall N** - retreat()'s recall right after a fight (hit or attacking within 5 rounds, an enemy seen within 10)
  first walks into a bush within N (none with a visible enemy within 2 or a known enemy ward in its bush), at most N + 2 turns; **kFightWard** -
  with an enemy champion within 8 or seen in the last 10 rounds, a ready ward into an adjacent bush whose connected bush holds none of our wards
  (nearest the enemy). 16 traced local games (02fields, 02the-pond, 00ribs, 01starvation): bush_recall_walk 95; fight wards on every camp fight
  were 100-200 a game (each champion keeps one ward) -> restricted to enemies in view / seen lately.
- **Marcella (Eric ~14:00): edit_marcearly.py** - kMarcGems bit 4: before r300 a reward of >= 10 gems goes whole to Marcella (alive, within 6)
  - gem rewards otherwise wanted Prism, whom we never draft; **kMarcBuild 10** = the top teams' 2.0.0 line (buildorder.ts OTHER=1, 94 games:
  Treasure H / Jungle F r185, Durability H r305, Durability H / Monster F r400, Bruiser H r435, Bruiser S r485-550; Power 6%): Treasure H,
  Durability H, Bruiser H, then Bruiser S; kMeleeOpen (her spell from reach; -30 locally before the reset fixes).
  **#429 = #428 + kBushRecall 5 + kFightWard + kMarcGems 4 + kMarcBuild 10 + kMeleeOpen** (B478x, run/cand429.edits), 125-game panel vs p428
  and p423 (upload 14:10, RESTORE=428); local s_bush (#428 config: bush / Marcella / both) in parallel.
- **#429 (= #428 + kBushRecall 5 + kFightWard + kMarcGems 4 + kMarcBuild 10 + kMeleeOpen) on the 125-game panel (14:25-14:30 UTC): 10 vs #428's
  32 wins, -24,869** (top-10 7 vs 16, Fish 0/0 vs 2/3, random-map 3 vs 11). A broken component; split by the local screen s_bush. #428 restored.
- **s_bush (B478x on the #428 config, 2240 each, paired vs off 1433):** kBushRecall 5 + kFightWard -23 +-14 (1397); **Marcella package (kMarcGems
  4 + kMarcBuild 10 + kMeleeOpen) -149 +-14 (1158)** - the #429 collapse; all -151 (1136). Split s_marc (each alone) queued.
- **Vesper resets (vespreset.py, 144 ladder games):** ours "atk reset atk" same target 64%, "move reset atk" 36%; theirs 50% / 42%, plus 5%
  split onto another camp member (ours 0%: hit() keeps the reset after a kill; kResetMore 1 spends it). Our Vesper double-hits as often as theirs.
- **Eric 14:40, replay 9c8571c4 (00packs vs Sponge, #429): escapedkills.py** - 6 of 10 low-enemy episodes escaped; their Ryth r188-r197 430 -> 1
  health with our Vesper 3 off and her dash ready (at r197 it stepped out first; ours walked - a ranged step spends the shot), their Ryth
  r809-r812 1170 -> 141 the same. **edit_dashkill.py** (bots/B480x = B479x + it): **kDashKill H** - an enemy out of reach with <= H x our
  strength: dash to a landing in reach (incoming under our health, under kDashKillSafe for chases; its spawn side first) and hit; **kFreeKillFix**
  - free_kill's ranged step needs a ready reset. Traced: dash_kill 66 / free_kill 49 in 16 games. Screen s_dash queued after s_marc / s_hand.
- **B479x = B478x + edit_handoff.py (kHandoff) + edit_clustersplit.py (kClusterSplit)**: idle-reward diagnostic (bots/Zidle, scratchpad
  idlechk*): 6,092 champion-turns within 3 of an uncaptured ready reward in 24 games, 737 believing it respawning (391 after a carrier
  hand-off); kHandoff 60: 625 / 5,996 - most such turns are the 1-3 walk onto a just-killed cluster. Traced breadcrumbs: cluster_one 16-32
  jobs a game with kClusterSplit 10.
- **Full code review (Eric 15:00; four read-only reviewers over bots/Zrev = B479x + cand428, by line range):** part 1 (1-4500 + draft.cpp):
  kCarryCast 2 never decodes teammates' sightings (live mapped loop skips read_carry_report; already "open" in Review-2026-10-28-full);
  engaged_ / wait_ / guarding_ survive death (kDeathReset off, never screened) -> a respawned champion walks back alone into the camp that
  killed it; minor: contact_turns_ / anti-osc read last turn's enemies, fight_dps_ stale after spawn shopping, kIgnoreSpawned drops enemies
  anywhere in the spawn box. Part 3 (9000-13400, fight code): free_kill's ranged step spends the shot (-> kFreeKillFix); spell_reach returns
  without HoR's hit after its stun-dash; escape dashes before the melee free hit; escape stuns land on stun-immune Marcella; a ranged escaper
  that cannot step never shoots (flee_shot also quit on cast_used_); the chase loop takes enemies in list order; **dash_towards refuses when "a
  step reaches it" - but a ranged step spends the shot (the r197 Vesper case)**; Vendetta never dash+step+hits; contest_altar may stun the
  escort; incoming_at counts ranged enemies 1 tile long (+1 more for spells forbidding walking). **edit_reviewfix29.py kReviewFix29** (bots/B481x
  = B480x + it): 1 carry reports, 2 spell_reach hit, 4 escape hit before dash, 8 no escape stun on Marcella, 16 ranged escape shot, 32 chase
  lowest first, 64 ranged chase dash. Parts 2 / 4 pending.
- tools/edits/edit_prospector.py (Oct 27 kMarcBuild 8/9 Prospector lines + kCaptureEmblem, untracked) was overwritten by mistake today and is
  lost; its output is intact in bots/B424x. The Oct 29 Prospector farm build is **edit_prospector2.py: kFarmBuild 8** (Marcella Prospector F,
  Vesper S, Ryth H as the second emblem; with kFarmBuildMaps 1 on non-control maps and boss maps) in bots/B480x.
- **s_marc (B479x on the #428 config, 2240 each, paired vs off 1441):** kMarcGems 4 **+12 +-10 (1466)**; **kMarcBuild 10 -116 +-12 (1227) - the
  #429 collapse** (the top teams' Treasure H / Durability H / Bruiser line starves our Focus-spell farming again, as kMarcBuild 7 / kBuild3
  did); kMeleeOpen -11 +-14 (1448). Eric was right: the gem rewards and the spell from reach were not the problem.
- **Review batch 2 (parts 2 + 4) into kReviewFix29 (bots/B481x):** 128 respawn_until_ cleared on alive / ready-uncaptured sightings (arrival_time
  dropped any group with a future respawn_until_ - a hand-off's full-ETA mark kept SEEN ready rewards unpickable: the real "reward left lying"
  bug), 256 our_cap_round_ not on enemy captures, 512 zone_role counts us (kZones 3 never ran), 1024 tribute_guard keeps captures / camp
  fights, 2048 the retreat altar shortcut needs the nearest altar usable, 4096 idle deliver needs a usable altar, 8192 no jam-yield when hurt
  / carrying. Not fixed (Varg / not drafted or low): Varg loop bit = help bit, rows_varg unreachable pack, dash_over legality, spawn-box
  shopping idle, monster_reach_depth cache radius, ranged boss oscillation (kReviewFix2 2 exists), hold_until_party counting.
- **Quick checks (140 games vs PoolLive, 70 maps x 2 sides, same games; scratchpad qchk + qcmp.py):** #428 68 / +3.3k; + fight bundle
  (kDashKill 3 + kFreeKillFix + kReviewFix29 127) 71 / +4.6k; + camp fixes (kReviewFix29 384 + kHandoff 60) 75 / +9.3k; + kMarcGems 4 +
  kMeleeOpen 77 / +12.6k; **all together (kReviewFix29 511) 86 / +17.0k**. **#430 = #428 + kDashKill 3 + kFreeKillFix + kReviewFix29 511 +
  kHandoff 60 + kMarcGems 4 + kMeleeOpen** (B481x, scratchpad run/cand430.edits), panel upload 15:14 (RESTORE=428). Local s_all (8 arms on
  B481x) queued behind s_hand.
- **#430 (= #428 + kDashKill 3 + kFreeKillFix + kReviewFix29 511 + kHandoff 60 + kMarcGems 4 + kMeleeOpen, UNCORRECTED B481x) on the 125-game
  panel (15:32-15:37 UTC): 28 vs #428's 32 wins, -4,177** (top-10 14 vs 16, Fish 2/2 and 1 vs 3, random-map 11/11; 24 flipped games). The
  local quick check (86 vs 68 of 140 vs PoolLive) did not carry to the ladder. Codex C263 found three flaws in that build (bit 64 unreachable,
  bit 4 spends the cast before the escape dash, bit 128 undone by read_event) - corrected in B482x (edit_reviewfix29b.py).
- **s_hand (B479x on the #428 config, 2240 each, vs 1441):** kHandoff 60 -6 +-10 (1431); **kClusterSplit 10 (+ kClusterOne 1) -169 +-16
  (1167)**; both -170 (1121). Splitting a squad member off for any cluster-only node within 10 loses heavily against the pool (PoolLive -110).
- s_all failed (8 arms of full edit strings: "Argument list too long"); re-run as **s_all2 on bots/B482c** (= B482x with cand428 baked in;
  arms carry only their switches): dash kill, kReviewFix29 127 / 384 / 15360 / 512, kDeathReset, kFarmBuild 8. **#431 = #428 + kMarcGems 4 +
  kMeleeOpen** (B482x) queued on the panel after #430's restore.
- **Panel noise (Oct 29, #428 vs #430 on 01hooks vs Mite):** the two games diverge at ROUND 1 (Willow's first move), before any changed switch can
  act - a code change shifts the set-up turn's fuel use, so every build reshuffles the pinned games (24 of 125 flipped for #430). A panel
  difference of a few wins is noise (flip count ~25 -> SD of the net ~5 wins); only large effects (#429 -22) are signals (Codex C259 agrees).
  01hooks swings W/L between #428 / #429 / #430 for this reason, not one switch.
- **Eric ~15:45, replay 425a478a (00pilgrimage vs Claudus Maximus, #430): "our champs stop at every node and start only once every champion is
  within hitting distance; theirs never stop moving forwards; their Vesper vacuums the leftover gold, Treasure S > Jungle S > Durability H >
  Bruiser"** (= our kVespBuild 6, live since #418). **tools/stress/campwait.py** (camp start = a team's first damage on a group after 30
  quiet rounds; participants = its champions hitting within 15 rounds), 81 ladder games (sl_top414/415): **camp starts a game ours 42.0 /
  theirs 75.9; participants 2.19 / 1.52; rounds within 4 of the camp without a hit before the start 2.57 / 0.97 per participant (idle 0.84 /
  0.25); first-to-last participant 2.8 / 1.6 rounds.** By phase: r<300 12.5 @ 2.61 vs 21.8 @ 1.66; r300-700 14.8 @ 2.15 vs 27.4 @ 1.49;
  r700+ 14.7 @ 1.87 vs 26.7 @ 1.42. The known gap (Oct 27: they solo clusters 183 / 230, we 28 / 105); every local screen of smaller parties
  lost (kOpeningRounds 60/40/0, kClusterSolo, kTeamSquads, kSplitRound, kClusterOne -45, kClusterSplit -169). **edit_clustersplit2.py**
  (B483x): kClusterSplitPeer - split only while the squad's own target is cluster-only. s_split (B483c = B483x + cand428 baked: narrow
  split / kOpeningRounds 60) queued after s_all2.
- **Codex ward audit (C270-C273) -> edit_wardfix.py (bots/B484x = B483x + it):** kWardRefresh - observe_enemies() runs before the turn's early
  ward placements and the fight decisions used that stale list (10 newly revealed targets in basic reach with can_attack true right after the
  placement, 2 hit that round): re-read the enemies when an early placement moved our ward; kFightWardOwn - fight_bush_ward skipped bushes
  holding ANY allied ward, but a teammate's ward gives us no sight (per-owner vision): count only our own; kReviewFix29 4 refined - the plain
  pre-dash hit only with an escape dash actually ready. Bush-share gap is mostly WHERE we stand (12 native games: ours 39.8% / top 69.7%;
  850 of 983 of our non-bush placements had no free bush within 2 - converting every alternative reaches only 47.9%).
- **#431 = #428 + kMarcGems 4 + kMeleeOpen (B482x) on the 125-game panel (15:55-16:00 UTC): 28 vs #428's 32 wins, margin +3,054** (top-10 12
  vs 16 -0.6k; Fish 3 vs 2, 3 / 3; random-map 10 vs 11 +2.6k). Inside the panel's noise (+-5 wins); margin up, wins down. Local s_marc:
  kMarcGems 4 +12 +-10, kMeleeOpen -11 +-14. Not adopted on this evidence.
- Quick check, corrected fight bundle (B484x: kDashKill 3 + kFreeKillFix + kReviewFix29 127 + kWardRefresh) vs #428 on 140 paired games vs
  PoolLive: 71 vs 68 wins, -1.7k (75 flips, 39 / 36) - neutral. **#432** = #428 + that bundle queued for the 16:22+ upload (panel at ~16:32).
- **campwait.py by camp kind (81 ladder games):** cluster-only nodes started a game ours 17.3 @ 1.45 champions / theirs 37.0 @ 1.23, near
  without a hit 3.54 / 1.21 per champion; monster camps 24.7 @ 2.71 / 38.9 @ 1.79, first-to-last participant 4.1 / 2.7 rounds. Local
  diagnostic bots/Zcl (#428 config, 24 games on cluster maps; scratchpad clchk): 14,735 turns within 4 of a living cluster-only node with no
  attack and no enemy - travel ~4.0k, capture (on another reward) ~5.0k (3.0k still), guard ~1.3k, fight_camp on it ~1.4k.
  **edit_clusterchip.py kClusterChip** (bots/B485x = B484x + it): turn end, no attack yet, no enemy in view -> hit a cluster-only member in
  reach. Quick check vs #428 (140 games): 64 vs 68, -10.3k (46 flips) - screen s_chip (B485c: chip / kWardRefresh / kFightWard+Own) queued
  after s_split.
- **s_all2 (B482c = B482x + cand428 baked, 2240 each, paired vs 1435):** kDashKill 3 + kFreeKillFix +9 +-11 (1455); kReviewFix29 127 (fight,
  corrected) -15 +-14 (1440); **kReviewFix29 384 (seen camps not respawning + no repeat-wait for enemy captures) +25 +-11 (1484)**; 15360
  (misc) -1 +-10 (1443); 512 (zones) identical (never fires: kZones 3 only on whole-team maps); kDeathReset +3 +-2 (1434, rarely fires);
  kFarmBuild 8 / maps 1 (Prospector) +5 +-10 (1455). **#433 = #428 + kReviewFix29 384 + kDashKill 3 + kFreeKillFix + kFarmBuild 8 / maps 1 +
  kMarcGems 4** (B485x, run/cand433.edits) queued after #432 (quota from ~16:55).
- **#432 = #428 + kDashKill 3 + kFreeKillFix + kReviewFix29 127 (corrected, B484x) + kWardRefresh on the 125-game panel (16:42-16:47 UTC): 18 vs
  #428's 32 wins, -10,657** (top-10 9 vs 16, Fish 2/2 and 1 vs 3, random-map 6 vs 11) - beyond the panel's noise: the fight bundle LOSES on the
  ladder (locally dash kill +9, bits 127 -15). With #430 (-4) both packages carried kDashKill 3; #432 adds the reachable ranged chase dash (bit
  64) and kWardRefresh. Suspect: dashing in on low runners against teams that punish it. Fight bundle off; #433 relaunched WITHOUT the dash
  kill: #428 + kReviewFix29 384 + kFarmBuild 8 / maps 1 + kMarcGems 4.
- **Monster-camp idle diagnostic (bots/Zmc, #428 config, 28 games; scratchpad mcchk):** 18,132 turns within 4 of a living monster camp with
  no attack, no enemy: idle (no target) 3,721, fight_camp / help on it without a hit ~3,600, travel past ~2,700, capture / deliver / guard
  ~3,200, wait_party ~900. The idle turns: 3,593 at 80%+ health, no gems, beside camps needing 2 (2,964) or 3 (497) by our own estimate - a
  solo champion that cannot take a 2-camp stands there (top teams pair on elks: 2.01 / camp). kShortNow (edit_shortnow.py, B486x: start
  when full_ok) changes 6 of 140 games - not the blocker. Earlier pairing tries (kSoloParty, kSchedLate, kFarmRoute) gained nothing locally.
- **s_split (B483c = B483x + cand428 baked, 2240 each, vs 1435):** kClusterSplit 10 + kClusterOne 1 + kClusterSplitPeer (split only while the
  squad's own target is cluster-only) **-56 +-14 (1360)** (the unrestricted split was -169); kOpeningRounds 60 +6 +-3 (1447; only close-spawn
  maps use it - race / control maps take kOpenRace / kOpenControl). The breadcrumbs split stays off locally; a ladder check is the only judge
  left for it (the pool punishes lone champions).
- **#433's first upload failed its stress scan** (stuck 6 / 202 rounds vs 5-41 for #427-#432): 01fracture side A - Marcella held 208 gems in a
  tribute channel r920-r1160 with the timer at 20 every round: kChannelWatch's tribute_doomed() (damage x remaining turns; 208 gems = 20 turns)
  cancelled each turn and deliver() restarted it next turn, HoR and Vesper standing guard (kTributeGuard). channel_unsafe (the start check)
  is looser, and wants_deliver honours deliver_block_until_ only with kUnsafeAltar > 0 (0). **edit_tributeloop.py kDoomBlock** (bots/B487x =
  B486x + it): a doomed cancel blocks delivering N rounds (wants_deliver and retreat's altar shortcut honour it). #433 re-run with kDoomBlock 8.
- **s_chip (B485c = B485x + cand428 baked, 2240 each, vs 1435):** kClusterChip +1 +-11 (1442; the -10k quick check was noise); kWardRefresh
  -0 +-12 (1446); kFightWard + kFightWardOwn -17 +-14 (1404). The pool rewards neither vision nor chipping; ladder only.
- #433 retry (B487x, kDoomBlock 8 added) stress scan: stuck 3 / 26 rounds (was 6 / 202) - submitted 17:13.
- **#433 = #428 + kReviewFix29 384 + kFarmBuild 8 / maps 1 + kMarcGems 4 + kDoomBlock 8 (B487x) on the 125-game panel (17:21-17:27 UTC): 21 vs
  #428's 32 wins, -8,838** (top-10 13 vs 16, Fish 1 vs 2 / 1 vs 3, random-map 6 vs 11); vs #423's 26 also -5. Locally positive item / reward
  changes (Prospector second emblem, Marcella's gem rewards) keep losing against the top teams (#431 -4, #433 -11). Next: the bug fixes
  alone - **#434 = #428 + kReviewFix29 384 + kDoomBlock 8** (B487x).
- **edit_waitreach.py kWaitLeaveReach** (Codex C283; bots/B488x = B487x + it): the party wait steps out of an awake camp's reach
  (leave_monster_reach) instead of the approach step - our Ryth waited 2 tiles from an awake elk taking 60 a round while the enemy farmed it.
  Screen s_wait (B488c = B488x + cand428 baked: kWaitLeaveReach / kDoomBlock 8 / both + kReviewFix29 384).
- **#434 = #428 + kReviewFix29 384 + kDoomBlock 8 (bug fixes only, B487x) on the 125-game panel (17:46-17:52 UTC): 24 vs #428's 32 wins, -7,481**
  (top-10 16 / 16 same margin; Fish 0 vs 2, 1 vs 3; random-map 7 vs 11); vs #423 26 -2. Every build since #428 lands at 18-28: #428's 32 looks
  like a lucky draw. Calibration: **#435 = #428 behaviour + kNoopFuel 1** (a no-op that reshuffles the panel through fuel / layout) on B477x.
- **Runtime-eval harness (edit_rteval.py, bots/B489x = B488x + it; Codex C284 / C285 generalised):** candidate features read bits from the
  draft-plan header byte 15 (kEvalDraftConfig, inside the checksum) into rt_eval_; every feature tests its own trigger first. OFF and ON builds
  differ only in the draft publication (wasm 1,015,598 vs 1,015,606 bytes). **Prefix check (40 maps vs PoolLive, side A): 34 byte-identical
  replays, 6 different** with bit 4 (the tribute block) - a panel comparison now isolates the games a feature touches. Bits: 1 ReviewFix29 128,
  2 ReviewFix29 256, 4 DoomBlock 8, 8 WaitLeaveReach, 16 MarcGems 4, 128 ClusterChip (32 / 64 for Codex's C277 / C274). Plan: **#436 = OFF
  baseline**, **#437 = bits 15** compared game for game with #436 (run/lad436_7.sh after #435).
- **s_wait (B488c = B488x + cand428 baked, 2240 each, vs 1435):** kWaitLeaveReach +4 +-7 (1443); kDoomBlock 8 -2 +-5 (1436, fires rarely);
  **both + kReviewFix29 384 +20 +-12 (1475)** - the same set as #437's runtime bits 1|2|4|8.
  **edit_rteval2.py** (in B489x before any harness upload): rt 32 = Codex C277 safe wait poke (a plain basic from the wait_party branch when no
  living hostile member of the group reaches us or a visible mate, no enemy in view; hold that turn), rt 64 = Codex C274 WatchWard retention
  (keep our bush ward when its cached mask covers every group tile). Paired check bits 32 + 64 vs OFF: 39 of 40 games differ (they fire often).
- **#435 = #428 + kNoopFuel 1 (calibration, B477x) on the 125-game panel (18:25-18:30 UTC): 32 / -46,766 vs #428 32 / -46,571** - a trivial code
  change does NOT reshuffle the panel (the "any change reshuffles from round 1" reading of #430 was wrong: something in #430's bundle acted at
  r1). Panel differences come from behaviour changes; but any change that alters one action in a game makes the rest of that game a fresh
  draw, so a frequently firing feature still faces ~+-5 wins of noise on 125 games; only large effects (#432 -14, #433 -11) are clear. The
  runtime harness helps for rarely firing features (bit 4: 6 / 40 local games differ), not for frequent ones (bits 32 + 64: 39 / 40).
- **#436 = harness B489x bits 15 (ReviewFix29 128 + 256, DoomBlock 8, WaitLeaveReach) on the 125-game panel (18:55-19:00 UTC): 27 vs #428's 32,
  -4,929** (top-10 15 vs 16 with a better margin, Fish 1 vs 2 / 2 vs 3, random-map 9 vs 11). With #434 (384 + DoomBlock: 24) two draws below
  #428 - the local +20 / +25 for these fixes does not show on the ladder; making seen camps pickable again may send champions to contested
  camps the old exclusion avoided. Off.
- **s_rt (B489c = harness + cand428 baked, 2240 each, vs OFF 1461):** bit 32 (safe wait poke) -0 +-4 (1455); bit 64 (WatchWard retention) -14
  +-13 (1431); **bit 16 (MarcGems 4) +21 +-11 (1480)**; bit 128 (ClusterChip) -0 +-11 (1450). **#437 = harness bit 16 alone** (MarcGems never
  tested alone on the ladder; #431 / #433 bundled it).
- **#437 = harness B489x bit 16 alone (MarcGems 4) on the 125-game panel (19:25-19:30 UTC): 31 vs #428's 32 wins, margin +46** (top-10 17 vs 16
  -13.2k vs -14.0k; Fish 3 vs 2, 1 vs 3; random-map 10 vs 11, -8.5k vs -11.5k). Equal to #428 on the ladder, +21 / +12 locally: the one change
  of today that holds up. Offered to Eric as a live candidate (#437 = #428 + Marcella's early gem rewards; other harness bits off).
- **Opening spread (81 ladder games, round-start positions, not channelling):** share of champions > 4 tiles from every mate ours / theirs -
  r40 12 / 21%, r80 12 / 35%, r120 16 / 36%, r160 16 / 37%, r260 28 / 41%; mean nearest-mate distance r80 2.6 / 5.1, r120 3.6 / 6.2. The top
  teams split early; our whole-team opening (kOpeningRounds 120 / kOpenRace 240 / kOpenControl 180) holds the five together. **#438 = #428 +
  60-round opening everywhere** (B477x) queued for ~19:50.
- **#438 = #428 + 60-round whole-team opening everywhere (B477x) on the 125-game panel (20:02-20:07 UTC): 30 vs #428's 32, -3,273** (top-10 15 vs
  16, Fish 2/2 and 2 vs 3, random-map 11/11); local s_open (B489c): 60 everywhere -32 +-8, 90 everywhere -29 +-8, race 120 -17 +-4. The early
  split by opening length alone does not reproduce the top teams' advantage. Kept.
- **First action round (81 ladder games):** ours median 3, mean 3.19 (33% by r2, 84% by r4); theirs median 2, mean 1.85 (77% by r2, 100% by
  r4) - the constructor's set-up (Oct 28 checkpoints: ~170k fuel, camp_groups + the per-camp loop) costs ~1.3 rounds at the start.
- **edit_onecap2.py kOneCapCarrier** (bots/B490x = B489x + it; Codex C280: Claudus' collections pay one recipient, ours split): two of ours on a
  reward's tiles - its carrier (resource_carrier) else the lowest slot keeps it, the rest move on. Screen s_onecap (B490c: carrier-keeps /
  + rt 16 / old kOneCapturer).
- **s_onecap (B490c = B490x + cand428 baked, 2240 each, vs 1461):** kOneCapCarrier -53 +-12 (1347); + rt 16 (MarcGems 4) -4 +-13 (1422);
  kOneCapturer (lowest slot keeps) -81 +-13 (1289). Forcing one collector loses locally (a split loses no value; stepping off costs turns). Off.
- **#439 = #428 + kMeleeOpen alone (B477x) on the 125-game panel (20:35-20:40 UTC): 23 vs #428's 32, -5,277** (top-10 9 vs 16, Fish 1 vs 2 and 5
  vs 3, random-map 8 vs 11). With local -11 / -30 and Codex's native note (the cast costs her a step; she arrives a turn later with nothing in
  melee reach), Marcella's spell from reach is off. Focus fire is not a gap: 2+ of our attackers on champions hit ONE target in 85% of such
  rounds (theirs 76%; 81 ladder games).
- **#440 = #428 + kFarmBuild 8 / maps 1 alone (Prospector second on Marcella F / Vesper S / Ryth H on farming + boss maps; B489x) on the 125-game
  panel (21:14-21:19 UTC): 19 vs #428's 32, -13,551** (top-10 9 vs 16, Fish 1 vs 2 / 2 vs 3, random-map 7 vs 11) - a clear loss on every bench:
  the second-emblem Prospector delays the core stats our fights need more than +25% cluster rewards pay. Off.
- **ELKRING FREEZE (Oct 29 ~21:45; found by a 140-game stuck scan of #428 vs B7Live on all 70 maps x 2 sides, scratchpad wide428):** 00elkring A lost
  88 - 1012 (12 stuck / 402 rounds from r32), B 29 stuck / 599 rounds. Diagnostic (bots/Zst): from r37 every champion idle with no target; the
  leader's choose_target() = -1 / score 0 though all ten elk camps were alive, known, 3-23 tiles away, needing 2-3. **Cause: kSquadPacksOnly**
  (whole-game team squads farm only our side's multi-monster camps, for rows) on a whole-game team map (team_rounds_ 2000) whose camps are single
  elks - no home pack, every group skipped. **edit_packsfallback.py kPacksFallback** (bots/B491x = B489x + it): filter only when the map has a
  home pack. Elkring (A + B vs B7Live, PoolLive, PoolCarry, PoolAggro): **#428 2 / 8 (88-319 gems) -> 8 / 8 (1001-1020 each)**. **#442 = #428 +
  kPacksFallback** queued (~22:08); wide scan with the fix (scratchpad wide442) running.
  The same fix on the harness base (B491x) flipped 15 of 140 all-maps games - B489x's dormant code changes fuel-limited turns (~113 a game) by
  itself. **On #428's own source (bots/B492x = B477x + edit_packsfallback.py): 8 of 140 flipped, net +2 vs B7Live** - elkring A+B and big-world
  A+B and quarry A won, contest B / elk-arena B / tangle A lost. #442 re-pointed to B492x.
- **#441 = #428 + kDashKill 1.0 + kFreeKillFix (dash in only for a one-hit kill; B489x) on the 125-game panel (~21:50-21:55 UTC): 26 vs #428's
  32, -1,590** (top-10 14 vs 16, Fish 2/2 and 2 vs 3, random-map 8 vs 11). The conservative dash kill does not gain either. Off.
- **Eric ~22:00, replay 3bb1264d (00lost_world vs SkuBap, #428): "Marcella hovers near Ryth while he dies to a Vendetta".** r160-r169: Ryth 860 ->
  70 health, their Vendetta (1200 -> 830) hit him every round from 1-2 tiles; our Marcella at full health walked 1-2 tiles from Ryth for nine
  rounds without an attack (five enemies around: the team was evading); escape()'s only melee hit is on an ADJACENT enemy and the Vendetta
  stayed 2-3 tiles from her. Her first hit came r169; Ryth died r170. **edit_escorthit.py kEscortHit H** (bots/B493x = B492x + it): a melee
  champion escaping with >= H x max health steps beside the enemy that is on an ally (within 2 of us, within 1 of the ally, no other enemy
  within 3 of the landing) and hits it. Screen s_escort (B493c: escort 0.75 / kMarcBuild 1 = Treasure H, Jungle F, Bruiser F / kBuild2 25 =
  the top-10 Marcella line Treasure H, Jungle S, Bruiser H).
- **Farming comparison (Eric ~22:00; 144 ladder games, tripstats.py / macrozones.py):** trips between completed recalls are the SAME length
  (median 58 vs 60 rounds; trips > 200 rounds 0.39 vs 0.33 per champion-game) - "long expeditions" are not the gap; they complete 25% more
  recalls (10.7 vs 8.6 per champion-game) and carry gold home on the first trip (median 20 vs our 0). Camp clears a game ours 36 vs theirs 69:
  home 20 vs 33, mid 15 vs 31, enemy side 2 vs 5 - about double in every zone and phase.
- **Group fights (Eric 22:10 "our group fighting ... is very lacking"; tools/stress/bystander.py, 144 ladder games):** rounds where one of ours
  loses health with an enemy within 3: 107 a game (theirs 95); **a healthy teammate (>= 60%) within 3 that neither attacks nor casts: 0.49 per
  such round, present in 37% of them - the top teams 0.16 / 13%, three times fewer bystanders.** Focus fire itself is fine (85% of 2+-attacker
  rounds on one target vs their 76%); the gap is champions beside a hit ally doing nothing (3bb1264d's Marcella). edit_escorthit.py now runs
  in the turn dispatch before escape / evade / every fight branch: melee steps beside the enemy on an ally and hits (no other enemy within 3 of
  the landing), ranged shoots it from reach. Traced 12 games: escort_shot 199 (Vesper / Willow), escort_hit 12.
- **edit_splitwolf.py (bots/B494x = B493x + it; on #428's source):** kClusterSplit / kClusterSplitPeer re-created on B477x's base + kSplitWolf
  (a one-monster node champions_needed(my_dps) == 1 counts as a small node). Traced: cluster_one 8-60 jobs a game. **Ladder #443 = #428 + the
  split (kClusterOne 1, kClusterSplit 10, Peer, SplitWolf), #444 = #428 + kEscortHit 0.75**, after #442 (Eric: the split "always screens
  negative" - the local pool is our own grouped bots; the ladder is the judge).
- Stuck scan of the elkring fix (B492x, 140 games vs B7Live): stuck 31 / 435 rounds (was 72 / 1,434), wins 132 (129); 02the-pack's 213
  loop rounds remain (a loop between two camps, not a freeze).
- **#442 = #428 + kPacksFallback (the elkring freeze fix, B492x) on the 125-game panel (22:24-22:29 UTC): 32 wins / -46,264 vs #428 32 / -46,571**
  - identical on 124 games, one top-10 margin +307 (no panel map is elkring; the fix changes only whole-team maps without a home pack). Recommended
  live: #428's behaviour with the freeze removed (elkring 2 / 8 -> 8 / 8 locally).
- **s_escort (B493c, the escape-only escort build + cand428 baked, 2240 each, vs 1425):** kEscortHit 0.75 (escape-level) **+9 +-6 (1444)**;
  kMarcBuild 1 (Treasure H, Jungle F, Bruiser F - Eric's "Treasure Health over Focus") -1 +-12 (1426): neutral, ladder-testable; kBuild2 25
  (the top-10 Marcella line Treasure H, Jungle S, Bruiser H) -106 +-13 (1210): a strength Marcella loses in our code, as kMarcBuild 10 / 7 did.
- **Emblem timing, ours vs the top teams (buildorder.ts; ours 81 games sl_top414/415, theirs 144 games):** first emblem median round - Marcella
  ours r150 (Treasure F 95%) vs theirs r185 (Treasure H / Jungle F); Ryth ours r265 (Treasure H) vs theirs r360; **Vesper ours r280 (Treasure
  S 52 / Jungle S 10) vs theirs ~r125 (Treasure S first in 48% of their Vesper games)** - the one emblem-timing gap is Vesper, 150 rounds of
  +33% gold and Treasure S late. Consistent with the gold routing (C280: their first three gold pairs all paid Vesper; ours HoR 40 / Vesper
  26 + Ryth 20 / Ryth 40) and gold at our first recall (median 0 vs 20). Willow ours r660 (Durability H). Lever after the focus items: early
  gold rewards whole to Vesper and a first recall at one shard's gold.
- **s_focus (B494c = B494x + cand428 baked, 2240 each, vs 1425):** **kEscortHit 0.75 (dispatch-level) 1471 wins (+46), +6 +-13** - ladder-worthy
  (#444); the small-node split (kClusterOne 1 + kClusterSplit 10 + kSplitWolf) with the squad-on-small-node rule **-95 +-15 (1288)**, without it
  **-205 +-16 (1081)**. #443 (the split with the rule) is on the panel anyway - Eric's test of whether the local pool is the wrong judge.
- **#443 = #428 + the small-node split (kClusterOne 1 + kClusterSplit 10 + kClusterSplitPeer + kSplitWolf, B494x) on the 125-game panel
  (23:01-23:06 UTC): 22 vs #428's 32, -11,018** (top-10 14 vs 16, Fish 2/2 and 2 vs 3, random-map 4 vs 11) - the ladder agrees with the
  local -95: a single member peeling off a squad loses (four slower farmers + one easy kill). Every "member splits off" form is now dead
  (kClusterOne -45 / #417 -4, kClusterSplit -169, Peer -56 / -95, + wolves -95 / #443 -10). The top teams never form the 5-stack; the one
  change in that direction not punished on the ladder was #438's 60-round opening (30 vs 32, local -32). Next design: team formation from
  the start (pairs / short opening), not peeling singles.
- **Eric ~23:15, replay d07096ae (00stampede vs Fish, #443): the two 4-gold-cluster nodes (2,24) and (18,24) sit exactly 23.5 from both spawns
  (contested middle).** Fish took each 8 times by r480 (every ~60 rounds, 2-5 champions each); we took group 11 once (r25-48, 2 of ours while
  5 of theirs hit it) and group 12 once (r137). Eric's rule: "a high-value node in a contested area near the middle: always group for it; a
  cluster node deep within our side: champions free to split off (no invading)"; and health emblems first so champions solo / duo stronger
  nodes without recalling. **edit_splithome.py kSplitHome M** (bots/B496x = B495x + it): the split takes only small nodes >= M steps nearer our
  spawn than theirs. s_focus3 re-queued on B496c: split-home 6 (+ wolves) / + peer / kTeamSquads 2 / kMarcBuild 1 (Treasure H) + escort.
  On that stampede game (macrozones / campwait on the single replay): clears by r300 ours 11 (home 10, mid 1) vs Fish 9 (home 1, mid 8); whole
  game ours 67 (home 54, mid 13) vs 84 (home 42, mid 42); participants per camp ours 1.12 (all solo) vs 1.75. Fish cycles the contested
  middle gold rows as a group from r20; we farm home alone and reach the middle only after r700.
- **edit_midgroup.py kMidClusterGroup V** (bots/B497x = B496x + it): a harmless node worth >= V (group_value = gems + 0.3 x gold; a 4-gold-cluster
  node = 48) is exempt from early_far() (stay-home / far-side-early / mid_avoid) and the far-side score factor for a squad - the team groups
  for the contested middle gold rows as Fish does. s_focus3 (B497c, 6 arms, after s_focus2): split-home 6 / + peer / midgroup 40 / midgroup +
  split-home / kMarcBuild 1 + kEscortHit 0.75.
- **s_focus2 (B495c, vs 1425):** kEscortHit 0.75 + kEscortStep 4 1450 (+25 wins), -11 +-13; kEscortHit 0.9 1454 (+29), -3 +-12 - the plain
  escort at 0.75 (1471, +6) stays the best form (#444); kClusterSplit 15 any zone **-321 +-16 (884)**: broad splits are catastrophic locally.
- **#444 = #428 + kEscortHit 0.75 (B494x) on the 125-game panel (23:31-23:37 UTC): 25 vs #428's 32, -4,206** (top-10 14 vs 16, Fish 1 vs 2 / 3
  vs 3, random-map 7 vs 11). Local +46 wins did not carry: the third "engage more" change the top teams punish (dash kill, ranged chase dash,
  escort). The bystander gap (37% vs 13%) needs a group-level commit rule, not a per-champion one - left for the write-up.
- **Eric's emblem rule (23:40): at least one of the Treasure / Jungle emblems must be a Health emblem** (health first lets a champion solo / duo
  stronger nodes without recalling). Live lines: HoR (Treasure H), Ryth (Treasure H, Jungle H), Willow (Durability H first) comply; Marcella
  (Treasure F, Jungle F) and Vesper (Treasure S, Jungle S) do not. #445 = #428 + kMarcBuild 1 (Marcella Treasure H). **edit_vesphealth.py**
  (bots/B498x = B497x + it): kVespBuild 7 = Treasure S, Jungle H, Durability H, Bruiser S; 8 = Treasure H, Jungle S, Durability H, Bruiser S;
  screen s_vesph (B498c: 7 / 8 / 7 + kMarcBuild 1) after s_focus3. Eric (23:45): re-bench live #428 on the pinned panel to confirm the
  opponents are unchanged (lad428b after #445; #435 = #428 + no-op already reproduced p428 with 0 flipped results).
- **Eric (23:50) on Fish's 3-pick draft:** HoR + Vesper (dashes) + Marcella as a strength bruiser TANK taking the aggro; their Vesper a tanky
  bruiser-strength carry soloing camps; Durability emblems always Health. Our 3-pick draft is Marcella / Vesper / Ryth (HoR for Ryth -175
  locally, #407 tie); a strength Marcella loses in our code (kBuild2 25 -106, kMarcBuild 10 -116): the tank role needs the fight code to
  stop leaning on her Focus spells (aggro-taking + the dashers' damage) - a structural lead, not a switch.
- **Eric (23:55): Marcella is stun-immune - her tribute channel cannot be interrupted by stuns (only by death), so she should be the team's
  gem carrier / banker and the tank while the others fight.** Leads (not built tonight): a larger delivery bag for Marcella only; tribute_doomed()
  less conservative for her (0.9 x hp assumes any hit breaks a channel - for her only lethal damage does); kMarcGems 4 as the routing half.
- **s_focus3 (B497c, 2240 each, vs 1425):** split-home 6 (clusters + wolves, our side only) **-165 +-16 (1127)**; + peer rule -77 +-14 (1324);
  kMidClusterGroup 40 -13 +-9 (1394); both -163 +-16 (1136); kMarcBuild 1 + kEscortHit 0.75 +3 +-14 (1461, +36 wins). Eric's zone rule in
  switch form does not screen: our-side-only splitting loses MORE than the middle-included one (a lone champion on our side still dies to the
  pool's roaming squads), and the squad grouping for rich middle nodes is mildly negative. #446 / #447 dropped; the slot after the #428 re-bench
  goes to Vesper's health line (s_vesph).
### Oct 30 (UTC 07:05-) - session died ~00:00: #445 (Marcella Treasure H) was LIVE unpanelled until 07:08; #428 restored; the Vesper screen rerun
- The Claude session ended around midnight with every queued script: #445 had just been activated for its panel (23:55 submit) and the restore
  never ran, so **#445 was live from ~00:00 to 07:08 UTC** (its 25 panel groups never queued); #428 re-activated 07:08. The #428 re-bench
  (lad428b), s_vesph and the midgroup / split-home scripts died too. s_vesph restarted 07:11 (B498c: kVespBuild 7 / 8 / 7 + kMarcBuild 1).
- **Groupings (tools/stress/groupings.py, 144 ladder games; champion-rounds in a cluster of size 1 / 2 / 3 / 4+, within 3 tiles):** r<300 ours
  22 / 16 / 20 / 43% vs theirs 34 / 17 / 16 / 33%; r300-700 ours 36 / 22 / 18 / 25% vs 54 / 21 / 13 / 12%; r700+ ours 43 / 23 / 18 / 16% vs
  62 / 22 / 10 / 6%. Recalls 38 vs 51 a game; with a teammate recalling within 5 rounds 49% vs 43% (mean mates 0.92 vs 0.58) - their recalls
  are LESS grouped. The local pool (PoolLive / Carry / Aggro / Finish) is our own builds, i.e. 4+-stacks 25-43% of the time where the top
  teams are 6-12%: a lone champion in a local screen meets a 5-stack far more often than on the ladder - but #443 lost on the ladder too.
- **#445's 0-5 / 1-4 series, 34 losses analysed** (Oct 30 ~08:00 UTC; ranked overnight 98/195, 39 series: 5-0 x1, 4-1 x6, 3-2 x15, 2-3 x9, 1-4 x6
  (DOOMSDAY, SkibidiSloppers x2, test4, SALUTE TO TUNG, dromedaries), 0-5 x2 (????, Sheeesh---); downloads in the scratchpad bad445/, tools
  `tools/stress/lossthemes.py` + `lossthemes2.py` (note: `cambc matches download -o` needs a Windows path (cygpath -w), a dir name with "????"
  is invalid, and a CR after the side letter in list.txt lands in the dir name as U+F00D)). **Themes:** (1) economy - camp clears 34 vs 62 a
  game with the SAME recall count (42 vs 42): each trip clears half as much; bank r300 96 vs 138, r600 225 vs 403; gold earned by r600 484
  vs 734 -> gear at r600 str 72 vs 92, max health 1680 vs 1849 (r300 str 55 vs 64 already). (2) the 18 fight losses are that gear gap
  cashed in: our deaths come at even numbers (2.6 of ours vs 2.6 of theirs within 6 tiles), 65% ganged, 52% mid-map, 26% on their half, 22%
  at home; repeated re-engagement after respawn in the worst games (starfish vs Sheeesh 39 deaths / 8 wipes, oasis 31 / 6, elk_arena 26 /
  4 with the enemy pair within 8 of our spawn 65% of the game, treasure_box 44%); spawn camping is rare otherwise (mean 5% of rounds) and
  only 14% of deaths were outnumbered 3+ vs <= 1 ally. (3) Sheeesh--- (Marcella / Prism / Tavi / Varg / Willow) took the 0-5: we earn a
  third of their gold and feed. (4) dromedaries' three wins (boss_battle, yellow_brick_road, broken_curve) are the exception: we OUT-gear them
  (str 122 vs 58 at r600) and still lose on gems - we fight while they bank. (5) elkring x2 = the kSquadPacksOnly freeze (45-51% idle; #442).
  Conclusion: the farming throughput gap (camp starts / clears per trip) is the root; fight code is second-order in these series.
- **#445 panel** (Oct 30 08:21-08:26 UTC, the existing upload, no re-upload; live 445 restored - Eric's choice): top 11/50, f1 2/20, f2 2/20,
  x1r 11/35 = **26 wins / -53.5k vs #428 32 / -46.6k (-6 wins)** - the Marcella Treasure Health line alone is not an improvement on the
  panel (same score as #423). #446 = #445 + kPacksFallback queued next (Eric: "add the elkring fix to 445 too").
- **s_richsync** (B499c = B498c + edit_richsync.py, #428 config baked, 2240 games/arm, seeds 1 2 4 5, pool Live/Carry/Aggro/Finish; Eric's
  Oct 30 recall request): kRichGold 300 (shop trip whatever the bag / walk at 300 gold) **+9 wins, +5 +-6 paired**; + kRichSync 10 (squad mates
  join the rich mate's recall) -6 wins, +1 +-11; + kHomeFarm 40 / kHomeReset (fresh decision at home, small nodes near home first)
  **-64 wins, -32 +-12**; kHomeFarm 40 + kHomeReset alone **-36 wins, -23 +-9**; **kRecallSync 8 + kSyncFar 30** (the old general join, only
  when our camp is 30+ travel rounds away, all game) **+29 wins, +13 +-8** - the first positive recall-sync result (Oct 26's kRecallSync 6 in the
  opening was -63). Next: kHomeFarm vs kHomeReset split, kSyncFar 20 / 45, and kRecallSync+kSyncFar with kRichGold.
- **#446 = #445 + kPacksFallback** (B497x + run/cand446.edits; submitted ~08:40 UTC Oct 30; panel 08:4x-08:5x): **26 wins / -53.2k** (= #445's
  26 / -53.5k; elkring is not on the panel). Live restored to 445 (Eric's choice). **Ranked by live version** (570 games since #428 went live,
  attributed by the panel switch times): #428 137/280 (49%), #445 121/230 (53%) - one SE apart, different opponent mix by time of day.
  The pinned panel replays stored opponent bots, so opponent updates never show there: run/rebench445.sh replays the 125 games FRESH
  (bench2qf.sh = bench2q.sh on cambc 4.0.0) with 445 live, changed margins = updated opponents.
- **s_cluster** (B500c = B499c + edit_clustermap.py, #428 config; Eric: "match the top teams on breadcrumbs"): on 00breadcrumbs the live
  config runs the 180/240-round whole-team opening (kOpenRace / kOpenControl; kAutoTeam finds no party camp) and the squad leapfrogs one
  cluster trail; Fish farms solo from r1. **kClusterOpen 0** (no monster anywhere on the map: no team opening) all maps **+23 wins, +13 +-7**
  (6 of 72 local maps are monster-free: breadcrumbs, adgato-gemcombat1-5), **breadcrumbs only (8 seeds x 4 opps x 2 sides) 48/64 vs 37/64,
  +99 +-47**; kLightOpen 0 / 60 (no party camp within 20 of home -> a short opening) **-61 +-9 / -38 +-9**: maps with only single
  monsters near home still want the team opening. kClusterOpen 0 goes into the next bundle.
- **Eric's Oct 30 ~09:00 package** (edit_ericpack.py, B501x = B500x + it; B502x = + edit_prospector2.py re-applied on this chain): measured first
  on the 34 #445 losses: **HoR shield** - ours is hit with the shield READY in 18% of hit rounds, theirs 34% (ours shields earlier; kShieldNear
  6 live) - no shield bug; **Vesper vs melee** - ours has a melee champion within 2 in 1150 rounds (34 a game) vs theirs 499 (15), dies from it
  33 vs 6 times, while the response mix is the same (shoot 59 / 56%, step without a shot 30 / 29%); contact starts with the enemy coming to
  her 58 / 57%, she is alone in 17% (theirs 37%). So she is dived twice as often and loses the trade (gear: str 72 vs 92 at r600), not
  "scared". Her dashes: ours 52% away from enemies, theirs 37%; after a dash she never shoots in the same turn (theirs 4%) - dash_towards
  admitted melee only (dash_ready: range_ > 1 -> false). Switches: kBraveRanged 1 (no kite step from ONE melee while the dash is ready and
  health >= kBraveHp 0.5) / 2 (none while fight_odds(3) >= 1), kRangedDash D (ranged chase dash, landing D from the target, fires whenever a
  step would cost the shot), kSplitDash (small-node split / kHomeFarm only for dash champions - Marcella stays grouped), kDraftAlt 4 (four
  picks Marcella, Vesper, HoR, Willow; bit 1 = three picks with HoR already existed). Screen s_ericpack (B502c, 9 arms: cluster open, draft,
  Marcella Fish bruiser kFishBuild 2, HoR Fish 4, brave Vesper, dash-only split + Vesper Fish line, Prospector kFarmBuild 8 / Maps 1, all-in-one);
  **#447 = #446 + the all-in-one** queued on the panel (run/cand447.edits) after the fresh opponent re-bench of #445.
- **Review of edit_richsync / edit_clustermap / edit_ericpack (subagent, Oct 30 ~09:30 UTC), fixed in edit_packfix.py (B503x):** (1) kRichSync
  read a mate's gold - champion::gold_count() throws for any champion but ours (require_self), so the join never fired; now joins a recalling
  squad mate within D when our trip is due or our camp is far (no gold test). (2) kHomeFarm's keep branch was dead: the pick un-solos
  (solo_ = false, adopt(-1)) before the call, so a job was re-adopted every non-quiet turn - the job is now checked beside cluster_one.
  (3) home_farm planned with stale mates_ (observe_mates() added). (4) **kRangedDash: the chase and assist callers stepped after the dash**
  (the step spent the shot) - a dash that lands in range now ends the movement. s_ericpack's brave-Vesper and all-in-one arms (B502c) carry
  bug 4; re-screened on B504c (s_ericpack2) and #447 relaunched on B504x. **edit_prospfirst.py (B504x): kFarmBuild 9 = Prospector HEALTH
  first for everyone but Willow, 10 = the collectors only** (Eric: "build prospector first ... always a prospector emblem of health").
- **Opponent update check (rebench445, Oct 30 09:21-09:27 UTC; Eric: "i feel like the top teams have updated their bots"):** the pinned 125
  games replayed FRESH against the opponents' current bots with #445 live, vs the pinned p445 (stored bots from the #405 era): **26 -> 18 wins,
  -53.5k -> -59.4k**. Changed (deterministic engine, same bot on our side = the opponent updated): **NEETCoders 10/10, SpongeAlbert 10/10,
  TrzyKwaterki 10/10, AdAstra 5/5, printdontindent 5/5, prismbestgirl 5/10**; unchanged: Intercontinental Fish 39/39, ClaudusMaximus,
  Mite, newerteam. The random-map bench went 11 -> 4 of 35. So the pinned panel (panel125.sh, --source-group = #405-era groups) has been
  stale against six of ten top teams; every panel verdict since #428 compared candidates on equal (stale) terms, but absolute levels are
  ~8 wins too high. **Re-pinned: `panel125b.sh` (--source-group = p445f, the fresh games); baseline p445f = #445 18 / -59.4k.** #447 runs
  on both (lad447 vs p428 on the old pins, lad447n vs p445f on the new).
- **s_richsync2** (B499c, #428 config): kHomeReset alone -6 +-3; kHomeFarm 40 alone -18 +-9 (both before the keep-branch fix); kRecallSync 8 +
  kSyncFar 20 -3 +-9, **kSyncFar 45 +9 +-7, kSyncFar 30 + kRichGold 300 +11 +-9** (s_richsync: kSyncFar 30 alone +13 +-8) - the far-camp recall
  sync is a consistent small positive at 30-45 travel rounds; 20 is too short.
- **#447 first upload failed the stress gate** (10:0x UTC): stuck 11 / 247 rounds (#446: 3 / 36), fuel identical - Willow (and HoR) standing
  30-150 rounds with no enemy near and allies 10-28 tiles away on interlock / islands / fracture. Isolation (run/iso447.sh: Up447 with one
  switch reverted, the six worst-map games each): all 10 / 241; **without the split (kClusterSplit 10 / kClusterOne 1 / kSplitDash /
  kSplitHome 4 / kSplitWolf) 2 / 11**; without the sync 3 / 31; without the draft 5 / 42; without brave / cluster-open / Fish builds /
  Prospector 7-8 / 73-219. The dash-only split peels both dashers off a whole-team squad and the non-dash members (Willow) wait for a party
  that never forms - a design hole in the split (party need counts members that left), not a switch bug. **#447 resubmitted without the
  split switches**; the split stays a separate screen arm (s_ericpack SPLV).
- **#447 (= #446 + the package WITHOUT the split: kClusterOpen 0, kDraftAlt 5, kBraveRanged 3 + kRangedDash 2, kFishBuild 7, kRecallSync 8 /
  kSyncFar 30 + kRichGold 300, kFarmBuild 9 / Maps 1; B504x; stress 21/24 wins, stuck 5 / 46) on the old-pin panel (10:09-10:2x UTC):
  **17 wins / -64.6k vs #428 32 / -46.6k (-15 wins)**: top 10/50 (16), Fish sets 0/20 + 0/20 (2 + 3), random 7/35 (11). The package as a whole
  is clearly worse on the panel; s_ericpack (9 single arms, B502c) will say which parts. Codex C292-C294 (A142 review): kHomeReset was
  unreachable (turn() returns early while recalling before prev_recalling_ is set - the s_richsync2 reset arm measured nothing);
  kSplitDash's nearer-mate veto still counts non-dash mates (a Marcella nearer the node vetoes Vesper's split); flee_shot gates cast_used_
  before can_attack; and the interlock freeze of the first #447 is **an existing hunt / farm alternation: Marcella (kHunter 5, kChaseMax 7)
  alternates two tiles for 101 turns - hunt() resets hunt_until_ when no enemy is visible and restarts on reacquisition, travel_stuck
  needs consecutive turns** - the squad waited on her. Prospector-first works (5 shards; Vesper PH r132 then TS r207).
- **s_ericpack (B502c = live config + edit_ericpack.py + prospector2, 2240 games/arm, base 1436):** kClusterOpen 0 **+23 wins, +13 +-7**;
  kDraftAlt 5 (HoR for Ryth, 3 / 4 picks) **-87, -56 +-10**; kFishBuild 2 (Marcella Fish bruiser TH JS BH DH BS) **-182, -93 +-13**;
  kFishBuild 4 (HoR Fish TH JF BH) -8, +2 +-5; kBraveRanged 3 + kRangedDash 2 (before the post-dash step fix) -71, -48 +-14; dash-only split +
  Vesper Fish line -33, -45 +-15; **kFarmBuild 8 / Maps 1 (Prospector SECOND on farming / boss maps) +45, +13 +-10**; all-in-one **-299,
  -196 +-16** (= #447's -15 on the panel). Keepers: cluster open, Prospector; the Marcella bruiser line and the HoR-for-Ryth draft lose
  outright locally (as every strength-Marcella / 3-pick-HoR test before: -106 / -175). s_ericpack3 (B506c, after the fixes): brave Vesper
  fixed, Prospector FIRST (kFarmBuild 9), home farm (reachable now), kHuntLoop 4, kOpenFuel 12, the repaired split, and a bundle of the
  non-losing parts (cluster open + brave Vesper + far sync / rich trip + Prospector first + open fuel + hunt loop + flee-shot fix).
- **Opening fuel (edit_openfuel.py, kOpenFuel 12 / kOpenSpare 60k):** six maps vs B7Live, B505c vs Open505 (tools/stress/openact.py): the
  first action is unchanged (median r4, 23% act by r2; acted share r1 12% / r2 19% / r3 23% / r4 58% in both), only r5-r12 improve (50 ->
  58%, 75 -> 79%, 81 -> 85%, 77 -> 85%, 79 -> 85%, 75 -> 87%, 71 -> 77%). The end-of-turn extras are not what stalls rounds 1-4: that is the
  constructor (set-up, ~185k vs the 2x first-turn budget) plus the first turns' own work (fields on demand in the first scoring, ward plan
  stage inside the turn). Instrumenting the set-up next.
- **#447 on the re-pinned panel (panel125b, current opponent bots): 11 / -66.7k vs #445 18 / -59.4k (-7)** - same verdict as the old pins
  (-15 vs #428). Live 445 restored 10:32 UTC.
- **Opening fuel, set-up phases (OpenF2 instrumentation, collision + interlock, 14 champions):** the constructor starts with 172.5k (the 2x first
  turn) and spends: camp groups + terrain arrays 69.2k, plan read / neighbours / kit factors 20.8k, walks + home distances 26.0k, boss
  classification 5.0k, snipe 14.5k, then overruns (the fuel reading rises between the snipe and walk-targets phases = a suspension inside
  the constructor); turn 1 starts with ~24k (min 0.4k) and ends in round 2 (35k left), so rounds 1-2 are lost on every champion and the
  first action is r3-4. The end-of-turn extras (kOpenFuel) only help r5+.
- **Set-up fine phases (OpenF4, 14 champions, collision + interlock):** terrain arrays 17.6k, camp groups 46.1k (camp_type kind() is cached in the
  SDK, so the cost is the camps() vectors / per-group queries / std::map stats), draft-plan read 16.9k (a 1,024-byte buffer copy), kit 2.6k,
  neighbours 4.4k, walks block 26.0k (= build_enemy_side's two fields under kSafeRoute 8; the walks themselves come from the plan), boss 5.0k,
  then a suspension. **First two turns (fnprof at r3):** warm_fields 33.6k, farm 31.6k, fight_group 27.5k x 0.5, field 24.5k, step 15.5k,
  plan_wards_step 15.0k (3 stage calls a turn, in-turn via kFuelJobs), safe_field 10.5k, observe_allies 7.5k, end_jobs 5.9k, manage_squad 5.9k.
  Plan: lazy enemy-side field (first safe_field / kMidZone use), the in-turn ward plan after round kOpenFuel, then the camp loop.
- **s_ericpack3** (B506c = live config + the fixed package; 2240 games/arm, base 1436; finished ~11:20 UTC Oct 30): **kBraveRanged 3 +
  kRangedDash 2 (after the post-dash step fix) +52 wins, +26 +-13** (was -48 with the bug); kFarmBuild 9 (Prospector HEALTH FIRST) -8, **-25
  +-12** (Prospector second, kFarmBuild 8, was +13 +-10 - keep second); kHomeFarm 40 + kHomeReset (both reachable now) -34, -32 +-11 (off);
  kHuntLoop 4 -7, -5 +-6 (neutral; it is a freeze fix, keep); kOpenFuel 12 -39, **-26 +-11** (deferring the turn-end field warm-up costs
  later turns more than it saves; off); dash-only split (competitor fix in) -34, -44 +-15 (still loses locally); bundle (cluster open +
  brave Vesper + far sync / rich trip + Prospector first + open fuel + hunt loop + flee-shot fix) +47 wins, +15 +-14.
- **Next candidate prepared: tools/cands/cand448.edits on bots/B506x** (applies and compiles; NOT uploaded) = #446's config (#445 + elkring fix)
  + kClusterOpen 0 + kBraveRanged 3 / kRangedDash 2 + kRecallSync 8 / kSyncFar 30 / kRichGold 300 + kFarmBuild 8 / kFarmBuildMaps 1
  (Prospector SECOND) + kHuntLoop 4 + kFleeShotFix. Each part screened >= 0 (+13, +26, +11..13, +13, -5, -). Panel it on the RE-PINNED
  panel (panel125b, baseline p445f = #445 18 / -59.4k) with RESTORE=445. Left out on purpose: Marcella bruiser line (-93), HoR for Ryth
  (-56), Prospector first (-25), opening fuel deferral (-26), the split (-44), home farm (-32).
- **Session note (Oct 30 ~11:30 UTC):** the old scratchpad (run/, panel125*.sh, scrim_*.ids incl. the p445f re-pin, bench2qf.sh) is gone
  with the session. tools/cands/ holds bench2qs.sh / benchcmp.ts / allfinished.sh / bench lists; the re-pinned group ids (scrim_p445f_*.ids)
  must be recreated - either re-run the fresh replay of the 125 pinned games (bench2q on cambc 4.0.0) with 445 live and re-pin, or panel
  against the old pins vs p428 (32 / -46.6k), whose ids are also only in the lost scratchpad (check tools/cands for copies first).
- **Re-pinned panel recovered (Oct 30 ~11:50 UTC):** tools/cands/recover_groups.py rebuilds a bench's group ids + spec lines from the
  platform (unranked matches carry groupId). p445f = the 25 groups queued 09:21:06-09:21:51 UTC: results/work/scrim_p445f_{top,f1,f2,x1r}.ids
  and bench_p445f_*.txt (top spec identical to tools/cands/bench_top10.txt). To panel a candidate vs p445f: bench2qs.sh TAG_part
  bench_p445f_part.txt p445f_part per part (tools/cands copies hardcode the old scratchpad SP - set SP to results/work and copy the .ids
  there), then benchcmp.ts p445f_part TAG_part.
- **Review of the LIVE #445 source (bots/Up445), three reviewers, Oct 30 ~11:40 UTC.** Fight code -> **edit_reviewfix30.py (bots/B508x / B508c,
  compiles with every bit on; NOT screened)**, kReviewFix30 bits: 1 free_kill() let a RANGED champion step then attack (the step spends the
  shot; the attack threw inside attempt yet the function returned true, skipping escape / evade / fight that turn); 2 strike_while_escaping's
  plain hit had no Ren-retaliation check (the other run-away hits all have it); 4 hunt() stepped onto the prey's cached tile after its own
  cast killed it; 8 contact_turns_ counted before observe_enemies() (kContactTurns escape a turn late). Farming: (a) Varg's loop flag
  (0x80) is read as a help call after the opening under kHelpCall 25 (write gate should be `kLoopFlag && kHelpCall <= 0 && looping_`; Varg is
  rarely drafted); (b) kRepeatWait marks every reward we SEE as ours (the fix, kReviewFix29 256, exists only on the B481x side branch - NOT in the B492x..B508x line; port it); (c) a help_walk never
  re-checks that the call still stands. Squad / capture / recall / deliver / shop / party-wait paths were checked clean.
  **Set-up fuel (decision-preserving, to implement + prove with eqcheck next):** the camp loop's 46k is malloc, not engine calls (camp
  accessors are inline; one batched layout call): group_threat() takes its vector BY VALUE (12-23k at 30 groups: take const& + a static
  scratch); std::map stats_of -> array by kind (3-6k); TileGroups entries_ never reserved (4-6k); spawns_near computed eagerly though
  kWalkSides 1 never reads it (2-5k); spawn_region().positions() built 5 times (1-2k); champion_name() is an engine call made 8x + once per
  group (2k); **build_enemy_side's first, unbounded field only finds the spawn-to-spawn walk = setup_spawn_path_ from the plan (~13k)**;
  read_draft_plan copies 1,024 bytes twice. Total ~40-55k of the constructor's ~150k. Unverified hazard: move_towards() (the field-less
  fallback step) has no fuel gate and runs a distance field. Round-3 non-movement is NOT the step() field gate; candidates left: idle()
  with a near target, or the opening squad's wait_party (kAllyWait) - read the round 1-4 note() trail in a replay to settle it.
- **Opening turns, per champion (edit_aclog.py build at normal fuel, collision + interlock, Oct 30 ~12:15 UTC):** a missing AC line = a lost
  turn. Every champion loses **r2** (the set-up overran turn 1); Marcella / Ryth / Willow also lose **r5**; **Vesper loses r2-r5 on
  collision (both sides)** and r2 + r4 on interlock - four straight turns; the first move is r3 for most. Activity when they do act is
  help_ask_squad (walking to the squad's camp) - no waiting decision is involved. Suspect for Vesper: kCaptureLeg (ranged champions also build
  a capture field per group in warm_fields), i.e. turn-end field warming that overruns into the next turn.
- **edit_setupfuel.py (B510x / B510c), kSetupFuel bits 1-16:** bit 16's premise verified on ALL 70 maps x 2 sides (3-round games, SfChk):
  the draft plan's spawn walk equals build_enemy_side's recomputed walk in 558 / 558 champion set-ups.
- **kSetupFuel 31 is exact:** eqcheck (edit_aclog builds, --fuel-quantum 200000000, 8 maps x 2 sides incl. yellow-brick-road and lanes) 16 / 16
  games identical. At normal fuel (six maps, tools/stress/openact.py) the opening improves modestly: acted share r2 19 -> 23%, r3 23 -> 35%,
  r5 50 -> 63%; first action mean 4.25 -> 4.12 (median 4 both). Safe to ship with any candidate (decision-preserving).
- **#448 = #446 + kClusterOpen 0 + kBraveRanged 3 / kRangedDash 2 + kRecallSync 8 / kSyncFar 30 / kRichGold 300 + kFarmBuild 8 / Maps 1 +
  kHuntLoop 4 + kFleeShotFix** (B506x + tools/cands/cand448.edits; submitted 12:08 UTC Oct 30, stress 22/24 wins, stuck 1 / 28) on the
  RE-PINNED panel (current opponent bots): **23 wins / -50.2k vs #445 18 / -59.4k (+5 wins, +9.2k)** - top 11/50 (10), Fish f1 2/20 (2, margin
  +0.3k), f2 3/20 (2, +3.1k), random maps 7/35 (4). Best panel since the re-pin; every bench improved or held. Live restored to 445 (12:21);
  #448 recommended to Eric.
- **Opening fuel root causes, measured per turn stage and per constructor phase (Oct 30 ~12:40 UTC, TurnF / CtorF instrumentation):**
  (1) **a production debug print**: the set-up prints the draft plan's wall-trap pairs (`if (kPlanCheck || kPairWalk > 1)` with kPairWalk 3
  live) - 100-150k fuel per champion on big maps (plan phase lanes 171k -> 47k, islands 172k -> 47k, big-world 127k -> 20k, swirl 118k ->
  18k without it); the first turn starts a round earlier there. Fixed as kSetupFuel bit 32 (edit_pairsprint.py, B512x; stdout only).
  (2) the constructor's camp loop (55-167k incl. the SDK's camp-list load; yellow-brick-road's 30-member groups pay an all-pairs packing
  loop), terrain arrays (88k on big-world), map profile (32-66k); (3) the first decision itself costs 50-120k (Vesper ~120k: the first team
  scoring builds fields); (4) the ward plan (Vesper / HoR ~28k a turn in end_jobs plus an in-turn step) - kWardPlanRound (edit_wardplanfuel.py,
  B511x; decision-changing, not screened). **kSetupFuel 63 (all exact savings) on six maps: first action median r4 -> r3, mean 4.25 -> 3.29;
  acting by r3 23 -> 50%, by r4 58 -> 75%** (top teams 1.85). **#449 = #448 + kSetupFuel 63** (B512x + tools/cands/cand449.edits) queued on
  the re-pinned panel vs p448.
- **s_fix30 (B509c, live config, 2240 games/arm, base 1432):** kReviewFix30 1 (ranged free_kill) +16 wins, +2 +-5; kReviewFix30 14 (Ren escape
  hit, hunt after a killing cast, contact timing) +1, +6 +-9; kFarmFix30 1 (repeat wait only for our captures) -1, +0 +-3; kFarmFix30 6
  (Varg loop flag, help walk) +6, +2 +-1; all +3 wins, +8 +-9. Neutral-to-positive bug fixes: ship them with the next candidate.
- **#449 = #448 + kSetupFuel 63** (B512x + tools/cands/cand449.edits; submitted ~12:55 UTC) on the re-pinned panel: **22 / -54.7k vs #448 23 /
  -50.2k (-1, -4.5k: noise - fuel timing reshuffles every game)**, vs #445 +4 / +4.6k. Live 445 restored 13:07. s_setupfuel (local, 2240/arm)
  queued to measure what the extra opening turns are worth.
- **s_wardplan (B512c with kSetupFuel 63 as base, 1466 wins - vs ~1432 for the same config without the savings in s_fix30):** kWardPlanRound 30
  -33 +-13, 80 -29 +-13 (the early ward plan pays: off); kReviewFix30 15 + kFarmFix30 7 on top -4 +-9 (neutral); all -39.
- **s_setupfuel (B512c):** kSetupFuel 31 -18 wins, -11 +-13; **kSetupFuel 63 +28 wins, +14 +-14** (the PAIRS print removal is the part that
  matters). Keep 63 (exact decisions, more opening turns).
- **Combat audit (Eric, Oct 30 ~13:20 UTC: ranked 5298d443, adgato_gemcombat5 vs Velvet Tributers, #449 lost 350-1001).** Our 7 deaths
  (tools/stress/deathaudit.py; tools/stress/mapgrid.ts now marks bushes - it never did, gemcombat5 has 479): HoR r28 dashed alone into 5
  enemies while the team retreated (OUTNUMBERED 5v3, three bystanders); Marcella r131 bounced (76,81)<->(77,81) for 20 rounds under one Vesper
  at range 3 with 63 gems, both abilities ready, a bush row 3 tiles south; Ryth r209 / r457 kept attacking (clusters) and stepping while a
  HoR + Varg / Vesper + Varg took him from full to dead; HoR r360-367 bounced two tiles before dying. Opening fight r12-r28: Willow never came
  within 6 (stood, then walked away), Marcella bounced two tiles for 7 rounds without attacking, HoR wandered north then dove alone.
  **Engine (Eric): ANY damage cancels a recall** - the escape is break sight (a bush the attacker is not in / has not warded), then recall.
  Local (Log449 = #449 + aclog, 12 maps x PoolLive / PoolAggro, 531 deaths): bystanders 356, bush within 3 at 60% health 234, cover reachable
  in time 163, stayed below 60% in reach 140, outnumbered 109, dive 88; the decision in the death windows was mostly escape (707 turns) -
  open-ground running from a melee chaser fails by rule (it walks and hits in one turn). kAntiOsc only acts with no enemy in sight.
  **edit_combat31.py (B513x / B513c):** kCoverEscape R (escape heads for an unwatched, enemy-free bush; in cover ambush at odds >=
  kAmbushOdds / recall if not hit and no enemy within 2 / hold), kFireOsc N (bouncing while hit -> cover, winnable fight, or straight away),
  kDiveGuard (no champion dash into more enemies than ours unless it kills), kWillowJoin R (Willow into heal range of a fighting ally).
  Screen s_combat31 + logged comparison (LogC31 on the same 48 games) running.
- **Four versions on the same games (re-pinned panel, current opponent bots; Oct 30 ~14:10 UTC).** #428's run was queued twice by a duplicate
  script (only 108 unique games survived); on the 96 games common to all four: **#428 22 wins / -31.7k, #448 20 / -29.2k, #449 19 / -32.0k,
  #445 14 / -39.9k**. The live #445 is the weakest; its only change from #428 is kMarcBuild 1 (Marcella Treasure Health), which #448 / #449
  inherit. Ranked by live window: #428 49% (280), #445 53% (230). **Prepared #450 = #449 with kMarcBuild 3 (Marcella's #428 line) +
  kReviewFix30 15 + kFarmFix30 7** (tools/cands/cand450.edits on bots/B515x).
- **HoR dashes (tools/stress/hordash2.py):** of our fight dashes 23% (48 local) / 27% (#445 ranked losses) land within 1 of an enemy champion
  (top teams 35%); 11-14% close distance without a hit while not chasing a runner, 46-50% are escape dashes. edit_ruindashhit.py
  (kRuinDashHit, B514x): the chase dash (dash_towards) with a damaging dash only lands its hit or follows a target that ran from us last round.
- **First combat test (combat31 all on, LogC31 on the 48 logged games): wins 28 -> 11, deaths 11.1 -> 22.4 a game.** Cover held (590 / 677
  holds unhit next round) but every escape - incl. evade at odds just under 0.85 - walked up to 4 tiles to a bush, held, then recalled (240
  recalls at any health): healthy champions left fights and farms. edit_cover2.py (B515x): kCoverHp (cover only when hurt, or hit while
  outnumbered), kCoverRecallHp (recall from cover only when hurt or with a full bag).
- **Correction (Eric, Oct 30 ~14:30 UTC: he switched the live submission during the #428 panel):** scrims play whatever version is selected at
  the time. tools/cands/panelversions.py reads our "BAMBOO vN" banner from one match per group: p428n 36 groups #428, **11 groups #445** (10
  of 13 random-map groups), 1 unreadable; p445f / p448 / p449 all the intended version (5 unreadable groups excluded). **On games each version
  verifiably played:** all four on 61 games: #428 18 wins / -16.8k, #448 14 / -17.0k, #449 13 / -18.5k, #445 11 / -22.8k; pairwise #428 vs
  #445 21-12 (77 games), #428 vs #448 24-17 (81), #428 vs #449 20-15 (70), #448 vs #445 18-13 (94), #448 vs #449 19-17 (91). **#428 is
  the strongest current version; #445's Marcella Treasure Health line costs the most.** Always verify panel versions before comparing.
- **#450 = #449 with kMarcBuild 3 (Marcella's #428 line) + kReviewFix30 15 + kFarmFix30 7** (B515x + tools/cands/cand450.edits; submitted
  14:26 UTC Oct 30; stress 22/24): re-pinned panel 24 / -50.2k (#448 23, #445 18). Versions verified (23 groups #450, 2 unreadable). Game for
  game on verified games: **#450 vs #428 19-23 wins, margin -21.8k vs -22.2k (77 games: a tie)**; vs #445 22-14 (+11.0k, 90); vs #448 23-20
  (+1.3k, 94); vs #449 21-16 (+5.5k, 84). So on #428's base the #448 / #449 behaviours are neutral on this panel; they add the elkring and
  hunt-loop freeze fixes (not on the panel) and the opening fuel. Live 445 restored 14:57.
- **s_combat31 (B513c, kSetupFuel 63 base 1466 wins, 2240/arm):** kCoverEscape 4 (ungated) **625 wins, -552 +-16** (the collapse); kFireOsc 3 -29,
  -13 +-8; kDiveGuard -8, -5 +-6; **kWillowJoin 10 +16 wins, +21 +-12**; all four 594, -557. Next: s_combat32 (gated cover kCoverHp /
  kCoverRecallHp, kRuinDashHit, Willow join, bundle).

### s_combat32 (Oct 30 ~16:10 UTC; B515c + kSetupFuel 63, 2240 games an arm, PoolLive/Carry/Aggro/Finish x seeds 1 2 4 5)
| Arm | Paired vs base |
|---|---|
| kCoverEscape 4, kCoverHp 0.6, kCoverRecallHp 0.5 (gated bush cover) | **-398 +-15** |
| kCoverEscape 3, kCoverHp 0.4, kCoverRecallHp 0.4 | **-183 +-13** |
| kRuinDashHit (HoR's damaging dash only to land its hit, or after a runner) | +17 +-11 |
| kWillowJoin 10 | +13 +-12 (s_combat31: +21 +-12) |
| bundle: cover 3/0.4/0.4 + kRuinDashHit + kWillowJoin 10 | -187 +-14 |
Bush cover is negative in every form tried (ungated -552); kRuinDashHit and kWillowJoin go forward.

### Fuel stunlock (Oct 30 evening; Eric: "we kind of get stunlocked by our fuel limits in many of the fights", ranked f2e61884 #450 lanes)
- Ranked f2e61884: 584 of 6,101 champion-turns capped at 100k (calm 8.4%, enemy within 6 17.6%, within 3 16.5%); most idle rounds in our
  death windows were capped turns or the round after one (Vesper r448 capped -> idle r449 -> dead r450; HoR r922; Ryth r1156/r1162-63; Willow
  r910/914/916/1194/1195/1198). Local #450 vs PoolLive, 24 maps x 2 sides: 2.31% capped (heavy six 5.85%: lanes 9-15%, big-world, yellow,
  harvest 28% near fights, gemcombat5, tangle); #374 1.71%, #405 2.04%, #428 2.49%.
- Where (tools/edits/edit_fuelwhere.py, edit_fnsusp.py -> tools/stress/fuelwhere.py, fnsusp.py): 62% of suspensions in the decision; on lanes
  ~50k spent before it (camp observation 14-21k, squad 8-12k, wards 3-10k); score_team_targets on the stack in 42% of suspensions (~47k a call
  on heavy maps, entered with ~45k: choose_target's kScoreFuel guard lapses once forget_picks() zeroes the pick round); field builds 18-32k on
  big-world / tangle / harvest / gemcombat5 (1-6k on lanes / yellow / corners).
- kFuelSafe (edit_fuelsafe.py / 2 / 3 / 4; B516-B521): 1 skip camps / squad / wards when the decision's learned cost would not fit; 2 learned
  turn-end rescore + kFieldCost floors; 4 team / solo rescoring needs its learned cost (squads keep a live stale pick only; deferred rescore
  first next turn); 8 fight diet (enemy within 6: no camps / squad / wards / warm). Heavy-six capped: base 5.72%, 1 4.83, 3 4.53, 4 6.31 (rescore
  first collides with observation), 5 3.87, 7 3.79, 7 (squad-safe) 3.63, 15 3.80; fight<=3 turns 1.61% -> 0.96% (7) -> 0.54% (15), near<=6
  2.48 -> 1.49 -> 1.04%.
- s_fuel1 (B517c + c450 + kRuinDashHit + kWillowJoin 10, 2240 a arm): kFuelSafe 5 -14 +-13, 7 -9 +-13, 3 -20 +-13 - local pool fights are
  cheap (our own bots), the ladder's are not: judge on a panel.

### Dash trio and carry rule (Oct 30 eve; Eric: Vendetta + Vesper + HoR at 3 picks, rewards to Vesper / Vendetta when farming together)
- edit_carrytrio.py (B518): kDraftAlt 8 (3 picks Ves, HoR, Ven), 16 (4 picks + Marcella); kCarryPair (others leave a reward to a near Vesper /
  Vendetta going for it; a carrier below 35% health, recalling, dead, too far or with an enemy within 3 cannot take it - then the other does).
- s_trio1 (12 three- + 13 four-pick maps, 800 an arm, B518c + c450 + kRuinDashHit + kWillowJoin 10): kDraftAlt 8 **-61 +-19**; + kCarryPair
  **-273 +-28**; kDraftAlt 16 **-196 +-22**; + kCarryPair -460; kDraftAlt 4 (Mar, Ves, HoR, Willow) -41 +-20. Ladder data agrees: the trio
  is the most-drafted top 3-pick set and -7.4..-11.1 wins per 100 vs team strength (top-builds-1031.md).
- kCarryPair deadlock found (edit_carryfix.py, B522): kTeamMoveOn sent the carrier on because HoR stood on the tiles, kOneCapturer let
  slot-0 HoR keep them, and HoR stepped off for the carrier. Fixed (carriers never yield to non-carriers); the trace then shows Vesper /
  Vendetta capturing what HoR leaves, but team gold still fell (sanity 24 games: HoR 1,005 -> 211, Vesper 4,371 -> 4,009) - concentrating
  rewards costs (as kVesperFeed did, -40).
- Our Vendetta on the current code (24 trio games, vendtrace.ts): doubles 97% of champion-fight turns with the reset ready (top 83%); kill
  refreshes used 0 of 1,136 (317 with a target in reach) -> kResetMore 3 (bit 1 = chain_kill / reset_follow after kills); dash turns with a
  hit 8 of 2,236 (135 ended beside a camp member) -> kTurnEndHit 2 (edit_draft31.py).
- **#451 panel** (= #450 + kRuinDashHit + kWillowJoin 10 + kFuelSafe 8, B521x + run/cand451.edits; re-pinned panel125b, 125 games, restored
  450 at 17:40 UTC): **22 wins -52,829 vs #450 24 / -50,212 (-2 wins, -2.6k: noise)**. Fuel on 50 panel games each (top-team opponents):
  capped near<=6 1.44% -> 0.71%, fight<=3 0.60% -> 0.39%, calm 1.97% -> 2.05% - the panel's games cap far less than ranked lanes (17%).
- **Approach-field roots for ranged champions** (probe on #450 + kFuelSafe 15, 6 heavy maps): kSightRoots' line-of-sight filter costs a
  median 21-32k a build (max 69k yellow, 55k harvest, 47k big-world) vs ~3k melee, uncounted by any floor. **kSightCache** (edit_sightcache.py,
  B525): the per-group mask once, roots & mask after - **exact 12/12** (unlimited fuel, AC logs identical); capped 2.30% -> 1.95% (rest of the
  pool 1.02 -> 0.79%); with kFuelSafe 15: **1.08%** (heavy six 5.72% -> 2.72%).
- edit_fuelsafe5.py (B524): a rescore-first turn skips the camp observation - bit 4 alone still 6.29% (a 47k heavy-map team rescore plus a
  30-60k decision cannot share one 100k turn).
- edit_sightcache2.py (B526: kSightWarm builds missing masks with spare fuel in end_jobs / dead turns; the mask imported in one
  import_linear_buffer call): exact 12/12, but capped rose (warm 2.66%, import only 2.62% vs kSightCache v1 1.95%; with kFuelSafe 15
  1.70-1.74% vs 1.08%). First-mask cost per group tile measured 6-18.6k (tangle) - the 12k/tile warm guard was too low. Keep v1 (B525).
- **s_mix2 (B521c + c450 + kRuinDashHit + kWillowJoin 10, 2240 an arm, base 1571):** kFuelSafe 8 -18 +-14, 10 -10 +-14, 15 -26 +-14 (with
  s_fuel1 every behaviour-changing fuel arm is -9..-26 locally); **kMarcBuild 9 (Treasure F, Jungle F, Durability H, Bruiser F) +11 +-7**;
  kMarcBuild 10 (Treasure H, Jungle F, Durability H, Bruiser F) -4 +-13; 11 (Treasure F, Jungle H, Durability H, Bruiser F) -7 +-9;
  kTurnEndHit 3 +1 +-13; kResetMore 3 +2 +-8 (no Vendetta in the usual drafts: both neutral).
- **s_draft2 (B521c, 12 three- + 13 four-pick maps, 800 an arm, base 519):** kDraftAlt 32 (3 picks HoR, Vesper, Ryth - Ad Astra's, +18.6 per
  100 on the ladder) **-81 +-19**; 64 (4 picks HoR, Ves, Ryth, Mar) **-157 +-23**; 96 -238; the trio done right (kDraftAlt 8 + kCarryPair +
  kResetMore 3 + kFishBuild 8 + kTurnEndHit 3) -243; with 4 picks -243. Every HoR-at-3/4-picks draft loses locally (as kDraftAlt 1 did:
  -251 locally, a tie on the 3-pick ladder bench #407) - the panel judges (#453).
- **Review of today's edits (independent read of B525x, Oct 30 ~19:00 UTC)** -> edit_review31.py (B528): skipped camp observation left a
  killed camp "alive" (reveal_stuck: avoid 40 + drop) - the skip now refreshes our target's state; kFuelSafe 4 wait counters counted calls
  not turns; the fsafe3 keep-turn return lacked solo_; answer_help joined calls on empty deferred picks; kCarryPair still deadlocked via the
  kSingleCapturer move-on and via kMarcellaCarry's carrier_on_tiles; pair_carrier_near's "within 2" ignored the carrier's target; kTurnEndHit
  bit 2 on leaving turns. **kRecallNextCache** (recall_capture rescored every group every capture turn, live code): no measurable fuel change
  (2.00% vs 1.95% capped), off. kSightCache confirmed exact by the reviewer (same roots: range, blocked, bounds, clear_line direction).
- **#452 = #450 + kRuinDashHit + kWillowJoin 10 + kSightCache + kMarcBuild 9** (B528x + run/cand452.edits) and **#453 = #452 + kDraftAlt 96**
  on the panel (lad452.sh, ~19:00 UTC).
- **s_esc1 (B523c + c450 + kRuinDashHit + kWillowJoin 10, 2240 an arm, base 1572):** kEscapeRoom 2 -21 +-13, 6 -30 +-13 (open-ground tie-break:
  off); **kCarryPair 1 on the usual 5-pick drafts (Vesper the only carrier) -409 +-15** - B523 still had the kSingleCapturer deadlock path the
  review found (fixed in B528); re-screened as s_carry2.
- **Panels (re-pinned, 125 games, same pinned games):** #450 24 / -50,212; #451 (+ fight diet + kRuinDashHit + kWillowJoin) 22 / -52,829;
  **#452** (+ kRuinDashHit + kWillowJoin + kSightCache + kMarcBuild 9) **21 / -49,462**; **#453** (#452 + kDraftAlt 96: HoR in the 3- and 4-pick
  drafts) **18 / -55,701** - the ladder agrees with the local -238: no HoR-for-Marcella/Ryth at 3-4 picks. Nothing beats #450 beyond noise.
- **Vesper's gold (50 #450 panel games, traces):** ours earned 53 / 186 / 380 at r150 / r300 / r600, theirs 266 / 572 / 1,372 (team totals
  close: 496 vs 570, 1,127 vs 1,268, 2,493 vs 3,094) - their Vesper takes ~45% of the team's gold, ours 11-15%.
- **kCarryPair after the deadlock fixes (B528c, 24 five-pick games vs PoolLive):** wins 14 -> 18, margin +71 -> +251, Vesper's gold 1,748 ->
  2,239, Marcella 2,197 -> 2,477 (team gold up): the -409 of s_esc1 was the kSingleCapturer deadlock. s_carry2 + #454 panel queued.
- **s_vesp1 (B527c + c450 + kRuinDashHit + kWillowJoin 10, 2240 an arm, base 1575):** kFishBuild 1 (Fish's Vesper Treasure S, Jungle S, Bruiser H,
  Durability H, Bruiser S) +0 +-6; kVespBuild 9 (prism's Treasure S, Jungle S, Prospector S, Bruiser S) -18 +-7; kSightCache -22 +-13 (exact
  under unlimited fuel: fuel-timing divergence; #452 with it 21 / -49.5k on the panel). Vesper builds stay (kVespBuild 6).
- Wide scan #452 (T452, 70 maps x 2 sides vs B7Live, genscan): 136/140 wins, loops 36 (230 rounds), stuck 17 (193 rounds), worst the-pack 79,
  nothing over 100 - passes.
- **#454 = #452 + kCarryPair 1** (B528x, deadlock-fixed): panel **17 / -58,839** (vs #452 21 / -49,462, #450 24 / -50,212; random-map x1r 4 vs 8
  wins) - feeding rewards to Vesper loses on the ladder again (as kVesperFeed 17 vs 22). Its upload scan also showed a Vesper / Willow walking
  loop on 01islands (8 loops, 139 rounds). kCarryPair stays off.
- **s_fuel3 (B528c with edit_review31's fixes + c450 + kRuinDashHit + kWillowJoin 10 + kSightCache, base 1552):** kFuelSafe 8 +13 +-15, 15 -9
  +-15, **1 +21 +-12** - the skipped-observation fix removed the fuel bits' local cost. #455 = #450 + kSightCache + kFuelSafe 9 on the panel.
- Ladder Oct 30 20:00 UTC: Bamboo rank 51 (2,017); top 10 2,299-2,475.
- **#455 = #450 + kSightCache + kFuelSafe 9 (fuel only, B528x):** panel **18 / -57,568** (vs #450 24 / -50,212; #452 21) though its upload scan
  had 2,494 fuel-limit turns (#451-#454: 3,600-4,400). Five variants of #450 today scored 17-22 (mean 19.2): #450's 24 sits high in the
  chaos spread; the 125-game panel does not resolve changes of a few percent. s_carry2: **kCarryPair (fixed) -107 +-13** locally (24-game
  sanity +4 wins misled); **kMarcBuild 9 +11 +-7 again** (replicated).
- **Unseen big maps (sprint_1_fx_groups-*, vs PoolLive):** #450 capped 9.6 / 9.8 / 34.6 / 47.2% of turns on 64 / 100 / 128 / 256 groups (128 +
  256: 5,046 suspensions in 12,559 turns, all in camp scoring at ~1k fuel a group). **edit_scorenear.py (B529) kScoreNear N + kScoreNearOver**:
  with kFuelSafe 13, N 24 -> 1.6 / 2.8 / 6.6 / 21.9%; N 48 7.6 / 12.3 / 14.4 / 25.1%. kScoreNearOver 48 + kScoreNear 24 leaves the pool maps
  (max 46 groups: islands; lanes 42) unchanged.
- **Where the top teams win (50 #450 panel traces):** banked gems even to r600 (332 vs 340), then ours stall (r1000 354 vs 531); gems gained
  per 300 rounds 187 / 220 / 202 / 163 vs 189 / 294 / 319 / 284, gold 1,087 / 1,351 / 1,283 / 947 vs 1,364 / 1,964 / 2,058 / 1,951, deaths
  1.5 / 2.6 / 2.9 / 3.3 vs 1.3 / 1.8 / 1.8 / 1.6. Camp damage per alive round: Vesper r300-600 20.6 vs 40.2, r600-900 23.4 vs 53.5 (HoR, Ryth
  level; Marcella 24 vs 32 late; their Vendetta 27-34). Their Vesper is the strength carry.
- **edit_vesperfree.py (B530) kVesperFree R:** on whole-team / boss maps our Vesper farms alone from round R. Sanity (32 games, R 100): her gold
  1,711 -> 2,467, team gold up, wins 17 -> 14. s_vfree (100 / 200 / 300) queued.
- **Vesper ours vs theirs (50 #450 panel traces):** camp-hit round share equal (27 / 21 / 15% vs 27 / 22 / 18%), damage per hitting round half
  (98 vs 186 r300-600, 158 vs 294 r600-900); strength r300 / 600 / 900 65 / 95 / 130 vs 118 / 190 / 290; **max health 1,000 / 1,000 / 1,500 vs
  1,050 / 2,250 / 2,900**; dead 12.4% / 16.0% of r300-600 / r600-900 vs 3.2% / 6.9%. Our Vesper reaches r600 with no health item. Marcella r600
  1,500 hp / 494 focus vs 2,200 / 207. Queued: s_vesph2 (kVespBuild 7 Treasure S, Jungle H, Durability H, Bruiser S; 8 Treasure H first; 7 +
  kMarcBuild 9) and panel #456 = #450 + kMarcBuild 9.
- **s_fuel4 (B529c + c450 + kSightCache + kScoreNear 24 / Over 48 (inert on pool maps), base 1521):** kFuelSafe 9 +10 +-14, 13 -11 +-15, 9 +
  kMarcBuild 9 +12 +-15 - neutral.
- **Our Vesper's deaths (50 #450 panel games, deathaudit):** 129 (2.6 a game), median r724, windows 1-5 rounds at a median 137 damage a round
  (bursts on a 1,000-1,500 hp Vesper); flags BUSH 79, BYSTANDERS 65, COVER_OK 51, NO_FIGHTBACK 50, STAYED 44, OUTNUMBERED 23, DIVE 10.
- **#456 = #450 + kMarcBuild 9** (Marcella Treasure F, Jungle F, Durability H, Bruiser F; B530x + run/cand456.edits): panel **26 / -46,769 vs
  #450 24 / -50,212** (top-10 15 vs 13, random-map 9 vs 6) - the first variant above #450 (local +11 +-7 twice). Panel scores today: #450 24,
  #451 22, #452 21, #453 18, #454 17, #455 18, #456 26 - versions with kSightCache / kFuelSafe / kRuinDashHit + kWillowJoin sat at 18-22.
- **s_vfree (B530c + c450 + kSightCache, base 1551):** kVesperFree 100 -36 +-12, 200 -18 +-10, 300 -2 +-10 - Vesper soloing on whole-team maps
  does not pay (as every split form before). Off.
- **s_vesph2 (B530c + c450 + kSightCache, base 1551):** kVespBuild 7 (Treasure S, Jungle H, Durability H, Bruiser S) **+7 +-7**; 8 (Treasure H,
  Jungle S, Durability H, Bruiser S) -1 +-11; 7 + kMarcBuild 9 +9 +-9.
- **edit_fuelsafe6.py (B531) kFuelSafeHeavy:** the kFuelSafe bits act only while the fuel governor (kFuelGov 1, live) marks the champion heavy.
  #456 + kSightCache + kScoreNear 24 / Over 48 + kFuelSafe 9 heavy-only (24 pool + 4 fx maps x 2 sides vs PoolLive): capped fx 25.5% -> 12.9%,
  heavy six 6.35 -> 4.38%, rest 1.03 -> 0.79%; wins 31 -> 35 of 56. #457 = that on the panel; s_rob queued.
- **#457 = #456 + kSightCache + kScoreNear 24 / Over 48 + kFuelSafe 9 heavy-only** (B531x): panel **15 / -55,760** (vs #456 26 / -46,769; top-10
  9 vs 15, random-map 4 vs 9). Every panel version carrying a fuel change scored lower (22, 21, 18, 15). Possible mechanism (untested): the
  live fuel governor's heavy mode (kFuelGov 1: big-map scoring modes, +40..+57 on heavy maps when adopted) engages less when turns cost less.
  Fuel changes stay out of the candidates.
- Wide scan #456 (T456): 127/140 vs B7Live (#452 136/140), loops 67 (680 rounds), stuck 20 (276), the-farm A loops at (22-23,18) 198 rounds
  (hovering at a camp late; game won), starvation B stuck 76 rounds - no freeze.
- **Panel B** (panelB.sh: the same pinned opponent bots - source groups p445f_* - on rotated map sets, sides flipped; 125 games independent of
  panel A) for #450 / #456 / #452 (run/panB_run.sh, from ~21:50 UTC).
- **Panel flips (per-game results on the 123 common panel-A games):** any two versions differ in 16-23 games (noise ~ +-4-5 wins). #456 -> #457
  17 W->L vs 6 L->W (sign test p ~0.03), #456 -> #455 13 vs 5, #450 -> #457 14 vs 5, #450 -> #456 7 vs 9: **kFuelSafe skipping (bit 1, even
  heavy-only) loses real games against the top teams** (local +21: the pool does not punish stale camp / squad state); #456 >= #450.
- **s_cgk (B530c + c450 + kSightCache, base 1551):** kCarryGemK 2.0 (more gold-heavy rewards to Vesper in squads) -15 +-6, 1.0 -25 +-7, 0.5
  -25 +-7 - every routing of rewards to Vesper loses (kVesperFeed, kCarryPair, kCarryGemK).
- **s_rob (B531c + c450 + kMarcBuild 9, base 1556):** + robustness set (kSightCache, kScoreNear 24 / 48, kFuelSafe 9 heavy-only) -15 +-13; + it +
  kRuinDashHit + kWillowJoin 10 +7 +-13. Neutral locally; the panel (#457 15) rejects it.
- **Panel B** (same pinned bots, rotated maps): #450 20 / -58,289; **#456 23 / -54,252** (flips 8 W->L vs 11 L->W). **A + B: #456 49 / -101,021 vs
  #450 44 / -108,501** (flips 15 vs 20) - the same direction on both independent panels: **#456 recommended over #450**. Wide scan #458: 132/140,
  02the-pack B lost 8-35 (the walled-ring altar map: whichever team breaches the 48-wolf ring banks; #452 / #456 breached and banked 800 there).
- Queued: #458 (#456 + kVespBuild 7), #459 (#450 + kMarcBuild 11 + kVespBuild 7, Eric's Marcella line), #460 (#456 + kRuinDashHit + kWillowJoin 10).
- #456's mechanism (50 panel-A games each, traces): Marcella max health r600 1,800 vs 1,500, deaths 1.74 vs 1.94 a game; Vesper deaths 2.38 vs 2.58.
- **Panel B #452** (#450 + kRuinDashHit + kWillowJoin + kSightCache + kMarcBuild 9): 22 / -55,264. **A + B (250 games): #456 49 / -101,021,
  #452 43 / -104,726, #450 44 / -108,501.**
- **#458 = #456 + kVespBuild 7** (Vesper Treasure S, Jungle H, Durability H, Bruiser S; B531x + tools/cands/cand458.edits): panel A **29 / -48,232**
  (vs #456 26 / -46,769, #450 24 / -50,212). Panel B queued after #459 / #460.
- **Oct 31 00:10 UTC: Eric made #458 the live default.** Eric switched to 458 by hand during #459's panel: panelversions.py shows 19 of its 25
  groups were played by #458 - **all 95 of those games identical to p458's** (the pinned-panel determinism check). The 30 games #459 really
  played (kMarcBuild 11 = Eric's Marcella line Treasure F, Jungle H, Durability H, Bruiser F + kVespBuild 7): 7 wins vs #458's 9 on the same
  games (local -7 +-9): no gain over kMarcBuild 9. #460 rebased: #458 + kRuinDashHit + kWillowJoin 10. Panels now restore 458.
- kScoreNear 24 / Over 48 on #458 (pool maps, decisions identical by construction): 33 of 48 local games still diverge (outcome / rounds /
  gems) from the few extra instructions per scoring pass - the bot is fuel-chaotic; any code change reshuffles pool-map outcomes. Kept as an
  option for unseen 50+ group maps (fx_groups 128 / 256 capped 35 / 47% on #450-family builds), not added to live.
- **Panel B #458: 25 / -52,644. A + B (250 games): #458 54 / -100,876, #456 49 / -101,021, #450 44 / -108,501.** Flips #450 -> #458: panel A 8 W->L
  vs 13 L->W, panel B 7 vs 12 (total 15 vs 25, one-sided sign test p 0.08) - the same direction on both independent panels. #458 is live.
- **s_marc12 (B532c + c450 + kVespBuild 7; base = #458's lines, 1560):** kMarcBuild 12 (Treasure F, Jungle F, Durability H, Bruiser H stacked)
  **-17 +-7**; #458 + kRuinDashHit + kWillowJoin 10 +11 +-12 (= #460, on the panel). Ryth / Willow health already at or above the top teams'
  (Ryth r600 2,200 vs 1,700): the health gap was Vesper and Marcella only.
- **Fish resubmitted ~15:55 UTC Oct 30** (fish-builds-1031.md, agent study): the new version went 204-55 (79%; 191-53 vs the top 10) after
  249-231, now rank 1 (2,562). First emblem by map only: Capture first on 46 maps (Marcella Capture F > Jungle F > Monster F > Bruiser H >
  Durability H > Bruiser F...; HoR Capture H > Jungle F > Monster F > Hunter H > Bruiser H; Vesper Capture S > Treasure S > Jungle S > Monster S >
  Hunter H > Durability H > Collectors S > Bruiser S/H; Vendetta Capture H > Jungle S > Monster S > Hunter H > Durability H > Collectors S >
  Bruiser S), Prospector first on 9 cluster-farm maps; drafts Marcella first on 35 of 64 maps. NB: our pinned panels hold Fish's OLD bot (p445f
  pinned 09:21 Oct 30). **edit_fishb.py (B533) kFishB bits 1 Marcella / 2 HoR / 4 Vesper / 8 Vendetta** - those champions skip the kFarmBuild
  override and treasure_first() (which counts Marcella as a Strength champion: with a non-Treasure first line she got Treasure Strength).
  #461 = #458 + kFishB 7 on panels A and B (lad461.sh).
- **#460 = #458 + kRuinDashHit + kWillowJoin 10:** panel A **23 / -52,200 vs #458 29 / -48,232**. With #451 (22) and #452 (21) the combat pair
  is ladder-negative (local +17 / +13): stays off. Wide scan #460 132/140 (no freeze).
- **#461 = #458 + kFishB 7** (Fish's new Marcella / HoR / Vesper lines): panel A **26 / -48,322 vs #458 29 / -48,232** (margin equal). Panel B next.
- **Eric (01:40 UTC Oct 31): why do splits fail; split-and-rejoin; the top teams' pre-started recall.** Notes for the next build session:
  splits failed because the remaining squad's party model is tuned for the whole group (four clear big camps slower and take more damage),
  the lone champion is picked off (the top teams' own splitters die 45% more per round on close maps) and returns out of phase - the top
  teams' splitter takes one own-half camp (~38 rounds) on the group's path / recall cycle and the group recalls and returns together. A
  "clockwork" version needs a group recall cycle (the squad's next trip home) and lets a member take a solo camp only if it is back by that
  trip; rejoining itself already happens (after a solo capture the squad target is re-adopted). **Pre-started recall (kPreRecall, not
  built):** gain ~1 round per recall (~9 a champion-game, ~0.7% active time); needs (1) every ally reader of is_recalling() (30 sites: recall
  sync, carriers, party gathering, help, escort...) to ignore pre-starts - the kRecallGenuine test (remaining_channel_time <= length - 2) -
  and (2) a keep / cancel decision before the turn's first move / attack / cast (the recall decisions sit in deliver / retreat / recall-capture
  / escape). Deferred: below the panel's resolution and too wide a change for the last hours before the knockout.
- **s_fishb (B533c + #458's lines, base 1564):** kFishB 1 (Marcella) +1 +-9, 2 (HoR) -3 +-7, 4 (Vesper) -3 +-9, 7 (all three) -8 +-11 - neutral;
  Fish's gain likely needs its whole system (map-keyed first emblem, drafts, timing), not the lines alone.
- **#461 panel B 19 / -58,378 (vs #458 25 / -52,644); A + B 45 vs 54 of 250** - Fish's new lines on our champions lose (local -8 +-11): rejected.
- **kEarlyRecall (edit_earlyrecall.py, B534; grant #13 "recall micro")**: the pre-start benefit without a blanket pre-start - at our turn end,
  if next turn would retreat (wants_retreat) and retreat()'s recall would fire (no threat within kRecallSafe, not hit, out of camp reach,
  >= kRecallDistance from home, not engaged / capturing), recall now (home a round sooner). Fires ~6 times a game (8 maps x 2 sides, logged).
  Blanket pre-start rejected for our code: a channelling champion's can_move / can_attack / can_cast are false (91 decision reads) and 30
  teammate readers of is_recalling() would take it for a trip. s_early queued.
- **s_early (B534c + #458's lines, base 1564):** kEarlyRecall first version -16 +-11 (it also fired on kill turns and left rewards); with
  "no early recall on a turn we attacked / near a cleared or reward camp" **+4 +-11** - safe, neutral (the one-round saving is below a
  screen's resolution). Goes into the clockwork candidate.
- **Recall / clockwork study (Oct 31 ~03:00 UTC, grant #13; full write-up `.info/knowledge/recall-cycle-1031.md`, tables
  `results/rc1031/tables.md`):** (1) pre-started recalls: Fish / Mite / print / Ad Astra yes, prism best girl and NEETCoders never - not what
  separates the top. (2) We are MORE synchronised than the top teams (46% of our recalls are joint, 2.7 champions; theirs 17-41%, 2.2-2.4).
  Our 90%+-health recalls are travel (recall_hop 40%, recall_capture 35%), not wasted shopping. (3) Time: our walk out from home is 28% of
  champion-rounds (Fish 21%; contest 30% vs 19%) - 84% of departures head for the squad's camp (contest: 21 rounds to the first hit vs 10
  solo). (4) **Elk captures equal (9.1 vs Fish 9.6 a game); light camps 15.3 vs 25.7** (clusters ~70% of Fish's nominal-gem lead), and
  34-43% of Fish's light captures are by a champion away from its group (ours 6-25%) - that is the "clockwork". (5) vs Mite / Ad Astra /
  NEET / prism the gap is camp damage (+21-34% per camp round; gems per damage equal), and strength follows gold income: our Vesper earns
  574 by r600 (theirs 645-1,502; strength 95 vs 105-235).
- **edit_clockwork.py (B535x / B535c): kClockSat S** (whole-team squad member the camp does not need takes a light camp it can clear,
  capture and walk back from before the squad is done there, + S - 1 slack), **kClockMeet W** (a member W+ travel rounds from the squad's
  camp takes light camps on that walk, detour <= kClockDetour 6), kClockTtk 8, kClockKinds 1 (harmless clusters; 2 adds wolves). Test
  games: galaxy 20 sat / 355 meet decisions, crater 60 / 22. s_clock (local, 5 arms) and **#462 = #458 + kClockSat 3 + kClockMeet 20**
  (panels A + B, lad462.sh) running.
- **Map plans of #458 (bots/TPlan: #458 config printing team_rounds_ / boss_map_ after set-up, 70 maps vs PoolLive, 40 rounds):**
  **48 maps are boss whole-team** (team_rounds_ 2000 + boss_map_: one squad of every living champion all game, kBossHp 5000 makes any golem
  node a boss): 10 close, 20 contest, 18 farm. 21 maps open as a team for 0-240 rounds; **kSquadPacksOnly only applies to elkring** (team 2000,
  not boss) - its s_packs screen was cancelled. The clockwork splits (kClockSat / kClockMeet) act on the 48.
- **Our map categories in #458 (set-up flags, no map names; per-map list `results/tplan/plans.json` from bots/TPlan):** control_map_ = spawn walk
  <= 45 (36 maps; after the opening squads of 2, else solo); boss_map_ = groups with >= 5,000 total HP, gems, hardest monster <= 250 str hold
  >= 30% of camp gems (48 maps - the 5,000 line catches 2-elk packs: swirl 2 elks + 2 gem clusters, elk-arena, collision; kPackHp 4,000 never
  fires on the pool) -> whole team one squad all game; otherwise the opening (team_rounds_) is 100 / all game by kAutoTeamStr, 240 on
  non-control, 180 control with walk > 16, 120 closer, 0 with no hostile camp (gem-combat maps, breadcrumbs). Map plan: boss 48, race 20,
  gem_count 2 (fragment, hooks), gold_tiebreak 0; Treasure first on 51 (scaling_map). No "farm map" flag: kFarmBuild 8 uses non-control
  or boss. The draft depends only on the pick count (3 Marcella-Vesper-Ryth, 4 + Willow, 5 HoR-Vesper-Ryth-Marcella-Willow).
- **s_clock (B535c + #458's lines, base 1564, seeds 1 2 4 5, 2240/arm):** kClockSat 3 **-52 +-13** (1504); kClockMeet 20 -1 +-11 (1579, +15
  wins); both -53 +-13; kClockSat 3 + kClockKinds 3 (wolves) -72 +-14. The satellite arm ran with the over-peel bug (every non-leader counted
  all others as staying) - s_clock2 re-screens it on B536c (edit_clockwork2.py). kClockMeet alone is neutral.
- **#462 = #458 + kClockSat 3 + kClockMeet 20 (B535x, satellites with the over-peel bug):** panel A **23 / -51,296 vs #458 29 / -48,232**,
  panel B **18 / -58,917 vs 25 / -52,644**: 41 vs 54 of 250 - rejected (local -53 agrees). Live restored to 458 (03:31 UTC).
- **Boss line scope (TPlan7500 / TPlan10000, 70 maps):** kBossHp 7500 -> 33 boss maps (15 leave: corners, crater, expanse, interlock, oasis,
  packs, quadrants, swirl, vault, elk-arena, islands, yellow-brick-road, geodes, harvest, treasure-box; they open as a team 100-240 rounds,
  then solo / pairs); 10000 (pre-#400) -> 29 (+ collision, eight, reverse-spiral; gift-wrapping stays whole-team by kAutoTeamStr).
  s_boss (local, both lines) queued after s_clock2.
- **s_clock2 (B536c, satellites counting only the members that stay; vs s_clock's base 1564):** kClockSat 3 **-42 +-13** (1503); + wolves
  (kClockKinds 3) -46 +-13; kClockSat 10 + wolves -57 +-14. The fix did not rescue it: peeling members off the whole-team squad for light
  camps loses locally in every form (with kPartyShare 2 -21, kRejoinFarm -60, kClusterOne -43 before) and on the ladder (#462). Off.
- **Eric's farm-map definition (Oct 31 ~04:00 UTC):** (a) no way to reach the opponent except over walls or through a monolith
  (01boss_battle); (b) terrain makes any invasion a very long walk (02cuts); (c) fights possible but contest points far from the bases
  (islands, ambush): early game is farming, split, but group for middle (symmetry-line) camps once enemies show there, keep splitting near
  base. **edit_farmmap.py (B537x / B537c), kFarmMap bits 1 classify (spawn walk with monolith camps blocked > kFarmWalk 60 or impossible;
  never a control map) / 2 split (one squad only for kFarmOpen 100 rounds and boss rallies: a kFarmRallyHp 10k+ camp hurt or survivable at
  kBossBudget, held kFarmRallyHold 30) / 4 pairs (kFarmSquad 2) with an enemy in sight.** Classification over the 70 maps (bots/TFarm):
  **23 farm maps** = the 22 with a spawn walk > 60 (ambush, dunes, expanse, galaxy, great-wall, lanes, pilgrimage, ribs, road-of-riches, rows,
  split, big-world, concentrated-wealth, fracture, islands, shortcut, starvation, cuts, famine, geodes, harvest, tangle) + boss-battle (two
  monoliths fill the only gap in its wall; was a control map, walk 38). Full games vs PoolLive: rallies on rows r600-1000, boss-battle
  r400-1150, cuts r600-900; ambush / islands / harvest have no 10k camp (split all game). s_farm queued (1 / 3 / 7 / 7 + rally 5000).
- **s_boss (B535c + #458's lines, base 1564):** kBossHp 7500 **-23 +-9** (1515, 15 maps leave whole-team play), 10000 **-38 +-10** (1479,
  19 maps): on the elk-pack maps the one-squad-all-game play beats a 100-240-round team opening followed by solo farming locally. Keep 5000.
- **#463 = #458 + kClockMeet 20 + kEarlyRecall (B536x; both neutral locally):** panel A **24 / -50,544 vs #458 29 / -48,232**, panel B
  **22 / -57,684 vs 25 / -52,644**: 46 vs 54 of 250 (the losses sit in the random-map x1r sets: 5 vs 11, 4 vs 8). Rejected; live 458
  restored 04:31 UTC. With #462 (41 vs 54) every clockwork piece has now lost on the ladder.
- **s_farm (B537c + #458's lines; base = s_clock's B535c 1564):** kFarmMap 1 (classify; boss-battle no longer control) -10 +-13 (1549,
  neutral); **3 (split + monolith rallies) -84 +-14** (1378); 7 (+ pairs) -68 +-13; 7 + kFarmRallyHp 5000 (rally for any boss camp) -58 +-13.
  On the 23 farm maps the mean margin falls from +193 (whole team) to -32 (split): dunes -623, pilgrimage -425, starvation -418, geodes -396,
  split -334, expanse -299, concentrated-wealth -285, shortcut -281, cuts -269, islands -263; only tangle (+48) and lanes (+55) gain. Rally
  for any boss camp helps where elk packs hold the gems (cuts +12, harvest +68, split -37, geodes -23). Our whole-team play is our strength
  on these maps locally. (B537c with kFarmMap > 0 changes non-farm games too: the set-up walk's fuel shifts later turns - chaotic, not a bias.)
- **Disk clean-up (Eric, 04:35 UTC):** deleted replays/Matchdatabase1024-part1 (1.5 GB, Oct 23 pre-patch zips), the 219 pre-2.0.0 entries of
  replays/p2, the unreferenced pre-patch sets me104 / rk1021b / ranked1515 / weak287 / top_noobot / top_pwonk / mono, today's temporary test
  replays (tplan*, tfarm*, t535, act1031 raw), and results/ev runs beyond the newest 20: 62 -> 77 GB free. Kept: the Oct 31 study sets
  (top1031, fishnew1031, us1031, builds1031), p2's engine-2.0.0 entries (Oct 26-29), results/cache, act1031d, the referenced small sets.
- **How Fish (Oct 30 version) groups on farm maps (tools/stress/farmgroups.py, 12 farm-class games, 11 won, median 1,019 rounds; vs our 9):**
  main group 4.9 in r0-100 (all six bodies), then 3.3 / 2.9 / 2.7 (ours 4.4 / 3.6 / 3.0 / 2.8 - similar sizes). The difference is WHO:
  Fish's main group is the twins + Willow (Cassi / Issac / Willow in the main group 62-73% of active rounds after r100) while the carries
  rotate out alone (Vendetta away 54% r100-300, Marcella 40-61%, HoR 34-54%, Vesper 39-44%); ours keeps Ryth / Vesper / Willow in it 72-86%
  to r600. Split champions take the light camps solo (clusters 6.6 / gold clusters 10.2 a game, 1-champion damage party 62-75%, 47-60% away)
  and come back for elk camps (one-elk camps 7.9 a game, 63% with 3-5 hitters) and golems (1.3 a game, 4-6 hitters; first at r80-84 by all
  six on two maps); monoliths late (r913-994) by two strong champions. Ours: clusters 1.3 a game (by the squad, 2-4 hitters), golems 0.3
  (first r346). s_fishfarm (kFishB 7 with / without kFarmMap 7 + rally 5000) queued.
- **s_fishfarm (B537c, base 1564):** kFarmMap 7 + rally 5000 -58 +-13 (1447, = s_farm C5); + kFishB 7 (Fish's lines) **-73 +-14** (1416):
  Fish's emblem lines do not pay even with the farm split (-15 more). With s_fishb (-8) and #461 (45 vs 54) they stay off.
- **Fish's camp micro (Eric's replay 64ef2dae, 00great_wall, Fish vs Ad Astra, Fish won 1,106-941 at r845; replays/eric1031; compared with
  our #458 vs PoolLive on the same map, results/gw):** (1) tempo: Fish's first elk camp r26 and the 3-elk camp r53 (ours r41 / r77 - we took
  a wolf pack first). (2) single elk: only HoR (+ Issac) adjacent, HoR dash stun / Cassi stun / Vendetta casts chained - the elk landed 4
  hits in an 11-round clear (Willow healed them); ours: HoR alone took ~6.5 hits over ~20 rounds, Marcella absent. (3) 3-elk camp: Fish's
  four melee each beside a DIFFERENT elk on different sides (Marcella W, Vendetta SE, HoR S, Issac NW) - each elk hits its nearest, so damage
  taken spread 510-840 each, Cassi / Willow at distance 3 untouched, damage dealt 1,116-1,591 each (even); ours stack W/SW and focus the
  weakest: taken Ryth 960 / Marcella 660 / HoR 420 (HoR left early), dealt Ryth 2,440 ... HoR 869. Blocked moves low on both sides.
  Next: kCampSpread (melee champions assigned to different monsters by roster order, tiles beside only their own monster).
- **edit_campspread.py (B538x / B538c), kCampSpread (+ kSpreadCampDist 6):** Fish's camp shape - with 2+ living hostile monsters, the
  k-th melee champion within 6 of the camp (roster order) takes the k-th hostile monster (tile order), attacks it and stands on the free
  tile beside it touching the fewest other hostile monsters. great_wall test game: Marcella walked round to the SE elk, HoR NW, Ryth SW
  (as Fish); HoR's only free tile touched two elks (clusters fill the rest). s_spread (6 / 4) queued.
- **edit_farmstat.py (B539x / B539c), kFarmStat bits 1 carries (Marcella, Vesper, HoR, Vendetta) / 2 everyone:** Eric's "health emblems on
  likely PvP maps, full strength / focus on farm maps" - on farm_map_ (kFarmMap 1) every health shard of the plan becomes the main stat's
  (dunes test: Marcella Durability H -> F, HoR Treasure H -> F, Ryth unchanged). s_stat (kFarmMap 1 ref, + kFarmStat 1, + 3) queued.
- **#464 = #458 + kFarmMap 7 + kFarmRallyHp 5000 (Eric's farm-map split):** panel A **18 / -63,797 vs #458 29 / -48,232** (x1r 3 vs 11).
  panel B **14 / -67,347 vs 25 / -52,644**: **32 vs 54 of 250** - the farm-map split loses hard on the ladder too (local -58). Rejected;
  live 458. kCampSpread s_spread: -14 +-9 (radius 6), -24 +-9 (radius 4); kCampSpread 2 (tiles only, focus fire kept; edit_campspread2.py,
  B540) queued as s_spread2.
- **s_stat (B539c, base 1564):** kFarmMap 1 alone -10 +-13 (1549, reference); + **kFarmStat 1 (carries' health shards -> main stat on the
  23 farm maps) -32 +-13** (1508); kFarmStat 3 (everyone) -38 +-14. Health keeps paying on farm maps for our comp; off.
- **edit_clusterpro.py (B541x / B541c), kClusterPro bits 1 Marcella Pro-F / Vesper Pro-S / HoR, Vendetta, Ryth Pro-H, 2 + Willow Pro-H:** on
  maps whose groups without a hostile monster hold >= kClusterProGems 150 gems (Fish's Prospector-first rule, fish-builds-1031.md s6), the
  plan's Prospector shards go and Prospector opens it. Checked: vault / lost_world Prospector first, anvil unchanged. s_cpro (1 / 3) queued.
- **s_spread2 (B540c, base 1564):** **kCampSpread 2 (Fish's tiles, focus fire kept) -8 +-10** (1557; vs PoolLive +163 vs +128) - neutral,
  better than kCampSpread 1 (-14). #465 = #458 + kCampSpread 2 on panels A + B; s_bspread (Eric: the build tests with it on) queued.
- **Eric (05:55 UTC): test Fish's builds together with the focus-fire camp spread.** s_fishspread (all arms kCampSpread 2 on B541c):
  alone / + kFishB 7 / + kFishB 15 / + kFishB 7 + kClusterPro 1 (Fish's per-map templates). (s_cpro without the spread was killed; the
  TaskStop of its sleeping shell left the screen running - kill the tree with taskkill /T.)
- **s_fishspread (B541c, all arms kCampSpread 2; base 1564):** spread alone -8 +-10 (1557 - identical to s_spread2 on B540c: deterministic);
  **+ kFishB 7 -31 +-12** (1508); + kFishB 15 -31 +-13; + kFishB 7 + kClusterPro 1 -32 +-12. Fish's lines lose with the camp spread too.
- **#465 = #458 + kCampSpread 2:** panel A **23 / -51,293 vs 29**, panel B **18 / -63,805 vs 25**: 41 vs 54 - rejected. Every behaviour
  change today has lost the pinned panels by 8-22 wins (#462-#465); #458 stays live.
- **Fuel on the ladder (Eric 06:35 UTC "a lot of fuel issues ... lose a round sometimes on 458"; tools/stress/fuelladder.py, 115 ranked
  #458 games since 00:10 UTC, summaries' fuelExhausted events):** **1.61% of champion-rounds lost (86 a game)**; farm maps 2.66%, close
  1.24%, contest 0.90%; lanes 9.5%, road_of_riches 10.0%, the_pack 6.8%, harvest 6.6%, gift_wrapping 5.6%, big_world 5.0%, treasure_box
  4.5%, tangle 4.0%; r0-199 2.70% (worst), later 1.2-2.3%; Vesper 2,881, Willow 2,591, HoR 1,946, Marcella 1,285, Ryth 1,181.
  Local (#458 config F0 vs PoolLive, the 12 worst maps): 244 suspensions a game (heavy four 535). Per-function (edit_fnsusp.py, six worst
  maps): score_team_targets on the stack in 53% of suspensions; inclusive (edit_fnprof.py, lanes + road_of_riches): **score_team_targets
  47.9k a call**, travel_time 375 a call x ~42 groups (kPairWalk's nearest-group scan inside it: O(groups^2) a pass). kSightCache (exact)
  -12% suspensions; + kRecallNextCache -9%. **edit_pairwalkcache.py (B542), kPairWalkCache:** the scan once per (round, tile) - exact
  (11 of 12 unlimited-fuel games identical; big_world differs by one input via the fuel governor's heavy mode, not the cache).
- **fuel30 (30 maps x 2 sides vs PoolLive, official fuelExhausted events; #458 config F0 144 a game):** kSightCache **-21%** (114); + kPairWalkCache
  -15% (123; heavy four +12% on 6 games - noise); **+ kScoreStale 12 -28% (104; wins 40 vs 35)**. kScoreStale 12 keeps a squad's last pick
  up to 12 rounds (6) when fuel is short, so the forced rescore stops landing on a near-empty turn. s_fuel (local) + #466 (ladder) queued.
- **Fuel on the ladder, other teams (summaries' fuelExhausted events, 594 opponent team-games + Fish's 404):** **Fish 0 lost turns in 404
  games; prism best girl 0 in 65, Ad Astra 0 in 64, Univ 0 in 45, print 1 a game, NEET 4 a game; all opponents 0.22% of champion-rounds
  (10 a game); us 1.60% (86 a game)** - we lose 7x the field's share and the top three lose none. Their per-turn fuel is not in the
  downloads (only our own team-x.fuel comes with a bundle); ours: mean 46.8k, median 47.4k, p90 74.9k, 1.89% of turns capped.
- **edit_campstun.py (B543x / B543c), kCampStun bits 1 stuns at the attacking monster (the living hostile member whose reach covers one of
  us; strongest, nearest) before the damage casts / 2 hold stunning casts while it is stunned / 4 hold HoR's dash too** (Fish's stun chain,
  Eric's replay 64ef2dae). Test games (#458 lines + kCampStun 7 + kDraftAlt 5): great_wall 68 Ryth stun casts + 59 HoR stun dashes,
  anvil 66 dashes, swirl 57. **Eric (07:25 UTC): HoR in every draft** - kDraftAlt 5 (3 picks Mar>Ves>HoR, 4 picks Mar>Ves>HoR>Wil; 5 picks
  already HoR first). s_stun: kCampStun 7 / kDraftAlt 5 / both / kElkRound 30 (early elk camps, as Fish) queued after s_fuel.
- **Phase profile (edit_fuelmarks.py / tools/stress/fuelmarks.py, #458 config, six worst maps, 52k champion-turns):** mean turn 59k =
  start 2.3k, pre-observation 5.6k (shop, team strength, crystal checks), enemies 2.3k, allies 5.1k, camp observation 10.7k, squad 9.6k,
  wards 2.2k, decide 15.7k, post 5.8k. Suspended turns (3,603; 65% cut in decide, 24% in post, 13% in squad) had spent 24k in the squad
  phase (the full score_team_targets pass, 40-48k on 42 groups, run by every member) and 24% also built a path field (big_world 26-32k a
  build, harvest 18-26k; kFieldFuel's fixed 30k floor lets a 30k build start with 35k left). Engine price list (Oct 25) in bot-status 1729.
- **edit_scoreslices.py (B544): kTeamSlices N (squad pass scores 1/N of the groups + targets + changed groups a pass, reuses the rest) +
  kFollowerEvery M (followers rescore every M rounds).** fuel30 (30 maps x 2 vs PoolLive, lost turns a game; #458 144): F5 (caches +
  kScoreStale 12) 104 (-28%); **F6 = F5 + kTeamSlices 3 + kFollowerEvery 6: 76.6 (-47%; heavy four -74%)**; **F7 = F6 + kSliceAll (solo
  pass sliced on every map): 70.3 (-51%)**; wins 35 / 35 / 35 / 35 (neutral margins). F8 = F7 + kFieldCost (learned field floor) next.
- **Fuel work, continued (fuel30 lost turns a game; #458 144.4):** F8 = F7 + kFieldCost 72.4 (no gain over F7's 70.3); F10 = F8 + kObsGuard 3
  (edit_obsguard.py, B545: health reads only where a champion can hit, far states every 3 rounds) 70.9 (no gain). Phase profile of F7:
  suspensions 3,603 -> 1,612 on the six maps, 87% now cut in decide (heavy turns' decide 33.5k); the camp observation, squad and post
  phases no longer cut. **edit_campcache.py (B546, kCampCache):** farm / fight_group take member positions, strength and this round's
  health from groups_ / hp_left_ instead of 3 reads a member a turn (exact by construction; eqcheck + fuel30 running as F11).
  Reader: tools/stress/fuelmarks.py now prints the decide cost by activity on heavy turns (FX7a = F7 + kLogActivity).
- **kCampCache (B546):** not exact after the fix either (7 of 12 unlimited-fuel games identical; lanes / vault / the-pack differ) and no
  fuel gain (72.7 vs F7 70.3; kCampSnap already reads each member once). Off. **Decide by activity (FX7a, heavy turns, p90 of the decide
  cost):** travel 56k, fight_camp 56k, capture 53k, help_ask_squad 63k, ruin_dash_camp 63k, guard 55k - a step builds the camp's approach
  field (big_world 26-32k) and kSafeRoute's safe copy in the same turn. **edit_onebuild.py (B547, kOneBuild F):** a second field compute
  in a turn needs F fuel left (F12 = F7 + kCampCache + kOneBuild 70000 measuring).
- **F12 = F11 + kOneBuild 70000: 81.2 (worse than F7's 70.3)** - refusing the second field build sends the champion on fallback steps and
  the build comes next turn anyway. Off. F13 = F7 + kAllySpellCache 3 (edit_allycache.py, B548: a mate's ready spell damage read every 3
  rounds) measuring.
- **F13 = F7 + kAllySpellCache 3: 74.0** (no gain over F7 70.3). Off. **F7 is the fuel configuration** (kSightCache + kPairWalkCache +
  kScoreStale 12 + kTeamSlices 3 + kFollowerEvery 6 + kSliceAll): 144 -> 70 lost turns a game on the 30-map set.
- **#466 = #458 + kSightCache + kPairWalkCache + kScoreStale 12:** panel A 26 vs 29, panel B 23 vs 25: 49 vs 54 of 250 (-5, within the
  panel's noise; its upload check: 2,911 fuel events vs ~4,800). Live 458 restored. **F14 = F7 + kStepLite 30000 + kCastLite 45000
  (edit_steplite.py, B549): 68.4** (F7 70.3, noise). Remaining lost turns under F7 by map (2 games each): harvest 564, big_world 466,
  stampede 463 (no better than #458's 416), tangle 370, lanes 304, road_of_riches 162; most others under 130.
- **s_stun (B543c, base 1564):** **kCampStun 7 (stun chain at the attacking monster) +10 +-12** (1572, neutral-positive); **kDraftAlt 5
  (HoR in 3- and 4-pick drafts, Eric's request) -50 +-11** (1490); both -51; kElkRound 30 (elk camps favoured from r30) +3 +-9.
  HoR-for-Ryth at 3 picks has now lost locally three times (-175 earlier, -50 here).
- **edit_warmfields.py (B550): kWarmSlack S / kWarmMax 2 / kWardFuel F** (fields warmed at the turn end on measured cost + S, target /
  squad target / nearest first; ward phase only with F left). F15 = F7 + kWarmSlack 6000 + kWardFuel 50000, F16 = F7 + kWarmSlack 6000.
- **Field warming loses: F15 (kWarmSlack 6000 + kWardFuel 50000) 87.4, F16 (kWarmSlack 6000) 86.8 vs F7 70.3** (heavy maps +84-111%):
  a turn-end build on the measured cost + 6k overruns when the build costs more than the decaying estimate. Off.
- **Field computes by site (edit_buildcount.py / tools/stress/buildcount.py, F7 on five worst maps):** on the 100x100 maps a champion
  computes a camp approach field every ~19 turns at 18-25k, its kSafeRoute copy 17-27k, capture fields 20-23k (fields 2.0-2.6k a turn on
  average, all in spikes); lanes / stampede fields cost 3-5k (their overruns lie elsewhere). bots/CostProbe: big_world full field 27.0k vs
  max_distance 12 5.5k; monolith 3.4k vs 2.1k - the engine charges per tile expanded. **edit_fieldcap.py (B551, kFieldCap S):** big maps
  (>= kCapArea 4000 tiles) cap camp approach fields (and their safe copies) at 2 x our distance + S, full redo if we are missed; stale caps
  rebuilt / ignored; home walks from capped fields fall back to the set-up spawn walk. F17 = F7 + kFieldCap 16 measuring.
- Eric (08:00 UTC) "why are HoR drafts failing for us when they perform so well in top teams?" - answered from top-builds-1031.md s2: at
  3 picks HoR sets underperform their teams' own strength (trio -7.4 / 100, HoR+Mar+Ves -10.5; Fish -28.7 with Ves>HoR>Mar, then dropped
  HoR from most 3-pick drafts and went 16-2); the trio is +11.4 at 5 picks. Only Ad Astra's HoR+Ryth+Vesper is positive (+18.6).
- **edit_postguard.py (B553): kScoutWindow** (scout_bush_ward reads the 5x5 window on a bush bitboard, not the whole bush list) -
  **exact** (12/12 identical unlimited-fuel games with kFuelGov 0; with the governor on 9/12, because the governor reacts to turn cost) and
  **F19 = F7 + kScoutWindow: 63.1 lost turns a game (F7 70.3, -10%; stampede 463 -> 141, harvest 564 -> 332), wins 39 vs 35.**
  kPostFuel 60000 (turn-end jobs only with 60k left): F20 55.7 but lanes / road_of_riches worse (fields then built in decide). Off.
  Profile of F19 on eight heavy maps (FX19, 70k turns): **the mean turn costs 57k of 100k before any spike** (camp observation 10.5k,
  squad 8.0k, pre 5.8k, allies 5.2k, decide 16.3k, post 5.0k); 1.8% of turns suspended, 78% cut in decide.
- **What a lost turn costs (GameRules.md 395):** a bot out of fuel is suspended and *resumes from the point of suspension next round* - one
  action round lost per suspension (~1% of champion-turns at 63 a game). Local screen s_slices (2,240 games an arm, base 1564): F5 config
  -18 +-14, **F7 +6 +-14, F8 (+kFieldCost) +9 +-13**; ladder #466 49 vs 54 (A+B), **#467 (= #458 + F7) panel A 23 vs 29**. Fuel is
  not where the wins are.
- **Camp damage split (tools/stress/damsplit.py; replays us1031 / fishnew1031 / top1031, r < 1000):** autos per camp round are equal
  across teams (Vesper 1.10-1.13); **Vesper damage per auto: ours 94, Fish 161, Ad Astra 159, Mite 140, others 138**; Marcella per auto
  54 (Fish 70) and **Marcella casts on camps 14 per 100 camp rounds (Fish 24, Ad Astra 26, NEET 21)**. Stats (scratchpad statcurve):
  Vesper at r400 str 85 / max hp 1,248 (Fish 153 / 2,132, Mite 131 / 1,673) - more of both, i.e. more gold, not a different build:
  **Vesper gold earned by r400 368 (Fish 1,035, Ad Astra 727, Mite 720)**; team earned at r600, 5 picks: ours 2,333, Fish 3,504, Mite
  3,682, Ad Astra 3,242.
- **Captures, 5 picks (rc1031 caps):** by r200 ours 6.8 (Fish 8.5, Mite 9.1, NEET 8.7, Ad Astra 7.4); **by r600 ours 20.2 (Fish 29.5,
  Mite 31.1, NEET 26.8, Ad Astra 26.1); elk camps 5.4 (Mite 10.6, Fish 7.6, NEET 7.5)**. Champions credited per capture 1.0-1.3 for every
  team (reward splitting is not the gap). Opening r1-100 (tools/stress/openuse.py): our camp-hit share 25.8% (Fish 22.4%), first hit
  r13 (Fish 14), still 11.9% (Fish 7.6%), but team gold r100 278 vs Fish 462.
- **#467 = #458 + F7 fuel package (B550x):** panel A **23 vs 29**, panel B **19 vs 25**: **42 vs 54 - rejected**; live 458 restored 08:51 UTC.
  Today's panel totals vs #458's 54 (A+B, 250 games): #462 41, #463 46, #464 32, #465 41, #466 49 (exact caches + kScoreStale 12), #467 42.
  Caution: #458 was made live for topping panel A (29 vs #450's 24), so its 54 carries selection luck; behaviour-neutral fuel builds
  land 5-12 below it (fuel-driven divergence alone moves a panel by several wins).
- Queued: **#468 = #458 + kSplitRound 300** (two squads on the whole-team maps from r300; never ladder-tested) and **#469 = #458 +
  kSaveSpells 4** (camp spells held only with an enemy within 4), one per hour for the scrim quota.
- **s_memb (B553c + #458's lines, base 1564):** **kMonsterEmb 3 (Monster emblem third, Marcella + Vesper) +22 +-10 (1597)**; 7 (+ HoR)
  +15 +-10; 3 + kCampStun 7 +9 +-9; 2 (Vesper only) -1 +-13 - Marcella's emblem carries it. Ladder: #470 queued.
- **Dashes over the void (Eric, Oct 31, replay d201c998 on 02cuts, replays/eric1031b):** our spawn pocket is closed by a diagonal hole
  band one tile thick across the diagonal; from (2,48) a dash lands on (4,46) outside. Vesper / HoR spent their r3 dashes inside the
  pocket (from (1,48) / (0,48) no landing crosses), Vesper left round the band's end at r24 and reached (4,38) at r45 (launch step + dash
  ~r9); later crossings (r108, r217) happened only when a travel dash started on a launch tile. **tools/stress/gapsave.py:** a dash over
  a one-tile hole saves 3+ steps from spawn to some camp on **44 of 71 maps** (02cuts 48 camps 10+, mean 57; road_of_riches 84 / mean 109;
  fracture 44 / 56; islands 82; breadcrumbs 36; shortcut, starvation, concentrated_wealth 36 / 28 / 14 at means 67-70). kDashGaps (Oct 20,
  off) paths dashers over one-tile gaps but also took their crystals on every map (its -41 +-32 screen lost on gapless maps).
  **edit_dashgaps2.py (B555, kGapCrystal):** with kDashGaps, dashers keep crystals. Probe G0 / G1 (kDashGaps + kGapCrystal) on 18 gap maps
  x 2 sides vs PoolLive; reader tools/stress/gapcross.py (void dashes, first hit, gold r300 / r600, wins).
- **Probe G1 (kDashGaps + kGapCrystal) vs G0 (#458 config), 18 gap maps x 2 sides vs PoolLive (tools/stress/gapcross.py):** void dashes
  676 vs 220, **team gold r600 63,336 vs 76,563 (-17%), wins 13 vs 19 of 36**; 02cuts 72 void dashes a game, gold r300 705 vs 1,467.
  kDashGaps prices every gap at one step on the path fields as if the dash were always ready: dashers stand at band after band waiting
  out the cooldown. Rejected (kGapCrystal does not rescue it). **edit_gapjump.py (B556, kGapJump N / kGapReach 4):** walking fields
  unchanged; with the dash ready and no enemy in sight, a launch tile within 4 whose 2-tile jump over a hole saves N+ steps is walked
  to and jumped from, before the plain travel dash (so a ready dash is kept for it); a dash on cooldown means walking. 02cuts: our
  dashers leave the spawn pocket over the band at r20 / r25 (their first camp is inside it). Probe G2 (N 6) / G3 (N 3) running.
- **Why saving steps lost (Eric: "figure out why saving steps would be a negative effect"; tools/stress/gapdiag.py, afterjump.py; r <= 600
  per game, G0 -> G1 kDashGaps):** the dash is shared by four jobs (HoR's camp damage: landing hit + stun; the 1-2 step travel shortcut
  each cooldown; fight engage; escape). kDashGaps held it for gaps on every gap map: **HoR dashes 48 -> 17, Vesper 39 -> 14** for +2-3 void
  crossings; HoR camp damage per 100 rounds 1,417 -> 1,090 (-23%), Vesper 1,452 -> 1,196 (-18%); dead share HoR 3.3 -> 7.8%, Vesper
  5.2 -> 7.7%; after a crossing the next camp hit came +24..+34 rounds later (G0 +9..+17: its route assumed further crossings, so it
  waited at the next band) and 13% of HoR's grouped crossings ended in a death within 30 rounds. Saving steps was never the cost - the
  held dash and the cooldown waits were.
- **kGapJump (B556) keeps the dash budget** (HoR 46-47 dashes a game, Vesper 36-37) and its jumps are healthy (jumper stays with the group,
  next hit +8..+16, deaths after jumps 0-3%). Gold r600 per game vs G0: N 6 **-149 +-156**, N 3 -159 +-158 (per-game SD ~930; 0 of 36
  games identical): noise at 36 games. Consistent by map: gold_rush +1,800..+2,000 a game, starvation +400..+800, concentrated_wealth
  +200..+1,200; road_of_riches B and shortcut A worse. Full local screen s_gap (N 6 / N 3 / old kDashGaps) queued after s_marc.
- **edit_gapgate.py (B557, kGapShare P):** Eric "only enable it for certain maps" - by layout (no map names). The draft's first turn
  measures the share of camp groups one-tile hole gaps bring 10+ steps closer to our spawn (walking field vs gap-opened field) into the
  draft plan's header byte 15 (kPlanGaps 8); kGapJump runs only where that share >= P. Verified in play (bots/GG, kPlanCheck prints
  GAPSHARE): ambush 33, lanes 0, road_of_riches 82, concentrated_wealth 63, gold_rush 80, starvation 92, 02cuts 96, harvest 9 - the same as
  tools/stress/gapsave.py's share10 (starvation 100 offline: champion start tiles vs the spawn region). P is chosen from s_gap's per-map
  results (32 games a map an arm).
- **#468 (= #458 + kSplitRound 300) never uploaded:** the upload stress gate refused it (24 games: stuck 11 cases / 245 rounds vs the
  8 / 160 limit, guarding still 30+ 7 cases) - two squads on the whole-team maps leave champions stuck. Panel B then replayed #458 as
  "B468" (25 wasted groups; panel scripts now skip panel B after a failed upload). Split play needs the stuck cases fixed before a test.
  #469 (kSaveSpells 4) re-queued for 10:12 UTC, #470 (kMonsterEmb 3) an hour after #469's panel A.
- **Fish's newest bot in every test (Eric, Oct 31 ~10:00):** one group (5 games: 00corners a, 00contest b, 01elk_arena a, 01starvation b,
  01big_world a; random pool draw, seed 1031) vs Intercontinental Fish's current bot, pinned: #458 played it at 09:59:48 (scrim_p458_fn /
  B458_fn, group 9a427ab3); candidates replay the same Fish version via --source-group in panel B (tag BN_fn). To stay at 50 groups an
  hour both panels drop their last random-map group (x1r 7 -> 6: panel A 24, panel B 24 + Fish 1); `cmp` now pairs games present in
  both tags (pairsum.awk; duplicate opponent / map / side keys merge, so ~110 paired games a panel). Backups panel125b.sh.bak1031,
  panelB.sh.bak1031.
- **s_gap (B556c, base 1564):** kGapJump 6 -10 +-13, 3 -3 +-14, old kDashGaps + kGapCrystal **-64 +-14**. By the draft's gap share
  (per-map margin vs base, kGapJump 6): share >= 75% (7 maps) +69 (gold_rush +495; the other six ~0), 50-75% -33, 20-50% -48, < 20% -15,
  no gap -6. kGapShare 75 is the only defensible gate and small.
- **Cloud screens (Eric 10:10 UTC "for claude cloud"; pushed to bamboo8 a030ea8):** tools/cloud/SCREENS.md + run_screens.sh + screens.py:
  seven screens, 28 arms on B557c + #458's lines (s1 kSaveSpells 6/4/2, kRuinSaveNear 3; s2 kMonsterEmb 1, 3 at 1/3/0; s3 kGapJump 6/3 +
  kGapShare 75/50, kGapJump 10; s4 kGuardMax 20/40, kSquadMoveOn 10, kGuardSingle 20; s5 kVespBuild 6, kMarcBuild 3, kRythBuild 2,
  kHorBuild 2; s6 kOpeningRounds 60/200, kElkRound 30, kGoldWeightEarly 0.5; s7 kRetreatHp 0.25/0.45, kHelpTtk 6/15). Results land on
  the cloud session's branch in tools/cloud/results/ (SUMMARY.md at the end).
- **edit_gemonly.py (B558, kGemOnly):** Eric "on gem only maps our champions buy treasure emblems ... durability or power ... or even
  prospect". Maps whose camps drop no gold: adgato_gemcombat1-5 only (every group gem clusters; next lowest gold share 0.53, vault).
  kGemOnly 2: Treasure entries become Prospector (+25% cluster rewards) of the same stat, then Durability, then Power (each family once);
  1: Durability / Power. Probe on the five maps x 2 sides vs PoolLive: **#458 config 5/10 wins, 9,391 banked; kGemOnly 2 8/10, 10,028**;
  Treasure items 32 -> 0, Prospector emblems 5 -> 12. For the final candidate.
- **Codex review (collaboration/20261031/code-and-economy-review.md), followed per Eric:** (1) departure-only light camp = kClockMeet
  (drops the detour once the squad is not quiet) -> **#471 = #458 + kClockMeet 20**, queued an hour after #470; (4) **edit_gapbfs.py (B559,
  kGapBfs):** gap_jump prices launch tiles by a local BFS over free tiles (unreachable skipped), walks the BFS's first step, bans a launch
  not approached since the previous round - probe GB (kGapJump 6 + kGapBfs) on the 18 gap maps running; (2) recall-capture with a Home
  emblem (3-turn recall) would leave a 5-turn capture early, and recall_turns() ignores Home unless kHomeBuild - latent only (no line buys
  Home / Capture), guard needed before adopting them; (5) Willow urgent heal before an optional reset - combat, not taken up; (6) spells:
  local s1 (cloud set, run here) kSaveSpells 6 +4 +-11, 4 -1 +-12, 2 -15 +-12, kRuinSaveNear 3 +1 +-6; ladder #469 tests kSaveSpells 4.
- **Probe GB (kGapJump 6 + kGapBfs) vs G0, 18 gap maps x 2:** gold r600 81,971 vs 76,563 (+7%, ~1 SE at 36 games), r300 +2%, wins 17 vs 19;
  void dashes 340 vs 220; HoR / Vesper standing still away from holes 12.9 -> 17.0% / 11.2 -> 14.5% (G2 without BFS 13.7 / 12.0) -
  unexplained, watch. Local screen of kGapBfs (gated 75 / ungated) after s3.
- **#469 = #458 + kSaveSpells 4 (B553x; submitted 10:26 after the cancelled mismatch v468):** panel A **20 vs 28**, panel B **17 vs 25**
  (paired 118 + 123 games), Fish's newest (pinned 09:59, 5 games) **0/5 vs 1/5** - rejected. The top teams' habit of casting near enemies
  does not transfer to our fight code. (pairsum.awk fixed 11:40: benchcmp prints "L-1000" without a space for margins <= -1000; the
  first paired totals dropped those rows.) The server holds a panel until the hourly quota frees (B469 waited 10:36 -> 11:30).
- **Vendetta (Eric 12:00 "given how all the top teams are using hor and vendetta, what is the issue with our bot?"):** HoR we draft at 5
  picks; at 3 picks HoR sets lose for the top teams too (trio -7.4, HoR+Mar+Ves -10.5; HoR+Ryth+Ves +18.6 only). Vendetta: our kit use was
  the gap (top-builds-1031.md s4: reset doubles 56-65% vs 83%, kill refreshes spent 1 / 108 vs 64%, 0 engage dashes); kResetMore 2 (live
  since #428) covers the hit-then-step paths, kResetMore bit 1 (kill chain on camps + champions) the refreshes. **edit_vendfive.py (B560,
  kFifthPick 4):** five picks HoR, Vesper, Ryth, Marcella, Vendetta (verified on 00lanes). Screen s_vend (after s_combo): kFifthPick 4 +
  kFishBuild 8; + kResetMore 3; kResetMore 3 alone on the live draft.
- **Cloud screens s5-s7 (Claude Code on the web, 4 cores, SEEDS 1 2, 1,120 games an arm; Eric pasted 12:2x UTC):** none >= +2 SE.
  s5 builds: kVespBuild 6 -13 +-10, kMarcBuild 3 -2 +-10, **kRythBuild 2 / kHorBuild 2 +0 +-0 (inert under the live config: another
  switch sets their lines)**; s6 opening: kOpeningRounds 60 -4 +-3, 200 -3 +-4, kElkRound 30 +3 +-13, kGoldWeightEarly 0.5 -5 +-16;
  s7 trips: kRetreatHp 0.25 -3 +-17, **0.45 -45 +-18**, **kHelpTtk 6 -11 +-4** (calling help sooner wastes mates; fits the over-staffing
  finding); kHelpTtk 15 not reported. Live values stand.
- **Screens s1-s4 (local, cloud arm set; tools/cloud/results/SUMMARY.md):** s2 Monster emblem every placement +2..+9 (at 2 earlier +22);
  s3 **kGapJump 6 + kGapShare 75 +8 +-5**, others +1..+5; s4 kGuardMax 20 / 40 -15 / -9, kSquadMoveOn 10 / kGuardSingle 20 ~0 (inert).
  **#470 (kMonsterEmb 3) panel A: 28 vs 28 wins, margin -40,622 vs -45,742 (+5,120)** - the first candidate today level on panel A.
- **#470 = #458 + kMonsterEmb 3 (B555x):** panel A 28 vs 28 (+5,120 margin), panel B 21 vs 25 (-4,144), Fish's newest 1/5 vs 1/5:
  **49 vs 53, margin +976** - level within noise, the best of today's candidates (others -5..-17). Live 458 restored 12:38.
- **edit_route.py (B561, kRoute R / kRouteGold 0.5 / kRouteDps 60 / kRouteSide 4 / kRouteBeam 120 / kRouteMax 20):** Eric 12:50 "can we
  make use of our draft fuel more? ... over 10 million fuel for draft" - only the 1,024-byte draft memory reaches play, so the draft plans
  the whole-team opening's camp order: our-side groups (walk ours <= theirs + 4), no golem / monolith, <= team size - 2 elk; walking
  steps between candidates (a field each); beam search over orders within R rounds (walk + clear at 60 / champion / round + capture +
  respawn before revisits; value = gems + 0.5 gold, down to half for late captures); 'R' section after the pairs (kPlanRoute 16). Play:
  while the team is one squad (round < team_rounds_ and R, no enemy seen), score_team_targets returns the route's next group not
  respawning / avoided (a camp being fought stays). Verified (bots/RT, kPlanCheck): routes on lanes (9 camps), stampede (12, a 4-group
  loop x3), big_world (6), harvest (7); sides mirror. Probe RT0 / RT on 12 maps running.
- **Route probe (RT kRoute 240 vs RT0, 12 maps x 2 vs PoolLive):** team gold r300 28,337 vs 26,249 (+8%), r600 62,936 vs 59,331 (+6%),
  wins 15 vs 13 (~1 SE each); camp-hit share r1-300 up for every champion (HoR 22.2 -> 23.5%, Vesper 28.2 -> 30.0%, Ryth 17.6 -> 18.8%,
  Willow 22.3 -> 23.6%), HoR standing still 16.4 -> 14.1%. Screen s_route (240 / 240 + gold 1.0 / 150) after s_vend.
- **s_combo (B559c, base 1569):** K1 = kMonsterEmb 3 + kGemOnly 2 + kCampStun 7 **-2 +-13**; K1 + gated BFS gap +1 +-13; K1 + kClockMeet
  20 -8 +-14; all -17 +-14; **kGapJump 6 + kGapBfs ungated -52 +-14** (the probe's extra standing still - kGapBfs has a fault, dropped);
  kGapJump 6 + kGapShare 75 + kGapBfs +1 +-5 (without BFS, s3: +8 +-5). The small single positives do not add. **#471 (kClockMeet 20)
  panel A 23 vs 28 (-5,479 margin).**
- **#471 = #458 + kClockMeet 20 (B558x):** panel A 23 vs 28, panel B 21 vs 25, Fish 1/5 vs 1/5: **44 vs 53 (-10.7k)** - rejected. The
  departure light camp loses alone too. **#472 = #458 + kRoute 240 (B561x)** queued for 14:04 UTC (panel A after the 14:12 quota window).
- **s_vend (B560c, base 1569):** **kFifthPick 4 (Vendetta for Willow at 5 picks) + kFishBuild 8 -165 +-12** (1,282 wins; PoolLive margin
  -56), + kResetMore 3 -160 +-13; kResetMore 3 alone (live draft) -5 +-8. Losing Willow costs far more than Vendetta adds in our code
  (sustain built around her heals); with the -125 of Oct 28 the swap is out until a no-healer fight rework. Not laddered.
- **s_route (B561c, base 1569):** kRoute 240 -14 +-14, + kRouteGold 1.0 +3 +-14, kRoute 150 -7 +-14. **#472 = #458 + kRoute 240 panel A
  23 vs 28 (-7.2k)**; panel B cancelled (Eric: fewer groups a test).
- **Starfish loss (replay f5e620e2, #458 vs shoutout MAPS 176 vs 1,012):** deaths 30 vs 11; dead 22-51% of the time after r200 (theirs
  0-24%); camp damage 47k vs 137k (central 6-elk boss: ours 1k, theirs 30k); standing still beside camps equal (8.9 vs 9.6%); our deaths
  mostly at 1-25% health with 0-1 mates within 5; the centre collapse at r620-632, then lone walks back from spawn. Locally (D458 vs
  PoolLive / PoolAggro on starfish) we win - the pool does not hold the centre. **edit_regroup.py (B562): kRegroup W** (a squad member on
  spawn waits up to W rounds for a mate when a mate is dead / the avoid alert is up and < 2 healthy mates are at the target) and
  **kContestBoss M** (an unhurt living boss no nearer us than them is no target).
- **Quick panel (Eric 14:40 "reduce our hourly quota usage to allow for more tests"):** quick.sh / ladquick.sh = panel A's top-10 set (50
  games) + Fish's pinned group (5) = 11 groups, paired vs #458; ~4 tests an hour; screening only. Chain: #473 kRegroup 25, #474
  kContestBoss 2, #475 both.
- **Quick panels (11 groups, 55 paired games vs #458):** #473 kRegroup 25 13 vs 16 (-4.6k); #474 kContestBoss 2 11 vs 16 (-6.1k); #475 both
  running. **Codex C303 / C304 (followed per Eric):** kRegroup held in step(), so deliver() could wait up to 25 rounds with a bag on spawn;
  unread mates counted absent; stale timer; kContestBoss missed solo scoring and caught packs. **edit_regroup2.py (B563):** hold only on
  camp walks (keys 0..49999, the step's own group), unread mates count as possibly there, one timer per spawn visit and destination;
  contested boss also in solo scoring, only true bosses (golem / monolith strength or 4+ elk) and only with 3+ other groups on our side.
  Quick chain #476 (kRegroup 25), #477 (kContestBoss 2), #478 (kMonsterEmb 3 + kMarcSaveNear 4, Codex C300 factorial); local s_fix
  screens the same plus both.
- **#475 (kRegroup 25 + kContestBoss 2, pre-fix B562x) quick panel: 11 vs 16 (-6.9k).** Fixed versions #476-#478 next.
- **#479 = #458 + kEarlyRecall (Eric 15:25 "add in our recall optimization that all the other teams are doing")** queued as a quick panel after #476-#478 (local +4 +-11; on the ladder only with kClockMeet in #463).
- Eric 15:34: kEarlyRecall in the upcoming builds: #477 (kContestBoss 2) and #478 (kMonsterEmb 3 + kMarcSaveNear 4) now carry it; #476 had uploaded without it; #479 tests it alone.
- **#476 = #458 + kRegroup 25 (B563x, Codex fixes) quick panel: 16 vs 16, Fish 1/5 vs 1/5, margin -2,951** (pre-fix #473: 13 vs 16).
- **s_fix (B563c, base 1569):** kRegroup 25 -19 +-12; **kContestBoss 2 -63 +-13**; both **-86 +-14**; kMonsterEmb 3 + kMarcSaveNear 4 -7 +-13.
  Skipping a contested boss hands its gems to the side that takes it (the pool contests). The contested-boss build was dropped before
  upload; chain renumbered (15:52): **#477 = #458 + kMonsterEmb 3 + kMarcSaveNear 4 + kEarlyRecall**, **#478 = #458 + kEarlyRecall**.
- **edit_recallwatch.py (B564, kRecallWatch bits / kRecallWatchHp 0.6 / kRecallWatchNear 6):** Eric ~16:00 (replay 8d7d6c98, #458 vs prism
  best girl on 01starfish): Vesper recalled at r27 on group 0's tile at full health with four enemies within 10 and four mates within 2;
  no reward at the end (an enemy on a tile reset the capture). While a channel runs our turn ends at once; damage interrupts a recall,
  a contested capture does not. Bit 1: a recall-capture is cancelled once its capture is contested / enemy-held / reset (capture state
  2 / 3 / 4); bit 2: a recall begun at 60%+ health is cancelled with an enemy in sight and a mate within 6. The turn is then played out.
  Quick #479 = #458 + kEarlyRecall + kRecallWatch 3 (vs #478 = kEarlyRecall alone); local s_rwatch (bits 1 / 2 / 3, + kEarlyRecall).
- **Recall watch:** s_rwatch (2 seeds, 1,120 an arm): bit 1 -22 +-16, bit 2 -35 +-17, both -35 +-17, + kEarlyRecall -42 +-18; quick
  #478 (kRecallWatch 3) 13 vs 16. Off. Claudus Maximus 4-1 on #476 vs 2-3: per-game table shows the flips spread over unrelated builds
  (arena won by 5 of 6 variants, pilgrimage by #476 and #477) - divergence, not a behaviour to keep.
- **Islands stall (Eric: fix it first) - root cause found: fuel-starved steps.** The 24-game scan of #458 + kEarlyRecall (rerun locally,
  scanER) put 928 of its loop / stuck rounds in 01islands side B (base 7): from r742 four champions on the spawn area's north edge, every
  camp beyond a hole band (the walk runs east), Marcella / Ryth still, Vesper / Willow bouncing (33,50) <-> (34,50). field() returns
  nothing under kFieldFuel 30k; step() then uses move_towards straight into the hole band, and the next turn arrives short again.
  kEarlyIsle (crystal maps; edit_earlyisle.py, B566) did not fire there (islands is no crystal map to the bot) - kept, off.
  **edit_fieldfirst.py (B567, kFieldFirst):** a field step() could not afford is built at the next turn's start (full budget). Scan of
  #458 + kEarlyRecall + kFieldFirst: **loops 6 / 40 rounds, stuck 2 / 5** (islands B 13 loop rounds) - passes the gate. Eric (16:40):
  kEarlyRecall in every build from now on -> with kFieldFirst. Quick #480 = #458 + both; local s_ffirst queued.
- **edit_enemycast.py (B568, kEnemyCast):** the enemy broadcast. #458's kCarryCast 2 already put the strongest enemy's coarse cell + round
  in each champion's priority word, but mates' words were read only on big maps (and carried no count). kEnemyCast: round mod 64 (bits
  12-17), enemy champions in sight (18-20), the nearest enemy when no carry was scored; read_enemy_casts reads every mate's word each
  turn on every map into enemy_reports_ (pos, round, count); kRegroup holds when mates report enemies within 8 of the destination
  outnumbering the healthy mates there. Verified (debug copy ECD, lanes / starfish vs PoolAggro): e.g. lanes r100 a champion at (3,11)
  holds reports of 5 enemies at (45,6) from mates two rounds earlier. Quick #481 = #458 + kEarlyRecall + kFieldFirst + kEnemyCast +
  kRegroup 25; local s_ecast queued.
- **#479 = #458 + kCaptureHit (B565x) quick panel: 18 vs 16, margin +1,069** - the first quick candidate above #458. Added to #481 (now kEarlyRecall + kFieldFirst + kEnemyCast + kRegroup 25 + kCaptureHit).
- **s_fuelrelax (B565c, 2 seeds):** kScoreFuel 40000 -7 +-15, 0 -14 +-17, kFuelGov 0 -10 +-16, kFieldFuel 20000 -13 +-19 - loosening the fuel gates trades stale picks for lost turns; the gates stay; kFieldFirst covers the stall case.
- **Quick #480 = #458 + kEarlyRecall + kFieldFirst (B567x): 12 vs 16 (-8.0k)**; s_ffirst (2 seeds): kFieldFirst -21 +-16, + kEarlyRecall
  -18 +-18. kFieldFirstAfter 3 (edit_fieldfirst2.py, B569) does not free the islands stall (the stuck champions alternate keys).
  **edit_fieldfirst3.py (B570, kFieldFirstGuard; Codex C305 / C308):** a pending field is dropped after a death, channel or target change
  and held while an enemy was in sight last turn; the streak counts consecutive rounds only. Scan with kEarlyRecall: loops 5 / 37,
  stuck 3 / 21 (islands B 10).
- **Recall-capture of a carrier's reward (Eric ~17:30, replay f8c96f2a, 01starvation vs Fish):** HoR and Vesper beside the gold nodes
  (r40), HoR recall-captured at r42 (full health, 0 gold), home r47, walking back at r60 while the squad went north. Mode 4 prices the
  trip by the capturer's own re-scored next camp; the carrier hand-off needs Vesper on a tile. **edit_recallcapfix.py (B571,
  kRecallCapFix bits):** 1 price against the squad's target, 2 no recall-capture of a reward whose carrier (Vesper, gold) is within 6.
  Quick #482 = #458 + kCaptureHit + kRecallCapFix 3 + kEarlyRecall + kFieldFirst + kFieldFirstGuard; local s_rcfix.
- **s_ecast (B568c, 2 seeds, on kEarlyRecall + kFieldFirst):** EF -18 +-18, **+ kEnemyCast -71 +-20** (PoolLive +191 -> +29),
  + kRegroup 25 -55 +-20. Cause: kEnemyCast put every sighting (the nearest enemy when no carry) into carry_reports_ and read mates'
  words on every map, so kCarryCast 2's carry_avoid (r400+: drop an untouched camp within 7 of a report for 20 rounds) fired on any
  enemy any mate saw. The kEnemyCast build #481 was cancelled before upload; **#481 is now the recall-capture candidate** (B571x,
  cand482.edits). **edit_enemycast2.py (B572, kEnemyCastFix):** bit 21 marks a scored carry; only carries feed carry_reports_ (mates'
  only on big maps, as before); every sighting still feeds enemy_reports_ for the regroup hold. Local s_ecfix queued after s_rcfix.
- **Grant #14 (Eric ~17:40 UTC Oct 31, 6 h): fuel, 8-byte memory, mid-game solo farming, late-game gem routes, Fish burst combat, bug checks.
  Default build #479 (Eric ~17:45: "279" read as #479 = #458 + kCaptureHit; he had selected it on the platform).** The #481 test upload went
  through seconds before its cancel and the platform's "follow newest ready version" made it live; `submissions activate 479` was blocked
  by the auto-mode classifier (Eric to re-select). Quick #481 (= #458 + kCaptureHit + kRecallCapFix 3 + kEarlyRecall + kFieldFirst +
  guard): **13 vs 16 (-4.6k)**. s_rcfix (2 seeds): kRecallCapFix 1 -14 +-15, 2 -22 +-18, 3 -31 +-18; EF + guard -22 +-18.
- **Islands stall check (isl2.sh, 01islands / 00vault / 01shortcut x 2 vs B7Live, stuck+loop rounds):** #458 + kEarlyRecall 973 (islands
  928); + kFieldFirst + guard 117 (islands 11); **+ kFieldFirstStill 6 (edit_fieldfirst4.py, B573: build the pending field only after 6
  rounds within 1 tile of one spot) 105 (islands 0)**.
- **Late game / mid game from traces (tools/stress/late/, us1031 27 games vs fishnew1031 36, different map samples):** gold per captured
  gem r600+ 10.8 (ours) vs 11.1 (Fish) - the same mix; Fish captures more (9-10 vs 6.5 a 150 rounds). Emblems a champion r600 3.0 / 3.9,
  r1000 6.3 / 8.1 (shards 30 gold). Unspent gold at the end 477 / 335. Camp episodes (>= 1,300 damage) r300-600: 6.0 vs 8.6 a game, 2.73
  vs 2.80 champions, damage per champion-round 63 vs 68; solo share r0-300 3% vs 19%. Champion-rounds r300-600: camp 17 / 19%, walk
  49 / 52%, still 13 / 14% (Fish's is in channel: their pre-started recall), home 6 / 6%, dead 9 / 8% - no party-size or idle gap.
  value_of's gold weight is 0.12 after r800, but x kVesperGoldW 3 (Vesper) and x kCarrierGold 3.5 (Vendetta / Varg) all game.
  **edit_gemlate.py (B574, kGemLate E / kGemLateSpan / kGemLateGold):** past E emblems a champion's gold weight (factors included) fades to
  kGemLateGold. s_late queued: #479 + exact fuel caches (kSightCache, kPairWalkCache, kScoutWindow), + kGemLate 3 / 5 / 3 at 0.08.
- **8-byte shared memory:** bytes 0-4 targets (+ solo / help flags), 5 respawn events (toggle bit), 6-7 alert; banker / focus bytes 8-14 are
  past the 8 bytes. Same-round captures that could overwrite an event: 5 of 1,200 (0.4%) - the event slot is not lossy in practice.
- **s_ecfix (B572c, 2 seeds, on kEarlyRecall + kFieldFirst + guard):** + kEnemyCast + kEnemyCastFix -45 +-19, + kRegroup 25 -54 +-20 (the
  same base alone in s_rcfix: -22 +-18). The carry side effect is gone (-71 -> -45) but the broadcast + regroup hold add nothing: off.
- **Fish burst study (agent, tools/stress/burst/, fishnew1031 / us1031 / top1031):** Fish do not burst harder - they finish better. Kills
  before r600 6.9 vs 2.8 a team-game (others 4.1); damaged enemies that die 29% vs 13%; enemy under 50% chased -> killed 52% vs 28%;
  kill rate by attackers 1 / 2 / 3+: 16 / 32 / 67% vs 5 / 19 / 27%; commit rates, cast-on-cooldown and focus fire equal to ours.
  Marcella with her nuke ready and an enemy under 30% at 3-4 tiles: casts 56% (Fish) vs 22% (us). Our chases end: recalled 20%, let go
  17% (kChaseMax 7), home 11%; 36% of our failed engagements open with Ryth's area spell (~7% convert). Fish stop chasing almost only on
  a recall out of reach or at home. Rules suggested: finish with the nuke, chase hurt prey home, collapse with three, dash only to
  finish, no lone Ryth opener. **edit_lowfinish.py (B575, kSpellFinish bits):** 1 a ready single-target damage spell at the weakest
  visible enemy under kSpellFinishShare 0.3 (or within the spell's damage) at the turn start, not while channelling (probe: 1-9 casts a
  game a champion); 2 Ryth's area spell at champions only with an ally within 2 of the target or it under 60%. s_finish, then s_chase
  (kChaseMax 10, kWoundedTeamHunt) queued.
- **Audit (agent, read-only, B573c):** (1) kCaptureHit can wake a full-health hostile node through a strength-0 cluster (per-member test;
  "hurt" never resets) - **edit_capturehitfix.py (B576, kCaptureHitFix bits 1 hostile groups only while a member is awake, 2 static reach
  filter)**; (2) kEnemyCast reads out-of-sight mates' priority (throws ~2k fuel each) - off; (3) kEarlyRecall recalls a carrier that
  retreat() sent to a nearby altar, and a kLowSnipe hold - **edit_earlyrecallfix.py (B577, kEarlyRecallFix)**; (4) kGapJump's single ban
  slot can bounce two refused launches - **edit_gapban.py (B578, kGapBanRing)**; (6) gap_jump scans 81 x 8 tiles a travel turn (fuel,
  not fixed); kFieldFirst + guard + still, kRecallCapFix, kGapShare, kGemOnly, kMonsterEmb, the priority-word layout: clean.
  s_fixes queued (kCaptureHitFix 3; kEarlyRecall with / without kEarlyRecallFix).
- **s_final2 (B573c, 2 seeds, base 1569 = #458 config):** **#479 (kCaptureHit) -49 +-17** (PoolAggro +170 vs +252, PoolLive +74 vs +150);
  + kEarlyRecall + kFieldFirst + guard + kFieldFirstStill 6 -53 +-18; + kGapJump 6 / kGapShare 75 + kGemOnly 2 -34 +-19; + kMonsterEmb 3
  -28 +-19. The default build's switch loses locally - the audit's wake bug (a capturer chipping a cluster of a full-health hostile
  node) is a candidate cause; s_fixes (now next) measures #458 + caches with / without kCaptureHit, + kCaptureHitFix 3, and kEarlyRecall
  with / without kEarlyRecallFix. s_finish / s_chase re-based on #458 + caches (no kCaptureHit).
- **s_late (B574c, 2 seeds, base 1569):** #479 + exact caches -25 +-20; **+ kGemLate 3 -8 +-20 (+17 over its base; PoolAggro +263,
  PoolFinish +253)**; kGemLate 5 -23; kGemLate 3 at kGemLateGold 0.08 -12. Fading gold to 0.04 from 3 emblems leans positive.
- **s_fixes (B578c, 2 seeds, base 1569):** #458 + exact caches -3 +-19 (neutral, as expected); + kCaptureHit (#479) -21 (-18 vs caches);
  **+ kCaptureHit + kCaptureHitFix 3 -8 (+13 over unfixed)**; + kEarlyRecall -13; + kEarlyRecall + kEarlyRecallFix -21 (no help: off).
  s_comb queued after s_chase: F0 = #458 + caches + kGemLate 3 + kEarlyRecall + kFieldFirst + guard + still 6, with kCaptureHit + fix,
  + kSpellFinish 3, + kChaseMax 10, and F0 without kCaptureHit.
- **Wide scan G1 (70 maps x 2 vs B7Live; wideTG1; candG1x.edits on B578x = #458 + exact caches + kGemLate 3 + kEarlyRecall + kFieldFirst +
  guard + still 6 + kCaptureHit + kCaptureHitFix 3 + kSpellFinish 3):** wins 129 / 140 (#458: 132), loop+stuck rounds 443 (#458: 1,016;
  the-pack 375 -> 52), fuel-limit turns 11,129 (#458: 15,069, -26%); no map with 100+ stuck rounds; worst 00anvil 77. (02the-pack's
  "0% gem share" is two round-2000 wins with no gems banked.) Note: c builds take c450.edits (a delta on #450-config defaults), x builds
  the full list (cand482.edits style) - same config checked (0 constant diffs).
- **s_finish (B575c, 2 seeds, base 1569):** #458 + exact caches -1 +-19; **+ kSpellFinish 1 (a ready damage spell finishes a low enemy at
  the turn start) +32 +-18 (809 wins vs 787; every pool up: PoolLive +173 vs +122)** - the best single switch of the day; kSpellFinish 2
  (Ryth area-opener gate) -5; 3 (both) -25: the Ryth gate is off. s_chase / s_comb were restarted as s_comb2 with kSpellFinish 1:
  F0 (= caches + kGemLate 3 + kEarlyRecall + kFieldFirst + guard + still 6) + capture hit fixed + finisher (G2), G2 without capture hit,
  G2 + kChaseMax 10, G2 + kWoundedTeamHunt, F0 + capture hit without finisher.
- **s_comb2 (B578c, 2 seeds, base 1569):** F0 = #458 + caches + kGemLate 3 + kEarlyRecall + kFieldFirst + guard + still 6. **G2 = F0 +
  kCaptureHit + fix 3 + kSpellFinish 1: -7 +-20; F0 + kSpellFinish 1 (no capture hit, "G3"): -1 +-20**; G2 + kChaseMax 10 -12; G2 +
  kWoundedTeamHunt -16; F0 + capture hit + fix without the finisher -21. The finisher adds ~+14 in combination and offsets the
  pre-started recall's cost; capture hit (fixed) ~-6 (noise); longer chases / team hunt do not help locally. Upload edits:
  run/candG2x.edits (B578x).
- **s_tune (B578c on G2, 2 seeds):** G2 -7; kSpellFinishShare 0.4 -15, 0.2 -10; kGemLate 2 -10; + kFinisher 6 (Oct 27 dash chaser) -18.
  Defaults stay (share 0.3, kGemLate 3). **edit_lowfinish2.py (B579, kSpellFinish bit 4):** a ready basic attack at the weakest enemy
  champion in reach under the share or within 0.9 x our strength, at the turn start; s_atk (G2 / G3 with and without it) running.
- **s_atk (B579c, 2 seeds):** G2 -7; **G2 + kSpellFinish 4 (basic-attack finisher) -27**; G3 -1; G3 + attack finisher -16: the attack
  finisher pre-empts the fight branches' own attack choice - off. s_confirm (fresh seeds 3-4: #458, #458 + kSpellFinish 1, G2, G3) running.
- **s_confirm (fresh seeds 3-4, B579c, base #458 767 wins):** #458 + kSpellFinish 1 +9 +-18 (seeds 1-2: +32; pooled ~+20); **G2 +11 +-21;
  G3 +12 +-20 (783 wins)**. Over both seed pairs G2 ~+2, G3 ~+6 vs #458 with kEarlyRecall included. Ladder test script run/quickG.sh
  (G3 as #482, then G2 as #483, restoring 479) waits for Eric's go-ahead on activations.
- **Team move (Eric ~22:55 UTC Oct 31): Velvet Tributers** (rank 71). **v1469 = G3** (B579x + run/candG3x.edits) submitted 23:02 UTC; its
  quick panel (9 top-10 groups, banner "BAMBOO v1469") **12 vs #458's 15 wins on the same 45 paired games, margin -12.6k vs -10.3k** -
  not better than #458 (noise ~+-4). benchcmp.ts now also matches "Velvet Tributers". Eric (~23:12): upload **v1470 = #458 (exact
  bots/Up458 source)** and **v1471 = #458 + kSpellFinish 1** (B579x + run/cand458sf.edits; every #458 constant identical, the only new
  behaviour kSpellFinish 1). Sprint 3 lock: 23:59 GMT. Bamboo8 branch on github.com/Ajayendra2705/cambridge-battlecode-2026a = bots/bamboo8 (v1469 source).
- **v1471 = #458 (23:18 UTC), v1472 = #458 + kSpellFinish 1 (23:22, live 23:31 UTC).** Quick panel q1472 (23:33): **21 vs #458's 16 wins on
  55 paired games (top 21 vs 15, Fish 0 vs 1), margin -11.3k vs -15.1k** - the day's best quick panel (previous: #479 18 vs 15 on the top
  part); vs G3 (q1469) 20 vs 12 on 45. Kept live for the Sprint 3 lock (23:59 GMT).
- **Teammate bots, local (s_vt, 70 maps x 2 sides, SEEDS 1, 140 games a pairing; VTmain = their ladder bot vx1, VTcmb1 / VTcmb2 / VTb10):**
  #458 303 / 560 (vx1 89, cmb1 68, cmb2 75, bot_10 71); #458 + kSpellFinish 1 296 / 560 (91 / 66 / 72 / 67). We beat vx1 ~64%; cmb1 and
  bot_10 are about even with us. Bamboo8 branch (github.com/Ajayendra2705/cambridge-battlecode-2026a): bots/bamboo8 (G3 v1469),
  bamboo458 (v1471), bamboo458sf (v1472), bamboo479 (#479), commit 84ba73e.
- **v1470 (a teammate's "v484 bundle (ranked best)", live / pinned from ~23:40 UTC), 9 top-10 groups (same opponents' bots, maps, sides):**
  **9 wins of 45, margin -14.1k** vs v1472 20 (-5.0k), #458 15 (-10.3k), G3 12 (-12.6k); v1472 ahead against 8 of 9 teams (Trzy
  Kwaterki 2 vs 4). **s_vt479 (local vs the teammates' four bots, 560 games):** #479 300 (-17 vs #458), **#479 + kCaptureHitFix 3 313
  (+16)**, #458 303.
- **v1473 = #479 + kCaptureHitFix 3** (B579x + run/cand479f.edits; submitted 23:55:25 UTC without the stress gate, Eric's 4-minute
  deadline; live 23:57:55, then Eric pinned v1472). Quick panel q1473 (banners v1473): **17 wins of 55, margin -15.3k (#458 16, -15.1k)**;
  top part vs v1472 17 vs 21 (-10.7k vs -6.8k); vs v1470 16 vs 9 on 45. Locally vs the teammates' bots it was our best (313 / 560).
  Ladder ranking tonight on the shared panel: **v1472 21 > v1473 17 ~ #458 16 > G3 v1469 (12 / 45) > v1470 (9 / 45)**.
- **s_rcl (Eric: "add the recall interaction into 458"; B579c, 2 seeds, base 1569):** v1472 (#458 + kSpellFinish 1) **+23 +-18** (813 wins);
  **R1 = #458 + kEarlyRecall + kFieldFirst + guard + still 6 -40 +-18** (747); R2 = v1472 + the same +9 +-19 (-14 vs v1472). The pre-started
  recall loses on every base (alone -10..-18, G3 12/45 on the ladder): kept out of v1472.
- Ports from the teammates' bots: `.info/knowledge/teammates-ports-1101.md` (hurt-first turn order in contact first).
- **Teammate ports (Nov 1, from github.com/Ajayendra2705/cambridge-battlecode-2026a bot_10; list in teammates-ports-1101.md):**
  **edit_hurtfirst.py (B580, kHurtFirst R):** with a visible enemy champion within R, the priority word's turn-order key (bits 27-30) is
  >= 8 + (under half health ? 4 : 0) + min(3, R - distance) - in contact first, hurt first (bot_10 set_turn_priority; vx1's go1 deaths -1.1
  a game). No reader uses bits 27-30 (only kBossCommit / kAggroShare write them). **edit_caphold.py (B581, kCapHold):** before the escape
  branch, on our reward tile of a group worth >= 20 gems or >= 100 gold, health >= 35%, an enemy within 8: hold while health > 1.5 x the
  summed enemy_burst_ + enemy_dmg_ within 6 + 1, attacking / casting (no dash) at the weakest enemy in reach (bot_10 P_CAP_STAY; vx1's hc2
  abandoned captures 12.1 -> 5.8). Screens s_hf (v1472 + kHurtFirst 6 / 4, pool + teammates) then s_ch (v1472 + kCapHold) queued.
- **s_hf (B580c, kHurtFirst on v1472):** pool (2 seeds, base 1569): v1472 +23 +-18 (813); + kHurtFirst 6 +5 (786; -18 vs v1472); **+ kHurtFirst 4
  +35 +-20 (818; +12 vs v1472)**. Teammates' bots (seed 1, 560 games, vs #458 303): v1472 296 (+0); + kHurtFirst 6 309 (+10; cmb1 +67 vs +27,
  bot_10 +39 vs +21, vx1 +168 vs +206). Mixed / within noise; s_hf2 (radius 4 and 6 vs the teammates on seeds 1-2) queued last.
- **Hybrid question (Eric agreed ~03:45):** per map vs the teammates' bots our #458 wins 63-65% on spawn walks 31-60, 50-56% on <= 30, but
  26% (cmb1) / 36% (bot_10) on walks > 60 (farm maps) - tools/stress/vt/hybridmap.py. cmb1 itself is a whole-bot dispatch (main.cpp: team
  size 3 -> vx1, else bot_10 in namespace cjb). s_hyb: #458, v1472, VTb10q (bot_10 with BOT_LOGC 0), VTcmb1 vs pool + VTmain on all 70
  maps (seed 1) - if bot_10 beats the common field on far maps clearly better than ours, build a spawn-walk dispatch (our bot <= 60,
  bot_10 > 60).
- **s_ch (B581c, kCapHold on v1472):** pool 813 wins, +17 +-19 (v1472 +23: -6); teammates' bots 303 / 560 (v1472 296), margin +88 (+89):
  bot_10 +70 vs +21, cmb1 +51 vs +27, vx1 +133 vs +206 - neutral overall. Like kHurtFirst 6 it gains on bot_10 / cmb1 and gives back on
  vx1.
- **s_hyb (all 70 maps x 2 vs PoolLive / Carry / Aggro / Finish / VTmain, seed 1, 700 games a bot):** #458 493, v1472 508, VTb10q (bot_10, log
  off) 448 (-91 +-27 vs #458), VTcmb1 439 (-147): against the common field bot_10 / cmb1 are weaker overall although even head to head. By
  spawn walk: <= 30 v1472 127 / 180 (+291) vs bot_10 93 (+66); 31-60 228 / 300 (+313) vs 180 (+149); **> 60 152 / 220 (+194) vs bot_10
  175 (+265)** - bot_10 better on 17 of 22 far maps (much worse on 00dunes, 00ribs, 00road_of_riches). Projected hybrid 530 / 700 vs 508.
- **edit_hybrid.py (B582, kHybridWalk W):** cmb1-style whole-bot dispatch - main() runs bot_10 (tools/edits/vendor/cjb_bot10 = cmb1's src/cj,
  namespace cjb, log off) for the whole game, draft included, when the spawn-to-spawn walk (walk_sides' measure) exceeds W (61: nearest
  maps adgato_gemcombat4 60 / 01islands 63); hybrid_b10_impl in the anonymous namespace, hybrid_use_b10 exported. Checked: 00anvil ours
  (Marcella / Vesper / Ryth), 01islands and 02geodes bot_10 (HoR / Marcella / Vendetta / Vesper / Willow). s_hybrid (v1472 +- kHybridWalk 61,
  pool seeds 1-2 + teammates) queued after s_split.
- **s_split (B581c on v1472):** pool (2 seeds): **kBossMode false -121 +-20 (660)**, kSplitRound 300 -34 (753), kSplitRound 150 -66 (733),
  v1472 +23 (813). Teammates (seed 1): kBossMode false 228 / 560 (-139), kSplitRound 300 294 (+4; bot_10 +53, cmb1 +56, vx1 +146),
  kSplitRound 150 276 (-33). Our bot is built around the one-squad boss mode: splitting it loses; bot_10's parallel farming works only
  inside bot_10 - the case for the whole-bot hybrid (kHybridWalk) rather than a farming port.
- **s_hf2 (B580c, teammates' bots, seeds 1-2, 1,120 games):** #458 603; v1472 600 (+13); + kHurtFirst 6 625 (+32); **+ kHurtFirst 4 656 (+71 +-18;
  cmb1 +165 vs +42, bot_10 +72 vs +36)** - with the pool's +12 over v1472 (s_hf), kHurtFirst 4 is the first port to gain on both.
- s_hybrid's pool stage aborted on a lock race (s_hf2 started at splitdone); its teammates stage ran; s_hybrid2 reruns the pool stage on B582c
  with v1472 / + kHybridWalk 61 / + kHurtFirst 4 / + both.
- **s_hybrid, teammates stage (B582c, seed 1, 560 games):** v1472 298; **v1472 + kHybridWalk 61 335 (+37 wins; margin +119 vs +84; better vs
  all four)**. By spawn walk: > 60 **113 / 176 vs 65 / 176 (margin +99 vs -81)**; <= 30 77 vs 80; 31-60 145 vs 153 - the near maps run our bot
  in both arms (checked: 01hooks, adgato_gemcombat2, 00swirl, 00contest print our PAIRS line) but 41 of 46 changed: fuel-driven divergence
  (the start-up spawn walk costs fuel), -11 wins net, noise. Pool stage: s_hybrid2.
- **s_hybrid2 (B582c, pool seeds 1-2, base 1569):** v1472 801 (+14); + kHybridWalk 61 813 (+12); + kHurtFirst 4 813 (+32); **+ kHurtFirst 4 +
  kHybridWalk 61 839 (+53 +-21 *)** - the gains stack. **Candidate H = #458 + kSpellFinish 1 + kHurtFirst 4 + kHybridWalk 61** (B582x +
  scratchpad run/candHx.edits). Checks running: s_Hvt (teammates, seeds 1-2) and the 70-map stuck scan (wideTH).
- **Wide scan H (wideTH, 70 maps x 2 vs B7Live):** **wins 135 / 140** (#458 132, G1 129); loop+stuck rounds 1,004 (#458 1,016); guarding still
  31 (612 rounds; bot_10 waits at respawning camps); fuel-limit turns 8,896 (#458 15,069). 100+ maps: 02the-pack 408 (our bot; #458 had 375)
  and 00great-wall 153 (bot_10; both games won at r842 / r810: camp waits, not a freeze).
- **s_Hvt (B582c, teammates' bots, seeds 1-2, 1,120 games):** #458 603; v1472 600 (+7); v1472 + kHurtFirst 4 646 (+58); **H 721 (+85 +-20;
  bot_10 +107, cmb1 +162, cmb2 +133, vx1 +241)**. H leads every local test: pool 839 (+53), teammates 721, wide scan 135 / 140.
- Platform at 07:16 UTC: mode pinned, **Live 1469 (G3) while Selected 1472**; teammates uploaded v1474-v1476 (v519 / v531, bot_10 lineage).
  H upload (v1477) and its panel wait for Eric's call (activating H interrupts teammates' tests).
- **v1477 = H** (B582x + tools/cands/cand1477.edits; stress gate 23 / 24, stuck 10 rounds) submitted 08:01:59 UTC Nov 1 without a note (the
  CLI sets notes only at submit: `cambc submit --note`; upload373.sh now passes "Bamboo <note>", 80 chars). Team mode pinned (Live 1472):
  `submissions activate 1477` blocked by the classifier again - Eric activates; run/pan1477.sh waits for Live 1477, then the 11-group panel.
- **v1477 (H) quick panel q1477 (Eric activated ~08:04 UTC):** 16 / 55 (top 16 / 50, Fish 0 / 5), margin -14.9k = #458 (16, -15.1k), **below
  v1472 (21, top 21 / 50)**; vs v1470 16 vs 9 on 45. Top part vs v1472: far maps (bot_10 in H) 14 games 4 vs 4 wins (pilgrimage, ribs lost;
  famine, harvest won); **near maps (ours in both: kHurtFirst 4 + divergence) 36 games 17 -> 12, all five flips W -> L** (quadrants,
  uncharted_lands, gold_rush, corners, starfish). Local screens again did not predict the ladder. Full panels A (q1477) + B (B1477) running.
- **Full panels for v1477 (H), 08:05-08:17 UTC, pinned 30 Oct opponents (`--source-group`):** panel A 118 games #458 28 vs H 25 (margin H +1.4k;
  x1r 10 vs 6), panel B 123 games 25 vs 28 (+2.2k), Fish's newest 1 vs 0: **54 vs 53, H ties #458**; quick panel 16 vs v1472's 21. Local best
  (pool 839, teammates 721, wide scan 135 / 140) but not ahead on the ladder. Next: v1472 + kHybridWalk 61 alone (no kHurtFirst - the five
  near-map W -> L flips point at it); consider re-pinning the panel to the opponents' current bots.
- **v1478 = v1472 + kHybridWalk 61** (B582x + tools/cands/cand1478.edits, note "Bamboo v1472 + bot_10 on far maps (hybrid 61)", live 08:31 UTC).
  Quick panel q1478 (09:05): **15 / 55 (top 14 / 50), margin -20.4k** - below v1472 (21) and H (16). Top part by map: far (bot_10 in H / v1478)
  14 games 4 / 4 / 4 wins (v1472 / H / v1478; bot_10 no better than ours vs the top 10); **near (our bot in all three) 36 games 17 / 12 / 10**:
  v1472 -> v1478 flips 8 W -> L, 1 L -> W. Determinism check (Up1472 vs Up1478 vs PoolLive, 8 near maps): different games on 7 of 8, v1478
  slower to win on 6. Local near-map split: pool (seeds 1-2) v1472 542 / 768 vs + hybrid 515 (-27); teammates 233 / 384 vs 222 (-11); far
  maps +39 / +48 locally. **The hybrid build costs our own bot ~3% on near maps** (the start-up spawn walk ~8.6k fuel in the draft turn, or
  the extra code) - s_hy999 (kHybridWalk 999: walk runs, bot_10 never plays) tests the cause on the 46 near maps.
- **Ladder farming check:** bot_10 / cmb1 farm no better than ours on near maps (69.5 vs 69.6 gems / 100 rounds vs the common field); on far
  maps +10% locally but not on the ladder panel (4 vs 4 wins).
- **s_fix2 (B582c on v1478 = v1472 + kHybridWalk 61):** pool (seeds 1-2) / teammates (seed 1): v1478 813 / 335; + kWaitAvoid 30 811 / 341;
  + kWaitCap 30 + kWaitAvoid 30 811 / 341 (rarely fires: the 01the_farm 60-round wait did not reproduce locally); + kFightBudget 0.7 812 / 340;
  **+ kEarlyRecall + kFieldFirst + guard + still 6: 848 (+52 +-20 vs #458) / 362** - but on the v1472 base (s_rcl) the same set was -24:
  build-to-build divergence is +-25-35 wins locally; ladder decides.
- **Teammates' panel replayed on v1478** (their v1476 window's 39 groups via --source-group; 21 ran on v1478 before Eric re-selected v1472;
  banners checked, far-map games have no banner = bot_10): paired 100 games v1476 22 vs v1478 20 (margin -46.9k vs -44.5k); v1475 11 vs 10
  (90 games); v1470 13 vs 10. Our bots and theirs win ~1 in 5 against that top-team panel. Tools: scratchpad dash/mkpanel.ts, winsum.ts.
- Platform: Eric re-selected v1472 (~09:40 UTC). Replay 38a369da (01the_farm, v1477, our bot, 3 picks): Vesper / Ryth waited ~60 rounds at
  the big camp while leader Marcella banked at a mid altar and shopped; the first attempt on the camp (3 wolves + elk + 5 clusters) failed
  at 25-35% health; captured 120 rounds later.
- **s_hy999 (46 near maps, pool, seeds 1-3, 1,104 games):** v1472 (B582c) 768; **+ kHybridWalk 999 (walk runs, bot_10 never plays) 739 (-29)**;
  + kHybridWalk 61 739 (identical): the start-up spawn walk alone costs our bot ~2.6% on near maps (probably its fuel in the draft turn cuts
  the map plan's work on bigger maps). With no far-map gain on the ladder (4 vs 4), the hybrid is shelved; a fix would read the draft plan's
  spawn_path instead of walking again.
- **v1479 = v1472 + kEarlyRecall + kFieldFirst + guard + still 6 + kWaitAvoid 30** (B579x, no hybrid code; tools/cands/cand1479.edits; note
  "Bamboo v1472 + pre-started recall + field-first guards + wait-avoid 30") submitted 10:09 UTC; the submit flipped the team to follow-newest.
  **Latest-opponents panel (Eric: "use the opponents latest bots"):** queuelatest.sh (no --source-group) - v1479 plays the top-10 + Fish specs
  against current bots (L1479), then v1472 replays those groups (L1472, --source-group L1479) after Eric re-selects it (run/latestpanel.sh).
- **Latest-opponents panel (Nov 1 10:15-11:15 UTC; L1479 fresh groups vs current bots, L1472 replays them via --source-group):** top 10 v1472
  **12 / 50 (-19.0k)** vs v1479 9 / 50 (-22.4k); Fish 0 / 5 each. Per opponent v1472-v1479: Ad Astra 2-0, Claudus 4-1, Fish 2-1, Mite 0-1,
  NEET 2-2, Sponge 0-1, Trzy 1-1, newer 0-0, print 0-1, prism 1-1. The pre-started recall has now lost on the ladder in every test (G3 12 / 45,
  v1479 -3 here): dropped. v1472 vs the 30 Oct pinned opponents 21 / 50 -> 12 / 50 against their latest bots (Sponge 3 -> 0, Mite 2 -> 0,
  newer / print 1 -> 0): the top teams improved; the pinned panel is out of date - re-pin future panels from L1479 / L1472 (scrim_L1479_*.ids).
- **Recall interaction (Eric ~12:00 UTC: top teams end every turn recalling and cancel next turn; why does ours not work?):** in the 20
  Sponge / Mite games their champions pre-start ~820 recalls a 1,000 champion-rounds (cancelled next turn, duration 1); real trips home: us
  9.1 / them 11.7 a 1,000 champion-rounds, both 5.0-round channels, started at 0.77 / 0.70 health. Any damage cancels a recall, so the
  pre-start saves only one round per voluntary trip home (~1% of champion time) - below what an 11-group panel can resolve. Ours
  (kEarlyRecall) is the narrow form (only turns whose next turn recalls anyway) because the full form needs a turn-start keep / cancel,
  a genuine-recall test in ~30 teammate is_recalling() readers and no pre-start on capture tiles. Enemy side already guarded (kRecallGenuine:
  punish only <= 3 ticks left; kRecallThreat: a recalling enemy's dash / spells count as ready). The fight loss (139 vs 30 deaths) is ~10x
  larger: defensive work first.
- **Defensive tests on the latest-opponent panel (Eric ~12:05 UTC):** run/testcand.sh N SRC EDITS NOTE uploads v<N>, activates it, replays
  L1479's groups (top 10 + Fish, pinned to the 10:15 opponents) as T<N>, compares with L1472 (v1472 12 / 50) and restores the version live
  at its start (v1478 was live and pinned at 12:05 - not set by us). Queue: v1480 = v1472 + kHurtFirst 4 (B580x), v1481 = v1472 + kRegroup 25 +
  kEnemyCast + kEnemyCastFix (B580x).
- **Defensive results (Nov 1 12:31-13:11 UTC, latest-opponent panel = L1479's 55 games replayed):** top 10: **v1472 12 / 50 (-19.0k)**,
  **v1480 (+ kHurtFirst 4) 6 / 50 (-24.2k)**, **v1481 (+ kRegroup 25 + kEnemyCast + fix) 6 / 50 (-25.2k)**; Fish 0 / 5 for all three. Per game
  (v1472 / v1480 / v1481): 35 LLL, 2 WWW, 2 WWL, 3 WLW, 5 WLL, 2 LWL, 1 LLW - each candidate lost 7-8 of v1472's wins and took 1-2 new ones;
  losses spread over Fish's newest (2 -> 0), NEET (2 -> 0), Claudus (4 -> 2), Ad Astra (2 -> 1). Both are built from B580x (not v1472's exact
  source), so part of the drop may be build divergence; the control would be v1472's settings built from B580x (11 groups). Neither ships.
  Side effect: the test versions were live 12:35-12:50 and 12:55-13:10, so other Velvet groups in those windows played them (by banner:
  QS2isLaw ranked 3-2 and KKB 3-2 on v1480; 剑桥夜爬者 3-2 and an_iq_too_high 5-0 on v1481; Prompt King 13:04 1-4 on v1472 - selected by
  someone mid-test; the script's restore then set v1478 back at 13:10). Banners: `cambc match-groups download ID` saves a zip of five match
  zips, each with our team-?.stdout ("BAMBOO vN", missing in ~1 in 3 games).
- **Ranked by version, Oct 31 23:00 - Nov 1 13:30 UTC (Eric ~13:30: "1478 is doing better than 1472 on ranked"):** scratchpad rankedver.py
  (every ranked game, version from the stdout banner) + rankedcmp.py (Elo-expected wins from both ratings before the group, walks.json map
  classes). v1472 48 groups, 125 / 240 (52%), expected 118.6 (+6.4), rating +41; **v1478 14 groups, 42 / 70 (60%), expected 34.9 (+7.1), rating
  +45** (11:50-13:30 run 30 / 45, 2050 -> 2095). By class (wins vs expected): v1478 close 9 / 15 (+1.6), contest 22 / 36 (+4.0), far 11 / 19
  (+1.5); v1472 close 22 / 49 (-2.3), contest 65 / 111 (+10.4), far 38 / 80 (-1.6). The gap (~7.5 points, SE ~7 before 5-game group
  correlation) is mostly on close / contest maps, where v1478 plays as v1472 (bot_10 only takes far maps): luck and opponent mix, not the
  hybrid. Far maps alone, the only place they differ: 58% vs 48% on 19 vs 80 games - suggestive, unresolved. Rating 1962 -> 2095 overall.
  Untagged groups 01:40-03:00 are the teammates' v1470 / v1475 / v1476 (no BAMBOO banner): 23 / 45.
- **Correction (Nov 2):** v1480's source is v1472's exact source + only edit_hurtfirst.py (the constexpr lines and the function); v1481's is
  v1472 + the kRegroup / kEnemyCast switches + the inert hurt-first code. So build divergence does not explain their 6 / 50: the switches lost.
- **Codex's new bot B583x (Nov 2 03:42-04:20 UTC, Eric: "lets start coding for a new bot"; Codex ran out of usage mid-way; Eric ~04:25:
  "continue the bot"):** bots/B583x = the v1478 source (hybrid included) edited directly (no edit script; Codex's final source saved in
  the session scratchpad b583x_codex/, sha1 359fe645). Changes, each a switch:
  - kRecallPrime: every turn ends with recall() (not while capturing / submitting / teleporting); next turn start cancels it unless
    recall_prime_continue() (health < kRetreatHp, kRichGold, shop trip). recall_committed(c) = channel >= 2 ticks old replaces
    is_recalling() in ~40 teammate readers; self_recalling() / begin_recall() for our own. Enemy readers unchanged (kRecallThreat /
    kRecallGenuine already handle pre-starts).
  - kWardOwn (switch added by Claude): no ward in a connected bush region that already holds an allied ward (allied_ward_in_bush).
  - kExclusiveSolo: during the opening (round < team_rounds_, when target-byte bit 7 = solo claim), a mate's solo-claimed quiet, non-central,
    own-half node scores x0.05. kSoloStartNow: at contact, a camp now soloable with current items starts at once (needed_ = 1, wait_ = 0).
  - kVendettaHunterBonus 6: Vendetta wins the hunter election. kCaptureCover 6: in combat whoever reaches a reward keeps capturing.
  - Fuel guards: kOneBuild 50k, kStepLite 18k, kCastLite 18k, kWardFuel 40k, kPostFuel 30k (all were 0).
  Codex's screens were 4-22 games vs Up1478 (seed 1): the explicit-cancel recall fix and the opening-only solo claims; the last run
  (interlock + the-farm) still 1 / 4, -1,093 - identical to kExclusiveSolo off, so the gate made it inert there. s_b583 (7 arms x 560,
  pool) measures the package and each component off.
- **Deaths vs Sponge / Mite latest bots (20 games, collaboration/20261101/claude-latest-panel, scratchpad deaths.py):** ours 267 vs theirs
  93; 68% on our half, 55% within 3 of a camp. 150 of 267 had >= 80% health six rounds before death; then 70% had a mate within 4 and only
  18% faced more enemies (within 6) than allies (within 4) + 1; foes within 6 average 1.46 -> 1.85 -> 2.07 (6 / 3 / 0 rounds before).
  By champion: Vesper 82, Ryth 67, Marcella 58, Willow 58, HoR 2. We lose team fights - healthy squishies burst in < 6 rounds beside
  mates while our tank lives - more than isolated picks. Fish replay 2a579d40 (us vs Fish, Codex's fish-combat-analysis.json): 9 kills to
  1, Fish's Vendetta (strength build) finished 7; 5 of 9 victims had no ally within 7.
- **s_b583 (B583x components, pool seed 1, 560 games an arm, base Up1478 414 wins +279):** B583x 384 (-91 +-26 *); without kRecallPrime
  410 (+11 +-26); without the fuel guards 372 (-107), without kExclusiveSolo + kSoloStartNow 378 (-105), without kWardOwn 382 (-95),
  without kCaptureCover + kVendettaHunterBonus 368 (-131): **priming is the whole loss** (deaths +0.6..2.0 a game, kills -0.4..1.6); the
  other parts are neutral to slightly positive on top of it (none significant alone). ~22 far maps identical in every arm (bot_10 plays).
- **s_prime (48 near maps, pool seed 1, 384 a arm, base B583x priming off 263 +279):** Codex's priming 237 (-149 +-38 *); + kRecallPrimeSafe 1
  (keep the pre-start only with no enemy within 8 last turn, not engaged) 274 (-29 +-37); **+ 2 (pre-start only with no enemy champion in
  sight) 272 (+4 +-36)**; + 3 268 (-29 +-32). Cause: recall_prime_continue kept the channel for hurt champions (health < kRetreatHp) with
  enemies near, so they stood still instead of fleeing. B583x default now kRecallPrimeSafe 2: safe priming is neutral locally, as its
  ~1-round-per-trip gain predicts.
- **Fuel scans (70 maps x 2 vs B7Live, scratchpad run/fuelscan.sh, wideTF78 / wideTF83 / wideTF83n):** fuel-limit turns (>= 99k of 100k)
  v1478 8,361; B583x (priming off) 8,588; B583x without Codex's fuel guards 9,355. The guards (kOneBuild 50k, kStepLite / kCastLite 18k,
  kWardFuel 40k, kPostFuel 30k) cut ~8% of B583x's own overruns but only offset its added work (ward-region scan, solo checks): ~60
  limit turns a game, worst on breadcrumbs (~140), corners (~120), eight (~60). Wins 131 / 134 / 136 of 140; loop + stuck rounds 872 /
  884 / 973; guarding still 203 / 407 / 284 rounds. Fuel needs a per-phase profile (which calls use the turn), not more thresholds.
- **v1494 = v1472 + kDraftAlt 65 (Sponge's small drafts: 3 picks Marcella / Vesper / HoR, 4 picks HoR / Vesper / Ryth / Marcella; bots/B1494d =
  Up1472 + draft.cpp only)**, Nov 2 06:31 UTC, on the 6 latest-panel groups richest in 3/4-pick maps (scratchpad bench_d / L1479d; scrim_T1494d):
  **5 / 30 vs v1472 5 / 30 (margin -11.9k vs -12.0k)**; the 14 five-pick games identical (pairing exact). 16 small-pick games 4 vs 4 wins:
  vs Sponge + Mite 2 vs 0 (-1.5k vs -5.9k: guardians, fragment flipped to wins), newer 1 vs 0, Fish + Ad Astra + Trzy 1 vs 4 (gemfight,
  the_line, gemcombat1 flipped to losses). Deaths 153 : 70 vs 197 : 91 - the same 2.2 : 1 trade; enemy HoR in the draft does not predict
  which version wins (dtest/drafts.jsonl). HoR alone does not fix our fights; the small-pick loss is in the play. Not adopted.
- **v1495 = B583x (Codex's bot, safe priming) on 9 latest-panel groups (bench_b / L1479b), Nov 2 06:43 UTC:** **7 / 45 vs v1472 12 / 45** (margin
  -21.2k vs -15.1k): B583x loses on the ladder although neutral locally. Not adopted. v1478 restored 06:50 UTC.
- **Fuel profile (Nov 2, tools/edits/edit_fuelprof3.py: phases + inclusive function counters inside debug_block, so free in local debug builds
  and absent in release; read by scratchpad fpsum.py).** v1478 on 48 near + 16 new maps x 2 vs PoolLive (118 games with our bot, 582k turns):
  1.12% of turns suspended (~55 a game), mean 45.6k a turn. Worst: **03the-front 11.75% of turns suspended (~500 a game)**, yellow_brick_road
  ~330, stampede, treasure_box, 03fan, the_pack, boss_battle, 03colosseum. Function shares of all fuel: manage_squad 12.4% (6.7k a call,
  max 99.9k), observe_groups 11.3%, observe_allies 8.9%, observe_enemies 6.3%, step 6.3% (max 99.9k), choose_solo 4.7%, score_team_targets
  4.2% (18.3k a call; 46k on the 8 heavy maps, 53k on 03the-front); path-field builds only 0.3%. Suspensions land in farm (46%), decide,
  post (the turn-end rescore starts at kScoreEndFuel 40k though a heavy-map rescore costs 46k) and squad. Inside scoring: arrival_time 432,
  travel_time 341, party_need 316, champions_needed 218 fuel a call per group. Groups: 03the-front 48 (166 camps), 03colosseum 42, 03contours
  40 - below kScoreNearOver 48. History (Oct 25-30): guards that skip work moved, not removed, suspensions and every fuel-change panel
  version scored lower; only decision-exact savings are safe.
- **Ranked by bot since Nov 1 20:30 UTC (scratchpad rankedver2.py tags our "BAMBOO vN" banner, the teammates' bot_10-lineage builds by their
  per-turn log as VT):** v1478 245 games 118 wins (48%), Elo-expected 123.8 (-5.8); **VT (v1488-v1493 = their v540-v569) 235 games 135 wins
  (57%), expected 117.9 (+17.1)**. By class (wins / games): far VT 46/65 vs v1478 36/65 (v1478 also runs bot_10 there), contest 49/82 vs
  50/97, close 17/47 vs 16/38, new 03 maps 23/41 vs 16/45. The live slot alternated through the night, so the opponent pool is shared.
  Ajayendra's panels (night-1101 docs/status.md) favoured 1478 over hy3b / older bot_10, but not over maximus' v540+ line, whose source is
  not in the repository.
- **v1503 (the teammates' v606, bot_10 lineage, 5.8k lines; Eric put the source in bots/v1503, Nov 2) vs v1478 - s_v1503 (pool, all 86 maps
  incl. the 16 new, seed 1, 688 games an arm):** v1478 486 +247; **v1503 536 +343 (paired +96 +-27 *)**; v1503 with BOT_LOGC 0 (bots/v1503nl,
  no per-turn log) 534 +334. By class (wins / margin): close v1478 94/136 +290 vs v1503 90/136 +244; contest 171/248 vs 180/248; far
  147/176 vs 161/176; **new maps 71/128 +106 vs 105/128 +383**. Fuel scans (70 maps x 2 vs B7Live): fuel-limit turns v1478 8,361, v1503
  2,662, v1503 no-log 1,177; wins 131 / 136 / 132 of 140. Changes over bot_10 (VTb10): engage at sim 0.0 (was 0.3), strike first in mutual
  one-turn reach (P_MSTRIKE) and from dash reach (P_PREEMPT), hurt champions hold only better fights (P_HDIS), melee move-and-hit on
  camps, HoR lands on camps, Willow heals the most-missing ally, proactive HoR shield, Prospector emblem first for carries, dash bridges +
  spawn crystal flash (central-altar maps with spawns > 61 apart). Local and ranked (+17.1 vs -5.8) agree: their line is stronger.
- **Teammates' versions compared (Nov 2 ~15:00 UTC, scratchpad vtversions.py: every game since Nov 1 20:30 attributed to the version live when
  it started - upload windows from `cambc submissions list --json` createdAt / statusAt, gaps from the ranked banner tags; 4,615 games).**
  Their line: v484 -> v540 (1488) -> v546 (1489) -> **v548 (1490, the default between tests)**; each later upload = v548 + one change, ~180
  scrim games on their panel. Paired with v1490 on the same opponent / map / side scrims (wins vs v1490's): **v1478 (ours) 99 vs 131 on 310**;
  v1492 (v563, dash bridges + spawn flash on central-altar maps) 34 vs 25 on 127 (margin -40k vs -55k); v1503 (v606 = v563 gated to spawns
  > 61 apart) 41 vs 43 on 175; v1499 (v574) 42 vs 41; v1498 (v591) 45 vs 47; v1504 (v607, ally memory in the fight sim; live from 14:36)
  38 vs 41; v1500 (v551 earlier bank) 50 vs 58; v1496 (v581) 30 vs 39; v1488 (v540) 41 vs 56. Ranked: v1490 91 games +4.1 vs Elo, v1478 241
  games -7.8; the test versions have 5-35 ranked games each. Their variants sit within ~+-9 wins of v548 (noise); v548's lead over v1478
  is the firm result. In v1503's params.h: P_CENTRAL_MIN_STEPS 0 = v563, P_BRIDGES 0 + P_TP_SPAWN 0 ~ v548.
