# Findings

Measured facts that shaped the bot, and what we know about stronger teams. Exact engine numbers live in `docs/MECHANICS.md`. The raw dated logs these come from are in `docs/journal/`.

## Engine and fuel

- The engine is deterministic: the same bots on the same map give the same result, locally and on the platform.
- Every SDK accessor is a host call (about 40 fuel). Read raw structs (`cambc::detail::sdk_champion`, `sdk_camp`) once per unit per turn. Printing is expensive too: heavy per-turn logging cost a bot 18k gem margin locally.
- Always test with `--release`, because the platform runs release builds.
- Our champions hit fuel exhaustion about 10 times per game, against about 4 for rivals, mostly on big maps. `pick_group`'s BFS costs about 45k fuel. (Since the fuel passes of 10-25, cand6: 0.85 per game after round 5 in the local quick pool; see "Code audit" below.)
- `init_world` spreads over the first rounds.

## Camps and economy

- Camps never regenerate or chase. A whole group wakes when one member is hit. A woken camp hits the nearest champion, not the one that woke it. Sleeping camps never attack, even adjacent. Camps fall asleep 2 rounds after no champion is in range.
- Spells reach 4. Camps reach 3, except elks 4, golems 4 and monoliths 5. Casters standing at 4 from range-3 camps take no damage ("standoff").
- Standing on a group's spawn tile blocks its respawn indefinitely.
- Gold gap against the top 10: 79% comes from captures (68 vs 40 clears per game, same ~118 gold per clear) and 21% from kills (kill = 100 gold, assist = 0).
- Opponents capture many small groups and gold clusters near their spawn every 80-110 rounds. Top teams tribute about every 32 gems; our order-quantity batch gives 60-100.
- Items: health emblems matter (all-Power builds lost on the platform). Top teams build Bruiser everywhere, HoR on focus, Marcella on focus (15 focus per shard, spell 2x focus). They buy Monster shards 7-14 per game and altar locks about 4-6 per game. We buy none of either.

## PvP

- Most of our deaths happen while fleeing (51-80% depending on the bot). The typical fatal engagement starts near full hp while walking to a capture, with about 2 allies and 0.8 enemies within 5. It ends 14 rounds later with 0.7-1.8 allies against 2.1-2.5 enemies: their teammates join and ours do not.
- Per-turn 1v1 damage is equal to rivals. Total champion damage is lower only because we die and flee more.
- Ryth and Marcella were starved of gold by slot-order capture sharing. `gb2` fixed it by sharing by fewest owned shards. Overfeeding one champion (gb3) was wasted.
- Platform opponents punish aggression that local bots reward. Blind no-flee play (nf2, ag*) and looser fight entry (pa1, lf1) lost on the platform. Current fight thresholds look like a local optimum both ways (tighter bpt1/bpt2 is also worse).
- Widening the help call made things worse (hc2: whole map 5/20 vs 10/20).

## Maps

- `boss_battle`: the single altar is walled in by a group of 2 monoliths (40000 hp). Nobody can tribute until it dies, so we skip bank trips while it lives (`altar_guard`). Rivals kill it. We have no team monolith assault yet (ag1/ag2 failed).
- `contest`: the only gems are two sleeping monoliths. The enemy farms the 4 centre gold clusters beside them, so we now treat sleeping monoliths as harmless.
- `elk_arena`: all 72 gems are in the centre group. The enemy 5-stack meets us there at rounds 17-30, and we arrive one by one.
- Maps we lose almost every game (panel 8): elk_arena, boss_battle, lanes, contest, starfish, quadrants. Earlier panels: the_farm, starvation, road_of_riches, lost_world, gemfight, hooks. Map facts are in `docs/reference/probe/map_table.md` (gem income per round 1.2-15.7; some maps cannot reach 1000).

## What top teams do (platform summaries, ranks 1-70)

- Attack on sight at the lowest-hp target in range, spells included. They chase 3 turns at most and recall at about 46% hp, never with an enemy within 4.
- They place wards constantly (100-280 per game) and farm in packs early, then fan out.
- Draft meta: Heart of Ruin, Marcella, Vesper, Ryth, Vendetta (in 63-76% of top-10 drafts).
- Kill participation is similar to ours (3+ participants in about 60% of kills). They win fights by numbers arriving and by not fleeing late.

## Rank 30 AlphaSlop (2026-10-23, 40 games vs hb4, run hb4_a@r30)

- hb4 wins 11/40. Deaths 14 vs 7 per game, kills 5 vs 13. Their Vesper kills 7 of ours per game (K/D 5.8/0.8).
- Gold funnel: their Vesper earns 4453 gold and collects 581 gems per game (ours 1505 and 190), Marcella 2688. Both build Treasure, Jungle, Durability, Home emblems, then Power (Vesper about 24 Power strength emblems per game). Copying the Power build alone lost (pv1 5/40).
- Early game: their 3-stack invades our half by round 25-40. 48 of our 78 deaths before round 300 are on our own half. Most fatal fights start with us alone (0 allies near) against 2-3 of them, at 90%+ hp, while fleeing.
- Before round 600 both teams collect the same gems; after round 600 they take 2.4x our gems from the middle.
- They tribute 21 times per game (we 12) and buy about 6 teleport crystals per game, only on wall and water maps (islands, reverse_spiral, split, swirl, shortcut, gold_rush): crystals are shortcuts across walls.
- They do not buy altar locks, and our locks (lkh, 9 per game) did not cut their tributes.
- boss_battle: our bags grow to 1600-1900 gems while the monolith guard blocks the altar, then carriers die one by one at the altar after the guard falls (about 7000 gems lost in one game).
- The ruliad (rank 31) beats AlphaSlop 8-2 in ranked games without winning fights (kills 8 vs 10, deaths 11 vs 9 per game). It banks fast (median 15 rounds from capture to tribute, 71 gems tributed by round 200), loses no bag (median 0), buys altar locks (6.9 per game) and out-clears AlphaSlop (47 vs 32). AlphaSlop collects 740 gems per game against it but 1286 against us: our lost bags are a big part of its income.
- Middle control decides it: mid gems per game before round 600, the ruliad 296 vs AlphaSlop 126, BBL 219 vs 32, hb4 104 vs 108; after round 600 hb4 151 vs 357. Most of our "gems lost" against AlphaSlop is one boss_battle game; elsewhere bag size is close to theirs (36 gems per tribute, median).
- A local imitation (`exp/aslop`: our code plus their Power build, gold funnel, early pack, Home emblem, teleports, frequent tributes) is no proxy: hb4 beats it 72.5% locally against 27.5% vs the real team, map agreement 16/40. Their edge is not in the visible habits.
- Following a teammate's target (pk1 whole team, bd1 pairs) cuts deaths but slows farming more (local 47-60% vs 73%).

## Batch b1 (2026-10-24, panel ranks 81-85)

