# bot_10: design notes and research

bot_10 is a C++ bot added on 11-01 (branch `bot-10`, source in `bots/pool/bot_10/src`, unchanged from the zip it came
in). These notes cover how it works, where it is out of date for engine 2.0.0, and ideas to test. **Nothing here has been
measured yet.** Every idea is a hypothesis with a ready variant or a pointer to the code it would touch. Rules and numbers
are from `docs/MECHANICS.md`; this file only adds what is specific to bot_10.

**Do not gate bot_10 variants before the Sprint 3 lock (Sun 1 Nov 05:29 IST).** Gates submit the bot they test
(`docs/WORKFLOW.md`). Local runs are safe.

## 1. How bot_10 works

About 5,200 lines. It compiles against the repo's SDK 4.0.0 (`clang++ -std=c++20 -fsyntax-only -I sdk/cpp`, no errors;
two warnings: unused `our_dps` at fight.cpp:542, missing `los` initializer at world.cpp:46).

| File | Lines | Role |
| --- | --- | --- |
| `main.cpp` | 24 | Draft turn or `Bot::play_turn()`; exceptions are caught, logged, and the turn still ends |
| `draft.cpp` | 28 | Fixed lineup by team size (below); pick order sets the ally ids, and the lowest id tanks |
| `params.h` | 526 | About 150 `P_*` switches and weights, set with `#define`, many of them A/B toggles |
| `bot.cpp` | 1073 | Turn pipeline, shop, tribute and altar choice, wards, crystal shortcuts, scans of visible units (cooldowns included) |
| `world.h/.cpp` | 669 | Per-champion map model: camp groups and their state, static distance fields (lazy, fuel-gated), islands and crystal jumps, gated altars, heavy-map detection |
| `nav.h` | 210 | Greedy descent of static fields far from the goal, BFS near it, escape and flee |
| `comms.h` | 80 | The 8-byte protocol (below) |
| `farm.cpp` | 1120 | Task (camp group) choice, opening, rallies, chipping of heavy groups over several healing trips, sieges, capture, island travel |
| `fight.cpp` | 1108 | A focus-fire simulation decides whether to engage, hold or retreat; ability use; escape planner; Willow support; turn priority |

**Turn pipeline** (`Bot::play_turn`, bot.cpp:783), in order:
1. Read comms and apply capture events.
2. If dead: shop.
3. Observe camp groups; detect our own capture by the gold or gems that arrive.
4. While channelling, continue unless enemies would catch the channel.
5. Recall if trapped.
6. On spawn: shop and heal to 98%.
7. Bank gems under pressure when an altar is within 4.
8. `combat()`.
9. Otherwise: heal trip, tribute, shop trip (300 gold), or `farm()`.
10. Stuck watchdog.
11. Precompute fields with leftover fuel.

**Draft** (draft.cpp): five a side, Heart of Ruin, Marcella, Vendetta, Vesper Vale, Willow. Four: Heart of Ruin, Marcella,
Vendetta, Willow. Three: Heart of Ruin, Vendetta, Vesper Vale. It never looks at the enemy's picks or the map. If a pick
throws, it takes the first legal champion by enum order.

**Shop** (`plan_for`, bot.cpp:31, build `P_BUILD 4`): jungle emblem first. Then:
* Vesper and Vendetta: durability (health), monster (strength), then strength/health bruiser.
* Heart of Ruin: durability (health), then health/health/focus bruiser.
* Marcella: durability, monster (focus), then health/focus bruiser.
* Willow: focus bruiser.

Shards are bought on spawn, 30 gold at a time. A champion goes home to shop at 300 gold, or at 150 when below 60% health.
Crystals are bought on island maps; locks are off (`P_LOCKS 0`). No Home emblem and none of the 2.0.0 families.

**Shared memory** (comms.h, all 8 bytes in use):
* Bytes 0-4: one slot per ally, holding a task group id + 1 or one of home, tribute, fight, dead, retreat, plus an engaged flag.
* Bytes 5-6: the last capture event (group and round).
* Byte 7: the team rally target.

