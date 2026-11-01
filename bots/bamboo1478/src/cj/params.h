// Tunable parameters (override with -D or by editing variant copies).
#pragma once
#ifndef P_TRIB_GEMS
#define P_TRIB_GEMS 60
#endif
#ifndef P_TRIB_NEAR
#define P_TRIB_NEAR 6       // tribute any gems when an altar is this close
#endif
#ifndef P_TRIB_MID_GEMS
#define P_TRIB_MID_GEMS 25
#endif
#ifndef P_TRIB_MID_DIST
#define P_TRIB_MID_DIST 10
#endif
#ifndef P_MAX_WAIT
#define P_MAX_WAIT 15       // max idle rounds to wait for a respawn when choosing a task
#endif
#ifndef P_GEM_W
#define P_GEM_W 3.f         // value of a gem in gold-equivalents
#endif
#ifndef P_GOLD_W_EARLY
#define P_GOLD_W_EARLY 1.f
#endif
#ifndef P_GOLD_W_LATE
#define P_GOLD_W_LATE 0.4f
#endif
#ifndef P_HP_COST
#define P_HP_COST 0.03f     // rounds of champion time per hit point lost (healing trips)
#endif
#ifndef P_SHOP_GOLD
#define P_SHOP_GOLD 300
#endif
#ifndef P_SHOP_GOLD_HURT
#define P_SHOP_GOLD_HURT 150
#endif
#ifndef P_HOME_HP
#define P_HOME_HP 0.30f     // go heal below this health fraction
#endif
#ifndef P_SWITCH
#define P_SWITCH 1.4f       // keep the current task unless an alternative scores this much better
#endif
#ifndef P_GATHER_WAIT
#define P_GATHER_WAIT 30    // rounds an opener waits at a heavy group for helpers
#endif
#ifndef P_OPENING
#define P_OPENING 0
#endif
#ifndef P_OPEN_MAX_DIST
#define P_OPEN_MAX_DIST 40  // opening group must be this close to spawn
#endif
#ifndef P_TANK_FLOOR
#define P_TANK_FLOOR 0.25f  // a tank keeps this health fraction in reserve
#endif
#ifndef P_SINGLE_CAPTURE
#define P_SINGLE_CAPTURE 1
#endif
#ifndef P_ENABLE
#define P_ENABLE 1.6f       // value multiplier when my joining is what makes a heavy group possible
#endif
#ifndef P_ENEMY_SIDE_W
#define P_ENEMY_SIDE_W 0.5f  // value multiplier for groups on the enemy half
#endif
#ifndef P_SIDE_MARGIN
#define P_SIDE_MARGIN 4      // groups within this many steps of equidistant count as contested, not enemy
#endif
#ifndef P_CAP_RECALL
#define P_CAP_RECALL 1          // recall while capturing when going home soon anyway
#endif
#ifndef P_CAP_RECALL_HP
#define P_CAP_RECALL_HP 0.6f
#endif
#ifndef P_CAP_RECALL_GOLD
#define P_CAP_RECALL_GOLD 150
#endif
#ifndef P_ENGAGE
#define P_ENGAGE 0.3f        // engage champions when the focus-fire simulation leaves us this far ahead
#endif
#ifndef P_FLEE
#define P_FLEE -0.1f         // retreat from nearby champions when the simulation leaves us this far behind
#endif
#ifndef P_LOCKS
#define P_LOCKS 0            // carry an altar lock and lock contested altars we tribute at (blocks only the enemy)
#endif
#ifndef P_LOCK_SIDE
#define P_LOCK_SIDE 8        // lock only altars that are contested or on their half (side below this)
#endif
#ifndef P_RALLY
#define P_RALLY 0            // team rallies on heavy (golem) groups (off: squads idle too long)
#endif
#ifndef P_RALLY_RATE
#define P_RALLY_RATE 1.3f    // minimum value per champion-round for a rally
#endif
#ifndef P_RALLY_MAX
#define P_RALLY_MAX 110      // rounds before an unfinished rally is called off
#endif
#ifndef P_RALLY_FROM
#define P_RALLY_FROM 60      // no rallies before this round (opening first)
#endif
#ifndef P_RALLY_DMAX
#define P_RALLY_DMAX 50      // farthest champion's walk to a rally group
#endif
#ifndef P_RALLY_MAX_DPS
#define P_RALLY_MAX_DPS 150  // rally groups hit at most this hard (golems yes, monoliths no)
#endif
#ifndef P_SALT
#define P_SALT 0             // perturbs re-planning phases (benchmark sampling only)
#endif
#ifndef P_RALLY_MIN_DPS
#define P_RALLY_MIN_DPS 100.f  // rally groups hit at least this hard (two elks, golems)
#endif
#ifndef P_RALLY_BIG_ONLY
#define P_RALLY_BIG_ONLY 0     // rallies only on golem groups
#endif
#ifndef P_RALLY_SPREAD
#define P_RALLY_SPREAD 99      // max difference between squad members' walks to a rally
#endif
#ifndef P_RALLY_GATHER_W
#define P_RALLY_GATHER_W 0.5f  // weight of squad idle time waiting for the last member
#endif
#ifndef P_CHIP
#define P_CHIP 1               // take heavy groups solo over several healing trips (camps never regenerate)
#endif
#ifndef P_CHIP_BIG
#define P_CHIP_BIG 1           // chip golem groups over several healing trips too (shared by whoever has spare health)
#endif
#ifndef P_CHIP_BIG_TRIPS
#define P_CHIP_BIG_TRIPS 8.f   // healing trips my share of a golem chip may need
#endif
#ifndef P_HEAL_SUSTAIN
#define P_HEAL_SUSTAIN 1       // a Willow on the same group counts as tank sustain in heavy-group feasibility
#endif
#ifndef P_HEAL_EFF
#define P_HEAL_EFF 0.8f        // share of her heals that land on the tank
#endif
#ifndef P_FREE_CAST
#define P_FREE_CAST 1          // cast ranged damage/cc abilities at enemies in range in every combat turn
#endif
#ifndef P_FREE_EXCL_MIN
#define P_FREE_EXCL_MIN -0.3f  // movement-exclusive casts only when the fight is above this (no retreat coming)
#endif
#ifndef P_HIT_RUN
#define P_HIT_RUN 1            // melee champions attack an adjacent enemy before retreating
#endif
#ifndef P_SKIRMISH
#define P_SKIRMISH 1           // an enemy in my attack reach and the fight above P_SKIRMISH_MIN: attack it
#endif
#ifndef P_SKIRMISH_MIN
#define P_SKIRMISH_MIN -0.3f
#endif
#ifndef P_RETREAT_COUNT_R
#define P_RETREAT_COUNT_R 4      // retreating allies this close (and healthy) still count on our side of the fight
#endif
#ifndef P_RETREAT_COUNT_HP
#define P_RETREAT_COUNT_HP 0.5f  // ... when above this health fraction
#endif
#ifndef P_TRAP_RECALL
#define P_TRAP_RECALL 1        // standing still, idle, with no walkable way home (camps respawned around me): recall
#endif
#ifndef P_WILLOW
#define P_WILLOW 1             // 5-champion draft: Willow (healer, last id: never tanks) instead of Ryth
#endif
#ifndef P_CHIP_FLOOR
#define P_CHIP_FLOOR 0.3f      // health fraction kept when chipping (go heal below it)
#endif
#ifndef P_CHIP_MAX_TRIPS
#define P_CHIP_MAX_TRIPS 3.f   // extra healing trips a solo chip may need
#endif
#ifndef P_CHIP_START
#define P_CHIP_START 0.6f      // start a chip only with this health fraction
#endif
#ifndef P_JUNGLE_FIRST
#define P_JUNGLE_FIRST 1       // buy the jungle emblem before anything else
#endif
#ifndef P_HOME_HP_ENEMY
#define P_HOME_HP_ENEMY 0.55f  // go heal below this health fraction when enemies were seen nearby recently
#endif
#ifndef P_CHIP_TRIP_W
#define P_CHIP_TRIP_W 2.f      // healing trip cost in multiples of the group's distance from spawn
#endif
#ifndef P_NO_FUTILE_FLEE
#define P_NO_FUTILE_FLEE 0     // fight back instead of fleeing from an adjacent melee champion (no dash ready)
#endif
#ifndef P_TRIB_SLOPE
#define P_TRIB_SLOPE 0.f       // extra gems carried before a tribute trip, per tile to the altar
#endif
#ifndef P_CAPTURE_MODE
#define P_CAPTURE_MODE 1       // capture bonus: 0 passives only (Vesper gold, Marcella gems); 1 gold x efficiency
#endif
#ifndef P_MAR_STR
#define P_MAR_STR 0            // Marcella stacks bruiser strength instead of focus
#endif
#ifndef P_END_TRIB
#define P_END_TRIB 850         // once either team has submitted this many gems, tribute whatever we carry
#endif
#ifndef P_CHASE_DISCIPLINE
#define P_CHASE_DISCIPLINE 1   // do not chase enemies that fight nobody, nor leave awake camps to chase
#endif
#ifndef P_CRYSTALS
#define P_CRYSTALS 2           // teleport crystals carried on island maps
#endif
#ifndef P_BUILD
#define P_BUILD 4              // 1: single bruiser stat; 2: bruiser cycles with health mixed in
#endif
#ifndef P_WAIT_TANK
#define P_WAIT_TANK 0
#endif
#ifndef P_SIEGE_FROM
#define P_SIEGE_FROM 400
#endif
#ifndef P_SIEGE_HP
#define P_SIEGE_HP 3000.f
#endif
#ifndef P_SIEGE_LATE
#define P_SIEGE_LATE 900
#endif
#ifndef P_SIEGE_MAX
#define P_SIEGE_MAX 300        // rounds before an unfinished siege is called off
#endif
#ifndef P_HEAVY_SHARE
#define P_HEAVY_SHARE 0.6f     // gem-income share in heavy groups that makes a map a siege map
#endif
#ifndef P_MAR_ROUTE
#define P_MAR_ROUTE 0.f        // route gem captures through Marcella (off: she walks alone and dies)
#endif
#ifndef P_SIEGE_DEATHS
#define P_SIEGE_DEATHS 2       // heavy-map siege called off when this many of us are dead at once
#endif
#ifndef P_SIEGE_CHECK
#define P_SIEGE_CHECK 120      // a heavy-map siege must have taken 30% of its target's health by then
#endif
#ifndef P_EXTRA_FIX
#define P_EXTRA_FIX 1          // heavy-group helper count: free allies (committed ones were never in the free pool)
#endif
#ifndef P_IDLE_HEAL
#define P_IDLE_HEAL 0.8f       // idle below this health fraction: go heal instead of standing around
#endif
#ifndef P_YIELD
#define P_YIELD 1              // step out of the way of allies heading home; boxed-in retreat steps out of camp reach
#endif
#ifndef P_PULL_WAIT
#define P_PULL_WAIT 15         // non-tanks wait this long for the tank to pull a group they could not tank alone
#endif
#ifndef P_OUTNUM
#define P_OUTNUM 0             // outnumbered by visible enemies and not clearly ahead: retreat before contact
#endif
#ifndef P_BURST_GUARD
#define P_BURST_GUARD 1.3f     // retreat when health is below this multiple of the burst enemies can land next round
#endif
#ifndef P_HURT_AWAKE
#define P_HURT_AWAKE 1         // hurt with no enemy champion near: unseen camps in reach are awake
#endif
#ifndef P_OPEN_ABORT
#define P_OPEN_ABORT 1         // an aborted (blacklisted) opening group ends the opening
#endif
#ifndef P_MAR_FIRST
#define P_MAR_FIRST 0          // draft Marcella first: she tanks (lowest id) and so captures and tributes most gems
#endif
#ifndef P_PREWAIT
#define P_PREWAIT 1            // with nothing to do, wait at the group that respawns soonest instead of idling
#endif
#ifndef P_MAR_EFF
#define P_MAR_EFF 0.6f         // capture-gold efficiency weight for Marcella (others: Vendetta 1, Vesper 0.85)
#endif
#ifndef P_OPEN_SAFE
#define P_OPEN_SAFE 0.6f       // opening group: camp damage over the kill must fit in this share of the team's spare health
#endif
#ifndef P_SIGHT_FIX
#define P_SIGHT_FIX 1          // at an attack spot with no live camp in sight: step next to the camps
#endif
#ifndef P_BUSH_CAMPS
#define P_BUSH_CAMPS 1         // camps in bushes are only visible from bush tiles: attack them from there
#endif
#ifndef P_CAP_FIX
#define P_CAP_FIX 1            // yield a capture only to an ally whose task it is
#endif
#ifndef P_LEAVE_BL
#define P_LEAVE_BL 12          // rounds a capture left to an ally stays off my list (0: old behaviour)
#endif
#ifndef P_WATCHDOG
#define P_WATCHDOG 6           // still this many turns while busy (not attacking): drop the task (0 = off)
#endif
#ifndef P_BURST_REACH
#define P_BURST_REACH 1        // fight sim: ability bursts land from 4 tiles (dashers 3, Vesper 5), not the attack range
#endif
#ifndef P_MAR_BUILD
#define P_MAR_BUILD 1          // 1: Marcella builds focus (monster, jungle, durability, then bruiser focus x2 + health)
#endif
#ifndef P_WARD_ENEMY_R
#define P_WARD_ENEMY_R 9       // no ward placement with an enemy champion this close (fight turns need the fuel)
#endif
#ifndef P_WARD_MIN_FUEL
#define P_WARD_MIN_FUEL 60000
#endif
#ifndef P_ESC_FT_EXTRA
#define P_ESC_FT_EXTRA 8       // escape planner: enemy front field radius beyond my own search radius
#endif
#ifndef P_ESC_MIN_FUEL
#define P_ESC_MIN_FUEL 45000   // skip the escape planner (~27k) below this much fuel left
#endif
#ifndef P_ABORT_FIX
#define P_ABORT_FIX 1          // aborts count all committed allies, need 2 rounds, never during the opening; engaged flag
#endif
#ifndef P_ESCNEED_TARGET
#define P_ESCNEED_TARGET 1     // health needed to leave awake camps counts only camps that would target me
#endif
#ifndef P_FINISH
#define P_FINISH 4.f           // stay to finish my group when it has at most this many rounds of our damage left
#endif
#ifndef P_TANK_HANDOVER
#define P_TANK_HANDOVER 1      // with another tank present, a tank keeps only two rounds of hits in reserve
#endif
#ifndef P_SEQ_DMG
#define P_SEQ_DMG 1            // camp fight damage estimate: damaging camps die one by one (0: constant group dps)
#endif
#ifndef P_ABORT_SLACK
#define P_ABORT_SLACK 1.15f    // a started group is abandoned only when the damage still to take exceeds this x spare
#endif
#ifndef P_RETREAT_HYST
#define P_RETREAT_HYST 0.3f    // after a retreat, keep avoiding unless the outcome beats P_AVOID by this much
#endif
#ifndef P_RETREAT_HYST_R
#define P_RETREAT_HYST_R 3     // ... for this many rounds
#endif
#ifndef P_ALTAR_STICKY
#define P_ALTAR_STICKY 4       // keep the altar chosen last round unless another is this many steps closer (0: off)
#endif
#ifndef P_ENGAGE_BUSY
#define P_ENGAGE_BUSY 1        // chase discipline does not apply to targets tanking camps, capturing or channelling
#endif
#ifndef P_GATHER_CHIP
#define P_GATHER_CHIP 3        // waiting at a heavy group this long with nobody coming: chip it (-1: off)
#endif
#ifndef P_GATHER_CHIP_BIG
#define P_GATHER_CHIP_BIG 2    // golem groups: chip only with this many champions present
#endif
#ifndef P_BURST_HEAL_FULL
#define P_BURST_HEAL_FULL 0.9f  // burst_low only below this health fraction
#endif
#ifndef P_BURST_HEAL
#define P_BURST_HEAL 1.2f      // go heal below this multiple of the biggest enemy burst seen recently (enemies near)
#endif
#ifndef P_DPS_HP
#define P_DPS_HP 0             // Vesper/Vendetta: jungle, durability (health), monster, then bruiser str/health
#endif
#ifndef P_DANGER_W
#define P_DANGER_W 1.f         // value multiplier for groups where enemy champions were seen in the last 20 rounds
#endif
#ifndef P_ESCAPE
#define P_ESCAPE 1             // race-based retreat: reach tiles before the enemies' reach does (recall spots, homewards)
#endif
#ifndef P_ESC_R
#define P_ESC_R 8              // retreat planning radius (walking steps)
#endif
#ifndef P_ESC_RECALL_HP
#define P_ESC_RECALL_HP 0.5f   // at a safe recall spot while retreating: recall below this health fraction
#endif
#ifndef P_CAUGHT_FIGHT
#define P_CAUGHT_FIGHT 0       // no tile in reach stays ahead of the chasers: hit back instead of fleeing
#endif
#ifndef P_RETREAT_CODE
#define P_RETREAT_CODE 1       // retreating champions say so in their slot (allies do not count them as help)
#endif
#ifndef P_ENEMY_CD
#define P_ENEMY_CD 1           // read enemy ability cooldowns (visible champions): bursts and dashes only when ready
#endif
#ifndef P_ESC_CAP
#define P_ESC_CAP 3            // healthy retreat: margin over the chasers worth keeping (beyond it, head home); 0 = always seek a recall spot
#endif
#ifndef P_ASSIST
#define P_ASSIST 1             // join a fight where an ally near me is being hit (unless the simulation says it is lost)
#endif
#ifndef P_ASSIST_R
#define P_ASSIST_R 6           // allies within this distance are assisted
#endif
#ifndef P_ASSIST_MIN
#define P_ASSIST_MIN -0.1f     // assist when the simulated outcome (with me) is above this
#endif
#ifndef P_CONTACT
#define P_CONTACT 1            // contact-based fight decisions: hold in contact unless clearly lost, avoid early otherwise
#endif
#ifndef P_HOLD_C
#define P_HOLD_C -0.6f         // in contact: fight back while the simulated outcome is above this
#endif
#ifndef P_AVOID
#define P_AVOID -0.85f           // out of contact: step away from enemies when the outcome is below this
#endif
#ifndef P_TP_SHORTCUT
#define P_TP_SHORTCUT 1        // jump over holes/walls with teleport crystals when it saves walking
#endif
#ifndef P_TP_GAIN
#define P_TP_GAIN 3            // steps saved (beyond the 4 rounds of channel and flash) to use a crystal
#endif
#ifndef P_TP_MIN
#define P_TP_MIN 10            // only for goals at least this far
#endif
#ifndef P_TP_CRYSTALS
#define P_TP_CRYSTALS 3        // crystals carried for shortcuts
#endif
#ifndef P_TP_WANT_WINDOW
#define P_TP_WANT_WINDOW 1000  // keep buying crystals this long after a shortcut was wanted
#endif
#ifndef P_WARDS
#define P_WARDS 1
#endif
#ifndef P_WARD_BUSH
#define P_WARD_BUSH 15         // ward score bonus for bush tiles
#endif
#ifndef P_BANK_SAFE
#define P_BANK_SAFE 1          // bank gems under pressure only if the walk and channel are survivable
#endif
#ifndef P_BANK_SAFE_F
#define P_BANK_SAFE_F 0.8f     // ...expected incoming damage below this share of my health
#endif
#ifndef P_REINF_ENGAGE
#define P_REINF_ENGAGE 0      // engaging counts enemies seen within this many rounds (out of sight now) as joining
#endif
#ifndef P_SIM_SYM
#define P_SIM_SYM 1            // fight sim: enemies reach the fight at our counted fighters (not at allies who stay out)
#endif
#ifndef P_SIM_REACT
#define P_SIM_REACT 0          // fight sim: rounds an ally needs to react before joining
#endif
#ifndef P_ALLY_CD
#define P_ALLY_CD 1            // read allies' cooldowns too: their bursts only when ready
#endif
#ifndef P_SIM_JOIN_R
#define P_SIM_JOIN_R 4         // allies this close to me join my fight even if they cannot see the enemies yet
#endif