- Fuel: on big maps `pick_group` overran the 100k budget (the bot then resumes mid-pick next turn and loses that turn). Platform exhaustions per game: big_world 381, road_of_riches 210, boss_battle 210 (rivals 0-15). The BFS from us was 8k-31k and the scoring loop 30k-62k per pick. Exact fixes (same choices): branch-and-bound over groups sorted by a score upper bound (fu1, fu5), and per-group distance fields instead of the BFS (walking distance is symmetric, so the field rooted at a group's camps read at our tile equals the BFS distance; fu4). Local hb4 vs fu5: big_world 370 to 70, road_of_riches 290 to 35, boss_battle 140 to 62.
- Elks reach 4 since 3.0, so `init_units` treats them as covering camps (range > 3). A group within 4 of a living elk group was skipped forever (strength < 100 counts as always covering), even while the elks sleep. starvation: the centre gem cluster beside sleeping elks was farmed 19 times by the enemy, never by us; road_of_riches: two 21-gem clusters on our half. Lifting the cover for everything woke elks (deaths +16% locally); lifting it only for clusters (cv2) fixed starvation's gems (18 to 336) but did not win games.
- Sunk effort: in losses, 63-100% of our champion time (R-line samples) went to groups we never captured, mostly one big contested group the enemy took (starvation g2, pilgrimage g12 704 gems, rows g6 470 gems after we wore it down for 400 rounds). Tool: per-game sample share in the batch-b1 analysis.
- Camp deaths: 40 of 145 base deaths had no enemy in view, 25 of them in `retreat`. The rejoin rule checked only the hardest single camp, so champions rejoined 4 elks (240 per round) at 30-50% health and died.
- Opponents buy altar locks (3-24 consumables per game). On road_of_riches the altars are mid-map and we spent 49-125 bank rounds per champion for 0 tributes.
- Opponent drift: Shawn (rank 85) changed bot between 03:00 and 04:00; our base on its 5 games went 3-2 to 0-5. Rerun the base whenever several variants show the same flips.

## Batch b2 (2026-10-24, panel ranks 83-87)

- Early deaths decide it: in losses 3.5 deaths per game before round 300 (wins 0.9), mostly fleeing 5-15 tiles from our spawn. On 3-champion maps (gold_rush, packs) the enemy 3-stack killed all three of ours by round 40-137. Following a teammate's target (pk6) does not keep champions together: on gold_rush our Vesper still trailed 6-8 tiles and died alone.
- Per-champion damage dealt is 30-100% below theirs (Vendetta 6641 vs 13093, Vesper 11313 vs 16929) although we buy more shards: the gap is fight behaviour, not items.
- Fight changes on this panel: lowest-health prey (lh2) +1, flee only when the sim says we lose (fp1) +1. Less chasing (ch1, 3-turn cap) -6, more engaging on even sims (fp3) -2, sim horizon 5 (sh1) -6, carriers avoid fatal fights (bg1) -1. The same six fp1 wins flip under every change.
- Teleport crystals: -2 on b1 (twice), +3 on b2 (6 wall maps). We buy 3-42 per game.
- The early middle bonus (x2 for mid groups before r400, from hb4) kills small teams: without it b2 went 11 to 17 (gains on 3-4 champion maps: gold_rush, packs, fragment, collision, gemfight) but b2x lost 3 on 5-champion maps. Keeping it only for teams of 5 (nm3) held b2x at 15 and won b2 16; with the exact fuel cache (fx1) 19/25. Judge such changes on both map sets: single-set results flip with map chaos.

## Batch b3 (2026-10-24, panel ranks 62-66)

- Base fx1: 12/25 and 11/25 (second set). Losses again start early: 3.5 deaths per lost game before r300 (wins 0.9), fleeing 5-9 tiles from our spawn with about two enemies near; on swirl an enemy rush killed all four of ours by r90.
- Defences that reacted to packs all failed: hold the spawn (hs1, won swirl but lost 4 others), leave at first sight of 2+ (pe1, 0 flips), flee toward a teammate (fa1, local deaths +42%), wider help call (ec2, 19/50 vs 27).
- Small positive pieces stacked to c5 (27/50 vs 23): the early middle bonus for full teams only until the champion is killed by an enemy (nm5), lowest-health prey (lh3), contested groups cost more after recent deaths (tu2), ability-slot cache (rs1).
- In c5's 11 lost b3/b3x games we died 22.5 times per game, 79% while fleeing; 148 of 195 flee deaths had 2-4 enemies near us (only 38 were 1v1). We get caught spread out.
- The help call (hb4) is tuned: answering within 14 tiles beats wider calls (ec2, -8 over 50 games), no answering (nh1, -7) and a radius of 8 (hc8, -3 on b3).
- Draft on b3: Varg instead of Ryth (dr3) +1 on b3 and -1 on b3x; Marcella second (dr2), Varg second (dr5, dr6), Tavi (dr4), Ryth fifth (dr9) and a Bruiser Varg (dr10) all lost 2-6 on b3. Our Ryth and Vendetta deal half the damage of the rivals' (6.9k vs 11.2k, 5.3k vs 10.5k) but swapping them out does not help.
- Platform group quota (50 groups per 30-minute window) binds with combined 10-group gates: plan at most 4-5 combined gates per hour.

## Decoded replays (vis_decode / rounds_extract, 50 c5 games on b3 + b3x, 2026-10-24)

- Full per-round state of both teams is now available (`tools/replay/rounds_extract.mjs`, about 14 s per game; `tools/replay/fight_geo.py` for team geometry).
- Rivals keep more company: mean teammates within 5 tiles 1.0-1.6 vs ours 0.66-1.22; in our losses the gap is 1.01 vs 0.66 after round 300. Champion-rounds with 2+ teammates within 5: theirs 36%, ours 24%.
- Death hazard depends on company only when enemies are near (about 0 per 1000 rounds with no enemy within 8). With 2 enemies near: alone 5.8 per 1000 rounds, with 2+ mates 2.0. Per situation our hazard equals theirs: we do not fight worse, we are alone more often.
- Rivals clear camps together: 47% of their camp-hit rounds have a teammate hitting a camp within 3 tiles (59% before r600), ours 36% (43%). Our greedy per-champion score ignores the time a joiner saves its teammates.
- Copying the sharing rate does not copy the result: a team-optimal sharing credit (sh3) raised our shared camp hits from 37% to 49% (rivals 47%) and lost 18 of 50 platform games against main's 28. Their sharing is a symptom, not the cause.
- Rival-vs-rival ranked games (95, ranks 55-80, `tools/replay/team_features.py`): winners and losers group the same (teammates within 5: 0.91 vs 0.93; shared camp hits 36% vs 37%). What separates them is deaths (4.9 vs 14.4 per game) and tributes (31 vs 18 per game; 279 vs 208 gems by r600).
- Our early banking is far behind everyone: by r300 we collect 103 gems and tribute 43 (1.6 tributes, first one at median round 279); rivals collect 129 and tribute 85 (3.6, first at round 130), our b3 opponents 156 and 112 (5.0, first at round 102). Our order-quantity batch is about 50 gems early; theirs about 22. We are ahead on items instead: item slots at r600 17.0 vs 14.7, max hp 2071 vs 1779. Forcing small early batches (bk4) lost 23 vs 28 of 50.
- In our losses rivals spend 24-28% of their rounds on our half, we 12% on theirs.
- Reinforcement is even: around our victims enemy numbers rise from 1.53 to 2.62 in the last 10 rounds, around theirs ours rise from 1.32 to 2.18. Total deaths over the 50 games are equal (398 vs 404).

## Testing lessons

See `docs/WORKFLOW.md`. In short: local results do not predict the platform for fighting, items or draft. Always run the base at the same time. Never select games by past result. Judge every fix by its own target metric as well as by wins.

## Outside references

Past postmortems and rival repositories (including measured top-team policies from decoded replays) are listed in `docs/journal/references.md`.

## Gem collection vs rivals (b5 panel, ranks 72-77, decoded replays, 2026-10-24 evening)

- dr3 collected 108 gems by round 300 vs the rivals' 133; the gap opens in the first 50 rounds (9 vs 15). Before the first emblem dr3 valued gold double, so a gold cluster scored 40 against a gem cluster's 7: it opened on gold clusters (99 first hits vs 65) and elks (46 vs 24), the rivals on wolves and gem clusters.
- ge4 (gold not doubled, no mid-push bonus) collected 140 by r300 vs the rivals' 127 and 319 vs 320 by r600: collection matched. Wins stayed 23/50.
- What remains is conversion: by r600 ge4 tributed 200 vs 256. We lose 42 gems per game on death (rivals 12) and carry 77 in bags (rivals 51).
- Local `tools/local/coll_at.py` reproduces the direction (ge1/gm1 +24 collected by r300 locally, +15 on the platform).
- Whole-game gem accounting (ge9 on b5): collected 859 vs 862, but tributed 580 vs 701. In losses gems collected by r400 decide the game; the largest deficits are road_of_riches (199 vs 546), concentrated_wealth, shortcut, packs, elk_arena. On road_of_riches and shortcut the rivals take gem clusters next to our home (357 and 182 gems by r400; we 11 and 0).
- Cause on road_of_riches: those clusters lie behind a one-tile hole line. A dash crosses it (MECHANICS 4), but our route fields treated holes as walls: walk 117 to the centre vs about 20 with a dash. 30 of 40 maps have holes.
- Death hazard by situation (ge9 on b5, 250k champion-rounds, P(death within 10 rounds)): no enemy within 6: 0.004-0.005; 1 enemy: 0.046 with an ally within 6, 0.069 alone; 2: 0.079 / 0.175; 3+: 0.181 / 0.310. Per round roughly 0.0045 per enemy within 6, x1.6 when alone. Rivals by r600: 11.2 tributes of median 20 gems; we 5.1 of 33.
- Tribute trips (ge4 on b5, by r600): the rivals tribute 11 times per game with a median bag of 15, we 5.5 times with 32, but the trips are alike: last gem gain to tribute 15 vs 18 rounds, altar 8 vs 10 tiles from the last gain. With their measured loss rate (0.00045 per gem-round) the order-quantity optimum would be a larger batch, not a smaller one, so their small batches are not loss avoidance. Banking-size variants (bk4, ge6, ge7, ge8, gb1) gave no platform gain: the tribute gap (200 vs 273 by r600) is bag lost on death (42 vs 15) plus collection (319 vs 340), not batch size.
- P(death within 10 rounds) by enemies within 6 / allies within 6 / health (ge4, ge9, gc1 on b5; 370k champion-rounds): 0 enemies: 0.003-0.004 above half health, 0.015-0.017 below. 1 enemy: 0.045 / 0.033 / 0.027 for 0 / 1 / 2 allies above half, 0.228 / 0.172 / 0.117 below. 2 enemies: 0.110 / 0.051 / 0.052 above, 0.459 / 0.321 / 0.164 below. 3+: 0.208 / 0.147 / 0.103 above, 0.694 / 0.470 / 0.329 below. Hitting a camp with an enemy within 6 is not riskier than not hitting one. Deaths per game by r600 (ge4): 3.1 in champion fights (rivals 2.0), 0.5 while hitting camps with an enemy in view (0.1).

## Platform noise on a 50-game panel (b5, 8 near-identical variants of dr3, 2026-10-24)

- Per game, wins out of 8 variants: 17 games lost by all 8, 7 won by all 8, 26 swing. Treating each swing game as a coin with its observed rate gives a standard deviation of about 2.2 wins per run, so about 3 wins for the difference between two variants. Scores 17-23 of these variants (mean 20.6) are not distinguishable. A 50-game gate only detects changes of about 6+ wins.
- Per-opponent swings are large: HouseOfCoders per-game win counts across variants run 0-7 of 8, so a 4-1 one run and 1-4 the next is expected.
- Continuous gem metrics move within noise too: collected by r600 305-321, tributed 187-200, lost on death 33-42 across the same variants.
- **Platform games are deterministic (2026-10-25 17:10).** The same bot (cand1) on b56 at 16:40 (`cand1_b56`, 42 wins) and at 17:02 (`main1025d_b56`, 49 wins) differed in only 9 of 90 games, and 8 of those 9 were against HouseOfCoders, who had changed their bot in between. So a game's result is fixed by our bot, their bot, the map and the side; "noise" between runs is opponents changing bots, and between two variants it is chaos: any behaviour change, even a fuel saving that lets a guard pass on one turn, makes a game diverge, and a diverged game's result is a fresh draw. A variant therefore flips about 20-30 of 90 games (cand3 vs cand1: 29, cand1n vs cand1: 20, cand1 vs cp3: 25), and its effect is the split of those flips. Opponents still change bots between runs minutes apart: cand3's 10 up, 19 down against main1025d came mostly from HouseOfCoders (cand1n, cand1 and cand3 each won 9 of their 18 games, main1025d at 17:02 won 16); without them cand3 is 9 up, 11 down. So run main before and after the variants (identical bots give identical results), drop the opponents whose results changed between the two main runs, and judge the split of the rest.
- The 17 always-lost games are structural: 6 vs umamusume (contest, gemfight, interlock, packs, boss_battle, concentrated_wealth), 4 vs Sydney's Realist (eight, gemfight, interlock, swirl), 3 vs ha2t (road_of_riches, starvation, yellow_brick_road), 1 vs HouseOfCoders (shortcut), 3 vs :3 (elkring, expanse, fragment). Several end at 0 or under 300 gems for us: those are the real gaps, not the swing games.
- Always-lost games, causes (ge4 decoded): boss_battle vs umamusume: we carried 1072 gems and tributed none (the altar guard died unseen; ab1 fixes the belief but the race is lost by then). shortcut vs HouseOfCoders: we collected 398 to their 1161 by r1000 and never came within 10 tiles of an altar (batch never reached, no deadline trigger). contest: 0 gems for both, we die 26-40 times. eight vs Sydney's Realist: 21-28 deaths by r800-1000 vs 1-3.

## Champion fights vs rivals (ge4 on b5, decoded, 2026-10-24 22:30)

- Fight starts (first hit between two champions after 15 quiet rounds), outcome over 20 rounds within 8 tiles: when the rivals start, they lose 0.19-0.22 champions and kill 0.48-0.64 per start, whatever the local numbers. When we start, we lose 0.36-0.55 and kill 0.31-0.38, even with more champions near (0.44 lost vs 0.33 killed). Choosing fights is not the problem; fighting them is.
- By r800 the rivals land 208 hits on champions per game, we land 124, at a similar damage per hit (75 vs 86). We spend fights running: the threat rule flees from even fights (enemy power above 0.9 x ours) and an enemy already in reach follows at the same speed.
- eight vs Sydney's Realist (0 vs 1016, 21-28 deaths to 1): their 5-stack enters our half by r40 and kills our champions one by one 7-10 tiles from our spawn (r43-60: each victim had 0-2 allies within 6 against all 5), then repeats on the other flank from r150. With enemies within 3, we hit a champion in 35% of rounds and the rivals in 50%.
- fh2 (ge4 + ab1 + fh1 + fh2, kept as `bots/pool/fh2`) vs ge4 on b34, decoded (fh2 37 games, ge4 the same map/side keys): by r800 our hits on champions 125 vs 118, enemy hits on us 152 vs 184, our deaths 4.2 vs 5.5; by r1000 collected 695 vs 640, lost on death 43 vs 63, tributed 537 vs 471. Same direction as fh1 on b5. Wins stayed equal (25 vs 25), so the fight gains are real but not yet large enough to show in 50-game win counts.
- Tribute channels (fh2 on b6, per game): starts with a bag above 100 gems complete 56% of the time (rivals 81%); 240 gems per game started in such channels, 95 banked. A tribute takes bag / 10 turns standing at the altar: the_farm vs AlphaSlop, 187- and 224-gem channels (19 and 23 turns) at the mid-map altar were interrupted and 487 gems went to the enemy (0-1036). Bags up to 100 complete 93-99% for both teams.
- b6 always-lost (6 variants): 6 of 11 vs AlphaSlop (expanse, gemfight, reverse_spiral, road_of_riches, swirl, the_farm); boss_battle vs HouseOfCoders (dr3 carried 4295 gems to r1953 and tributed none: the guard monolith beside the altar had died at r1350, the other one lived, and we treat the whole group as the guard); shortcut, hooks, yellow_brick_road, road_of_riches vs The Party of Heroes.

## Where we are behind, team level (b6, decoded, 2026-10-25 02:05)

Per game, us vs rivals (same games for each variant):

| bot | collected r300 | tributed r600 | collected r1000 | tributed r1000 | lost on death r1000 | bag r1000 | deaths r1000 |
|---|---|---|---|---|---|---|---|
| dr3 (main) | 133 vs 150 | 189 vs 291 | 593 vs 723 | 406 vs 597 | 80 vs 48 | 107 vs 78 | 7.8 vs 6.1 |
| sp1 | 163 vs 138 | 237 vs 288 | 634 vs 697 | 460 vs 579 | 70 vs 39 | 104 vs 79 | 7.2 vs 7.2 |
| ef3 | 164 vs 140 | 247 vs 273 | 676 vs 728 | 479 vs 588 | 82 vs 52 | 116 vs 88 | 7.0 vs 7.2 |

- The ef3/sp1 line out-collects the rivals early and matches deaths, but still tributes about 110 fewer gems by r1000 (dr3: 191 fewer). The rest of the gap is conversion: we carry about 30 more gems at any time and lose about 30 more on death; and from r600 to r1000 we collect 17% less.
- Per champion type (sp3 on b6, rounds to 1000): our Vespers hit an enemy champion in 3.5% of alive rounds, rival Vespers 4.9%; Vendettas 2.9% vs 4.5% (31 vs 43 and 25 vs 39 hit rounds per game). A hit round does the same damage for both (attacks per round 1.2-1.3, solo damage per round 130-139). So the damage gap is the number of rounds spent hitting champions, not the quality of a hit: the rivals stay in fights longer or join more of them. Camp damage per round is equal (Vesper 29 vs 32, Vendetta 26 vs 24). (An earlier count that put the champion-hit share level at 0.09 counted self-casts as hits.)
- Items at r600 (emblems per champion): rival Vespers 3.0 Power-strength, 0.9 Bruiser, 0.8 Treasure, 0.6 Durability; ours (sp1) 1.75 Durability, 1.5 Bruiser, 1.0 Treasure, 0.3 Power. Rival Vendettas 1.8 Bruiser-strength, 0.7 Bruiser-health, 0.6 Treasure-health, 0.6 Jungle-strength, max health 2067 vs our 1728.
- Damage-heavy items alone (sp4: damage counted twice in the item formula) raised local deaths to 1182 vs 944: the rivals pair damage with more health, so they must have more gold or spend it better.
- Team wealth (gold held + item value) per game, b6: r300 rivals 1222-1303 vs us 1084-1162 (about 10% behind), r600 3093-3205 vs 2700-2921 (6-15% behind), r1000 about equal. Rival Vespers carry about 30% more item gold than ours by r600 and are their top damage dealers (6050 champion damage per game vs our 4200).
- Bug: in `pick_group` the capture rule "the claimant who gains most from the gold keeps it" compares `capture_priority(type) * 16 + slot` with a constant `mine = 16 * 16`, which no champion reaches (max 9 * 16 + 5), so it never fires; the first claimant captures. Gold passives are not used either: Vesper gains +33% of every gold gain and Marcella +2 gold per gem she tributes, so gold-rich captures belong to Vesper and gem-rich ones to Marcella. Not fixed tonight (changes every capture; no platform slot left to test it).
- boss_battle vs HouseOfCoders (sp3, b6): they killed both guard monoliths by r550-700, tributed from r611 and reached 1365 by r799; we carried 651 gems at r600 and never reached the altar, which their five held. Whoever kills the guard first owns the only altar.
- Hit rate by distance to the nearest enemy (sp3 + sp1 + ef3 on b6, rounds to 1000): Vesper with an enemy in range (3) hits a champion in 41% of rounds, rival Vespers 53% (ours step toward something in 14% of those rounds, theirs 8%: a ranged attack costs the move). Vendetta with an enemy 2-3 tiles away hits in 16% of rounds, rival Vendettas 26% (a dash closes 2 tiles). In range, melee hit rates match (Vendetta 77 vs 80%, Heart of Ruin 79 vs 81%, Marcella 81 vs 88%). These two are where the rivals' extra hit rounds come from.

## Tribute channels without game-end tributes (cp3 on b56, 70 decoded games, 2026-10-25 day)

- `decoded.py channels` used to count a tribute that ends the game as broken (the game stops before the channel ends, or the score is capped at 1000). Of our 87 channels with a bag over 100, 19 were such finishing tributes (12.5k of the gems "started" came from three boss_battle bags of 1378-3318 gems). The tool now skips them.
- Corrected, per game: bags over 100 start 1.0 times, 78% complete, 165 gems started and 118 banked (rivals 0.5, 94%, 71 and 63). Real loss to broken big channels is about 47 gems per game, not 288. Of the 15 real big failures, 13 broke while the carrier lived (a stun or an enemy lock) and 2 ended in death.
- The larger difference is frequency: the rivals start 21.3 tributes of 50 gems or less per game, we start 13.4, and their 51-100 channels complete 99% vs our 92%. In total they start 764 gems of tributes per game, we 697.
- boss_battle losses: one of our champions held 3269-3318 gems from r1472 and never banked (the only altar is guarded), so the game was lost on gems in a bag.

## Code audit with check builds (2026-10-25 day, `exp/au1`-`au12`, 80 local games each vs `pool/dr3`)

Check builds count every caught engine error by call site and, at the end of each turn, what the turn left unused (an attack with a target in reach, a ready spell with an enemy in range, a planned move not made). `tools/local/audit_errors.py` totals them. What they found in cp3, all fixed in `bf1`-`bf7` (`docs/experiments.md`, "Code audit"):

- Heart of Ruin's striking dash failed 94 times per game: `valid_tiles()` is the casting range only, not the legal landings. bf1 alone took b56 from 31 to 40 of 90 against a same-session base (with the reset and ward fixes below).
- 40 attack-reset casts per game were spent on a target the basic attack had just killed; 26 ward placements per game were refused on warded tiles.
- About 36 turns per game ended with an attack unused while an enemy champion or an awake camp stood in reach (every branch returns early).
- Help calls decoded to the wrong place on the 8 maps larger than 66 tiles; the focus byte could read as "no call".
- A turn that ran out of fuel resumed next round on its old snapshot: all "Known occupied destination" errors and stale attacks came from this.
- Most stuck walks were paths whose way forward lay inside enemy danger: champions stood still, sometimes 5 rounds next to a reward.
- Camp deaths came from walking to a capture through the reach of another group's awake elks with too little health to get out.
- The setup took 8 rounds on boss_battle: a 730-fuel design query asked twice per camp, vectors grown one element at a time (about 400 fuel per allocation) and a 430k loop of distance checks.

What is left in the au7/au8 counts, and why it stays:

- About 1,000 danger stalls per 80 games: a champion holds outside enemy reach for at most two turns, then picks another target. Deliberate.
- About 50 "Known occupied destination": a hidden unit in a bush that the engine already knew about (`vis=0` in every trace). The move then takes the next tile. (Wrong: see the au9-au11 list below.)
- Fuel: the setup still spills into round 2-3 on big maps (`cm::camp_groups()` alone costs 40k), and fights with the simulator can pass 100k on yellow_brick_road. About 0.3% of turns.
- Single digits: resets refused as "available attack" (caught, nothing spent), flee turns that stay because the only way home crosses camp reach (by design).

Second pass (`exp/au9`-`au11`, check builds of cand1 and cand3) with traces at each remaining count:

- "Known occupied destination" is not a bush unit: after our own dash or step the view changes, and units that came into view count as known. Every traced case was next to a tile just reached, on a tile out of view at the snapshot (`docs/MECHANICS.md`, blocked moves). Also, the engine's `move_towards` steps onto the goal tile itself when it is next to it, so walking at a unit or camp from the next tile always threw.
- 66 of 80 traced stuck walks to a capture stood where the target's route was unreachable: the route avoids other groups' monolith and golem reaches, and a fight or a flight had left us inside one.
- The 20k fuel floor for a local search skipped about 270 searches per 80 games, and those turns stood still; a search costs 4k at the median.
- The status line printed every 20 rounds cost 13k fuel and made 1.6% of those turns run out of fuel (0.17% of others).
- "An available attack cannot be reset" and almost every "attack unused with a target in reach" came from turns that ran out of fuel between the check and the action: the turn resumed next round with a fresh attack. Most "path found but no step" counts are such stale turns too (rounds 1-2 of big maps, and the audit build's own print rounds 500, 1000 and 1500).
- "Movement already used" (55 per 80 games): the respawn-wait loop tried all 8 neighbours after the move was spent and marked each as occupied.
- Not errors: "stuck" flee turns are champions already on their spawn (spawn distance 0).

Fuel pass (probes `exp/pf7`-`pf11`, 2026-10-25 afternoon, release builds on big_world, boss_battle, road_of_riches and yellow_brick_road, 2 games each vs `pool/dr3`):

- Per-stage fuel per turn (pf8): snapshot 27k on big_world, 19-20k boss_battle, 14-17k yellow_brick_road, 11k road_of_riches; knowledge 7-12k; pick 3-14k on average but 50-73k at most; everything else under 6k on average.
- Two lines made the snapshot cost (pf9): clearing a 10,000-entry awake flag array every turn (12.5k on big_world) and stamping the round on every visible tile (10k, about 25 fuel per tile). Reading the view as packed bits in one call and stamping only awake camps cut the snapshot to 8.5k on big_world, 9k on boss_battle and 7k on road_of_riches, with the same answer for every visible tile (pf10, 378 checks).
- With 27k gone from every turn, the fuel left at the pick stage on big_world rose from 50-70k to 70-90k. The travel-field guard (field cost + 30k) then passes, all 24 fields exist by round 250 (before: 15 of 24 still missing at round 500 for one champion), and picks cost 21-25k instead of 50-64k.
- Turns out of fuel per game (pf9 -> pf10): big_world 67 -> 16, boss_battle 20 -> 8.5, road_of_riches 13 -> 8.5. About 5 per game of the rest are each champion's opening turn (setup plus the first pick on 200k).
- Remaining per-turn costs (pf11): `update_knowledge` 4.5-9k (it checks every spawn tile of every group against the view), `build_phantoms` 3-6k (it loops over every known camp); both are exact loops that can be cut by skipping whole groups.

Third pass (`exp/au13`-`au17`, probes `pf14`-`pf18`, 2026-10-25 evening, 80 local games each vs `pool/dr3` unless noted):

- After the fuel pass 9-10 caught engine errors per 80 games were left (au13, au14). Printing each one as it happens (au14 "E" lines) gave the causes: 5 in turns that had run out of fuel and resumed on the old snapshot (two dashes onto a "Known occupied destination" in camp fights, two attack resets refused as "An available attack cannot be reset", one simulator read of a unit no longer in vision); 3 moves onto a unit that our own new ward had just revealed in a bush; 1 dash refused as "Destination is unreachable within movement range" (the landing's path crossed an enemy spawn tile, which the SDK's walk never enters).
- cand6 fixes all three kinds: `stale()` is also true under 1000 fuel, and every action that follows a search checks it right before the call; occupancy is read again after placing a ward; dash paths are closed at enemy spawn tiles. The audit builds of cand6 (au15, au16) had 0 caught engine errors and 0 bot errors in 400 games (80 + 240 quick pool + 80).
- The setup gets about 175k of the first turn's 200k. It runs into round 2 on 17 of 40 maps and into round 3 on road_of_riches, boss_battle and islands (about 310k in all): `cm::camp_groups()` 25-42k, the group loop about 2.1k per group, fields and per-spawn reads 30-60k, the strong-camp cover loop up to 86k (boss_battle: 46 strong camps x 31 groups). Before cand6 a turn that spilled went on with 53-75k and ran out again in the pick, so on 8 maps champions first acted at round 4; cand6 goes on after a spill only with 80k left.
- Camp fights started under 15k fuel ran out 28 times of 43; from 25k up, 2 of 11,600 (pf14). cand6 ends the turn instead of starting one (au16: 125 turns per 80 games, 36 of them on lost_world). Turns out of fuel in rounds 1-29, setup spills left out, fell from 126 to 45 per 80 games; later rounds 65 to 54. In the 240-game quick pool cand6 ran out of fuel on 205 of 1.31M turns after round 5 (0.85 per game).
- A turn that picks a target costs 18-50k at the median (2k without a pick); the bound pass costs about 0.5k per group, and its one field read per group is under a tenth of that (`get()` is 46 fuel, pf18). `distance_field` storage is 8x8-chunked (`docs/MECHANICS.md` section 13): a row-major direct read is wrong.
- On the platform (`tools/replay/fuel_events.py`, b56 match summaries): no `botFault` events for cand1 or cand3. `fuelExhausted` per game: cand1 (main1025d, 35 games) 20.1, of them 7.4 in rounds 1-3 and 11.3 from round 31; cand3 (25-50 games) 9.0, of them 5.1 in rounds 1-3 and 3.7 from round 31. So the snapshot fix cut later exhaustion by two thirds on real games too. cand3's setup still spilled on almost every map of 35x31 tiles or more (each champion once, into round 3 on 50x41 and 100x100); many rivals' bots spill there as well. cand6 adds cand4's opening savings (the per-tile awake array alone cost 50k of big_world's first turn).

## Deaths, fight starts and fuel in fights (decoded b56 and b3456 runs, 2026-10-25 night)

Runs: `cand1_b56` (78 decoded games), `main1025d_b56` (67), `cand3_b56` (69), `main1025e_b3456` (81 of 140; the first 81 are mostly the b34 part). Per game by round 1000 unless noted; "us" vs the rivals in the same games.

- **Same exposure, twice the deaths.** Rounds per game with 1, 2 or 3+ enemies within 6 and 0-2 allies within 6 are about equal for both sides, but our chance of dying within 10 rounds in those states is about twice the rivals' when healthy: 1 enemy and no ally 0.037 vs 0.019, 2 enemies and no ally 0.116 vs 0.048, 3 enemies and 1 ally 0.166 vs 0.058 (`cand1_b56`, health above half). Below half the gap is smaller (0.226 vs 0.137 with 1 enemy, no ally).
- **Fight starts** (first hit between a pair after 15 quiet rounds; champions of each side within 6 of the target): when we start, 2.32 of ours vs 2.43 of theirs; when they start, 2.67 of theirs vs 2.13 of ours. The same in all three runs. 32% of our starts are outnumbered (theirs 18%), 28% outnumbering (theirs 49%). Nobody converges after a start: the counts within 6 fall over the next 8 rounds on both sides.
- **Which fights kill us:** our 7.94 deaths per game (`cand1_b56`) come 4.04 from fights they started, 2.21 from fights we started, 1.42 from fights both started in the same round; their 5.99 deaths come 2.24 from fights we started and 1.92 from fights they started. In most of these fatal fights the victim's side had as many or more champions within 6 at the start.
- **Hitters at a death:** at our deaths 2.69 enemies are within 6 and 1.97 of them hit champions in the last 5 rounds; at theirs 2.27 of ours and 1.49 hitting. 32% of our deaths have 3 or more distinct champion hitters in the last 10 rounds (theirs 17-20%). Rounds in which 2 or more champions of a team hit enemy champions: us 18.6-19.3 per game, rivals 30.4-31.0. Focus quality is the same: all hitters on one target in 74% of those rounds (rivals 75-78%), the lowest-health enemy in reach chosen in 72-73% (rivals 71-72%).
- **Fuel exhaustion kills in fights.** Deaths within 5 rounds after the same champion's own `fuelExhausted` event (platform match summaries joined with decoded games): `cand1_b56` 1.12 per game, `main1025d_b56` 0.94, `main1025e_b3456` 0.84, `cand3_b56` 0.45; the rivals 0.03-0.14. That is over half of the death gap on b56 (7.94 vs 5.99). Our exhaustions after round 3 with an enemy within 6: 5.6 per game for cand1 (rivals 2.2), 3.6 for cand3. They happen in big fights (most with 3-4 or more enemies within 8) and on a few maps: yellow_brick_road 24-38 per game, swirl 28-32, lanes up to 25, boss_battle, elk_arena, gemfight, starfish. Example (`cand1_b56`, elk_arena, match 021e378b): our Vesper ran out of fuel at round 24 in a 4v5 fight, stood idle for rounds 24-26 while four enemies hit her and died; our Varg ran out at round 31 and died idle at round 33. A turn that runs out resumes next round on its old snapshot, so one exhaustion costs one or two rounds of doing nothing, at the worst moment.
- **Idle rounds near enemies.** With an enemy champion within 3, our champions took no action in 12.0% of rounds on b56 (40.6 per game; rivals 7.4%, 26.4), about 26 per game of them above 30% health and off spawn (rivals 18). Fuel exhaustion explains 3.6 per game. A local probe of fz1 (pf22, 80 games vs dr3) found 5.1% idle, 12.3 per game of them stunned and under 2 per game from any one decision path (a melee capturer with the enemy 2-3 tiles away), so the rest of the platform gap is stuns and fuel.
- **The big-hit log line was the worst single fuel cost in fights.** The "H" line printed on any hit over 25% of health cost 37.6k fuel a line (max 55.5k: iostream float formatting), about 5 times a game in fights (pf20). Removing it and the fight simulator's vector allocations (fz1) cut turns out of fuel with an enemy within 6 from 154 to 39 per 32 local games on heavy maps, and deaths from 298 to 241.

## Where cand1 (main) still lacks on b3456 (main1025g, 101 decoded games, 2026-10-25 evening)

Per game to round 1000, us vs the rivals in the same games (`decoded.py gems`, `channels`, `starts`, `fuel`, `types` on `data/fights/main1025g_b3456_b3456`). The run won 77 of 140; gems over all 140 games 103630 vs 106812.

- **Banking, not collection.** Collected 700 vs 714, tributed 511 vs 588. The difference sits in bags (128 vs 75 carried at round 1000) and lost on death (61 vs 52). Channels with bags over 100 complete 63% vs 88% (1.0 vs 0.6 starts per game, 173 vs 92 gems started); 51-100 bags 92% vs 98%. Break rate per channel turn with 1 enemy within 10 of the altar 0.0147 vs 0.0029, with 2 enemies 0.0269 vs 0.0066. The rivals channel small bags more often (9.9 vs 6.4 per game of 20 gems or less).
- **Fight choice.** They start 26.2 fights per game, we 22.9. Their starts are outnumbering in 45% and outnumbered in 23%; ours 31% and 36%. Our deaths in fights they started 3.28 per game; theirs in fights we started 2.52.
- **Fuel.** Deaths within 5 rounds after our own fuel exhaustion 0.94 vs 0.03. Exhaustions per game in rounds 1-3 6.5 vs 2.1, later with an enemy within 6 4.7 vs 1.8; most on swirl (29 per game) and yellow_brick_road (27). cand6 (opening) and fz1 (fight turns) are the fixes, both waiting for their gates.
- **Vesper is the weakest champion against her counterpart:** champion damage 4337 vs 6971, deaths 1.20 vs 0.78, hit-round share 0.036 vs 0.053, hit rate in range 0.44 vs 0.56. Vendetta 3272 vs 3492 damage, hit-round share 0.028 vs 0.035. Our Marcella (6451 vs 4560) and Heart of Ruin (3983 vs 2806) deal more damage than theirs.
- **Overall fighting is close on this panel:** by round 800 hits 129 vs 156, champion damage 12871 vs 13025, deaths 5.1 vs 4.8 (on b56, cand1 died 7.94 times per game vs 5.99).

## Why our tribute channels break, and where the unbanked gems sit (main1025g, 101 decoded games, 2026-10-25 night)

Scratch analyses on `data/fights/main1025g_b3456_b3456` (by round 1000 unless noted; "us" vs the rivals in the same games).

- **The unbanked-gem gap is boss_battle.** Bags at round 1000 on boss_battle (5 games): 1429 vs 488, tributed 22 vs 283. Without boss_battle the bags are equal (60 vs 53 per game) and the tribute gap (536 vs 604) is spread over maps we lose (concentrated_wealth, gemfight, eight, swirl, interlock, road_of_riches, shortcut). Rounds with a bag over 100 standing still off spawn: 38.6 per game for us, 9.3 for the rivals, and 3222 of those rounds in all were on boss_battle.
- **boss_battle guard timing:** the rivals damage the two guard monoliths from r490-720 and kill them by r536-1531; in the two games we lost, the rivals killed them at r536-681 and won (620 and 797 tributed). We hit them 0-45 times per game (rivals 13-197). Whoever kills the guard first owns the only altar (earlier finding, b6).
- **Broken channels over 50 gems:** 0.64 per game for us (86 gems started), 0.12 for the rivals (13). 28 of our 65 were on starfish, 12 on gold_rush. Pattern on starfish (match 04110ba3, r1170-1190): our 134-gem carrier channels for 14 turns; one enemy at 4-5 tiles (727 health against our 2661) casts a damaging stun every 8 rounds, which cancels the channel; we restart it at once and never fight back, because the prey search reaches only max(range, 4). After the break the carrier died within 15 rounds in 0.14 per game (18 gems per game to the killer; rivals 0.06, 5).
- Damage does not cancel a channel and our bot never cancels one, so "left the altar" after a break means a stun (or death) first; we then flee or walk on.

## cand6 against main on the same b3456 games (cand6_b3456 vs main1025g, 2026-10-25 night)

- Wins 70 vs 77 of 140 (22 L->W, 29 W->L). Platform fuel (`tools/replay/fuel_events.py`): our `fuelExhausted` 5.1 per game vs 15.2 (after round 30: 1.6 vs 8.2); deaths within 5 rounds after our own exhaustion 0.26 vs 0.94 per game (`decoded.py fuel`), the rivals 0.03-0.08; our exhaustions with an enemy within 6 1.3 per game, the rivals' 2.2.
- Paired on the 86 games decoded in both runs (`tools/replay/paired.py`, same opponent and map; per game to r1000, cand6 minus main): collected +63.7 +- 25.2, tributed +34.5 +- 22.3, their tributed -28.7 +- 23.0, tribute margin +63 +- 41, our deaths -0.5 +- 0.6, their deaths +0.3 +- 0.5. On those 86 games the wins moved -3 (12 L->W, 15 W->L). The flips are large in both directions (L->W games: our deaths 12.6 -> 3.8; W->L games: 2.7 -> 6.1), the signature of chaos rather than of a weaker bot.
- Local fuel probes on 32 heavy-map games (`docs/experiments.md`, pf23-pf25): contact turns out of fuel per 1000 are 8.07 for main + fz1's fixes, 1.32 for cand7 (cand6 without cand3's movement changes, + fz1) and 1.14 for fz1. The fuel gain comes from cand4's exact speed-ups and cand6's fixes, not from the movement changes.
- **Where they catch us** (main1025g + cand6, 218 decoded games, deaths to r1000 in fights the killer side started, victim state at the first hit of that fight): ours 3.52 per game, theirs 2.28. 52% of ours start on our own half (spawn distance more than 4 shorter than to theirs), 36% in the middle, 11% on their half; theirs 39% / 43% / 18%. So per game 1.84 of our deaths come from fights they start on our half, against 0.88 of theirs on their half. At the start the victim is healthy (90%+ health in 65% vs 67%) and carries little (20 gems or less in 83% vs 86%); allies within 6: none 40% vs 36%, two or more 28% vs 37%. Our victims by type: Heart of Ruin 30%, Vendetta 25%, Varg 23%, Vesper 15%, Marcella 7%.