Nothing about the enemy is shared. Each champion keeps its own world model, and draft memory is unused.

**Captures** (farm.cpp:553-626): whoever farms a group captures it. When several allies stand on it, one stays
(`P_SINGLE_CAPTURE`), chosen by `capture_bonus`: Vesper (gold × 1.33 × 0.85), then Vendetta (gold × 1), Marcella
(0.6 × (gold + 2 × gems)), Heart of Ruin (0.45 × gold).

## 2. Where bot_10 is out of date for engine 2.0.0

bot_10 matches the 3.0.x rules: golems, the reworked Heart of Ruin, 120-HP clusters, camp ranges. It has no 2.0.0 code
(`docs/MECHANICS.md` section 0).

* **Its picks took the nerfs.** Heart of Ruin (strength growth 3.5 → 3, focus 12 → 10), Marcella (4.5 / 14) and Vesper
  Vale (base strength 55 → 45) were nerfed. Vendetta is unchanged and Willow was buffed (focus 120 → 140). The buffs it
  never drafts: Cassi (base focus 70 → 100), Ren (stun 0.75 → 1.1 × focus), Tavi (1.4 → 1.6), Varg and Issac (base
  strength +5), Stellar (focus growth 7 → 8.5).
* **No 2.0.0 items, no Home.** Each passive emblem gives 5 points of its stat. A bruiser emblem gives 7 (5 + 1 + 1), so a
  useful passive costs only 2 stat points against the bruiser emblem it displaces. Capture (team capture 5 → 3 turns) and
  Home (recall 5 → 3) are the obvious candidates; Skirmish (+5%) and Collectors (+1% per family) are not.
* **Crystals: carry limit 1** (`docs/MECHANICS.md`, measured). `P_CRYSTALS 2` and `P_TP_CRYSTALS 3` assume more: the
  second buy throws and is caught, so the only cost is a wasted host call. A champion who crystals onto an island has no
  crystal to leave with and recalls instead (farm.cpp:1074). That is safe but takes 5 rounds.
* **Logging ships on.** `BOT_LOGC` defaults to 1 (common.h:27): a formatted line every champion turn plus fight details,
  flushed through `fwrite` each turn. The team rule is no logging bots on the ladder. Every variant below turns it off.
* **Unused draft resources.** The first draft turn has 100× fuel and 1,024 bytes of draft memory reach every champion.
  bot_10's champions build their world model on their first turn instead. On big maps `init` can leave under 120k fuel,
  and the champion then skips its first action (bot.cpp:787).

## 3. Ideas to test

Make the variants with `python -I tools/variant/b10_ideas.py` (all of them, or name some). Each is `bots/pool/bot_10`
with one change and the log off. **`b10n` (log off, nothing else) is the base for every comparison.** All eleven were
made and syntax-checked here, with no errors. They are ordered by strength of evidence: ports of changes main measured
first, then ideas from the 2.0.0 rules, then removals of things main tried and rejected.