#ifndef P_PRIO
#define P_PRIO 1               // scheduling priority: champions near enemies act first within the team (low health first)
#endif
#ifndef P_PRIO_R
#define P_PRIO_R 6             // ... enemies within this distance
#endif
#ifndef P_DASH_ENGAGE
#define P_DASH_ENGAGE 1        // dashers (Vendetta, Vesper, Issac, Ren) dash to strike a target just out of reach
#endif
#ifndef P_HOR_AOE
#define P_HOR_AOE 1            // Heart of Ruin's dash lands where its blast catches the most enemies
#endif
#ifndef P_SPREAD
#define P_SPREAD 1             // enemy area blasts ready: fight from tiles not adjacent to allies
#endif
#ifndef P_KILLSHOT
#define P_KILLSHOT 1           // go for enemies I can finish this turn; exclusive nukes cast for kills
#endif
#ifndef P_SUPPORT
#define P_SUPPORT 1            // Willow follows the nearest working ally instead of farming alone
#endif
#ifndef P_SUPPORT_FROM
#define P_SUPPORT_FROM 0
#endif
#ifndef P_SUPPORT_MAR
#define P_SUPPORT_MAR 1        // Willow supports Marcella first
#endif

#ifndef P_HITFIX
#define P_HITFIX 2             // in fights, attack anyone in reach when the focus target is out of reach (2: holdfight closes in)
#endif