## When a teammate is hit (main1025g + main1025e, 182 decoded games, 2026-10-25 night)

- `decoded.py assist`: a champion at 60%+ health whose teammate within 6 takes a hit from an enemy champion. With the nearest enemy 1-2 tiles away we hit a champion in 60% of those rounds and stand still in 21%; the rivals 67% and 13%. At 3-4 tiles we hit in 16% and stand still in 26%; the rivals 28% and 16%. Our code explains the holds: without `winning`, `finisher` or `rich`, a champion that is not `losing` attacks only what is already in reach and then moves with `avoid_danger`, outside every enemy's reach, so a melee champion never closes in.
- Outcome over the next 10 rounds with an enemy within 4 (once per champion and teammate per 15 rounds), by numbers within 6. Even numbers: when we joined (hit or stepped closer), the teammate died in 19% and enemies near it died 0.48 per event; when we held, 29% and 0.26. We died ourselves in 10% vs 8%. Ahead: join 16% / 0.43, hold 19% / 0.29. The rivals join more often when ahead (11.0 joins and 4.3 holds per game; ours 7.7 and 5.1). Joining is confounded with the simulation saying we win, so this ranks the idea, it does not measure it. Variant `as1` (`docs/experiments.md`).
- Ranked games 10-25 by side (57 with summaries): side a 14 of 25, side b 20 of 32. Every unranked panel until `b7` had us on side a only.

