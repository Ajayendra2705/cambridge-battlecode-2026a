# Live bot overview: platform #371 (Oct 26 2026, engine 2.0.0)

Source: `bots/Up371/src` (= `bots/B375x` + scratchpad `run/cand371.edits`; edit chain in `tools/cands/`, `tools/edits/`).
`bot.cpp` 15.3k lines + `draft.cpp`. 848 constants: 436 feature switches (203 on, 233 off) and 412 tuning parameters.
Each switch's comment holds its history and measurements; lists generated from the live source (scratchpad `live371/on.txt`,
`off.txt`).

## Draft (draft.cpp, by pick count)
- 3 picks or fewer: Marcella, Vesper, Ryth (kSmallMarc). 4 picks: Marcella, Vesper, Ryth, Willow (kFourPick 2).
  5 picks: Heart of Ruin, Vesper, Ryth, Marcella, Willow (kMetaDraft 4 -> kWillowMeta 1). Taken picks fall through the list.
- The first draft turn (100x fuel) also computes the static map plan (walks from both spawns, neighbour values) into draft
  memory for every champion's set-up (kDraftPlan).

## Set-up / map reading (every champion, from the layout)
- Control map: spawns at most 45 path steps apart (kControlDist): squads whenever enemies are about, no enemy-side camps before
  r100 (kFarSideEarly), midline avoidance before the control check (kMidAvoidDiff 6, kMidAvoidSetup), hub altar bonus and idle
  spot (kHubBonus 1.0, kHubIdle, kHubAvoid after a death there).
- Opening as one squad where the camps near spawn need several champions (kAutoTeam + kAutoTeamStr; kOpeningRounds 120).
- Boss maps (gems in huge camps): kBossMode, kBossBudget 1.5, kBossCommit 31, kBossCall 40.
- Path facts: walking-only targets (kWalkTargets, kSquadWalkable), dash gates over 1-tile gaps (kDashGate), walled altars
  (kWalledAltar 1), crossfire across holes (kCrystal planner only on race maps: kCrystal 40, kCrystalRaceOnly), sight-checked
  firing tiles (kSightRoots, kShootReach).
- Map categories (kMapCat) exist in B376x only, off: the 16-game screen found no per-category gain for numeric weights.

## Turn priority (first that acts wins; bot.cpp turn loop)
1. escape: burst guard (enemy next-turn damage >= health, from r600), group burst, caster burst range, focus loss 25%.
2. stand_shot (ranged keep shooting while the incoming burst < health; kStandShot 1.0, also instead of the outnumbered walk home).
3. evade: our odds < 0.85 within 6 (x0.7 when ahead, + bag caution 2.0 per 100 gems), only enemies that can reach us.
4. kite: ranged step away from melee within 2 (kKiteMelee), spell spacing; poke_step out of unreachable pokers.
5. fight_enemies: trade when odds >= 1.0 (kEngageOdds; kBurstOdds 3 spell model, kCasterThreat, enemy reset parity), assist a
   fight within 6 next to an ally (kAssist), spells at the weakest in range (kSpellReach, also when outnumbered), Heart of
   Ruin's dash as an attack (kRuinKit), move-then-attack resets (kMoveReset 2), save spells when enemies are within 8.
6. hunt (kHunter 5): matchup chase plus prey rules - enemies at <= 50% health (kWoundedPrey), carriers of 20+ gems
   (kCarrierPrey), recalling enemies near us (kRecallPunish 6), also on their half (kPreyFar); once they bank 600 and lead,
   the whole team near a carrier hunts it (kDenyAt 600). Election skips busy allies (kHuntElect).
7. heal on spawn to 95%; low melee snipes a mate's camp (kLowSnipe).
8. retreat: 35% health (50% with 20+ gems; 50% late in tiebreak games), shopping at < 60% with gold, 150 gold between camps
   (kShopTripGold), finish-camp exception, bag recall (100 gems), safe/reach-aware retreat.
9. deliver: bank at 40 gems (kDeliverGems) at a usable, safe altar (kBankUsable, kAltarUsable, kChannelSafe 6, kChannelOdds
   1.5, kChannelWatch cancels a tribute that would get us killed); finish logic once banked + bags reach 1000 (no shopping,
   carriers bank, others guard: kFinishNoShop, kFinishDeliver, kFinishBank, kFinishGuard, kFinishBudget 0.95).
