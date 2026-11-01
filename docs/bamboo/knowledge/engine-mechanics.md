# Engine mechanics (verified)

Behaviour confirmed by probe bots, replays or the SDK, including where `GameRules.md` is wrong or silent.
Dates are 2026-10 UTC. "Probe" means a purpose-built test bot on a purpose-built map.

## Targeting and aggro

- **Monsters hit the nearest champion** (Chebyshev distance). **Ties go to whoever acts first in the turn order.**
  Who attacked the monster, who hit it last, and who it was already hitting do not matter. (Probe Oct 20,
  `bots/AggroProbe`: with two champions adjacent to a wolf, the later-acting one attacked alone for 6 rounds and the
  wolf kept hitting the earlier one; stepping back to distance 2 moved aggro the next round.)
- **Dashes do not reset aggro (probe Oct 28, engine 2.0.0, `bots/AggDash`, 02uncharted-lands, both sides alike):** Vendetta (priority 100)
  and Vesper (priority 1) beside a lone wolf: Vendetta took every hit; Vendetta dashing to another tile still beside it and attacking,
  then Vesper doing the same, changed nothing; Vendetta dashing out to distance 2 moved the hits to Vesper the next round. Aggro is
  re-chosen every round from distance, then turn order; a dash matters only when it changes who is nearest. Dash + basic attack in one
  turn works (an ability does not use the attack).
- **A monster's hit is exactly its strength** (× 0.9 with a Durability emblem, × 0.7 with Jungle), once per round, to
  the nearest champion: wolf 20, elk 60, monolith 200. In 80 ladder games (v190, Oct 20) every round of camp damage to
  a party of 2–6 of ours went to a single champion: the damage is never shared within a round.
- **Leaving reach costs reach − distance hits:** the monsters' step comes after the champions' turns, so walking
  straight out from distance d takes a hit after every step still inside. From beside a monolith that is 4 × 200 = 800,
  an elk 3 × 60 = 180, a wolf 2 × 20 = 40. Monsters never chase.
- **Priority sets that tie-break.** Turn order within a team is priority, then draft order; `set_priority` takes effect
  from the next round. With `set_priority(50)` on the later champion, it took every hit (`bots/AggroProbe2`).
- Teams alternate within a round: team A acts first in odd rounds (round 1), team B in even rounds.
- Monsters see through bushes, do not chase, and **hit back through walls**: a woken wolf behind a wall hit its
  attacker every round (probe Oct 20, `bots/WallProbe2`).
