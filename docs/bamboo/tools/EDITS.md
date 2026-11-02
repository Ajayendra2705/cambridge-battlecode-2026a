# Source edit scripts (October 21, 2026)

Each `edit_<name>.py SRCDIR` rewrites `SRCDIR/bot.cpp` (some also `draft.cpp`) with exact-text substitutions and asserts
every anchor matches once, so a script that no longer applies fails loudly instead of silently editing the wrong place.
They were written against the v197/v200 code (`bots/B7Live/src`) and the review-bundle code (`bots/Bamboo7/src` at
commit 9153cdc); `bots/V201/src` = `B7Live/src` + aggro, aggro2, aggro3, wakeguard, bait2, nextonce with the switches
set (see `.info/knowledge/bot-status.md`).

| Script | Adds |
|---|---|
| `edit_review21.py` (`--only F1..F8 SMALL`) | the 2026-10-21 review fixes |
| `edit_blindcap.py`, `edit_waitfix.py`, `edit_walkgroup.py`, `edit_walkgroup2.py`, `edit_fuelcamp.py`, `edit_escapecache.py` | the 01yellow_brick_road fixes and the big-group fuel work |
| `edit_metafarm.py`, `edit_fuelhi.py`, `edit_waitdbg.py`, `edit_pickdbg.py` | experiment and diagnosis switches (pickdbg: GROUP/CHAMP dumps for `tools/stress/pickscan.py`) |
| `edit_aggro.py`, `edit_aggro2.py`, `edit_aggro3.py` | `kAggroExit` (+ `kAggroFlee`, `kAggroHit`, `kAggroExitStr`) |
| `edit_frontneed.py` | `kFrontNeed`, `kFrontLine` |
| `edit_prism.py` | `kPrismCarry`, `kPrismBag`, draft `kPrismFarm` |
| `edit_nextonce.py` | `kNextOnce` |
| `edit_wakeguard.py`, `edit_bait2.py` | `kWakeGuardStr`, `kBaitGuard` |
| `edit_threepick.py` | draft `kThreePick`, `kThreePickClumps` (three-pick maps: Heart of Ruin + Ryth + a third; v203 sets 1) |
| `edit_altarbait.py` | `kAltarBait` (needs `edit_wakeguard.py` first) |
| `edit_makeway.py` | `kMakeWay`, `kMakeWayHp` |
| `edit_farside.py` | `kFarSideAll` (the round-100 enemy-half ban on every map) |
| `edit_carry.py` | `kCarry` (designated carry; anchors on the v200 `carrier_` line, so apply it before `edit_prism.py` or not at all on Bamboo7) |
| `edit_report.py` | `kReportRound` (REPORT line for `fastscreen.py`'s cut-off mode) |
| `edit_powerbuild.py` | `kMetaBuild` 3–6 (Power-stacking builds of the top teams; all lose locally) |
| `edit_campaware.py`, `edit_rootwalk.py`, `edit_waitsafe.py` | the pathing set: `kCampAware`, `kRootWalk`, `kWaitSafe` |
| `edit_midall.py` | `kMidAvoidAll` (no midline camp before that round on every map) |
| `edit_autoteam.py` | `kAutoTeamPacks` |
| draft `edit_prismswap.py` | `kPrismSwap` (someone else in Prism's slot; 5 = Heart of Ruin) |
| `edit_waitfix_dir.py`, `edit_walkgroup.py`, `edit_walkgroup2.py`, `edit_blindcap.py` | the review line's 01yellow_brick_road fixes, ported to the v200 line (not switch-gated except `kCaptureBlind`) |
| `edit_rowscan.py` | `kRowScan`: on a group's own tiles with none of it in sight, walk to its nearest unseen spawn tile (the yellow_brick_road row freeze; on in v226/v227) |
| `edit_delivercommit.py` | `kDeliverCommit`: a retreat heading for a near altar keeps retreating (rejected: -27 +-14, boss_battle; B7Dev line only - its anchor needs `kAltarBait`) |
| `edit_bankusable.py` | `kBankUsable`: retreat's altar shortcut and deliver() need an altar that can take a tribute now (boss_battle: Ryth stood beside the live boss with 964 gems, "retreat", from r1727 to the end) |
| `edit_shophold.py` | `kShopHold` N: a shopping retreat keeps going N rounds once started, off the spawn (the boss_battle travel <-> retreat loop at the kNearShop boundary) |
| `edit_pokenodash.py` | `kPokeNoDash`: `cast_offensive(target, champion, allow_dash)`; the outnumbered poke never dashes in (review 2026-10-22 #1) |
| `edit_dashdamage.py` | `kDashDamage`: a hitting dash counts as damage, reach range + radius (review #2) |
| `edit_waveshared.py` | `kWaveShared`: followers treat the squad's impossible shared target as a wave; `wave_pick_` reset (review #3) |
| `edit_memberblock.py` | `kMemberBlock`: camp tiles block per living member; the camp epoch hashes the occupied tiles (review #4) |
| `edit_finishbag.py` | `kFinishBag`: our bag counts towards the finish-window gate (review #5) |
| `edit_pickdirty.py` | `kPickDirty`: an invalidated squad pick keeps its timestamp for the low-fuel guard (review #6) |
| `edit_planwalks.py`, `edit_allocguard.py`, `edit_rowscan_dead.py` | no switch: draft-plan walk flag only on success; allocator wrap guard; the row scan skips members seen dead |
| draft `edit_meta4.py` | `kMetaDraft` 4: HoR, Vesper, Ryth, Marcella, Vendetta (the Oct 21 meta; Eric; live as v229) |
| `edit_deadroot.py` | `kDeadRoot`: approach roots skip members seen dead (Vesper "arrived" 3 from a dead cluster, 4 from the living ones: big_world 848 rounds); `kDeadRootErase` 0/1/2: also drop the approach field when a member dies - 1 any watched group (−120 ± 55), 2 our target's only (−86 ± 48: the roots shift mid-fight); roots-only (0) +10 ± 22, on in v232; `kFightStall` N: N still turns fighting one camp with nothing landing → avoid it (12 in v231) |
| `edit_shootreach.py` | `kShootReach`: a shootable camp (kWalkTargets) needs a firing tile a walk from our spawn reaches, seeing a member not seen dead; recomputed when the living count changes (review #7; +9 ± 6; on in v232) |
| `edit_revealfix.py` | `kRevealFix`: a reveal step that cannot move (a wall, not a bush, between us and a camp in range; its tiles unwalkable) steps greedily, else avoids the camp (fracture: Vesper 3 from a wolf behind a wall column, 676 rounds; on in v231) |
| `edit_altarboss.py` | `kAltarBoss`: every altar's tribute tiles on camp spawn tiles → those groups are boss groups (map-general); `kAltarBossBudget`; `kWindowBank`: on such a map bank any bag the moment an altar opens. Both measured no better on boss_battle (the window is shared and short); off |
| `edit_wallonly.py` | `kWallStep` 2: the engine path only when a wall crosses the line - loop rounds 36 → 448 on wall maps; off |
| `edit_dashtie.py` | `kDashTie`: travel-dash landings tied on path distance go to the one nearest the goal (Eric: HoR dashes sideways; +20 ± 37, on in v239) |
| `edit_wallcommit.py` | `kWallStep` 3 + `kWallCommit`: the engine's path kept for N turns toward the same goal when a wall crosses the line - wall-map loop rounds 38 → 926: the engine's own path step bounces; off |
| `edit_proclessbuild.py` | `kMetaBuild` 7: procless's 1.0.2 order - Treasure (Health on HoR and the melees, Strength on Vesper), Jungle, Durability Health, the main stat (Eric: their health-oriented build). Pool −23 ± 47, **ladder bench −4,910** (v242): off |
| `edit_vespersolo.py` | `kVesperSolo` N / `kVesperSoloWealth` / `kVesperGold`: Vesper farms alone (gold-weighted) before round N while poorer than the wealth line (Eric: early solo gold before she joins fights). −41 / −41 / −64 in three forms: off |
| `edit_marcellacarry.py` | `kMarcellaCarry`: Marcella takes whole rewards like a carrier - her passive pays 2 gold per gem tributed (Eric). +51 ± 38, bench −12,996 (best of the session): **on since v240** |
| `edit_recallcaphp.py` | `kRecallCapHp`: no recall-capture at this share of health or more with no emblem to buy and no bank due (Eric: no recalls straight after a capture when healthy). Pool neutral (0.75 −2, 0.8 −5); benched alone as v248 |
| `edit_bully.py` | `kBullyOdds` / `kBullyRange` / `kBullyWealth` / `kBullyCaptureOnly`: an enemy contesting our target camp is run off when our odds and wealth are clearly better (Eric: a strong Marcella picks those fights). −43 / −40 / −90 (capture-only): **off** - the fight costs more farming than the camp |
| `edit_joinfight.py` + `edit_joinfight_idle.py` | `kJoinFight`: waiting beside, or idling near, a camp a mate is fighting right now (a member lost health within 2 rounds): join it (Eric: champions standing around while a mate fights alone). Pool +36 ± 31, bench a wash (swirl coin-flip aside ~+500): **on since v245/v247** |
| `edit_fightcap.py` | `kFightCap` / `kFightCapAvoid`: an objective-less fight (enemy within 5, no camp engaged or captured) is left after N rounds and the camps around avoided (Eric: stalled in fights while the enemy farms). Pool +58 ± 28 at 60, **bench −2,475** (v246): off |
| `edit_rangedsolo.py` | `kRangedSoloBias`: a ranged champion solos only when its camp scores this much above the squad's pick (corridors: Vesper soloing far camps on both sides of the map, 43% of turns travelling) |
| `edit_lowsnipe.py` | `kLowSnipe` / `kLowSnipeFloor`: a melee champion under the retreat line beside a camp a mate is fighting (no enemy about, the mate not low) snipes it from outside its attackers' reach with a damage ability that out-reaches them (Marcella, Ren vs wolves), holding outside the reach while it recharges (Eric: snipe instead of backing straight away) |
| `edit_vespercarry.py` | `kVesperCarry` / `kCarryGemK` / `kVesperGoldW`: rewards go whole to the champion whose passive fits them - gold-dominant groups (gold >= K × gems) to Vesper Vale (+33% gold), gem-dominant ones to Prism (Focus per carried gem) - when that champion is near; 1 under the team-mode carrier gate, 2 in any squad; `kVesperGoldW` weights gold in Vesper's camp scores (prism best girl: one champion on the tiles at 97% of captures, Vesper 35% of gold rewards, Prism 61% of gem rewards; our Vesper 8%). Two seeds paired: 1 −19, 2 +10, **2 + gold weight 1.33 +33 ± 34 (217/280 vs 211/280)** → v252 (bench 10/40 −14,031, best of the series; shares 25% of captures). Others leaving the tiles outright for her: −208 ± 32 (rewards unclaimed: she only captures her own target). 3 (others step off when she is beside the tiles on the same camp) + weight +38 ± 32 but still 25% shared (HoR recall-capturing while she steps on); she waits beside occupied tiles −0/+8 (sharing 9%, her gold back to 8%); 4 (she leaves channelling mates their reward) +5 (sharing 10%); 5 (no recall-capture beside her) −6 (14%); the weight alone −23 ± 17. **v252 kept as is** |
| `edit_meta5.py` | draft.cpp `kMetaDraft` 5 = prism best girl's lists (Prism, Vesper, Marcella, Ryth, HoR; three picks Prism, Vesper, HoR; 90/108 and 14/17 won on Oct 22), 6 = meta4 with Prism in Vendetta's place. Seed 1: 5 −9 ± 45, 6 −18 ± 32, 5 with kVesperCarry 2 −43 ± 42 (off) |
| `edit_nearinvade.py` | `kNearInvade` / `kNearInvadeQuiet` / `kNearInvadeControl`: an enemy-side camp within N walking steps of the midline scores as ours (no `kFarSide` factor, no `kFarSideEarly` ban) while no enemy was seen within 8 of it for Q rounds (Eric: camps a little on their side go untouched; procless took 191 of them to our 19). Two seeds: 6/Q20 −63 ± 27, 10 −60, 6/Q60 −44; control maps off −27 ± 22 → v253: bench 5/40 −18,257 vs v252 −14,031, **rejected**. `kNearInvadeMode` 1 (only while `kInvadeDead` enemies are confirmed dead with `kInvadeWindow` rounds of respawn left; Eric's experiment 4): 6 steps +35 ± 23 (with held crystals, two seeds), 14 steps +9; **four seeds on v258: mode 1 −2 ± 16, mode 2 (respawn covers walk + clear + 10, quiet 20) −23 / −26**: rejected |
| `edit_aclog.py` | logging build: one `AC` line per champion per turn with activity, position, target, health and bag (read with tools/stress actprof/travelprof/switchwhy); never upload |
| `edit_diag.py` | `kDiag` (logging builds): MX lines (the trade decision next to a 4-turn matchup estimate and enemy emblems from item_count) and IV lines (best home vs best enemy-side camp by full cycle with enemy info); read with tools/stress/diagjoin.ts. No behaviour change |
| `edit_matchup.py` | `kMatchupGate` / `kMatchupLog`: the matchup predictor in the bot (mirror of tools/stress/matchup.ts; parity 100% via matchparity.ts) and fight decisions using it: 9 compute only (fuel control), 4 withhold the trade on a predicted loss and carry on (no movement override). Rewritten after the 2026-10-22 audit: the first version (modes 1-3: pooled damage, summed spells at the longest reach, walk-home on decline) benched −54/−62/−59 locally and is gone. Four seeds, 40 maps: eager compute-only (9) −34 ± 18 (fuel: suspensions +39%), eager withhold (4) −40 (vs 9: −6 ± 11); lazy (computed only at the trade) compute-only (8) −8 ± 8, withhold (5) −17 (vs 8: −9 ± 15). Off |
| `edit_fuelphase.py` | `kFuelPhase` (logging builds): fuel checkpoints between play_turn's phases; a suspension (fuel_remaining jumps up: the engine resumed the turn next round) prints the phase and activity. v255 vs B7Live, 70 games: 1.2% of champion-turns suspended, 90% in the decide/act phase |
| `edit_fuelprobe.py` | (after edit_fuelphase.py) scoped probes on ~75 member functions: each suspension is reported by the innermost probed function it happened in. Top sites: step's own body, score_team_targets, fight_group, nearest_enemy, team_finishing + team_total, try_dash, ally_jam, safe_field |
| `edit_campsnap.py` | `kCampSnap`: fight_group reads each living monster's position, strength and health once and counts crowds once; same target choice and aim (fuel only) |
| `edit_fuelcache.py` | `kFuelCache`: enemy distances from this turn's cached positions, finishing() once a round, no dash scan without a dash (fuel only); pair with `kTeamTotalOnce` true. With kCampSnap: suspensions 4,571 → 3,535 in 70 games (−23%); two seeds +8 ± 26 → v256 |
| `edit_nextcache.py` | `kNextCache`: the next camp chosen once per capture (1 leader's publication, 2 also recall_capture's pick, 3 recall_capture uses the leader's). Two seeds on top of the caches: −8 / −14 / −9 (off) |
| `edit_capowner.py` | `kCapOwner` / `kCapOwnerNear`: one capturer per cleared camp chosen before anyone steps on (Vesper for gold, Prism for gems, then carriers, then nearest); non-owners move on only while the owner is beside the tiles; 2 also steps a non-owner off a shared tile (farming review #1). Two seeds on the fuel caches: 1 −2 ± 28, 2 −11 ± 30, near 5 −2; with respawn events −21 (off) |
| `edit_partyttk.py` | `kPartyTtk`: team camp scores use the squad's own summed damage (my dps + the strongest mates' slot_dps, kit factors) for clear time (farming review #2). Two seeds on the caches: −31 ± 29 (off) |
| `edit_respawnevent.py` | `kRespawnEvent` / `kEventSlot`: a fresh capture one champion sees is written to the spare target-slot byte (five champions or fewer, < 127 groups; toggle bit for repeats); the others mark that camp respawning (review: compact capture events in shared memory). Two seeds on the caches: +1 over the caches (wins 223 vs 212/280) |
| `edit_teleheld.py` | `kTeleportHeld` / `kTeleportExtra` / `kTeleportRebuy`: use a crystal already held when a landing saves N net rounds (channel turns + extra; the engine's exact extra is 0), purchases unchanged, never during a planned jump, not while hit or with an enemy in sight; `kTeleportRebuy` false stops the planner's rule rebuying a crystal spent this way (Eric's crystal plan, experiment 1). Two seeds: 5 +18 ± 11 / +16 ± 10, exact timing +16, 3 +6, 8 +11. **Four seeds: 5 with rebuy +23 ± 7, without +14 ± 8** → v258 (rebuy) |
| `edit_release.py` | `kRelease` / `kReleaseSolo` / `kReleaseKeep`: the highest-slot surplus member leaves a camp the others finish within N rounds safely, for a camp it can take alone (experiment 2). Keep 2: 9 releases in 28 games, +7..+9 (≈ −10 vs held crystals); keep 1: −22 ± 19 (off) |
| `edit_arrive.py` | `kArriveSteps`: fight-start odds count only allies who can reach us within N steps with no wall on the line (experiment 3). 2 −12 ± 29, 4 +6 ± 26 (off) |
| `edit_autoteamstr.py` | `kAutoTeamStr` / `kAutoTeamStrScale`: the team-or-solo opening classes camps by `champions_needed` against a roster-average champion at `kAutoTeamStrScale` × its damage (the same answer on every teammate), not by monster count (Eric: strength-based splitting). ×3 +24 ± 25, bench a tie with corridors +749/+646: **on since v241** |
| `edit_dashwake.py` | `kDashWakeStr` / `kDashWakeHp` / `kDashWakePaths` / `kDashWakeTravelStr` (the travel dashes' own strength line: 60 = elks and up, −5 ± 33 with fracture +244, elk-arena +258; 1 = any attacker −29): a dash landing is checked for the camp groups it would newly wake and their attackers in reach (Eric's design). Offensive-only at strength 100 (`kDashWakePaths 1`) +13 ± 7; the travel path costs fuel (−71) and the escape comparison ignores champion damage - keep both off |
| `edit_bush.py`, `edit_dashgap.py`, `edit_micro.py`, `edit_microfuel.py`, `edit_rules.py`, `edit_sight*.py`, `edit_sprint.py` | earlier sessions' experiments (October 19–20); their anchors may no longer match |

Order for a full rebuild of the live line from `bots/B7Live/src` (= v200): aggro, aggro2, aggro3, wakeguard, bait2,
nextonce, threepick, altarbait, makeway, carry, farside (`bots/B7Dev`); v203 = that + `kThreePick = 1` +
`kPartyArrival = true`.

**October 21 afternoon.** `bots/B7Dev` = the line above + hornext, truewake, gapescape, gapauto, fishdraft, report,
powerbuild, campaware, rootwalk, waitsafe, midall, autoteam, prismswap (every switch off). Screen settings used since:

```
V4   = s/kThreePick = 0;/kThreePick = 1;/@@s/kPartyArrival = false;/kPartyArrival = true;/@@s/kTreasureBuild = 1;/kTreasureBuild = 2;/
       @@s/kAutoTeam = true;/kAutoTeam = false;/@@s/kSquadSize = 2;/kSquadSize = 1;/@@s/kTrueWake = false;/kTrueWake = true;/
       @@s/kRangedHome = false;/kRangedHome = true;/            (v204's settings + kRangedHome; one line, no breaks)
P    = V4 @@ s/kCampAware = false;/kCampAware = true;/ @@ s/kRootWalk = 0;/kRootWalk = 2;/ @@ s/kWaitSafe = false;/kWaitSafe = true;/
D1   = P @@ s/kSquadSize = 1;/kSquadSize = 3;/ @@ s/kMidAvoidAll = 0;/kMidAvoidAll = 100;/ @@ s/kVargSwap = 0;/kVargSwap = 5;/
```

`bots/Cand206` (tracked) = `B7Dev` + `edit_waitfix_dir.py` + `edit_blindcap.py` with D1 and `kCaptureBlind = 0` written
into the source: the next upload candidate (see `.info/knowledge/bot-status.md`, "Local screens of October 21 afternoon").

**v227** (Oct 21 22:00, `bots/Up227`) = `bots/Up224/src` (v205's code, diagnostics off) + `edit_rowscan.py` (switch set to
true) + `edit_waitfix_dir.py`, `kBotVersion` 227. v225's B7Dev-based switch set went 4/20 in ranked games against v224's
18/30, so the v205 line is the base again.

**The v205 dev line: `bots/Dev227`** (untracked) = `bots/Up227/src` + rowscan_dead, planwalks, allocguard, bankusable,
pokenodash, dashdamage, waveshared, finishbag, shophold, pickdirty, memberblock, meta4 (every switch off). `bots/Dev227m`
= the same with `kMetaDraft = 4`. The review of 2026-10-22 (`.info/Reviews/Review-2026-10-22-4683c2e.md`) is answered
switch by switch in `.info/knowledge/bot-status.md`.