## Channels with an enemy close (main1025g + main1025e, 182 decoded games, 2026-10-25 night)

- `decoded.py channels`, bags over 30, an enemy champion within 4 of the channeler on any channel turn: ours 1.64 per game, 64% completed, an enemy cast on our channeler in 23%; theirs 0.85 per game, 84% completed, we cast on theirs in 10%. Without an enemy within 4 both sides complete 100%. So the larger part is defence: rivals reach our channels twice as often as we reach theirs (our altar trips run into them, `bank_gems` starts a channel whatever stands near), and they use stuns on them twice as often. Matching their offense would break about 0.15 more of their channels per game (about 12 gems delayed); our own breaks cost about 0.6 channels per game (bag 83).

## The banking gap is mostly boss_battle (main1025g + main1025e, 182 decoded games, 2026-10-25 night)

- Carried bag at r1000: 104 vs 66 per game over all games, 58 vs 52 without boss_battle; on boss_battle 1461 vs 500 (6 games). Tributed without boss_battle: r600 282 vs 290, r1000 558 vs 575 (176 games, we won 101); on boss_battle 18 vs 236 by r1000, yet we won 4 of 6 late. cand6 without boss_battle: 548 vs 597 by r1000.
- Without boss_battle the channels bank about as much as the rivals' (sum over bag sizes of gems banked per game 729 vs 734); ours come in fewer, larger channels that break more often: bags 51-100 complete 92% vs 98%, over 100 75% vs 89%.
- So the handoff gap "bag 128 vs 75 at r1000, bags over 100 complete 63% vs 88%" is mainly boss_battle (variant `gk1`). Outside it the tribute deficit by r1000 is about 3%; the next gaps should be measured again on `b7`, whose teams rank above us.

