# How the top teams group, split off and play contest vs farm maps (Oct 31 study, engine 2.0.0)

Eric's question before the Nov 1 knockout: how do the top teams group up on each kind of map, when does a champion split off
from the main group, which champion is it, what does the main group consist of, what does the split champion do, and what do they
do on contest maps vs farm maps. Everything below is measured from replays; guesses are marked as such.

## Data and method

- **Games:** 140 ranked games between two of the ladder's top 13 (Oct 30: prism best girl, Mite, Ad Astra, Intercontinental Fish,
  newer team, hello, print dont int, Trzy Kwaterki, Univardisty of Shingtonwash, Claudus Maximus, policy wonk, NEETCoders,
  Sponge), engine 2.0.0, created 2026-10-29 20:40 to 2026-10-30 16:10 UTC (median Oct 30 14:50; after the Oct 29-30 updates).
  **All 70 pool maps x 2 games**, chosen so each team has 21-22 team-games. Each game gives two team samples: **280 team-games**.
  Replays: `replays/top1031/MAP__teamA__teamB__id8/` (trace.json + grid.txt beside each).
- **Tools (new, `tools/stress/`):** `grpselect.py` (selection), `dlmatches.py` (download), `grpprep.py` (extract1.ts traces +
  mapgrid.ts grids, 4 jobs), `grpsplit.py` (per-game metrics, JSONL), `grpsum.py GAMES.jsonl [R]` (all tables below).
  Re-run: `python -I tools/stress/grpsplit.py OUT.jsonl replays/top1031/*/` then `python -I tools/stress/grpsum.py OUT.jsonl 6`.