#ifndef P_HOLD_NUKE
#define P_HOLD_NUKE 1          // holdfight: cast movement-exclusive damage abilities (we stand anyway)
#endif

#ifndef P_ESC_RELIEF
#define P_ESC_RELIEF 1         // escape_need counts the rounds until a healthy ally behind takes the camps over
#endif
#ifndef P_ESC_RELIEF_HP
#define P_ESC_RELIEF_HP 0.5f   // ... allies above this health fraction
#endif

#ifndef P_CALM_AVOID
#define P_CALM_AVOID 1         // enemies keeping their distance do not trigger avoidance
#endif
#ifndef P_CALM_D
#define P_CALM_D 5             // ... when all of them are at least this far
#endif
#ifndef P_CALM_HP
#define P_CALM_HP 0.6f         // ... and my health fraction is at least this
#endif

#ifndef P_CAP_STAY
#define P_CAP_STAY 1           // capturing: stay on the tile under attack (hit back from it) unless about to die
#endif
#ifndef P_CAP_STAY_GEMS
#define P_CAP_STAY_GEMS 20
#endif
#ifndef P_CAP_STAY_GOLD
#define P_CAP_STAY_GOLD 100
#endif

#ifndef P_SUP_FIX
#define P_SUP_FIX 1            // choose_task: a supporting Willow (she copies an ally's task) is not a committed helper
#endif

#ifndef P_MONO_SIEGE
#define P_MONO_SIEGE 1         // monoliths are siege targets on every map (whole team, several trips)
#endif
#ifndef P_MONO_FROM
#define P_MONO_FROM 350
#endif
#ifndef P_MONO_HP
#define P_MONO_HP 1800.f       // ... once the leader (lowest alive id, the tank) has this much max health
#endif

#ifndef P_CT_FUEL
#define P_CT_FUEL 35000        // choose_task stops evaluating groups below this much fuel (an exhausted turn loses its action)
#endif

#ifndef P_REPLAN_MIN
#define P_REPLAN_MIN 60000     // defer the periodic re-plan (task still valid) below this much fuel, at most 2 turns
#endif
#ifndef P_NAV_LOW
#define P_NAV_LOW 22000        // below this: travel by the static field only (no BFS)
#endif

#ifndef P_NODEAD
#define P_NODEAD 1             // a teammate's fight nearby: join it or leave, never farm beside it
#endif
#ifndef P_ND_R
#define P_ND_R 6               // ... teammates within this distance
#endif
#ifndef P_ND_JOIN
#define P_ND_JOIN -0.5f        // ... join when the simulated outcome is above this, else leave
#endif
