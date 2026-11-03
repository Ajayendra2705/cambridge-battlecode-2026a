# MASTER SHEET - everything we know (Cambridge Battlecode 2026a, team Bamboo Teahouse)

One sheet to read first and keep current. It collects the verified game facts (including engine behaviour the competition
docs never state), the platform and tooling facts, how we test, what the top teams do, what our live bot is, what we
tried, and Eric's standing rules. Each section names the file with the full detail. Last full revision: **Oct 27 2026
~00:00 UTC** (engine 2.0.0, live bot #392).

**Trust order for a game fact:** this sheet and `.info/knowledge/*.md` (verified by probe, replay or the SDK) > the SDK
header `sdk/cpp/cambc.h` > the handbook `.info/GameRules.md` (pre-patch text, corrections marked). When something here
turns out wrong, fix it here and in the detail file the same day; never delete silently - mark it outdated with the date.

---

## 1. The goal and Eric's standing rules

- **Goal: win the Sunday Nov 1 2026 knockout** - a 15-map series on NEW hand-made maps (pool-like style, unseen layouts).
  Judge changes by series wins on unseen maps; gem margin on known maps is diagnostic only. Gate on wins, not margin.
- **No map hardcoding.** No map-name checks, no per-map constants, no thresholds eyeballed from one map. Rules come from
  what the bot reads off the layout at draft/set-up (spawn walk, camp values, midline, holes). Map-type rules decided at
  the draft ("farming / fighting / small / big / barren / rich") are the endorsed form.
- **Version numbers:** `kBotVersion` = the platform submission number (`cambc submit` prints "Submitted bot version N").
  Upload copies are `bots/Up<N>`; bench tags `top<N>`.
- **Benches are against the current top 10** (rebuilt from `cambc ladder`); 3 min after an upload the build is ready,
  3 min after queuing the results are out - read them at once, never block on replay downloads.
- **Screens:** one precise change per arm against the retained base; when a switch adds a computation, screen base /
  compute-only / decision (judge the decision against the compute-only control). Quote the run directory.
- **Git:** commit or push only when Eric asks; push only to `bamboo8`; never `git add -A` blind. Commit trailer:
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the model name in use).
- **Data hygiene:** delete only regenerable data (`results/ev`, replays); never `rm` a relative glob after `cd`; never edit
  a script a running screen is using; prune `results/ev` (it filled the disk once).