## Losses are decided by early fights (main1025g + main1025e + cand6 on b3456, 289 non-boss decoded games, 2026-10-25 night)

- Per game, losses (134) vs wins (155), us-them: deaths by r150 1.4-0.8 vs 0.6-0.9, by r350 3.1-1.9 vs 1.4-2.3, by r1000 10.4-4.8 vs 3.4-7.9; collected by r150 55-61 vs 79-56, by r1000 521-843 vs 808-533. The side that loses the first fights farms less and loses the rest.
- Deaths to r200 in losses: ours 1.82 per game (champion kills 1.65, camps 0.17), theirs 1.07 (0.70, 0.36). Of our champion-kill deaths, 48% are on our own half, 66% with 3 or more enemies within 6 at the death, 26% while we had hit camps in the 10 rounds before. Same picture as the 10-23 finding (enemy 3-stacks on our half), smaller.
- Idle next to enemies (healthy, an enemy champion within 2, no action and no move in the round; 299 games to r1000): ours 12.9 per game, theirs 8.0. The difference: stunned by an enemy stun cast that or the previous round 2.39 vs 0.00, at our own spawn 1.44 vs 0.19, out of fuel 0.72 vs 0.21; the remaining idle rounds are about equal (8.3 vs 7.5).
- Deaths from the last 90%+ health point within 3 rounds (bursts): 12% of ours in losses (1.2 per game), 2% of theirs; in wins 1% of ours, 7% of theirs.