- **Damage to any member wakes the whole node, clusters included.** Ryth hit only a gem cluster beside a wolf; the
  untouched, full-health wolf woke and hit him every round he stayed in its reach, also after the cluster died (probe
  Oct 20, `bots/WakeProbe`; user's report). Varg's splash also damages monsters beside his target. An awake group sleeps
  after two rounds with no champion in reach. The same holds for a monolith whose group contains clusters (01gold_rush:
  chipped clusters woke the full-health monolith, Oct 21). **The SDK reports the real state:** `camp::is_awake()` /
  `is_asleep()` (via `camp::state()`) for any visible camp, so bots need not infer it from health (`kTrueWake`).

## Vision and attacks

- **Attacks need vision, not a clear line.** A ranged champion hits an enemy behind a wall (basic attacks and damage
  spells) once its own ward sees the target. The melee enemy on the other side could never answer (probe Oct 20,
  `bots/WallProbe`). Holes never block sight.
- **Ward placement ignores walls:** the placement area is the full Chebyshev-2 square, wall tiles included (placing
  *on* a wall may throw), so a ward can sit over a one-tile wall. Wards are permanent and undamageable. Since the patch
  a ward can be placed only every 10 rounds.
- **Enemy wards in our vision are visible:** `cambc::vision::wards(team::enemy)` / `ward_tiles(team::enemy)` /
  `ward_at(p, team::enemy)` list them from the turn after placement, and `cambc::ward::visible_tiles_from(p)` gives
  what a ward at `p` sees (probe Oct 20, `bots/WallProbe3`).
- **Any damage cancels a recall** (Eric, Oct 30). A recall under fire cannot finish: break line of sight first (a bush the attacker is
  not in and has not warded), then recall. Stuns cancel channels too; Marcella is stun-immune but not damage-immune.
- **Bushes:** nobody outside a bush sees into it; a champion inside sees its whole (connected) bush and out of it. So a
  tributer in a bush beside an altar is hidden unless an enemy or enemy ward is in that bush. A teammate standing in a
  bush is invisible to a mate outside it (`roster[i].position()` throws), so squad counts by position flicker.

## Movement

- **Dash + step + attack in one turn** for melee champions: a ready dash (2) + step (1) + reach (1) hits an enemy 4
  tiles away. Ranged champions share one allowance for moving and attacking: a ranged champion that steps cannot shoot
  or cast a damaging spell that turn, so its threat is only its range from where it stands.
- **A dash walks its steps (Oct 28, edit_ruincamp.py probe, 140 games):** `valid_tiles()` lists every tile within the dash range, but a
  2-tile landing whose middle tiles all hold a live monster (or an enemy champion) is refused with engine error 32 "Destination is
  unreachable within movement range" (987 of 2,977 HoR camp landings). Nothing is spent on a refusal; try the next landing.
- Dashes cross holes, not walls. One-tile hole gaps (a hole with walkable tiles on opposite sides) are dashable
  crossings; a 2-wide hole line is not.
- **Live monsters block walking.** Allies do not (you can walk through allies but not land on them); only units you
  can see block a landing. Distance fields built on walls/holes/altars route *through* live camps, so a camp filling a
  passage stalls champions on its face unless the field blocks camp tiles.
- Teleport crystal: a move and then the channel start in the same turn is legal; the channel ticks at turn ends
  including the start turn; the hop lands at the start of our turn and the turn stays full (Issac: 3 hop + 2 dash + 1
  step = 6 tiles in the landing turn).
- `spawn_region()` returns the spawn bounding box; only the tiles champions start on heal and shop. Team A fills its
  box from low y, left to right; team B is the map-symmetry image.

## Spells and reach

- Area spells (Stellar/Prism/Ryth: range 4, radius 1) aimed at a tile beside the target hit champions 5 tiles away;
  single-target spells reach 4.
- **Ability kinds as the SDK reports them** (probe Oct 23, cambc 3.0.5, `bots/AbProbe`: each champion printed its
  abilities' kind flags and payloads on its first turn). **Ryth's area stun is `aoe_damage`, not `cc`** (radius 1,
  duration 1, modifier 1, targets ground, enemies and camps, excludes walking), so code that looks for stuns with
  `is_cc()` never finds it: `kKiteStun` bit 1 never cast it (fixed behind `kKiteAoe`, off: −24 ± 25 locally), while
  `kAoeReach` (which needs `is_aoe_damage()`) does apply to it. `ability_cc` has no radius field.

  | Champion | Slot 0 | Slot 1 |
  |---|---|---|
  | Cassi | damage, enemies/camps, range 4, ×2, excl | cc, enemies/camps, range 4, 1 turn, ×0, walking OK |
  | Issac | (no payload) | dash 2, radius 0 |
  | Stellar | damage, range 4, ×2, excl | aoe_damage, ground/enemies/camps, range 4, radius 1, ×1.4, excl |
  | Varg | (no payload) | range 4, ×2.5, 5 turns, no targets (shield) |
  | Ryth | aoe_damage, ground/enemies/camps, range 4, radius 1, 1 turn stun, ×1, excl | (no payload: attack reset) |
  | Ren | cc, enemies/camps, range 4, 1 turn, ×0.75, excl | dash 2, radius 0 |
  | Willow | range 4, ×3, no targets (heal) | (no payload) |
  | Vendetta | (no payload) | dash 2, radius 0 |
  | Prism | cc, enemies/camps, range 4, 1 turn, ×1.5, excl | aoe_damage, ground/enemies/camps, range 4, radius 1, ×1, excl |
- **Monster reach after the patch:** wolf 3, elk 4, golem 4, monolith 5 (SDK and replay state, Oct 20). Before the patch
  the monolith reached 3 in the engine despite the handbook's 5.

## Economy and timers

- Spawn healing is **full in one turn**. Respawn is a fixed 60–61 rounds.
- A tribute lasts max(1, ceil(gems/10)) turns; only stun, death or an altar lock stops it (damage does not).
- **Tribute range is 1** (`constants::submit_gems_range`; verified Oct 21 on a ranked 01boss_battle win: all 145 tribute
  rounds were from (24,20), distance 1 from the altar at (25,20)). There the altar's only non-wall, non-hole neighbour is
  the boss's own spawn tile, so it can be tributed at only while the boss is dead - any plan that walks to that altar with
  the boss alive stands beside it for nothing (the bot's `kBankUsable` fix, Oct 22).
- Gold bonuses add: Treasure emblem 20% + Vesper Vale's passive (33% since the patch). A second emblem of the same family
  adds stats but no second passive.
- Settings (cambc 3.0.1): 2000 rounds, 1000 gems to win, kill gold 100, assist gold 0, passive gold 0, ward cooldown
  10, ward lifetime unlimited, ward vision 6.

## Priority is a 32-bit broadcast (Eric, Oct 23; probe `bots/PrioProbe`)

`champion::set_priority(int32)` stores a value that `champion::priority()` (next round's) and `prev_priority()` (this round's) read
on **any visible champion, ally or enemy**. Probe (cambc 3.0.5, 00contest, each champion set 1000·round + 10·slot + team each
turn): a value set this turn is read by every mate acting later in the same round as `priority()` and by everyone next round as
`prev_priority()`; enemies in vision read both too (Fish sets 0/−1/−2: turn order only). It also sets the team's turn order
(higher first), so data must live in the low bits under the intended order, or the order follows the data. The replay state
carries `priority` / `nextPriority` per champion. Use: per-champion state for mates in sight (target, intent, a rally tile,
an enemy sighting) without the 8-byte shared memory; and reading an enemy team's values if it encodes anything there.
Who uses it (Oct 23 ranked replays, `results/review20261023/replays`): **:3 broadcasts data** - top nibble a fixed rank per
champion (HoR 5, Vendetta 4, Vesper 3, Marcella 2, Prism 1 = turn order), low 16 bits two team-wide countdowns (multiples of 8
and 4, both falling by 2 a round, identical on every member, re-set each round; semantics unknown); procless fixed per-champion
values (40/55/65/80/1000 and 96-100), Fish 0/−1/−2.. (aggro order); we 0 everywhere. Nobody decodes ours, so a per-champion
broadcast of ours is safe; reading :3's clocks would need their meaning.

**What the top 10 put there (Oct 27; 67 top-10 bench replays of #388, `scratchpad/prio.ts` + `priosum.py`; the replay state is
omniscient, our bot reads the same word only on enemies in vision):**

| Team | Word | Decoded |
|---|---|---|
| Ad Astra | `0x0T0S0LLL` | T turn-order nibble (Vesper 13, HoR 12, Marcella 11, Ryth 10, Varg 7); S (bits 16-18) intent: 1 farm (61%), 2 fight at the camp, 0 go bank / tribute (94% carry gems), 4 recall home, 3 / 5 chase or fight a champion (enemy within 5 in 96% / 74%); L (bits 0-11) the target camp group id under 1/2, a tile under 3/5 |
| Trzy Kwaterki | bits 10-16 / 5-9 / 0-2 | missing health % / a fixed per-champion id 27-31 (turn order) / state: 1 farm, 2 to the altar (100% carry gems), 4 home, 5 fight (enemy within 5 in 81%), 6 enemy near (38%) |
| Mite | number | 1000 + health / 50 while farming (healthier acts first); ~94-98 when engaged (73% enemy within 5); 0 otherwise |
| NEETCoders | signed number | per-champion turn order (35-60) negated in fights (45% vs 7% enemy within 5) |
| Fish | -1 / -2 / -3 ... | **minus the health quartile** (-1 above 75%, -2 50-75%, -3 25-50%, -4 below; a solo Vesper -6..-9 = the same offset by 5): the healthiest of equally near champions acts first and soaks the camp hit (9644b4dd: 34 of 50 tied hits; Oct 27). 0 / 1 / 3 / 4 in fights |
| prism best girl, willow best girl | signed | negative while carrying gems (71% / 68%); willow's high half is a 16-bit flag-like field, not decoded |
| print dont int / Claudus / Sponge | 96-100 fixed / 0 ±1 / rare 1000 | turn order only |

Nothing in them is hidden from vision except intent (enemy `gem_count()`, health and channels are readable directly), the formats
differ per team and can change before the knockout, so reading them would be per-opponent hardcoding; not used.

## Bot API

- Shared memory is 8 bytes (0–7); access past 7 throws. Draft memory is 1,024 bytes; champions are fresh instances
  after the draft, so draft memory is the only channel. Every map query works during the draft.
- Fuel is about 1 per WASM instruction at -O3: bitboard/distance-field accessors ~40–50, malloc+free 200–385,
  `std::map` insert+destroy ~690, a 13x13 flood fill ~15–30k. A turn has ~100k; overruns lose turns.
- `cambc::round_number()` can lag after a fuel suspension inside a turn.
- `ability_dash` (SDK 3.0.1) has `range` plus landing `radius`, `modifier` (damage = Focus x modifier) and `duration`
  (stun), used by Heart of Ruin.

## Tooling facts

- Local games are deterministic and builds are byte-identical, which is what `tools/evaluatec.sh` caches on.
- `cambc matches download <id>` works for any team's match. `cambc match-groups create` (3.0.1) needs `--json` and
  prints compact JSON. Teams whose submission no longer compiles are out of matchmaking (HTTP 409 "no eligible bot").
- Replay state: `channelType` 1 recall, 2 tribute, 4 teleport crystal; buff type 0 shield, 1 stun, 2 enhanced attack.
  Champions carry `earnedGold`, `treasureGold` (gold from the Treasure passive) and `items` (counts by `item_type`
  index: Treasure emblems are 19, 21, 23).
- `cambc run-batch` plays the same games as `cambc run` (same winner and final round) at the same speed per game.
- Map builder (engine exports `MapBuilder_*`): symmetry 0 mirrors x, 1 mirrors y; the spawn box is half-open
  (x0,y0,x1,y1); a 3x2 box was rejected as malformed, 3x3 worked.

## Instances, memory and the recall pre-start (probes, Oct 24)

- **Each champion runs in its own WASM instance.** `bots/InstProbe`: a global counter rises by exactly 1 a round in each of the
  five champions, so globals are never shared within a team. Writable team memory is the 8-byte `shared_memory`
  (`shared_memory_bytes` from the game settings). Draft memory (1,024 bytes) is readable all game but **frozen after the draft**
  (`invalid_action_memory_draft_frozen`); the in-game copy is a startup snapshot. Other team channels: each champion's 32-bit
  priority word (readable by anyone who sees it), and draft memory as a precomputed plan (the draft's first turn has 10x fuel).
- **A recall started at the end of a turn counts that turn's end.** `bots/RecallProbe` on 00expanse: a champion that moved in
  round 10 and called `recall()` at the end of round 10 was home at round 15; one that called `recall()` at the start of round 11
  was home at round 16.
- **Cancelling a recall at the start of the next turn is free:** after `cancel_recall()` the champion moved a full step the same
  turn, six turns in a row, and could start a new recall at that turn's end (one recall start and one cancel per turn:
  `invalid_action_recall_already_used`, `invalid_action_cancel_channel_already_used`). So "pre-start a recall every turn end,
  cancel next turn unless you want it" saves one round on every recall that is not timed to a capture. Caveat for teams that
  read allies' `is_recalling()`: a pre-started recall stays visible to teammates acting later in the round.

## Melee move + attack (Eric Oct 26; handbook line 105, confirmed in the fish-five v366 traces)
- Melee champions may walk and basic-attack in the same turn, in either order: both teams' HoR / Ryth / Marcella / Vendetta
  show "attack then move" and "move then attack" turns. Ranged champions share one allowance for walking and basic attacks
  (an attack reset restores it: kMoveReset).
- Melee turns that combined a move with an attack, ours vs Fish's: treasure_box HoR 33 vs 105, Marcella 40 vs 67; anvil
  Marcella 37 vs 69, Ryth 51 vs HoR 89. Move-only melee turns ending beside an enemy champion in the five games: ours 44,
  Fish's 6 (scratchpad check on trace.json: next-round positions); starting beside one and leaving without a hit: 36 vs 28.
- Our code attacks around a step only in camp fights, chases, assists and escape() (strike_while_escaping); kMeleeFree
  (edit_meleefree.py, bots/B377x, off) adds a turn-end free hit and a hit before retreat / outnumbered steps.

### Contested captures (Oct 27, ranked 117214ce vault + GameRules)
- A capture needs the group's spawn tiles held **uncontested**: one enemy on any spawn tile of the group resets the capturing team's
  5-round timer (GameRules "Leaving the region empty or admitting an enemy resets progress"). `camp_group::capture_state()` returns
  {timer, state}: 0 no capture available, 1 ally capturing, 2 contested, 3 enemy capturing, 4 capture available (needs the group in
  vision, not the champions). Big multi-member groups (vault: 49 clusters) go to whoever kills the last member and stands on a tile -
  damage dealt earns nothing.