- **Codex collaboration:** Codex writes `collaboration/codex-to-claude.md`, Claude writes `claude-to-codex.md` (ids C###
  / A###). Codex owns the shared-memory / priority / draft-plan protocol layout; Claude owns bot copies, screens, uploads,
  adoption and the knowledge notes. Text Eric pastes in his messages is Codex's suggestion unless he says otherwise.
- **Fuel is always a concern:** +10k fuel a turn costs ~-33 locally, +28k -242; profile anything per-group on
  01yellow_brick_road (30-member groups). Decision-preserving edits are proved by identical games under
  `--fuel-quantum 200000000` (`tools/stress/eqcheck.ts`).
- Eric's vocabulary (node, backing, offering, cheese, autos, void, waves, overtime, rotation aggro): `glossary.md`.

## 2. Platform, toolchain and data

- **CLI:** `%LOCALAPPDATA%/cambc/bin/cambc-4.0.0.exe` (engine 2.0.0 = the ladder since Oct 25 22:52 UTC; local screens match
  the ladder). Older exes 3.0.4 / 3.0.5 kept for old replays. Repo `sdk/` refreshed with `cambc init --yes .`.
- **Commands:** `build <bot>`, `run A B --map M [-o dir] [--statistics f.json] [--rounds N]`, `run-batch --jobs N`,
  `submit <bot>` (session lasts 7 days), `submissions list` / `submissions activate N` (pins the live version; activating an
  old one rebuilds it, minutes; `activate latest` does not unpin - activate the number), `maps pull --force`,
  `maps list --page P --limit 50` (70 maps; ladder names use underscores, files hyphens), `ladder --json`,
  `matches list --team ID --kind ranked --limit 25 --json`, `matches download ID` (any team's match, signed in),
  `matches summary` (cached per match in `results/sum/<id>.json`: per-champion metrics, item buys, timelines, events).
- **Rate limit:** the CLI returns HTTP 429 when called in quick succession - retry after a few seconds.
- **Replay bundle (`.repl26a` = zip):** `replay.repl26a`, `team-a/b.stdout` (NUL-padded; our `std::cout` and the
  `BAMBOO vN` banner), `team-x.debug`, `team-x.fuel` (13-byte header, then u64 LE fuel per champion turn; 100,000 = a capped
  turn, 10,000,000 = draft turns). `tools/replay_engine.ts` (Deno) walks the state; `tools/stress/extract1.ts` writes
  `trace.json` (rounds, champions, actions kind 4 move / 5 attack / 6 cast / 23 blocked move, camp damage, income, recalls).
  Replay state: `channelType` 1 recall, 2 tribute, 4 crystal; buff 0 shield, 1 stun, 2 enhanced attack; champion
  `priority` / `nextPriority`; `items` counts by `item_type` index.
- **Item ids:** `family x 6 + stat x 2 + emblem` (families monster, power, durability, treasure, jungle, home, bruiser,
  tribute, capture, prospector, hunter, skirmish, greed, collectors; stats str, foc, hp; emblem bit = combined).
- **Public API (no login):** `/api/v1/ladder`, `/api/v1/match-groups?team=ID`, `/api/v1/match-groups/<id>` (matches and
  official stats). Scrim quota: a rolling 60-minute window of 50 groups (5 maps each).
- **Determinism:** local games and ladder matches are deterministic per (our submission, theirs, map); builds are
  byte-identical (screens cache on source hashes). A baseline needs re-running only when an opponent resubmits or the
  engine changes. Troll submissions exist (a team once gave 20/20 free wins): bench only against the top 10.
- **Fuel:** ~1 per WASM instruction at -O3; a turn has ~100k, the first draft turn 100x (local 10x on old CLIs), each
  champion's first turn 2x. Costs: bitboard / distance-field accessors ~40-50, malloc+free 200-385, `std::map`
  insert+destroy ~690, 13x13 flood fill 15-30k. Overruns lose turns; `round_number()` can lag after a suspension.

## 3. How we test (detail: `tools/SCREENING.md`)

- **Local screen:** `MATCH_TIMEOUT=900 SEEDS="1 2 3" OPP="PoolLive PoolCarry PoolAggro" python tools/fastscreen.py BASE 'edits' BASE 'edits@@s/old/new/' ...`
  (always set MATCH_TIMEOUT: on Oct 27 one hung match blocked a screen for 90 minutes and could not be killed from the sandbox;
  `tools/stress/salvage_screen.py` recovers a stuck run from its statistics files)
  (Oct 27: the old H340 / B7Live pool did not predict the ladder - it ranked the kept #392 worst; the new pool = live config, a fed-carry
  variant and an aggressive variant tracks it better; refresh bots/PoolLive when a version goes live)
  on the 70-map pool, paired against C1; edits are literal `s/old/new/` substitutions joined by `@@` (`tools/apply_edits.py`,
  falls back to `draft.cpp`). One screen at a time (`results/ev/.screen.lock`). 840 games an arm (3 seeds) resolve about
  +-10; confirm anything selected on fresh seeds (winner's curse is real: a +19 became -4). `ROUNDS=800` is a fast reject
  filter only (late gains are invisible; re-checked Oct 27 on the new pool: right sign on 3 of 3, missed one -40 loser; needs
  `kReportRound` - `tools/edits/edit_report.py`, in B411x+; drop an arm at z below -2 on seed 1, confirm the rest in full games). Opponents are our own code: farming faults we share are invisible - check income
  against the top teams' own games too.
- **Candidate edit files:** `tools/cands/cand<N>.edits` (the exact switch list of each upload on its `bots/B###x` source).
  Live chain: `cand389.edits` on `bots/B396x`.
- **Ladder test:** `STUCK_CASES=8 STUCK_ROUNDS=120 sh run/ladtest.sh N SRC EDITSFILE "note" top<prev>` (stress check on
  unseen terrain, upload, sleep 180, activate N, queue `bench_top10.txt`, print the per-game table against the previous
  tag), then `sh run/bigbench.sh top<N>` (`bench_top10r.txt` = the same 50 maps vs another top-10 team with sides flipped,
  `bench_hold10.txt` = 20 held-out maps x 2 teams). The **140-game panel** is the regression check; a single 50-game bench
  swings +-5k / +-4 wins from fuel-driven divergence. Scripts and bench lists: `tools/cands/` (copies of the scratchpad
  `run/` and bench files; they hardcode the scratchpad path `SP`).
- **Probes with bot stdout:** `LOGS=1 CAMBC=<4.0.0 exe> python tools/stress/localrun.py BOT PoolLive OUTDIR maps...` (run-batch; bundles keep
  team stdout). fastscreen passes `--log-limit 0`: no stdout in its bundles. A plain `cambc run` of an edited bot is NOT a valid harness
  (Oct 28: 22-1012 with and without the change). Kill a background script from its own Bash call with a pattern that cannot match the call
  itself (`s_pair[s]\.sh`), never in the call that relaunches it.
- **Pinned opponents (Eric, Oct 28 23:55):** `cambc match-groups create TEAM --source-group <previous group id> --maps ...` plays the opponent's
  EXACT bot of that earlier group. `bench2qs.sh TAG SPEC SRCTAG` queues SPEC against the groups of scrim_SRCTAG.ids line by line: the same
  maps, sides and opponent versions on a deterministic engine = exact pairs with the stored baseline. No same-time baseline bench needed
  (that halves the scrim cost and removes the hourly drift); keep the baseline's ids files (scrim_top405t.ids, scrim_fish405c.ids).
- **Pinned 140-game panel (Oct 29):** `panel.sh queue TAG` replays four stored #405 benches against the same opponent bots (top-10 50, two
  Fish set groups 40, random-map x1 50: tags TAG_top / _f1 / _f2 / _x1); `panel.sh cmp BASE CAND` sums wins and margin over the same games.
  Base = p418 (#418). 28 groups a candidate. **Since Oct 29 11:00 (Eric): panel125.sh / ladpanel125.sh** - the random-map bench cut to its
  first 7 groups (bench_x1r / x1r_405; baselines' first 7 ids as TAG_x1r): 25 groups = 125 games, two candidates an hour.
- **Always verify the banner** (`BAMBOO vN` in the downloaded stdout) and the engine version before comparing benches.
- **Stress maps:** `maps/sprint_1_hs_*` and `fx_*` (corridors, hole pockets, rooms, disconnected spawns, 64-256 groups);
  the live code wins 41/42 there with 0 faults.

- **Panel noise (Oct 29):** identical behaviour reproduces the panel (#435: 0 of 125 results flipped); any behaviour change makes each game it
  touches a fresh draw, so a frequently firing feature faces ~+-5 wins of 125 - only large effects are signals; local wins (pool = our own
  bots) repeatedly failed to carry (s_all2 +25 -> #433 / #436 below #428). **Runtime-eval harness** (edit_rteval.py): candidate features read
  bits from draft byte 15, OFF / ON builds differ only in the draft's publication (8 bytes of wasm); 34 of 40 local paired games stay
  byte-identical for a rarely firing feature - pairing helps rare triggers, not frequent ones.

## 4. Engine behaviour beyond the docs (verified; detail and probes: `engine-mechanics.md`)

**Aggro and camps**
- An awake monster hits the **nearest champion (Chebyshev)**, once a round, for exactly its strength (x0.9 Durability,
  x0.7 Jungle); ties go to **whoever acts first in the turn order** (priority, then draft order). Who attacked or hit last
  never matters. Damage is never shared within a round. Monsters never chase.
- Leaving reach from distance d costs (reach - d) hits: beside a monolith 800, an elk 180, a wolf 40.
- **Fish shares camp hits through that tie** (copying it lost -31 to -72 in every form for our one-tank comp, Oct 27): priority = minus the health quartile, so the healthiest adjacent champion soaks;
  hurt melee dash from distance 1 to 2-3 and a fresh mate dashes in. Ours keeps the draft order (HoR soaked 66%). `kAggroShare` (B409x).
- **Damage to any member wakes the whole group, clusters included** (gold_rush's monolith wakes from a cluster chip);
  an awake group sleeps after two rounds with nobody in reach; `camp::is_awake()` reports the real state.
- Monsters see through bushes and **hit back through walls**. Reach: wolf 3, elk 4, golem 4, monolith 5.
- Reward goes to the allies on the capture tiles (lowest id gets the remainder); groups respawn together.
- **An enemy on any spawn tile of a dead group resets the capture timer** (contested); `camp_group::capture_state()` shows
  enemy_capturing (3) + timer. Killing most of a big group earns nothing - the team on its tiles at the end captures (vault, Oct 27).
- Teams alternate within a round (A acts first in odd rounds). Turn order within a team = priority, then draft order.

**Vision, wards, bushes**
- **Attacks need vision, not a clear line:** with a ward over a wall, basic attacks and spells hit through it and the
  melee enemy behind cannot answer. Holes never block sight.
- Ward placement is the full Chebyshev-2 square, walls included (a ward can sit over a one-tile wall or inside a boss's
  reach); wards are permanent, undamageable, one per 10 rounds. Enemy wards in our vision are listed by
  `vision::wards(team::enemy)`; `ward::visible_tiles_from(p)` gives a ward's view.
- Nobody outside a bush sees into it; inside you see the whole connected bush. A teammate in a bush is invisible to a mate
  outside (`position()` throws) - keep last-seen mate positions for counts.

**Movement and turns**
- Melee: **walk and basic-attack in the same turn, either order**; a ready dash (2) + step + reach hits 4 tiles away.
  Ranged champions share one allowance for moving and shooting/casting damage (an attack reset restores it).
- Dashes cross holes, not walls; a 1-hole gap is dashable, a 2-wide hole line is not. Live monsters block walking; allies
  can be walked through but not landed on; only visible units block a landing. Distance fields must block live camp
  tiles or champions stall on a camp's face.
- Teleport crystal: move then start the channel in one turn; lands at our turn start with a full turn (Issac: 6 tiles).
- `spawn_region()` is the bounding box; only the start tiles heal (fully, in one turn) and shop. Respawn is 60-61 rounds.
- **Recall pre-start:** a recall started at a turn's end counts that turn; cancelling at the next turn's start is free
  (one start and one cancel a turn). Four top-10 teams (Mite, willow best girl, NEETCoders, print dont int) pre-start a
  recall every turn end: during our turn they show `remaining_channel_time` 4 (2 with a Home emblem) and "cannot cast".
- **A dash may not land on the caster's own tile** (engine error 32 "Forbidden landing tile", although `valid_tiles()` lists it;
  probe Oct 27). To dash-hit an enemy whose only free neighbour is our tile: step off, then dash back onto the vacated tile.
- A tribute lasts max(1, ceil(gems/10)) turns from range **1**; only stun, death or an altar lock stops it. Altar lock HP 5.

**Spells (SDK ability kinds)**
- Area spells (Stellar, Prism, Ryth: range 4, radius 1) aimed beside a target hit 5 tiles away; single-target reach 4.
- **Ryth's area stun is `aoe_damage`, not `cc`** (`is_cc()` never finds it). Cassi S1 cc (walking OK), Ren S0 cc, Prism S0 cc;
  Varg S1 shield 2.5 x Focus 5 turns; Willow S0 heal 3 x Focus; attack resets (Ryth S1, Vendetta S0) carry no payload;
  dashes (Issac, Ren, Vendetta, Vesper) range 2 radius 0; HoR S1 dash range 2 with landing damage 1.75 x Focus and a 1-turn
  stun within 1 (`ability_dash` has range, radius, modifier, duration).
- Gold bonuses add (Treasure + Vesper's passive); a second emblem of a family adds stats, no second passive.

**Team channels**
- Each champion is its own WASM instance (no shared globals). Shared memory is **8 bytes** (past 7 throws). Draft memory
  1,024 bytes, written in the draft, **frozen after it** (the draft's first turn has 100x fuel: precompute the map plan).
- **Priority is a 32-bit broadcast:** `set_priority(int32)` is readable on any visible champion (ally or enemy) via
  `priority()` (next round) / `prev_priority()`; it also orders the team's turns (higher first). What the top 10 encode
  (Oct 27, decoded): Ad Astra intent + target camp, Trzy Kwaterki missing-health % / id / state, Mite 1000 + health/50,
  Fish / NEET / prism / willow turn order with fight or gem-carrying signs. Only intent is new over vision and formats are
  per team: not read. Nobody decodes ours.

## 5. Game numbers on engine 2.0.0 (Sprint 3 balance; detail: `patch-sprint3.md`, `patch-2026-10-20.md`)

- Settings: 2,000 rounds, 1,000 gems to win, kill gold 100 (+50 with a Hunter emblem), assist gold 0, ward cooldown 10.
- Camps: wolf 1350 HP / 20 str / reach 3 / 4 gems 40 gold; elk 2400 / 60 / 4 / 15 gems 90 gold; gem cluster 120 HP 7 gems;
  gold cluster 120 HP 20 gold; monolith 20000 / 200 / 5 / 200 gems 300 gold; golem 5000 / 120 / 4 / 36 gems 160 gold.
- Items: Treasure +10% gold (was 20), Monster +15% camp damage, Jungle -30% camp damage taken, Durability -10%; new:
  Tribute (33% shorter tribute), Capture (3-turn captures), Prospector (+25% cluster rewards), Hunter (+50 kill gold),
  Skirmish (+5% to champions), Greed (35 shards of stat, no passive), Collectors (+1% per emblem family). 5 shards = 1 emblem.
- Champions (2.0.0 per-shard nerfs: Ryth str 4.5, Vesper base str 45, Marcella str 4.5 / foc 14, HoR str 3 / foc 10; buffs:
  Cassi foc 100, Issac str 45, Stellar foc 8.5/shard, Prism hp 65/shard, Willow foc 140, Ren stun 1.1x, Varg str 45, Tavi
  stun 1.6x). HoR: 1000 HP, 100 Focus, passive up to +50% damage with missing health, S0 shield 1.5 x Focus 5 turns, S1 the
  dash. Vendetta: kills (camps too) reset both cooldowns; S0 attack reset, S1 dash, 8-turn cooldowns, 1000 HP. Vesper:
  +33% gold, dash. Marcella: stun-immune, 2 gold per gem tributed. Ryth: bonus health adds strength. Prism: Focus per carried
  gem. The bot reads live stats; no number above is hardcoded.
- Champion enums differ between `champion_draft` (Cassi&Issac share a pick) and `champion_type` (`champions.md` table).

## 6. Maps (detail: `camps-and-maps.md`)

- Pool: **70 maps** (00*, 01*, 02*, adgato-gemcombat1-5); local files from `cambc maps pull --force`. The knockout uses new
  hand-made maps: everything must generalise.
- Our layout classes (computed at set-up, same for every champion): **farming / race map** = spawns more than 45 path steps
  apart (`kRangedSteps` / `kControlDist`); **control map** otherwise; close spawns = 16 steps or fewer. Spawn walks: rushbait
  ~2, swirl 13, fragment 23, collision 34, corners 40, interlock 41, eight 46, monolith 49, lanes 81, expanse 85,
  pilgrimage 123. Boss maps = gems in huge camps (monolith shares: contest 100%, monolith 76%, gold_rush 75%, corridors 57%,
  big_world 55%, broken_curve 54%, fracture 47%, boss_battle 34%). Scaling maps (long games) get Treasure-first builds.
- Team sizes on the pool: mostly 5v5 (27 of the 50 bench maps), 4v4 6, 3v3 8, 6v6 2.
- Layout facts worth remembering: boss_battle's two monoliths side by side at the centre (400 a round to the nearest once
  woken; Fish baits beside them asleep); gold_rush's monolith group holds its 24 clusters; eight's altar inside a bush ring;
  elk_arena's altars have bushes; shortcut's spawn rooms open through a hole row (dashable); yellow_brick_road's two
  30-cluster rows (fuel); starfish's altars in a central bush pocket.
- **Map weighting result:** only the whole-team opening length is layout-dependent at our sample sizes (race 240 rounds,
  control with spawns > 16 apart 180, else 120: +29 +-9, out of sample). Per-category economy weights gained nothing
  (+0.2 +-8.5 a map at 16 games/map); single-feature gates were worse than none.

**Camp limit test (Oct 27, `bots/LimitBot`, 448 games, bot-status.md):** a 2-elk node (2 elks + 2 gem clusters) needs **3 champions
with no items** (any 3 of our pool: 32 rounds, 63% health left), 2 once both hold 2 emblems and one is HoR or Ryth; 4 bare take 25 rounds,
5 bare 22 - champion-rounds per clear 96 / 100 / 110, so the 5-stack is the least efficient. Chaining a second node without healing: 3 bare
43%, 3 with one emblem 86%, 4 bare 94%.

## 7. The top teams on engine 2.0.0 (detail: `champions.md` "Top-10 builds and kit use", `bot-status.md` Oct 26-27)

- Top 10 (Oct 27 23:30 UTC): Intercontinental Fish, Trzy Kwaterki, Mite, willow best girl, Claudus Maximus, prism best girl,
  NEETCoders, Ad Astra, Sponge, hello (Supaswag 11, print dont int 12; we are 57 at 1,923). The bench lists (`tools/cands/
  bench_top10*.txt`) still hold the Oct 26 ten - rebuild them from `cambc ladder` before the next ladder test.
- **Play-style percentiles among the top 20 + us** (radarnow.py, 27 Oct; dashboard "Ladder Team Profiles"): KDA 60, Trade 80,
  Gank 20, Outplay 44, Gold 65, Farm eff. 65, Vision 55, **Farm 25** - early kills and camps per 100 rounds are the gaps. Every one drafts HoR; Vendetta is in 5 of the 10's lists; Vesper and Marcella
  everywhere; Willow only Supaswag / willow best girl; Prism only prism / willow best girl.
- **Where they beat us (140-game panel of #388, by r600):** gold 3,100 vs 2,015 a game (their Vesper 32% of it, ours 22%;
  our Ryth 25%, theirs 5%); kill gold 620 vs 190; captures 31.1 vs 22.7; effective strength 101 vs 67; deaths 6.2 vs 13.4
  a game (dead 5% vs 12% of champion time); opening spread 1.68 teammates within 5 vs our 2.47.
- **Builds:** HoR Treasure H > Jungle F > Bruiser/Durability H, ends Bruiser Focus and Health equally; Vesper Treasure S >
  Jungle S > Bruiser S/H (5.4 / 2.6 at the end); Marcella Treasure F > Durability H > Bruiser F/H/S; Vendetta Treasure S >
  Prospector S > Jungle H (or Hunter S > Jungle S > Durability H) then Bruiser S/H; Ryth often nothing before r440.
  Copying lines wholesale lost locally (-132); Focus-heavy HoR lines -11..-25: builds must fit how our code plays.
- **Kit use:** their HoR shields 5 times per 100 rounds (ours 3.3), 28% at full health, 19% as an enemy comes within 4-6
  (now copied: `kShieldNear` 6); dashes onto enemies 11% / away 7% (ours 7% / 13%). Vendetta: resets at camps (kills refresh),
  dash mostly travel, frontline 76%. Their Willow and Vesper stay out of contact (enemy within 3: Willow 1.2% of rounds vs
  our 6.1%; Vesper 5.7% vs 8.3%).
- **Fights:** our logged fight odds of 1.0-1.5 were really < 1 in 63% of turns (per-champion occluded vision); caution
  switches (respect, ghosts, standoff, forecast threat) never reduced deaths against them and cost farming locally.
- Four of them pre-start recalls every turn (section 4); Fish parks wards on contested altars.
- **Map categories in our bot (Oct 31, #458; bot-status.md):** control = spawn walk <= 45 (36 maps); boss = groups of 5,000+ HP hold
  30%+ of camp gems (48 maps, catches 2-elk packs) -> one squad all game; otherwise a team opening of 0-240 rounds. **Eric's farm maps**
  (Oct 31): no way to the opponent but over walls / through a monolith (boss_battle), or a very long walk (cuts), or far contest points
  (islands, ambush) - split, group for middle camps once enemies show there; `edit_farmmap.py` kFarmMap classifies 23 maps (walk with
  monoliths blocked > 60 or impossible).
- **Recall cycles / clockwork (Oct 31, 203 games; `recall-cycle-1031.md`):** the top teams' recall cycle is individual (2.2-2.4
  champions per joint recall, 17-41% of recalls joint) - ours is more synchronised (46%, 2.7). Pre-starting recalls is not what
  separates the top (prism best girl, NEETCoders never do). The clockwork is **light camps (clusters, wolves) taken by a champion
  away from its main group**: elk captures equal Fish's (9.1 vs 9.6 a game), light camps 15.3 vs 25.7, 34-43% of Fish's by an away
  champion (ours 6-25%). Our walk out from home is 28% of champion-rounds (Fish 21%): 84% of departures chase the squad's camp.
  Against the other top teams the gap is camp damage (+21-34% a camp round), and strength follows gold income on the carries.
- **Grouping (Oct 31, 140 top-vs-top games, all 70 maps; `top-teams-grouping-1031.md`):** their play changes at a spawn walk of
  **60** steps, not our 45 (first PvP hit r46 vs r132, 5.0 vs 1.9 kills before r300). The main group is small: 5 picks 3.2-3.4 of
  ~4.5 active in r0-100, then 2.5-2.8 on contest maps and 2.1-2.3 on farm maps (typically a pair + three solos); the first 20-round
  split (> 8 tiles) comes at median r46 (farm 5-pick), r63-80 (5-pick contest), r89-92 (4 picks), r114-138 (3 picks): Vesper /
  Marcella on farm maps, HoR on close 3-4 pick maps; alone, own half, one camp, ~35 rounds, then back. Split champions join only
  11-20% of fights elsewhere; killing fights are 2v2; monoliths first hit at median r591 by three. Grouping shape does not predict
  the winner (52-62%).

## 8. Our bot (live **#428** since ~13:50 UTC Oct 29 by Eric's choice = #427 + kResetMore 2 + kMarcFleeReset; #427 = #423 [#418 + kFreeKill 0.9] + kDashBehind + kVendFight 103 + kFleeAbil 11; `bots/B477x` + `tools/cands/cand428.edits`. Earlier: live **#415** again since ~06:15 UTC Oct 29 by Eric's choice = #405 + kPairWalk 3 + kRepeatWait 20, `bots/B464x` + `tools/cands/cand415.edits`;
#418 (+ kVespBuild 6) 04:10-~06:15, pinned-equal to #415 (+1 win / 70); #415 Oct 29 02:55-04:10; #405 Oct 28 09:11 - Oct 29 02:55; detail: `bot-overview-371.md`, `bot-status.md`)

- **State at Oct 31 ~21:15 UTC (newest; overrides the live line above).** Eric's default build is **#479 = #458 + kCaptureHit** (he asked
  ~17:45 UTC); the platform shows **#481** live (= #458 + kCaptureHit + kRecallCapFix 3 + kEarlyRecall + kFieldFirst + guard; quick panel 13
  vs #458's 16) because a submission flips it to "follow newest ready version", and `submissions activate` is blocked by the auto-mode
  classifier - Eric activates. **kCaptureHit wakes full-health hostile nodes through a strength-0 cluster** (audit; local -49 / -18):
  kCaptureHitFix 3 (edit_capturehitfix.py) recovers it to ~-5. **kSpellFinish 1 (edit_lowfinish.py: a ready single-target damage spell at
  the weakest visible enemy champion under 30% or within the spell's damage, at the turn start) +32 +-18 alone, +14 in combination** -
  the day's best switch. Candidates (bots/B578x + run/candG2x.edits): **G2 = #458 + exact fuel caches + kGemLate 3 + kEarlyRecall +
  kFieldFirst + guard + still 6 + kCaptureHit + fix + kSpellFinish 1: local -7 +-20; G3 = G2 without capture hit -1 +-20**; wide scan
  (70 maps x 2): loop/stuck 443 rounds vs #458's 1,016, fuel-limit turns -26%, no 100+ map. Detail: bot-status.md, Grant #14.

- **ELKRING FREEZE in #428 (Oct 29 ~21:45): kSquadPacksOnly skips every camp on a whole-game team map (team_rounds_ 2000) without a
  multi-monster home pack - the leader's pick is -1 and all five idle all game (00elkring A lost 88 - 1012; big-world too).** Fix
  `tools/edits/edit_packsfallback.py` kPacksFallback (filter only when a home pack exists): elkring 2 / 8 -> 8 / 8 locally; on #428's own source
  (bots/B492x) 8 of 140 all-maps games flip, net +2 vs B7Live. **Ladder #442 = #428 + it: panel 32 / -46.3k, identical to #428 on 124 of 125
  games - recommended live (22:30 UTC).** Any unseen knockout map classed whole-team with single-monster camps would freeze the same way.
  Since then on the panel: #443 small-node split 22 (loses, as locally), #444 escort hit 25 (the third "engage more" change punished).
- **Oct 29 grant #11 (14:40 UTC-) on the 125-game pinned panel, vs #428 32 / -46.6k:** #430 bundle 28; #431 MarcGems 4 + MeleeOpen 28;
  **#432 fight bundle (kDashKill 3 dash-in on low runners, ranged chase dash, escape fixes) 18**; #433 ReviewFix29 384 + Prospector farm build +
  MarcGems 4 + DoomBlock 21; #434 ReviewFix29 384 + DoomBlock 24; #435 no-op (kNoopFuel 1) **32, 0 results flipped**; #436 harness bits 15 (bug
  fixes + kWaitLeaveReach) 27; **#437 harness bit 16 = MarcGems 4 alone 31 / -46.5k (= #428; local +21 / +12): the one holding change**; #438
  60-round opening everywhere 30 (local -32). Aggression and item / reward-routing changes lose against the top teams; bug fixes are neutral at
  best. Real bugs fixed (behind switches, B487x+): the tribute cancel / restart loop (kDoomBlock), rewards left lying (kReviewFix29 128),
  carry reports never read (bit 1), kZones 3 never ran (bit 512). Runtime-eval harness: `tools/edits/edit_rteval.py` / `edit_rteval2.py`
  (bots/B489x; bits in draft byte 15).
- **#405** = #402 + HoR camp dash (kRuinReach: a refused 2-tile landing - a monster on the middle tile - is retried; kRuinCampAim 7: land on
  the most monsters). Source: `bots/B438x/src` + `tools/cands/cand405.edits` (on B439x+ kRuinReach is an int: `= 1`). Not adopted on the
  ladder Oct 28 (same-time pairs, 100 games each): #406 Marcella tribute + Durability line, #407 HoR for Ryth at 3 picks, #408 kReviewFix 6
  (16 vs 21; local +33 / +41; 71-71 over 280 games), #409 kVesperFeed 7 (17 vs 22), #410 HoR in every draft (3-pick bench 5/50 vs 2/50,
  4-pick 14/50 vs 16/50: a tie). Candidate chain Oct 28 night (all switches off by default, each `tools/edits/edit_*.py` names its base):
  B455x kAuction, B457x + fixed auction + kHealIdle, B458x kSquadLeash, B459x kPairWalk (draft-turn wall-trap pairs), B460x kFarmGuard,
  B461x kContestedKeep. **#411 = #405 + kHealIdle 0.4 + kTwinTarget 3** (local +17 +-11): ladder tie with a slight edge (top-10 12/50 vs same-time
  11/50; Fish sets 2/20 vs 0/20 on different maps, 0/20 vs 0/20 with -2k on the PINNED games) - a tie; **#412 = #405 + kPairWalk 3** (draft-turn wall-trap pair records, trap-only; local +7 / +9,
  ambush +202) pinned games: top-10 14/50 vs 11/50, Fish 0/20 vs 0/20 - modest positive; **kContestPush** (edge 1, odds 1.2; local +26 +-6, Eric's
  rule from replay e3bc9f14: push a contester off a held reward) as #413 on the same pinned games: top-10 8/50 vs 11/50, Fish 1/20 vs 0/20 -
  the local +26 did not carry, not adopted; #414 = #412 + kHealIdle 0.4: top-10 12/50, Fish 0/20 (-2.8k) - the heal adds nothing over #412; #415 = #412 + kRepeatWait 20: top-10 13/50, Fish 0/20 - neutral; #416 + kShopFar 45 -1 win vs #415; **#417 + kClusterOne (Eric's
  one-champion-per-cluster rule) top-10 9/50, -4.4k vs #415, local -43: off for good**; **#418 = #415 + kVespBuild 6 (Vesper Treasure S first, the top 10's
  line): top-10 13/50 (= #415), Fish 1/20 -10,200 (best of #412-#418), local +13 +-7** (live from 04:10); #419 = #418 + Vendetta for Willow + Fish health lines: 140-game panel 14 vs 24 wins - the Willow-less
  meta draft fails in our fight code even with health lines; #420 = #418 + repeat reach 20 / wait 30: panel 24 vs 24 (gap 60 -> 41 rounds
  locally changes nothing); **kFreeKill** (Eric's replay 22ebc966: a one-hit kill a step away before
  escape / evade; local +16 / +8 / +21) - panel #421 (#415 + it) 25 vs 24, #422 (#418 + it + Marcella Durability H line) 22 vs 24 / +2.3k: small,
  unresolved; **#423 = #418 + kFreeKill: panel 28 vs 24 wins, +2.4k - the recommended knockout build**; kKillChain −9, kMeleeOpen −30,
  Vendetta planner / dash discipline neutral on a losing draft; kSafeBag 80 −15, kBushChase −9, kBushGhost −4..−7, kDashBehind −4 (ladder-only questions);
  kAnyHit (hit any member in reach when the target is out of reach) −23: the misses are partly deliberate focus fire; its stress scan shows 7 waits of 12-37 rounds (gate relaxed to 8 / 160, no freeze).
