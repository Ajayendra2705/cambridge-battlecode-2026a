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

Make the variants with `python -I tools/variant/b10_ideas.py` (all of them; or name some). Each is `bots/pool/bot_10`
plus one change, with the log off. **`b10n` (log off, nothing else) is the base for every comparison.** All five were
made and syntax-checked here (no errors).

| Variant | Change | Why | Measure |
| --- | --- | --- | --- |
| `b10n` | log off | Base; also the fair version of bot_10 to compare with main | Is bot_10 competitive at all (b10n against `pool/vx1`, locally first) |
| `b10cap` | Capture emblem: 2nd on Heart of Ruin (health), 4th on Vesper and Vendetta (strength) | 2 rounds saved per capture, and less time on a contested tile | Captures per game, collected gems by r1000, deaths while capturing |
| `b10home` | Home emblem after the core emblems on Heart of Ruin, Vesper, Vendetta, Marcella, Willow | Recall 5 → 3 on every healing and shop trip (spawn heals fully in one round) | Rounds spent recalling, collected by r1000 |
| `b10lock` | `P_LOCKS 1` (an existing bot_10 switch) | Carry one lock and lock contested or enemy-side altars we tribute at; 2.0.0 locks take 5 hits | Enemy tributes at locked altars, our lock placements |
| `b10bag` | `P_TRIB_GEMS` 60 → 48 | A killer takes the whole bag (`docs/MECHANICS.md`, "Tribute often"), and a tribute takes only ceil(0.1 × gems) rounds; main's bb2 gained from bags about 18% smaller | Gems lost on death, tributed by r1000 |

Larger ideas, no variant yet, in rough order of expected value:

1. **Draft for 2.0.0.** Re-pick with the nerfs and buffs above, and let the draft look at team size and the map (the SDK
   serves `camp_groups()` during the draft). Risky: some bot_10 logic is champion-specific (Willow support, Marcella
   routing, Heart of Ruin's dash), so a new lineup needs a breakage check first.
2. **Interrupt enemy tributes with a lock.** Placing a lock on an altar within 2 tiles cancels the enemy tribute channels
   there and blocks new ones until 5 hits break it (`docs/MECHANICS.md` §9). The killer takes the whole bag anyway, so
   cancelling a big tribute is worth a lot. bot_10 only locks altars it tributes at itself. Main's dl2 locks against the
   rivals' game-winning tribute; bot_10 would need the same trigger (a visible enemy channelling at an altar within 2 of
   a champion who carries a lock). `tools/variant/mklock.py` targets main's code, not bot_10's.
3. **Draft-time precompute.** Use the 100×-fuel draft turn to analyse the map (group distances, islands, gates, the
   opening) and pass a compact result to every champion through the 1,024 bytes of draft memory, so no first turn is
   lost on big maps.
4. **Share enemy sightings.** All 8 bytes are taken, and nothing tells allies where enemies are. Packing the per-ally
   slots tighter could free a byte or two for the last enemy carrier seen (position and round).

## 4. Benchmark commands

On the team machine (`README.md` quickstart; local runs do not submit anything):

```
python -I tools/variant/b10_ideas.py                                   # make b10n, b10cap, b10home, b10lock, b10bag
powershell -File tools/cambc.ps1 build exp/b10n --release              # compile check, same for the others
python -I tools/local/multi.py exp/b10n --pool pool/vx1 --jobs 6       # bot_10 (log off) against main's source
python -I tools/local/multi.py exp/b10cap --pool pool/vx1 --jobs 6     # then each idea, compared with b10n's run
```

Item, draft and fight changes need the platform (`docs/WORKFLOW.md`), and only after the Sprint 3 lock.

## 5. Open questions

* bot_10 already assumes the killer takes the bag (bot.cpp:926, "gems are theirs if I die there"), which matches
  `docs/MECHANICS.md`. Its bank threshold of 60 was tuned under 3.0.x and is worth re-checking (`b10bag`).
* The farming and fight audits of bot_10 (`farm.cpp`, `fight.cpp`) are in progress. Their findings will be added here.