- **Definitions** (round-start positions, Chebyshev distance, walking distances by 8-way BFS around walls and holes from each
  team's start tiles):
  - *active* = alive and more than 4 steps from its own start tiles (healing / shopping champions are left out);
  - *main group* = the largest single-linkage cluster of active champions (link radius **R = 6**, R = 4 checked: same pattern,
    every group ~0.3 smaller), 2+ members;
  - *away* = active, outside the main group and **more than 8 tiles from every member of it**; *near* = outside it but within 8;
  - a *split episode* = **20+ away rounds** (dead / home rounds pause it, a round within 8 of the main group ends it);
  - *own / enemy half* = the walk from one spawn is shorter by more than 2 steps (the bot's `far_side_` rule); *mid zone* = the
    two walks differ by at most 4;
  - *PvP hit* = an attack or cast whose target tile holds an enemy champion; a *kill* = a death with a PvP hit on the victim in
    the 3 rounds before (82% of the 2,617 deaths); a *fight* = PvP hits merged with gaps of at most 5 rounds.
  - Cassi and Issac count as two bodies; "5+" picks includes the 6-body teams.

## Map categories

**Rule: spawn walk** (BFS steps between the two teams' start tiles): **close <= 30, contest 31-60, farm > 60.** The cut at 60, not
the draft's 45 (`kRangedSteps`), is where the top teams' play changes (per map, both games averaged):

| spawn walk | maps | first PvP hit (median) | PvP kills before r300 / game | kills per 1000 rounds | main share r0-200 / 200-700 (5 picks) |
|---|---|---|---|---|---|
| <= 30 | 17 | 19 | 5.3 | 19.4 | 72% / 67% |
| 31-45 | 19 | 44 | 4.5 | 17.1 | 73% / 63% |
| 46-60 | 12 | 46 | 5.0 | 16.6 | 75% / 64% |
| > 60 | 22 | 132 | 1.9 | 8.3 | 61% / 47% |

The 46-60 maps (00breadcrumbs, 00crater, 00eight, 00gemfight, 00monolith, 00quadrants, 00stampede, 01gold_rush, 02fields,
adgato_gemcombat2/3/4) play like contest maps for the top teams but are "race" maps for our draft and opening (240-round
whole-team opening, HoR-first draft). Threshold scan (per map, "contest-like" = first PvP hit before r100 and 10+ kills per
1000 rounds, 45 of 70 maps): a walk cut at 60 misclassifies 13 maps, at 45 23, at 30 32. Single features (per-map correlations,
70 maps): first-hit round vs log(walk) +0.41, free tiles +0.43, total gems +0.47; mid-zone time vs log(walk) -0.63 (the
strongest), share of gems within 6 steps of the midline +0.44; kills per 1000 rounds vs walk -0.35, free tiles -0.36, midline gems
+0.33; monolith/golem share of gems ~0 for kills (boss maps range from a fight at r25 to none at all). Spawn walk is kept because
the bot already computes it and the bands separate cleanly.

- **close (17 maps, 34 games):** 00anvil, 00fragment, 00lost_world, 00oasis, 00packs, 00reverse_spiral, 00rushbait_v2, 00swirl,
  00the_line, 01elk_arena, 01yellow_brick_road, 02arena, 02stalactites, 02the_pack, 02treasure_box, adgato_gemcombat1, 5.
  Picks: 3 x6 maps, 4 x6, 5 x5.
- **contest (31 maps, 62 games):** 00breadcrumbs, 00collision, 00contest, 00corners, 00crater, 00eight, 00elkring, 00gem_fields,
  00gemfight, 00interlock, 00monolith, 00quadrants, 00quarry, 00stampede, 00vault, 01boss_battle, 01broken_curve, 01corridors,
  01gold_rush, 01hooks, 01starfish, 01the_farm, 02crossing, 02fields, 02gift_wrapping, 02guardians, 02the_pond,
  02uncharted_lands, adgato_gemcombat2, 3, 4. Picks: 3 x6, 4 x8, 5 x17.
- **farm (22 maps, 44 games):** 00ambush, 00dunes, 00expanse, 00galaxy, 00great_wall, 00lanes, 00pilgrimage, 00ribs,
  00road_of_riches, 00rows, 00split, 01big_world, 01concentrated_wealth, 01fracture, 01islands, 01shortcut, 01starvation, 02cuts,
  02famine, 02geodes, 02harvest, 02tangle. **20 of 22 are 5-pick maps** (00rows and 01shortcut 4): "farm" and "5 picks" coincide.

## 1. Grouping: the main group is small, and smallest on farm maps

Main group by window (R = 6). Cells: mean main-group size / share of active champions in it / share of rounds with no group of 2+.

| category | picks | n | r0-100 | 100-200 | 200-400 | 400-700 | 700+ |
|---|---|---|---|---|---|---|---|
| close | 3 | 24 | 1.7 / 73% / 24% | 1.6 / 66% / 30% | 1.5 / 63% / 34% | 1.4 / 61% / 36% | 1.5 / 69% / 29% |
| close | 4 | 24 | 2.5 / 81% / 12% | 2.1 / 70% / 22% | 2.1 / 68% / 23% | 1.9 / 64% / 26% | 1.8 / 63% / 28% |
| close | 5+ | 20 | 2.5 / 78% / 16% | 2.2 / 66% / 23% | 2.3 / 67% / 21% | 2.3 / 67% / 21% | 1.9 / 67% / 26% |
| contest | 3 | 24 | 2.1 / 82% / 15% | 1.8 / 71% / 23% | 1.5 / 62% / 36% | 1.4 / 56% / 38% | 1.4 / 57% / 36% |
| contest | 4 | 32 | 2.5 / 76% / 14% | 2.2 / 66% / 22% | 2.2 / 64% / 21% | 2.3 / 66% / 19% | 2.0 / 65% / 23% |
| contest | 5+ | 68 | 3.4 / 79% / 6% | 2.8 / 68% / 12% | 2.8 / 65% / 13% | 2.6 / 63% / 14% | 2.5 / 62% / 15% |
| farm | 4 | 8 | 2.2 / 74% / 17% | 2.0 / 64% / 24% | 2.0 / 63% / 25% | 2.0 / 59% / 25% | 1.9 / 56% / 21% |
| farm | 5+ | 80 | 3.2 / 71% / 6% | 2.3 / 51% / 18% | 2.2 / 49% / 20% | 2.1 / 46% / 22% | 1.9 / 43% / 26% |

Party structure (cluster sizes of active champions), commonest per phase; mean number of parties:

| category | picks | r0-200 | r200-700 | 700+ | parties r0-200 / 200-700 / 700+ |
|---|---|---|---|---|---|
| close | 3 | 3 25%; 2 19%; 2-1 18% | 2-1 20%; 2 20%; 3 15% | 3 28%; 2 19%; 2-1 17% | 1.5 / 1.6 / 1.4 |
| close | 5+ | 5 11%; 2-1 11%; 1 9% | 4 10%; 2-1 10%; 3 9% | 1 12%; 2 10%; 3 10% | 1.7 / 1.8 / 1.7 |
| contest | 3 | 3 34%; 2-1 22%; 2 14% | 2-1 27%; 3 18%; 1-1 17% | 2-1 30%; 3 18%; 1-1-1 14% | 1.4 / 1.7 / 1.7 |
| contest | 4 | 4 15%; 2-1 12%; 3-1 12% | 2-1 14%; 4 12%; 3-1 11% | 2-1 14%; 4 11%; 2 10% | 1.8 / 1.9 / 1.8 |
| contest | 5+ | 5 15%; 4-1 8%; 3 7% | 3-1 9%; 2-1-1 8%; 2-1 8% | 2-1-1 8%; 3-1 8%; 2-1 8% | 1.9 / 2.2 / 2.2 |
| farm | 5+ | 5 14%; 2-1-1-1 12%; 4-1 9% | 2-1-1-1 16%; 2-1-1 12%; 3-1-1 9% | 2-1-1-1 19%; 2-1-1 12%; 3-1-1 9% | 2.5 / 3.0 / 3.2 |

**All active champions in one cluster** (3+ active), share of rounds r0-100 / 100-200 / 200-400 / 400-700 / 700+:
contest 5+ 44 / 27 / 22 / 17 / 19%; contest 4 43 / 24 / 23 / 26 / 22%; contest 3 47 / 31 / 25 / 17 / 19%; close 5+ 40 / 22 / 25 /
27 / 27%; **farm 5+ 35 / 9 / 9 / 7 / 5%**.

Reading: even the opening is not a full stack (main share 71-82% in r0-100). From r100 a 5-pick team on a farm map is typically
**a pair plus three solos** (2-1-1-1); on contest maps a group of 3 with satellites (3-1, 2-1-1); on 3-pick maps a pair plus one.
With R = 4 every number drops (farm 5+ main share 64% / 42% / 40% / 38% / 34%), the ranking of categories is unchanged.

## 2. When the first champion splits off, and who

First split = the team's first 20-round episode of a champion more than 8 tiles from the main group. "Enemy" = share of that
episode on the enemy half; "later" = that champion's away rounds from onset to the game's end / rounds in that span.

| category | picks | n | none | onset p25 / med / p75 | onset < 150 | first splitter (share) | enemy | solo | later |
|---|---|---|---|---|---|---|---|---|---|
| close | 3 | 24 | 0 | 40 / 138 / 222 | 62% | HoR 54%, Marcella 21%, Vesper 12%, Vendetta 8% | 12% | 100% | 14% |
| close | 4 | 24 | 1 | 46 / 89 / 174 | 67% | HoR 30%, Vesper 26%, Marcella 13%, Vendetta 9% | 30% | 92% | 14% |
| close | 5+ | 20 | 0 | 42 / 80 / 132 | 80% | Marcella 25%, Vesper 20%, HoR 15%, Vendetta 10% | 1% | 97% | 21% |
| contest | 3 | 24 | 0 | 79 / 114 / 202 | 58% | Marcella 29%, Vendetta 21%, HoR 17%, Ryth 12% | 17% | 98% | 16% |
| contest | 4 | 32 | 1 | 34 / 92 / 146 | 72% | HoR 32%, Marcella 19%, Vesper 19%, Ryth 10% | 18% | 99% | 19% |
| contest | 5+ | 68 | 0 | 36 / 63 / 138 | 75% | Marcella 24%, HoR 21%, Vendetta 18%, Vesper 16% | 10% | 73% | 19% |
| farm | 4 | 8 | 0 | 36 / 47 / 79 | 88% | Ryth, Marcella, Tavi 25% each | 0% | 91% | 32% |
| farm | 5+ | 80 | 0 | 22 / 46 / 74 | 98% | Vesper 22%, HoR 18%, Marcella 18%, Vendetta 16% | 7% | 75% | 39% |

- **Order: farm 5-pick first (median r46), then close / contest 5-pick (r63-80), 4-pick maps (r89-92), 3-pick maps last
  (r114-138).** Stricter thresholds (12 tiles, 40 rounds) keep the order: farm 5+ r86 (66% before r150, 5/80 never), contest 5+
  r167 (16/68 never), 4-pick maps r122-200 (42-50% never), 3-pick maps r297-363 (33-54% never).
- **Which champion, normalised by how often it is drafted** (first splits / team-games with the type): close: HoR 41%, Marcella
  27%, Vesper 26%; contest: Marcella 30%, HoR 26%, Vesper 25%, Ryth 24%, Vendetta 19%; farm: Vesper 32%, Marcella 24%, HoR 17%,
  Vendetta 16%. Cassi (7%) and Willow (5-17%) rarely split first; Issac 10-29% (n 14-30).
  **On close 3-4 pick and contest 4-pick maps it is most often HoR** (close 3: 54%, close 4: 30%, contest 4: 32%); on contest
  3-pick maps Marcella (29%) / Vendetta (21%); on 5-pick maps it is spread over Vesper / Marcella / HoR / Vendetta.
- **Where: their own half.** 0-18% of the first episode on the enemy half (only close 4-pick 30%), 73-100% alone.
- **Not "for good".** The first splitter is away for only 14-39% of the rest of the game: it farms a camp and comes back. A split
  is a short trip, not a role. Dedicated splitters (60%+ of a champion's active r200-700 rounds away) exist almost only on farm
  maps: **54 of 88 farm team-games have one** (Marcella 27/67 champion-games, Ryth 14/49, HoR 23/81, Vendetta 22/81, Vesper
  15/60, Prism 4/9), vs 19/124 on contest and 9/68 on close maps.

Away share of each type's active rounds, early r0-200 / mid r200-700 / late 700+ (5-pick-heavy; solo share of away ~80-95%, enemy-half
share of away 3-17%):

| type | close | contest | farm |
|---|---|---|---|
| Marcella | 19 / 27 / 27% | 24 / 32 / 33% | **39 / 53 / 54%** |
| Vesper | 21 / 31 / 27% | 25 / 30 / 30% | **40 / 47 / 50%** |
| HoR | 26 / 28 / 26% | 22 / 29 / 34% | 33 / 47 / 52% |
| Vendetta | 24 / 29 / 25% | 20 / 30 / 32% | 33 / 45 / 51% |
| Ryth | 18 / 25 / 26% | 22 / 28 / 28% | 30 / 46 / 47% |
| Tavi | 20 / 22 / 20% | 23 / 31 / 27% | 38 / 44 / 51% |
| Willow | 24 / 22 / 45% (n 5) | 14 / 23 / 23% | 24 / 31 / 30% |
| Cassi / Issac | 14-26 / 22-27 / 18-28% | 12-16 / 23-24 / 22-23% | 21-23 / 31-39 / 39-45% |

## 3. What the main group consists of

P(in the main group | active and the team has one), early r0-200 / mid r200-700:

- **farm 5+ (n 80):** Issac 75/55%, Cassi 72/64%, Willow 72/63%, Varg 69/52%, Ren 67/54%, Ryth 65/49%, Prism 62/36%, Vendetta
  61/47%, HoR 61/46%, Tavi 58/50%, Marcella 55/40%, **Vesper 54/45%**.
- **contest 5+ (n 68):** Issac 85/69%, Willow 82/71%, Cassi 82/72%, Varg 79/66%, Ryth 75/66%, Tavi 74/61%, Vendetta 73/62%, HoR
  72/64%, Vesper 70/61%, Ren 69/59%, Marcella 69/61%, Prism 67/53%.
- **3 picks (contest, n 24):** HoR 77/60%, Vendetta 80/56%, Vesper 76/63%, Marcella 71/50%; commonest main groups HoR+Vendetta
  (12% of rounds r200-700), HoR+Vendetta+Vesper 11%, HoR+Vesper 10%, HoR+Marcella 8%. **HoR is the anchor of every common 3-pick
  group.**
- Exact 5-pick compositions are spread thin (no set above 5% of rounds). The most stable members are the **supports** (Willow,
  Cassi, Issac: 55-64% in r200-700 on farm maps, 69-72% on contest maps) and Varg / Ryth; HoR, Vendetta, Vesper and Marcella sit
  close together below them (contest 61-64%; farm 40-47%, Marcella and Prism lowest). On farm maps in r0-200 Vesper (54%) and
  Marcella (55%) are the least grouped.
- **Who moves with whom** (share of rounds a pair is in the same cluster when both are active, r0-200 / r200-700): farm: Ryth+Willow
  82/59%, Cassi+Issac 57/42%, Vendetta+Willow 53/42%, HoR+Ren 57/41% ... least Ryth+Vesper 32/18%, Marcella+Prism 40/17%;
  contest: Cassi+Willow 80/70%, Ryth+Varg 72/65%, HoR+Issac 75/60% ... least HoR+Prism 46/39%. Willow sticks to the melee
  carry; the two ranged / gold carries avoid each other.

## 4. What split champions do

Per 100 champion-rounds by state (main / near = outside the cluster but within 8 / away = split):

| category | state | champion-rounds | gold | gems picked up | camp damage | deaths | PvP deaths |
|---|---|---|---|---|---|---|---|
| close | main | 136,838 | 178 | 26.6 | 2,468 | 0.31 | 0.27 |
| close | near | 14,143 | 207 | 31.9 | 2,494 | 0.29 | 0.25 |
| close | away | 53,223 | 182 | 27.4 | 2,802 | **0.45** | **0.39** |
| contest | main | 279,467 | 153 | 30.9 | 2,593 | 0.29 | 0.23 |
| contest | near | 30,610 | 174 | 33.1 | 2,205 | 0.29 | 0.22 |
| contest | away | 119,811 | 181 | 31.3 | 3,076 | 0.30 | 0.26 |
| farm | main | 197,360 | 122 | 22.1 | 2,500 | 0.11 | 0.08 |
| farm | near | 24,557 | **170** | **31.0** | 1,541 | 0.13 | 0.11 |
| farm | away | 178,837 | 110 | 15.9 | 1,959 | 0.14 | 0.11 |

Per split episode:

| category | episodes | median length | gold / episode | gems / episode | camp groups hit (median) | with a death | on the enemy half | team fights at its spot | fights elsewhere | joined those |
|---|---|---|---|---|---|---|---|---|---|---|
| close | 774 | 32 | 71 | 11.3 | 1 | 11% | 12% | 342 | 586 | 20% |
| contest | 1,848 | 32 | 79 | 13.4 | 1 | 8% | 15% | 696 | 1,412 | 17% |
| farm | 2,906 | 38 | 54 | 7.7 | 1 | 6% | 9% | 654 | 1,887 | 11% |

- A split is **one camp on their own half, ~30-40 rounds**, worth about one wolf or elk reward (54-79 gold, 8-13 gems).
- **Satellites earn most:** champions just outside the group (within 8) earn the most gold and gems per round in every category
  and die no more than the group. Far splitters earn as much as the group or more on close / contest maps and less on farm maps
  (110 vs 122 gold, 16 vs 22 gems per 100 rounds: longer walks).
- **Dying:** on close maps split champions die 45% more per round than the group (0.45 vs 0.31 per 100 rounds); on contest and
  farm maps about the same (0.30 vs 0.29; 0.14 vs 0.11).
- **They do not come back for fights:** of team fights that start elsewhere during a split, the split champion joins (hits, is hit, or
  comes within 6 of the fight in 15 rounds) only 11-20%.

## 5. Contest vs farm: contact, fights, territory

| category | games | first contact (enemy within 5) | first PvP hit | champions in the first fight (both teams, first 10 rounds) | deaths in it | in the mid zone | mid-zone share of active rounds r0-300 / 300+ | enemy half r0-300 / 300+ | PvP kills per team <300 / 300-700 / 700+ | kills made on the enemy's half | length |
|---|---|---|---|---|---|---|---|---|---|---|---|
| close | 34 | r14 | r19 | 4 | 1.06 | 38% | 50% / 50% | 10% / 16% | 2.6 / 3.5 / 4.1 | 48% | 1,059 |
| contest | 62 | r36 | r44 | 4 | 1.03 | 32% | 24% / 28% | 10% / 13% | 2.3 / 3.0 / 3.1 | 56% | 950 |
| farm | 44 | r86 | r103 | 2 | 0.56 | 33% | 13% / 18% | 7% / 9% | 0.9 / 1.6 / 1.9 | 47% | 984 |

- **Fights are skirmishes, not team fights:** fights that kill someone involve a median 2 champions a side (mean 2.5 close /
  contest, 2.0 farm), 1.3-1.5 deaths each, 13.5 / 10.8 / 6.9 per game (3.3 / 2.8 / 1.5 before r300); 69-74% happen on one team's
  half, 26-31% in the mid zone. The first fight is a 2v2 on close/contest maps and a 1v1 on farm maps.
- **Invading is rare everywhere:** 7-16% of active rounds on the enemy half; but about half of all kills (47-56%) are made there
  (the victim on its own half). Contest maps: the most enemy-side kills (56%).
- By picks: 4-pick contest maps fight earliest among contest maps (first hit r26, 8.4 kills / team-game), 3-pick contest the
  latest (r61, 5.9); farm 4-pick maps (00rows, 01shortcut) barely fight (first hit r414, 1.6 kills).

**Boss maps** (monolith / golem groups hold 30%+ of the gems; party = the team's champions within 6 of the boss while it damages it):

| boss | maps | team-games | hit it | first hit p25 / med / p75 | party median (3+ share) | most present |
|---|---|---|---|---|---|---|
| monolith, close/contest | 9 | 36 | 25 | r507 / **r591** / r719 | 3 (53%) | Vesper 81%, Varg 78%, Ryth 76%, Ren 75%, Vendetta 65%, Marcella 57%, HoR 50% |
| monolith, farm | 5 | 20 | 9 | r733 / r927 / r1020 | 1 (3%) | Marcella 57%, Vesper 35% |
| golem, close/contest | 4 | 16 | 13 | r30 / **r88** / r479 | 3 (55%) | Ryth 76%, Vesper 75%, Ren 68%, HoR 63% |
| golem, farm | 4 | 16 | 14 | r65 / r332 / r542 | 2 (38%) | Willow 64%, Varg 63%, Ryth 57% |

Monoliths are a **late, 3-champion** objective on contest maps (not the whole team; Willow 36%, Cassi / Issac ~20% present) and
mostly ignored on farm maps; golems are taken early by three.

## 6. Team differences (n = 5-9 farm team-games, 13-17 close+contest per team: directions only)

| team | farm: n | whole team r0-100 | main share r0-200 / 200-700 | first split med (commonest) | away share | kills / deaths | W-L | close+contest: n | whole team r0-100 | main share r0-200 / 200-700 | first split med (commonest) | away share | kills / deaths | W-L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AdAstra | 6 | 17% | 55% / 47% | 18 (Marcella) | 48% | 7.0 / 2.8 | 5-1 | 16 | 35% | 71% / 62% | 104 (HoR) | 30% | 8.7 / 8.6 | 9-7 |
| ClaudusMaximus | 7 | 46% | 64% / 43% | 76 (Marcella) | 45% | 6.7 / 12.9 | 1-6 | 14 | 46% | 71% / 59% | 78 (HoR) | 29% | 8.4 / 14.4 | 4-10 |
| hello | 7 | 26% | 51% / 40% | 21 (Vesper) | 53% | 1.6 / 3.6 | 3-4 | 14 | 40% | 69% / 66% | 68 (Marcella) | 25% | 6.7 / 8.8 | 10-4 |
| IntercontinentalFish | 6 | 60% | 77% / 60% | 85 (Issac) | 33% | 8.3 / 9.8 | 3-3 | 15 | 54% | 81% / 70% | 84 (Vesper) | 23% | 16.4 / 15.8 | 10-5 |
| Mite | 6 | 8% | 49% / 45% | 15 (Vesper) | 50% | 2.0 / 1.7 | 4-2 | 16 | 34% | 68% / 63% | 62 (Vesper) | 27% | 9.0 / 11.0 | 11-5 |
| NEETCoders | 7 | 32% | 56% / 38% | 56 (HoR) | 52% | 1.9 / 5.1 | 1-6 | 14 | 41% | 72% / 60% | 54 (HoR) | 30% | 4.6 / 6.9 | 5-9 |
| newerteam | 6 | 19% | 48% / 41% | 24 (Varg) | 51% | 2.8 / 3.0 | 4-2 | 15 | 37% | 66% / 55% | 114 (Marcella) | 32% | 7.5 / 5.9 | 7-8 |
| policywonk | 9 | 41% | 64% / 47% | 58 (Vendetta) | 44% | 3.2 / 7.8 | 3-6 | 13 | 47% | 74% / 65% | 93 (Vendetta) | 28% | 14.5 / 13.2 | 7-6 |
| printdontint | 7 | 58% | 70% / 47% | 72 (HoR) | 43% | 8.4 / 4.7 | 5-2 | 15 | 41% | 71% / 64% | 80 (HoR) | 27% | 8.5 / 11.5 | 9-6 |
| prismbestgirl | 5 | 51% | 73% / 52% | 73 (Vendetta) | 42% | 1.0 / 3.4 | 3-2 | 17 | 46% | 79% / 65% | 78 (Marcella) | 26% | 9.0 / 14.9 | 8-9 |
| SpongeAlbertandBob | 8 | 39% | 63% / 48% | 50 (Marcella) | 44% | 6.5 / 2.5 | 7-1 | 13 | 45% | 72% / 61% | 106 (HoR) | 31% | 14.6 / 9.0 | 8-5 |
| TrzyKwaterki | 7 | 22% | 57% / 44% | 38 (Vendetta) | 48% | 4.6 / 10.4 | 3-4 | 15 | 37% | 71% / 65% | 97 (Marcella) | 26% | 3.5 / 10.5 | 3-12 |
| Univ. of Shingtonwash | 7 | 33% | 68% / 73% | 47 (Vesper) | 29% | 3.9 / 4.7 | 2-5 | 15 | 57% | 82% / 73% | 90 (Varg) | 21% | 7.7 / 12.2 | 5-10 |

Three farm-map styles (direction clear, sizes small):
- **Group, then split at ~r70-85:** Fish (whole team 60% of r0-100, first split r85), print dont int (58%, r72), prism (51%, r73),
  Claudus (46%, r76). On close + contest maps Fish and Univardisty are the most grouped (81 / 70%, 82 / 73%) and Fish kills most
  (16.4 a game).
- **Split from spawn:** Mite (8%, first split r15), Ad Astra (17%, r18), newer team (19%, r24), hello (26%, r21), Trzy (22%, r38):
  about half of active rounds away; few deaths for most of them on farm maps (Mite 1.7, Ad Astra 2.8, newer 3.0, hello 3.6 a game;
  Trzy 10.4).
- **Stay grouped all game:** Univardisty (main share 68% / 73% on farm maps, 29% away).

**Grouping does not decide games.** Same-game comparison, P(the team with the larger value wins): main share r0-700 62% (close,
n 34) / 52% (contest, 62) / 57% (farm, 44); main share r0-200 48-52%; later first split 47% / 50% / 39% (farm: the earlier
splitter won 61%, n 44, ~1.5 SE); enemy-half share 79% / 68% / 62% and kills 86-97% (both mostly consequences of being ahead).
The best farm-map records here come from different styles (Sponge 7-1: whole team 39% of r0-100, first split r50; Ad Astra 5-1:
17%, r18; print 5-2: 58%, r72).

## What this changes in the earlier notes

- `top-teams-1.0.2.md` "Fish keeps four to six together for elk pairs": on 2.0.0 a 5-pick main group is 2.5-2.8 on contest maps
  after r100 and 2.1-2.3 on farm maps; all active champions are together only 17-27% (contest) / 5-9% (farm) of rounds after r100.
  Big groups form for a camp or a fight and dissolve.
- MASTER.md section 7 "opening spread 1.68 teammates within 5" / bot-status "they split early" are confirmed and now dated by map
  class: first 20-round split r46 (farm 5-pick) to r138 (close 3-pick) vs our 120 / 180 / 240-round whole-team openings.
- The farming / control cut the bot uses (45 steps) splits the top teams' behaviour less well than 60 (section "Map categories").

## Rules we could implement (data first, then the guess; none tested yet)

1. **Map class cut at 60 steps, not 45** (data: first PvP hit r46 vs r132, 5.0 vs 1.9 kills before r300, main share 75% vs 61%
   for walks 46-60 vs > 60). Guess: maps of 46-60 steps should get the control opening (180 rounds) and the contest draft rather
   than the race ones. Touches `kRangedSteps` / `kControlDist` users (draft, opening length): screen on the 12 affected maps.
2. **Farm maps (> 60, nearly always 5 picks): open together, then let the gold carries satellite.** Data: group-then-split teams hold
   the whole team for ~70-85 rounds; after that Marcella and Vesper are away 53% / 47% of r200-700, alone (87-89%), on their own
   half (3-11% enemy half), one camp per trip (~38 rounds), and they do not come back for fights elsewhere (11%); the supports
   (Willow, Cassi, Issac) stay in the group most, Willow with Ryth 59-82% of rounds. Guess: opening ~100 instead of 240 on > 60
   maps, then Vesper and Marcella solo own-half camps near the party. **Caution:** shorter openings (kOpenRace 0 -43, #438 60-round
   opening 30 vs 32 on the panel) and satellites / cluster solo (-21..-156, -37) all lost locally, and grouping does not predict
   wins in this data. If tried, use the "near" form (stay within 8 of the group: the best earners per round in every class).
3. **Close 3-4 pick and contest 4-pick maps: the first to leave is usually HoR** (54% / 30% / 32% of first splits), at r89-138,
   alone, on its own half, for ~30 rounds, and it comes back (the commonest 3-pick groups all contain HoR). Our 3-pick draft has no
   HoR, so the analogue is unclear: data only.
4. **Close maps (<= 30 steps): keep everyone within 8.** Split champions there die 45% more per round (0.45 vs 0.31 PvP+camp deaths
   per 100 rounds) and earn the same as the group; the top teams keep 61-81% of active champions in the main group.
5. **Monoliths: no commitment before ~r500 on contest maps; three champions, not five** (first monolith hit median r591, party 3
   in 53% of boss rounds); farm-map monoliths are mostly left (9 of 20 team-games touched one, first at r927). Golems early (r88)
   with three. Compare with our boss mode (one squad of five all game on 48 of 70 maps, MASTER section 9 item 9).
6. **Do not build fight rules around 5v5:** killing fights are 2v2 (median 2 a side), half the kills happen on the victim's own
   half after a short invasion, and split champions rarely respond. A pair arriving fast matters more than the whole team.

## Caveats

- Positions are round starts; "away" counts walking to and from home and recall trips outside the 4-step spawn zone.
- PvP hits are matched by target tile (area spells aimed beside a champion are missed): kills are a lower bound (82% of deaths).
- Per-team cells hold 5-17 team-games; the per-category tables hold 20-80 (8 for farm 4-pick). Maps appear twice each, so map
  effects dominate small cells. Opponents are other top teams only.
- Single-linkage clusters chain: a line of champions 6 apart counts as one group; R = 4 gives the same ordering.