| Variant | Change | Evidence | Measure |
| --- | --- | --- | --- |
| `b10n` | Log off, nothing else | Base. The team ships no logging bots | b10n against main locally: faults, fuel, economy |
| `b10cc` | Carrier caution: with 30+ gems (`loaded`, fight.cpp:616) never engage, skip the hold, assist, join and skirmish branches (fight.cpp:785, 828, 864, 895), and count any fight as lost (901, 904) | Main's cc2: gems lost on death 141 → 80 a game, deaths −0.4, tributed +58 (`docs/lineage.md`). bot_10 only raises a carrier's engage bar to 0.45 (fight.cpp:663) | Gems lost on death, deaths, tributed by r1000 |
| `b10sq` | `choose_task` scores a group by value / √n instead of value / n (farm.cpp:490) | Main's sq2 counts a joiner's share as √n (`docs/lineage.md`). bot_10 spreads out: it joins a taken harmless group only when the owner needs longer than its own walk (farm.cpp:483-485) | Deaths, champions caught alone, collected |
| `b10d4` | Four a side: Willow → Vesper Vale | Main's four-pick lineup (Heart, Vesper, Marcella, Vendetta) won 11 of 26 four-pick maps against 5-6 (`bots/main/src/draft.cpp` comment, dq2m) | Four-pick maps only |
| `b10lki` | Lock-interrupt: buy one lock on spawn (10 gold); when a visible enemy is tributing at an altar within 2 tiles, place it there (new `Bot::lock_interrupt`, called after `see_units`; `P_LOCKS` stays 0) | Placing a lock cancels enemy tribute channels and blocks new ones until 5 hits (`docs/MECHANICS.md` §9). The killer takes the whole bag anyway, so a cancelled big tribute is a large swing; main's dl2 acts on the same rule | Enemy tributes cancelled, their gems banked after our lock |
| `b10cap` | Capture emblem: 2nd on Heart of Ruin (health), 4th on Vesper and Vendetta (strength) | Engine 2.0.0: team capture 5 → 3 turns. Main gives its five-a-side Vesper Capture of strength as her second emblem (`bots/main/src/shop.h:112-124`) | Captures per game, collected by r1000, deaths while capturing |
| `b10home` | Home emblem after the core emblems on Heart, Vesper, Vendetta, Marcella, Willow | Recall 5 → 3 on every healing and shop trip; spawn heals fully in one round | Rounds spent recalling, collected by r1000 |
| `b10bag` | `P_TRIB_GEMS` 60 → 48 | A killer takes the whole bag (`docs/MECHANICS.md`, "Tribute often"), and a tribute takes only ceil(0.1 × gems) rounds; main's bb2 gained from bags about 18% smaller | Gems lost on death, tributed by r1000 |
| `b10lock` | `P_LOCKS 1` (an existing bot_10 switch) | Lock contested or enemy-side altars we tribute at; 2.0.0 locks take 5 hits | Enemy tributes at our locked altars |
| `b10notp` | Teleport shortcuts off (`P_TP_SHORTCUT 0`; island travel still uses crystals) | Main's four shortcut tries (tp1, tp2, tpe, tpd) were rejected, net 0 or worse (`docs/experiments.md`) | Walk rounds on wall maps, collected |
| `b10noend` | No bank-everything sweep at 850 tributed (`P_END_TRIB` 2000; banking a winning bag stays) | Main's sweeps es1, es2 and dr7 were neutral or rejected (`docs/experiments.md`) | Close games, gems carried at the end |

## 4. Compared with main (vx1)

These come from a design comparison of the two bots. Each point below was checked against the source or the docs named.

* **Lineup.** Main plays Heart of Ruin, Vesper, Marcella, Vendetta and Varg four and five a side, and Heart, Vendetta,
  Vesper three a side. On a three-pick map with no gold camps it plays Heart, Vesper, Marcella (`bots/main/src/draft.cpp`,
  nm2). bot_10 has no Varg, takes Willow, and leaves Vesper out four a side.
* **Groups.** Main counts a joiner's share as √n (sq2). bot_10 counts 1/n, which spreads the team.
* **Carriers.** Main's carrier with 30+ gems never engages (cc2). bot_10's carrier still holds, assists and skirmishes.
* **Endgame.** Main locks the rivals' game-winning tribute (dl2), chases the winning carrier (dl4), and splits a winning
  capture (sc1). bot_10 has none of these.
* **Robustness.** Main skips any action that follows a search when the round has moved on or fuel is under 1,000
  (`stale()`, `bots/main/src/snapshot.h:203`, from fd2z). bot_10 has no such guard and logs every turn.

**bot_10 ideas worth testing in main:**
1. **Willow as an escort.** bot_10's Willow follows the nearest working ally, Marcella first (`P_SUPPORT`,
   `try_support`). Main's wl1 (Willow for Varg) was N: "52 more deaths in 60 games; Willow's 700 health farms alone". The
   follow rule addresses exactly that.