- **Source (#402):** `bots/B426x/src` + `tools/cands/cand402.edits` = #400 + kBlockCapture 7 (a reward group in sight the enemy is
  capturing, worth 10+, a free tile within its timer + 2 steps, health 50%+, fight odds 1.0+ (#401: 0.4): stand on it - an enemy on a tile resets
  their capture; hold it while contested). **#400:** `bots/B419x/src` + `tools/cands/cand400.edits` = #395 + boss mode on big nodes (kBossMaxStr 250, kBossHp 5000,
  kBossGemShare 0.3: camps of 5,000+ health hitting <= 250 holding 30%+ of the map's gems make it a boss map - whole team all game, boss
  camps taken once the team's strength allows) + kDeliverGems 40. #395 source was
  `bots/B408x/src` (bot.cpp ~15.8k lines + draft.cpp) + `tools/cands/cand395.edits` (= #392 + kRythMix 2; #392 = #389 +
  kContactTurns 8 + kRuinRedash + kVesperGoldW 3; B408x also carries the Oct 27 farming / carry / strength switches, all off). Edit chain
  since #371: `tools/edits/edit_*.py` applied in order (each header names its predecessor and the `bots/B###x` it made).
- **Draft (by pick count):** <=3 Marcella, Vesper, Ryth; 4 + Willow; >=5 HoR, Vesper, Ryth, Marcella, Willow. Taken picks
  fall through. Swaps tested: HoR for Ryth at 3 -47, Vendetta for Willow -125 (-145 with her top build): off.
- **Turn priority:** escape (burst guard) > stand-shot > evade (odds < 0.85) > kite > fight (odds >= 1, burst model,
  assists, HoR dash as an attack, melee free hit) > hunt (wounded / carriers / recallers, deny once they bank 600) > base
  heal (hurt near spawn walks in and heals, `kBaseHeal` 4) > retreat (35% health) > deliver (bank at 40 gems since #400) > tribute
  guard / contest > farm (score = gems + gold x weight, solo after the opening, parties sized by front line) > turn-end
  free melee hit (`kMeleeFree` 3) > Willow heal > HoR shield when an enemy is within 6.
- **Opening:** whole team together for 120 rounds, 240 on race maps, 180 on control maps with spawns > 16 apart; one helper
  joins big parties (`kBigParty` 1). Recall-capture with slack 10.
- **#389's config in words:** #372 (hunting, chase cap 7, melee move+attack) + base heal + melee free hit + Ren guard +
  pre-recall threat fixes (`kRecallThreat`, `kRecallGenuine` Home-aware) + stand-shot odds fix + opening by layout +
  big party + recall slack 10 + bag 30 + HoR shield at 6 + HoR Bruiser F/H end mix.
- **Ladder panel (140 games vs the top 10):** #382 16 wins / -74,835; #385 15 / -75,207; #386 23 / -69,621; #387 26 /
  -64,530; #388 28 / -59,052; #389 28 / -60,537; #390 (kMaxNeed 4) 25 / -61,109; #391 (contact rule) 29 / -57,559; #392 29 / -55,335; #393 (carry flee) 20; #394 (Vesper duo) 25;
  **#395 (Ryth H/S mix) 32 / -49,335** (same-time re-bench 27 / -59,621); #396 (pairs after the opening, local +20) 26, rejected;
  #397 (finisher) 28 / -58,134; #398 (boss 250 / 0.5) 23 / -59,204; #399 (boss 5000 / 0.3) 27 / -50,192; **#400 (+ bag 40) 38 / -42,918**; #401 (block-capture) 32 / -46,815 two hours later, same-time top-10 + rotated 24 vs #400's 26 (tie).
- **Positive locally (kept):** base heal +13, recall threat + genuine +15, opening by class +29 +-9, big party +9/+8,
  slack 10 + bag 30 +28 +-15, shield near ~+8, HoR end mix ~+5 (six seeds each).
- **Negative or neutral (off):** camp spreading (`kSpread`), respect base, ghosts, standoff, hunt bound, fuel savers
  (score every 2, solo fuel, hitters cache), whole-team squads (-57 / -105), `kSetupControl` -16, `kTeamWholeRate` -30,
  flee reset +2, `kRecallThreatAll` (ladder worse), economy variants (bag 25 +5, 35 -10, slack 15 -19), Vesper gold weight
  2 / 3 / 4 (+1 / +19 then -4 / -19), Ryth gold x0.5 -10, Willow back / escape lines (+10 +-18 / +2 / -9), Focus HoR lines,
  passive-aware HoR odds -5, HoR escape 0.3 +2, kLadLog (fuel: -1.4 kills a game).
- **Fuel profile on fight turns:** observe_enemies 7.8k, observe_groups 7.3k, manage_squad 5.5k, observe_allies 5.1k;
  fight turns run near the 100k cap, so any logging there costs kills.
- **Known bugs fixed recently:** opening class decided per champion at different times (teammates disagreed for ~100
  rounds; fixed at set-up), Home-emblem miss in the genuine-recall check, base-heal wasted turn, follower stall in
  spreading, forget_picks spam.
- **Protocol (shared memory, Codex's layout):** bytes 0-4 slot targets (+ help/solo bits), byte 5 respawn events, 6-7
  alerts / banker / carry sightings; the draft plan in draft memory.

**Farming study (Oct 27, `bot-status.md` "farming like Fish"):** Fish's edge on farming maps = a 6th champion (Cassi & Issac) on every
5-pick map, 3x our elk-camp captures after the opening (parties of 3-5 re-form; ours never do after the 240-round opening), gold-cluster
sweeps, camps re-taken at the respawn (cycle 71 vs 94 rounds on wolf packs), and far fewer deaths. Tools: `tools/stress/extract2.ts`,
`farmcmp.py`, `transcmp.py`, `incomebench.sh` (gold/gems by r600 on six quiet maps vs our own code: the live config 2,747 / 359).
Tested and NOT adopted: exact respawn timers, cluster solo, neighbour bonus, help-start, big parties, late scheduler, solo parties,
the twins draft (six bodies farmed 11% less: our twin code), and a set-up team-orienteering route planner (kFarmRoute, four iterations:
2,433 -> 2,577, fixed loops idle five champions). Only kMaxNeed 4 is mildly positive (~+9 +-5).

**Snowball study (Oct 27):** gold decides games (kills ahead + gold behind at r600: 22% wins; both ahead 69%). Our income does not
scale: camp damage per champion-round 14 -> 17 from the opening to r900 vs theirs 18 -> 30, strength 83 vs 142 at r900 (our Focus is
higher), Vesper 802 gold vs their 2,000. Strength-heavy Marcella lines raise income but lose fights (-50); Vesper as gold carry is in #392.

## 9. Open levers (what the evidence points at next)

1. **Farming throughput, not caution:** captures 22.7 vs 31.1 by r600; their Vesper's camp damage 55% above ours. Camp
   weights do not fix it (section 8); look at trip shape (we turn home at ~82% health; recall-capture timing) and party
   waiting.
2. **Kill gold 190 vs 620:** finishing wounded enemies near our camps (hunt rules are on; the gap is odds calibration and
   melee follow-up, not willingness).
3. **Deaths 13.4 vs 6.2:** not solved by blanket caution; per-situation (monolith reach, tribute under ward vision,
   pre-recall reads) rules did better than global ones.
4. Sprint 3 unknowns to verify with probes once seen: Capture emblem timing, Prospector on cluster loops, Hunter kills.
   (Oct 27: Capture / Prospector emblems screened neutral or negative, also against a capture-contesting pool.)
5. **(Oct 27) The r300 gold leader wins** (#399 panel: losses 963 vs 1,321 gold at r300 compounding to 2,938 vs 4,998 at r900; the
   mirror in wins). The gap is farming rate: 9.8 vs 15.3 captures by r300, 17.9 vs 30.4 in r300-900 (the top teams solo clusters and
   1-elk camps); every smaller-party arm still loses locally (cluster solo -37, two squads -44..-76, whole team everywhere -248).
6. **(Oct 27) Contested captures decide big nodes:** whoever stands on the tiles when the last member dies captures; an enemy on a tile
   resets the timer. #401's kBlockCapture contests enemy captures (+66 wins locally; a tie vs the top 10, who contest too).
7. **(Oct 27) 3-pick maps:** 42% of ranked games vs 71% / 56% at 4 / 5 picks; HoR for Ryth there is -251 locally.
8. **(Oct 28) The farming gap is damage output, not pathing:** timebudget.py - both sides move 53-56% and hit camps 15-22% of champion
   time; our camp damage per hitting round is 22-28% lower and we are dead 12% vs 8% mid-game. Half is per-champion (HoR casts its
   hitting dash on camps 0.19 vs 0.30 per attack; Vesper's strength 113 vs 145), half the draft's 5th slot (Willow 8.8 camp damage a
   round vs Vendetta 27). Split-play arms fail because grouping was never the gap.
9. **(Oct 28 pm) Party size and carry feeding, measured:** our clears r300+ carry 1.0-1.9 champions past the first adopter's need, ~90%
   squad followers (48 of 70 maps are boss maps since #399: one squad of five all game). Every release of them is neutral or negative
   locally (`kPartyShare`: share -71, satellites -21..-156; with a single-monster boss gate from r600 +4 / +5). Fish's lead is two fed
   strength carries: their Vesper / Marcella earn 2x ours by r600 (1,577 / 1,926 vs 602 / 1,090 gold); in our parties Vesper takes only
   ~20% of the rewards she clears (theirs ~40%). `kVesperFeed` 3 doubles her gold (probe) but loses -40 locally, 7 is neutral, and the
   ladder said 17 vs 22. Our champions dropping under 35% in a fight die 64% (27% the next round) vs Fish's 30%: their health pools are
   ~1.7x ours. **Local screens did not predict the ladder on any of four candidates today**; 100-game same-time pairs resolve only ~5 wins.
10. **(Oct 28 night, 28 Fish ladder games, audited by Codex C247/C250)** Fish clears 1.5x our camps by r300 and 1.8x by r600 at equal gold
   per clear (gold r600 2,393 vs 4,445); their champions deal ~40% more camp damage per alive round at the same HoR dash cadence (damaging
   dashes 3.34 vs 3.72 per 100 rounds, members per dash 1.87 vs 1.70) - scaling and contact time, not dash use or aim. Before r300 we die
   LESS (44 vs 58); after r600 134 vs 86, truly outnumbered (victim counted) 28% vs 12%; Ryth / Vesper / Marcella die 10-12 tiles from any
   ally while healthy, Willow beside one fighter. Of 54 healthy approaches toward enemies before those deaths, 33 are farm() steps toward a
   retained camp or reward with an enemy beside it (22 of 33), not chases; chase + prey off costs -23 locally (the hunting rules earn their
   keep vs the pool). Willow's heal (cooldown 8) is cast 3.5 per 100 rounds: **kHealIdle 0.4 +17 +-11 locally (+36 wins)**; kTwinTarget 3
   is invisible locally (no twins in the pool, Fish-only). Draft-turn wall-trap pair records (kPlanPairs) verified in play (ambush 24 pairs).
   Opening r1-150: our champions hit camps 19-29% of rounds vs 27-36%, stand still 21-26% vs 13-21%; our gold goes to Marcella, theirs to
   Vesper (243 vs our 102 by r150).
11. **(Oct 29, 250 top-10 games) Emblems are team styles, not map styles:** Prospector newerteam 87% / TrzyKwaterki 72% / AdAstra 51% of
   champion-games (Marcella Focus, Vesper Strength, Prism, Varg), Hunter NEETCoders 44% by r167, Capture newerteam 49%; Fish, Claudus and
   Sponge build only Treasure (Vesper's first emblem at r125 in 48% of all top-10 Vesper games). Prospector share by map class 26 / 18 / 28%.
   Detail: bot-status.md "Emblem use of the top 10"; tools/stress/emblems.ts + emblems.py.

12. **(Oct 30 eve, grant #12; detail bot-status.md "Fuel stunlock" onward)** *Where the top teams win:* banked gems are even to r600 (332 vs
   340 in 50 #450 panel games), then ours stall; from r300 their farming rate rises (gems per 300 rounds 294 / 319 vs our 220 / 202) and
   their Vesper is the carry (camp damage per alive round 40-54 vs 21-23; strength 190 vs 95 and max health 2,250 vs 1,000 at r600; dead
   3-7% vs 12-16% of mid-game rounds). Routing rewards to Vesper loses every way (kVesperFeed, kCarryPair -107 / panel 17 vs 21, kCarryGemK
   -15..-25, kVesperFree -36..-2). *Fuel:* ranked lanes 9.6% of turns capped (idle death-window rounds were capped turns); kSightCache
   (exact: ranged approach roots cost 21-69k a build) and kScoreNear (fx_groups 128 / 256: 35 / 47% capped -> 7 / 22%) cut caps, but every
   panel version with kFuelSafe skipping lost real games (#456 -> #457 17 W->L vs 6 L->W). *Drafts:* the dash trio (Ves+Ven+HoR, the most
   drafted top 3-pick set) is -7..-11 per 100 vs team strength; HoR at 3-4 picks lost locally (-81..-243) and on the panel (#453 18 vs 21).
   *Measurement:* two versions differ in 16-23 of the 125 panel games: read the W->L / L->W flips (sign test), not the totals; panel B
   (panelB.sh) = the same pinned bots on rotated maps for 125 independent games.

---
*Update rules:* a verified fact goes in with its date and method; results go to `bot-status.md` first, then the summary
line here; when a version goes live, update section 8 and the memory index. Keep this file under ~300 lines - it is a
sheet, not the archive.

## 10. Fights (Oct 27 study; detail bot-status.md "the fight side")
- We lose even fights (-0.25 net kills a fight vs the top's +0.25) and do not finish dominant ones (2.8 v 1.4 champions: we kill 23% of the
  enemies we hit and lose 0.30 a fight); every champion type of ours dies ~2x as often as theirs when caught. Per-round micro is close
  (attack rates with an enemy in range within ~5 points). The gap is individual stats: their fed, health-built carry bursts our weakest.
- Replay hit matching: compare a hit's tile with the target's position at the round's start AND the next round's (the other team may
  have moved first) - start-only undercounts ~25%.
- **Fish finish, they do not burst harder (Oct 31 study, tools/stress/burst/, 36 Fish / 27 ours / 140 top games):** commit rates,
  casting on cooldown and focus fire equal ours; kills before r600 6.9 vs 2.8 a team-game; damaged enemies that die 29% vs 13%; hurt
  prey (< 50%) chased -> killed 52% vs 28%; kill rate with 3+ attackers 67% vs 27%; Marcella with her nuke ready and an enemy under 30% at
  3-4 tiles casts 56% vs 22% (our champion casts came only from the fight branches). Fish stop chasing only on a recall out of reach or
  at home. The spell finisher (kSpellFinish 1) copies the nuke rule (+32 locally); kChaseMax 10, kWoundedTeamHunt and a Ryth opener
  gate did not help locally.