## Outnumbered and out of reach (main1025g + main1025e + cand6 on b3456, 299 decoded games to r1000, 2026-10-25 night)

- Healthy (50%+), 2+ enemy champions and at most 1 ally within 6: 147 rounds per game for us, 130 for the rivals; P(death within 10 rounds) 0.065 vs 0.050 with 2 enemies, 0.149 vs 0.095 with 3+. With 3+ enemies we are caught at 1-2 tiles 22.5 rounds per game, they 13.8.
- What each side does there, by distance to the nearest enemy (share of rounds stepping toward its own spawn): 2 enemies at 3-4 tiles, rivals 30%, us 23%; at 5-6 tiles 30% vs 17%; 3+ enemies at 3-4 tiles 34% vs 22%, at 5-6 tiles 36% vs 18%. With no enemy within 6 (healthy, off spawn) the shares are 15% vs 11%, so the rivals' retreat is a response to the numbers. Their P(death) after those home steps is 0.006-0.053, ours 0.039-0.133.
- In our code this state goes to the losing branch's first case ("already out of reach: keep working"), which keeps farming with `avoid_danger` until an enemy comes into reach. Variant `ro1` (`docs/experiments.md`).
- Not a gap: hitting camps under 30% health with an enemy champion within 5 is 1.0 round per game for us (2.0% of 50.6 such rounds), 0.2 for the rivals. Under 30% with an enemy within 5 our P(death within 10 rounds) is 0.346 vs 0.286 (the escape gap above); without an enemy near we finish camps at low health more often (11.9% vs 6.9% of rounds) and die less (0.014 vs 0.038).
- umamusume (rank 40 on 10-25 22:05) beat main1025g and cand6 in all 20 b3456 games. They draft nearly our team (Vesper, Marcella, Heart of Ruin, Vendetta, plus Ryth on 5-champion maps) and win the first fights: gemfight r200 deaths 5-1 and 4-2, swirl 3-0, interlock 3-1; on broken_curve we led 515-408 in tributes at r700 and still lost.

