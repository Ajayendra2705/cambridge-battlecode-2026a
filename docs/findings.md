# Findings

Measured facts that shaped the bot, and what we know about stronger teams. Exact engine numbers live in `docs/MECHANICS.md`. The raw dated logs these come from are in `docs/journal/`.

## Engine and fuel

- The engine is deterministic: the same bots on the same map give the same result, locally and on the platform.
- Every SDK accessor is a host call (about 40 fuel). Read raw structs (`cambc::detail::sdk_champion`, `sdk_camp`) once per unit per turn. Printing is expensive too: heavy per-turn logging cost a bot 18k gem margin locally.
- Always test with `--release`, because the platform runs release builds.
- Our champions hit fuel exhaustion about 10 times per game, against about 4 for rivals, mostly on big maps. `pick_group`'s BFS costs about 45k fuel.
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
- The 17 always-lost games are structural: 6 vs umamusume (contest, gemfight, interlock, packs, boss_battle, concentrated_wealth), 4 vs Sydney's Realist (eight, gemfight, interlock, swirl), 3 vs ha2t (road_of_riches, starvation, yellow_brick_road), 1 vs HouseOfCoders (shortcut), 3 vs :3 (elkring, expanse, fragment). Several end at 0 or under 300 gems for us: those are the real gaps, not the swing games.
- Always-lost games, causes (ge4 decoded): boss_battle vs umamusume: we carried 1072 gems and tributed none (the altar guard died unseen; ab1 fixes the belief but the race is lost by then). shortcut vs HouseOfCoders: we collected 398 to their 1161 by r1000 and never came within 10 tiles of an altar (batch never reached, no deadline trigger). contest: 0 gems for both, we die 26-40 times. eight vs Sydney's Realist: 21-28 deaths by r800-1000 vs 1-3.
