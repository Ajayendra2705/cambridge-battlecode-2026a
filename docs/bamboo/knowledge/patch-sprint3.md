# Sprint 3 patch (announced October 26)

**Status: announced by the dev team (Eric relayed the notes on Oct 26), not yet verified.** At 22:10 UTC Oct 25 (platform clock)
our ranked games still ran engine patch `1.0.3:fcb6c3e8…` - the new maps were already in the ranked pool, the balance and item
changes were not in the engine yet. PyPI's newest cambc was 3.0.5 (installed) and the local SDK (`sdk/cpp/cambc.h`) has none of
the new emblems. Verify each number below with a probe or the new SDK once the engine ships, then move it into the tables.

## Champions

| Champion | Change |
|---|---|
| Ryth | Strength per shard 5 → 4.5 |
| Vesper Vale | Strength 55 → 45 |
| Marcella | Strength per shard 5 → 4.5; Focus per shard 15 → 14 |
| Heart of Ruin | Strength per shard 3.5 → 3; Focus per shard 12 → 10 |
| Cassi | Focus 70 → 100 |
| Issac | Strength 40 → 45 |
| Stellar | Focus per shard 7 → 8.5 |
| Prism | Health per shard 60 → 65 |
| Willow | Focus 120 → 140 |
| Ren | Stun damage (S1) 0.75x → 1.1x Focus |
| Varg | Strength 40 → 45 |
| Tavi | Stun damage (S2) 1.4x → 1.6x Focus |

Four of our five 5-pick champions are nerfed (HoR, Vesper, Ryth, Marcella); Willow is buffed. Fish's Cassi / Issac pair is buffed
and its Vesper nerfed.

## Items

- Treasure emblem: bonus gold 20% → 10%.
- Monster emblem: bonus damage to camps 10% → 15%.
- New emblems (each combines from 5 shards of the chosen stat unless noted):

| Emblem | Passive |
|---|---|
| Tribute | 33% shorter tribute, rounded up to at least one turn |
| Capture | Capture in 3 turns instead of 5 when present as the capture starts |
| Prospector | 25% more gold and gems from your share of cluster rewards, rounded down |
| Hunter | **50 extra gold per champion kill (150 a kill in all)**, before gold bonuses; linked duo deaths grant one reward (announced as 100, cut to 25 the same day - "a full emblem every kill" - then set at 50 after community feedback; final as of Oct 26) |
| Skirmish | 5% more damage to champions |
| Greed | 35 shards of the chosen stat; no passive; combines at 25 shards (750 gold) to give 35 shards' worth of stats |
| Collectors | 1% bonus damage per unique completed emblem family owned (Collectors included); shards and duplicate stat variants add no family |

What it means for the bot (to check when the SDK lands): if the new item types shift the existing `item_type` values, a bot
built on the old SDK buys the wrong items - rebuild on the new SDK before anything else. `kTreasureBuild` / `kFirstEmblem` 2
(Treasure first) lose half their value; Monster first gains. Capture (3-turn captures) changes recall-capture timing and
contested captures; Prospector fits a gold-cluster loop; Hunter adds 50% to kill gold (the kill gap, bot-status.md "The kill gap").

## Maps

Thirty maps joined the published pool (70 in all; `cambc maps pull`, Oct 26): the 15 combat maps announced with the patch -
00anvil, 00breadcrumbs, 00crater, 00dunes, 00galaxy, 00oasis, 00quarry, 00ribs, 00the-line, 00vault, adgato-gemcombat1 to 5 -
and 15 `02` maps (02arena, 02crossing, 02cuts, 02famine, 02fields, 02geodes, 02gift-wrapping, 02guardians, 02harvest,
02stalactites, 02tangle, 02the-pack, 02the-pond, 02treasure-box, 02uncharted-lands), which look like the Sprint 2 tournament
maps. No existing map file changed.

## Draft-turn fuel (SDK header change, shared by Eric Oct 26)

`cambc::fuel_remaining()`'s doc changed: **the first draft turn gets 100x the turn budget (was 10x)**; each champion's first turn
still gets 2x. PyPI still had cambc 3.0.5 when this was posted, so local runs keep 10x. Our draft turn already spends ~100-150k on the
static map plan (`draft.cpp` kDraftPlan, guarded by `fuel_remaining() > 400000`); with 100x there is room to move more of the
per-map precompute (path fields, camp-route fields, the walled-altar check) into that turn. Any such move must stay guarded by
`fuel_remaining()` so it degrades to today's behaviour where the budget is 10x.