## Vesper: shots, items and fleeing after a hit (cand6 + fd2 + rt1 on b3456, 420 decoded games, 2026-10-26 night)

- Champion damage per game by r1000: our Vesper 5290 (rt1), the rivals' Vesper 6604 (main1025g/e games); our other champions are level with theirs or ahead (Heart of Ruin 4363 vs 2929, Marcella 7166 vs 4868, Vendetta 3865 vs 3709 on kd1). Vesper deaths: cand6 0.97, fd2 0.83, rt1 1.01, kd1 0.86, main1025g 1.21; the rivals' 0.78.
- Shots are not the gap. With an enemy champion within 3 (off its spawn) at round start, our Vesper shoots 35.4 times per game, theirs 32.2: we spend more rounds in range (71 vs 60 per game) and shoot in a smaller share of them (healthy: 0.51-0.56 vs 0.60-0.61; `decoded.py shots` splits this by health and by a hit the round before, for every champion type).
- Items are. At r600 our Vesper has about 150 strength and 2323 health, theirs 188 and 2135. Their build (emblems per Vesper at r600): Bruiser strength 2.20, Power strength 1.28, Bruiser health 0.86, Treasure strength 0.61, Durability health 0.60, Jungle *strength* 0.42; ours Durability health 1.51, Power strength 1.31, Bruiser strength 1.03, Treasure strength 0.96, Jungle health 0.91 (`decoded.py items --round 150/300/450/600`). Strength 188/150 = 1.25 matches the damage ratio 6604/5290. Variant `vi1`.
- After a hit at 50-80% health (an enemy champion hit her the round before, an enemy within 3) she shoots in 49% of rounds, theirs in 62%, and both die within 10 rounds in 10-11% of them. The cause, from a local log build (`vl1l`, 320 games): `healthy` in the losing branch requires "not hit this round", so one hit sends a losing Vesper into `flee` (walk home, no shot); at 50%+ health such turns are 3.05 per game, and all other no-shot turns next to an enemy are stuns (2.73). Also we are hit more often: 13.9 rounds per game at 50%+ health right after a hit, the rivals 8.0.
