# Intercontinental Fish: builds, drafts and purchases (Oct 31 study, engine 2.0.0)

Eric (Oct 31): "analyse Fish's recent games and their build paths on all the champions and map types". Fish = Intercontinental Fish
(team 1890540d-...), **ladder rank 1 at 2,562** on Oct 31 00:30 UTC (Ad Astra 2,449, Mite 2,428, prism 2,423). A deeper, Fish-only,
map-class-split follow-up of `top-builds-1031.md` (whose Fish rows are Fish's *old* version, A below).
Everything in tables is measured; lines starting **Guess:** are interpretation.

**Data**
- All of Fish's ranked games from 2026-10-30 00:00 to 2026-10-31 00:30 UTC: **739 games** (both sides engine 2.0.0), listed by
  `tools/stress/fishlist.py` into `results/fish1031/matches.jsonl`.
- **Fish resubmitted at ~15:55 UTC Oct 30** (every draft changed between the 15:50 and 16:00 match batches; nothing changed after):
  - **version A** (old, = the Fish rows of `top-builds-1031.md`): 480 games, **249-231 (52%)**, vs the current top 10 210-200.
  - **version B** (new): 259 games, **204-55 (79%)**, vs the current top 10 **191-53**. Per opponent A -> B: Mite 22-48 -> 27-13, prism
    34-41 -> 33-7, Ad Astra 34-41 -> 29-10, newer 26-19 -> 25-5, hello 33-12 -> 19-6, print 13-17 -> 21-4, NEET 38-17 -> 14-1, Univ
    6-4 -> 19-6. (The opponents also update; the jump is across all of them.)
- Builds and purchases: match summaries (`cambc matches summary`, cached in `results/sum/`): **all 259 B games** (1,351 champion-games
  in the tables: 01boss_battle's 9 games are left out of the build tables because boss gold gives Vesper 40-164 emblems a game) and
  178 of the 480 A games (newest first; 170 used, 863 champion-games). Ours for comparison: our last 70 ranked games (Oct 30 22:20 -
  Oct 31 00:30: 55 of the version live before 00:10, 15 of #458); none of our 70 was against a top-10 team, Fish's B games almost all are.
- Opponent strength: 244 of the 259 B games are against the current top 10 (ranks 2-10), only 15 against others (policy wonk 13-2),
  so a top-10-vs-others build split is not possible (the 5-14 "others" games per champion show the same first three emblems).
- Map class = spawn-walk band of `top-teams-grouping-1031.md` (close <= 30, contest 31-60, farm > 60 steps); pick count is fixed per map.
- Tools (new): `tools/stress/fishlist.py` (one team's ranked list), `tools/stress/fishreport.py` (drafts, builds by version x class x
  picks, paths, timing, wins vs losses, purchases, stat shares, emblem kinds; env TEAM / SPLIT / EXCL / ONLY); summaries fetched with
  `tb1031sum.py` (TEAMS="Intercontinental Fish"). Outputs: `results/fish1031/report_B.txt`, `report_A.txt`, `report_B_C.txt` /
  `_P1` / `_P2` (map groups below), `report_us.txt`, `md_tables.txt`.
  Re-run: `SINCE=2026-10-30T15:58 EXCL=01boss_battle python -I tools/stress/fishreport.py results/fish1031/matches.jsonl`.

Short names: Cap Capture, Tre Treasure, Jun Jungle, Mon Monster, Hun Hunter, Dur Durability, Col Collectors, Bru Bruiser, Pro
Prospector, Pow Power, Hom Home; -S / -F / -H = Strength / Focus / Health. Emblem passives (2.0.0, `patch-sprint3.md`): Capture =
captures take 3 turns instead of 5 (if present when the capture starts); Monster +15% camp damage; Jungle -30% camp damage taken;
Hunter +50 gold a champion kill; Collectors +1% damage per distinct emblem family held; Prospector +25% of your cluster rewards;
Treasure +10% gold; Durability -10% damage taken.

---

## 0. Headline (data)

1. **Fish B is a new build system, not a tweak.** Version A opened Treasure on every carrier (Tre-S Vesper r139, Tre-H Marcella r109,
   Tre-H Vendetta r261, Tre-H HoR r379) and used none of the Sprint 3 emblems. Version B opens **Capture** on every champion that
   captures camps (Marcella Cap-F r110, Vesper Cap-S r108, Vendetta Cap-H r167, HoR Cap-H r236 on the Capture maps), then **Jungle ->
   Monster -> Hunter Health -> Durability Health (-> Collectors) -> Bruiser stack**. Treasure survives only on Vesper (2nd).
2. **Two templates chosen by map** (the same map always gets the same first emblem: 0 of 323 champion x map pairs show two): Capture-first
   on 46 of the 64 maps with B games; **Prospector-first** on 9 cluster-farm maps (main-stat Prospector, then Monster, Jungle Health,
   Durability Health, Bruiser) and on 9 others (Prospector Health on HoR / Vendetta, Focus on Marcella).
3. **Drafts changed with it:** Marcella replaced Vesper as first pick on most 4- and 5-pick maps (Mar>Ven>HoR>C&I(>Willow)), Willow
   replaced Marcella / Ren as the 5th, and C&I joined every 3-pick draft (Ves>Mar>C&I, Ves>HoR>C&I, Mar>HoR>C&I).
4. **On maps where the draft did not change** (Ves>Ven>HoR>Varg>C&I, Ves>Ven>HoR>C&I>Ren, 00swirl / 01shortcut / 00rows) Fish went from
   **54-41 (57%) to 32-12 (73%)** - the build change (plus whatever else changed in the same submission) is worth a lot by itself.
5. **Timing:** Fish's Marcella completes her first emblem at r116 (ours r204), Vesper r157 (ours r216, our #458 r282), HoR r232 (ours
   r216); gold earned by r600 Marcella 1,398 (ours 912), Vesper 1,252 (ours 582), HoR 460 (ours 376) - Fish against the top 10, we
   against teams outside it.

## 1. Drafts (data)

Per pick count and map class, ordered picks with records. **Every map gets exactly one draft per version.**

| version | picks | close | contest | farm |
|---|---|---|---|---|
| A | 3 (93, 32-61) | Ves>HoR>Mar 41 (14-27) | Ves>HoR>Mar 36 (11-25); Ves>HoR>Ven 16 (7-9) | - |
| A | 4 (96, 62-34) | Ves>Ven>HoR>C&I 30 (21-9) | Ves>Ven>HoR>C&I 53 (33-20) | Ves>Ven>HoR>Varg 9 (5-4); Ves>Ven>HoR>C&I 4 (3-1) |
| A | 5 (291, 155-136) | Ves>Ven>HoR>C&I>Mar 33 (16-17) | Ves>Ven>HoR>C&I>Mar 97 (55-42); >C&I>Wil 23 (15-8) | Ves>Ven>HoR>Varg>C&I 61 (37-24); >C&I>Ren 52 (22-30); >C&I>Mar 25 (10-15) |
| **B** | 3 (41, 30-11) | **Ves>Mar>C&I 17 (15-2)**; Ves>HoR>C&I 4 (4-0); Mar>HoR>C&I 3 (3-0) | Ves>HoR>C&I 9 (3-6); Ves>Mar>C&I 8 (5-3) | - |
| **B** | 4 (63, 53-10) | **Mar>Ven>HoR>C&I 24 (21-3)**; Ves>Ven>HoR>C&I 4 (4-0) | **Mar>Ven>HoR>C&I 29 (23-6)** | Ves>Ven>HoR>Varg 4 (4-0); Ves>Ven>HoR>C&I 2 (1-1) |
| **B** | 5 (155, 121-34) | **Mar>Ven>HoR>C&I>Wil 14 (12-2)**; Ves>Ven>HoR>C&I>Wil 3 (3-0) | **Mar>Ven>HoR>C&I>Wil 53 (44-9)**; Ves>Ven>HoR>C&I>Wil 12 (8-4) | Mar>Ven>HoR>C&I>Wil 30 (24-6); **Ves>Ven>HoR>Varg>C&I 27 (20-7)**; Ves>Ven>HoR>C&I>Wil 9 (7-2); Ves>Ven>HoR>C&I>Ren 7 (3-4) |

Which maps moved where (A draft -> B draft; records A / B):

| picks | A draft | B draft | A | B | maps |
|---|---|---|---|---|---|
| 3 | Ves>HoR>Mar | **Ves>Mar>C&I** | 16-20 | **16-2** | 00anvil, 00fragment, 00packs, 02arena (close), 02the_pond (contest) |
| 3 | Ves>HoR>Ven | Ves>Mar>C&I | 7-9 | 4-3 | 00breadcrumbs, 01gold_rush (contest) |
| 3 | Ves>HoR>Mar | Ves>HoR>C&I | 7-24 | 7-6 | 02the_pack (close), 00collision, 01broken_curve, 01the_farm (contest) |
| 3 | Ves>HoR>Mar | Mar>HoR>C&I | 2-8 | 3-0 | adgato_gemcombat1 (close) |
| 4 | Ves>Ven>HoR>C&I | **Mar>Ven>HoR>C&I** | 51-26 | **44-9** | 00oasis, 00reverse_spiral, 00rushbait_v2, 00the_line, 02stalactites (close); 00gemfight, 00interlock, 00quarry, 00vault, 01hooks, 02guardians, adgato_gemcombat2/3 (contest) |
| 4 | Ves>Ven>HoR>C&I | same | 6-4 | 5-1 | 00swirl (close), 01shortcut (farm) |
| 4 | Ves>Ven>HoR>Varg | same | 5-4 | 4-0 | 00rows (farm) |
| 5 | Ves>Ven>HoR>C&I>Mar | **Mar>Ven>HoR>C&I>Wil** | 47-47 | **58-7** | 00lost_world, 01elk_arena (close); 00contest, 00elkring, 00gem_fields, 00monolith, 00quadrants, 02crossing, 02fields, 02uncharted_lands, adgato_gemcombat4 (contest); 00great_wall, 00lanes, 00split, 02famine (farm) |
| 5 | Ves>Ven>HoR>C&I>Ren | Mar>Ven>HoR>C&I>Wil | 12-12 | 12-6 | 00dunes, 00galaxy, 00ribs (farm) |
| 5 | Ves>Ven>HoR>C&I>Wil | Mar>Ven>HoR>C&I>Wil | 15-8 | 10-4 | 00eight, 01corridors, 01starfish (contest) |
| 5 | Ves>Ven>HoR>C&I>Mar | Ves>Ven>HoR>C&I>Wil | 13-14 | 11-4 | 02treasure_box (close), 01boss_battle, 02gift_wrapping (contest) |
| 5 | Ves>Ven>HoR>C&I>Ren | Ves>Ven>HoR>C&I>Wil | 2-7 | 7-2 | 00pilgrimage, 01fracture (farm) |
| 5 | Ves>Ven>HoR>Varg>C&I | same | 37-24 | 20-7 | 00ambush, 00expanse, 00road_of_riches, 01big_world, 01islands, 02geodes, 02harvest, 02tangle (farm) |
| 5 | Ves>Ven>HoR>C&I>Ren | same | 6-9 | 3-4 | 01concentrated_wealth, 01starvation (farm) |
| 5 | Ves>Ven>HoR>C&I>Mar | (no B game yet) | 21-13 | - | 01yellow_brick_road, adgato_gemcombat5 (close); 00corners, 00crater, 00stampede (contest) |

- B's core is **Marcella + Vendetta + HoR + C&I**; Vesper is kept on the Varg cluster-farm maps, on 3-pick maps, and on five 5-pick maps
  (Ves>Ven>HoR>C&I>Wil: 02treasure_box, 01boss_battle, 02gift_wrapping, 00pilgrimage, 01fracture). Willow is now the 5th pick
  everywhere except the Varg / Ren maps. No Ryth, Prism, Tavi or Stellar in either version.
- The weakest B cell is **3 picks on contest maps (8-9)**: Ves>HoR>C&I 3-6 on 00collision / 01broken_curve / 01the_farm.
- **Guess:** the draft rule looks like "Marcella first unless the map is a cluster-farm map (Varg) or has a boss / long Vesper loop";
  the 5 maps with no B game yet will probably get Mar>Ven>HoR>C&I>Wil (they had A's main 5-pick draft).

## 2. Builds by map group (data) - the clearest view of version B

The first emblem is a pure function of the map (Section 2.2), so the B games split into three groups; within a group the lines are
stable. "share" = share of that champion's games completing the emblem at least once; r = median round of the first completion.

**C = Capture-first maps (46 maps; 191 games, 155-36, without 01boss_battle's 9)** (`report_B_C.txt`):

| champion | n | first six emblems: commonest per position (share, median round) | modal first four (share) | emblems by r600 | end S/F/H |
|---|---|---|---|---|---|
| Marcella | 150 | Cap-F 97% r110 > Jun-F 93% r193 > Mon-F 67% r230 (/Bru-H 25%) > Bru-H 55% r334 > Dur-H 44% r354 > Bru-F 53% r441, then Bru-F / Bru-H | Cap-F > Jun-F > Mon-F > Bru-H (54%) | 8.7 | 0/63/37 |
| Vendetta | 152 | Cap-H 99% r167 > Jun-S 94% r267 > Mon-S 70% r343 > Hun-H 45% r392 > Dur-H 39% r434 > Col-S 35% r589, then Bru-S | Cap-H > Jun-S > Mon-S > Hun-H (43%) | 5.7 | 75/0/25 |
| HoR | 168 | Cap-H 93% r236 > Jun-F 83% r367 > Mon-F 61% r521 > Hun-H 38% r555 > Bru-H 35% r642 > Bru-H 36% r659 | Cap-H > Jun-F > Mon-F > Hun-H (38%) | 2.7 | 0/30/70 |
| Vesper | 64 | Cap-S 100% r108 > Tre-S 61% r161 (/Jun-S 33%) > Jun-S 53% r286 > Mon-S 41% r311 (/Hun-H 23%) > Mon-S / Hun-H > Dur-H 31% r391, then Col-S, Bru-S / Bru-H | Cap-S > Tre-S > Jun-S > Mon-S (31%) | 12.5 | 56/0/44 |
| Cassi | 191 | Pow-F 70% r328 > Dur-F 48% r493 > Bru-H 41% r621 > Bru-H stack | - (21% none) | 1.4 | 0/48/52 |
| Issac | 191 | Pro-H 69% r350 > Bru-H 39% r524 > Dur-H 28% r619 > Pow-S 23% r700 > Pow-S | Pro-H (30%) | 1.0 | 32/0/68 |
| Willow | 104 | Pro-H 39% r441 > Pow-S 20% r680 > Hom-H 8% (60% of Willows complete no emblem) | - | 0.5 | 30/0/70 |

Emblem families held (share of games, first completion) on the Capture maps, e.g. **Vesper on close maps (28 games): Cap-S 100% r83,
Tre-S 100% r142, Jun-S 100% r186, Mon-S 100% r218, Hun-H 100% r257, Dur-H 100% r328, Col-S 100% r352, Bru-S 100% r365, Bru-H 96% r533**
- eight distinct families by r365, then the Collectors emblem (+8% damage) and the Bruiser stack. Vendetta (all B): Mon-S 85%, Hun-H 65%,
Dur-H 71%, Col-S 55% r525, Bru-S 60% r550. Marcella: Mon-F 95%, Bru-H 90%, Dur-H 87%, Bru-F 84% (no Hunter, no Collectors).

**P1 = cluster-farm maps** (00ambush, 00expanse, 00road_of_riches, 00rows, 01big_world, 01islands, 02geodes, 02harvest, 02tangle - the
Varg-draft maps; 31 games, 24-7) (`report_B_P1.txt`): **main-stat Prospector first on everyone**, no Capture:

| champion | n | emblems (share, first completion) | end S/F/H |
|---|---|---|---|
| Vendetta | 31 | Pro-S 100% r149, Mon-S 94% r222, Jun-H 90% r359, Dur-H 87% r508, Bru-S 77% r508 | 80/0/20 |
| HoR | 31 | Pro-F 94% r201, Mon-F 87% r265, Jun-H 68% r298, Dur-H 61% r431, Bru-F 58% r460 | 0/79/21 |
| Vesper | 31 | Pro-S 100% r258, Mon-S 97% r372, Jun-H 90% r414, Dur-H 77% r496, Bru-S 65% r528 | 75/0/25 |
| Varg | 31 | Pro-S 87% r266, Mon-S 74% r415, Jun-H 65% r497, Dur-H 61% r615, Bru-S 48% r620 | 72/0/28 |
| Cassi / Issac | 27 | Pro-F 37% r223, Mon-F 22% / Pro-S 59% r406, Mon-S 41% | - |

**P2 = Prospector-Health / Focus maps** (00lost_world, 00the_line, 00vault, 02stalactites, adgato_gemcombat2/3/4, and the 3-pick
Ves>Mar>C&I maps 00breadcrumbs, 02the_pond; 28 games, 20-8, median game 600 rounds) (`report_B_P2.txt`): Marcella **Pro-F 93% r202**, Jun-F 82%
r245, Mon-F 82% r388, Bru-H 68%, Dur-H 64%, Bru-F 54%; Vendetta **Pro-H 88% r210**, Jun-S 54% r184, Mon-S 42%; HoR **Pro-H** 62% r266.

Records by group, A -> B: Capture maps 185-176 (51%) -> 160-40 (80%); P1 42-28 (60%) -> 24-7 (77%); P2 22-27 (45%) -> 20-8 (71%).

- **Guess:** P1 / P2 are the maps whose reachable rewards sit mostly in gem / gold clusters (vault has 49 clusters; the Varg maps are the
  cluster-loop farm maps), where Prospector's +25% pays and captures are few. Not measured here: the map files' cluster share would test it.

### 2.1 Per champion x map class x pick count (data; `md_tables.txt`)

line = commonest emblem at each position (share of the cell's games, median completion round; /2nd choice if 15%+); modal first four
= the commonest first-four sequence and its share (stability); end emblems = held at the end, per game; S/F/H = shard-equivalent stat
shares (an emblem = its 5 shards) at r600 and at the end. Mixed cells (farm 5p) mix the Capture and Prospector maps - read Section 2
for those. Vesper's close 4p (00swirl) and close / contest 5p cells (3-4 games) are outliers with 23-45 Bruiser emblems a game.

#### Vesper

| cell (class, picks) | n | W-L | median rounds | line: emblem at positions 1-6 (share, median round; /2nd choice if 15%+) | modal first four (share) | emblems by r600 | end emblems / game | S/F/H r600 | S/F/H end |
|---|---|---|---|---|---|---|---|---|---|
| all | 97 | 72-25 | 1030 | Cap-S 66% r108 (/Pro-S 23%) > Tre-S 41% r169 (/Jun-S 23%) > Jun-S 36% r294 > Mon-S 30% r323 (/Dur-H 16%) > Mon-S 25% r222 (/Hun-H 21%) > Bru-S 30% r511 (/Dur-H 24%) | Cap-S > Tre-S > Jun-S > Mon-S (21%) | 9.8 | Bru-S 7.8, Bru-H 6.5, Mon-S 1.0, Dur-H 0.9 | 70/0/30 | 58/0/42 |
| close 3p | 21 | 19-2 | 1275 | Cap-S 100% r104 > Tre-S 86% r144 > Jun-S 76% r233 > Mon-S 62% r297 (/Hun-H 24%) > Hun-H 38% r376 (/Mon-S 33%) > Dur-H 43% r527 (/Hun-H 24%) | Cap-S > Tre-S > Jun-S > Mon-S (52%) | 9.7 | Bru-S 11.2, Bru-H 9.7, Mon-S 1.0, Dur-H 1.0 | 73/0/27 | 58/0/42 |
| close 4p | 4 | 4-0 | 1002 | Cap-S 100% r33 > Tre-S 50% r104 (/Jun-S 25%) > Hun-H 50% r218 (/Mon-S 25%) > Jun-S 50% r218 (/Tre-S 25%) > Mon-S 50% r218 (/Bru-S 25%) > Bru-S 100% r254 | Cap-S > Tre-S > Hun-H > Jun-S (50%) | 35.2 | Bru-H 44.8, Bru-S 16.0, Mon-S 1.0, Dur-H 1.0 | 56/0/44 | 31/0/69 |
| close 5p | 3 | 3-0 | 800 | Cap-S 100% r79 > Tre-S 67% r71 (/Jun-S 33%) > Hun-H 33% r110 (/Jun-S 33%) > Jun-S 33% r110 (/Mon-S 33%) > Mon-S 33% r110 (/Bru-S 33%) > Bru-S 67% r161 (/Dur-H 33%) | Cap-S > Tre-S > Hun-H > Jun-S (33%) | 22.7 | Bru-S 11.7, Bru-H 8.7, Mon-S 1.0, Dur-H 1.0 | 67/0/33 | 60/0/40 |
| contest 3p | 17 | 8-9 | 1079 | Cap-S 88% r50 > Jun-S 65% r121 (/Tre-S 29%) > Tre-S 53% r121 (/Jun-S 29%) > Hun-H 35% r166 (/Mon-S 29%) > Hun-H 47% r406 (/Mon-S 41%) > Dur-H 24% r162 (/Mon-S 18%) | Cap-S > Jun-S > Tre-S > Hun-H (29%) | 12.9 | Bru-S 11.5, Bru-H 9.6, Mon-S 1.0, Tre-S 1.0 | 72/0/28 | 58/0/42 |
| contest 5p | 3 | 3-0 | 568 | Cap-S 100% r30 > Jun-S 100% r87 > Mon-S 67% r87 (/Tre-S 33%) > Tre-S 67% r87 (/Hun-H 33%) > Col-S 67% r104 (/Mon-S 33%) > Dur-H 67% r104 (/Bru-S 33%) | Cap-S > Jun-S > Mon-S > Tre-S (67%) | 24.3 | Bru-S 12.0, Bru-H 5.3, Mon-S 1.0, Dur-H 1.0 | 69/0/31 | 69/0/31 |
| farm 4p | 6 | 5-1 | 1034 | Pro-S 67% r188 (/Cap-S 33%) > Mon-S 67% r291 (/Jun-S 17%) > Jun-H 50% r509 (/Tre-S 17%) > Mon-S 33% r752 (/Dur-H 33%) > Hun-H 33% r777 (/Bru-S 33%) > Bru-S 33% r877 (/Col-S 17%) | Pro-S > Mon-S > Jun-H > Dur-H (33%) | 2.5 | Bru-S 1.3, Mon-S 1.0, Dur-H 0.7, Pro-S 0.7 | 73/0/27 | 70/0/30 |
| farm 5p | 43 | 30-13 | 891 | Cap-S 37% r299 (/Pro-S 37%) > Tre-S 28% r249 (/Pro-S 23%) > Jun-S 26% r444 (/Jun-H 26%) > Dur-H 26% r443 (/Mon-S 16%) > Bru-S 30% r530 > Bru-S 35% r530 (/Dur-H 16%) | Pro-S > Jun-H > Mon-S > Dur-H (9%) | 5.3 | Bru-S 4.3, Mon-S 0.9, Bru-H 0.9, Dur-H 0.8 | 73/0/27 | 74/0/26 |
| *old version A, all* | 170 | 92-78 | 1028 | Tre-S 71% r137 (/Jun-S 16%) > Jun-S 46% r257 (/Tre-S 19%) > Bru-H 56% r328 > Dur-H 39% r381 (/Bru-S 24%) > Bru-S 41% r443 (/Dur-H 19%) > Bru-S 54% r460 | Tre-S > Jun-S > Bru-H > Dur-H (25%) | 5.8 | Bru-S 8.3, Pow-S 1.0, Tre-S 0.9, Jun-S 0.8 | 79/0/21 | 88/0/12 |

#### Vendetta

| cell (class, picks) | n | W-L | median rounds | line: emblem at positions 1-6 (share, median round; /2nd choice if 15%+) | modal first four (share) | emblems by r600 | end emblems / game | S/F/H r600 | S/F/H end |
|---|---|---|---|---|---|---|---|---|---|
| all | 209 | 169-40 | 846 | Cap-H 72% r167 > Jun-S 72% r267 > Mon-S 58% r341 > Hun-H 35% r392 (/Dur-H 21%) > Dur-H 31% r435 > Col-S 26% r599 (/Bru-S 23%) | Cap-H > Jun-S > Mon-S > Hun-H (32%) | 5.2 | Bru-S 4.4, Mon-S 0.9, Jun-S 0.8, Cap-H 0.7 | 64/0/36 | 75/0/25 |
| close 4p | 28 | 25-3 | 961 | Cap-H 71% r226 (/Jun-S 18%) > Jun-S 82% r341 (/Pro-H 18%) > Mon-S 75% r373 (/Hun-H 18%) > Hun-H 54% r461 (/Mon-S 18%) > Dur-H 39% r487 > Col-S 29% r592 (/Bru-S 25%) | Cap-H > Jun-S > Mon-S > Hun-H (36%) | 4.6 | Bru-S 4.0, Jun-S 1.0, Mon-S 1.0, Hun-H 0.9 | 55/0/45 | 72/0/28 |
| close 5p | 17 | 15-2 | 1018 | Cap-H 59% r100 (/Pro-H 35%) > Jun-S 71% r232 > Mon-S 53% r338 (/Hun-H 18%) > Hun-H 35% r396 (/Mon-S 18%) > Dur-H 41% r389 > Col-S 35% r516 | Cap-H > Jun-S > Mon-S > Hun-H (35%) | 5.5 | Bru-S 7.8, Jun-S 0.8, Mon-S 0.7, Dur-H 0.6 | 63/0/37 | 82/0/18 |
| contest 4p | 29 | 23-6 | 770 | Cap-H 66% r186 (/Pro-H 24%) > Jun-S 72% r267 > Mon-S 55% r413 > Dur-H 28% r643 (/Hun-H 21%) > Hun-H 28% r643 (/Dur-H 21%) > Col-S 34% r762 (/Bru-S 17%) | Cap-H > Jun-S > Mon-S > Dur-H (28%) | 3.9 | Bru-S 3.0, Jun-S 0.8, Mon-S 0.7, Cap-H 0.7 | 58/0/42 | 71/0/29 |
| contest 5p | 56 | 47-9 | 728 | Cap-H 98% r130 > Jun-S 96% r235 > Mon-S 73% r341 (/Hun-H 21%) > Hun-H 48% r371 (/Mon-S 21%) > Dur-H 41% r413 (/Col-S 18%) > Bru-S 27% r499 (/Col-S 23%) | Cap-H > Jun-S > Mon-S > Hun-H (48%) | 6.7 | Bru-S 4.3, Cap-H 1.0, Jun-S 1.0, Mon-S 0.9 | 66/0/34 | 73/0/27 |
| farm 4p | 6 | 5-1 | 1034 | Pro-S 67% r35 (/Cap-H 33%) > Jun-H 50% r116 (/Jun-S 33%) > Mon-S 83% r116 (/Jun-H 17%) > Dur-H 50% r221 (/Hun-H 33%) > Bru-S 50% r263 (/Dur-H 33%) > Bru-S 83% r296 (/Dur-H 17%) | Pro-S > Jun-H > Mon-S > Dur-H (50%) | 11.7 | Bru-S 15.0, Mon-S 1.0, Dur-H 1.0, Jun-H 0.7 | 81/0/19 | 88/0/12 |
| farm 5p | 73 | 54-19 | 891 | Cap-H 62% r245 (/Pro-S 30%) > Jun-S 53% r316 (/Mon-S 25%) > Mon-S 41% r328 (/Jun-H 22%) > Dur-H 25% r565 (/Hun-H 23%) > Bru-S 29% r539 (/Dur-H 22%) > Col-S 23% r572 (/Bru-S 21%) | Cap-H > Jun-S > Mon-S > Hun-H (21%) | 4.3 | Bru-S 3.5, Mon-S 0.8, Dur-H 0.7, Cap-H 0.6 | 63/0/37 | 74/0/26 |
| *old version A, all* | 134 | 78-56 | 996 | Tre-H 58% r260 (/Mon-S 19%) > Jun-S 42% r366 (/Jun-H 19%) > Bru-H 43% r455 (/Pow-S 19%) > Dur-H 38% r557 (/Pow-S 17%) > Bru-S 33% r644 (/Pow-S 17%) > Bru-S 40% r699 (/Pow-S 17%) | Tre-H > Jun-S > Bru-H > Dur-H (28%) | 3.7 | Bru-S 3.3, Pow-S 1.6, Tre-H 0.7, Jun-S 0.6 | 61/0/39 | 76/0/24 |

#### HoR

| cell (class, picks) | n | W-L | median rounds | line: emblem at positions 1-6 (share, median round; /2nd choice if 15%+) | modal first four (share) | emblems by r600 | end emblems / game | S/F/H r600 | S/F/H end |
|---|---|---|---|---|---|---|---|---|---|
| all | 225 | 179-46 | 852 | Cap-H 70% r236 > Jun-F 64% r359 > Mon-F 48% r520 > Hun-H 28% r550 > Bru-H 26% r642 > Bru-H 27% r659 | Cap-H > Jun-F > Mon-F > Hun-H (28%) | 2.7 | Bru-H 1.5, Cap-H 0.7, Mon-F 0.7, Jun-F 0.7 | 0/48/52 | 0/39/61 |
| close 3p | 7 | 7-0 | 1509 | Cap-H 86% r102 > Jun-F 86% r192 > Mon-F 57% r275 > Hun-H 43% r318 > Bru-H 43% r405 > Bru-H 29% r377 | Cap-H > Jun-F > Mon-F > Hun-H (43%) | 3.7 | Bru-H 6.4, Jun-F 0.9, Cap-H 0.9, Mon-F 0.6 | 0/32/68 | 0/16/84 |
| close 4p | 28 | 25-3 | 961 | Cap-H 71% r247 (/Pro-H 29%) > Jun-F 86% r391 > Mon-F 64% r577 > Hun-H 39% r533 > Bru-H 29% r666 > Bru-H 25% r693 | Cap-H > Jun-F > Mon-F > Hun-H (36%) | 2.4 | Bru-H 1.0, Jun-F 0.9, Cap-H 0.7, Mon-F 0.7 | 0/47/53 | 0/38/62 |
| close 5p | 17 | 15-2 | 1018 | Cap-H 59% r251 (/Pro-H 24%) > Jun-F 53% r334 > Mon-F 47% r449 > Hun-H 41% r546 > Bru-H 47% r550 > Bru-H 47% r555 | Cap-H > Jun-F > Mon-F > Hun-H (41%) | 3.0 | Bru-H 2.9, Mon-F 0.6, Jun-F 0.6, Cap-H 0.6 | 0/31/69 | 0/22/78 |
| contest 3p | 9 | 3-6 | 1079 | Cap-H 100% r155 > Jun-F 78% r252 > Mon-F 78% r316 > Hun-H 44% r370 (/Bru-H 33%) > Bru-H 56% r473 (/Hun-H 33%) > Bru-H 89% r548 | Cap-H > Jun-F > Mon-F > Hun-H (44%) | 4.6 | Bru-H 5.8, Cap-H 1.0, Mon-F 0.9, Jun-F 0.9 | 0/30/70 | 0/18/82 |
| contest 4p | 29 | 23-6 | 770 | Cap-H 59% r427 > Jun-F 48% r678 > Mon-F 34% r678 > Hun-H 24% r673 > Bru-H 17% r878 > Bru-H 10% r736 | (none) (28%) | 1.1 | Cap-H 0.6, Jun-F 0.5, Mon-F 0.4, Hun-H 0.3 | 0/37/63 | 0/39/61 |
| contest 5p | 56 | 47-9 | 728 | Cap-H 95% r252 > Jun-F 84% r304 > Mon-F 64% r521 > Hun-H 36% r529 > Bru-H 23% r602 > Bru-H 27% r673 | Cap-H > Jun-F > Mon-F > Hun-H (36%) | 2.6 | Bru-H 0.9, Cap-H 0.9, Jun-F 0.8, Mon-F 0.7 | 0/45/55 | 0/38/62 |
| farm 4p | 6 | 5-1 | 1034 | Pro-F 67% r110 (/Cap-H 33%) > Mon-F 67% r151 (/Jun-F 33%) > Jun-H 67% r188 (/Mon-F 33%) > Bru-F 50% r394 (/Hun-H 33%) > Dur-H 50% r394 (/Bru-H 33%) > Bru-F 67% r534 (/Bru-H 17%) | Pro-F > Mon-F > Jun-H > Bru-F (50%) | 5.3 | Bru-F 6.3, Mon-F 1.0, Bru-H 1.0, Dur-H 0.7 | 0/69/31 | 0/73/27 |
| farm 5p | 73 | 54-19 | 891 | Cap-H 55% r258 (/Pro-F 30%) > Jun-F 49% r414 (/Mon-F 22%) > Mon-F 32% r439 > Mon-F 15% r378 > Bru-H 21% r746 > Bru-H 22% r634 | Cap-H > Jun-F > Mon-F > Hun-H (14%) | 2.9 | Bru-H 1.2, Bru-F 0.8, Mon-F 0.7, Cap-H 0.5 | 0/58/42 | 0/47/53 |
| *old version A, all* | 170 | 92-78 | 1028 | Tre-H 63% r364 > Jun-F 44% r591 > Bru-H 38% r691 > Bru-H 32% r773 > Bru-H 26% r874 > Bru-H 14% r948 | Tre-H > Jun-F > Bru-H > Bru-H (22%) | 2.0 | Bru-H 1.7, Pow-F 1.0, Tre-H 0.7, Jun-F 0.6 | 0/45/55 | 0/38/62 |

#### Marcella

| cell (class, picks) | n | W-L | median rounds | line: emblem at positions 1-6 (share, median round; /2nd choice if 15%+) | modal first four (share) | emblems by r600 | end emblems / game | S/F/H r600 | S/F/H end |
|---|---|---|---|---|---|---|---|---|---|
| all | 178 | 147-31 | 928 | Cap-F 81% r110 > Jun-F 86% r193 > Mon-F 67% r242 (/Bru-H 22%) > Bru-H 53% r340 (/Mon-F 19%) > Dur-H 42% r368 (/Bru-F 29%) > Bru-F 51% r449 (/Dur-H 29%) | Cap-F > Jun-F > Mon-F > Bru-H (46%) | 8.1 | Bru-F 6.8, Bru-H 4.7, Mon-F 0.9, Jun-F 0.9 | 0/68/32 | 0/63/37 |
| close 3p | 20 | 18-2 | 1176 | Cap-F 100% r104 > Jun-F 100% r211 > Mon-F 80% r254 (/Bru-H 20%) > Bru-H 80% r351 (/Mon-F 15%) > Dur-H 50% r421 (/Bru-F 35%) > Bru-F 55% r517 (/Dur-H 35%) | Cap-F > Jun-F > Mon-F > Bru-H (80%) | 8.8 | Bru-F 11.4, Bru-H 8.9, Mon-F 1.0, Jun-F 1.0 | 0/68/32 | 0/59/41 |
| close 4p | 24 | 21-3 | 954 | Cap-F 67% r131 (/Pro-F 17%) > Jun-F 79% r240 > Mon-F 71% r264 (/Bru-H 21%) > Bru-H 54% r327 > Dur-H 50% r351 (/Bru-F 17%) > Bru-F 62% r477 | Cap-F > Jun-F > Mon-F > Bru-H (33%) | 7.4 | Bru-F 6.1, Bru-H 4.2, Mon-F 1.0, Jun-F 1.0 | 0/67/33 | 0/63/37 |
| close 5p | 14 | 12-2 | 1020 | Cap-F 50% r135 (/Jun-F 29%) > Jun-F 64% r326 (/Pro-F 29%) > Mon-F 79% r326 > Bru-H 57% r430 (/Mon-F 21%) > Bru-F 50% r402 (/Dur-H 36%) > Bru-F 71% r526 | Cap-F > Jun-F > Mon-F > Bru-H (36%) | 7.3 | Bru-F 6.6, Bru-H 5.0, Mon-F 1.0, Jun-F 1.0 | 0/67/33 | 0/61/39 |
| contest 3p | 8 | 5-3 | 1098 | Cap-F 62% r188 (/Pro-F 25%) > Jun-F 88% r188 > Mon-F 62% r471 (/Bru-H 25%) > Bru-H 62% r551 (/Dur-H 25%) > Dur-H 50% r976 (/Mon-F 25%) > Bru-F 88% r461 | Cap-F > Jun-F > Mon-F > Bru-H (38%) | 9.0 | Bru-F 10.2, Bru-H 8.5, Mon-F 1.0, Dur-H 1.0 | 0/67/33 | 0/58/42 |
| contest 4p | 29 | 23-6 | 770 | Cap-F 66% r83 (/Pro-F 24%) > Jun-F 72% r182 > Mon-F 55% r218 (/Bru-H 24%) > Bru-H 31% r351 (/Mon-F 28%) > Bru-F 41% r451 (/Dur-H 21%) > Dur-H 48% r406 (/Bru-F 21%) | Cap-F > Jun-F > Mon-F > Bru-H (28%) | 7.9 | Bru-F 6.3, Bru-H 4.0, Mon-F 0.9, Jun-F 0.9 | 0/69/31 | 0/65/35 |
| contest 5p | 53 | 44-9 | 736 | Cap-F 96% r74 > Jun-F 94% r141 > Mon-F 64% r186 (/Bru-H 25%) > Bru-H 51% r274 (/Mon-F 21%) > Dur-H 47% r281 (/Bru-F 26%) > Bru-F 51% r375 (/Dur-H 36%) | Cap-F > Jun-F > Mon-F > Bru-H (47%) | 10.1 | Bru-F 7.2, Bru-H 4.4, Mon-F 1.0, Jun-F 1.0 | 0/67/33 | 0/65/35 |
| farm 5p | 30 | 24-6 | 888 | Cap-F 90% r166 > Jun-F 90% r321 > Mon-F 67% r343 (/Bru-H 23%) > Bru-H 53% r487 (/Mon-F 17%) > Dur-H 43% r513 (/Bru-F 20%) > Bru-F 47% r656 (/Dur-H 27%) | Cap-F > Jun-F > Mon-F > Bru-H (53%) | 5.2 | Bru-F 3.4, Bru-H 2.1, Mon-F 0.9, Jun-F 0.9 | 0/71/29 | 0/68/32 |
| *old version A, all* | 83 | 42-41 | 1031 | Tre-H 73% r86 (/Jun-S 18%) > Jun-S 49% r270 (/Bru-H 28%) > Bru-H 61% r323 > Dur-H 57% r397 (/Bru-S 28%) > Bru-S 65% r399 (/Dur-H 20%) > Bru-S 78% r428 | Tre-H > Jun-S > Bru-H > Dur-H (31%) | 8.5 | Bru-S 15.3, Tre-H 1.0, Jun-S 1.0, Dur-H 0.9 | 69/0/31 | 85/0/15 |

Others (B, all maps; A for reference):

| champion | B n | B W-L | B line | B emblems by r600 | B end S/F/H | A line |
|---|---|---|---|---|---|---|
| Cassi | 246 | 195-51 | Pow-F 58% r331 > Dur-F 38% r494 > Bru-H 33% r621 > Bru-H stack (31% complete none) | 1.3 | 0/51/49 | Pow-F 45% r444 > Dur-F 24% r680 > Bru-H |
| Issac | 246 | 195-51 | Pro-H 57% r345 > Bru-H 30% r524 > Dur-H 22% r617 > Pow-S 17% r700 > Pow-S (33% none) | 0.9 | 35/0/65 | Tre-S 48% r495 > Pow-S 18% r723 |
| Varg | 31 | 24-7 | Pro-S 61% r343 (/Mon-S 26%) > Mon-S 45% r420 > Jun-H 42% r485 > Dur-H 32% r557 > Bru-S | 2.2 | 72/0/28 | Mon-S 88% r257 > Jun-H 85% r407 > Pow-S stack |
| Willow | 112 | 93-19 | Pro-H 40% r441 > Pow-S 19% r680 > Hom-H 7% (59% none; close maps Pro-H 71% r287) | 0.4 | 31/0/69 | (7 games) Tre-S 43% r562 > Pow-S |
| Ren | 7 | 3-4 | Pro-H 71% r408 > Bru-H 43% r570 > Dur-H 29% r647 > Pow-F | 1.0 | 0/34/66 | Bru-H 74% r340 > Dur-H 61% r666 > Pow-F |

### 2.2 Stability (data)

- First emblem by map is deterministic in B: for each champion and map, every game that completed an emblem had the same first one
  (0 of 323 champion x map pairs differ; Capture maps Cap-x, P1 main-stat Prospector, P2 Pro-H / Pro-F).
- Full first-six paths (`report_B.txt` paths): Marcella **Cap-F > Jun-F > Mon-F > Bru-H > Dur-H > Bru-F 29%** (43-8), the next four
  variants (12%, 7%, 7%, 6%) only reorder Mon-F / Bru-H / Bru-F / Dur-H; Vendetta Cap-H > Jun-S > Mon-S > Hun-H > Dur-H > Col-S 11% (21-1),
  with Hun-H / Dur-H / Col-S / Bru-S reordered in the next variants; HoR Cap-H > Jun-F > Mon-F > Hun-H > Bru-H > Bru-H 14% (26-6);
  Vesper's six-paths are spread (max 7%) because the order of Tre / Jun / Mon / Hun / Dur / Col varies - but the set is the same.
- **Guess:** positions 3-6 follow "next affordable emblem from a fixed set" (or a gold-threshold order), not a fixed list; the set is
  fixed per champion and map group.

### 2.3 Stat shares (data)

| champion | B r300 | B r600 | B end | A end |
|---|---|---|---|---|
| Vesper | 79/0/21 | 70/0/30 | **58/0/42** (Capture maps 56/0/44, P1 75/0/25) | 88/0/12 |
| Vendetta | 54/0/46 | 64/0/36 | 75/0/25 | 76/0/24 |
| HoR | 0/47/53 | 0/48/52 | 0/39/61 (Capture maps 0/30/70; P1 0/79/21) | 0/38/62 |
| Marcella | 0/75/25 | 0/68/32 | **0/63/37** | **85/0/15 (Strength)** |

Marcella switched from a Strength carrier (A: Bruiser S stack, 15 a game) to **Focus + Health** (B: Bruiser F 6.8 + Bruiser H 4.7 a
game); Vesper's late stack is now half Bruiser Health (B: Bru-S 7.8 + Bru-H 6.5 a game; A: Bru-S 8.3, 12% Health).

## 3. Wins vs losses (data; within B, so team strength is fixed)

| champion | wins: modal first three (share), emblems 1-4 (median rounds), by r600, gold r600 | losses: same |
|---|---|---|
| Marcella | Cap-F > Jun-F > Mon-F (59%); r111 / 190 / 236 / 303; 9.1; 1,526 | Cap-F > Jun-F > Mon-F (42%; Pro-F first 19%); r192 / 365 / 537 / 580; 3.5; 400 |
| Vendetta | Cap-H > Jun-S > Mon-S (53%); r154 / 240 / 332 / 392; 5.9; 987 | Cap-H > Jun-S > Mon-S (42%); r273 / 401 / 524 / 534; 2.5; 318 |
| HoR | Cap-H > Jun-F > Mon-F (48%); r218 / 356 / 484 / 530; 3.0; 536 | Cap-H > Jun-F > Mon-F (35%); r260 / 459 / 592 / 692; 1.7; 300 |
| Vesper | Cap-S > Tre-S > Jun-S (28%); r138 / 214 / 277 / 308; 11.1; 1,387 | Cap-S > Tre-S > Jun-S (44%); r195 / 242 / 326 / 301; 5.9; 698 |

- **The path does not change with the result; the timing does** (losses run 60-350 rounds later at every emblem, with a third to half
  the gold by r600). Losses are a bit more often on the Prospector maps (P1 + P2 B record 44-15 vs Capture maps 160-40).
- Opponent strength: no split possible (244 / 259 games vs the top 10); the 5-14 non-top-10 games per champion show the same first three.

## 4. Purchases besides emblems (data)

No item was ever sold (0 sell events in A or B). Consumables are Altar Locks (10 gold) and Teleport Crystals (10 gold); wards are placed
(no purchase).

| per champion-game, B | altar locks (share of games, first) | teleport crystals (share, first) | wards placed | gold on shards | first shard |
|---|---|---|---|---|---|
| Marcella | 2.04 (75%, r103) | 0.16 (2%) | 32 | 2,338 | r76 |
| Vendetta | 1.29 (62%, r108) | 0.83 (12%, r96) | 29 | 1,417 | r78 |
| Vesper | 1.12 (38%, r66) | 1.63 (26%, r53) | 29 | 3,062 | r87 |
| HoR | 0.95 (57%, r166) | 0.68 (13%, r97) | 28 | 776 | r114 |
| Cassi / Issac | 0.69 / 0.73 (51% / 50%, r201-210) | 0.41 / 0.52 (12-14%) | 25 / 28 | 405 / 337 | r170 / r186 |
| Willow | 0.48 (42%, r259) | 0.29 (7%) | 26 | 184 | r262 |
| Varg | 0.29 (16%) | 1.35 (29%, r49) | 16 | 705 | r160 |

- Per team-game B: close maps 6.4 altar locks / 2.1 crystals / 176 wards; contest 6.7 / 0.1 / 150; **farm 3.1 / 8.6 / 128** (crystals
  are a farm-map item: the Varg / cluster maps). A: close 8.0 / 0.7, contest 7.0 / 0.0, farm 2.9 / 6.7.
- Ours (70 games): altar locks 8.3-10.2 a team-game on every class (Marcella 2.9-3.5, Vesper 2.3, Ryth 1.7-2.2 a game, bought in
  87-100% of games from r120-157), crystals 9.8-14.7 on farm maps, wards 99-197 a team-game - **the same shape as Fish's**; Fish buys
  fewer locks on farm maps (3.1 vs our 8.3).

## 5. Comparison with our live #458 (code: `bots/Up458/src/bot.cpp` build_plan; measured: our 70 ranked games, `report_us.txt`)

Our lines (verified in the source): a plan is bought emblem by emblem, then its last entry is stacked forever. kFarmBuild 8 /
kFarmBuildMaps 1 inserts a **Prospector emblem second** for Marcella (F), Vesper (S) and Ryth (H) on maps with a spawn path > 45 or a
boss (seen in 50-100% of our games, close maps included).

| champion | Fish B (Capture maps; Prospector maps) | ours #458 (code) | ours measured (pre-#458 live / #458) | difference |
|---|---|---|---|---|
| **Marcella** | Cap-F r110 > Jun-F r193 > Mon-F r230 > Bru-H r334 > Dur-H r354 > Bru-F r441 > Bru-F / Bru-H; end F 63% H 37%. P2 maps: Pro-F first | kMarcBuild 9: Tre-F > Jun-F > Dur-H > Bru-F stack (+ Pro-F 2nd on long maps) | Tre-F 96-100% r188-235 > Pro-F r286-306 > Jun-F r338-350 > Dur-H r459-496 > Bru-F r533; end F 94% | **Choice:** Capture not Treasure first; Monster 3rd; Bruiser H in the stack (we stack only Bru-F). **Timing:** first emblem 80-120 rounds later; gold r600 912 vs 1,398 |
| **Vesper** | Cap-S r108 > Tre-S r161 > Jun-S r286 > Mon-S r311 > Hun-H / Dur-H > Col-S > Bru-S / Bru-H; end S 56% H 44%. P1: Pro-S r258 > Mon-S > Jun-H > Dur-H > Bru-S | kVespBuild 7: Tre-S > Jun-H > Dur-H > Bru-S stack (+ Pro-S 2nd on long maps) | pre-#458: Tre-S 89% r210 > Jun-S r323 / Pro-S r355 > Dur-H r497 > Bru-S r579; #458: Tre-S 80% r282 > Pro-S r343 > Jun-H r366 > Dur-H r448 > Bru-S r488 | **Choice:** Capture before Treasure; Jungle **Strength** (ours Health); Monster, Hunter, Collectors absent; late stack half Health. **Timing:** first shard r87 vs r168, first emblem r157 vs r216-282; gold r600 1,252 vs 582 |
| **HoR** | Cap-H r236 > Jun-F r367 > Mon-F r521 > Hun-H r555 > Bru-H stack; end F 30% H 70%. P1: Pro-F r201 > Mon-F > Jun-H > Dur-H > Bru-F | kBuild2 bit 8 -> kRuinBuild 4: Tre-H > Jun-F > Bru-F / Bru-H alternating (kHorBuild 1 is never reached) | Tre-H 85-100% r206-348 > Jun-F r424-555 > Bru-F r499-775 > Bru-H r642-837 | **Choice:** Capture H not Treasure H (same stat); Monster F 3rd; Hunter H; Bruiser H only (we alternate F / H). **Timing:** similar first emblem (r232 vs r216), gold r600 460 vs 376 |
| **Vendetta** (we do not draft her) | Cap-H r167 > Jun-S r267 > Mon-S r343 > Hun-H r392 > Dur-H r434 > Col-S r589 > Bru-S stack. P1: Pro-S r149 > Mon-S > Jun-H > Dur-H > Bru-S | kFishBuild bit 8 (off) = Fish's *old* A line Tre-H > Jun-S > Bru-H > Dur-H > Bru-S | - | kFishBuild now copies an abandoned line |
| **Willow** | Pro-H 40% r441 (close 71% r287) > Pow-S; 59% complete none | kBuild2 bit 16: Dur-H > Bru-H > Tre-F stack | Dur-H 36-41% r432-511 > Bru-H r715-1108 | Prospector H vs Durability H as the one emblem; both rarely get two |
| **Ryth** (Fish does not draft her) | - | kRythMix 2: Tre-H > Jun-H > Bru-H / Bru-S alternating (+ Pro-H 2nd on long maps) | Tre-H 87-91% r285-301 > Pro-H r497-530 > Jun-H r603-638 > Bru-H r690-852 | no Fish data |

**Timing vs choice, summarised (data):** Fish's first emblem is earlier on Marcella (r116 vs our r204) and Vesper (r157 vs r216 / r282),
equal on HoR. Per class, Marcella's first emblem: close r137 vs our r188, **contest r84 vs r210**, farm r166 vs r221; gold r600 close 1,253
vs 827, contest 1,563 vs 1,051, farm 695 vs 772. So the Marcella gap is on close / contest maps; on farm maps our Marcella earns as much.
Vesper's gold gap is partly draft: Fish drafts Vesper only on 3-pick, Varg-farm and five 5-pick maps; we draft her everywhere.

## 6. What we could copy

**From data (exact sequences in our item names; B = 79% wins, the lines are identical in wins and losses):**

1. **Marcella (our biggest overlap with Fish B - she is Fish's first pick on 35 of the 64 maps):** Capture Emblem of Focus -> Jungle Emblem of Focus ->
   Monster Emblem of Focus -> Bruiser Emblem of Health -> Durability Emblem of Health -> Bruiser Emblem of Focus, then Bruiser Focus /
   Bruiser Health alternating (Fish ends 63% Focus / 37% Health). As a plan: `{capture_shard_of_focus, jungle_shard_of_focus,
   monster_shard_of_focus, bruiser_shard_of_health, durability_shard_of_health, bruiser_shard_of_focus, bruiser_shard_of_health,
   bruiser_shard_of_focus, ...}`. It differs from our kMarcBuild 9 in three places: Capture for Treasure, Monster added 3rd, Bruiser
   Health mixed into the stack.
2. **HoR:** Capture Emblem of Health -> Jungle Emblem of Focus -> Monster Emblem of Focus -> Hunter Emblem of Health -> Bruiser Emblem of
   Health stack (vs our kRuinBuild 4: Treasure H -> Jungle F -> Bruiser F / H).
3. **Vesper:** Capture Emblem of Strength -> Treasure Emblem of Strength -> Jungle Emblem of Strength -> Monster Emblem of Strength ->
   Hunter Emblem of Health -> Durability Emblem of Health -> Collectors Emblem of Strength -> Bruiser Strength / Bruiser Health
   alternating (vs our kVespBuild 7: Treasure S -> Jungle H -> Durability H -> Bruiser S).
4. **Cluster-farm maps (Fish's P1 group): main-stat Prospector FIRST, then Monster (main stat), Jungle Health, Durability Health, Bruiser
   (main stat)** on every carrier, no Capture: Vesper Pro-S > Mon-S > Jun-H > Dur-H > Bru-S; HoR Pro-F > Mon-F > Jun-H > Dur-H > Bru-F;
   Vendetta Pro-S > Mon-S > Jun-H > Dur-H > Bru-S. Ours puts Prospector second (kFarmBuild 8) and on every spawn-path > 45 map.
5. **Vendetta (if drafted):** Capture H > Jungle S > Monster S > Hunter H > Durability H > Collectors S > Bruiser S stack; kFishBuild bit 8
   (Treasure H first) copies Fish's abandoned A line and should not be used as "Fish's build" any more.
6. **Spend earlier:** Fish's first shard r76-87 on Marcella / Vesper / Vendetta (ours: Marcella r95, Vesper r168, HoR r153).

**Guesses (not measured):**
- Why Capture first: a 3-turn capture (vs 5) frees the capturer 2 rounds per camp and shortens the contested window - Fish gives it to
  every champion that captures (not Willow, C&I). Our Oct 27 local screens found Capture / Prospector emblems neutral or negative
  (MASTER section 9 item 4; item 1 of the same list: our captures 22.7 vs the top teams' 31.1 by r600); Fish's ladder jump says the
  pool screen may not show it - a ladder A/B is the test, not a local screen.
- Monster (+15% camp damage) third and Hunter Health (+50 gold a kill) fourth suggest Fish farms camps faster and kills more in B; the
  Collectors emblem (Vesper, Vendetta) pays only because they hold 6-8 families by r500.
- Which maps are "Prospector maps": probably the cluster-reward share of the map (vault, the Varg farm maps). A general rule from the
  map (cluster gold + gems vs camp gold + gems in reach) would reproduce Fish's split without map names.
- Our Ryth has no Fish counterpart; the template applied to her would be Capture Health > Jungle Health > Monster Strength > ... -
  untested and not backed by any Fish data.
- Part of B's jump is the draft (Marcella first, Willow, C&I at 3 picks) and possibly unseen behaviour changes in the same submission;
  the same-draft maps (57% -> 73%) bound the build-plus-behaviour part, they cannot separate the two.

---

## 6. Update Oct 31 ~05:45 UTC: every map, and the map category behind the templates (data)

- **No resubmission since Oct 30 15:58:** 0 draft changes on any map across all 404 version-B games (to 05:20 UTC Oct 31); since 00:30
  UTC Fish went **126-24**. Version B now covers 69 of 70 maps (01yellow_brick_road unseen). Per-map table: `results/fish1031/maps_B.json`
  (`tools/stress/fishmaps.py`); map features `results/fish1031/mapfeat.json` (`tools/stress/mapfeatures.py`, one trace per map).
- **Every map has exactly one draft and one first emblem per champion.** Three templates (first emblem of the carries):
  - **C, Capture first (50 maps):** Marcella Cap-F, Vendetta Cap-H, HoR Cap-H, Vesper Cap-S; Cassi Pow-F, Issac Pro-H, Willow Pro-H or none.
  - **P1, main-stat Prospector + Varg draft (9 maps: 00ambush, 00expanse, 00road_of_riches, 00rows, 01big_world, 01islands, 02geodes,
    02harvest, 02tangle):** Ves>Ven>HoR>Varg(>C&I); Vesper / Vendetta / Varg / Issac Pro-S, HoR Pro-F (Mon-S / Mon-F on a few).
  - **P2, Prospector Health / Focus on the carries (10 maps: 00breadcrumbs, 00lost_world, 00the_line, 00vault, 02stalactites,
    02the_pond, adgato_gemcombat2-5):** Marcella Pro-F, Vendetta / HoR Pro-H, Vesper Pro-S; Issac / Cassi often nothing.
- **P2 = cluster maps, a clean rule:** nominal gems in cluster-only groups (gem clusters x 7) **>= ~154** separates P2 from C on 59 of
  60 maps (the one miss, 02the_pond, has 70 cluster gems but 47% of its gems in clusters); by share, cluster-only gems >= 47% misses
  00lost_world (40%) and catches 00galaxy (93%, 105 gems) and adgato_gemcombat1 (Capture). Reading: Prospector (+25% cluster rewards)
  first where clusters hold 150+ gems.
- **P1 = big farm maps (the Varg draft), not one clean rule:** best one-feature cut map width >= 100 (64/69); best pair **area >= 6,319
  tiles AND small monster camps (wolves / one elk) >= 18% of the gems: 66/69** - misses 00rows, 01islands, 00road_of_riches, which Fish
  also plays as P1 (rows: two monoliths + 30 clusters, Varg splash; road_of_riches: 74 gem clusters on a 40x40, walk 243). **Guess:**
  a hand-picked list of cluster-loop farm maps, consistent with "big map or cluster loop + Varg".
- **Health vs strength / focus by map (emblems completed by r600, share of Health):** Marcella 30-32% on every class (no map effect);
  Vendetta 40% (close / contest) vs 35% (farm), **26% on P1**; Vesper 37% close vs 27-28% contest / farm; **HoR 60-62% close / contest vs
  41% farm, 24% on P1**; Issac 91-95% vs 73% farm, 31% on P1. So "health on fight maps, full stat on farm maps" holds for HoR, Vesper,
  Vendetta and Issac, and most sharply on the P1 (Varg) maps; Capture farm maps keep the Capture template's health share.