2. **Capture plus recall.** When it is going home anyway (below 60% health, 150+ gold, or off the mainland) and no enemy
   is in view, bot_10 starts the recall on the capture tile. The 5-round capture completes during the 5-round recall
   (farm.cpp:599-603).
3. **Tribute from a dead guard's tile** on walled-in altars (bot.cpp:474-561). This is the idea behind gf2. fin2 (vx1
   plus gf2 alone) was prepared but never gated (`docs/status.md`).
4. **Spreading against area stuns** while an enemy area spell is ready (`P_SPREAD`), and aiming Heart of Ruin's dash at
   the most enemies (`P_HOR_AOE`).

## 5. Larger ideas (no variant yet)

1. **Draft for 2.0.0, five a side.** Willow (bot_10) or Varg (main) is the open question. Let the draft also read the map
   (the SDK serves `camp_groups()` during the draft), as main's nm2 does. Some bot_10 logic is champion-specific (Willow
   support, Marcella routing, Heart of Ruin's dash), so a new lineup needs a breakage check first.
2. **Stale-round guard.** Port main's `stale()`: skip an action when `round_number()` changed during the turn or fuel is
   under 1,000. It touches every action site.
3. **Walk in to interrupt.** `b10lki` only locks when a champion is already within 2 of the altar. A tribute of g gems
   lasts ceil(0.1 × g) rounds (6 for a 60-gem bag), so a champion 3-4 tiles away could still step in and lock in time.
4. **Draft-time precompute.** Use the 100×-fuel draft turn to analyse the map (group distances, islands, gates, the
   opening). Pass a compact result through the 1,024 bytes of draft memory, so no champion loses its first turn on a
   big map (bot.cpp:787).
5. **Share enemy sightings.** All 8 bytes are taken, and nothing tells allies where enemies are. Packing the per-ally
   slots tighter could free a byte or two for the last enemy carrier seen.

## 6. Benchmark commands

On the team machine. Local runs submit nothing. Write the decision rule in `docs/experiments.md` first. Local results
judge faults, fuel and economy, not fights, items or the draft (`docs/WORKFLOW.md`).

```
python -I tools/variant/b10_ideas.py                                         # all variants into bots/exp/
powershell -File tools/cambc.ps1 build exp/b10n --release                    # compile check, same for the others
python -I tools/local/multi.py exp/b10n --pool main --jobs 6 --keep          # head to head with main
python -I tools/local/audit_errors.py data/runs/multi-HHMMSS                 # bot errors, turns out of fuel
python -I tools/local/multi.py main,exp/b10n --pool pool/cand1,pool/cp3,pool/dh3 --jobs 6   # common-opponent screen
python -I tools/local/lpair.py data/runs/multi-HHMMSS main data/runs/multi-HHMMSS exp.b10n
python -I tools/local/coll_at.py data/runs/multi-HHMMSS 300 600 1000
python -I tools/local/multi.py exp/b10cc --pool pool/cand1,pool/cp3,pool/dh3 --jobs 6        # then each idea, against b10n's run
```

Notes:
* `audit_errors.py` and `ltypes.py` add up every candidate in a run folder, so give them a folder with one candidate.
* Use `--jobs 11` only with 2 GB or more of free RAM.
* Delete the `bots/exp/` folders once their rows are written.

Item, draft and fight changes need the platform, and only after the Sprint 3 lock.

## 7. Open questions

* bot_10 already assumes the killer takes the bag (bot.cpp:926, "gems are theirs if I die there"), which matches
  `docs/MECHANICS.md`. Its bank threshold of 60 was tuned under 3.0.x (`b10bag`).
* bot_10's tank rotation keeps non-tanks farther from damaging camps than the tank (farm.cpp). It relies on camps
  breaking distance ties toward the lowest id, which `docs/MECHANICS.md` does not confirm; probe that before relying on it.
* The farming and fight audits (`farm.cpp`, `fight.cpp`) are in progress. Their findings will be added here.