10. tribute guard (a mate tributing 50+ gems), contest an altar only when it pays (kContestPay 1, kContestBackoff 15, wards).
11. farm(): pick a camp and take it (below). Every turn after: Willow casts her heal (kWillowHeal).

## Farming
- Camp score = gems + gold x gold weight (0.3 at r0 fading to 0.12; Vesper weighs gold x1.33), per champion needed
  (kPerChampionPick), travel with safe routes around the enemy side (kSafeRoute 8) and around awake camps' reach
  (kAvoidReach), respawn timing shared (kRespawnEvent), claimed rewards skipped.
- Mostly solo farming (kAlwaysSolo, kSquadSize 1, kSingleCapturer, kTeamSolo) with parties sized per camp: no camp needing more
  than 3 before r500 beyond 20 tiles (kMaxNeed), party present within 15 (kPartyPresent), leader starts early when it can hold
  (kStartBeforeParty), help calls within 25 (kHelpCall), join a mate's fight (kJoinFight), waves on camps too big (kWaveFallback).
- Reward routing: gold-heavy rewards to Vesper when within 6 (kVesperCarry 2), Marcella takes whole rewards (kMarcellaCarry).
- Recall-capture (kRecallCapture 4): start the recall on the reward tiles so it overlaps the capture, unless home is 20+ steps
  worse for the next camp (kRecallCapSlack 20) or the bag must bank (kRecallCapBank 10). #371: a healthy (90%+) champion whose
  gold + this reward buys not even a shard only recalls when home is no further from the next camp; with no camp next it
  recalls in the downtime (kRecallCapIdleSlack 0, kRecallCapBuyMode 1, kRecallCapIdleNone).
- Camp fighting: monster reach table (kTrueReach), area spells at the densest packs (kCampAoe 15, kSplashAim), stuns in camp
  planning (kStunModel), fight stall/close, loop and jam guards (kLoopGuard 10, kAllyJam 2, kAntiOsc 4).

## Builds and shopping
- Shop at spawn: shards to the next emblem first, altar lock, teleport crystal where planned (kShopFix, kUseAltarLocks).
- Heart of Ruin: Treasure H, Jungle F, Bruiser H; Willow: Durability H, Bruiser H, Treasure F (kBuild2 24, the #369 change).
  Ryth: Treasure H, Jungle H, Bruiser H (kRythBuild 1). Marcella: the rank-3/10 teams' focus lines (kMarcBuild 3).
  Vesper: the general meta path (no Vesper-specific line on). Treasure first on long-game layouts / boss maps (kTreasureBuild 1).

## Team coordination (shared memory: Codex owns the layout)
- Published targets and squad claims, respawn events (byte 5), enemy banker (kBankerByte 8), enemy carry sightings from r400
  (kCarryCast 2), help and boss calls, defend alerts, the draft plan.
- Willow heals the most-hurt ally in reach and never steps into a fight (kWillowHeal, kWillowStay); no follow/medic mode.

## Fuel
- Governor for heavy turns (kFuelGov 1: big-map scoring when the mean turn cost passes 70k), linear field copies (kFieldLin 12),
  per-turn caches (kFuelCache, kFuelEpoch, kFuelAllies, kCampSnap, kTeamTotalOnce), big-map rescoring cadence (kScoreBigGroups 36),
  dead turns build fields (kDeadCompute).

## Off: built and measured, not live (selection)
- Willow: follow the group / follow gate / heal party / medic / heal-wait (kWillowFollow, kFollowGate, kHealParty, kMedicCall,
  kHealWait) - Noobot-era tests negative or neutral.
- Recalls: recall sync, late/early trip rules, emblem-sized purchase test, layout gate (kRecallSync, kLateTripRound,
  kRecallCapBuyMode 2, kRecallCapIdleMid); #370's 100-gold version (ladder -2 wins).
- Routing: lookahead (-59 at 16 games/map), nearer-mate, cohesion / near-ally, map categories (kLookahead, kNearerMate,
  kCohesion, kNearAlly, kMapCat).
- Combat: team focus target, tile micro, flee to allies / closest ally, turn and fight, secure kill, pick-off, rally
  (kTeamFight, kTileMicro, kFleeToAllies, kFleeClosest, kTurnFight, kSecureKill, kPickOff, kRally); escape-dash keep.
- Builds: wholesale top-5 copies (kBuild3, kTopBuild: -132 locally), Home emblem builds, pure farm builds.
- Economy: gold-share captures, poorest capturer, squad rotation, shop-all, wait-shop, bank-while-waiting.
