# Findings

Measured facts that shaped the bot, and what we know about stronger teams. Exact engine numbers live in `docs/MECHANICS.md`. The raw dated logs these come from are in `docs/journal/`.

## Engine and fuel

- The engine is deterministic: the same bots on the same map give the same result, locally and on the platform.
- Every SDK accessor is a host call (about 40 fuel). Read raw structs (`cambc::detail::sdk_champion`, `sdk_camp`) once per unit per turn. Printing is expensive too: heavy per-turn logging cost a bot 18k gem margin locally.
- Always test with `--release`, because the platform runs release builds.
- Our champions hit fuel exhaustion about 10 times per game, against about 4 for rivals, mostly on big maps. `pick_group`'s BFS costs about 45k fuel. (Since the fuel passes of 10-25, cand6: 0.85 per game after round 5 in the local quick pool; see "Code audit" below.)
- `init_world` spreads over the first rounds.
- Fight-turn fuel (probe `exp/fuelm`, hb4 code, 32 local games vs hb4/tf3 on 8 maps, 2026-10-24): turns with a prey use 41.7k on average (p50 41k, p90 56k, p99 70k, max 88k). Building the sim inputs costs 10k (max 44k) and `simulate_fight` 4.5k (max 11k), with 3.7 units on average. `fuel_remaining()` costs 6 fuel.
- Small dense nets cost about 7 fuel per multiply-add as written (scalar loops, no vectorisation): a set encoder with phi 6->16 and head 32->16->1 cost 6.8k on average (max 9.3k), and a 2-layer phi 6->16->16 cost 13.9k (max 47k incl. first-call weight init). Clang `-O3 -msimd128` only half-vectorises dot-product loops (`a += W[j][k] * x[k]`), because it may not reorder float adds. Transposed weights with explicit `wasm_simd128.h` axpy loops (`acc[j] += W[k][j] * x[k]`) cut this to 2.9k (max 3.7k) and 7.0k (max 16k), with outputs equal to the scalar nets within 6e-8.

- Learned fight model (`ml/`, 2026-10-26): one FightQ forward pass (12 units, 2.3k params, SIMD) is affordable, but a 5-model ensemble plus the existing `simulate_fight` exhausted fuel on 301 turns in one local game (main: 13).

## Camps and economy

- Camps never regenerate or chase. A whole group wakes when one member is hit. A woken camp hits the nearest champion, not the one that woke it. Sleeping camps never attack, even adjacent. Camps fall asleep 2 rounds after no champion is in range.
- Spells reach 4. Camps reach 3, except elks 4, golems 4 and monoliths 5. Casters standing at 4 from range-3 camps take no damage ("standoff").
- Standing on a group's spawn tile blocks its respawn indefinitely.
- Gold gap against the top 10: 79% comes from captures (68 vs 40 clears per game, same ~118 gold per clear) and 21% from kills (kill = 100 gold, assist = 0).
- Opponents capture many small groups and gold clusters near their spawn every 80-110 rounds. Top teams tribute about every 32 gems; our order-quantity batch gives 60-100.
- Items: health emblems matter (all-Power builds lost on the platform). Top teams build Bruiser everywhere, HoR on focus, Marcella on focus (15 focus per shard, spell 2x focus). They buy Monster shards 7-14 per game and altar locks about 4-6 per game. We buy none of either.

## PvP

- Ranked-replay diagnosis (`ml/death_trace.py`, `ml/death_analysis.py`, 2026-10-27; ours = 50 Velvet Tributers games, others = 1,290 games grouped by ladder rating vs ours). Per side-game: we die less (6.9 vs 9.1-9.7 for higher and similar teams) and lose fewer gems dying (83 vs 101-105), but kill far less (5.0 vs 8.2-8.3), and our opponents tribute 70-80 more gems than opponents of similar teams. Death anatomy is the same for every group (hp bleeds over ~13-16 rounds, the turn away comes at ~0.3 hp, killers were almost always seen earlier), and flee survival by hp is the same, so fleeing deaths are a property of the game, not our gap. We spend less time with an enemy in reach (443 vs 505-554 rounds per side-game) and engage less when the simulator says even or losing (42% / 23% vs 49% / 40%), slightly more when it says winning. Low-hp enemies near us: 9.4 chances per game vs 11.9-13.7, converted 45% vs 48%.
- Most of our deaths happen while fleeing (51-80% depending on the bot). The typical fatal engagement starts near full hp while walking to a capture, with about 2 allies and 0.8 enemies within 5. It ends 14 rounds later with 0.7-1.8 allies against 2.1-2.5 enemies: their teammates join and ours do not.
- Per-turn 1v1 damage is equal to rivals. Total champion damage is lower only because we die and flee more.
- Ryth and Marcella were starved of gold by slot-order capture sharing. `gb2` fixed it by sharing by fewest owned shards. Overfeeding one champion (gb3) was wasted.
- Platform opponents punish aggression that local bots reward. Blind no-flee play (nf2, ag*) and looser fight entry (pa1, lf1) lost on the platform. Current fight thresholds look like a local optimum both ways (tighter bpt1/bpt2 is also worse).
- A learned engage model (FightQ v1: supervised Q(s,a) on 1.4M platform decisions, val MSE 0.73 vs 0.94 baseline) plays far worse than `simulate_fight` + hand rules (local, 10x fuel: 19/60 vs 43/60). Its engage-vs-stay gap is about the size of its seed-to-seed noise; the more decisions it controls, the worse the bot (fq1-fq4 in `docs/experiments.md`).
- A learned reinforcement predictor (`ml/reinforce_*`: enemies/allies arriving within 7 rounds, death AUC 0.707 -> 0.734) wired into the flee rule or simulate_fight (rf3-rf7) is neutral to slightly negative over 560 local games (374-380 vs main 384), although 60-game samples looked positive. Picking the best of several 60-game runs is selection bias; confirm on 560. The predictor is just as accurate against our local pool bots (enemy AUC 0.785 vs 0.787 on platform games, calibrated per bin), so the neutral local result is not a distribution-shift artefact: knowing reinforcements are coming does not improve these flee/sim decisions.
- Farm prediction model (fpr) in target choice (`ml/fpr_*`, `ml/bot/fpr.h`, fpr5): pick_group's top 8 live-camp groups are rescored as formula score x P(our team captures the group), P from a small MLP on group, champion and units-near-group features trained on 261k platform capture attempts. Local: style bench 94/140 vs main 76; 560: 391 vs 384 with deaths -24%, captures +13%, margin +21%. Replacing the formula's time estimate with the model (fpr2) lost: the formula's team-size and claim logic matter; the model works as a correction, not a replacement. The bot's own clear-time estimate is nearly uncorrelated with real capture times (fitted slope 0.14).
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

## Where we lose to ranks 18-40 (b8, main1026a, 120 decoded games, 2026-10-26 night)

Panel b8 (12 teams, ranks 18-40, ratings 1958-2101): 29 wins of 120, our score 575 per game against 940. Per game to round 1000, us vs them (`decoded.py gems|captures|defend|items|risk|starts`):

- **Economy is the gap.** Collected 626 vs 843, tributed 460 vs 704, lost on death 61 vs 47, deaths 6.0 vs 4.7. At r300 collection is still close (151 vs 165); the gap opens from r300 to r1000. On b3456 (rivals at our level) collection was equal (696 vs 689).
- **Captures** (a capture is a gem or gold gain without a kill on a tile of a group whose camps all died; an earlier count from gem gains alone missed gold-only cluster groups): 42.5 groups per game vs 45.8. By region (closer to own start, middle, closer to the enemy start): own half 31.4 (373 gems) vs 29.7 (373), middle 8.6 (162 gems) vs 11.7 (277), enemy half 2.5 (28) vs 4.4 (55). The whole capture gap is in the contested middle and enemy half; on our own half we take more groups (more gold clusters) for the same gems. They lead in the first 250 rounds already (10.3 vs 11.9). Of the camp hit-rounds that end without our own capture (99 per game vs their 66), 53 per game end with the group taken by them (theirs by us: 18), mostly with an enemy within 6 at our last hit (40 vs 18), on elk groups (51 vs 34). Shared captures: 2% of ours, 8% of theirs.
- **The rest of the collection gap is bags from kills:** about 72 gems per game more for them.
- **Capture cycle** (one capturing champion, between its captures, to r1000): 83 rounds vs 74 (moves 49 vs 42). Clearing (first hit to last camp dead) 21.5 vs 23.2, claiming (dead to captured) 12.1 vs 10.8. The straight distance between consecutive captures is the same (12.3 vs 12.4 tiles). Back-and-forth steps are not the cause (2.0% vs 1.7% of quiet moves). Camp-hitting effort is the same (0.98 vs 0.96 of our champions hit a camp in an average round to r250).
- **Items:** by r600 their champions earned about 30% more gold (Vesper 1207 vs 912, Vendetta 785 vs 577, Heart of Ruin 667 vs 565, Marcella 944 vs 804) and have more health: max health at r600 Heart of Ruin 1936 vs 1521, Vendetta 2145 vs 1669, Marcella 2217 vs 1914, Vesper 2563 vs 2232. They build Bruiser of the main stat and Bruiser health (Vesper: Bruiser strength 2.72, Bruiser health 1.57 emblems at r600), Jungle of the main stat (not health), Treasure, and one Durability health.
- **Fights:** they start 26.8 fights per game, we 19.9; our deaths in fights they started 3.25 per game, theirs in fights we started 1.68. P(death within 10 rounds) is higher for us in every local situation (enemies and allies within 6, health half) while the time spent in each situation is about the same. As defenders at half health or more our champions hit back in fewer rounds (Heart of Ruin 0.42 vs 0.50, Varg 0.36 vs 0.45, Vesper 0.26 vs 0.36) and die more often (Heart of Ruin 0.23 vs 0.13 per fight started on it, Marcella 0.23 vs 0.15, Vendetta 0.20 vs 0.12). Our Vendetta and Vesper are attacked about twice as often (6.1 and 4.9 fights per game vs 2.9 and 2.6). Positions are not the difference: time by region and the share alone, near enemies or outnumbered are about equal. Per type the same holds (main1026a + vi1 + bh1, 360 games to r1000): the distance to the nearest enemy over rounds with one within 6 is distributed alike (Vesper inside an enemy's basic reach 0.13 of those rounds for both sides, Vendetta 0.18 for both), and so is what the champion did in the 3 rounds before a fight started on it. Yet fights start on our champions more often per such round: Vesper 4.2 vs 3.0 per 100, Marcella 4.8 vs 3.8, Vendetta 5.7 vs 4.9, Heart of Ruin 5.4 for both. The rivals choose to engage us more, which fits their fight checks rating our weaker champions (less health and fewer items) as beatable. Deaths to enemy champions (5.3 per game for us, 3.8 for them) go faster for us: 5 rounds before the death our victims still had 53% of their health, theirs 46%, with the same numbers around (enemies within 6: 2.3 vs 2.4, allies 1.05 vs 1.07). In those 5 rounds our victims hit a champion in 36% of rounds, theirs in 46%, and moved without moving away from the nearest enemy in 30% vs 19%.

## The Sprint 3 items against our b8 economy (main1026a, 120 decoded games to r1000, before the patch, 2026-10-26 night)

The patch notes leave one question open: whether Prospector's "cluster rewards" means every camp group's reward or only the gem and gold cluster camps in it. Both readings are estimated below as upper bounds (the item held by every capturing champion from round 1, before rounding effects on split rewards). **Measured since (probe pp0, engine 2.0.0, 13 local games): only the cluster camps.** The emblem adds 25% of the holder's share of the group's gem-cluster gems and gold-cluster gold, rounded down on the total (`docs/MECHANICS.md` sections 10 and 11), so the "cluster camps only" line below is the one that applies.

- **Captures are taken alone:** 99% of our group captures and 93% of the rivals' have one capturing champion, so "your share" is nearly always the whole reward.
- **Where our gems come from:** 597 captured gems per game (rivals 788). Mixed groups bring most of them: elk + gem (+ gold) groups 249 per game (rivals 323), gem + wolf groups 46 (70), single gem groups 37 (70). Gold-only groups are 15 captures per game for 856 gold.
- **Prospector, all groups:** +138 gems and +1193 gold per game for us (rivals +183 and +1370), about +23% gems.
- **Prospector, cluster camps only** (7 gems per gem cluster and 20 gold per gold cluster in the group): +40 gems and +328 gold per game (rivals +63 and +379), about +7% gems.
- **Treasure at 10%:** about +540 gold per game if every champion held it from round 1 (captures 4788 gold, kills about 630), and no gems. Prospector beats it on either reading, because it also adds gems, and gems decide the game.
- **Hunter:** about 6.3 kills per game for us, so +315 gold per game spread over the killers at the engine's 50 per kill (the value the organisers confirmed on Discord, 10-26 04:07 IST; +630 at the notes' first 100). That is less than Prospector, and the gold goes to champions who already earn it.
- **Capture** (3 turns instead of 5): the median claim (last camp dead to capture) is 6 rounds for both sides, so the item saves about 2 of them on each of 42 captures per game. That is about 2% more capture time per champion, plus a shorter window for steals.
- **Patch-day order (written before the measurement):** first Prospector instead of Treasure as the first emblem (on either reading). Then Capture or Tribute as a second passive. Then Greed against Power for champions with 750 gold to spend: 35 against 30 stat shards, with nothing extra until the 25th shard.
- **After the measurement:** Prospector against Treasure is about +40 gems and -212 gold per game for us, a small and uncertain trade (the local quick pool of `exp/pr1` gave 356 of 420 against main's 359, which does not judge items). The top 12 teams do not buy any of the new items: in 66 of their ranked games on engine 2.0.0 (05:00-07:30 IST on 10-26, both sides decoded), no champion holds a Tribute, Capture, Prospector, Hunter, Skirmish, Greed or Collectors item at the end, and they still open with Treasure and then build Bruiser.

## The 30 maps we never tested (main vs pool b_log, pd1, tf3, 180 local games, 2026-10-26 night)

The platform pool has 70 maps since 10-26 (`docs/MECHANICS.md` section 15); our gates and quick pools used only the first 40, and ranked games already include the others (02gift_wrapping seen at 10-26 04:00). On the 30 newer maps main won 148 of 180 against the pool (206 of 240 on the first 40), but carried and lost far more:

- **Gems lost per game 98, against 36 on the first 40 maps; deaths 4.2 against 3.4.** The worst maps: 02guardians 578 lost per game (13.3 deaths), adgato-gemcombat5 398 (7.2), 02the-pack 377 (2.0 deaths, so about 190 gems per death), 02stalactites 184, 02treasure-box 177, adgato-gemcombat1 160, 00the-line 146, 00anvil 134, 00crater 125 (11.2 deaths). 00ribs has 13.5 deaths per game.
- **02guardians:** its one altar (20,20) has only two standable tiles in tribute range, each holding a monolith of its own group (probe mp1). Nobody can bank until one of them dies. Our altar-guard rule only recognises a single guard group (boss_battle), so it does not apply here. In a local game against tf3 the monoliths died at r1408 and r1473, nobody tributed before that, and our Vesper carried 388 gems by r1000. Of all 70 maps only 01boss-battle and 02guardians have every altar tile held by camps; 02treasure-box has 4 camp tiles and 4 free tiles beside its altar.
- **Fuel:** turns that ran out after round 3 were 1.5 per game on the new maps (0.5 on the first 40), led by 00vault (23 per game) and 02tangle (10). The probe (pf30, 36 games on six of these maps) puts 226 of 326 run-outs in the camp fight (`cf choose` 146, `camp fight` 114, `cf hit` 19), whose path searches flood large walled areas. On the platform our run-outs are still far fewer than the rivals' (b8: 3.7 against 10.6 per game).
- **Ranked, last 100 games (mixed test bots):** first 40 maps 31 of 62 won; 00 extras 6 of 8; adgato 2 of 4; 02gift_wrapping 0 of 1. Two blowouts were on extras: 00oasis 92-1006 (30 deaths) and 00dunes 60-1010 (37 deaths).

## Engine 2.0.0: main (m4) against the b9 teams (main1026f, 115 decoded games to r1000, 2026-10-26 morning)

The b9 teams are the 12 b8 teams, now ranks 17-57 (we are 81). main1026f won 40 of 120; our deaths 897 against 615.

- **Economy:** even at r300 (collected 180 vs 173, tributed 117 vs 117), behind from there: r600 397 vs 420 collected, 308 vs 341 tributed; r1000 626 vs 719 collected, 496 vs 604 tributed, lost on death 50 vs 43, deaths 5.5 vs 4.0 per game (`decoded.py gems`).
- **Every type dies more** (deaths per game to r1000, us vs them): Heart of Ruin 1.51 vs 1.05, Varg 1.43 vs 0.91, Vendetta 1.35 vs 0.88, Marcella 1.04 vs 0.84, Vesper 0.83 vs 0.52. Gems per game: Vesper 141 vs 212, Heart 116 vs 155, Vendetta 142 vs 175 (`decoded.py types`).
- **Health at r600:** Heart of Ruin 1408 vs 1737, Vesper 1742 vs 2001, Marcella 1913 vs 2065, Vendetta 1590 vs 1706 (Varg 1345 vs 1259). They build Bruiser of the main stat and of health; we build Power, Treasure, Jungle health and Durability (`decoded.py items`). bz1m's premise holds on 2.0.0.
- **Vesper with an enemy in basic reach** (`decoded.py shots`): at 80%+ health and not hit the round before (30 rounds per game for both sides) ours hits a champion in 49% of rounds and moves in 41%, theirs 62% and 29%; P(death within 10 rounds) 0.021 vs 0.007. After a hit at 50-80%: 49% vs 60% (vh1m's premise holds).
- **Heart of Ruin in the same spots dies faster:** after a hit at 80%+ health P(death within 10) 0.075 vs 0.027, at 50-80% 0.181 vs 0.100, with about the same hit share (0.81 vs 0.88).
- **Fights:** they start 28.0 fights per game, we 19.1; our deaths in fights they started 2.96 per game, theirs in fights we started 1.36 (`decoded.py starts`).
- **Banking:** bags over 100 complete 64% vs 85% (we start 1.0 such channels per game, they 0.8); bags over 30 with an enemy within 4 complete 52% vs 80%, and an enemy casts on our channeler in 22% of them (theirs 6%) (`decoded.py channels`).
- **Draft:** we field Varg on 4- and 5-pick maps; our 4-pick games went 6 of 25 (3-pick 11 of 20, 5-pick 19 of 63). The top 12 teams field Vesper 94%, Marcella 86%, Heart 85%, Vendetta 73%, Ryth 38% and Varg 6% of their games (66 games on 2.0.0).
- **Blowouts:** 01hooks 0-1012 (41 deaths against 2) and 00swirl 45-1012 (53 against 1): a four-champion group holds the centre (01hooks: one altar in the middle, gem clusters on the centre line) or stands 4-6 tiles outside our spawn (00swirl); our champions walk out one or two at a time and die, or step out, take a hit and dash back to heal. Near our own spawn with 2+ enemies within 6 we spend 21 rounds per game (them 15) and hit a champion in 9% of them (them 21%). 00vault 4-1077 in 489 rounds came with 34 of our turns out of fuel.
- **Dashes into enemies are not the problem:** dashes that land within 2 of an enemy champion (7.4 per game for us, 7.6 for them) end in the caster's death within 6 rounds 4% of the time for us and 3% for them, and in an enemy death 22% vs 10% (first 26 games).
- **Fuel on the platform:** 0 bot faults; 3.5 turns out of fuel per game (2.4 of them in rounds 1-3, the setup spill), the rivals 8.1 (`fuel_events.py`).

## Item gold decides the fights (main1026f on b9 and the top 12 teams, decoded, 2026-10-26 morning)

Same 115 games as the section above, compared with `data/fights/top12_20` (66 ranked games between top-12 teams on engine 2.0.0). The scripts were one-off reads of the decoded rows; the numbers are per game to r1000 unless stated.

- **How we die.** Deaths after an enemy champion hit: 5.13 vs 3.50. By what the victim did in the 3 rounds before the fatal fight started (first hit after 8 quiet rounds): walking 2.66 vs 1.75, hitting camps 0.82 vs 0.26, hitting champions 1.29 vs 1.23, tribute 0.10 vs 0.04. With no teammate within 6 at that moment: 2.07 vs 1.07; with two or more teammates within 6 about equal. The walking deaths are spread over both halves, all distances from spawn, both directions and all round bands: no single place or move explains them.
- **Same situations, worse outcomes.** An enemy champion arrives (within 6, none in the 5 rounds before) next to a champion that is hitting camps 7.4 times per game for us and 7.7 for them. Both sides then keep hitting camps in about half of the next 5 rounds (53% vs 50%) and hit a champion in 7-8%. Our farmer dies within 15 rounds in 6% of these arrivals, theirs in 3%; alone against one arrival 7% vs 1%. Lone 1v1s at half health or more (both sides, no other champion within 6) happen 10 times per game; exposure in the risk table is equal (109 vs 110 rounds per game with one enemy and no ally at high health), but P(death within 10 rounds) is 0.031 vs 0.010.
- **What decides a 1v1 is item gold.** Lone 1v1 episodes (1171, outcome within 15 rounds) by the difference in gold held as items (30 per shard): when we are poorer by 300 or more (28% of episodes) we die in 11% and they in 0%; richer by 300 or more (15%): we 0%, they 8%; within 100 (32%): we 4%, they 2%. By max health the same split: under 85% of theirs (46% of episodes) we die 8% and they 0%; above 115% we 2% and they 8%.
- **Gold.** Team gold (unspent plus 30 per shard) us / them at r300, r600, r1000: 961 / 1086, 2418 / 2726, 4428 / 5139 (ratio 0.89, 0.89, 0.86). On 3-champion maps we are ahead (1.08-1.12), on 4 and 5 behind (0.83-0.88). Kill gold explains about a third of the gap (they kill us more: 100 gold a kill), camp gold the rest. Per type at r600, gold held as items: Heart of Ruin 370 vs 524, Vesper 705 vs 838, Vendetta 441 vs 513; Marcella and Varg equal. bz1m (Bruiser health in the formula) changed the split between stats, not the amount: its Heart still had 362.
- **The top 12 earn much more gold at the same gems.** On 5-champion maps by r300: camp gold 1377-1440 per team (b9 rivals 1137, us 985), gems collected 166-173 (us 178), 13.4 captures (us 12.3). They kill 8.6-9.3 wolves (40 gold, 4 gems), 4.3-4.4 elks and 7.8-8.8 gem clusters; we 5.3 wolves, 4.1 elks and 14.2 gem clusters. So their captures carry more gold and fewer cluster gems. At r600 their Vesper holds 1170-1250 gold of items (ours on b9 705), their 5-champion team 3700-4000 gold (ours 2680). Our pick values a gold at 0.25 gems (`gold_weight`), which ranks a gem cluster (7 gems, 120 health) above a wolf (14 points, 1350 health) at most distances. gw1 (0.5 to r600) and gw2 (1.0 to r400) test this.
- **Fuel probe on the heavy new maps (pf32, m4, 36 local games on 00vault, 02tangle, 02the-pack, 02harvest, 02stalactites, adgato-gemcombat5):** turns out of fuel per 1000: contact 2.22, quiet 2.41 (pf31 before wf1: 5.19 and 3.61). With finer stage marks, quiet run-outs come from group route rebuilds (`group_field`, "gf build", 59: one build costs up to 50k, 19k on average on these maps) and picks (51); contact run-outs from camp hits (11) and the post-turn step (11). 00vault and 02tangle hold 80% of them. On the platform these are about 1 turn per game after round 3, so they are not the next gap.

## Where the gold gap sits, by champion (main1026g on b9 and the top 12 teams, decoded, to r600, 2026-10-26 noon)

Per champion-game of each type, all team sizes; "top 12" is both sides of `data/fights/top12_20`. Gold is gold held as items plus unspent (30 per shard); a rise of 100 or more (133 for Vesper) in a round where an enemy died counts as one kill.

- **Camp gold by type** (us / b9 rivals / top 12): Vesper 632 / 844 / 1199-1261, Marcella 665 / 655 / 823-923 (with her tribute gold), Vendetta 385 / 539 / 577-600, Heart of Ruin 335 / 509 / 451-471, Varg 357 / 454 / 382. Kill gold is 33-68 per champion for us, 56-87 for the b9 rivals. Half of the camp-gold gap to the top 12 is Vesper's.
- **Captures:** our Vesper makes 5.8 capture events by r600 with 79 base gold each (gold / 1.33) and 14 gems; the top 12's Vesper 8.7-9.4 with 98-101 gold and 13-14 gems; the b9 rivals' 8.7 with 71. Only 8-13% of capture events are shared with a teammate on any side, so captures are solo for everyone.
- **What they hit** (camp hits to r600 per champion-game, wolf / elk / gem cluster / gold cluster): our Heart 32 / 39 / 22 / 31, the top 12's 55-59 / 43-47 / 7-8 / 11-15; our Vesper 49 / 62 / 13 / 12, theirs 68-70 / 56-58 / 11 / 18-20. Our Heart spends its hits on clusters and our Vesper on elks; the top 12 put both into wolves.
- **Time:** by r600 our Vesper hits camps in 123 rounds (top 12 141-146) and walks quietly (no enemy within 6, no camp within 4) 158 (136-141); our Marcella walks 207 (143-169). Walks that end at a camp: our Heart 101 rounds in 10.8 trips (top 12 78-79 in 8.6-9.7), our Vesper 88 in 11.8 trips (82-85 in 15-16, 5.3 rounds a trip against our 7.5). Tribute walks and time at spawn are about equal.
- **Per hit:** the team earns about 3.8 gold of camp gold per camp hit (top 12 about 4.8) and hits camps about 620 times per 5-champion team (top 12 about 740) by r600: 20% fewer hits and 26% less gold per hit, which compounds to their 1.5 times our camp gold. The per-hit part is target choice (wolves and gold clusters over gem clusters) plus their larger items.
- **Local check of gw2** (28 kept local games, `tools/local/local_decode.sh`, `data/runs/multi-110350`): `gold_weight` 1.0 before r400 moves the 5-champion r300 kills from 5.9 wolves, 15.3 gem clusters and 17.9 gold clusters to 9.0, 8.3 and 27.4 (the top 12 on b9 maps: 9.3, 8.8, 23.8), camp gold 956 to 1209, and team gold at r600 by 16% (3019 to 3489), for 21% fewer gems by r300 and 1.5% fewer by r600. gw3 (0.5 to r1000) adds 4% more gold at r600 for 9% fewer gems.
- **Not a capture-claim gap:** of the hits on a group that a champion then captures (to r600, since the group last respawned), our Vesper made 63% herself and the top 12's Vesper 59-61%; teammates 34% vs 35-37%. So their Vesper does not take over teammates' clears more than ours does: her extra gold comes from more and richer captures of her own. Our Heart of Ruin farms more alone than theirs (65% of its captures are of groups only it hit, top 12 42-45%, b9 rivals 41%).
- **Build order** (first three emblems by the round each first appears, main1026h vs b9 rivals vs top 12; emblems first seen in the same round are ordered by item index, a small artifact): our Vesper Treasure strength (r199), then Jungle health 52% / Power strength 26% (r314), then Durability health or Jungle health (r435); the top 12's Vesper Treasure strength (r178-200), then Jungle strength 33-48% / Power / Monster strength (r289-296), then Durability health / Bruiser health (r338-351); the b9 rivals' Vesper takes Jungle strength second in 42%. Our Heart of Ruin Treasure focus (r374), then Jungle health 75% (r520); the top 12's Treasure health 48-52% (r307-331), then Jungle focus 44-48% (r440-476). Our Vendetta Treasure strength (r336), then Jungle health 66% (r478); the top 12's Treasure strength or health (r263-279), then Jungle strength 38-48% (r410-416). The b9 rivals' Varg takes Jungle strength as its first emblem in 47%. Nobody else builds Jungle health second; our Heart, Vendetta and Varg reach their first emblem 60-100 rounds after the rivals'. `exp/js1` copies the Jungle-in-the-main-stat order (locally: Vesper Jungle strength second in 68%, r286).
- **Where our hits go** (to r600, each hit credited to the group life it fell in): 85% of our camp hits are on groups we then capture, 7% on groups the enemy then captures, 4% on groups nobody captures within 40 rounds (b9 rivals 90%, 3%, 3%; top 12 88-89%, 4-5%, 3%). Steals cost us about 5% of our hits.

## The gold gap is items held and starts in the opening (main1026h, gw2 on b9 and the top 12, decoded, 2026-10-26 13:00)

Measured with scratchpad readers over `data/fights/main1026h_b9_b9`, `gw2_b9_b9` and `top12_20`; gold held is unspent gold plus 30 per shard owned.

- **Same damage at the same items:** in rounds where one champion alone hits a wolf or elk, damage per round by main-stat shards held (0-4 / 5-9 / 10-14) is the same for every side: Vesper 60 / 87 / 120 for us, 59 / 83 / 114 for the b9 rivals, 56-56 / 86-87 / 108-117 for the top 12; Vendetta 90 / 118 / 170, 86 / 120 / 158, 87-89 / 123 / 162-164. Attacks per hitting round are equal too (Vesper 1.17 against 1.11-1.15, the attack reset included). So the camp-damage gap is the strength the champion holds: the top 12's Vesper holds 16.3-16.6 strength shards on average in her hitting rounds to r600, ours 7.4 (b9 rivals 9.6).
- **What a Vesper holds** (strength / health shards): at r300 ours 6.6 / 3.7, b9 rivals 8.4 / 3.5, top 12 11.9-12.4 / 4.2-5.5; at r600 13.4 / 9.4, 20.9 / 9.3, 26.2-32.2 / 12.5-13.0. After Treasure, Jungle (or Power, Monster) strength and one Durability health, the top 12 buy Bruiser strength emblems again and again (5 strength, 1 health, 1 focus each): some hold 5-9 by r450.
- **Gold held over time** (Vesper; team): r50 51; 106 (b9 rivals 54; 144, top 12 78-86; 147-154), r100 116; 260 (122; 331, 173-178; 355-374), r300 334; 967 (382; 1168, 547; 1305-1405), r600 693; 2373 (925; 2875, 1279-1341; 3215-3502). The gap opens in the first 100 rounds and then compounds. Our Heart of Ruin holds 31 at r100 (b9 rivals 67).
- **Same gems, more gold:** the top 12 collect 72-74 gems by r150 and 169-174 by r300, as many as main (75, 172), with 40% more team gold. By r300 their 5-champion teams kill 46 camps (wolf 9.3, elk 4.4, gem cluster 8.8, gold cluster 23.8) against main's 39 (5.4, 4.1, 13.4, 16.0). gw2 (gold counts as a gem before r400) moves us to 41 (7.5, 3.4, 9.8, 20.6) and team gold at r50 / r100 to 137 / 327, but collects 61 gems by r150 and 147 by r300, while the rivals in those games collect 97 and 222 (86 and 194 against main1026h): the gem clusters we leave go to them.
- **Vesper's first target:** an elk in 46% of games (b9 rivals 20%, top 12 21-24%), a gold cluster in 22% (34%, 31-48%); her first camp hit at r19.3 (16.2, 12.2-13.6). When her first target is a gem cluster she reaches it at r32.9 (rivals r12.5). gw2: elk 24%, gold cluster 37%, wolf 27%, first hit r16.6.

## Draft by team size: dq3 against main1026h on the pinned panel b9p (120 games each, decoded to r1000, 2026-10-26 13:50)

Same opponents' bots in both runs (b9p pins them to main1026h's games), so every difference is ours. dq3 won 44 against 33.

- **4-pick maps (26 games), Marcella in place of Varg:** 11 wins against 6. Our deaths by r1000 7.1 against 9.7 per game (Heart of Ruin 1.85 against 2.77, Vendetta 2.00 against 2.46, Vesper 1.38 against 1.73); gems collected 594 against 510, the rivals' 687 against 777. Marcella dealt 8478 champion damage per game by r1000 (Varg 3002) and collected 218 gems (196).
- **5-pick maps (73 games), the same five in a new pick order** (Heart of Ruin, Vesper, Marcella, Vendetta, Varg; main's was Heart, Vendetta, Vesper, Varg, Marcella): 23 wins against 17, gems collected 672 against 647, our deaths 5.8 against 5.7 and theirs 5.1 against 3.9; every champion's damage to champions rose (Heart 2694 against 2225, Vendetta 2803 against 2084). The pick order sets the champions' ids, slots and turn order, so this part may be chaos as much as a better team.
- **3-pick maps (21 games), unchanged code:** identical games, 10 wins in both runs, which confirms that the pinned panel repeats games exactly.
- **What is left after dq3** (b9p, per game, us vs the rivals): gems collected 184 vs 187 by r300, 390 vs 444 by r600, 634 vs 765 by r1000 (tributed 505 vs 640); team gold 0.90 of theirs at r300 and r600, 0.91 at r1000; deaths by r1000 5.7 vs 5.3 (main1026h: 6.2 vs 4.1). By numbers around the victim the deaths now match the rivals' and the top 12's (outnumbered 3 to 1 or worse: 1.28 per game, rivals 1.07, top 12 0.91-1.56). The remaining death gap sits on a few maps where our champions walk alone into the enemy's whole team (00ribs 60 deaths against 2 in 3 games, 00swirl 83 against 32, 00contest 22 against 0, 01starfish 49 against 31). So after the draft the largest gap is the mid-game economy: the gem gap opens after r300.

## Captures given up on the tile (b9p, dq3 against the rivals and the top 12, to r1000)

Tools: `decoded.py holds` (new) and `decoded.py captures` on dq3_b9p (120 games) and the top 12 set (66 ranked games, 10-26 morning).

- **Same clearing, fewer captures.** Group captures per game: 39.4 against the rivals' 42.5. By region (closer to own start, middle, closer to the enemy start): own half 29.4 vs 28.6, middle 7.5 vs 9.9 (176 vs 249 gems), enemy half 2.4 vs 3.9 (29 vs 47 gems). Clearing (first hit to last camp dead) takes 21.7 rounds vs 22.0 and claiming (last camp dead to the capture) 11.5 vs 11.2 (median 6 for both). Per champion the activity shares are the same for both sides (hitting camps 17%, on capture tiles 7%, moving 43-46%, dead 8%).
- **We step off before the capture.** A hold is a side's champions on a defeated group's tiles. We start 51.5 holds per game and the rivals 50.6. We capture 39.4 of them and leave 12.1 before the capture. The rivals capture 42.4 and leave 8.2; the top 12 leave 5.6-6.2. The figure is stable across our variants (main1026h 12.8, js1 11.9, dq3 12.1).
- **What was near when our last holder stepped off** (per game, us vs the rivals): an enemy on a tile 1.2 vs 0.8, an enemy within 4 of the group 4.2 vs 4.0, neither 6.7 vs 3.4. Of the 6.7: an enemy 5-8 tiles from the holder 2.6 vs 1.2, a teammate within 2 of the group 1.3 vs 0.5, camps hit in the next 10 rounds 0.7 vs 0.2, other 1.0 vs 0.3; the holder under half health 0.5 vs 0.3; home 0.2 vs 0.8 and tribute 0.3 vs 0.2. Most of our left holds end after 1-2 rounds (7.4 vs 4.9).
- **The cost:** of the groups we clear (last hit), 5.2 per game are not captured by us within 30 rounds (rivals 3.1, top 12 3.0), and in 2.7 of them an enemy came within 4 (49 gems per game; rivals 1.3 and 20). The enemy takes 2.2 of our cleared groups per game, we 0.8 of theirs.
- **The branches** (local probe cl0 on main, 140 games against cand1 and cp3): a chase in the pvp branch takes a healthy capturer off its tile 2.6 times per game, re-picks 2.6 (to another defeated group 1.3, a respawning one 0.9, a live one 0.4), flee 1.6, a bank trip 0.75, kite 0.2. A re-pick scores the capture in progress against the next target as if one excluded the other, though the capture ends within 5 rounds.
- **The middle race** (`decoded.py lives`, captured group lives by region): of 17.2 middle lives per game we hit 7.8 first (median 13 rounds after the group came up) and the rivals 9.1 (15); we capture 7.2 and they 10.0. They steal 1.53 middle groups per game from our first hits and we 0.83 of theirs; over the whole map they steal 3.1 and we 1.7. main1026h gives the same picture (middle first hits 7.5 vs 9.6, steals 0.77 vs 1.64), so about half of the middle gap is getting there first and half is steals, which hc2 targets. The top 12 hit 52% of the middle lives first and steal as much as is stolen from them.
- **Not the death penalty:** 19% of our captures lie in the middle whether or not the capturer died to an enemy in the last 400 rounds (rivals 22% and 29%), so the contested-group penalty after deaths (tu2) is not what keeps us out of the middle.

## The middle race is decided by position (b9p dq3 against the rivals, and the top 12 set, to r1000)

`tools/replay/race.py` and `tools/replay/zones.py` over `data/fights/dq3_b9p_b9p` (120 games) and `data/fights/top12_20` (66 games). A middle life starts when a middle group comes up (round 1 or a respawn) and ends with its capture, as in `decoded.py lives`.

- **Who hits first is who was nearer when the group came up.** Of our 7.8 middle first hits per game, our nearest live champion was a median 6 tiles from the group at that moment and theirs 12; of their 9.1, ours was 12 and theirs 6. In their first hits we were nearer in 1.1 lives per game, even (within one tile) in 2.5 and they were nearer in 5.4; in ours the mirror image (4.5, 2.2, 1.1). Median delay from up to the first hit: 13 rounds for us, 15 for them. Openings (lives from round 1) are even: 1.6 vs 1.7.
- **They keep more champions near the middle.** Champions within 10 tiles of a middle group when it comes up, averaged over the lives: ours 1.18, the rivals' 1.37. The top 12 have 1.59 there against their opponents' 1.34, and hit 10.4 middle lives first per game against 8.9.
- **What our nearest champion did instead** (their first hits, its first event in the next 40 rounds, per game): fought an enemy champion 5.15, hit own-half camps nearer to it 1.02, hit other middle camps nearer to it 0.91, went home 0.64, hit this group after them 0.30, tributed 0.20. The top 12 in the same spot: 4.53, 1.36, 0.98, 0.73, 0.21, 0.24. So the choice of the nearest champion looks like the top 12's; the difference is where the champions are.
- **Time by zone** (share of champion-rounds, own half / middle / enemy half / dead, each side from its own view): r150-300 us 0.68 / 0.19 / 0.05 / 0.09, the rivals 0.62 / 0.20 / 0.09 / 0.09; r300-600 0.67 / 0.19 / 0.06 / 0.08 against 0.62 / 0.22 / 0.09 / 0.07; r600-1000 0.64 / 0.19 / 0.07 / 0.09 against 0.60 / 0.22 / 0.09 / 0.08. The top 12: 0.66 / 0.19-0.20 / 0.07-0.08 from r150. We spend about 5 points more of our time in our own half.
- **The levers left** in `pick_group` (`targets.h`): there is no middle bonus since ge4 (`mid_push = false`, x2 before r400 for groups with side -6..6 within 20 tiles; hb4 still had it, and Michael's op2 removing it on hb4 was neutral locally), and a respawning group's wait counts 2-4 rounds per round (x4 on our side, x2 on contested ones), so champions do not wait at middle groups about to come up. hc1 (holding the tile) brought holds left to the rivals' level without raising gems, so the remaining middle gap is arrival, not holding.

## Where the extra own-half time goes (b9p mw1 against the rivals, r150-1000, 2026-10-26 17:45)

Scratch readers over `data/fights/mw1_b9p_b9p` (120 games); zones as in `tools/replay/zones.py`.

- **Alive champion-rounds in our own half:** us 0.713 of all alive rounds, the rivals 0.668. The whole gap is one kind of round: at 90%+ health, an empty bag, 6+ tiles from the start tiles: us 0.226, the rivals 0.178. Bag-carrying, low-health and near-home rounds are level.
- **In those rounds we walk:** moving without hitting 0.151 vs 0.114; hitting camps 0.035 vs 0.027; nothing 0.035 vs 0.033. Of the moves, walking outward not right after a tribute or a respawn is 0.062 vs 0.046, and sideways (same distance from home) 0.020 vs 0.007.
- **Steady walks** (healthy, empty bag, not hitting, 6+ steps in 8 rounds), rounds per game: own half 160 vs 164, middle 25 vs 45, enemy half 7 vs 17. Walks that double back (net displacement under half the steps) are rare on both sides (own half 7.8 vs 9.5). So there is no target thrash; the rivals simply walk to middle and enemy-half targets more often, and our own-half rounds are more stop-and-go between own camps.
- **Two pick levers moved none of this:** mw1 (a middle group's respawn wait counted once per round) and mb1 (the old x2 middle bonus before r400) left champions within 10 of a middle group when it comes up, and middle first hits, where they were (`docs/experiments.md`). mb1 raised deaths to 931 from about 812.

## We lose even fights the rivals start (b9p mw1 against the rivals, to r1000, 2026-10-26 18:05)

`decoded.py starts`, `risk` and `defend` over `data/fights/mw1_b9p_b9p` (120 games).

- **Deaths by who started the fight**, per game: ours in fights the rivals started 2.98, theirs in fights we started 1.86; both started 1.03 vs 0.79. They start 28.8 fights per game (38% outnumbering us), we 22.9 (30%).
- **Same situation, more deaths:** P(death within 10 rounds) at half health or more with one enemy and no ally within 6: us 0.020, the rivals 0.012; with two enemies and no ally 0.071 vs 0.033; two enemies and one ally 0.046 vs 0.028. The rounds spent in each state are about equal.
- **Attacked at half health or more** (`defend`, next 6 rounds): we hit back less and die more. Varg hits in 0.36 of rounds (rivals 0.46) and dies 0.22 (0.13); Heart of Ruin 0.42 / 0.21 against 0.46 / 0.14; Vendetta 0.35 / 0.14 against 0.38 / 0.09; Vesper 0.26 / 0.12 against 0.35 / 0.11. We are attacked more often too (Vesper 5.6 times per game against 2.6).
- **Likely cause in the code:** the threat branch (`bot.cpp`) treats a fight as lost when the enemies' power (health x damage within 5) is over 0.9 times ours, so an even fight sends a healthy champion into the kite step unless the simulation says we win, and the simulation scales enemy damage by `cal_f` (up to 2x, from the damage taken against the damage predicted). fb1 and fb2 (`docs/experiments.md`) test the two.

## Where the gem gap comes from (b9p mw1 against the rivals, ranks 18-40, to r1000, 2026-10-26 evening)

Readers: `tools/replay/groupkind.py`, `budget.py`, `deaths.py`, `surprise.py`, `response.py` (new), `decoded.py sources`, `champs`, `channels`, over `data/fights/mw1_b9p_b9p` (120 games); compared with `data/fights/top12_20` (66 ranked games of the top 12) and `data/fights/t2040` (48 ranked games of the ranks 20-40 teams, `tools/replay/teamdl.py`).

- **Gems collected 672 vs 791.** By the camp type last hit: wolf 66 vs 118, elk 178 vs 226, monolith 8 vs 30, gem clusters 292 vs 309, gold clusters 94 vs 86, golem 30 vs 18. By group kind and region (`groupkind.py`, captures and their gems per game): middle elk groups 1.68 vs 2.86 (-35 gems), monoliths 0.04 vs 0.12 (-18), enemy-half elks 0.32 vs 0.77 (-17), own wolves 8.5 vs 10.0 (-18), middle wolves 1.8 vs 2.7 (-14); we take more own elks (+22) and middle clusters (4.5 vs 3.8, +28). The top 12 take own elks 8.6 and own wolves 10.3 per game, own clusters about 11 (we 7.0, 8.5 and 14.0).
- **The time budget is the same** (`budget.py`, share of champion-rounds): hitting camps 0.171 vs 0.177, walking without a bag 0.290 vs 0.286, on a dead group 0.073 vs 0.072, dead 0.081 vs 0.069, hitting champions 0.037 vs 0.043. Unspent gold is 10% of held gold for both sides at r300-600. So the gap is what a round yields (damage, item gold, which groups), not how the rounds are spent.
- **Deaths to champions 5.13 vs 4.09 per game** (`deaths.py`, situation 10 rounds before): at full health 1.98 vs 1.30; with no enemy within 6 then 0.88 vs 0.43; having hit no champion in those 10 rounds 0.97 vs 0.47 (`surprise.py`: an enemy within 6 for 7+ rounds, 4+ hits taken 0.54 vs 0.18; Vesper 0.35 vs 0.10, Vendetta 0.23 vs 0.08, Varg 0.15 vs 0.05). These are chases in which our champion neither escapes nor hits back.
- **Same response, worse outcome** (`response.py`, fight episodes on a champion at 50%+ health, 12 rounds): fought 7.8 per game (dies 0.20, an enemy near dies 0.18) vs 8.7 (0.16, 0.21); mixed 14.2 (0.10, 0.15) vs 11.6 (0.07, 0.20); ran 5.0 (0.06, 0.05) vs 4.7 (0.04, 0.09). At even numbers the outcomes match (fought 0.13 vs 0.12 deaths); when outnumbering we fight less often (2.3 vs 3.8 per game) and convert fewer kills.
- **Big bags leak.** Gems lost on death per game (whole game) by bag: 200+ 31.2 vs 13.9, 100-199 10.3 vs 8.2, 60-99 16.5 vs 13.1, 30-59 22.1 vs 13.6. Solo captures of 100+ gems: 0.62 per game (109 gems) vs 0.45 (82); a teammate shares such a capture 7% of the time (rivals 15%). Single deaths carried 676 (the_pack, r1889), 600 (contest), 470 (rows), 343 (vault) gems. On rows the 470-gem capturer (one capture) started a 47-turn channel and died in it; on vault 343 gems and a 34-turn channel, the same. A tribute takes 0.1 turn per gem.
- **00contest (the ruliad and Nyx: 0 gems in every run).** The only gems are three monolith clears (200 each). Our Marcella took all three (r1344-1785) and carried 600 gems for about 450 rounds: 37 rounds of tribute channels, all broken (enemy stuns and an altar lock; all five enemy champions carry a lock from r200), then the team was wiped at r1840 and the enemy Ryth tributed her 600. Locally against a lock bot (`tools/variant/mklock.py`) we see and break enemy locks (5 hits), so the loss is the channel length, not the lock code.
- **Massacres:** 00ribs against the ruliad and Tartarus (0 and 14 gems in every run): we die 20-23 times to 0-2, every death on the centre line 40-70 tiles from both homes, one champion at a time from r57. 00swirl and starfish look the same (20-46 deaths).
- **Always lost across 11 runs on b9p:** 30 of 120 games; Nyx 7 of 10.

## Repeat deaths against ranks 20-40 (b10, 10-26)

Source: `mw1_b10@b10` (main against 21 teams ranked 20-40, 105 games, 29 wins), decoded in `data/fights/mw1_b10_b10`; reader outputs in `data/analysis_b10/`. Readers: `tools/replay/massacre.py`, `repeat.py`, `alone.py`, and `decoded.py`.

- **Two kinds of losses.** 17 of the 105 games are massacres (our deaths 12+ and 2.5 times theirs; all lost): 21.2 deaths per game against 3.0, 42% in our own half and 42% in the middle, 41% with no ally within 6, 71% within 6 tiles and 150 rounds of an earlier death of ours. In the other 88 games we die 5.5 times per game and they 6.5, so the whole death gap sits in the massacres. The remaining losses are quiet economy races (gems collected by r1000 664 vs 844 over all games; middle captures 7.9 vs 11.0 per game, 176 vs 250 gems).
- **Repeat deaths** (`repeat.py`, to r1000): 3.37 of our 6.45 deaths per game are repeats against the rivals' 2.13 of 4.69. The victim is a teammate of the earlier victim in 2.67 (rivals 1.50); the same champion back from respawn 0.70 (0.63). Over 10 rounds after the earlier death and outnumbered by 2+ at the death: 1.19 per game against 0.34. Traced victims walked 15-25 tiles back to the spot, saw 2-4 enemies at 4-8 tiles and kept going (`starvation`, `adgato_gemcombat3/4`, `elkring`). Vision is not shared, so a teammate never learns of the death.
- **Alone against two or more** (`alone.py`: no ally within 6, 2+ enemies within 6, half health or more): 59 rounds per game for us, 45 for them. At 5-6 tiles the rivals step away in 29% of those rounds and we in 17% (we keep level 24% vs 13%, stand 23% vs 18%); at 3-4 tiles 36% vs 27%. We die within 10 rounds 3.8 times as often at 5-6 tiles (0.045 vs 0.012), 2.8 times at 3-4 (0.115 vs 0.041) and 2.2 times at 1-2 (0.215 vs 0.097).
- **Fight quality, for reference** (`decoded.py risk`, `shots`, `assist`): in the same numbers state we die about twice as often (no ally, 2 enemies within 6, high health: 0.097 vs 0.041 within 10 rounds). Our Vesper hits a champion in 45% of rounds with one in range, theirs in 60% (champion damage 3378 vs 5948 per game; at r600 theirs holds about 60% more strength shards). Earlier tries to make her shoot more (vh1m, vs1) raised her deaths.
- **Tested on this factor:** ob1 (back off when alone against 2+) and kz1 (a shared kill-zone mark that `pick_group` avoids for 150 rounds); see `docs/experiments.md`.

## Gems lost on death: carriers (b10, b9p and top-12 games, 10-26)

Measured with `tools/replay/carrier.py` and two scratch counts (bags at death, banking base rate), to r1000. "Carrier" means a champion with 30+ gems in its bag.

- **Exposure is level, the death rate is not.** We carry 30+ gems about as long as the rivals (b10 630 vs 549 champion-rounds per game, b9p 550 vs 548), but die 1.69 times per 1000 such rounds against 0.75 (b9p 1.41 vs 0.85). Gems lost on death by r1000: b10 94 vs 42 per game, 75 vs 27 of them in deaths with 30+; b9p 71 vs 45. A killer takes the whole bag, so each lost gem is also an enemy gem.
- **Shape of a carrier death** (b10): last activity `flee` in 0.65 of 1.07 per game (`D` lines); 2+ enemies within 6 at the death in 0.73 vs 0.21; after carrying 30+ for over 60 rounds in 0.61 vs 0.12; not heading to an altar in the 10 rounds before. 17% of our deaths carry 30+ (rivals 9%, top-12 games 10%).
- **After an enemy comes within 8** (b10): rival carriers start a tribute within 15 rounds in 30% of cases (2+ enemies 27%) and die in 1% (2%); ours 17% (15%) and 3% (10%), from the same altar distance (8 vs 9 tiles). b9p: 31% / 41% against 21% / 19%. Without an enemy in sight (sampled every 15 rounds) the rate is 0.38 vs 0.26 at 5-12 tiles from an altar, 0.23 vs 0.28 within 4: the rivals bank more at mid distance anyway, and a sighting lowers our rate (0.26 to 0.17) more than theirs (0.38 to 0.30).
- **Top-12 teams** (38 ranked games of 10-26, engine 2.0.0, `teamdl.py`): their carriers bank after a sighting no more than ours (20%, 2+ enemies 18%; their opponents 20% / 14%), quiet rate 0.25 at 5-12 tiles, and die 0.88 times per 1000 carrying rounds (their opponents 0.82). Their games have more deaths on both sides (6.1 per game), but carriers are 10% of them. So banking on sight is a habit of the ranks 20-40 teams, not of the top; what the top share with them is a carrier death rate about half ours.
- **Passing an altar** (a champion with a bag comes within 2 of an altar; P(tribute within 3 rounds)): b10 rivals 63-94% with no enemy within 8 and 32-71% with one, we 49-86% and 19-38%; b11p 84-99% / 46-79% against 35-81% / 11-30%; the top 12 64-89% / 38-67%. So better teams tribute at every altar they pass, also with an enemy near; we hold small bags for the batch and, with an enemy near, flee or fight instead.
- **Tribute counts** (b11p base, whole games): the rivals start 27 channels per game, we 17.7; of 20 gems or less 10.9 against 5.7. Channels over 100 gems complete 64% for us, 79% for them; over 30 gems with an enemy within 4 during the channel, 65% against 75% (an enemy cast on the channeler in 22% against 6%).
- **Enemy altar locks:** every one of our 382 hits on units that are neither champions nor camps in the 25 b11p base games came from a carrier within 2 of an altar, so they are hits on enemy locks (a lock takes 5): 15 hit rounds per game, on maps of all five b11p teams (the_pond 65, anvil 55, breadcrumbs 45, dunes 35, gold_rush 30). The rivals never hit one (we place no locks). Traced deaths include carriers that stood at a locked altar for 10-16 rounds while enemies closed in.
- **Traced carrier deaths** (b11p base, scratch `ctrace.py`): fleeing home 20 tiles past an altar 1 tile away with 70 gems; bank walks of 10-20 tiles into enemies standing near the altar (crater, dunes, gemcombat3); a carrier with 111 gems leaving its own spawn for an altar and dying on the way; channels of 11-14 turns (105-137 gems) started with enemies 3-7 tiles away.
- **Death rate by bag** (`tools/replay/bagrate.py`, b11p base mw1, to r1000): per 1000 rounds alive, our champions with 0 / 1-29 / 30-59 / 60+ gems died 2.26 / 1.10 / 1.97 / 3.70 times, the rivals' 1.38 / 1.26 / 0.50 / 0.63 (b10 rivals 1.35 at 0, 0.70 at 30-59 and 0.82 at 60+; top 12 1.77-1.83 at 0, 0.90-0.95 at 30-59 and 0.72-0.79 at 60+). Better teams' carriers die less often than their empty-handed champions; ours died more often. Our 60+ carriers had an enemy within 8 in 38% of their rounds, the rivals' in 26%.
- **What decides a death in contact** (b10 base, 105 games, to r1000, scratch `factors.py`; contact: an enemy champion within 6; outcome: death within 10 rounds): our champions spend 755 contact rounds per game (rivals 793) and die in 7.8% of them (5.0%). The team hp share within 8 (own side over the enemy's) decides most: our 30+ carriers die in 0.227 / 0.117 / 0.080 / 0.026 / 0.013 of contact rounds at shares <0.5 / 0.5-0.8 / 0.8-1.25 / 1.25-2 / 2+, the rivals' in 0.131 / 0.052 / 0.042 / 0.020 / 0.015, and our carriers spend 21 / 18 / 26 / 27 / 34 contact rounds per game in those classes against 9 / 11 / 18 / 20 / 31. So the gap is both more time in unfavourable contact and a higher risk in it. The rivals hit enemies with a bag as often as we do (60+: 27% of contact rounds, we 21%). The bag itself does not change our risk (logistic coefficient 0.0 with the other factors in), while it lowers theirs.
- **Fitted risk model** (`tools/replay/riskfit.py`, b10 + b9p base, 225 games): P(death within 10 rounds) = sigmoid(-1.99 - 0.577 log2(share) - 2.505 hp_frac + 0.586 enemies_within_4 + 0.447 hitting) for us (share: own hp plus allies' within 5 over the enemies' within 6) and sigmoid(-1.804 - 0.410 log2(share) - 3.170 hp_frac + 0.594 enemies_within_4 + 0.679 hitting) for the rivals. Predicted and observed rates agree within 0.003 in every quintile; a fit on our 30+ carriers alone gives nearly the same coefficients. At full health, one enemy within 4 and an even share the risk is 0.020 for us and 0.012 for the rivals.
- **How carrier deaths happen** (b10, scratch `cdeath.py` and `contact.py`): 1.07 deaths per game with 30+ gems (average bag 70) against the rivals' 0.41 (67). The contact spell before such a death lasts a median 18 rounds (theirs 17); it starts at a share of 1.25+ in 48% of our deaths (theirs 70%) and ends below 0.8 in 75% (44%): favourable contacts that turn. Contacts of 30+ carriers start 8.0 times per game (rivals 6.2), with the enemy closing in 2.6 times (1.5) and our carrier itself 2.5 (2.6); only 5% of them end in a death within 15 rounds (2%).
- **Tested on this factor** (`docs/experiments.md`): sg1 (bank on sight) and kl1 (cancel enemy tributes) rejected, at1 (tribute at every altar passed) not accepted; cc1 (no fights, and every threat a lost fight, from 50 gems) cut our gems lost on death by r1000 on b11p from 141 to 109 per game, cc2 (the same from 30 gems) to 80, with deaths per 1000 rounds at 30-59 / 60+ gems of 1.35 / 1.46 (rivals 0.50 / 0.18). cc2 is main from 10-27 00:05; it lands 14 fewer hit rounds per game and the rivals die 1.0 time less. Graded rules on the risk model above all lost to the fixed bar on b11p (gems lost on death by r1000, cc2 80 per game): rk1 (leave a fight or skip it when P(death) x stake, stake 2 x bag + 25, exceeds the gain) 110, rk2 (a lower threshold) 118, rk3 (a risk budget: P(death) x 2 x bag under one gem) 94. A turn-by-turn graded rule flips between staying and leaving as the share moves, where the fixed bar commits a carrier to leaving; and letting some carriers fight raised fighting team-wide. ca1 (cc2 + at1) 84 and cc3 (the bar at 15) 89 were rejected too. On b12p mw1 loses only 42 gems per game on death (b11p 141), and cc2 there loses 41: the carrier factor depends on the opponents, and the stronger killers of carriers are in b11p.
- **Carriers at low health** (cw1 on bvp + bhp, 100 games, to r1000, scratch `hpbag.py`, `bagdeath.py`, `lowcarry.py`, `carrycell.py`; cw1 + cc2 panels, 150 games, for the reference rows): our champions with 20+ gems spend 53 rounds per game under 35% health, 46 at 35-50%, 143 at 50-75% and 689 above, the rivals' 24 / 38 / 101 / 750, and die under 35% at 3.2 per 100 rounds against 3.1: 1.7 deaths per game there against 0.7, nearly the whole carrier death gap (deaths with 20+ gems 1.84 per game losing 106 gems, rivals 0.84 losing 40). Empty-handed champions are as often low on both sides (120 vs 104 rounds under 35%), so the rivals keep health in hand when they carry and we do not. We start 4.9 low-health carrier episodes per game, the rivals 2.5, alike in cause: about half were at 75%+ health ten rounds before, half hit camps in those rounds, half had an enemy within 4. Capture rewards followed by death within 15 rounds cost only 11 of our 97 gems lost per game (rivals 5 of 36). In contact (an enemy within 6) our carriers die 0.87 times per 100 rounds against 0.40, mostly from the low-health, no-ally cells (one enemy 7.3 rounds per game at 3.2 per 100, rivals 4.8 at 1.8; two 4.3 at 6.7, rivals 1.9 at 4.6; three or more 2.7 at 15.6, rivals 0.3 at 20.9).
- **Carrier deaths on cw1** (bvp, bhp, b11p, b12p, 150 games, to r1000; `tools/replay/bagdeath.py`, `carrierctx.py`, `decoded.py gems`): gems tributed 472 per game against the rivals' 622, lost on death 92 against 38, in the bag at r1000 71 against 91, collected 635 against 750. Deaths with a bag of 20+ 1.51 per game against 0.72, with 2.24 enemies and 0.47 allies within 6 (rivals 1.52 and 0.90), 8.8 tiles from the nearest altar (8.7), at 58% health six rounds before (55%), after carrying 20+ for 100 rounds (101); heading to an altar in 21% (12%), channelling in none. With a bag of 30+: 0.89 deaths per game losing 69 gems against 0.43 losing 26; channelling 0.05 vs 0.03, within 3 of an altar 0.17 vs 0.07, hitting camps 0.01 vs 0.03, elsewhere 0.65 vs 0.29 (48 vs 16 gems). Carrier deaths are mostly pack deaths in the open, not at altars or in camp fights.
- **Health in hand does not save carriers** (rv1, rv2, 10-27): a reserve of 0.5% health per gem carried (at most 30%) in the retreat and heal rules cut carrier rounds under 35% health from 49 to 32 per game over the four panels, yet deaths with a bag of 20+ stayed at 1.35 per game (cw1 1.51) and gems lost on death at 92 (92); on b11p and b12p both rose. Of our carrier (30+) deaths, 0.38 per game (31 gems at the time) had passed within tribute range of an altar in the 150 rounds before without tributing, 0.33 of them with an enemy within 8 (rivals 0.15 and 0.11), and only 0.02 per game during a camp fight (scratch `lastpass.py`), so banking during camp fights would save about 2 gems per game.
- **Tribute channels** (cw1, four panels, `decoded.py channels`, `tools/replay/breaks.py`): bags over 100 complete 79% against the rivals' 98%, 51-100 90% against 98%. Per channel turn with one enemy within 10 of the altar ours break 0.011 against 0.0018, with two 0.026 against 0.0074. Broken channels per game: by enemy locks 0.46 (rivals 0.17), by enemy casts (stuns) 0.29 (0.01), by the channeler's death 0.05 (0.03); 42, 27 and 12 gems in them. A broken channel keeps its gems unless the channeler dies, so channels cost time and exposure more than gems.
- **Held altars** (`tools/replay/heldaltar.py`; a carrier with 20+ gems closing on its nearest altar from 4-10 tiles while two or more enemy champions stand within 3 of it): cw1 1.70 such walks per game, 12% die within 15 rounds, 11.4 gems lost per game; the rivals 1.08, 2%, 1.1. ha1 (10-27) made `bank_gems` hold off at a held altar and moved nothing (1.82 walks, 11% deaths, 11.5 gems; lost on death 105 against 92): so these walks are mostly not bank trips (heal trips home, picks or help calls that pass the altar are the likely rest; not measured, since the bot logs no activity on the platform).

## Marcella is built thin (b11p and b12p cc2 runs against the rivals, to r1000, 2026-10-27)

- **Items at r600** (`decoded.py items`): our Marcella holds Power-focus 0.94 (b11p) and 1.42 (b12p) emblems, Treasure 0.83 and 0.95, Durability 0.44 and 0.47, Jungle 0.56 and 0.68, with 1756 and 1800 max health. The rivals' Marcella holds Bruiser-focus 2.35 and 2.41, Bruiser-health 1.65 and 0.77 emblems and 2817 and 2732 max health. The top 12 (10-26) build her Bruiser of strength, focus and health (2.36 / 2.27 / 0.91 emblems, 2497 max health).
- **Deaths and gems** (`decoded.py types`): ours dies 1.89 (18 games) and 1.19 (21 games) times per game by r1000 and collects 168 and 179 gems; the rivals' Marcella dies 0.22 and 0.62 times and collects 306 and 191.
- **Why the formula picked Power** (`shop.h`): after Treasure, Marcella's focus is about 130 and her health about 1200, so Power scores 6 x 14 / 130 = 0.65 against Bruiser-focus 5 x 14 / 130 + 100 / 1200 = 0.62; Bruiser's strength (her basic attack grows 4.5 per strength shard) was counted only for Heart of Ruin. With it (+4.5 / 45 = 0.10) Bruiser-focus scores 0.72. Locally (mc1, 120 Marcella games) her final items become Bruiser focus 6.2 and Bruiser health 3.7 emblems, against cc2's Bruiser focus 4.3, Durability 3.5 and Power 2.7.
- **Much of the gap is gold**: in the 13 b12p games we lose on both mw1 and cc2, our Marcella's max health at r600 is 1423 against the rivals' 2854 (`paired.py --type marcella`). With half the items, the build order alone cannot close it.

## Hole maps: the walk to the altar (probe of the 70 maps, ladder losses, dh1 and dh3 on the platform, 2026-10-27)

- **The loss that showed it:** We NEED internships (rated about 1800) beat us 996-0 on road_of_riches (10-27 01:44), and estrogen :3 1005-0 there earlier. Each spawn is walled in by a spiral with one-tile hole lines: walking, the altar is 121 steps from our spawn; one dash over a hole line makes it about 20. We tributed nothing in 629 rounds while bags reached 278 gems; the rivals' dashers farmed the centre and banked there. Our routes treated holes as walls (`W.terrain` includes holes). Ladder record on road_of_riches before dh3: 0 of 4.
- **Survey** (probe `bots/exp/mp1` prints the terrain grid; grids in `data/mp1/grids/`; scratch `holegap.py`, `dh2open.py`): with the useful holes open (both sides walk-reachable from our spawn, walk distances differing by 20+), the walk from our spawn to the altar shrinks by 40+ steps only on road_of_riches (121 to 25), shortcut (112 to 46), concentrated_wealth (88 to 28) and fracture (79 to 39); great_wall saves 29, reverse_spiral 22, gemfight 18, quarry 13, breadcrumbs 12, gold_rush 7.
- **Crossing everywhere loses** (dh1, b11p + b12p, paired to r1000): where the crossing saves little it leads into the rivals' fights: gemfight our deaths 4 to 22 and 1 to 8 (two wins became losses), gold_rush 3 to 25; where the walk is far longer it wins: concentrated_wealth collected 208 to 887 (loss to win), shortcut 504 to 930.
- **Crossing only where it saves 40+** (dh3 on the pinned panel `bhp`, 40 games on the four maps): tribute margin +290 ± 81 per game (road_of_riches +695, shortcut +206, concentrated_wealth +174, fracture +86), our deaths +2.5 and theirs +2.8, wins 20 vs 10 of 50. Adopted as main (version 831).
- **Fuel note:** `distance_field::export_linear_buffer()` and `bitboard::export_linear_buffer()` (bits, least significant first) read a whole field or board in one call; a per-tile `get` or `is_set` is a 40-50 fuel host call, and dh2's per-hole reads (about 830 fuel a hole) stopped at its fuel floor on fracture without opening anything. On road_of_riches the first turn's init has only about 2k fuel left when it reaches the hole test, so the rest of init runs on turn 2 (the bot resumes where it stopped).

## Massacres in ranked games (our last 100 ranked games to 10-27 02:40; 14 losses decoded in `data/fights/mass1`)

- **14 of the last 100 ranked games** are losses where we die 14-37 times and the rivals 0-6 (gold_rush 34/0 and 37/0, collision 21/5, stalactites 15/0, gemfight 19/1, fragment 21/4, starfish 21/6, gemcombat5 14/3, eight 14/5 and 16/0, gemcombat2 18/1, gemcombat1 20/2, breadcrumbs 15/4, ribs 16/0). Our draft in all of them: Heart of Ruin, Vendetta, Vesper (+ Marcella, + Varg).
- **Gold** (`decoded.py gold`): our team gold is 0.38 of theirs at r300 (460 vs 1226) and 0.33 at r600 (1030 vs 3144). Camp kills to r300: gold clusters 7.6 vs 14.1, gem clusters 19.4 vs 16.6: they farm gold first. On the b11p + b12p panels the ratio is 0.77 at r300 (0.64 on 4-pick maps).
- **Items at r600** (`decoded.py items`): their Vendetta holds Bruiser-strength 1.54 and Bruiser-health 0.54 emblems with 1777 max health; ours holds Treasure and Jungle with 877, our Heart of Ruin 785, our Vesper 1038.
- **Where we die** (`massacre.py`): 55% on our own half, 26% middle, 20% their half; 41% alone (no ally within 6); 69% within 6 tiles and 150 rounds of an earlier death of ours (`repeat.py`: 11.0 repeat deaths per game against their 0.43). Typical: a full-health champion dies within 10 rounds to one or two enemies.

## boss_battle: we never hit the guard (our 6 ranked boss_battle games, 10-26/27, `data/fights/boss1`)

- Ladder record 0 of 6 (gems 465 vs 1151). `decoded.py guard`: we hit the altar guards 0 times in 5 of the 6 games (40 in the sixth); the rivals hit them 115-378 times and killed the first guard monolith at r472-r1130. We tributed nothing by r1000 in 4 of the 6.
- By r1000 we collect as much as they do (1547 vs 1521 per game) but carry 1220 in bags and tribute 132 (they 355). Our channels with 100+ gem bags complete 36% of the time (4.2 per game; theirs 78%), mostly with two enemies within 10 of the altar.
- `pick_group` has no guard logic: two comments ("The altar guard is itself a monolith group", "its worth grows with the gems we cannot bank") have had no code under them since before the 10-23 restructure. With the guard exempt from the covered rule (gk2 = gk1 on cc2) our champions kill it locally at r818-r971, no sooner than the rivals do on the platform, so that change alone would not win these games.

## Ranked record by map (our last 300 ranked games to 10-27 03:30, scratch `permaprank.py`)

- No win: boss_battle 0 of 6 (465-1151), quarry 0 of 5 (215-1022, deaths 10.0 vs 6.8), vault 0 of 4 (347-1109), road_of_riches 0 of 4 (539-1015), uncharted_lands 0 of 3, adgato_gemcombat1 0 of 3 (363-1035), oasis 0 of 2, monolith 0 of 2. One win: eight 1 of 7 (416-968, deaths 13.6 vs 4.7), ribs 1 of 5 (233-884, deaths 18.2 vs 8.0), gold_rush 1 of 4 (deaths 23 vs 9), stalactites, gemfight, starfish, yellow_brick_road 1 of 4.
- quarry (7 ranked games, `data/fights/q_quarry`): we collect 96 vs 206 gems by r300 and 320 vs 930 by r1000; the rivals bank small bags all game (32 channels of 50 gems or less per game, ours 12). Our activity counters to r500 (replay stdout `A` lines) show 77-146 rounds of `capture` per champion. The hole detour there is small (altar 24 walking, 12 with holes), so it is not the dh3 cause.
- vault (4 games, `data/fights/q_vault`): collected 442 vs 1243 by r1000, deaths 7.2 vs 3.8; only 4 hole tiles.
- corridors and yellow_brick_road (ranked 0 of 3 and 0 of 4 in our last 100 games to 10-27; 6 losses decoded in `data/fights/q_corr`, `decoded.py captures`, to r1000): middle captures 6.2 per game (191 gems) against 13.5 (395), own half 15.3 against 13.2, enemy half 0.2 against 2.3; claim time (last camp dead to the capture) 15.9 rounds against 7.4 (medians 6 and 5), capture cycle 140 rounds against 101.

## 00vault: one 343-gem group, a door fight and a hold (ranked 0 of 8; `data/fights/q_vault`, `main_bvp_bvp`, 10-27)

- The centre is one group: 49 touching gem clusters (120 health, harmless), 343 gems a capture (428 with a Prospector emblem; the rivals had them), respawn 50 rounds after the capture. The rest of the map holds 4 wolves and 4 gold-cluster groups, so three captures decide the game. `tools/replay/vault.py` lists who holds it and each capture.
- Ranked (4 decoded): captures us 4, them 13. The first race: we arrive first (r12) and clear most of it (49 to 8-10 clusters by r48-52), then lose the fight at its east door: in 375faa97 our Vendetta (120 of 1000) and Marcella (235 of 1200) kept fighting and died at r52-54, their Vendetta fled at 10 health, came back full from their spawn 12 tiles away, and their three champions took the capture from our two.
- A unit on any spawn tile stops the respawn, and 41 of the 49 tiles have no free neighbour off the group, so a champion of ours waiting for the respawn inside it never steps off (`camp_fight.h` tries one step). df114844: dead r195-r526 with only our champions on it for 267 rounds while both teams waited.
- That deadlock is not all loss: on `bvp`, rw1 (walk out) cut our hold time from 60 to 20 rounds per vault game, and our captures fell from 1.6 to 1.2 per game (theirs 2.1 to 2.4); where main held it after its own capture (b5279070) the game stayed even. Holding a big group down after our capture keeps a lead; leaving only helps when behind.
- 00monolith (ranked 0 of 3, `data/fights/q_mono`): close games decided by the two standalone monoliths (200 gems each), which the rivals kill at r739-r1263. Locally our champions start on them only after r600: the clear model needs health above six monolith hits plus 40 (`clear_time`).
- boss_battle guard (gk3, local): when our team kills the guard it arrives at the opened altar spent and the other side banks first (0-1187 against main's 0-0 draws). A guard plan needs the bank right after the kill.

## Packs: outnumbered deaths and what we do on sighting one (cw1 on bvp, bhp, b11p, b12p, 150 games, to r1000, 2026-10-27)

Readers `tools/replay/packs.py`, `packseen.py`, `packreact.py` and `packwalk.py` (logic in each file's header).

- **Deaths outnumbered by two or more within 6** (enemies minus allies at the death): 3.37 per game against the rivals' 1.13. In 97% of them the victim itself had had two or more of those enemies within 8 earlier (on average 19 rounds before the death; rivals 98%, 21 rounds); a teammate seeing them first while the victim did not is 1%. Vision is not the gap: the victim saw the pack and stayed.
- **Pack sightings** (two or more enemy champions within 8 off their spawn, at most one ally within 6, after 5+ rounds without): 29.6 per game for us, 26.7 for the rivals, at the same distance (6.0 vs 5.7). Over the next 5 rounds both sides step away from the pack equally (-0.40 vs -0.39 tiles net), but we hit camps in 0.57 of those rounds and champions in 0.53, the rivals camps 0.37 and champions 0.70. We die within 15 rounds in 9.1% of sightings, they in 5.7%; at 75%+ health 6.8% against 3.2%. Split by what the champion did in the rounds before the sighting (cw1 + dm1 on bvp and bhp): walking 17.2 sightings per game, death within 15 rounds 9.1% against the rivals' 4.2%; hitting champions 16.7% vs 13.0%; hitting camps 7.2% vs 4.9%.
- **Tested on this:** kb1 (two tiles more berth around visible packs) left the outnumbered episodes and deaths unchanged; ob1 (step away when alone against two or more, 10-26) and ro1 (walk home when outnumbered) moved nothing measurable either. Keeping away does not work; the rivals answer a pack by fighting it (hit rounds on champions 0.70) and stop farming.
- **pa1 (10-27, all four panels, 150 games):** a pack of 3+ that outnumbers us by two ends the camp fight for a re-pick, and `pick_group` divides by 1 + 0.25 danger² instead of 1 + 0.25 danger. Outnumbered deaths 3.43 per game against cw1's 3.39 (falls on bvp only: 3.16 vs 3.36; bhp 4.30 vs 4.14, b11p 3.16 vs 3.00, b12p 2.48 vs 2.36); death within 15 rounds of a 3+ sighting 13.8% against 14.7%, 3+ sightings 5.5 against 6.2 per game. Gems collected fell 635 to 599 (-5.7%) and tributed 472 to 433 (-8.3%) while the rivals collected 47 more, and our deaths rose 6.4 to 6.7. Seven variants now (kz1, kz2, ob1, ro1, kb1, dm1, pa1) avoided or left places with packs or deaths: none cut our deaths across panels, and the ones that moved the pick gave groups to the rivals. The outnumbered deaths are not a choice of where to farm.

## Idle time and deaths near home (platform runs bvp, bhp, b11p, b12p, b9p, mass1 and others, to r1000, 2026-10-27)

- Idle champion-rounds (alive, same tile, no action, off the start area; `tools/replay/idle.py`) per 100 alive rounds, us vs the rivals over 430 decoded games: inside a tribute channel 1.7 vs 2.0, beside a dead camp (respawn waits) 9.1 vs 9.8, beside a live camp 0.3 vs 0.4, an enemy within 4 0.6 vs 0.7, other (no camp or enemy near) 6.6 vs 5.0. The gap sits on maps with big groups: 00monolith 10.0 vs 3.6, 00the_line 12.2 vs 3.9, 02arena 11.9 vs 3.4, 00pilgrimage 12.4 vs 7.0, 00rows 10.1 vs 4.6, 00stampede 10.5 vs 7.1.
- Cause: the gather before groups of 200+ strength (`camp_fight.h`) restarted its 25-round count after each approach step, so a lone champion crawled towards the group one step per 26 rounds (on 00monolith it parked five or six tiles from a monolith from r400 on). Fixed in cw1. 00vault's "other" idle is mostly holds of the walled vault from its door tiles, two tiles from any camp: not waste.
- Our champions move less: 2230 move actions per game by r1000 against the rivals' 2561, and tribute less often (12.8 tributes against 17.6), while attacks (916 vs 862) and casts (417 vs 412) are level. We place more wards (237 vs 157).
- Most of the death gap is near our own spawn. Per game by r1000 (417 games), by distance from the victim's own start tile: 10 or less 1.74 vs 0.88, 11-20 2.68 vs 1.99, over 20 2.04 vs 1.75; so 1.55 of the 1.84 extra deaths fall within 20 tiles of home. Of the near-home deaths, those moving homewards over their last five rounds are 2.68 vs 1.31 (outwards 1.10 vs 0.99), outnumbered 1.92 vs 0.79, and at 90%+ health ten rounds before death 1.61 vs 0.98: champions caught on the way home by groups that kill them in under ten rounds.
- The worst maps for it: 00swirl (spawns about 15 tiles apart) 23.9 deaths per game within 10 of our spawn against 5.4, four of our champions dead by r57-r97 to a 4-stack; 00eight 7.0+6.2 vs 0.2+0.8; 01gold_rush 11-20 tiles 10.1 vs 1.7; 00oasis; 01starfish; 00stampede, where the rivals' five stand outside our spawn strip's 3-wide exit (x 14-16, y 9-11) and our champions come out one at a time (4.2 deaths per game in that 10x10 block by r600; all 9.2 of our deaths by r1000 there have an enemy within 4).
- Oscillation is not a cause: deaths after moving back and forth between two tiles are 0.105 per game for us and 0.133 for the rivals.
- By team size (b11p, b12p, bhp, bvp bases, 150 games): 4-pick maps are the worst, 16 wins in 53, deaths by r300 3.5 vs 2.1 and by r1000 8.2 vs 5.6; team gold at r300 744 vs 987, although camp gold by r300 is level (472 vs 459): the gold gap there is kill gold. 5-pick 31 of 86 (deaths r1000 6.0 vs 3.7), 3-pick 4 of 11 (2.5 vs 3.0).
- Cohesion (`tools/replay/cohesion.py`, cw1 on bvp + bhp): on 5-pick maps we stand with no ally within 6 in 51% of alive rounds to r1000 against the rivals' 37% (r0-150: 1.26 allies within 6 against 2.34), and a teammate hits the same group in 31% of our camp-hit rounds against 49%; on 4-pick maps the two sides are close (29% vs 25% alone). Closing that gap does not close the death gap: du1 (pairs in `pick_group`) brought us to 44% alone and 44% shared, and our deaths rose 0.5 per game while gems collected fell 6%. The death gap is in how our fights go, not in how spread out we are.
- Gems by camp type to r1000 (same 150 games, credited to the camp type last hit): gem clusters 272 vs 348, wolves 72 vs 132, elks 116 vs 151, gold-cluster groups 128 vs 101, golems 10 vs 22, monoliths 5 vs 13.

## Builds after the patch, and where the margin is lost (cw1 on bvp, bhp, b11p, b12p, decoded, to r1000, 2026-10-27)

- **The rivals left Treasure.** First emblem (`tools/replay/emblemorder.py` over b11p, b12p and bhp): their Vesper Prospector 35%, Treasure 30%, Capture 19%; Heart of Ruin Prospector of health or focus 39%, Treasure 35%, Capture 9%; Marcella Treasure 39%, Prospector of health 21%, Bruiser 8%, Capture 8%; Vendetta Capture 40%, Prospector 28%, Treasure 26%. Ours is Treasure in 82% (Vesper), 75% (Marcella), 92% (Heart of Ruin) and 96% (Vendetta). Their second emblem is Jungle of the main stat (Vesper 57%), ours Jungle of health (47-80%). At r600 (`decoded.py items`, b11p + b12p) their Marcella holds Bruiser-focus 2.18 and Bruiser-health 1.18 emblems with 2644 max health, ours Power-focus 1.43 and Treasure 0.86 with 1681; their Vesper Bruiser-strength 2.08, ours Power-strength 1.15. `pr2` tests Prospector first.
- **Team gold** (`decoded.py gold`): 1091 / 1202 at r300 (0.91), 2603 / 2709 at r600 (0.96); 4-pick maps 783 / 968 at r300. Camp kills to r300 are level or better for us (gold clusters 20.8 vs 17.6, gem clusters 20.3 vs 17.8, wolves 5.9 vs 5.9), and gems by r600 come from gem clusters 195 vs 224, elks 75 vs 91, wolves 44 vs 84, gold clusters 70 vs 51.
- **The margin is lost in lopsided games.** Split by deaths to r1000 (ours minus theirs; `tools/replay/massgames.py`): fewer deaths than the rivals in 60 games, 43 wins, margin +245 per game; 0-2 more in 34 games, 14 wins, -170; 3-5 more in 16 games, 2 wins, -455; 6-9 more in 20 games, 1 win, -532; 10 or more in 20 games, no win, -671. The 40 games with 6+ more deaths hold 107% of the total deficit (-149 per game). They are spread over opponents and maps (b11p and b12p: every team has one or two), e.g. 00crater 16-2, 00swirl 25-4, 00oasis 14-1, 02guardians 12-1, 00dunes 13-3. In 00crater 15 of our 16 deaths are while fleeing from three or four enemies (a 4-stack kills us at r41, r79 and r118); in 00oasis the rivals' Marcella holds 2400-3700 health from r440.
- **Prospector first does not pay for us** (pr2 on bvp, bhp, b11p, b12p, 149 games against cw1's 150): gem-cluster gems by r600 190 against 195 (b11p +20, bvp -32, bhp +5), collected by r1000 610 against 635, tributed 443 against 472, deaths 6.8 against 6.4. Every champion that finished an emblem took Prospector first. So the rivals' better farming with Prospector or Capture first (their Capture-first Vesper collects the most) likely comes from how they play, not from the emblem; Capture first for us is untested.
- **02the_pack** (one altar in the middle, 3-pick): nobody tributes before r1298 in the b11p game; we bank 273 against 796 at r1419. In ranked games we lost it 352-1000 at r1784 and 0-533 at r2000.

## Massacres and the damage gap: postmortem (cw1 on bvp, bhp, b11p, b12p, 150 games, to r1000, 2026-10-27)

Full tables and method in `results/analysis/postmortem_2026-10-27.md`; readers `tools/replay/deathfactors.py`, `packresp.py`, `contact.py`, `damage.py`, `lostbag.py`, `trace.py`.

- **Captures are equal; bags and deaths are not.** 43.0 captures per game worth 571 gems against 43.5 worth 576. The gap in gems collected (635 vs 750) is gems taken from our dead (we lose 92 per game on death, they 38). On b11p + b12p 7% of our camp-hit rounds go to groups the rivals then capture (theirs 2%).
- **Massacre games (our deaths minus theirs 6+ by r1000): 40 of 150, 1 win; even games (2 or less): 94, 57 wins.** In massacres we trail by 3.5 deaths at r300 and their team gold is 2.1 times ours (705 vs 1483), 2.2 times at r600. 4-pick maps 18 of 53 games, 5-pick 21 of 86; 01concentrated_wealth and 00gemfight 6 of 12 each, 02stalactites and 00stampede 4 of 11.
- **Massacre deaths against even-game deaths:** 3+ enemies within 6 during the fatal contact 68% vs 54% (by r300 78%, 4+ in 53%); a teammate died within 8 tiles and 60 rounds before 43% vs 20%; walking out from home before the contact 35% vs 25%; own half 49% vs 39%; 80%+ health when the contact started 73% vs 61%; one of the killers seen 11-30 rounds before 75%; last bot activity flee 65%, stunned 11%. Traces (00stampede): all five enemies shadow a full-health champion at 4-6 tiles for 10-20 rounds while it walks on or holds; a stun, then death 4-6 rounds after the first hit. A pack of individually weak enemies makes no danger tiles.
- **Pack sightings carry the whole death gap.** 3+ enemies within 8 outnumbering us (`packresp.py`): 19.4 per game with death within 15 rounds in 15.3%, theirs 15.0 and 9.5%; 2.97 against 1.42 deaths per game, a difference of 1.55 = the total gap. We die more for every response (fought 0.293 vs 0.178, closed in 0.221 vs 0.146, left 0.033 vs 0.018); with their response mix our rate would be 15.1%.
- **Contacts by numbers** (`contact.py`): at +1 and 80%+ health we die as rarely as they do (0.046 vs 0.043 within 15 rounds) but kill 43% less (0.176 vs 0.308; hit share 0.19 vs 0.28); at even numbers and 80%+ we die 0.081 vs 0.049, at -1 0.168 vs 0.056.
- **Carriers are not careful** (`lostbag.py`): deaths per 1000 alive rounds with 0 / 1-19 / 20-49 / 50-99 / 100+ gems us 1.78 / 1.63 / 1.54 / 1.74 / 2.38, them 1.43 / 0.96 / 0.84 / 0.88 / 0.33, with equal rounds spent carrying.
- **Damage** (`damage.py`, per champion-game): about 13.1k per game against 17.1k. Vesper 3050 vs 4907: hit share in contact 0.29 vs 0.43 (moves with an enemy in reach in 23% of contact rounds vs 16%, idle with one in reach 8% vs 4%), strength shards while hitting 9.0 vs 14.6. Marcella 4024 vs 5228: 25.7 contact rounds vs 36.8, outnumbered in 36% of them vs 16%. Vendetta 2661 vs 3028 (hit share 0.60 vs 0.68), Heart of Ruin equal. Our Varg 1496 against their fifth picks 2.0-6.1k. Damage on champions that die within 10 rounds: ours 22-24%, theirs 31-36%.
- **Joining** (`decoded.py assist`): with the numbers on our side and a teammate hit, they join 10.0 times per game, we 4.8 (enemies dead within 10 rounds after a join 0.53 vs 0.32); with the enemy 3-4 tiles away we hit 17% (30%), stand 26.5% (18.5%), hit camps 8.3% (3.8%). The fight simulation (3 rounds, enemy first) calls a fight won only on more enemy deaths or a 0.2 health-fraction margin; locally (probe np0) it said "not winning" in 21% of rounds where we outnumbered at 80%+ health. ja1 tests a fix.
- **Joining when ahead does not convert (ja1, 146 games on the same four panels):** counting a fight as won when we outnumber, match their power and stand at 70%+ health raised our hit share in contacts at +1 from 0.18 to 0.22, but P(an enemy dies within 15 rounds) fell from 0.171 to 0.143, our deaths rose to 6.6 and gems collected and tributed fell 9%. More hits at +1 do not make kills: the rivals' kill rate at +1 (0.30) comes from something other than hitting more often.
- **Chain deaths** (`tools/replay/chain.py`, cw1 four panels): a champion dying within 60 rounds of a teammate's death within 8 tiles of the spot: ours 2.16 per game (34% of our deaths), theirs 1.16 (24%). The difference (1.0) is two thirds of the death gap. At the first death our later victim was 11+ tiles from the spot in 19% of cases (theirs 7%) and walked 3+ tiles closer before its own first hit in 27% (19%); 2.7 enemies stood within 6 of the spot (1.8).
- **Why Vesper misses shots** (probe vp0l, 40 local games): with an enemy within 3 at turn start she shoots in 69% of turns (87% at 80%+ health). The no-shot turns are `flee` after a hit or under half health (11.7 per game, never a shot: a fleeing ranged champion does not shoot), flee dashes (3.4, no shot first although the dash still lands after a ranged attack) and `pvp` steps towards a prey 4 tiles away (1.3). The decoded in-range hit share of the same games is 0.52, not 0.69: a share from round-start positions also counts rounds where the enemy stepped out of reach before her turn. vd1 (shoot before a safe flee dash, shoot in reach instead of stepping to a prey at 4) raised it locally to 0.59 and her champion damage from 4641 to 5648 per game.
- **Focus fire is equal; fighting together is not** (`tools/replay/focus.py`, cw1 four panels): in rounds where two or more champions of a side hit enemy champions, all hits go to one target in 75% of ours and 76% of theirs, and with two or more enemies in reach a hit goes to the lowest-health one in 73% vs 72%. But they have 29.0 such rounds per game, we 14.3, and the champions we hit die within 10 rounds 20.7% of the time, theirs 29.3%. ja1 raised our multi-hitter rounds to 18.6 while the share dying fell to 18.7%.
- **Hurt champions and their chasers** (`tools/replay/escape.py`, cw1 four panels): a champion under half health with an enemy within 4 (after 10 rounds without): ours 16.1 times per game, dying within 15 rounds in 34% (theirs 12.3 and 26%), with 2.2 enemies and 0.9 allies within 6 (1.8 and 1.2) and hit again within 3 rounds in 70% (59%); both step away from the nearest enemy in 43-44% of first rounds. Our champions within 2-4 tiles of a hurt enemy hit it within 3 rounds in 36% of cases when carrying under 30 gems (theirs 48%): Vendetta 0.24 vs 0.40, Marcella 0.24 vs 0.34, Vesper 0.52 vs 0.62; their ranged picks finish best (Tavi 0.62, Prism 0.64, Cassi 0.65). Those that do not hit act alike on both sides (about 31% move away, 31% move sideways, 13-16% stand); the difference is the numbers: their chasers outnumber the enemy within 6 in 63-67% of cases, ours in 37-40%.
- **Draft by team size** (cw1 four panels): we win 4 of 11 on 3-pick maps, 22 of 53 on 4-pick, 34 of 86 on 5-pick. Commonest rival teams: 4-pick Heart of Ruin, Marcella, Ryth, Vesper (17 of 53) and Heart, Marcella, Vendetta, Vesper (10); 5-pick Heart, Marcella, Ryth, Vendetta, Vesper (32 of 86), then with Willow for Ryth (15).
- **Platform quota**: 50 match groups per hour, in windows starting at :22 IST (07:52Z). A four-panel judgement (b11p, b12p, bvp, bhp) uses 30 groups, so at most one and a half such tests fit an hour; a gate that runs out waits in `gate.sh`'s retry loop without printing (its output reaches the chain log only through `tail -3`).
- **Vesper shooting more costs the team (vfs1, all four panels):** shooting before a safe flee dash and in reach instead of stepping to a prey raised her in-range hit share 0.42 to 0.46 and her champion damage 11%, with her own deaths +3%; but team deaths rose 0.34 per game, gems collected fell to 95% and tributed to 93% of cw1, and Heart of Ruin (1.95 vs 1.84) and Vendetta (1.79 vs 1.60) died more. The third such variant after vh1m and vs1.
- **Tavi as the fifth pick (ta1, all four panels, 149 games):** her champion damage per game 1922 against Varg's 1498, below the rivals' Tavi (6121 on three panels), because she hits in 38% of her in-range rounds (theirs 58%); she died 1.55 times per game and team deaths rose 6.36 to 6.8. Our ranged play, not the pick, limits a ranged fifth pick (Vesper 0.43 against 0.60).
- **Holding back when outnumbered (ou1, b11p + b12p, 50 games):** with no step or dash in and no champion ability when more enemies than allies stood near, our deaths by r1000 rose 5.5 to 6.5 and our kills fell 4.4 to 3.2 (whole games: their deaths 192 against cw1's 285). Kills in outnumbered spots come from the spells and stuns cast there.
- **Melee step-ins** (`tools/replay/closein.py`, cw1 four panels, to r1000): the rivals step next to an enemy more often (Heart of Ruin 12.4 per game against 8.6, Marcella 6.7 against 3.1, Vendetta 7.6 against 5.7), mostly when ahead in numbers (59-63% of their step-ins, ours 44-47%). Ours die within 10 rounds after 9.5-14% of step-ins (theirs 3-7%); Marcella's at even numbers 16% against 3%.
- **Packs below the danger filter** (`tools/replay/dgap.py`, cw1 four panels, bursts from type and items held): an enemy makes danger tiles only when its own burst reaches 30% of our current health, which no champion reaches against a healthy ally at base stats. In our rounds with 2+ enemies within 8 at 80%+ health no single enemy passed in 55% (rivals' rounds 51%), and there our champions died within 10 rounds with P 0.016 against the rivals' 0.004 in the same spot (3+ enemies: 0.028 against 0.007); where an enemy passed, 0.058 against 0.037. pb1 counts the pack's summed burst.
- **Flee steps** (`tools/replay/fleeinto.py`, cw1 four panels): under half health with an enemy within 3, our champions move in 48.3 rounds per game (rivals 39.8). 63% of our steps gain distance from the nearest enemy (71%), 22% leave it level (12%), 7% close it (8%), 9% come within 2 of another enemy (9%); a death within 10 rounds follows 40% of our level steps (28%) and 27% of the steps away (25%). The flee walk follows the home field and ignored chasers; fw2 takes the step down that gains distance.
- **Health at contact start is not the gap** (scratch `conthp.py`, cw1 four panels): contacts (an enemy within 6 after 10 rounds without) 36.5 per game against 38.9; 79% of ours start at 80%+ health (81%), 5% under half (5%). At 80%+ we die within 15 rounds in 4.5% (2.7%).
- **Fuel is no longer a factor:** deaths after our own turn ran out of fuel were 0.00 per game on cw1's four panels (0.45-1.12 on 10-25 before fz1).
- **Mechanism probes** (10-27, 40 local games each against cand1 and cp3 on 10 maps, a print-only copy of the variant against the same print on a copy of main; `tools/local/probe_lines.py`): all four changes do what they were written to do. pb1 (`multi-154132` against `multi-154027`): in turns where only the summed pack makes danger (2+ enemies within 8, none passing alone), our champions end inside the pack's reach in 48% of turns (main 59%), leave it in 10% (3%) and enter it in 6% (8%; pb1's entries are nearly all fights); farming inside the reach falls from about 45% of those turns to about 10%. fw2 (`multi-154815`): `flee_step` makes 59% of flee walks, and each one is farther from the nearest enemy and downhill; on those turns the plain home step was level 20% of the time. The other flee walks (`walk_home` 25%, bush 12%, none 5%) come on turns with no downhill step away, and `walk_home` is level there 57% and closer 13%. hw1 (`multi-154841` against `multi-154949`): on our half, 17% of the turns with an enemy within 3 have 3+ enemies within 6; hw1 sends no call in exactly those turns (main calls in all), and helper walk turns fall from 85 to 76 per game. mr1 (`multi-154914` against `multi-154949`): in threat-branch turns with her rooting spell ready, Marcella casts it at the top in 0% (main 66%) and walks in 80% (main 28%).

## Team fights: we fight beside a hit teammate less, not worse at focus (cw1 on bvp, bhp, b11p, b12p, 150 games, to r1000, 2026-10-27 evening)

Readers: `tools/replay/teamfight.py` (multi-hitter rounds, what follows a hit) and scratch scripts for the rest (`hpstate`, `lowconv`, `react`, `fightflee`, kept in the session scratchpad).

- **Death risk by health level** (champion-rounds off spawn with an enemy champion within 8; P(death within 10 rounds)): 80%+ health 0.020 for us against the rivals' 0.013; 50-80% 0.057 vs 0.039; 30-50% 0.110 vs 0.086; under 30% 0.270 vs 0.231. Before r300, when items are still small, the ratio is the same or larger (80%+ 0.024 vs 0.013, 50-80% 0.062 vs 0.041), so the item gap does not explain the fight gap. Before r300 we spend 70 rounds per game under 30% health away from spawn against their 39, 41 of them with no enemy near (their 19), and at 30-50% health with no enemy near we hit camps in 41% of rounds (35%).
- **Going low and dying low:** our champions fall below 30% health with an enemy within 6 9.7 times per game and die within 15 rounds 51% of the time; theirs 7.0 times and 44%. After such a fall the other side hits the low champion in 38% of the next five rounds when it is ours and 26% when it is theirs.
- **Focus and spells are not the gap.** In rounds with two or more hitters, all of them hit one target 75% of the time for us and 77% for the rivals (1.25 vs 1.24 targets). Casts per game by champion type match (Marcella on champions 10.8 vs 13.0, on camps 27.7 vs 24.1; Heart of Ruin dashes 74 vs 78); the rivals' 24 casts on champions per game against our 10 come from their spell champions (Prism 27, Cassi 17, Tavi 14).
- **Participation is the gap.** Rounds per game with a champion hit: us 101, rivals 128; with two or more of the side hitting: 14.3 vs 29.0. After one of a side is hit at 40-80% health with that side not outnumbered within 6 (13.5 events per game for either side), the hit champion fights back in 40% of cases (rivals 50%), runs in 22% (19%); its allies within 6 hit a champion in 15.8% of their next five rounds (23.6%) and hit only camps in 9.7% (7.6%). When it fights back, its allies hit in 23% of their rounds (30%) and an enemy within 6 dies within 15 rounds 23% of the time (34%); when it runs, its allies hit in 10% (17%) and an enemy dies 4.5% of the time (15%): their teammates keep the fight going after one steps back, ours stop.
- **Fight starts at even or better numbers** (first champion hit after 15 quiet rounds within 10 tiles, the target at 80%+ health and its side not outnumbered within 6): when we are hit first we lose the first champion within 20 rounds 20% of the time and kill first 12%; when they are hit first, 11% and 22%. When both the target and an ally fight back, we lose first 41% (kill 17%) and they 13% (kill 42%).
- **Fight view** (02stalactites, cw1_bvp, r12-r29): their Heart of Ruin, Tavi, Willow and Marcella against our Heart of Ruin, Vesper, Marcella and Vendetta, all packed. They hit our Vendetta with four champions and stunned her three rounds in a row (Heart of Ruin's dash, Marcella's stunning attack, Tavi's spell); she died at r19 without acting from r16. Our Heart of Ruin walked to a camp 4-5 tiles away and hit it from r16 to r19; our Marcella cast once and walked about; our Vesper hit their Heart of Ruin every round, and Willow healed it twice (77% to 100%, 57% to 94%). In code terms the bystanders were in the neutral zone: the 3-round simulation did not say `winning` (it needs more enemy deaths or a 0.2 health-fraction margin) and they were not `losing`, so they hit only what was in reach and went back to the plan.
- **Healers:** a rival Willow heals 41.8 times per game (to r1000), about 213 net health per heal, 8,900 per game. Against the 50 games with a rival Willow we die 8.1 times per game (5.5 against the rest) and win 34%. Their Willow, Tavi and Prism stand within 4 of an ally in 72-81% of their rounds off spawn (their other champions about 50%, ours 44-47%).
- **Deaths per game by champion type, ours against theirs:** Heart of Ruin 1.84 vs 1.19, Vendetta 1.60 vs 0.73, Vesper 1.26 vs 0.64, Marcella 1.18 vs 0.65 (our Varg 0.99).
- **Rival teams:** we win 1 of 10 against the 4-pick team Heart of Ruin, Marcella, Vendetta, Vesper (our own 4-pick team), 4 of 15 against Heart of Ruin, Marcella, Vendetta, Vesper, Willow, and 16 of 32 against Heart of Ruin, Marcella, Ryth, Vendetta, Vesper. Losing the mirror points at play, not the draft.
- **Top 15 ladder teams' drafts** (their last 30 ranked games each, engine 2.0.0, 10-27 17:30 IST): 5-pick teams field Marcella 95%, Heart of Ruin 90%, Vendetta 84%, Vesper 83%, Ryth 63%, Willow 23%, Tavi 20%, Prism 15%, Varg 14%; their commonest 5-pick team is Heart of Ruin, Marcella, Ryth, Vendetta, Vesper (5 of the 15 teams). Teams with Willow won 45% of those games, without 54%.
- **Measurement noise, paired:** on the pinned panels a variant's per-game paired difference in our deaths has a standard deviation of about 3-4 (dm1, b11p, b12p, bhp, bvp rows), against 7.4 for unpaired runs: base and variant games on the same opponent and map correlate at about 0.7-0.85. Over 150 paired games the standard error of a deaths change is therefore about 0.3 per game.

## Stuns carry the death gap; fights start at full health (cw1 on bvp, bhp, b11p, b12p, 150 games, to r1000, 2026-10-27 evening)

Reader: `tools/replay/stuns.py` (stun sources and windows in its header). Scratch readers for the rest (`lowfound`, `champdeath`, `cdready`, in the session scratchpad).

- **Deaths do not start low.** Walking back from each death while an enemy champion stays within 8, the victim's health when that contact began: under 40% 0.19 per game for us against the rivals' 0.22, 40-60% 0.41 vs 0.35, 60-80% 0.71 vs 0.59, 80%+ 4.85 vs 3.18 (after 30 quiet rounds 1.95 vs 1.09). The whole gap is in contacts that begin at high health. At the death our victims have 2.45 enemies within 6 against the rivals' victims' 1.8 (Heart of Ruin 2.43 vs 2.06, Vendetta 2.53 vs 1.70, Vesper 2.46 vs 1.57, Marcella 2.43 vs 1.85), about one more enemy than ten rounds before (theirs about 0.4 more).
- **Stuns:** the rivals land 21.0 stuns on our champions per game, we 9.5 on theirs. Ours are Heart of Ruin 7.0 per game (theirs 6.4) and Marcella 2.7 (4.5); theirs add Ryth 11.5 per game it plays (68 games), Tavi 11.0 (38), Prism 12.7 (18) and Cassi 7.3 (31). Of our deaths 49% (3.12 per game) have a stun on the victim in its last 6 rounds, of theirs 32% (1.54); deaths without one are 3.24 against 3.28. The death gap is the stunned deaths.
- **Conversion per stun is equal.** P(the stunned champion dies within 6 rounds) by enemies within 3 of it: none 0.13 (our targets 0.09), one 0.17 vs 0.13, two 0.30 vs 0.27, three 0.58 vs 0.54, four 0.77 vs 0.50. Our stunned champions have no teammate within 3 in 61% of stuns (theirs 49%). So the gap is the number of stuns, which follows the rivals' drafts.
- **By game group** (deaths per game, stunned in brackets): 5-pick games against a rival extra stunner (Ryth, Tavi, Prism, Cassi or Ren; 71 games) us 6.23 (3.32), them 4.70 (1.20): the gap is all stunned deaths, the rest is in our favour (2.91 vs 3.50). 4-pick with an extra stunner (37) 7.35 vs 7.03. Against teams with only Heart of Ruin and Marcella as stunners, i.e. the mirror team Heart of Ruin, Marcella, Vendetta, Vesper with or without Willow (31 games, we won 5): 4-pick 8.81 (2.94) vs 3.69 (1.56), 5-pick 4.73 (1.27) vs 2.47 (0.87); there the gap is mostly deaths without stuns.
- **Our own extra stunner does not convert.** In ry1 (Ryth for Varg on 5-pick maps, b11p + b12p) our Ryth landed 7.5 stuns per game (the rivals' Ryth 10.3), our stuns rose from 9.3 to 13.3 per game, but only 13% of our stunned targets died within 6 rounds (cw1 17%, the rivals 20%) and our deaths did not change (paired +0.0).
- **Cooldown use is the same.** Casts per game by slot, ours against theirs: Marcella's stun reset 23.7 vs 24.4 (an enemy within 6 at the cast 22% vs 32%, the next attack on a champion 15% vs 22%); Heart of Ruin's dash 72.4 vs 76.9 (enemy within 6 23% vs 22%, landing next to a champion 11% vs 9%), shield 42.6 vs 35.9; Vendetta's reset 49.7 vs 49.2, dash 65.6 vs 70.7; Vesper's reset 37.1 vs 36.8, dash 57.7 vs 59.6. Both sides spend most resets on camps.
- **Fighting together did not help (tj1).** Committing teammates to an enemy in contact raised our multi-hitter rounds from 14.3 to 17.8 per game and the rivals' hit rounds as much as ours: more fighting without a better exchange, as fb3 and ja1 before.

## cw1's base on b11p and b12p is a lucky draw (all bots decoded on the four pinned panels, 2026-10-27 evening)

Reader: `tools/replay/baserank.py`. Games on a pinned panel are deterministic and our bot draws no random numbers, so a base run is one fixed draw, and every variant judged against it shares that draw's luck.

- Against its 12 children run on the same panels (pa1, pr2, ja1, vd1, ta1, tj1, fw2, pb1, ou1, dm1, ha1, rv2), cw1 ranks first of 13 in wins on b11p (12 of 25 against a mean of 8.0, +1.8 sd) and on b12p (9 against 6.75, +2.6 sd); in our deaths second (5.72 against 6.56) and first (5.36 against 6.10); in tributed second (568 against 517) and first (594 against 536). On bvp and bhp it sits in the middle: wins 7th and 3rd of 13, our deaths 11th and 5th. The children are not worse than cw1 where its draw is ordinary, so the b11p and b12p runs are luck, not strength.
- Pooled over the four panels (150 games) the base is better than a typical child by 0.25 of our deaths per game, 0.27 of their deaths (0.52 in the death exchange), 21 gems collected (3.4%), 22 tributed (4.6%) and 7 wins. Most of today's guards were smaller than that (our deaths +0.2 or +0.3, tributed 97% or 98%), so a neutral change failed them on b11p and b12p alone.
- Variants rejected today by margins inside that bias: dm1 (death marks) met its bars on bvp + bhp and failed only on b11p + b12p (deaths +0.75 there; -0.25 over the four panels); fw2 (flee step) missed its deaths target at 6.31 against 6.36 with the bar a fall of 0.3; rv2 (carrier reserve) fell to 96.6% tributed against a 98% guard, with every carrier metric worse on b11p and b12p only. Over the four panels rv2, dm1 and fw2 have our fewest deaths of all cw1 children (6.25, 6.23, 6.31; cw1 6.36).
- Null variants (`nl1`, `nl2`: the direction order in `move.h` permuted, so tie-breaks change and nothing else) measure cw1's own level on b11p and b12p. Method from here: run `baserank.py` before writing guards, and judge against the mean of the base and its nulls where the base is an outlier.

## Audit of cw1, gifted clears and 00ribs (cw1 on the fresh pinned panel b13p, ranked blowouts, 2026-10-27 night)

Readers: `tools/replay/gift.py` (camp hits by who captured that group life, per map) and `tools/replay/giftstay.py` (contested group deaths: capture outcome by how many of ours stayed on the group). Ranked blowouts decoded in `data/fights/q_blow`.

- **No cheap bug wins left in the code.** The check build au18 (cw1 with `tools/local/audit_layer.patch`; four hunks of `move.h` notes did not apply and were left out) played all 70 maps on both sides against dr3 (140 games, `data/runs/multi-205212`): 0 caught engine errors and 6 turns ending with an attack unused and a target in reach in 738k champion turns. Stuck walks are almost all deliberate danger avoidance (`stuck_danger` 1.2k). 13% of all turns are respawn waits (`resp_wait`). On the platform cw1 had no bot faults on b13p and 3.6 fuel run-outs per game, 80% of them in rounds 1-3.
- **Ranked blowouts are repeat deaths.** In 7 ranked losses of 10-27 where we died 21-43 times (00ribs, 02arena, 01gold_rush, 00oasis, 00road_of_riches; `massacre.py --min 10`) we died 25.6 times per game against 3.0, 77% within 6 tiles and 150 rounds of an earlier death of ours (other games 49%), mostly full-health champions alone against two to four enemies, and most of the deaths come after r750. On 01gold_rush the late victims die near our own spawn to one or two hits: the enemy items are far ahead by then.
- **Shared altars are not the map feature.** Every one of the blowout maps has only altars that are as far from the enemy spawn as from ours (contest 20/20, ribs 66/66, crater 27/27, oasis 15/15, anvil 14/14, guardians 23/23), but over the six cw1 panels we win 40% of games on such maps and 44% on maps with an altar nearer us (scratch `claude_altar.py`, walk distances on the `data/mp1/grids`): no lever there.
- **Gifted clears** (`gift.py`, cw1_b13p, to r1000): 7.1% of our camp hits go to group lives the enemy then captures, theirs 4.1%. They concentrate on our worst maps: 00ribs 64%, 00crater 43%, 01elk_arena 39%, 00quarry 32%, 00fragment 25%, 00swirl, 01concentrated_wealth and 01yellow_brick_road about 20%.
- **Contested captures** (`giftstay.py`, cw1_b13p: groups we hit most, an enemy within 8 and one of ours within 3 at the group's death, 468 group deaths in 50 games): with none of ours on the group 4 rounds later we capture 43% (94 cases), with one 88% (327), with two 92.5% (40). In the 94 cases our champions near the group were at 50%+ health 91% of the time and died within 4 rounds 3%; 51% stood 2-3 tiles off the group and 46% walked 4+ away. Traces show most of them fighting enemies 1-4 tiles away while the group died (no capture is possible while an enemy stands on the region), and some healthy champions walking off with the enemy 5-8 tiles away.
- **00ribs** (cw1_b13p, 128-1029 at r1156, only 10 deaths): all gems sit in one group of two elks and clusters at the bottom, 66 steps from both spawns, beside both altars. Our five champions walk there at the start (r60), fall to 150-500 health against the elks, walk home to heal and come back, about 130 steps a round trip (bottom at r60, r160, r260, r380): 0 gems collected by r300 and 57 by r600 against the rivals' 200 and 600. The rivals farm gold clusters beside their own spawn first (20-26 gold each by r30) and capture what we cleared (43 tributed by r120).

## Bad maps and 00ribs: how the hill is lost (bmp base, ranked games, 2026-10-27 late night)

Readers: `tools/replay/midwake.py` (strong-camp wakes by zone and support), `tools/replay/ribshill.py` (how 00ribs hill deaths begin); scratch `ribsopen.py`, `hilltrace.py`, `presence.py` (hill budget). Decoded: `data/fights/cw1_bmp_bmp` (bmp base, 50 games against the ten b11p/b12p teams), `data/fights/rk_ribs` (our ten ranked 00ribs games of 10-26/27 against teams ranked about 40-75, all lost).

- **Per map on bmp, to r1000, us against them:** 00ribs collected 90 vs 738, deaths 14.9 vs 2.6 (0 of 10 won); 00contest deaths 23.0 vs 5.2 (0 of 10); 00crater collected 335 vs 934, deaths 14.8 vs 3.6 (1 of 10); 01elk_arena collected 249 vs 520, deaths equal (4 of 10); 02guardians collected 605 vs 889 and tributed 4 vs 183 by r1000, but 377 vs 391 by r2000: a late-banking map, not a banking failure (3 of 10; ranked 7 of 12).
- **Middle strong-camp wakes (bmp):** our middle wakes are taken by the enemy 44% of the time, theirs 12%, at every support level (woken alone 47% vs 12%, with three or more of us 32% vs 12%); they wake middle camps with three or more 4.76 times per game, we 2.22. Second wakes (another middle camp of ours already under way) are equal, 0.70 vs 0.72 per game, so cg2 aimed at no gap.
- **Ranked per map** (600 games from 10-26 22:10 UTC, 51% won): 00ribs 0/10, 01boss_battle 0/5, adgato_gemcombat1 0/5, 00packs 1/9, 00eight 1/8, 00contest 3/15, 02gift_wrapping 2/10, 01yellow_brick_road 2/10, adgato_gemcombat5 3/14, 00interlock 2/8, 00crater 3/12, 01corridors 4/13: the twelve worst maps 23 of 125 (18%). Raising them to 40% is about +30 rating.
- **00ribs is the same against everyone.** Ranked (teams near our rating) and bmp (teams above us) give the same budget: champions on the hill 1.12 / 1.17 for us against 2.82 / 2.94; dead 1.04 / 0.93 against 0.15 / 0.16; deaths by r1000 16.6 / 14.9 against 2.4 / 2.6; heal trips 12.8 / 16.1 per game leaving the hill at 35% health against 29.0 / 26.3 at 49-51%, mostly by recall (their walking-up time is 0.21 champions, ours 0.34; `go_home` recalls only with no enemy within 5 and no unexplained hit in the last 3 rounds).
- **Hill deaths** (both sources, 20 games): 113-117 of our 149-166 deaths per 10 games are on the hill, a median 30-33 rounds after entering, with 2.84-2.96 enemies and 0.75 allies within 6 at death (the rivals' hill deaths 1.15-1.46 and 0.92-1.08); 10 rounds before death our victim was at 78-79% health. At the first contact after entering (`ribshill.py`, 230 of our deaths) 81% were still walking in, 61% already had two or more enemies within 8 (their deaths 31%), the victim hit first in 46% (theirs 58%), moved closer in the next 3 rounds in 71%, and died a median 21 rounds later (theirs 36).
- **The opening loses the hill before any fight.** In all 20 games our five champions reach the hill by r44-r57. Where the enemy comes later (half the games, r66-r110), our champions split over the groups: in eddef4ab our Vesper tanked elk A alone from 100% to 28% in 12 rounds (r52-64) while two teammates farmed the middle gem group beside it, the Heart of Ruin took elk B's hits there (100% to 28%, r62-74), the Vendetta stood idle at full health beside elk A's respawning group for 16 rounds and then recalled home, and by r100 the hill was empty or held by one of us at 31-64% when their five arrived at full health. Where both arrive together (r43-59), their five wait as a pack at the edge of the hill without touching a camp (1a7e013f: four of them idle at full health 4-6 tiles north of elk A, r52-64) while we tank the elks, then strike our weakest and our late arrivals (r66-80: three of ours dead or fleeing). Our hill count falls from 5 at r60 to 0-3 at r90 and 0-1 at r120 in most games.
- **Mid-game trace** (bda9c08a, r560-700): three of ours arrive within 10 rounds at full health, split again (one tanks a camp to 28%, one hits another camp, one captures), and the one left opens a lone 1v1 at the corridor mouth (the "first strike in a lone 1v1" rule) and dies when two more enemies arrive; the capturer stood idle 6 tiles away during that death and later died the same way.

## 00ribs opening, meetings and tank assist (cw1 on the bad-maps panel brk, 2026-10-28 night)

Panel `brk` (ten teams of ladder ranks 40-58, 20 games per map; base `main_brk@brk`, 26 of 100, decoded in `data/fights/main_brk_brk`). Readers: `tools/replay/ribsopen.py`, `ribsbudget.py`, `meetings.py`, `tankalone.py`.

- **Per map, to r1000, us against them:** 00ribs 2 of 20 won, collected 147 vs 774, deaths 13.6 vs 2.7; 00contest 5 of 20, collected 53 vs 379, tributed 21 vs 316, deaths 15.1 vs 7.7; 00crater 3 of 20, collected 380 vs 901, deaths 11.4 vs 6.5; 00eight 7 of 20, collected 702 vs 948, lost on death 139 vs 36, deaths 9.8 vs 5.1; 00packs 9 of 20, collected 614 vs 656, deaths 4.0 vs 3.8 (level).
- **00ribs budget** (r60-1000, champions on average, us vs them): dead 0.85 vs 0.17, on the hill 1.40 vs 2.58, walking down 1.56 vs 1.61, walking up 0.29 vs 0.23, home 0.30 vs 0.32, other 0.53 vs 0.22; heal trips 16.2 vs 27.9 per game, leaving the hill at 34% vs 54% health. Both sides walk down about 30 times per game; 13.6 of our trips follow a death, 2.7 of theirs.
- **The opening is lost in every game.** In all 20 games our five reach the hill at r44-r61, before or with the enemy; our first death comes at r58-r101, theirs before r200 in only 6 games. Our hill count is 4-5 at r60, 0-4 at r90 and 0-2 at r120, even when their five arrive late (r77-r87 in two games: 5 vs 0 at r60, 3 vs 5 at r90, 1 vs 5 at r120). Trace a41ac01d (we are team 0): our first arrival wakes elk 2 alone at r52 and tanks it from 100% to 28% by r64 (60 damage a round) while a teammate 1-5 tiles away hits clusters; another wakes elk 1 alone at r64 and falls from 88% to 28% by r76; elk 2 dies at r76 once three hit it, elk 1 is still at 624 at r104 with one or two hitters; by r108 three of ours have recalled home and two are dead, and the enemy kills elk 1 and takes the group. Focus sets the cost: with k of us on an elk (about 85 damage each a round) it costs about 1650/k health, so one hitter per elk costs about 3300 for both elks and five about 660.
- **Meetings at camps** (`meetings.py`): on the 00ribs hill, when one of ours hits a camp with one enemy within 6, our farmer dies within 20 rounds in 22% of the episodes and the watcher in 6%; when one of theirs farms with one of ours within 6, their farmer dies in 2% and our watcher in 23%. Over all 99 games: 7% and 6% when we farm, 2% and 14% when they farm. The first three rounds look alike on both sides (the farmer keeps farming in 56-65%, hits the watcher in 11-18%, is hit by it in 9-14%); the farmer has an ally within 6 in 74-79% for us and 85-88% for them. Whoever farms, the champion who dies is ours.
- **Camp hits under watch** (00ribs, the same games): with no enemy within 6 our camp hitters die within 20 rounds 6.1% of the time, theirs 1.2%; with one enemy within 6 24.6% vs 1.5%; with two or more 31-48% vs 2-6%. They hit camps for 420 champion-rounds per game, we for 253.
- **Tank assist (tk1, platform):** a champion near a strong camp that hits a teammate joins that fight. On 00ribs our solo share of strong-camp tank rounds fell from 73% to 58% (the rivals 50%), and by r1000 we collected 230 (147) and tributed 189 (123) while they collected 705 (774): paired margin +134 +- 75 per game. Deaths barely moved (12.9 vs 13.6), and 00crater (-74 +- 73) and 00eight (-57 +- 54) went slightly the other way, so the panel total was flat (`docs/experiments.md`).

## 00ribs: elk damage before contact, and waking the elks together (cr3 on brkp, 2026-10-28 night)

Base `cr3_brk@brkp` (cr3 = main since 10-28 00:50, 14 of 100; cw1 26 on the same pinned games), decoded in `data/fights/cr3_brk_brkp`. Reader: `tools/replay/elkopen.py` (strong-camp damage before the first champion hit of the game).

- **cr3 on brkp, per map to r1000, us vs them:** 00ribs 3 of 20 won, collected 173 vs 723, deaths 11.4 vs 3.8; 00contest 2 of 20, collected 40 vs 430, deaths 15.0 vs 4.8; 00crater 1 of 20, collected 329 vs 999, deaths 12.3 vs 4.3; 00eight 3 of 20, collected 611 vs 979, lost on death 123 vs 23; 00packs 5 of 20, collected 499 vs 837, deaths 5.0 vs 1.8. On 00ribs our hill count is 5.0 at r60, 4.3 at r75, 3.05 at r90 and 0.5 at r120.
- **Elk damage before contact (00ribs):** the first champion hit of the game comes at r63 on average (cw1's games r51-86). Before it our champions take 453 elk damage per game (cw1 582) and the rivals 57 (15), from 1.9 of ours (0.3 of theirs). In the cw1 games where contact came late (r86) we had already taken 2640. On the other 80 brkp games contact comes at r36, and before it we take 725 strong-camp damage per game and they 512.
- **Who wakes the middle elks (00ribs, `midwake.py`):** we wake 6.35 middle strong camps per game, 4.15 of them with fewer than three of us within 6, and the enemy takes 48% of them; they wake 10.25, 4.85 with fewer than three, and we take 6%. Our team loses 5.0 champions within 30 rounds of our middle wakes per game, theirs 1.05.
- **Converging locally (ce1-ce3, against cand1, cp3 and dh3):** redirecting the final pick to the elk a teammate already claims, and waiting within 5 tiles until four of us that claim it stand within 6, cut our middle wakes with fewer than three near from 7.0 to 0.7 per game and second wakes from 1.2 to 0 on 00ribs. Skipping the second elk inside the scoring instead (ce1) made the hill less attractive than the gold clusters near home (arrivals r45-77 instead of r45-57). Waiting at a lone middle strong group (00crater: an elk group and a golem group 22 tiles apart) let the opponents wake and take them and doubled our deaths there (ce2), so ce3 waits only where the map pairs two middle strong groups within 12 tiles.
- **Waking the elks together works, and the hill is still lost (ce3 and ce4 on brkp, platform).** ce3 cut our 00ribs middle wakes with fewer than three of us within 6 from 4.15 to 0.35 per game, the share the enemy takes from 48% to 18% and the elk damage before contact from 453 to 171 per game. Yet the hill count stayed 5.0 / 4.3 / 2.75 / 0.65 at r60 / 75 / 90 / 120 (base 0.5 at r120), deaths by r1000 fell only 11.4 to 10.6 and collected rose 173 to 205. ce4 (the capturer of the first elk joins the second instead of waiting 60 rounds at its respawn) played the opening to r130 exactly as ce3 and changed nothing measurable.
- **Where the hill goes (cr3 / ce3, r120):** of our five, 0.5 / 0.65 are on the hill (at 53% / 68% health), 2.0 / 2.1 dead, 2.1 / 1.8 walking and 0.4 / 0.45 at home; the rivals keep 1.8 / 1.5 on the hill with 0.7 dead. Health is not the gap: at r75 ours are at 72-75% and theirs at 71-75%, at r90 51-66% against 69-70%.
- **The opening fights (r60-130, ce3; scratch `whostart.py`, `allyfar.py`, `dact_ribs.py`):** we lose 2.15 champions per game and they 0.85. Our victim strikes first in 34 of 43 deaths, at 85% health with 2.07 enemies and 2.44 allies within 6; 2.35 more enemies stand 7-15 tiles away (allies 1.10). It dies 14 rounds later with 4.05 enemies and 1.81 allies within 6, and 1.12 of its teammates are already dead. Our D lines at those deaths: flee 28, stunned 11, pvp 3. The fight starts at even numbers and the rest of their stream arrives; ours does not. Trace 67bc7170 (r60-86): after our Vendetta falls at r66, their five focus one of ours at a time (all hit our Varg at r68-72, our Marcella at r74-78, our Heart of Ruin at r80-84), ours spread hits over three targets, and two of theirs at 11-14% health recall out; our Vesper at 50% health and our Heart of Ruin at 79-91% stood 5-8 tiles off while the first three of ours died.
- **Holding before an enemy-held middle group (ce5 = ce4 plus hg1's hold, only on maps with paired middle strong groups, that is 00ribs; platform):** about 208 champion-rounds of holds per game; our hill deaths whose contact had two or more enemies within 8 fell from 115 to 84 per 20 games, our deaths by r1000 by 1.1 +- 0.7 per game, and their deaths rose by 1.9 +- 1.2 (paired against `cr3_brk@brkp`, 00ribs margin +106 +- 73 per game). Collected rose only 173 to 200 and the hill count at r120 stayed 0.55. In all three variants (ce3, ce4, ce5) our r60-130 deaths stay at 2.0-2.15 per game: what loses the hill is the first fight with their stream, not the elks or walking in alone.
- **Respawn waits on 00ribs (A lines, team rounds per game to r1000):** cr3 999, ce3 910, ce4 596 (the redirect to the live partner), ce5 622; walking to a capture about 1500, dead about 550, camp fights about 210-260. Cutting 400 rounds of waiting (ce4) changed neither deaths nor collected. Idle rounds in the hill middle are not a gap: the rivals idle there 430-470 rounds per game, we 270-440.
- **Participation in the 00ribs fights (r60-130):** rounds with two or more of a side hitting champions 6.7-8.3 per game for us against 12.0-15.3 for them, all on one target 59-68% against 69-80%; after r130 17-19 against 35-41. The same participation gap as on the four general panels ("Team fights"), larger on 00ribs.

## The user's two queued games (decoded 10-28 03:20; `data/fights/task2_queued`, replays in `data/replays/platform/task2_queued`)

Scratch readers (session scratchpad): `gline.py` (timeline), `gdeaths.py` (every death with bag, numbers within 6 and killers), `camphits.py` (who hit the monoliths), and a capture listing.

- **Ranked 02guardians loss to EggsAfter11AM (5daaa999, 10-27 21:30 IST, our bot of the cw1 line, 4 champions each; ended at r1181 on gems, we tributed 0).** Nobody can tribute until a guard monolith beside the only altar dies, and the game was decided by who carried the bags when it died. By r300 we led (collected 198 against 62, gold earned 876 against 859). From r300 to r1000 we died 13 more times (15 against 3 by r1000) and lost every gem we collected (423 lost on death against their 30); 11 of the 15 deaths had exactly one enemy and no ally within 6, mostly to their Vesper or Ryth at full health, and 2 were to camps. Their kills and farming made them rich: gold earned by r1000 7094 against 1669, their Vesper at 2400 max health at r600 (ours 1400) and 3500 at r900. With 1028 gems in their bags at r1000, they hit monolith 45 (21,20) 68 times from r1014 and killed it at r1074, then tributed. We never hit either monolith. **Fix idea:** while altar guards block banking and our team carries 150+ gems (here r300-r450: 139-238), send the healthy team to kill the nearest guard monolith together (the 200+ gather rule, four of us), so the lead is banked instead of lost; the enemy needed about 60 rounds with four champions. Metric: our tributed by r1000 on 02guardians (0 here; 4 per game on bmp) and our gems lost on death there (423 here). Precedent: gk2 and gk3 tried the same on 01boss_battle and killed the guard too late (r818-r971 locally).
- **Unranked 01elk_arena loss to ha²t (cd52a466, 10-28 00:08 IST, 5 champions each; tributes 72 against 936 at the end, r1313).** All gems come from the centre group (two elks and clusters around (25,24); 72 gems per capture). They took 10 of its 11 captures by r1000 (720 gems against our 72). In the 30 rounds before each of their captures their champions within 8 of the centre rose from 2.9 to 4.5 on average while ours fell from 2.4 to 2.0: we were there first or level (r569 3 against 2, r745 3 against 1, r904 3 against 2) and lost the count when it mattered. Our 10 deaths by r1000 (theirs 5) were all near the centre with 4.1 enemies and 2.2 allies within 6 on average (their deaths 3.6 and 1.8). Gold earned by r1000 4115 against 7144. **Fix idea:** on maps whose gems all sit in one middle group (01elk_arena), rally the team at that group from about 15 rounds before its respawn (the respawn broadcast gives the round) and wake it only with four of us within 8, as ce3 does for paired elks. Metric: our champions within 8 of the centre at each capture (2.0 against their 4.5) and our share of centre captures (1 of 11).

## 00contest: who takes the monoliths (cr3 on brkp, 10-28)

Decoded `cr3_brk@brkp`, its 20 00contest games against the five brkp teams, to r1000 unless stated. The map has 32 gold clusters in 12 groups and two monoliths, at (17,31) and (32,18), each inside a walled pen that opens away from the centre. The monoliths hold the only gems on the map (200 each, back 150 rounds after their capture). Both altars are at the centre, 7-8 tiles from each monolith. Scratch scripts: `monokill.py` (each monolith death), `gdeaths.py` (each death).

- **They take the monoliths.** 46 monoliths died by r1000 in the 20 games. The rivals killed 43 and captured 43; we killed 3 and captured 2. Their kills start at r565-r1000 (2.3 per game) and take 15-50 rounds with 3-5 of their champions within 6, who end at 65-95% health; they capture within 6 rounds of the kill. We hit monoliths 21 times per game against their 253, and not at all in 15 of the 20 games.
- **When we kill one, nobody captures it.** In 179afe54 our Vesper killed (32,18) at r882 with 23 hits from 3 tiles and left at 42% health. None of ours stood on its tile, and their Ryth walked on at r903 and captured its 200 gems at r906.
- **Their tributes.** 37 tributes of 60+ gems by r1000 (200 gems on average, a channel of about 21 rounds) at the centre altars. 1.97 of their champions stood within 6 of the channeler (alone in 5 of 37). At the channel start 1.24 of ours were within 8 (any in 25 of 37); we broke none.
- **They can because they are richer.** Team gold (unspent plus 30 per shard, `decoded.py gold`): r300 1153 against 2058, r600 2313 against 4303, r1000 4159 against 7308 (0.57). By r300 they cleared 62.5 gold clusters against our 49.3, and we died 5.8 times against 1.2 (460 more kill gold for them).
- **How we die early.** Our 116 deaths before r300 had 3.25 enemies and 1.04 allies within 6; most victims were at 80-100% health 10 rounds before. In the first 60 rounds 1-3 of ours die at the centre (r33-60, around (22-26, 19-24)), arriving one or two at a time against their four or five. Fight starts by r300 (`decoded.py starts`): they start 29.2 per game and outnumber us in 61% (3.14 against 2.15 within 6 of the target); we start 15.2 and are outnumbered in 52%. To r1000 we die 8.9 times per game in fights they start, 3.55 in fights we start and 2.55 in both.
- **Captures** (`decoded.py captures`): we 62.5 per game (55.7 on our half, 1.4 in the middle with 20 gems), they 61.4 (36.0 on their half, 11.8 in the middle with 420 gems, 13.7 on our half).
- **Locally the same bot takes them.** Against pool/cand1, cp3 and dh3 on 00contest cr3 collects 567 gems per game (6 games, `data/runs/multi-031836`): our own pool does not move in packs.

Cause: the monoliths go to the side that can stand next to one for 20-50 rounds, and on this map that is settled by r300. The rivals arrive in packs, we arrive one or two at a time and die (5.8 against 1.2 by r300), they get richer (gold 1.9 times ours by r600) and kill both monoliths from r565 on. mn1 (`docs/experiments.md`) let the team pick a monolith with an honest clear model and a tie-aware retreat; locally its champions tanked down to about 440 health and died walking out of the monolith's reach.


## Why we lose: maps, fights and items (deep look, 10-28 night)

The user asked (10-28 04:05) for more time on the maps themselves and for very simple, general ideas instead of map-specific fixes. Base: cr3 on brkp + b13p (150 decoded games, to r1000 unless stated), top12 = 152 decoded ranked games of the top 12 teams on our five worst maps (`data/fights/top12`, "us" = the top team). Scratch readers in the session scratchpad: `follow.py`, `follow12.py`, `followb.py`, `race.py`, `focus5.py`, `fightact.py`, `tight.py`, `farmnear.py`, `mhp2.py`, `ourmaps.py`, `ftrace.py`, `dtrace.py`.

- **Maps (800 ranked games since engine 2.0.0, `data/tmp_ourranked.json`; map dumps of all 70 maps in `data/maps_txt/`, made by the probe `bots/probe/md1`).** We win 0-25% on 01boss_battle, adgato_gemcombat1, 00ribs, 01yellow_brick_road, 00eight, adgato_gemcombat5, 00crater, 00packs, 00interlock, 00rows, 02gift_wrapping, 02stalactites, 00contest, and 75-91% on 00pilgrimage, 01concentrated_wealth, 01islands, 00gem_fields, 01big_world, 00rushbait_v2, 02tangle, 00road_of_riches, 00ambush, 02harvest. Over the 69 maps with 5+ games the win rate rises with the walking distance between the spawns (r = +0.33) and the map area (+0.24; +0.41 over the first 40 maps) and falls with strong camps per tile (-0.37 over the first 40). The bad maps force contact: 00eight and 00crater have one altar, in the middle; 00contest's two altars and only gems (two monoliths) are in the middle; 00ribs' altars and only gem camps sit on one hill 65 steps from both spawns; 00packs is 31x31. On the normal-map panel b13p we are nearly level (collected by r1000 677 against 744, deaths 5.8 against 4.7); on brkp the gap is large (deaths 9.0 against 4.1 over both panels' 150 games).
- **Even fights go their way at every stage.** Fight starts on a healthy defender (first hit between a pair after 15 quiet rounds, defender at 50%+) with equal numbers within 6 of the defender: when we attack, the defender dies within 10 rounds in 7-8% and one of our attackers in 19-21%; when they attack, 17-20% and 7%. The same holds with equal numbers within 12 (8% / 21% against 20% / 7%) and before r150 at equal gold (31 against 34 gold a champion: 8% / 17% against 20% / 9%). At +2 we kill in 18% and lose one in 13%; they kill in 48% and lose one in 5%. The top 12 against their opponents are close to even in the same test (r<150: 14% / 16% against 16% / 21%), so our lopsidedness is unusual.
- **Being near a teammate does not save us.** A defender of ours dies within 10 rounds in 19% with an ally adjacent, 24% at 2-3 tiles, 26% at 4-6 and 30% with none within 6; theirs in 7-10% at every distance. Farming next to enemies is as common for them (camp hits with an enemy within 5-6: 49.7 rounds per game against our 35.1), but P(death within 10) is 4-5 times ours at every distance and health band (enemy within 3-4, health 70%+: 0.050 against 0.011).
- **Early fights: we hit less.** In even fights with two or more a side, over 8 rounds, before r300: when they attack they land 12.0 hits on champions and we 7.9; when we attack we land 9.1 and they 9.7. Focus is the same (72-75% of a side's hits on its most-hit target). Per champion-round our champions hit a champion 25-29% of the time against their 31-38% (Heart of Ruin 0.29 vs 0.37, Marcella 0.25 vs 0.37, Vesper 0.28 vs 0.38); the difference goes into level moves (neither closer nor away: 11-15% against 6-8%), moving away (Marcella 0.23 vs 0.17) and, for Heart of Ruin, camp hits (0.12 vs 0.06).
- **Later fights: stats.** Team gold (unspent plus 30 per shard) is 0.65-0.70 of theirs from r300 on (5-pick maps: 880 against 1358 at r300). Their camp gold by r600 is about 44% higher (per champion-game: Vesper 874 against 565, Marcella 777 against 450) and their kill gold three times ours. Bonus max health per gold held (alive champions) at r300: our Heart of Ruin 0.67 (their 1.37), Marcella 0.42 (1.14), Vendetta 1.05 (1.36); at r600 the gap narrows (1.23 / 0.95 / 1.40 against 1.45 / 1.28 / 1.43). Cause: our first emblem for the focus users is Treasure of focus (+50-70 focus, no health), and after it the shop formula counts focus as all of their damage, so Marcella buys Power of focus second (98% hold Power-focus shards at r400). Focus drives only their spells (Heart of Ruin: dash 1.5 x focus and shield every 8 turns, about a third of its damage; Marcella: a 2 x focus spell every 8 turns, about a quarter); their basic attacks use strength. In late even fights hit counts are equal (7.5 against 7.5 when we attack) but their most-hit target dies in 23% and ours in 12%.
- **Stuns (from the 10-27 finding):** the death gap is the stunned deaths; the rivals' fifth pick (Ryth, 68% of brkp games) lands 11.5 stuns per game. In ry1 our Ryth cut the rivals' hit rounds on our champions by 12.2 +- 5.4 per game; it was rejected on a tribute margin that the two panels disagreed on (-62 and +34).
- **Chasing (traces):** in a 4v1 on 00split (r583-597) their lone Heart of Ruin walked away from four of ours at 89% health; our melee walked behind it and our Vesper stepped into range each turn and so never shot. In the r37 4v4 on 00eight our Varg (100%) only moved for five rounds 2-4 tiles from the fight, our Heart of Ruin changed targets three times as each one escaped (their Vendetta at 17% then healed by Willow to 59%), and their three hit our Heart of Ruin until it died.

## Turn order: the rivals act first in contact (replays, 10-28 morning)

Within a team, champions act in `set_priority` order (higher first, from the next round; default draft order), one champion per team in turn (`docs/MECHANICS.md` section 2). We never set it: our champions always acted in draft order (Heart of Ruin, Vesper, Marcella, Vendetta, Varg). Readers: `tools/replay/orderdump.mjs` and `tools/replay/turnorder.py`; per-team rules from scratch `teamorder.py`.

- **Almost every top team reorders its turns.** In the top12 replays (152 ranked games of the top 12 on our five worst maps), 19 of 21 teams ran 50-98 distinct within-team orders per game; only print dont int and Ad Astra keep draft order. A champion under 40% health within 2 of an enemy acts first among its team (mean rank 0.09-0.25 on a 0-1 scale for Mite, hello, Claudus Maximus, Sponge, prism best girl, Trzy Kwaterki, Supaswag and NEETCoders; Intercontinental Fish 0.42). Mite and hello also put champions 6-9 tiles from an enemy last (0.65-0.68); Trzy Kwaterki and NEETCoders order by health everywhere (hurt first).
- **Against us.** On brkp (cr3, 100 games) 57 opponents reorder. For pairs of our champion and theirs within 2 tiles at a round start, their champion ended its turn first in 62.8% of pair-rounds against those 57 and in 45.5% against the 43 in draft order. When one of ours died with an enemy within 2, the nearest enemy had acted first in that round in 66% (reordering opponents) and 50% (draft order).
- **Draft by map: no.** The top 20 teams draft the same champions on our bad and good maps (ranked listings with draft picks, `data/topdrafts/top20.json`, 2,500 games): Marcella 93-97%, Heart of Ruin 87-90%, Vendetta 85-87%, Vesper 81-83%, Ryth 57-60%, then Tavi, Willow, Varg and Prism at 14-24%. Our draft differs only in the fifth pick (Varg for Ryth). Their win rates on our bad and good maps are equal (0.50 and 0.51), so the bad maps are bad for our play, not harder in general.
- **Maps by feature** (`data/map_features.json`, from the md1 dumps): our ranked win rate is 0.55 on the 31 maps with an altar on our side and 0.46 on the 38 without; by spawn walking distance it rises from 0.32-0.44 (under 30 steps) to 0.54-0.65 (70 or more).
- **Past variants on bad maps** (scratch `metamap.py`: paired results of 30 gated variants split by our ranked win rate per map): no family stands out; on the 4-16 bad-map games a variant had on the mixed panels, the two null variants nl1 and nl2 moved the tribute margin by -267 and -394 per game, so those subsets cannot judge a change. tj1 (team fight) was the most positive there (margin +167 +- 127 on 16 games, against -45 and -30 on mid and good maps).
- **Who should act first, by distance** (`tools/replay/firstpay.py`, cr3 on brkp, 100 games, rounds 1-1000). A natural experiment: within a game the order of a given pair of champions flips (the starting team swaps every round, so pairs at the same team rank alternate), and only pairs seen with both orders at a distance count. Net hits between the pair in that round (ours on them minus theirs on us, per 100 pair-rounds), ours first against theirs first: distance 1 +0.3 against -26.1 (opponents in draft order +6.5 against -36.0), 2 -2.1 against -15.0, 3 -3.6 against -11.5, then 4 -6.1 against -0.6, 5 -2.1 against +0.6, 6 -0.3 against +0.2, 7 and more equal. So act first within 3 and last at 4-6. At 4 a ranged champion that moves first cannot shoot (range 3, no move and shot in one turn) and walks into theirs: acting first we land 2.0 hits and take 8.1, acting last 6.8 and 7.4 (their casts on us 3.1 against 4.1, so the cast risk at range 4 is smaller than the shots gained). go1 (first within 5) is wrong at 4-5: in its brkp games, distance 4 gives -7.8 when ours acted first against +1.2 when theirs did. go2 (first within 3, last at 4-8) is the rule this table asks for.
- **A champion that acts last and then first moves twice in a row.** A priority set during a turn applies from the next round, so a champion that acts last at distance 4-8, steps in, and sets itself first for the next round gets two turns with no enemy turn between them whenever its team starts that next round (odd rounds for team A, even for team B).
- **Tribute channels are safe** (go1; scratch `channels.py`, the same picture as `decoded.py channels` and `breaks.py`): we die mid-channel 0.03 times per game on brkp and 0.12 on b13p (the rivals 0.00 and 0.26), and 4-7% of channels are broken by a stun or lock. Cancelling channels (`cancel_submit_gems`, never called) has nothing to win. The gap is the count: we start 9.5 tributes per game on brkp against their 20.7 (b13p 15.2 against 22.0), with equal bags (33-39 gems).
- **Who acts first by distance, in the top teams' games** (top12, scratch `teamorder.py`; mean rank within the team, 0 = first, 1 = last): nearest enemy at 1 tile 0.36, 2 0.38, 3 0.45, 4 0.48, 5 0.54, 6-8 0.56-0.58, none within 8 0.49; under 40% health 0.15 at 1 tile up to 0.31 at 4 and 0.43 at 5. They act first in contact and last at 5-8, hurt champions first.
- **The pair-level gain did not carry over to whole games (go2, rejected).** go2 acted first within 3 and last at 4-8 (the table above): on brkp ours acted first in contact 75% (go1 73%) and opened 36% of engagements (34%), but our deaths rose 0.7 +- 0.4 per game, gems collected fell to 95% and tributed to 91%. At 4-6 tiles a champion that farms near enemies ("hold") died within 5 rounds 0.0121 times per round against go1's 0.0095: acting last there gives the enemy the first step and shot.

## Early gold, strong camps tanked alone, free ranged hits (go1 on brkp and b13p, 10-28 morning)

Base: go1 on brkp (100 games) and b13p (50), decoded, to r1000 unless stated. Scratch readers in the session scratchpad: `deathact.py`, `evenfight.py`, `stepin.py`, `mtrace.py`; the rest are inline counts over `data/fights/go1_*`.

- **They are stronger by r200, and the gap starts in the first 100 rounds.** Shards per champion (an emblem counts 5) on brkp: r100 1.0 against 1.2, r200 2.9 against 4.2, r300 5.1 against 7.4, r500 10.4 against 14.8, r700 16.0 against 23.5, r1000 25.6 against 33.2; max health over base 1.13 against 1.31 at r300 and 1.65 against 2.02 at r700. On b13p we are level (r500 14.8 against 15.9, r1000 36.4 against 36.3). Team gold earned (carried plus 30 per shard) on brkp: r60 143 against 176, r100 238 against 345, r200 525 against 791, r300 842 against 1276; their kills by r100 0.92 against our 0.43, which is 49 of the 107 gold gap at r100. Per map at r100: 00crater 119 against 262, 00ribs 90 against 242, 00eight 291 against 457, 00packs 234 against 286, 00contest 456 against 480. With 40% more shards their champions have about 20% more health and damage, so a fight at equal numbers is about 1.4 to 1 against us in Lanchester power.
- **Fight starts by numbers (go1 brkp, `evenfight.py`; first hit between a pair after 15 quiet rounds on a defender at 50%+, numbers within 6 of the defender).** They start 48.9 fights per game and we 25.0. With more of them than of the defenders: they 13.4 (+1) and 11.2 (+2 or more) per game, we 4.8 and 2.2. Outcomes are worse for us in every band: at even numbers the defender dies within 10 rounds 9.8% when we attack and 15.2% when they do, an attacker dies 14.6% against 5.8%; outnumbered we start 10.1 per game (they 10.6) and lose an attacker in 26.8% (they 10.9%); at +2 we kill in 26% and they in 44%. go1 improved our side of every band against cr3 (an attacker dead at even numbers 17.9% to 14.6%, +2 kills 13% to 26%).
- **Most of our deaths come in fights we joined.** Of 9.48 deaths per game (brkp, to r1000) 6.93 follow a hit we landed on a champion in the victim's last 6 rounds (they 3.46 of 4.65); the victim took 8.7 hits in those rounds (theirs 7.1), had 62% health 6 rounds before, 2.84 enemies and 1.03 allies within 6. Deaths without a hit of our own: 0.24 fleeing, 0.41 at a camp, 1.90 other.
- **Free ranged hits.** Their ranged champions land 94.0 basic hits per game on our champions, ours 56.2 on theirs (b13p 43.1 against 36.3). Hits on a victim that was not fighting (no champion hit this or last round) and had not just walked into range: 35.1 against 14.1 per game. Our melee champions take 26.7 per game of these (theirs 11.8): in 8.1 they moved toward the shooter (and hit it within 3 rounds in 30%), in 11.8 they kept the distance (15%), in 6.8 they moved away. Their Vesper deals 7673 champion damage per game and dies 0.47 times, ours 4721 and 1.61. A Vesper's burst is under 30% of our health, so it is not in `S.danger` (`knowledge.h`), and a champion hit while it has a prey within 4 that it is not winning against falls through to its plan.
- **00crater: we tank the middle golem and elk alone.** Strong camps tanked alone (`tankalone.py`, to r300): on 00crater 58.8 solo rounds per game against their 15.1 (00eight 70.0 against 40.1, 00packs 20.7 against 2.8, 00ribs 30.9 against 24.0; all b13p maps 53.3 against 24.4). Middle wakes on 00crater (`midwake.py`, to r1000): we wake 4.45 per game with nobody else of ours within 6, take 3425 damage per such wake and kill the camp in 48% (49% taken by them); they wake 2.35 alone, take 1384 and kill 83%. Team deaths within 30 rounds of a middle wake 4.15 per game against 1.20. By r150 we capture our own two wolf groups 0.70 times per game and they theirs 2.10 (`groupkind.py`). Traces (e7e6f573, 8d7e3af3): three of ours go to the elk with three of theirs, Varg to one of our wolf groups, and Marcella walks alone to the golem at r25, tanks it from 100% to 20% by r40, recalls, and returns at r70 and r110 to do the same; nobody takes our second wolf group. Their sixth (Cassi and Issac) and Vendetta farm their own two wolf groups.
- **Cause in the code.** `pick_group` (`targets.h`) scores a group that needs heal trips with the best of three team sizes: the champions that claim it, one more, and the whole team (time x n per champion-round, plus 4 rounds of waiting per extra champion). At n = 5 an unclaimed golem scores like a nearby wolf group, so a lone champion picks it, but nothing brings the others: `planned_team` is set and never read, and the `gather` wait in `camp_fight.h` only covers groups with 200+ strength (a golem has 120, an elk 60).

## 00crater: one altar in a pocket, and the opening order (10-28 morning)

Base: go1 and cl1 on brkp (20 00crater games each), the top teams' 27 00crater games (`data/fights/top12`), decoded, unless stated. Readers: `tools/replay/firstcap.py`, `tools/replay/openpack.py`, `groupkind.py`, `midwake.py`; the layout from `data/mp1/grids/00crater.txt` and the camp list of a decoded game.

- **Layout.** One altar, at (30,3), inside a walled pocket open only to the south (rows 8-9 between x 21 and 39); every bag of ours empties on its tiles (29-31, 3-7). Just below the pocket's mouth sits the middle elk group (an elk and three gem clusters: 2760 health, 36 gems and 90 gold, 60 a round to the nearest champion within 4). Each side's top wolves (a wolf and two gem clusters: 1590 health, 18 gems and 40 gold) lie about 20 steps from its spawn and 8 from the elk; the golem group (a golem and four gem clusters: 64 gems, 160 gold) is in the south middle, and a small wolf group sits in each far corner. Both teams' routes to the altar cross the elk.
- **The top teams take their own top wolves with all five first, then the elk together.** At r20 all five of Mite stand at their top wolves; they capture them by r30 and fight at the elk from r30-40, often while the other team is tanking it (af0982a9: the opponent's Heart of Ruin at 11% on the elk at r30, dead by r40). Teammates within 6 at r15-45 (`openpack.py`): top teams 3.45, their opponents 2.53; brkp rivals 2.64, go1 1.97, cl1 2.75. First reward (median, `firstcap.py`): top teams r30, their opponents r63; on brkp go1 r90 and cl1 r56 against the rivals' r49-50. Elk captures by r300: top teams 1.74 per game, their opponents 0.96.
- **First and third rewards on brkp (go1, median):** 00ribs r108 against the rivals' r22 (third r142 against r79), 00crater r90 against r49 (third r151 against r86), 00packs r41 against r36 (third r130 against r105), 00eight r34 against r34 (third r151 against r76), 00contest r23 against r26. All brkp maps: first r41 against r34, third r133 against r74, reward events by r100 2.4 against 3.6, team gold r100 239 against 346. On b13p we are level (first r28 and r28, third r66 and r66), and the top teams are level with their opponents (r27 and r26).
- **Why we split (pick probe on cl1, local 00crater against cand1, never shipped).** At r1 all five pick our top wolves (each scores them alone: Marcella 0.53 against 0.51 for the elk). From r4, a champion that sees a teammate's claim on the wolves scores them with n = 2 (`value / (time x n)`, the per-champion rate): Marcella's wolves fall to 0.39 and the unclaimed elk wins (0.51); at r7 Heart of Ruin and Vesper see the elk claimed by one or two and the wolves by one, and follow (elk 0.35-0.43 against wolves 0.28-0.37). Only Varg stays. So the more of us head for a small group, the more leave it: the rate rule spreads the team over the nearest groups in the first rounds.
- **What cl1 changed on 00crater.** With claimant-only scoring our four reach the elk at r22-25 instead of three plus Marcella on the golem; the rivals' five arrive at r30 from their own wolves while the elk still hits us, and we lose that fight (b0d7e72a: three of ours dead by r70, none of theirs; f122d0fd: we take the elk at r60 but lose four by r140, our Heart of Ruin carrying 36 gems from r60 to its death at r130). By r300 our 00crater deaths rose from 2.25 to 3.3 per game, mostly in our own half with 3 of them and 2 of us within 6.
- **With the opening fixed (tg1 on brkp, 19 00crater games), the gap opens after r150.** Collected by r300 144 against their 167 (go1 124 against 194), by r600 291 against 411, by r1000 472 against 829. Captures r300-1000 per game: golem 0.89 against their 2.37 (57 against 151 gems), elk 2.16 against 5.37 (77 against 177), our own wolves 10.0 against their 9.05, and they take our wolves 4.05 times (we theirs 0.63); the top teams take the golem 2.78 and the elk 4.07 times in that window. Teammates within 6 per alive champion-round (`cohesion.py`): r0-150 2.26 against their 1.79, but r150-300 0.86 against 1.39, r300-600 0.80 against 1.31, r600-1000 0.72 against 1.22 (alone 43-50% against 30-34%; top teams 1.19-1.30 and 28-31%).
- **They take the middle strong camps we wake once they arrive** (scratch `steal.py`, to r1000; contact = the other team's first champion within 6 of the camp after the wake). We wake middle strong camps as often as they do (7.1 against 7.4 per game), but after contact we lose 62% of them (3.05 per game), 60% even when more of us than of them stand within 6 at contact, and 67% when the camp still has over 60% health; they lose 32% of theirs, the top teams 26%. Elks we woke: we kill 2.53, they take 2.16 per game; golems 1.21 and 0.89; of theirs we take 1.26 elks and 0.16 golems. In the camps we keep, 2.7 of us stand within 8 at contact, in those we lose 2.0 (top teams 3.0 and 2.4); in the 12 rounds after contact at a camp we lose, each of ours hits the camp 3.5 times and champions 2.9 times, 12% die and 33% walk more than 6 away (health 76% to 55%), and they finish the damaged camp 20-50 rounds later (camps never heal). Our heal rule sends any champion under half health home while an enemy was seen in the last 30 rounds (`bot.cpp`, "Heal when worn down"), so after a fight the middle empties.

## 00eight: the first centre fight (go1 and tg1 on brkp, 10-28 late morning)

- **Layout** (41x30, mirrored left-right; coordinates from the west side): the spawns are walled at mid-height on the west and east edges and open north and south; one altar in the centre (20,15) between the hole rows 13 and 17. Each side has a double elk group (2 elks, a gold and a gem cluster: 37 gems, 200 gold) at its north exit (12-13, 3-4), a triple elk group (3 elks, 2 gem clusters, a gold cluster: 59 gems, 290 gold) at its south exit (12-15, 25-27), a wolf with a gem cluster (11 gems, 40 gold) in front of the spawn (9-10, 15), and 2 wolves with 2 gold clusters (8 gems, 120 gold) at (17-18, 10-11), 4 tiles from the altar. A champion's killer takes its whole bag and 100 gold (`docs/MECHANICS.md`, sections 9 and 10), and a capture's gems go only to the champions standing on the group when it completes.
- **The gap is fights, not steals** (go1 on brkp, 20 games, to r1000): we collect 663 against their 1000, tribute 481 against 897, lose 130 gems on death against 28 and die 10.1 times against 4.4. They take our middle strong camps after contact in 2.0 of about 29 elk lives per game (33%; on 00crater 62%). 12 of the 20 games are massacres (our deaths minus theirs 6 or more), all lost, with team gold at r300 809 against 1889 (`deathfactors.py`). In those games 82% of our deaths are in our own half, 61% at 11-20 tiles from home; at the contact's start we outnumber them in 75% and stand at 80%+ health in 61%, and 43% die within 60 rounds and 8 tiles of a teammate's death. Deaths with 40-79 gems: 1.25 per game (72 gems) against 0.20 (13) (`bagdeath.py`).
- **go1's opening** (traces, mirrored): all five take the north double elk at r20-35; one champion stands on the group at the capture and gets all 37 gems; at r40 it heals at home and keeps the bag (the order-quantity batch is about 70 then: collection rate 0.28, trip 45 rounds, hazard 0.002), while three walk to the centre wolves at 23-54% health and meet the rivals there at r50-60: 3 of ours die for 1. Our third reward comes at r151 against their r76 (`firstcap.py`; reward events by r100 1.9 against 3.9, team gold at r100 292 against 458). The carrier then takes its 37 gems to the triple elk in the south for 120 rounds and more.
- **The top teams' opening** (Mite on `top12_eight`): five on the north double elk at r20-35, the gems split over two carriers (19 and 18), a heal at home on the way, the two bank at r70-80 while three hold the centre wolves, and they win the centre fight there.
- **tg1** (cl1, plus before r40 each champion scores a group as if alone) changes the order: all five take the wolf with the gem cluster in front of the spawn at r22, then both centre wolf groups, and meet the rivals at r42-54 with five at 75-100% health. On the same 20 brkp games: first reward median r22 (r34), team gold at r50 212 against the rivals' 108 (go1 226 against 195), their deaths 4.4 to 8.3 and ours 10.1 to 8.3, our collected 663 to 801, tributed 481 to 600, lost on death 130 to 96; their collected 1000 to 788. Teammates within 6 at r150-300 2.08 (go1 1.79, top teams 1.92). Gated again on the re-pinned `brkp2` as task 5's first variant (`tg1e` in `docs/experiments.md`).
- **Carriers at the centre altar** (probe bp1l on tg1, then wb1 on `brkp2`; 10-28 midday): tg1's bank stage gave up banking for 40 rounds in 34% of its evaluations of carriers with 30+ gems, 30 of 51 give-ups while the carrier closed on the altar every turn (a stale closest distance kept from an earlier walk that a fight, recall or shop trip cut off). Resetting the walk (wb1) cut our rounds with a bag of 20+ on brkp2's 00eight games by 36% (909 to 579 per game), but not the gems lost on death (100.9 per game against tg1e's 100.2 and the go1 base's 103.5): the bags still die at the altar. Traces (`tools/replay/bigbag.py`): a champion takes the triple elk group alone (59 gems), walks to the centre altar and reaches it at 60-100% health with 2-4 enemies within 6. There the threat branch runs before the bank stage, so the carrier kites out of reach and the bank walk brings it back next turn, for 3-8 turns, without starting the 6-turn channel, while the rivals' carriers tribute beside it and complete (damage does not cancel a channel). A Vesper with 70 gems at full health first spent 5 turns breaking an enemy altar lock. Our channels started with an enemy within 4 complete 77-81% of the time (the rivals' 62-74%; `decoded.py channels`), and tributes start with an ally within 3 of the altar as often for us as for the rivals (36-40% against 32-37%), so escorts are not the gap. Starting the channel there under threat when health outlasts the nearby enemies' damage per round times its turns (uf1) rarely triggers against the platform's teams (tribute starts with an enemy within 6 of the altar 8.3 per game against tg1e's 7.8) and leaves the loss unchanged (105.7), while the channels cost farming (collected -14 +- 5 per game over brkp2's 100 games).

## 01yellow_brick_road and the cover lock (helper h3 on our ranked games, go1 on bwm; 10-28 afternoon)

- **Layout** (40x30, rotated; details in `docs/helper3/NOTES.md`): spawns 29 steps apart joined by a road between two rows of 30 gold clusters (one group each, 3600 health, walls until cleared); along it per side wolves, an elk pair and in the centre two 45-gem groups (2 elks, 2 wolves, gems, gold) touching the two central altars; off the road two corner elk groups per side.
- **The gap is farming, not fights.** Our 12 newest ranked games (h3): collected by r1000 498 against 883, deaths 7.4 against 6.8. On `bwm` (go1, `main_bwm1028@bwm`, 20 games against ranks 79-90): collected 676 against 857, tributed 630 against 814, our deaths 5.8 against their 9.7, 5 wins.
- **Cause: `pick_group`'s `covered` rule** (`targets.h`). A live elk group made every group within its reach 4 unpickable, asleep or not (monoliths only within 10 rounds of waking), so elk groups within 4 of each other locked each other for good: our corner pair and the centre pair, 39% of the map's gems. Captures of those groups per game by r1000 (`tools/helper3/h3_lockgems.py`): ranked us 1.2 against the rivals' 13.8 on their mirrored groups (gems 47 against 441); bwm us 0.9 against 13.0 (41 against 402). `tools/helper3/h3_cover.py` finds the same lock on 7 of 70 maps: 01hooks (all 88 gems of a clear), 00fragment (76%), 01boss_battle (63%, the 400-gem guard included), 01yellow_brick_road (39%), 01corridors (22%; on bwm we take none of its five east lanes' locked groups, the rivals 4.7 a game), 00corners (15%), 00swirl (5%).
- **Local check of the fix** (h3, an elk group covers only while awake; main against `h3cv1`, the seven lock maps, 42 games each): locked-group captures 1.2 to 14.5 per game, collected +30%, tributed +40%; yellow 6 of 6 wins (3), deaths 7.8 to 5.0. On 70 maps (420 games each) the total is flat (wins 241 against 240): gains on yellow, 00swirl and 01corridors (+342 to +538 gems a game), losses on 01hooks, 00fragment and 01boss_battle (about -335), because the pool bots carry the same lock and the fix opens those groups to them too (a pair split across the halves, or the boss guard that opens the altar). Platform rivals have no such lock. Gated as `cov1` (task 6).
- **Platform result (cov1, adopted 10-28 17:14 IST).** On bwmp's 20 yellow games: locked-group captures 0.9 to 17.2 per game, collected +29%, tributed +28%, wins 5 to 11; our deaths +0.8 +- 1.0, which failed that rule's bar of +0.5 (our deaths per game vary by about 4.5, so 20 games cannot resolve it). Retest on a 100-game panel of five lock maps (`lkmp`: yellow, hooks, fragment, boss_battle, swirl; ranks 66-78): captures 3.0 to 14.9 per game (the rivals 15.1 to 13.1), our deaths -2.3 +- 0.7 per game, collected +46%, tributed +65%, wins 30 to 50; 00swirl deaths 20.1 to 12.2. The fix changes play only near elk groups: bwmp's interlock and both gemcombat maps played identical games, and b13p2 (one game per map, 50 maps) moved by +0.1 deaths and +8% tributed.

## Ranked 00vault loss to 天天开心 (23e527b9, 10-28 15:02 IST, lost 0-1000 at r325; flagged by the user)

Decoded in `data/fights/vault_ranked` (replays `data/replays/platform/vault_ranked`); the map has no elks, golems or monoliths, so go1 and cov1 play it alike. Our ranked record there before today: 8 wins, 7 losses of 15 (10-26/27).

- **Layout** (31x31, rotated): one group decides the game, the vault: 49 gem clusters (x12-18, y12-18) worth 343 gems, walled, with a 2-tile door on each side (ours at x19 y14-15, theirs at x11 y15-16; holes at top and bottom), respawning 50 rounds after its capture. The rest is four wolf and gold groups (4 gems each) and two gold pairs; both altars, (25,5) and (5,25), are as far from either spawn.
- **The opening.** Both teams reach the vault at r10. Hits on vault clusters r10-22: theirs 39, ours 7. Their four enter by their door and cut inward; two of ours walk around the vault to that same door (one south by (13,20)-(10,18), one north by (16,10)-(10,14)) and enter beside their four. Fight inside r24-45: two of ours die, none of theirs; a third flees at 90 health.
- **Three captures, all theirs.** Their bags jump by 371 gems at r80, 399 at r175 and 385 at r277; tributed 229 by r100, 488 by r200, 776 by r260 and 1000 at r325 (the instant win). We collected 4 gems; hits on the vault over the game, ours 74 against 230.
- **Waiting at the door.** Before the first respawn (r101-129) one of ours stands still at (19,15) for 29 rounds and a second at (20,16) for 18. When the vault returns at r130 both hit through the door, one cluster at a time, while their four clear it from inside. From r157 to r169, with 13 clusters left and then through their capture, the two stand idle at the door again (1000 and 852 health). A capture needs 5 rounds with no enemy on the region and resets when an enemy enters (`docs/MECHANICS.md`, section 7), so one step onto a cleared vault tile would have reset each of their captures: at every one of the three, one of ours stood within 3 tiles of the region.
- **In today's other 00vault game** (f58b53c6 against Ding, won 813-595 at r2000) they captured at r62 and r195, we at r810 and r1099.
- **Fix idea: capture denial.** When every camp of a group is dead and an enemy champion stands on its region, a champion of ours within 3 steps and not in kill range steps onto a free region tile, which resets the capture. Metric: rival captures completed while one of ours stood within 3 tiles of the region (3 of 3 here). The door wait (idle rounds beside a respawning group that the rivals reach from their side) is the second thing to look at.

## 00interlock: lone waiters in our own half (bwm base, go1; 10-28 afternoon)

Twenty games of `main_bwm1028@bwm` (ranks 79-90), to r1000: collected 591 against 642, tributed 531 against 614, lost on death 35 against 7, deaths 6.0 against 4.0. Helper h3's ranked-game study (`docs/helper3/NOTES.md`, "00interlock") found the same: lone champions die on the long lanes after r600. Scratch readers `deathkind.py` and `staydeath.py` (first contact = the first round of the final approach with an enemy within 4; home distance = open steps to the victim's spawn):

- **The whole death gap is in our own half.** Deaths at home distance 20 or less: ours 2.85 per game, theirs 0.70 (21+: 3.10 against 3.25).
- **Mostly champions standing still, alone.** Before contact the victim's home distance changed by less than 3 over 8 rounds: 3.00 against 1.40 per game; at contact alone 2.40 against 1.10 (alone and outnumbered by 2+: 1.60 against 0.55). Static deaths in our own half: 1.35 against 0.15, after r600 1.00; enemies were already within 9 five rounds before contact in 1.25 of the 1.35 (2+ of them in 0.75); death came 6-15 rounds after contact in 0.90 (a flight down a lane). The examples stand at or beside our far groups (our elk group x28-29 y2-4, the middle elk group x31-32 y9-11) or idle in a lane.
- **Why they stay:** the fight count (`bot.cpp`, `enemy_count`, `enemy_power`) takes enemies within 6 only, and a threatened but healthy champion out of reach keeps working; so a lone champion leaves only when the pack is in reach.
- **Walks home are not it here:** deaths that began on a walk toward home with an enemy in sight, 0.35 against 0.35 per game (scratch `homewalk.py`; over all of bwm 0.60 against 0.40, gemcombat5 1.35 against 0.55).
- **Leaving on sight does not work** (ev1, ev2, local): walking home for 8 rounds when 2+ enemies come within 9 and no ally is within 6 removed the static own-half deaths locally (0.50 to 0.00 on 6 interlock games) but gave up 00contest (deaths +5 to +6 per game, tributed -333 to -367, also with the rule limited to our half and outside camp fights). The cure has to be company (fewer lone waiters at far groups), not distance.
- **Company does (sq2, 10-28 evening).** Scoring a group only for the champions already heading there (tg1) and counting a joiner's share as sqrt(n) instead of n (sq1) keeps our champions together. On bwmp's 20 interlock games, paired to r1000 with `cov1_bwmp@bwmp`: allies within 6 per alive champion-round 0.72 to 1.02 (rivals 1.06), alone 49% to 37%, solo strong-camp tank rounds 322 to 173 per game (`tools/replay/tankalone.py`); our deaths in our own half 2.85 to 1.15 (`tools/replay/ownhalf.py`), all our deaths 6.0 to 2.6 (-3.3 +- 0.7), theirs 4.0 to 5.5, collected +142 +- 50, tributed +158 +- 53. tg1's scoring alone (tg2) did not move cohesion locally, so the sqrt share does the work. Locally against our own pool the same change cost gems on the gem-rich maps (our-half gems on yellow 882 to 757, gemcombat1 802 to 682); on the platform the other 80 bwmp games held (collected 97.3%, tributed 98.3%, deaths -0.6), with yellow -12% and gemcombat5 -9% collected against corridors +16% and gemcombat1 +5%. Local pools do not hunt in packs, so they overstate what spreading out earns.

## adgato_gemcombat5: big bags on a long trip (sq2 on bwmp; 10-28 evening)

Twenty games of `sq2_bwmp@bwmp` (ranks 79-90), to r1000: collected 982 against 1187, tributed 547 against 918, lost on death 297 against 102, deaths 5.3 against 4.0 (cov1, the same games before company: collected 1076 against 1081, lost 321 against 99). Collection is level; the gap is what dies in the bag. Helper h3's ranked-game study (`docs/helper3/NOTES.md`, "adgato_gemcombat5") gives the layout: one altar between the two spawns, 15 steps south of both; all 24 groups are gem clusters, the rich ones far south (a 140-gem group 56 steps out, 63-gem groups 45 out).

- **We bank too rarely and carry too much** (`tools/helper3/h3_tribbag.py`): tribute starts 8.1 per game against 17.4; our bag at a tribute start q1/median/q3 56/66/140 against 35/63/84; champion-rounds carrying 40+ gems 763 against 584, 80+ 490 against 237; deaths with a bag 2.8 per game (median 133 gems) against 1.5 (63).
- **Cause: the order-quantity batch** (`bot.cpp`, "Order quantity") grows with the collection rate, which is two to three times a normal map's here (h3's probe h3bql: go1's batch quartiles on gemcombat5 36/65/94), so a champion holding 63-140 gems still counts as under its batch and walks on to the next group; one trace (h3): Varg took the 140-gem group at r417, then 63 more, and died with 203 six tiles from the altar.
- **Candidate: a 40-gem cap on the batch** (h3bq1, ported on sq2 as `bq2`). Locally against our pool (6 games, paired with sq2's): tribute starts 10.8 to 13.0, rounds carrying 80+ 456 to 375, lost on death 281 to 188, tributed 853 to 943; gemcombat1 lost on death 96 to 56. Local pools do not hunt carriers as the rivals do, so the platform decides.
- **The 140-gem middle group is the leak** (scratch `capclass.py`, gem jumps of 15+ without a kill): we take it 3.8 times per game, the rivals 0.9; within 120 rounds its capturer tributed 1.20 times, died 0.90 (141 gems, half of our 297 lost on death) and still carried 1.70. The rivals take the 21-gem groups 11.8 times per game (8.5 on their half), we 2.0: captures 12.3 per game averaging 73 gems against 24.4 averaging 37. Nobody splits a capture (1.00 capturers per capture for both teams).
- **The capturer walks alone** (scratch `trace140.py`): at r71 four of ours take the 140 group; the batch there is about 227 gems (order quantity with c 0.63 and a 97-round trip), so the capturer waits with the team for the respawn and takes 280, then walks the 41-44 steps to the altar alone (no teammate within 6 after about 16 rounds) and dies 1-6 tiles from it with 2-3 enemies near, or tributes.
- **The approach kills, not the altar** (`tools/replay/altarvisit.py`, scratch `deathspots.py`): our bag deaths fall in the corridor north of the altar 0.75 per game, the altar room 0.90 and the south field 0.85, 1.65 of 2.55 while moving toward the altar; visits within 1 of the altar end in death 0.25 times per game (of 8.45). Visits with no enemy within 6 at arrival: ours 3.15 per game, the rivals 8.65. Tributing under threat would save little: of the deaths whose first contact was within 3 of the altar (0.95 per game), a walk and channel would have finished in 32% (40 gems per game; scratch `couldbank.py`).
- **bq2 and esc2 on bwmp** (`docs/experiments.md`): the 40-gem cap left tribute starts at 8.3 per game and lost on death at 317; the 60-gem cap (esc2, whose escort never ran) sent the 140 bags off at once, tributed 1.85 of 4.5 and lost 1.30 (lost on death 343), because the carrier still walked alone.
- **The capturer freezes inside the 140-gem group** (traces; scratch `freeze.py`, carrier-rounds with 30+ gems standing still on the group's tiles): the group is 5x4 in a walled pocket with a 3-wide exit. A capturer inside it has no neighbour off the group, and the respawn-wait step-off (`camp_fight.h`) looked only at neighbours, so it stood on a spawn tile and held back the respawn its teammates waited for; in other games the waiters, within 2 of the group, filled the exit row (one esc3 game: all five still from r80 to r200). Frozen carrier-rounds: 94 per game for sq2 on bwmp (18 of 20 games), 41 for esc3. esc4 steps toward the altar when no neighbour is off the group and stands waiters back to 4 while a teammate is on the tiles: on main locally 85 to 27.5 per game. Any group of 3x3 or more has interior tiles like this.

## adgato_gemcombat1: deaths at the altar and no gold (esc4 on bwmp; 10-28 night, task 9)

Twenty games of `esc4_bwmp@bwmp` (ranks 79-90), to r1000, us against them: deaths 5.0 against 3.1, collected 805 against 949, tributed 604 against 852, lost on death 150 against 54, carried 51 against 42. The layout is in `docs/helper3/NOTES.md` ("adgato_gemcombat1"): six 21-gem cluster groups, one altar in the centre, no gold camps.

- **The tribute gap is the death gap counted twice.** The rivals' collected includes the gems they take off our dead (our 150 lost) and ours includes theirs (54): from camps the teams collect about 750 against 800. So of the 248 tributed gap, about 190 is the 96 lost-on-death gap counted on both sides; the largest gap is gems lost on death (2.8 times theirs), with deaths 1.6 times theirs.
- **Where we die** (scratch `data/task9_scratch/deaths1.py`, own-side coordinates): within 4 of the altar 2.35 per game (78 gems, 1.10 alone) against 1.10 (29, 0.25 alone); in our own half 2.35 against their 1.30 there; in their half 0.25 against their 0.75 in theirs. Altar deaths are fights, not channels: a tribute in the last 8 rounds in 6% (scratch `altardeath.py`). Bag deaths (30+) 1.50 per game for 125 gems, 1.35 of them within 10 of the altar. The rivals stand within 4 of the altar 805 champion-rounds per game, we 474; our tribute starts have an enemy within 6 in 57% (theirs 32%; scratch `tribco.py`).
- **Kills from equal damage** (`decoded.py fights`, `starts`, esc4 and sq2, 40 games): champion damage by r800 14085 against 14788, deaths 4.2 against 2.4; fights they start kill 0.26 per start, ours 0.14. By type (`decoded.py types`): our Heart of Ruin dies 2.0 times per game against theirs 0.5; under half health and hit (`decoded.py shots`) our Heart spends 17.3 rounds per game with P(death within 10) 0.43, theirs 6.5 rounds at 0.09; at 80%+ and hit 0.046 against 0.005. Their champions survive the same contact much more often.
- **No gold for items.** Team gold (`decoded.py gold`) r300 119 against 228, r600 213 against 557. Split by the rival's draft (scratch `marcsplit.py`, esc4 and sq2, 40 games): against the 24 teams that field Marcella the rivals hold 717 at r600 (we 252) and our lost on death is 181 against 63; against the 16 without her 284 (we 151), lost 155 against 21. Our 3-pick draft is Heart, Vendetta, Vesper on every map; Vesper's passive (+33% camp gold) gives nothing on a map without gold camps, and gemcombat1 is the only 3-pick map of the 70 with no gold (`data/maps_txt`).
- **Cause (as far as measured):** our champions lose the fights at the centre and in our half at equal damage, with half the rivals' items by r600 (gold comes only from kills and Marcella here), and the gems die with them. The death gap is there against the teams without Marcella too (deaths 4.7 against 2.4), so gold is not all of it.
- **Target (task 9):** set at 22:00 against esc4 (lost on death 110 or less, base 150, rivals 54). esc4 was not adopted (22:05, its b15 collected bar), so main is sq2, whose gemcombat1 numbers on bwmp (`sq2_bwmp@bwmp`, to r1000) are: lost on death 191 against 39, deaths 5.3 against 2.8 (our Heart 2.1 against 0.5, Vendetta 1.9 against 0.75), tributed 598 against 881, team gold r600 210 against 530; within 4 of the altar we die 2.15 times per game with 124 gems, they 0.95 with 15. Target against sq2: lost on death 115 or less per game (half the gap), with tributed not below 598.
- **Mechanism check for nm1** (Heart, Vesper, Marcella on 3-pick maps without gold camps; local, 6 games each against cand1, cp3, dh3, `data/runs/multi-215243`): our team gold r600 314 to 827, by r1000 598 to 1700; tributed by r1000 859 to 872, lost on death 70 to 70; wins 5 to 6 of 6. Probe hp0l (esc4 with a print, the same games): hurt Hearts with an enemy within 2 choose `flee` in 66 of 113 turns under 35% health and `pvp` in 34.
- **nm1 on the platform** (the draft change on esc4, `nm1_bwmp@bwmp`, paired with `esc4_bwmp@bwmp` on the 20 gemcombat1 games, to r1000): team gold r600 213 to 820 (the rivals 465), lost on death 150 to 85 (-65 +- 39), tributed 604 to 752 (+148 +- 52), our deaths 5.0 to 3.2 and theirs 3.1 to 6.5, deaths within 4 of the altar 2.35 to 1.55; wins on the map +8 of 20. Our Marcella dies 0.75 times per game with 11660 champion damage (the rivals' Marcella 1.58 and 7711). The other 78 bwmp games replayed identically. Gold was the larger part of the gap.
- **nm2 on the platform** (the same draft change on sq2, `nm2_bwmp@bwmp`, paired with `sq2_bwmp@bwmp` on gemcombat1, to r1000): team gold r600 210 to 678, lost on death 191 to 98 (-93 +- 31; bar 115), tributed 598 to 723 (+125 +- 64), our deaths 5.3 to 4.2 and theirs 2.8 to 4.8, bag deaths (30+) 1.80 to 0.90 per game, deaths within 4 of the altar 2.15 to 1.75 with 124 to 51 gems; on the map 10 games went from loss to win and none the other way. What is left: the rivals still start 31 tributes per game with a median bag of 21 against our 17 with 42 (scratch `tribbag1.py`; champion-rounds carrying 40+ gems 758 against 166), and our bag at r300 is 81 against 26; the 20-gem batch cap (bc1, `results/analysis/bc1_on_sq2.patch`) is the next lever there.
- **The gold gap is gemcombat1's alone among 3-pick maps** (scratch `pick3.py`, 152 three-pick games of sq2, esc4, cov1, go1, tg1 and main runs on b13p2, b14, b15, brkp2, brk, b13 and lkm, team gold at r600): ours 2437 against the rivals' 2582 over all of them (00packs, 76 games: 2553 against 2931; 01gold_rush, 9: 1901 against 3401; 00fragment, 24: 1954 against 1982), against gemcombat1's 210 against 530. Every other 3-pick map has gold camps, so the Heart, Vendetta, Vesper draft stays there.

## Ranged hits outside fights (sq2 on brkp2; 10-28 night, task 10)

Reader: `tools/replay/rangedhits.py` (decoded runs, to r1000). It splits every basic hit by an enemy ranged champion on a champion into: in a fight (the victim hit an enemy champion that round or the one before), walked in this round, walked in last round, and free; "outside fights" is the last three. It also counts exposure rounds (a non-fighting turn that ends inside an enemy shooter's basic range) with the share shot next round, and the response to a light shot (shooters only, victim not fighting, at 50%+ health): a round later it hit back, is out of range, is still in range, or is dead.

- **The gap** (`sq2_brkp2@brkp2`, 100 games, the five pinned maps): ranged hits on our champions 102.8 per game against 63.6 on theirs; in a fight 53.0 against 37.2, walked in this round 13.1 against 3.3, walked in last round 8.5 against 7.9, free 28.2 against 15.2, so **outside fights 49.9 against 26.4**. In fights the two Vespers are level (42.9 against 37.2); outside fights their Vesper hits us 40.7 times, ours them 26.4. We end 89.2 non-fighting turns per game inside an enemy shooter's range, they 47.6 (shot next round 39% against 40%); after a light shot we are still in range a round later in 50% of 15.1 events per game, they in 38% of 7.2 (the top 12 teams on their own games: 37%).
- **Other panels.** b13p2 (sq2): outside fights 32.8 against 18.7. esc4 on b14 and b15: about 33 against 18, exposure 57.1 against 30.7. bwmp (sq2): 25.6 against 24.0, level. Ranked games on our four worst maps of 10-28 (00ribs, 00lost_world, 02crossing, 02gift_wrapping, 19 games, `data/fights/ranked_bad1028`): ranged hits 69.8 against 26.8, outside fights 39.8 against 10.9. The top teams (top12 panel) take 81.5 ranged hits per game and deal 100.5, with exposure about equal to their opponents'.
- **Where the exposure comes from** (tg1e on brkp2, scratch scripts): by the move that ended in range, chase 30.5 against 24.3 rounds per game, step level 19.5 against 5.8, step away 19.4 against 8.7, standing 14.6 against 7.9. Non-chase exposure after a hit in the 3 rounds before: 38.9 against 12.2; without one 14.7 against 10.2; homeward 24.5 against 7.2. Champions that were just shot walk home through the shooter's range.
- **Hits in the round we walked in** (13.1 against 3.3): we stepped closer 7.7 times (4.8 toward the shooter, our nearest enemy, so chasing it; 2.8 toward another enemy), level 0.9, away 0.3; in 4.2 we had not moved and the shooter came into range and shot.
- **How a shooter shoots from beyond its range** (`tools/replay/rh_comeinslots.py`, the shooter's action list in that round): of those 4.21 hits per game, 2.63 come after a walk and the shooter's attack reset (Vesper's slot 0: 2.17, 0.06 of them with a ward first; Tavi's slot 0: 0.29; Willow's slot 1: 0.17) and 1.58 after Vesper's dash (slot 1, two tiles; 0.10 of them with a ward first). No shooter walked and shot without a reset in the 100 games: the reset restores the shot a walk costs a ranged champion, so a shooter with its reset ready threatens 4 tiles, and a Vesper with her dash ready 5 (each slot has an 8-turn cooldown). Our shooters landed no hit of this kind on a non-fighting enemy in the 100 games.
- **Cause in code (sq2).** In the threat branch (`bot.cpp`) `healthy` was `S.hp >= 0.5 * max && !hit_by_enemy`: any hit made a champion unhealthy, and it fled home (`walk_home` with danger avoidance off) through the shooter's range. `take_snapshot` (`knowledge.h`) adds danger tiles only for enemies whose burst is at least 30% of our health; a Vesper's burst (135 at base stats against 1000-1200 health) never qualifies, so no move avoided a shooter's range.
- **rz1** (shooters' basic range is danger, and a light shot from shooters alone keeps a champion `healthy`; row rz1 in `docs/experiments.md`). Local probe pair on the brkp2 maps (30 games each, `XP` lines per turn ending in a shooter's range): no-hit exposure turns to_capture 118 to 25, approach 105 to 18, respawn waits 90 to 18, camp fights 85 to 4, bank 40 to 0, flee 440 to 332, pvp 1304 to 1582; hits outside fights 39.9 to 31.9 per game; by r1000 deaths 6.0 to 4.4, collected 706 to 735. Most of the remaining pvp exposure is the chase step from 4 to 3 (990 of 1582 turns).
- **Holding at the range edge in a chase costs more than it saves** (rz2 = rz1 + no pvp close-in step that enters a shooter's range unless it reaches the prey; local, the same 30 games): whole-game kills 458 to 394, deaths 189 to 228; by r1000 deaths 4.4 to 5.4, collected 735 to 670, although hits outside fights fell to 27.4.
- **The gap is how often we are shot first, not what follows** (`tools/replay/rh_pursuit.py`; a first shot is a shooter's basic hit on a non-fighting champion it had not hit in the 8 rounds before): on us 14.8 per game, on them 7.5. In the next 8 rounds that shooter adds 2.29 hits on us against 1.98, walks toward the victim 1.47 against 1.45 times, and the endings are alike (victim dead 0.13 against 0.12, hit back 0.27 against 0.36, apart 0.33 against 0.30). First shots at about 3.3 hits each make up the whole outside-fight count.
- **Where the first shots come from** (`tools/replay/rh_firstshot.py`, `rh_camein.py`): already in range at the round start 6.32 against 6.04 per game (level); came into range that round 8.52 against 1.47. Of those, the shooter came in (a walk and a reset, or a dash) 3.21 against 0.00, and the victim walked in 5.31 against 1.47; it saw the shooter at the round start (its own fog view, `vis`) in 4.35 against 1.15.
- **We walk into shooters' range more often; they shoot as readily** (`tools/replay/rh_walkevents.py`): walk-ins (a non-fighting champion moves from beyond 3 tiles of an enemy shooter to within 3) 27.0 against 17.4 per game, shot by it that round or the next in 52% against 47%; toward the shooter 21.8 against 15.7. In the local probe rz0l (main), 841 of the 1002 turns that walked into a visible shooter's range were in the pvp branch.
- **What we were doing when we walked in** (`tools/replay/rh_walkctx.py`; first shots after the victim walked into the range of a shooter it saw, per game, us against the rivals; enemies on their spawn do not count as nearest). Toward the nearest enemy, the shooter itself: 2.61 against 0.72 (of ours 1.52 plain chases, 0.56 while farming, 0.32 toward our spawn, 0.11 carrying 30+). Toward the nearest enemy, another one: 0.89 against 0.30 (0.66 plain, 0.17 farming). Not toward the nearest enemy: 0.85 against 0.13 (0.21 toward our spawn, 0.13 going home hurt, 0.11 farming, 0.37 other). Banking walks are almost never shot (0.01). No single context holds the gap: chasing is the largest, and those chases trade about even (next bullet).
- **Vesper's turn after a hit on her** (`tools/replay/rh_vesperhit.py`, sq2 on brkp2, to r1000; an enemy champion hit her the round before and one stands within 3 at the round start; per game, us against the rivals). It happens in 34.5 turns against 22.9. She shoots in as many of them (11.7 against 10.7 turns; shot and dash 0.07 against 0.79), so the extra turns are spent walking (12.5 against 7.0), dashing and walking (5.3 against 1.7) and doing nothing (4.9 against 2.6). Her death rate within 10 rounds after each kind of turn is alike on both sides (shot 0.08 against 0.07, walk 0.28 against 0.22, nothing 0.32 against 0.30): the gap is how often she is hit, not what she does then.
- **Those chases trade about even** (`tools/replay/rh_walkpay.py`: melee walk-ins toward a shooter no ally is fighting, the next 7 rounds). With the shooter our nearest enemy, 8.4 per game (the rivals 6.5): 2.34 shots taken, 1.71 hits dealt, the shooter dead in 7% and the walker in 4% (the rivals 2.30, 2.19, 6%, 3%). With another enemy nearest, 6.3 per game (3.8): 2.32 shots taken, 2.47 hits dealt, the walker dead in 8% (the rivals' 9%). With an ally already on the shooter (2.1 per game) the shooter died in 23%, the walker in 1%.
- **The top teams do not avoid these hits; they out-shoot** (`data/fights/top12`, 152 games, `tools/replay/rh_comeinacts.py`, `rh_firstshot.py`): top teams take 11.55 first shots per game and land 15.04; their shooters land about 7.8 hits per game from beyond range (4.64 after a walk and a reset, 3.11 after a dash) and take about 5.4.
- **What the defensive variants did on the platform** (rows rz1, rz4): neither moved the hits outside fights (49.9 to 47.6 and to 50.1, guards held). rz1's danger tiles do not touch the pvp walk-ins, which are most of them; rz4 removed the walk-ins it targets (probe rz4l: 227 closing steps skipped per 30 games, none of that kind left), and they are few. Keeping a 4- or 5-tile berth from a shooter whose reset or dash is ready (rz3) cost deaths +2.2 per game locally.
- **How the attack reset is spent** (`tools/replay/rh_resets.py`, every reset cast by a ranged champion, to r1000): our shooters 41.07 per game, all after an attack (double shot); the rivals' 37.51 double shots plus 18.92 after a walk, then a shot (most of them in fights; 2.63 on non-fighting victims). The rivals do not give up double shots for the walk-in shot: they cast the reset about 56 times per game to our 41, because ours waits until we are already in range.
- **How Vesper's dash is spent** (`tools/replay/rh_dashes.py`, slot 1, the actions before and after it in the same turn, to r1000). sq2 on brkp2, ours against the rivals', per game: as the first action with no shot after it 67.93 against 52.66; after a walk 0.00 against 8.00; after a shot 0.93 against 0.50; dash then shot 0.16 against 7.85. In the top 12 games (top teams against their opponents): 40.40 against 36.20, 11.53 against 12.75, 1.18 against 2.56, and dash then shot 7.55 against 6.22. Every side but ours dashes into a shot six to eight times per game.
- **What a shot from beyond range buys** (`tools/replay/rh_shotpay.py`: a shooter over 3 tiles from a non-fighting victim at the round start hits it at its round-start tile; that round and the next 6, per event). The rivals' on us (sq2 on brkp2): 4.21 per game; their team then lands 3.95 hits on the victim, we hit the shooter back 0.92 times, our victim dies in 14% and their shooter in 1%, and the victim hits any enemy within 3 rounds in 27%. Ours in rz5 (local, five brkp2 maps vs cand1, cp3, dh3, 30 games, `data/runs/multi-002527`): 4.50 per game, 3.47 hits, 1.12 hits back, victim dead in 8%, our shooter in 0%, victim fighting within 3 rounds in 29%. Reset use in that run (`tools/replay/rh_resets.py`): 8.63 walk-in shots and 39.50 double shots per game against main's 0 and 46.00, so rz5 casts 2.1 more resets per game and gives up 6.5 double shots. Ranged hits on the rivals rose 75.1 to 79.5 per game, but outside fights only 38.7 to 39.9: the free hits (28.2 to 26.0) and those a round after a walk (7.6 to 6.6) fell, and in a fight rose 36.4 to 39.6.
- **rz5 on the platform** (brkp2, 100 games paired with sq2 to r1000; row rz5): our walk-reset-shots on non-fighting enemies 0 to 3.94 per game; hits on them outside fights 26.4 to 31.8, on us 49.9 to 48.0. Our team then hits the victim 2.87 times in 7 rounds (the rivals' shots on us: 4.02), it hits back 1.21 times, the victim dies in 9% and our shooter in 0%. Our deaths rose 8.47 to 8.84 per game, all of it in melee champions (Vendetta +0.3 +- 0.1, Marcella +0.2 +- 0.1; Vesper -0.1), while our double shots fell 41.07 to 35.97 per game. Locally the same change had cut deaths 254 to 242 (150 games).
- **rz6 on the platform** (brkp2, 100 games paired with sq2 to r1000; row rz6): Vesper dashes, then shoots, 10.12 times per game (the rivals 7.68), 4.42 of them on non-fighting enemies, and keeps her double shots (41.3 per game). Hits on them outside fights rose 26.4 to 35.1 and their deaths 7.36 to 8.20, but hits on us outside fights stayed (49.9 to 49.5; all ranged hits on us 102.8 to 103.2), and our deaths rose 0.43 per game, again in the melee champions (Heart of Ruin and Vendetta +0.2 each), with our gems lost on death 41 to 63 per game. With rz5 this settles it: out-shooting the rivals raises both sides' deaths and leaves the hits they land on us outside fights where they were, so that gap is not a shooting race we lose.

## False bank blocks after a break (main = nm2, local probe; 10-29 00:20 IST, lead session)

- **The bug.** `bot.cpp` gives up banking for 40 rounds (`bank_blocked_until`) when the walk to the altar makes no
  progress for 7 bank turns (`bank_best`, `bank_stall`). Both were reset only when the bag fell below the batch or a
  block fired, not when the walk broke off. A heal trip home (recall), a fight or a death between two bank turns kept
  the best distance of the earlier walk, so the walk back from home counted as no progress and the carrier was blocked
  six or seven turns into it. It then farmed on with its bag for 40 rounds.
- **How often** (probe `exp/mainpl` = main + one print per block with the rounds since the best was set and the
  current run of consecutive bank turns; play identical to main; 7 maps x cand1, cp3, dh3 x both sides,
  `data/runs/multi-002132`, lines in `data/task9_scratch/bs_main.txt`): 215 of 223 blocks were false (the best
  predated the current walk), 8 genuine. Per game: 00fragment 2.0 (mean bag at the block 25), 00interlock 5.5 (38),
  00lost_world 7.3 (30), 00packs 1.5 (29), 01corridors 6.0 (67), adgato_gemcombat4 9.7 (50), adgato_gemcombat5 3.8
  (106).
- **Found through esc5 on adgato_gemcombat4** (locally esc5 lost 183 gems on death per game against main's 40;
  ablation `data/runs/multi-001050`: without the escort 41, without the cap or the respawn fixes 183). In
  `exp-esc5~pool-cp3~adgato-gemcombat4~A` our Vendetta recalled home with 119 gems at r198-203, was blocked at r210
  on the walk back (probe `exp/esc5pl`), farmed to 196, recalled again with 238 at r349, was blocked again at r355,
  and died at the centre altar at r516 with 350. The escort adds fights and heal trips (champion-rounds per game to r1000,
  main against esc5: pvp 146 to 206, recall 41 to 49, home_heal 17 to 21), which is likely why esc5 hits the bug more
  often.

## Deaths in fights the rivals start (sq2 on brkp2 and the top 12; 10-29 night, t10)

Readers: `tools/replay/decoded.py starts`, `tools/replay/fs_firsthit.py`, `tools/replay/fs_closein.py`. Base sq2 on brkp2 (100 games, to r1000); top12 = the 152 decoded ranked games of the top 12 teams on our worst maps (`data/fights/top12`, "us" = the top team).

- **The side that opens a fight wins it.** Our deaths per game by who opened the fight that killed us (walking back through champion hits within 8 of the victim until 15 quiet rounds): 5.14 when the rivals opened it, 1.67 when we did, 1.63 both; theirs 3.04 when they opened it, 2.86 when we did, 1.27 both. They open 60.2 fights per game (first hit between a pair after 15 quiet rounds), we 37.3, outnumbering in 42% of theirs and 33% of ours. The top 12 teams open 58.0 and their opponents 49.5.
- **The gap is openings from 4-5 tiles** (`fs_firsthit.py`, distance at the round start): ours 10.1 per game, the rivals' 28.4, the top 12 teams' 31.7 and their opponents' 26.9; from 1-3 tiles 27.2 against 31.8. The rivals' openings from 4-5 tiles: Vesper's basic attack 9.19 (ours 2.15: a walk and a reset, or a dash; see "Ranged hits outside fights"), Marcella's spell 7.43 (6.26), Ryth's spell 4.08 (we draft no Ryth), Vendetta 1.89 (0.71), Heart of Ruin 1.08 (0.67), Cassi, Tavi and Willow 3.3 together; the top 12 teams' Marcella spell 9.28, Vesper 8.41, Vendetta 2.77, Heart of Ruin 2.46. The victim had the opener in its own reach in one of the 3 rounds before in only 2.1 (ours) and 2.4 (theirs) openings per game: the opener comes from beyond reach.
- **Melee openings with a step and a dash** (`fs_closein.py`): the rivals' Hearts of Ruin step, dash next to the target (the striking dash: damage and stun) and hit 0.75 times per game, their Vendettas dash, step and hit 1.62 times; the top 12 teams' 2.05 (Heart of Ruin) and 1.97 plus 0.86 the other order (Vendetta). Ours never do (our Hearts and Vendettas dash only from 3 tiles: 1.45 and 2.07 per game). These openings kill the victim within 10 rounds in 21-39% and lose the striker in 2-5%. Ours also dash, hit and then walk (Heart of Ruin 1.02 per game: the victim dies in 3%, the striker in 17%; Vendetta 0.54: 4% and 11%). rz7 gives our Hearts and Vendettas the step-and-dash opening (row rz7).
- **Melee hits followed by a walk** (`fs_hitwalk.py`, sq2 on brkp2, to r1000, per game): after a basic hit on an enemy champion our melee champions stand 98.4 times (the rivals 134.8), walk away 45.4 times (33.8) and walk level (to a tile as far from the target) 19.7 times (4.3). Standing: the target dies within 10 rounds in 33% (34%), the hitter in 8% (7%); walking away: 5% (8%) and 32% (25%); walking level: 7% (16%) and 32% (26%). Most of our level walks are by Hearts of Ruin (8.4 against 1.3). Which branch of the bot makes them is not measured yet (a local probe with `log_rounds` would show it); the hitter's deaths after a walk mark fights already lost as much as any cost of the walk.
- **rz7 on the platform** (brkp2, 100 games, paired with sq2 to r1000): our Hearts of Ruin and Vendettas made 4.06 step-and-dash openings per game, and our openings from 4-5 tiles rose from 10.1 to 13.7 per game, but the rivals still opened 60.9 fights per game (60.2): our openings came on top of theirs, not in place of them. Our deaths in fights they open fell from 5.14 to 4.99, in fights we open rose from 1.67 to 1.88, and theirs in fights we open from 2.86 to 3.24; all deaths: ours +0.16 +- 0.4, theirs +0.6 +- 0.6. The new openings killed the victim within 10 rounds in 22-26% (the rivals' own 21-39%, locally 34-47%).

## Gems per camp hp: gold groups over gem clusters (main = nm2 on b13p2 and b16p; 10-29 03:00 IST, t9)

Base: `nm2_b13p2@b13p2` (50 games on 50 maps, five teams above us) and `nm2_b16p@b16p` (the fresh batch of 10-28, teams then 14-28 ranks above us), decoded, to r1000. Scratch readers in `data/task9_scratch/` (gitignored): `activity.py`, `campdmg.py`, `wastedmg.py`, `capkind.py`, `gemmap.py`.

- **On b13p2 the gap is collection, not deaths.** By r1000 we collect 640 gems against 724 and tribute 509 against 606; we die 4.9 times per game against 4.3 and lose 40 gems on death against 47. The gap grows late: collected by r300 186 against 202, by r600 405 against 444. On b16p we are level (713 against 680 collected, 3.6 deaths against 4.7).
- **We hit camps as much and as hard; they get more gems for it.** Champion-rounds per game hitting a camp, r600-1000: 212 against 201; camp damage per camp-hit round 152 against 136 (r300-600: 104 against 100). Gems gained without a kill per camp-hit round: r0-300 0.67 against 0.66, r300-600 0.87 against 1.02, r600-1000 1.08 against 1.31; gems per 1000 camp hp removed 7.1 against 9.6 after r600.
- **Not waste, not steals.** Of our credited camp damage 89% goes to camps that die within 40 rounds and are captured by us (theirs 86%); damage on camps that survive 40 rounds is 3% (theirs 5%). Steals (a group captured by the side that did not hit it first) are under 1.2 per game in each region.
- **Group choice: we take gold where they take gem clusters.** Captures per game by group kind (us against them): pure gem-cluster groups 5.8 against 11.0 (114 gems against 163; own half 2.5 against 3.6, middle 2.0 against 5.6), gem clusters with a golem 0.18 against 0.42 (13 gems against 33), pure gold-cluster groups 12.4 against 10.0 (620 gold against 581). In all, captures yield us 554 gems and 3712 gold per game, them 612 and 3385. The pure gem-cluster gap sits on a few maps with a middle field of single clusters or big cluster groups: 02stalactites (2 captures against 12), 00lost_world (6 against 84), 02treasure_box (0 against 94; its only altar is in a walled box among 16 single clusters, the rivals stood in the box all game and we tributed 0 in 717 rounds), 02the_pack, 01broken_curve, 00anvil.
- **We no longer lack gold on normal maps.** Team gold (unspent plus 30 per shard) against the rivals': b13p2 1.03 at r300 and r600, 1.11 at r1000; b16p 1.08, 1.17 and 1.21; brkp2 (the bad maps, where we die more) 0.93, 0.88 and 0.92. It is spent: about 40-60 unspent per champion on both sides. The 10-26 finding that the top 12 earned about 1.5 times our camp gold by r600 no longer holds on these panels, and the earlier `gold_weight` tests (rows gw1-gw3, ge1-ge3, pw1, pw2, pg1, pg6) ran on older bots and mostly raised the weight. `gold_weight` counts 0.25 gem per gold to r1400; lv1 lowers it to 0.1 from r300 (row lv1).
- **By team size (10-29 03:30, `tools/replay/bysize.py`, `capkind.py --size`, `mapgap.py`).** The collection gap is the 5-champion maps: on b13p2 (29 of 50 games) collected 665 against 782, tributed 520 against 680, deaths 5.2 against 3.1; on 3- and 4-champion maps we are even or ahead (b16p: ahead on all sizes but 5, where collected is 732 against 752). The gold surplus above is the 3- and 4-champion maps (team gold 1.2-1.67 times theirs); on 5-champion maps it is 0.93-0.97 at r300 and 0.96-1.04 at r600. The pure gem-cluster gap (5.1 against 8.7 captures per game over b13p2 and b16p) is 57% two maps, 02treasure_box (0 against 94 in its one game) and 00lost_world (15 against 71 a game); the rest is a tail of 0.05-0.3 per game each (02the_pack, 01big_world 0 against 13.5, 00split, 01broken_curve, 00ribs). When a middle gem group comes up their nearest champion is a median 2 tiles from it with 3.1 of theirs within 10, ours 8 tiles and 1.5 (`race.py --kind gem`); outside the middle, gem-cluster groups sit up and unhit 37-45% of rounds 1-1000.
- **lv1 (gold 0.1 gem from r300) on b13p2 and b16p**: collected +38.8 +- 13.9 per game to r1000, tributed +41.1 +- 13.9, our deaths +0.27 +- 0.22 (pooled 100 games); pure gem-cluster captures on b13p2 5.80 to 7.62, gold clusters 12.40 to 8.06; team gold at r600 -5.5% (b13p2) and -6.2% (b16p). Adopted (row lv1).

## Bags at the end of games, and the ranked losses (main = nm2; 10-29 03:40 IST, t10)

Readers: `tools/replay/endbag.py`, `tools/replay/budget.py`, `decoded.py gems`, `tools/platform/ranked.py`. Panels `nm2_b13p2@b13p2`, `nm2_b16p@b16p`, `nm2_bwmp@bwmp`, `nm2_bgl@bgl` (250 games).

- **Ranked record (the last 100 games to 10-29 03:13 IST):** 49 wins. Of the 51 losses, 31 are economic (our deaths minus theirs under 3; the rivals reach 1000 at a median r1050 while we hold a mean 656 tributed; 11 of them end with us at 800 or more) and 20 are fight losses (deaths 3 or more above theirs, each on a different map). The economic losses spread over 25 maps and 13 opponents; `an iq too high` won 6 of its 10 games against us that way, with no fight loss.
- **We do not lose games with the win in hand.** In our 118 panel losses we held 1000 in hand (tributed plus carried) at the end in 2 (adgato_gemcombat5 971+161, 00split 922+97), in 3 at any time; the rivals did in 7 of their 132 losses (8 at any time). In our close losses our bag at the end is mostly 0 (02famine 995+0 against 965+324, 00swirl 986+0, 01yellow_brick_road 973+0 and 962+0, 01corridors 962+0): the rivals won by banking their last bag first. Mean bag at the end: losers ours 58, theirs 36; winners 118 and 110.
- **Bank trips do not cost camp time.** Share of champion-rounds to r1000: hitting camps 0.176 against 0.177 (b13p2) and 0.181 against 0.165 (b16p); walking with a bag 0.128 against 0.105 and 0.110 against 0.094 (bags carried longer, not more trips); tribute rounds equal (0.004).
- **The bag at r1000 is larger** (91 against 71 on b13p2, 57 against 45 on b16p, 67 against 57 on bwmp), but gems lost on death are below the rivals' on b13p2 (40 against 47) and b16p (28 against 36); only bwmp is above (89 against 41, the adgato_gemcombat maps of tasks 8 and 9).
- So tribute timing holds no gap worth a variant (earlier batch caps, bk1-bk4 and ge6, cost collection). The economic gap is collection ("Gems per camp hp").

## First 5v5 brawls and Heart of Ruin's dash before the flee (main = nm2; 10-29 05:00 IST, t10)

Readers: `tools/replay/fs_brawl.py`, `fs_heartdash.py`, `fs_heartafter.py`, `fs_ffcomp.py`, `fs_attacked3.py`, `fs_ready.py`, and the probe joins `probe_contact.py`, `probe_vesper.py`, `probe_inreach.py` (probe rz8l). Panels: nm2 on b13p2, b16p and b17p (150 games; 78 on 5-pick maps), lv1 on the same three for the brawls, and `data/fights/top12`; to r1000.

- **The first 5v5 brawl goes to the rivals.** In the first fight of a game with 4+ of each side within 8 of the victim (31 brawls, nm2 + lv1, 5-pick maps), over the next 20 rounds: our champion hit-rounds 18.5 against 27.4, damage to champions 1277 against 1784, deaths 0.84 against 0.45; we lose the first champion in 16 of 24 (Heart of Ruin 8, Vendetta 6). Champion-rounds with an enemy in basic reach: ours 19.9, theirs 29.9, of which 16.4 are their ranged picks (Vesper 5.8, Willow 4.9, Tavi 3.6, Stellar 1.7); melee is level (13.2 against 13.5). The top 12 against their opponents: 19.9 against 17.9 and deaths 0.33 against 0.58.
- **Our Vesper hits in 0.42 of her in-reach brawl rounds** (theirs 0.61, the top 12 0.64). Probe rz8l: with an enemy champion within 3 she shoots in 57% of rounds; in `flee` (12.1 rounds per game) in 19%, walking away in 54%; before a `flee_dash` (3.7) in 19%. Three variants made her shoot more (vh1m, vs1, vfs1) and each raised team deaths, so this is not retried.
- **Being together does not win our first fights** (`fs_ffcomp.py`, 75 games on 5-pick maps): with all five of ours within 8 of the victim we still lose the first fight in 54% (13 games); the top 12 lose 11% in that case. Allies of a victim at even numbers join (hit a champion within 5 rounds) by their distance to the nearest enemy (`fs_attacked3.py`, lv1 on b13p2 + b16p, 5-pick maps, to r150): 1 tile 0.90 against the rivals' 0.95, 3 tiles 0.50 against 0.71, 5+ tiles 0.25 against 0.65.
- **Abilities are not held back** (`fs_ready.py`): at fight starts on our champions their slots are ready as often as the rivals' (Heart of Ruin shield 0.41 against 0.37, Vesper 0.56 against 0.63).
- **Heart of Ruin dashes in and then walks away.** Our Heart's striking dashes with an enemy champion within 3 of the landing: 9.71 per game against the rivals' Heart's 8.08 (150 games). In 3.92 per game (the rivals' 0.87) the Heart hits and then walks in the same turn, and it dies within 10 rounds after 22% of those (the rivals' 6%). On 5-pick maps after a landing among more enemies than allies + 1, our Heart dies after 39% (1.36 per game), theirs after 16% (0.87), the top 12 after 12% (3.61 per game; they almost never walk after the dash). Probe rz8l: these dashes are cast in `flee` (3.46 per game; then a hit and a walk away 48%, level 37%; the Heart died after 35%). The threat branch (`bot.cpp`) casts the champion abilities at the prey before it decides to kite or flee, and the Heart's dash is one of them: it lands next to the prey and the walk home starts from there, with the turn's cast spent (no shield, no flee dash). In `pvp` the same dashes (5.65 per game) are not followed by a walk, and an enemy near the landing dies within 10 rounds after 54%. rz9 skips the dash there (row rz9).

## Gem clusters in rounds 300-600, and own-half clusters a passing champion takes (main = nm2 on b13p2, b16p, b17p; 10-29 07:54 IST, t9)

Base: `nm2_b13p2@b13p2`, `nm2_b16p@b16p`, `nm2_b17p@b17p` (150 pinned games, decoded, to r1000 unless stated). Readers: `tools/replay/decoded.py` (`gems`, `lives`, `sources`), `tools/replay/capkind.py`; scratch readers in `data/task9_scratch/` (gitignored): `activity.py`, `hometrips.py`, `groupcaps.py`, `timeline.py`.

- **Lives and camp time are level; the rivals take gem-richer groups.** Camp lives captured per game: 41.5 against 42.5 (own half: we 28.7, they 4.4 of ours; middle 10.1 against 11.6; their half: we 2.7 of theirs, they 26.5). Champion-rounds hitting a camp, r100-1000: 607 against 608. We spend more champion-rounds in our own half (2431 against 2264) and fewer in theirs (229 against their 369 in ours); home trips 41.8 against 46.2 a game.
- **The collected gap opens in rounds 300-600 and is gem clusters.** Collected: r300 180 against 189, r600 394 against 439, r1000 668 against 717, r1500 822 against 864. Gems by the camp type last hit (`decoded.py sources`): gem clusters 80 against 88 by r300, 164 against 213 by r600, 252 against 312 by r1000; monoliths 3 against 14 by r1000; elk (194 against 195), wolf (95 against 90) and gold clusters (102 against 83) are level or ours. The tributed gap is larger than the collected one (r1000: 542 against 612) because our bag is larger (85 against 62).
- **Where the cluster gap sits** (pure gem-cluster groups, captures and gems per game, us against them): own half 3.16 (55 gems) against 4.64 (71), middle 1.84 (59) against 3.69 (75), their half 0.75 (8) against 1.22 (13). In the middle the rivals take more and smaller clusters (20 gems a capture against our 32).
- **Own-half clusters lose the pick to gold.** Probe `lv2pl` (main plus one `Q` line per pick, local, 00road-of-riches, r100-1000; row lv2pl): of 3285 picks made while one of our own-half one- or two-cluster gem groups was up within 20 steps, `pick_group`'s upper bound pruned it in 2643 and it scored below the pick in 597 (median 0.68 of the pick's score); it was picked 35 times. 57% of the winning picks were solo (median 0.76 of the cluster's travel-free value), and 970 of 1506 were mixed groups whose gold counts 0.25 gem. On that map the rivals take 30.5 such captures a game, we 0.5.
- **Boosting them works only near.** Local, 54 games each against cand1, cp3 and dh3 on 9 maps (rows lv2, lv3): counting their gems 1.6 times at any distance (lv2) doubled own-half pure-cluster captures (9.35 to 19.81 a game) but the champions walked home for them, our middle captures fell and the opponents' collected rose (739 to 770; our collected margin +11 a game, team gold at r600 -10%). Within 8 steps only (lv3): captures 9.35 to 19.04, collected 896 to 946, the opponents' 739 to 712 (margin +77), team gold at r600 -5%. On the platform (lv3 on b13p2 + b16p + b17p against the nm2 bases, 145 paired games to r1000): own-half pure-cluster captures 3.16 to 4.68 a game (the rivals' 4.64 to 4.46), collected +35.2 +- 11.2, tributed +30.3 +- 11.3, our deaths -0.39 +- 0.18, the rivals' collected -22.4 and tributed -26.1, team gold at r600 unchanged (100.6%).
- **On rz9 the gain shrank** (lv3r = rz9 + the same `targets.h`, against `rz9_b13p2@b13p2` and `rz9_b16p@b16p`, 95 paired games to r1000): own-half pure gem captures still rose (2.52 to 3.49 a game; middle 1.76 to 2.51) and the opponents' collected fell 11.3, but our collected rose only 7.6 +- 16.8 and tributed fell 2.1 +- 14.6 (lv3 against nm2 on the same two panels: +26.4 and +16.7). Weighting the two comparisons by their games (145 against nm2, 95 against rz9 on the same pinned opponents), the change gives about +24 collected and +18 tributed a game. With lv3 the panels' camp economy is level (gems by camp type to r1000, lv3's 145 games: gem clusters 281 against 281, elk 198 against 183, gold camps 108 against 81, wolf 99 against 99, golem 18 against 25, monolith 1 against 14; captures 44.0 against 41.1 a game; unspent gold per champion at r600 44 against 45); what is left is the 5-pick maps (85 games: collected -30, tributed -55, deaths +0.7 a game), most of it in massacre games (t10's factor).
- **00ribs, the largest single-map gap** (2 games, collected 28 against 976, deaths 11.5 against 2.0): every gem sits at the far end of a 51x85 map, in two elk groups with four clusters each (43 gems, 90 gold, 2880 hp) beside the two altars, 65 steps from both spawns. Our champions arrive one by one, die there (in one game 6 of our 9 deaths within 10 tiles of the altars) and never hold the ground; the rivals stay beside the altars for 100-200 rounds at 50-65% health and buy health (one tank at 3600 by r850).

## Ranked record at 10-29 08:35 IST: blowouts repeat on 00ribs and 00contest (mains nm2, lv1, rz9; t9)

Reader: `tools/platform/ranked.py 100` (the last 100 ranked games; 81 have summaries), list in `data/task9_scratch/ranked100.txt`.

- 37 wins of the 81. Of the 44 losses, 16 are close (we tribute 700 or more; our deaths 2.9 against their 5.4 a game), 12 are in between and 11 are blowouts (we tribute under 400 and die 6 or more times more than they do): 00ribs three times (0-1049 with deaths 13/1, 57-1005 with 13/0, 214-1016 with 20/4), 00contest twice (0-1000 with 18/4, 200-1000 with 28/5), 02guardians (0-1158, 17/3), 00eight (197-1019, 13/2), 01gold_rush (264-1020, 20/4), 02crossing (376-1000, 8/0), 00quarry (156-1012, 14/8) and 02stalactites (77-1076, 8/0).
- Unlike t10's 03:40 count (fight losses each on a different map), the blowouts now repeat on two maps: 00ribs, where the gems sit by the far altars (see "Gem clusters in rounds 300-600", last bullet), and 00contest (not looked at yet). Deaths per game: in our wins 3.9 against 10.5, in our losses 8.2 against 5.8.
- So the close losses (16) are the camp-choice factor (lv3, lv4), and the blowouts are map-specific death traps for the fight factor (t10).

## Deaths by champion type after rz9: Vesper in contact, Vendetta's dives (rz9 on b13p2, b16p, b17p; 10-29 08:45 IST, t10)

Base: `rz9_b13p2@b13p2`, `rz9_b16p@b16p`, `rz9_b17p@b17p` (144 pinned games, decoded, to r1000). Readers: `tools/replay/sizedeaths.py`, `typedeaths5.py`, `dmgstate.py`, `withnumbers.py`, `meleestick.py`, `adjepisodes.py`, `atdist.py`, `vesperidle.py`, `dives.py`, and the probe join `probe_dive.py` (probe rz11l).

- **Five a side is where we die more.** Deaths per game by team size, us against them: three a side 2.62 against 4.23 (26 games, 18 wins), four 5.12 against 7.32 (34 games, 18 wins), five 4.35 against 3.58 (84 games, 40 wins; in 9 of them a rival Cassi pick brings Issac, 5 against 6). In the 75 games with exactly five a side, by type: Vesper 0.84 against the rivals' Vesper 0.38, Vendetta 1.08 against 0.72, Varg 0.97 against 0.77, Heart of Ruin 0.91 against 0.83, Marcella 0.61 against 0.73.
- **Outnumbered we take more hits** (`dmgstate.py`, 75 games, enemies and allies within 5): with 3+ enemies and no ally near, hits received per round 1.24 against 0.82 and deaths per 100 such rounds 5.5 against 4.1; with 2 enemies and no ally 0.60 against 0.43. With 2+ allies near, our own hit share is lower at every number of enemies (one 0.11 against 0.19, two 0.23 against 0.32, three or more 0.36 against 0.42).
- **With the numbers, they close in and hit more** (`withnumbers.py`, rounds where the champion's side has at least as many champions within 5 as the enemy): melee adjacent to an enemy 22.2 rounds per game against 37.2 (hit share 0.79 both). Ranged at distance 3: 14.1 rounds per game against 30.6. At distance 4 (19.8 against 25.5 rounds), ours hit in 0.03 and walk closer in 0.47, the rivals' hit in 0.20 and walk closer in 0.28; a hit from 4 needs a walk or a dash first, which rz5 and rz6 tried on brkp2 (both failed their death guards).
- **Melee contact does not stick** (`meleestick.py`): when the enemy next to our melee champion steps away, our melee is next to it again at the next round start in 0.18 of the cases at even numbers (theirs 0.46), 0.30 with more champions near (theirs 0.49) and 0.13 with fewer (theirs 0.30). With more champions near, their melee spends 39.0 rounds per game next to one of ours against our 22.5.
- **Vesper in contact** (all 144 games; the rivals field her in 99): episodes of round starts with an enemy champion next to her 5.97 per game against 4.69, with 17.3 hits on her in them against 10.8 (her own hits 5.97 against 5.31); 0.51 per game end with her death (theirs 0.23), and in 2.33 she gets 3+ tiles away (1.40). With a melee enemy 2 tiles away (17.6 rounds per game against 14.4) she does nothing in 0.25 of the rounds (theirs 0.12) and walks away in 0.11 (theirs 0.21). Of her no-action rounds with an enemy within 3 (9.06 per game against 6.26), 4.27 have a stun cause in that round or the one before (an enemy Heart of Ruin's dash landing next to her 1.36, Ryth's area 1.33, Marcella's stun hit 1.29, Ren 0.22), the rivals' Vesper 2.10 (we field no Ryth); 4.78 have none the reader sees (theirs 4.17).
- **Vendetta's dives** (`dives.py`, a slot 1 dash landing next to an enemy champion, 75 games): ours 2.87 per game against the rivals' 1.33. She dies within 10 rounds after 0.16 of ours and 0.05 of theirs, and a champion next to the landing dies within 10 after 0.22 against 0.24. Dives followed by her death within 10 rounds: 0.46 per game against 0.07, more than the whole Vendetta gap (1.08 against 0.72). By the margin at the landing (enemy champions within 3 minus her and her allies within 3): at -1 or better 0.95 per game against 0.59 (she dies after 0.03 and 0.00, a target after 0.35 and 0.27), level 1.31 against 0.55 (0.15 and 0.05; targets 0.18 and 0.21), one short 0.47 against 0.14 (0.29 and 0.20; targets 0.14 and 0.30), two or more short 0.15 against 0.04 (0.73 and 0.33; targets 0.00). Heart of Ruin's striking dashes show no such gap (3.67 per game against 5.21; she dies after 0.08 and 0.06).
- **The dives come from the fight branch.** Probe rz11l (main plus `log_rounds`, 48 local five-a-side games against cand1, cp3 and dh3, `data/runs/multi-081430`): 2.50 of the 3.36 dives per game are in activity `pvp`, the `dash_next_to` in the favourable-fight branch of `bot.cpp` (melee at 3 tiles from the prey); the attack-on-sight branch has a second one for Vendetta. The local opponents punish the dives less than the platform's: she dies after 0.06 of the dives at level or better and 0.14 of those one or more short.

## Outnumbered: the same exposure as the rivals, twice the deaths (rz9 on b13p2, b16p, b17p; 10-29 09:35 IST, t10)

The 75 games with five a side, to r1000. Readers: `tools/replay/outnumbered.py` (all three tables), `tools/replay/walkins.py` (walk-ins by margin).

- **The death gap is in fights with three or more enemies near.** Deaths per game by the enemy and allied champions within 6 of the victim: three or more enemies and no ally 0.77 (the rivals 0.49), one ally 0.89 (0.21), two or more allies 0.96 (0.87). With two enemies or fewer we die less than they do (1.78 against 2.05). Our deaths in all 4.41 per game, theirs 3.63.
- **We are outnumbered no more often than they are, but die more per round there.** Rounds per game with three or more enemies within 6: no ally 21.2 (the rivals 17.4), one ally 35.0 (32.7), two or more 95.8 (97.4). The chance of dying within 5 rounds of such a round: 0.175 against 0.125, 0.118 against 0.051, 0.048 against 0.041.
- **What we do there.** With three or more enemies within 6 and at most one ally (no ally / one ally): our health 0.63 / 0.67 of max (theirs 0.70 / 0.76), nearest enemy 2.44 / 2.58 tiles (3.00 / 2.89), we attack in 35% of the rounds (22% / 27%), move away from the nearest enemy in 41% / 34% (50% / 40%), sideways at the same distance in 23% / 22% (13% / 12%), closer in 10% / 15% (14% / 19%), and lose 84 / 63 health per round (50 / 44). They step back to 3 tiles and keep moving away; we stay closer, keep hitting and move sideways.
- **Walk-ins one or more short.** Our Vendetta and Varg walk next to an enemy where the enemies within 3 of the new tile outnumber them and their allies within 3 2.40 times per game (the rivals' 1.33). One short against a target above 40% health: 1.31 per game (0.81), the walker dies within 10 rounds after 0.28 (0.08), the target after 0.08 (0.07). Two or more short: 0.49 (0.13), dies after 0.54 (0.20), no target dies. One short against a target at 40% or less: 0.60 (0.39), dies after 0.07 (0.03), target dies after 0.36 (0.45). Level: 6.89 (3.12), dies after 0.06 (0.02), target after 0.24 (0.11). Our Vesper walks in short 0.45 times per game, dying after 0.47 (theirs 0.21, 0.17); Heart of Ruin and Marcella show no gap (0.28 and 0.16 deaths per game after short walk-ins against 0.30 and 0.18). This led to rz13.
- **Locally the outnumbered rounds are mostly `flee`.** Probe rz11l (48 local games against cand1, cp3 and dh3, `data/runs/multi-081430`; scratch `probe_outnum.py`): of our 64.4 rounds per game with three or more enemies within 6 and at most one ally, `flee` 23.9 (moves away in 63%, sideways in 29%; dies within 5 rounds after 0.217 of them, loses 65 health per round), `pvp` 11.5 (closer in 46%; 0.036), `to_capture` 6.9, `kite` 3.9 (away in 91%; 0.016), `flee_dash` 2.6 (away 90%; 0.056), stunned 2.0 (0.196). The flee step (`walk_home`) takes the neighbour closest to spawn and ignores where the enemies are, so a third of its steps keep the distance to the nearest enemy.
- **00contest, the extreme case.** In the three 00contest games (all lost) we died 36, 14 and 15 times by r1000 (the rivals 2 in all): 41 of our 65 deaths had three or more enemies within 6 and at most one ally, 4-35 tiles from our spawn (median 16); the victims' health the round before was 11% of max at the median (quartiles 5% and 18%).

## Vesper's contacts while short: her shot from 2 tiles (rz12 on b13p2, b16p, b17p; 10-29 10:55 IST, t10)

Five-a-side games to r1000, 76 with our Vesper and 59 with the rivals' (`tools/replay/contacts.py` and scratch readers on the same decodes). "Short" means more enemy champions within 6 of her than her allies within 6 plus one.

- **Deaths.** Our Vesper dies 0.82 times per game, theirs 0.51. An enemy stands next to ours in 63% of her deaths (theirs 37%). She spends 12.5 rounds per game next to an enemy (theirs 7.5), 8.1 of them in a contact that already lasted a round (4.1).
- **Contacts begun while short:** 2.11 per game against 1.10. She dies within 10 rounds after 0.28 of them (0.22); a contact lasts 3.01 rounds (2.18); her dash was ready at the start in 31% (38%). How they begin, per game: right after her shot, the enemy stepping in, 1.14 against 0.37 (0.97 against 0.34 from 2 tiles); she moved and an enemy came, 0.41 against 0.19; she walked in, 0.28 against 0.25; she stood, 0.28 against 0.29.
- **At 2 tiles from a melee enemy while short and healthy** (half health or more, no health lost since the round before): ours shoot in 84% of the rounds (two shots in 18%) and move in 14%; theirs shoot in 52% and move in 34%. The next round an enemy stands next to ours in 47% (28%), and she dies within 5 rounds after 8.3% (2.2%).
- **Next to an enemy while short:** with half health or more 3.5 rounds per game against 1.9 (P(dies within 5) 0.120 against 0.036; ours attack in 32% and walk in 35%, theirs 48% and 26%); under half health 2.9 against 0.7 (0.452 against 0.548).
- **Cause in the code.** The threat branch's kite step (`bot.cpp`) takes a "free" hit, on a target farther away than its own reach, before it steps out of danger. A shooter cannot walk after its shot, and with the reset ready the reset spends the turn's one cast, so the flee dash cannot run either: she stays at 2 tiles and the melee enemy steps in. **rz17** (row) steps out first and shoots with the reset after the walk.
- **rz17** (row; b13p2 + b16p, 95 paired games): stepping out before the shot cut the contacts after her shot from 2 tiles from 0.89 to 0.68 per game and her deaths from 0.84 to 0.72 (-0.13 +- 0.07). Our deaths fell only in the 39 games with fewer than five a side (3.44 to 2.69, -0.74 +- 0.34; theirs +0.69 +- 0.39); with five a side they stayed (4.41 to 4.46, +0.05 +- 0.23), as Marcella, Vendetta and Heart of Ruin died a little more. On b17p (its check, 50 games, 20 with five a side) her deaths fell again (0.92 to 0.80) but the contacts after her shot from 2 tiles did not (1.20 to 1.30 per game), so the step out of the kite branch is not where most of them begin; over the three panels (145 games) her deaths 0.87 to 0.74 (-0.12 +- 0.06), ours 4.15 to 3.92 (-0.23 +- 0.16), win share 0.54 to 0.58. rz17 is N by its rule (mechanism).
- **rz14's flee step** (rows rz14, N) cut our Vesper's deaths on the three panels from 0.82 to 0.64 per game, more than any other type's (Marcella 0.76 to 0.62, Varg 1.04 to 0.92).

## Golem groups: nobody starts them alone (rz9, lv3, lv3r on b13p2, b16p, b17p; probe lv5pl; 10-29 10:55 IST, t9)

Reader: `tools/replay/golemcrew.py` (each side's champions hitting a golem per round, and per golem life
who dealt the last hit, its length and the largest crew), 88 platform games on maps with golems.

- **Level overall, behind on four maps.** Golems killed per game, us against the rivals: 2.11 against 2.35 over the 88
  games, with the same crew sizes (one champion in 54-55% of golem-hit rounds). By map: 02famine 1.10 against 4.30,
  00split 2.12 against 3.62, 00quadrants 0.75 against 1.88 (the rivals' largest crew 3.7, ours 2.7; one champion in 63%
  of our golem-hit rounds, 23% of theirs), 02cuts 3.17 against 3.83, 02uncharted_lands 3.27 against 3.91; we kill more
  on 00oasis (8.2 against 2.0) and 00dunes (3.6 against 1.2). Ranked, last 300 games: 00quadrants 1 win of 7, 00split
  2 of 7, the six golem maps 9 of 24.
- **02famine:** each side has its own gem+gold+golem group (5 camps, 50 gems, 200 gold). The rivals capture theirs 3.86
  times a game with 411 champion-rounds within 2 of it; we capture ours 1.14 times (69) and farm our home elk group
  instead (11.9 captures a game, 699 champion-rounds).
- **Why (probe lv5pl, main's `pick_group`):** a lone champion scores a golem group at about a quarter of what it
  picks. 00quadrants' two middle gem+golem groups (13 camps, 120 gems, 160 gold each): median 0.21-0.25 alone against a
  median pick of 1.0-1.07; 02famine's own golem group 0.11-0.14 against 0.44-0.45. With 2-4 teammates already claiming
  it the score is 0.36-2.06, so the group is taken only after others have committed (in 4-22% of picks, by crews of
  3-5). `clear_time` charges a lone champion for the heal trips the golem's 120 strength forces.
- **A crew in the score is not enough (lv5, local):** scoring strong groups with one more teammate and gathering for
  that crew raised our golem kills from 1.50 to 2.83 a game on 8 golem maps (crews up to 3.07), but group captures fell
  from 52 to 42 a game, collected from 1029 to 965, and deaths rose 0.9 a game; a golem life lasted 86 rounds against
  54. A golem crew pays only when it does not stop the rest of the farming. Next to try: one designated farmer for our
  own-side golem group with its respawn waited out (the rivals' famine pattern), or crews only for own-side golem groups.
- **Narrowed to golems, the same (lv6, local on rz12, 11:10):** crews only for golem groups outside the enemy's half raised golem kills from 1.69 to 2.81 a game, but captures fell from 52.5 to 45.1, collected from 1055 to 963 and deaths rose 0.46 a game; the opponents' collected rose where our crews went (00quadrants 973 to 1100, 00split 906 to 1040). Golem crews in `pick_group` are closed. What the rivals do differently on these maps is still open: their golem clears are not crews (55% of their golem-hit rounds are one champion), so the next look is how their lone champion survives a golem (items, abilities, kiting at range) before any variant.
- **No lone-champion trick either** (scratch `data/task9_scratch/golemhit.py`, rz9 on b13p2, b16p, b17p, 33 games with golems, to r1000): the rivals hit golems 128.9 times a game against our 91.8, all from 1-3 tiles (0-4% from 5 or more), and lose as much health per golem hit (weighted over types about 38 against our 34; their Marcella 42, Vesper 38, Heart of Ruin 37, Vendetta 76, Ryth 57, and the ranged Willow, Tavi and Cassi 4-10 while a teammate holds the golem; ours Marcella 45, Vendetta 45, Vesper 29, Heart of Ruin 29, Varg 17). So the rivals simply spend more champion time on golems on these maps and still out-collect us elsewhere; the golem gap follows from a wider gap there, not from how golems are cleared.

## Where the gap is after rz12: six maps hold all of the collection gap (rz12 on b13p2, b16p, b17p; 10-29 11:18 IST, t9)

Readers: `decoded.py gems`, `tools/replay/bysize.py`, `mapgap.py`, `capkind.py --map`. Runs `rz12_b13p2@b13p2`,
`rz12_b16p@b16p`, `rz12_b17p@b17p` (145 games, 78 won: 21 of 45, 27 of 50, 30 of 50), to r1000.

- **Overall, us against them:** collected 692 against 706, tributed 563 against 610, lost on death 42 against 38, bag
  at r1000 87 against 58, deaths 4.2 against 4.6. Collection is level at r300 (182 and 182) and 409 against 426 at r600.
  By team size the 5-pick maps still trail on two panels (tributed 556 against 651 on b13p2, 572 against 664 on b17p,
  650 against 649 on b16p), 4-pick maps on b17p (463 against 572); we win 19 of 26 on 3-pick maps.
- **Six maps carry it** (`mapgap.py`, the rivals' collected minus ours summed over the map's games per panel game):
  00ribs +11.0 (2 games, 64 against 860, deaths 7.5 against 4.0), 00eight +10.7 (4 games, 512 against 900, deaths 11.0
  against 5.5), 00vault +8.8 (2, 694 against 1330), 00quarry +6.8 (3, 511 against 839), 02crossing +6.3 (2, 603 against
  1060), 00crater +5.1 (1, 178 against 923, deaths 17 against 1). These 14 games (10% of the panel) hold about 49 a
  panel game against a whole gap of about 14: on the other 131 games we collect more than the rivals.
- **What the rivals take there** (`capkind.py --map`): on 02crossing pure gem clusters (7 gems each), 42.0 captures a
  game against our 12.5 (their own half 20 against our 12, the middle 13.5 against 0.5, and 8.5 a game in our half
  against our 0 in theirs) and middle elk+gem groups 8.0 against 3.0; on 00quarry we take more of our own gold (27.3
  captures, 1563 gold, against 23.0 and 1105) and they the middle wolf+gem groups (10.7 captures, 413 gems, against 6.0
  and 236); on 00vault the middle gem groups of 140-200 gems a capture (2.5 a game, 0.5 of them in our half, against
  our 1.5). 00ribs, 00eight and 00crater are the death maps of the sections above.
- **Locally only 02crossing shows a gap** (main against cand1, cp3 and dh3 on 02crossing, 00vault and 00quarry, both
  sides, 18 games, `data/runs/multi-111953`, decoded `local_multi-111953_main`): 02crossing 2 of 6 won, collected 898
  against 1040, but its shape differs from the platform's: the pool bots take more of their own elk+gem groups (7.83
  captures a game against our 4.83) and a few more pure clusters (24.3 against 19.0; middle 5.7 against 3.5). 00vault
  (5 of 6, 693 against 410) and 00quarry (6 of 6, 989 against 248) do not reproduce. A change for 02crossing's
  clusters needs a platform panel with that map; the local pool is no test bed for it.

## The gap maps against teams 18-34: half their collection, from the opening (main = rz12 on bcg; 10-29 11:44 IST, t9)

Base run `main1029_bcg@bcg` (live main = rz12, 11:24-11:35 IST; panel row `bcg` in `results/panels/README.md`, pinned
as `bcgp`), decoded in `data/fights/main1029_bcg_bcg`, to r1000. Readers: `mapgap.py`, `decoded.py gems`, `capkind.py
--map` (output `data/task9_scratch/bcg_base.txt`).

- **2 of 50 won.** Collected 504 against 942 a game, tributed 437 against 827, lost on death 36 against 18, deaths 4.0
  against 2.8. The gap opens in the opening: collected 171 against 261 by r300, 330 against 626 by r600.
- **Per map** (10 games each): 00quarry 1 win, 214 against 964 (deaths 6.5 against 2.6); 00vault 1 win, 354 against
  1074 (5.0 against 4.4); 02crossing 0, 713 against 1062 (6.4 against 3.7); 00expanse 0, 750 against 948 (0.7 against
  1.0, so a pure economy gap); 02famine 0, 491 against 660 (1.3 against 2.4).
- **They capture more of almost every kind** (`decoded.py holds`: 38.5 group captures a game to r1000 against 51.7;
  we leave 4.4 holds uncaptured against 1.8, 2.3 of them with an enemy on or within 4 of the tiles), by kind (captures a game, us against them): 00quarry wolf+gem 3.4 against 15.9,
  gem clusters 4.6 against 11.3, gold 24.2 against 31.2; 00vault wolf+gold 1.6 against 7.0, gem 0.9 against 2.6;
  02crossing elk+gem 8.1 against 12.7, gem clusters 17.2 against 22.4, wolf+gold 1.0 against 6.3 (wolf+gem 13.0
  against 9.2 is ours); 00expanse wolf+gold 3.7 against 8.0, wolf+gem 3.8 against 7.7, elk+gem+gold 7.7 against 10.3;
  02famine gold 7.4 against 12.6, wolf+gold 6.7 against 11.0, the golem group 0.5 against 2.9.
- So against teams this high the collection gap is broad farming speed from the first rounds, not one group kind;
  on the pinned panels (lower teams) it hid behind maps we win. `bcgp` is the exact base for a change aimed at it;
  with 2 wins in 50, judge such a change on collected by r300, r600 and r1000 and captures, not on wins.
- **Fights there** (`decoded.py starts`, to r1000): they start 24.9 champion fights a game, we 14.5; of our 4.0 deaths
  2.84 come in fights they start (theirs in fights we start 0.98). So on these maps the death gap is the fights the
  rivals start (t10's factor, 'Deaths in fights the rivals start'), beside the farming gap.
- **The opening** (`decoded.py captures --round 300`): by r300 we capture 14.1 groups a game (own half 12.4 for 106
  gems, middle 1.2 for 44, their half 0.5 for 12), they 18.6 (own 14.2 for 92, middle 2.7 for 107, ours 1.7 for 13):
  the middle is 63 of the 90 gems they lead by at r300. Per capture, a capturer's rounds since its previous capture
  are 64.6 (median 51) against 49.9 (42), with 38.9 moves against 28.6 for the same straight hop (14.4 against 15.0
  tiles); clear and claim times are close (11.9 and 8.2 against 13.7 and 6.8). Trips home are not it (scratch
  `data/task9_scratch/hometrips.py`, to r1000: they make 40.6 a game against our 36.2, 20.8 against 13.6 with a bag;
  their bag at r1000 is 97 against our 32).
- **Where the time goes, r300-700** (scratch `data/task9_scratch/activity.py`, champion-rounds a game, our own half /
  middle / their half from each side's view, us against them): we move empty 487 / 50 / 30 against 336 / 60 / 75 and
  stand empty 171 / 41 / 6 against 99 / 44 / 26, so about 220 more rounds a game walk or wait empty-handed in our
  own half. They spend 238 rounds a game in our half (fights 28, camp hits 32, carrying a bag 75) against our 67 in
  theirs, and 285 against 203 in the middle; we fight in our own half 29 against their 11.5 in theirs. The next look
  for t9 is that idle own-half time: what our empty champions wait for (respawns, claims) while the rivals farm the
  middle and our half.

## Where the idle own-half time goes on bcg: a camp hidden in a bush (00quarry), walk churn (5-pick maps), the vault wait (main = rz12 on bcg; 10-29 13:15 IST, t9)

Base `main1029_bcg@bcg` as in the section above (decoded `data/fights/main1029_bcg_bcg`). Scratch readers in
`data/task9_scratch/`: `whatnext.py` (what an empty-handed champion's still or walking round leads to), `stillnear.py
--kind` (still rounds by the dead group near, its kind and rounds to its respawn), `walkdirect.py` (rounds of a walk
that do not bring the champion closer to where it ends), `cmswitch.py` (probe cm0pl's target switches), `adiff.py`
(A-line activity deltas). Per-map gems: `data/task9_scratch/bcg_base_permap_gems.txt`.

- **The 220 idle rounds split by map** (own half, r300-700, empty-handed champion-rounds a game, us against them):
  00quarry stands 377 against 133 (258 against 51 next to a dead camp); 00vault stands 137 against 41 (101 against
  12); 02famine walks 684 against 283 (walks that end at a camp 447 against 157); 02crossing walks 401 against 291
  (225 against 147); 00expanse walks 764 against 643 (to a camp 530 against 442, to a respawning group 173 against
  77). So on 00quarry and 00vault we wait, on the 5-pick maps we walk. Collected by r600 (us against them): 00quarry
  162 against 657, 00vault 282 against 949, 02crossing 598 against 826, 00expanse 321 against 364, 02famine 288
  against 333: the gem gap by r600 sits on the two waiting maps and 02crossing, not on the two maps that walk most.
- **00quarry: a gold cluster hidden in a bush.** Each side has a two-cluster gold group, (5,10) and (6,10) on the
  west side, whose inner cluster stands on a bush tile (the bush column at x=6, rows 10-18). A bush tile is seen only
  from inside its bush (`docs/MECHANICS.md` section 4), so from (5,10) our bot never sees it. After killing (5,10) a
  champion stands on that tile in the capture branch (`camp_fight.h`: no live camp of the group in view, so walk onto
  a spawn tile), while the engine reports the group alive (probe cm0pl's CF lines: `sdk_camp_group_state` 1, the
  adjacent bush tile not in view, capture state no_capture_available). The capture never starts, the group never
  comes back, and teammates that target it wait beside it. On the platform base our champions stood on that tile 359
  champion-rounds a game to r1000 (282 to r600) and stood still within 2 of it 326 more; the rivals 52 and 48 on
  theirs. That is about one of our four champions parked there all game: the A lines give `capture` 309
  champion-rounds a game in r250-750 on 00quarry (6 games reaching r750). Locally the same (`data/runs/multi-130554`,
  6 games against cand1, cp3 and dh3: every long capture on that tile or its mirror (29,10), from round 8 on). Of the
  70 maps (probe cmbushl, output `data/task9_scratch/bushcamps.txt`) only 00quarry and 02harvest have camps on bush
  tiles: two gold clusters each (on 02harvest the outer gold of the gold+elk+gold groups at (29-31,29) and its
  mirror, 15 gems and 130 gold a capture).
- **5-pick maps: walk churn.** Walks that end at a camp waste 0.206 of their rounds against 0.114 (94 against 45
  rounds a game, r300-700): 02famine 168 against 67, 02crossing 111 against 45, 00expanse 101 against 43, 00quarry
  61 against 49, 00vault 30 against 21. Probe cm0pl (a CM line at each target switch; 30 local games on the five maps
  against cand1, cp3 and dh3, `data/runs/multi-125437`): per game in r300-700, 14.5 switches away from a live target
  4+ tiles away while walking to it. Of those, 89% come at a periodic re-pick with no state change, 44% go back to
  the old target within 40 rounds, 41% turn to a target the other way, the new score over the current is 1.27 at
  the median (quartiles 1.10 and 1.59), a teammate also claims the current target in 51%, and 26% would have held
  without the futility divisor (`group_invested` counts walking rounds). Another 15.5 switches a game leave a
  respawning target while walking to it. Locally the waste share is the platform's (0.21), so it can be checked
  locally. But the r600 gem gap on 02famine and 00expanse is 45 and 43 a game: there we lose champion time more
  than gems, so a fix for it must be judged on the walk waste and must not cost gems.
- **00vault: the wait at the 343-gem group.** Our still rounds beside the respawning centre group with 31+ rounds
  to go: 58 a game in our half against 3.8 (`stillnear.py --kind`); locally 1712 of 2000 champion-rounds in r250-750
  are `resp_wait` on 00vault. This is the hold described in '00vault: one 343-gem group, a door fight and a hold'
  (our waiters cannot step off the group; the rivals take it 1.9 times by r1000 against our 0.7).
- **Target metric (written 13:15 IST, before any variant):** gems collected by r600 on bcgp, paired against the base
  `main1029_bcg@bcg` (330 a game; the rivals 626), judged on the games a variant changes. First variant cm1, the
  bush camp: mechanism, 00quarry champion-rounds on our outer gold tile beside the bush (to r1000) 100 a game or fewer
  (base 359, `data/task9_scratch/quarrytile.py`); target, 00quarry collected by r600 up by 60 a game or more (base
  162; 10 paired games). Guards (to r1000): all 50 bcgp games, and the pinned b13p2, b16p and b17p against rz12's
  runs there, our deaths up at most 0.3 a game and collected and tributed at least 97% of the base; 00quarry deaths
  up at most 0.5 a game. (13:30, before the gate: the other 40 bcgp games were first to be judged alone, as if they
  replayed unchanged. They do not: a local check with a cheaper test (`multi-132649`) still changed 2 of 4 games on
  00vault and 02crossing against main's, the fuel chaos of any code change, so they are a fresh draw and are judged
  with the whole panel. Guard panels hold one 00quarry and one 02harvest game each in b13p2 and b17p, none in b16p.)

## Against teams 34-60 we lose the group fights (rz12 on the fresh batch b19; 10-29 13:20 IST, t10)

Base `rz12_b19@b19` (main = rz12; Olympus 34, Noobot 37, PENTAKILL 48, Sheeesh--- 55, SquidProxyLovers 60 of the 12:40
ladder, we were 72), 50 games, 15 won, decoded in `data/fights/rz12_b19_b19`, to r1000. Readers: `bysize.py`,
`typedeaths5.py`, `outnumbered.py`, `decoded.py starts`, `fights`, `gold`, `items`, `teamfight.py`, `packreact.py`, and
two scratch readers (allies within 6 over alive rounds; deaths by the rivals' draft).

- **Five a side is where it goes wrong.** 31 games: 6 won, our deaths 6.61 per game against 2.71, collected 618
  against 877, tributed 533 against 799; with three a side we are level (deaths 4.09 against 4.55, 6 of 11 won). By
  type in the 25 games with exactly five a side: Heart of Ruin 1.44 against 0.64, Marcella 1.36 against 0.28,
  Varg 1.64 against 1.00 (their Varg in 5 games), Vendetta 1.68 against 0.43, Vesper 1.36 against 0.40. Every type dies
  about three times as often. Deaths come at the same rate all game: 2.2 against 1.1 by r300, 4.2 against 2.2 by r600,
  6.8 against 3.3 by r1000 (all 50 games).
- **Not spread out, but beaten together.** Alive rounds off spawn by allies within 6 (none / one / two or more): ours
  0.31 / 0.26 / 0.42, theirs 0.32 / 0.24 / 0.45. With an enemy champion within 8, our deaths per 100 rounds are 0.79 /
  0.80 / 0.70, theirs 0.35 / 0.38 / 0.09; on the three pinned panels (rz12, 76 five-a-side games) the same cells are
  0.71 / 0.50 / 0.26 against 0.57 / 0.37 / 0.29. With three or more enemies within 6 and two or more allies we die 1.92
  times per game against 0.40 (P(dies within 5) 0.107 against 0.019 per round) and lose 48 / 33 / 39 health per round
  with two / three / four allies near (theirs 36 / 29 / 13).
- **They start the fights.** They start 36.3 champion fights a game (outnumbering the target's side in 48%), we 16.8
  (36%); 4.50 of our 6.8 deaths a game come in fights they started and 1.08 in ours, while 1.04 of their 3.3 come in
  ours. After a pack sighting (two or more enemies within 8, at most one ally within 6) we die within 15 rounds in 9.7%
  (theirs 4.4%), stepping towards the pack -0.57 tiles over the next 5 rounds (theirs -0.83) and hitting a champion in
  0.50 of those rounds (0.74).
- **They hit harder and together.** By r800 their champion damage is 15285 a game against our 9821 (hits 169 against
  122), with 31.2 rounds a game where two or more of them hit champions (ours 16.9). Team gold in the five-a-side games
  is 0.79 of theirs at r300 (1136 against 1449) and r600 (2708 against 3414); a kill pays 100 gold, so their 2.0 extra
  kills by r600 are about 200 of the 706 gap. Max health at r600: Marcella 1862 against 2536 (they hold 1.71 Bruiser-focus
  and 1.13 Bruiser-health emblems, ours 1.33 Power-focus and 0.87 Treasure-focus), Heart of Ruin 1476 against 1876,
  Vendetta 1575 against 1770, Vesper 1914 against 2012.
- **Drafts with stuns and heals** (scratch, three pinned panels, five a side, rz12): our deaths against a rival Tavi
  6.16 per game against their 4.79 (19 games), without one 3.75 against 3.67 (57); against a Willow 5.23 against 3.41
  (22), without 4.00 against 4.17 (54). The fight simulation (`sim.h`) has no heals. Team strength may explain part of
  this, as the teams that draft them may simply be stronger.
- **rz19** (main + rz14's flee step, row rz19) on b19: our deaths 6.76 to 6.24 per game (-0.52 +- 0.41), theirs +0.58,
  collected 97.8%, tributed 97.9%, the same 15 wins; N by its mechanism bar. rz20 (the flee step plus rz17's shooter
  step) passed its target-only rule on the fresh batch b20 (our deaths -0.76 +- 0.40) and is main since 14:05.

## Shots, spells and stuns from beyond our reach (rz12 on b19, rz20 on b20, probe rz21l; 10-29 14:40 IST, t10)

Same games as the section above (`rz12_b19@b19`) and rz20's `rz20_b20@b20`, to r1000. New reader
`tools/replay/poked.py`; `stuns.py`, `focus.py`, `deaths.py`, `decoded.py types` and `assist`, and scratch readers for the
rest (no-hit deaths, engagement starts, the size of a shot).

- **Deaths without hitting back.** On b19, 1.86 of our 6.44 deaths to champions per game came after the victim hit no
  champion in its last 10 rounds (theirs 0.16 of 2.64; `deaths.py` counts the same). In those deaths 77% of the hits
  on the victim in its last 3 rounds came from beyond its own reach (by distance 1 / 2 / 3 / 4: 0.11 / 0.18 / 0.44 /
  0.25), from Tavi 0.29, Prism 0.22, Marcella (the spell) 0.18, Vesper 0.12, Willow 0.12; by victim Vendetta 0.54,
  Heart of Ruin 0.50, Vesper 0.42, Marcella 0.22, Varg 0.18 per game. In its last 10 rounds the victim moved level with
  the nearest enemy 3.1 times (theirs 0.9) and had an enemy champion in its own reach in 0.9 rounds (1.9). On b20 with
  rz20: 0.94 against 0.48.
- **Poked: hit from beyond our reach** (a shooter's basic attack or a spell, from the hitter's tile at the round start
  to the hit's tile, while we hit no champion that round). b19: 20.8 episodes per game against 10.8, and we died within
  10 rounds after 24% of them (theirs 11%); with three or more enemies within 6, 8.6 per game and 34% (3.5 and 17%).
  Our melee champions' response over the next 3 rounds (share, then P(dies within 10)): hit 0.30 (0.30), closer 0.17
  (0.20), level 0.14 (0.21), away 0.28 (0.08); theirs hit 0.43 (0.06), closer 0.10 (0.02), level 0.09 (0.12), away 0.30
  (0.05). b20 with rz20: 14.2 against 8.5 per game, 19% against 16%.
- **A single shot is small, so no shooter alone is danger.** One ranged basic hit on our melee champions took 11% of
  their max health on average (63% of those hits under 10%, 6% over 30%); ours on theirs 7%. The bot marks danger only
  around an enemy whose own one-round burst reaches 30% of our health (`knowledge.h`), so rival shooters left our
  champions working inside their reach. rz21 counts the enemies' bursts together.
- **Stuns.** They stunned our champions 20.6 times per game (Ryth 14.2, Prism 15.3, Tavi 12.1 per game in the games
  that field them), we stunned theirs 7.2 (Heart of Ruin 4.4, Marcella 3.5); 53% of our deaths had a stun on the
  victim in its last 6 rounds (theirs 31%). In the 25 five-a-side games where they field a stunner beyond Heart of Ruin
  and Marcella our deaths were 6.84 per game (3.80 stunned) against 2.76; in the 6 without, 5.67 against 2.50.
- **Not the choice of target.** When two or more of a side hit champions in a round, all hit one target in 73% of ours
  and 75% of theirs; but they have 31.2 such rounds a game against our 16.8 (`focus.py`). Next to a teammate under fire
  (enemy 3-4 tiles away) the mirror types hit as often as theirs (Heart of Ruin 0.04 / 0.10, Marcella 0.15 / 0.18,
  Vendetta 0.06 / 0.09, Vesper 0.34 / 0.40): their larger share (0.30 against 0.15) is their extra shooters (Prism 0.50,
  Willow 0.41, Tavi 0.36). Ours moved level more (1-2 tiles away 0.12 against 0.06, 3-4 tiles 0.15 against 0.10).
- **Our fights go worse at every count.** First hits after 5 quiet rounds, by enemies within 6 against our side within
  5: ahead, ours 13.4 per game (the hitter died within 10 after 7%, the target after 22%), theirs 23.7 (1%, 34%); even
  8.8 (12%, 10%) against 10.0 (6%, 19%); behind 7.2 (21%, 7%) against 5.6 (13%, 18%). Hits on carriers of 30+ gems
  (the `rich` engage) are few: 2.8 per game.
- **What our poked melee champions are doing** (probe rz21l, local against cand1, cp3, dh3, 48 games): in the turn after
  the poke `flee` 38%, `pvp` 31%, farming activities 16% (`to_capture`, `fight`, `resp_wait`, `approach`, `tribute`,
  `bank`, `retreat`). Local pokes are fewer and less deadly (dead within 10 after 12%).

## Fuel of the fight layer: mi4 and mi5 against rz20 (platform and local probes; 10-29 evening, agent)

Readers: `tools/replay/fuel_events.py` (platform `fuelExhausted` events), `decoded.py fuel`, `tools/local/fuel_probe.py` (stage fuel of a probe build; it now also reads probe builds whose PF lines have no crowd part), and the per-function `FN` lines of the probe builds mi4c, mi5c and mi6p (scratch summer, not kept).

- **Platform:** mi4 ran out of fuel after round 30 1.48 times a game on b19p (rz20 0.46) and 0.60 on b20 (rz20 0.28); with an enemy within 6, 1.1 and 0.6 times a game (rz20 0.2 and 0.2). Deaths within 5 rounds after our own exhaustion stay rare (0.04 a game). The worst map is 01yellow_brick_road (17 contact exhaustions in one b19p game).
- **Local, six heavy maps** (01yellow-brick-road, 00vault, 00stampede, 02the-pack, 02stalactites, 00swirl against cand1, cp3, dh3; 36 games each): contact turns (an enemy within 6) cost mi5 51.2k on average against rz20's 38.5k and ran out 7.6 times per 1000 against 1.85. By stage: the fight sim +6.8k, the fight branch +4.8k (on 36% of contact turns), `build_foes` +2.7k; the later stages (pick, camp fight, retreat) are where the turns run out.
- **Per function (mi5c, per game per team):** `pick_group` 16k a call (883 calls, the largest overall, as in main), `read_slots` 1,084 a call (6,615 calls: `build_foes` reads every enemy within 8 every turn), `simulate_fight` 4.7k a call (1,105 calls), `dash_landings` 2.1k, `refresh_occ` 1.9k, `step_tiles` 1.3k, `threat_at` 330, `guard_of` 85 after its cache (mi4's fuel fix).
- **mi6's `read_slots`** (the design cached once per champion, two raw host calls a slot): 478 a call, contact turns 45.0k, 5.0 run-outs per 1000 contact turns (row mi6).

## Endgame: winning bags and the rivals' last channel (rz20, cm1r and mi4 runs, ranked sets; 10-29 23:50 IST, agent)

Runs: rz20 and cm1r on b13p2, b16p, b17p and bcgp, rz20 and mi4 on b19p and b20, and the ranked sets `rk_atnam` and
`rk_mff`, decoded; a pinned game played identically by two bots counts once (472 games). Readers:
`tools/replay/winbag.py`, `tools/replay/deny.py`.

- **Winning bags** (a bag that alone lifts its team's tributed gems to 1000): we held one in 184 games and lost 13 of
  them (7%); the rivals held one in 289 and lost 9 (3%). From the first round with such a bag to its first tribute
  start: 18.9 rounds for us (median 13), 14.8 for them (median 9). Most of it is the walk (15.8 move rounds a bag for us,
  12.0 for them); camp hits 0.61 and champion hits 0.71 rounds a bag for us, 0.36 and 0.45 for them.
- **Examples.** 00dunes (rz20 on b16p): at 997 tributed our Varg captured 18 gems (a two-turn channel) and hit a camp
  until the rivals won five rounds later, because the bank stage waits while camps hit us (the `incoming == 0` gate in
  `bot.cpp`; row wn1). adgato_gemcombat2: at 973 tributed a 42-gem Vendetta paced beside the altar for 16 rounds with
  two enemies 5-6 tiles away. 02geodes (ranked against atnaM, lost 997-1002): at 997 with empty bags, four of ours
  cleared a 92-gem group, all of it went to the Heart of Ruin (a 10-turn channel), and the rivals won about 3 rounds
  before it would have completed. The reward is split among the allies on the tiles, so with four capturers each
  channel would have been 3 turns.
- **The rivals' last channel** (237 games lost before r2000): one of ours stood within 4 tiles of the winning carrier
  during its channel in 34 games (14%), within 6 in 82 (35%), within 8 in 115 (49%); counting the carrier's walk with
  the winning bag, 53 (22%) within 4. A stun cancels a channel (`docs/MECHANICS.md` section 9), so denying that channel
  is an untested lever.
- **Big bags are slow to bank.** Several of our lost winning bags were 120-470 gems (00rows 470, 01corridors 428,
  00monolith 256, 01fracture and 02uncharted_lands 200): 12-47 turns of channel, against the rivals' final bags of
  14-66 gems.

## Denying tribute channels (dl2, sc1, dl4, cd2 on b19p and b20p; 10-30 00:30-02:10 IST, session 86)

Runs `cm3m_b19p`, `dl2_b19p`, `sc1_b19p`, `dl4_b19p`, `cd2_b19p` (b19p, pinned) and `sc1_b20p`, `dl4_b20p` (b20p),
decoded. Readers: `decoded.py channels`, `tools/replay/deny.py`, `tools/replay/winbag.py`.

- **We almost never act on the rivals' channels.** With one of ours within 4 of a rival channelling 30+ gems (1.2 a
  game on b19p) we cast on the channeller in 3% of those channels; they cast on ours in 30-34%. Their near channels
  complete 61-65%, ours 54-59%; our 100+ bags complete 65%, theirs 79%. Our draft (Heart of Ruin, Marcella, Vendetta,
  Vesper, Varg) has no stun spell: the only stuns are Heart of Ruin's landing dash and Marcella's reset hit. cd2
  (hit, dash or step in on a channel of 30+ within 3 tiles) raised our share to 6% only.
- **An altar lock cancels the last channel.** dl2 (one lock bought once the rivals have tributed 600; placed only on a
  game-winning channel) fired 3 times in 48 local games and turned one loss into a win (02fields against dh3: the
  rivals' 142-gem channel at 902 cancelled at r913, we won at r917). On b19p its guards held; games lost before r2000
  33 to 29. Buying the lock at the first shop (dl1) shifted every game's item timing and raised local deaths 15%.
- **Splitting the winning capture** (sc1) acts only at the capture that completes our 1000; on b19p it matched the
  base to r1000 and cut the rounds from a winning bag to its tribute start 22.3 to 21.2.
- **The winning carrier's walk.** wn2 (a winning carrier skips kiting and duels and walks to the altar) cut the rounds
  from a winning bag to its tribute start 19.8 to 10.8 on b19p, but its camp plus champion hit rounds while holding the
  bag stayed at half the base's (5 against 10): the carrier is hit while walking.
- **Ranked close losses** (`data/fights/rk_close`, 4 games of 10-30 00:40-01:10): we held no winning bag in any; one of
  ours stood within 2 tiles of the rivals' winning carrier in one (adgato_gemcombat4) and within 6 in another.

## Where the gap is after dl4: fight starts, health, captures by region; local guard noise (session 86, 10-30 02:30-03:40 IST)

Runs `dl4_b19p@b19p`, `dl4_b20p@b20p`, `wn3_b20p@b20p`, `cd2_b19p@b19p` (main-like bots; wn3 and cd2 differ from dl4
only near the end), 197 decoded games to r1000. Readers: `decoded.py risk`, `starts`, `fights`, `types`, `items`,
`gems`, `sources`, `captures`, `holds`.

- **Economy:** collected 171 / 373 / 651 by r300 / r600 / r1000 against the rivals' 203 / 482 / 824; tributed 523
  against 644 by r1000; lost on death 60 against 28. By r600 the gap is in gem clusters (146 against 195) and elks
  (105 against 139).
- **Captures by region (r1000):** our own half level (27.8 captures, 381 gems, against 28.9 and 387); the middle 8.9
  (187 gems) against 11.1 (257); the other side's half 1.8 (27) against 4.9 (69). Our capturer takes 87.8 rounds
  between captures (median 64) against 69.6 (48), with 52.8 moves against 43.6.
- **Fights:** by r800 the rivals start 27.3 champion fights a game, we 14.9; 3.1 of our 4.2 deaths by r800 come in
  fights they started. Above half health our P(death within 10 rounds) is about twice theirs in every cell of enemies
  and allies within 6 (alone against one: 0.033 against 0.017; against three: 0.186 against 0.088); below half health
  the two sides are close (alone against one: 0.167 against 0.146).
- **Per champion type (r1000):** the rivals' Vesper collects 285 gems a game against ours 146 and deals 4840
  champion damage against 3393; their Marcella 5538 against 4036. Our Varg deals 1098, the least of any champion on
  either side. Max health at r600: Marcella 1888 against the rivals' 2200, Vesper 1949 against 2113.
- **Ranked, 100 games before 02:35** (`data/ranked100.txt`): 57 won. Lost in every recent game: 01islands (0 of 3,
  562-1002, 659-1004, 810-1002), adgato_gemcombat4 (0 of 3), 01boss_battle (0 of 2, 0-1103 and 162-1014).
- **01islands locally** (6 deterministic games a bot against cand1, cp3, dh3): main wins 1, earlier mains nm2 to mi5
  win 4 (collected 936-1028 a game against main's 909); cm3m 3, dl2 2, sc1 1. Not separated from the spread of
  near-identical bots on six games (row ns1).
- **Local guard noise** (rows nop1 / nop2, dl3's 10 maps against cand1, cp3, dh3): a fuel-only change of a few hundred
  fuel a turn moves main's 49 wins and 141 deaths to 50 and 135, so the guard bars (47 wins, 155 deaths) sit above
  noise; every mid-game change tested tonight raised deaths past them (pk1 160, mi7 173, cm4 181, wl1 193). Burning
  about 25k fuel a turn (nop1) gives 38 wins and 260 deaths, and an exact fuel saving (mi7, 0 mismatches) also moved
  deaths to 173: play depends on fuel through the fuel-gated picks and travel fields.

## Quiet and loud games, idle rounds beside a hit teammate, big channels (session 86, 10-30 04:00-04:20 IST)

Runs `dl4_b19p@b19p`, `dl4_b20p@b20p`, `dl4f_b19p@b19p` (main = dl4), 144 decoded games to r1000, split by deaths of both
sides by r1000: "quiet" at most 4 (43 games), "loud" the rest (101). Splitter: scratch, copies the games into
`data/fights/q_split/{quiet,loud}` with their index lines; then `decoded.py gems`, `captures`, `sources`, `channels`.

- **Loud games carry the economy gap.** Collected by r1000 537 against 783 (69%), tributed 420 against 651, lost on death
  77 against 23, deaths 7.8 against 4.7. Captures 34.7 against 43.1: our own half level (23.6 against 24.1), the middle
  9.5 against 12.5, the other side's half 1.6 against 6.5 (93 gems a game: the rivals take our groups). Won 27 of 101.
- **Quiet games are close but still lost.** Collected 818 against 885 (92%), tributed 687 against 653, but the rivals
  hold bags of 224 at r1000 against our 104 (tributed plus bag 791 against 877) and win with late big tributes. Won 10
  of 43. Lost quiet maps: 02geodes, 01big_world, 00monolith, 00expanse, 00collision (3 each). By camp type the rivals
  take more elk (303 against 261), wolf (159 against 124) and monolith gems (48 against 23).
- **Big channels break.** In quiet games our channels over 100 gems complete 59% (1.0 a game, 172 gems started, 87
  banked), theirs 83%; per channel turn with 1 or 2 enemies within 10 of the altar ours break at 0.015 and 0.026, theirs
  at 0.006 and 0.007. With an enemy within 4 of our channeller (1.47 a game) 56% complete and an enemy casts on the
  channeller in 24% (theirs 0.74 a game, 69%, 3%). `bank_gems` (`targets.h`) walks to the nearest altar and channels
  whatever enemies are near.
- **Idle beside a hit teammate.** A healthy (60%+) champion with an enemy within 4 and a teammate within 6 hit this
  round stands still (no hit, no camp hit, same distance) 12.7 rounds a game against 7.7 (scratch reader on
  `decoded.py assist`'s cases). The difference is rounds with no action at all, off a capture or channel and not
  parked: 5.1 against 1.6, spread over all five of our types (0.7-1.3 each; the rivals' 0.03-0.43). The rivals field
  more stuns (Ryth, Tavi, Ren, Prism); the earlier Vesper reader found half of her no-action rounds near enemies had a
  stun cause.
- **Item timing moves deaths.** cap1b (Capture as the second emblem, in place of a Power or Bruiser one) raised the
  local deaths from 141 to 201 on dl3's 10 maps while captures rose 46 to 48 a game: one emblem of fight stats less in
  the mid-game costs about one death a game against our own pool.
- **What our champions do when a fight is opened on them** (scratch reader on the `defend` cases: the first hit of an
  enemy on a healthy (50%+) champion after 15 quiet rounds between the pair, 147 games of dl4 on b19p and b20p, to
  r1000; per game, P(the victim dies within 10 rounds) in brackets): already in a fight with someone else (a hit
  either way in the 5 rounds before) 12.14 (0.28) against the rivals' 6.89 (0.13); walking 10.61 (0.16) against 5.76
  (0.10); hitting a camp 3.24 (0.11) against 1.37 (0.10); standing 2.15 (0.20) against 0.67 (0.15); in or just after a
  channel 1.23 (0.14) against 0.90 (0.09). By numbers within 6 of the victim: outnumbered 12.10 (0.31) against 5.52
  (0.17), even 8.99 (0.16) against 4.82 (0.12), ahead 8.30 (0.11) against 5.24 (0.05). The largest share of our deaths
  is pile-ons: a further enemy joining a fight we are already in.

## Pinned panels are deterministic (session 86, 10-30 05:00 IST)

The same bot on the same pinned panel plays the same games: main (mi8) gated as `mi8_b19p` (03:46) and again as
`mi8g_b19p` (04:39) gave identical raw results (12 of 50, our gems 31090 against 46992, deaths 446 against 271), and so
did `mi8_b20p` (03:53) and `mi8g_b20p` (04:55) (18 of 50, 36240 against 41487, deaths 235 against 240). On a pinned
panel the base therefore needs no fresh run in the same session: any earlier run of the same bot on that panel is the
same set of games, as long as the engine and the pinned opponents do not change. Each variant then costs 10 groups per
panel instead of 20. Non-pinned panels still need a same-session base (the opponents change their bots).

Still exact seven hours later (10-31 09:47 IST): bb2 gated on b28p at 09:43 (`main_b28p@b28p`) gave the raw result of
its 02:58 run on b28 (`main_b28@b28`: 20 of 50, our gems 37896 against 44571, deaths 323 against 212). The check was
run because none of the 13 variants gated on b28p since 03:17 (kb5 to fr1) passed its rule; the base is exact, so
those verdicts stand.

## The rivals' Vesper farms, ours hands her groups over; massacres; 01boss-battle skews local screens (session 86, 10-30 11:12 IST)

Main = bb2 on its pinned runs `bb2_b19p@b19p`, `bb2_b20p@b20p`, `bb2_b21p@b21p` (150 games), to r1000 unless noted.

- **Deaths are no longer the gap.** By round band our deaths per game are level with or below the rivals' (r0-100 0.41
  against 0.46, r500-1000 2.16 against 2.57). Collected 742 against 833 and tributed 576 against 632 remain. By the camp
  type last hit (`decoded.py sources`): gem clusters 266 against 308, elks 225 against 254, monoliths 9 against 36; gold
  clusters 109 against 96. Team gold is ours by 8% at r1000 (5324 against 4917): we still trade gems for gold.
- **The gap by champion type is the Vesper** (`decoded.py types`, `champs`): their Vesper collects 296 gems a game against
  our 164, holds 1080 camp gold at r600 against our 704 (level at r200: 266 against 232), and deals 166 damage a round to
  camps against our 120 at r1000, about her 38% more strength (bruiser strength 6.5 emblems a Vesper at r1000, plus
  Monster, Jungle, Prospector and Capture of strength; ours builds Durability and Jungle of health). The other shared
  types are level (Heart of Ruin 154 against 146 gems, Marcella 232 against 215, Vendetta 149 against 158).
- **Our Vesper hands her groups over** (`tools/replay/handoffs.py`, to r600): she is the top hitter on 8.0 groups a game and
  a teammate captures 3.7 of them (401 gold); she takes 2.2 (286). The rivals' Vesper hands 1.6 and takes 3.1 a game she
  plays. Our claim rules give a dead group to the claimant with the fewest shards. Counting Vesper's shards at half (vw1)
  moved locally about 650 gold a game to her from the other four, whose deaths rose; at three quarters (vw2) 270 gold.
- **Own-half small gem groups** (`capkind.py --permap gem:own`): on some maps the rivals take their own half's pure gem
  groups three to ten times as often as we take the mirror ones (00gemfight 6.3 against 24.8 a game, 02fields 2.5 against
  21.5, 02arena 2.0 against 13.6, 00gem_fields 7.3 against 21.7, 01shortcut 0 against 13); in all, 2.9 against 5.4 a game.
  On 00lost_world the rivals park in the centre ring of eleven small gem groups (57-75 captures by r600) after winning
  the opening fight at the left edge, while we farm our own corner groups and never go back.
- **Massacres** (`deathfactors.py`): 20 of the 150 games (our deaths minus theirs 6 or more), none won; our deaths 13.0
  against 2.6, team gold at r300 744 against 1261 (in the 115 even games 1241 against 1038, deaths 2.17 against 5.37,
  63 wins). In them 52% of our deaths come in flight, 75% after the killer was in view for 11-30 rounds, 44% with no
  teammate within 6; Marcella is the killer in 59%. Opening fights (deaths to r120) are even on average: we win 34 and
  lose 27 of them, and win 59% and 19% of those games.
- **01boss-battle skews local screens.** Its boss pays thousands of gems, so one local game can collect 16,590 gems and
  lose 14,668 on death. In the vw2 screen it alone raised collected from 1037 to 1138 a game and lost on death from 36 to
  125 (bb2's screen: 1037 and 35 without it, 1070 and 59 with it). Read local collected and lost without 01boss-battle.

## Ranked massacres are enemy balls; test bots on the ladder; steals (session 86, 10-30 14:00 IST)

Sources: our 64 newest ranked games of 10-30 decoded in `data/fights/rk1030` (downloaded with `tools/replay/qmaps.py`, index
built from the ranked listing), main = bb2's pinned runs `bb2_b19p@b19p`, `bb2_b20p@b20p`, `bb2_b21p@b21p` (150 games), to
r1000. Readers: `tools/replay/deathfactors.py`, `tools/replay/steals.py`; scratch `balls.py`, `mtrace.py`, `rk_drafts.py`.

- **All ranked losses with a death gap are lost games, and they are 22% of ranked games.** Of the 64: 9 massacres (our
  deaths minus theirs 6 or more by r1000) and 5 mixed (3-5), none won; 50 even games, 30 won (60%). In the 60 ranked games
  to 13:30, 14 were massacres; the rivals' champion damage in them was 1.8 times ours (48.4k against 27.4k) and their gold
  2.8 times (`rk_drafts.py`).
- **They start early, in the middle, in a first life.** In the 9 massacres our deaths by r300 are 3.8 a game against 1.8
  (even games 0.9 against 1.6): 91% in a champion's first life, 68% in the middle, 79% begun while we outnumbered at the
  contact's start, 76% with 4+ enemies within 6 during the contact, 74% with 3+ killers.
- **The rivals move as one ball.** Rounds r50-600 with four or more rivals within 4 of one of them and one of ours within 8
  of it: 15% in ranked massacres, 5% in even games (bb2's panels: 14% and 5%). Our own team is such a ball in 7% of
  massacre rounds against 13% in even games (panels 5% and 19%). Trace (adgato_gemcombat4 against shoutout MAPS,
  `mtrace.py`): the five rivals stay within 2-3 tiles of each other from r40 and park at a middle group; our Varg, Heart
  of Ruin, Vesper and Vendetta walk up one at a time at full health, keep working while the ball stands 6-7 tiles off,
  and die in its reach; the Heart of Ruin returns 20 rounds after its respawn and dies there again. Tested as bv1.
- **Test bots on the ladder lost more.** Ranked sets are created every 10 minutes at :x0:05 and play out within a minute.
  Each gate submits the bot under test for 3-6 minutes, so 23 of the 80 ranked sets of 10-30 to 13:50 were played by a
  test bot: 51 wins in 115 games (44%), against 154 in 285 (54%) for the sets played by main. Since 13:51 `gateq.sh`
  uploads a test bot only from :x1:00 to :x2:59 (of 400 ranked games 375 were created at :x0:00-:x0:09, 20 at :x0:10-:x0:49 and 5 at :x2:0x; each finishes 30-90 seconds after its creation), so the ranked sets are played by main.
- **Steals** (`steals.py`, bb2's panels): the rivals captured 1.45 of our kills a game (36 gems, 145 gold), we 0.82 of theirs
  (21, 94). At the kills they stole one of theirs was within 6 of our nearest champion in 80%; our nearest was on the
  tiles 3 rounds later in 23% against 65% for the kills we kept. Groups where we dealt half the damage or more and the
  rivals captured: 1.63 a game (42 gems, 166 gold) against their 0.97 (32, 112). Tested as cs1.
- **Willow games are level on deaths now** (bb2's panels, scratch `willow.py`): with a rival Willow our deaths 5.51 a game
  against their 5.66 (47 games, 18 won); without Willow or Tavi 3.78 against 4.20 (94, 42 won). The 10-29 gap (5.23
  against 3.41) is gone, so the fight simulation's missing heals were not tested.
- **In massacres every meeting is deadlier for us, whatever the count** (rk1030, 64 ranked games to r1000, scratch
  `ovview.py`; an episode starts when a champion off its spawn has two or more enemies within 8, more than its own side
  within 6, the nearest 3+ away). In the 9 massacres (death gap 6+) ours had 70 episodes a game and died within 20 rounds
  after 20% of them; the rivals 43 and 5%. By count: one of ours against two 0.15 (theirs 0.02), two against three 0.27
  (0.02). In the other 55 games the two sides match: 47 episodes each, 9% against 11%. So the massacre opponents win
  fights at any count, and fewer meetings, not better counts, is the lever. Three or more of our deaths by r200 marked 5
  of the 9 massacres and 1 other game; four by r300, 5 and 2; four by r400, all 9 and 8 others (scratch `early.py`).
  Tested as ow1.
- **Enemies just out of view rarely explain a surprise** (rk1030, scratch `ghosts.py`, `warn.py`): of our 111 deaths to
  r1000 in massacres, 60 began (first enemy within 4) already outnumbered in view and 23 began level and ended
  outnumbered. Of those 23, a memory of each enemy seen within 8 in the 12 rounds before would have flagged 6, and a
  ball (four or the whole team within 4 of one) seen within 10 in the 30 rounds before only 1 (bv2's rule). Of the 60,
  the first outnumbered view came 3 or more rounds before the contact in 33, and the victim had walked toward the enemies
  in 24; bv1's ball condition held at that first view in 11.
- **The massacre rivals travel in threes, and even our winning counts die** (rk1030, scratch `meet.py`; a meeting is the
  first enemy coming into view, within 8 and 3+ tiles off, after a round with none, keyed by enemies within 8 against our
  side within 6). In the 9 massacres the rivals met one of ours with three or more of theirs within 6 50 times a game (we
  18). Our death within 20 rounds after a meeting with one enemy in view: alone 0.09 (theirs 0.03), with one teammate
  0.11 (0.03), with two 0.09 (0.01). In the other 55 games the rates match (0.02-0.03 for us, 0.03-0.06 for them). So in
  massacres the one enemy in view is the front of a group: ow1's outnumbered rule fires only once the rest is in view.
- **The whole economy gap sits in the games where we die fast** (bb2's 150 pinned games, b19p + b20p + b21p, to r1000;
  scratch `caution.py`). ow1's trigger (our deaths at least 3 + one per 100 rounds after r200, at some round to r1000)
  holds in 37 games: we won 7; our deaths 11.1 a game against their 5.9; collected 472 against 852; tributed 305 against
  669. In the other 113 games we won 58; deaths 2.0 against 4.6; collected 830 against 827; tributed 665 against 620. So
  outside those games our economy is level with the panel's rivals, and a quarter of the games decide the gap. The
  trigger selects on deaths, so the gems follow partly by construction; the size of that group is the finding.
- **Stunners mark the fast-dying games** (bb2's 150 pinned games plus the 64 ranked games of rk1030, 58 caution games
  against 156; scratch `cautdraft.py`): the rivals field Tavi in 36% of the caution games against 15% of the rest, Ren 12%
  against 6%, Prism 19% against 8%, Willow 38% against 28%, Marcella 97% against 86%; Heart of Ruin 50% against 75% and
  Vendetta 50% against 63%. With a Tavi on their side 47% of games become caution games (all games: 27%).
- **Fast-dying games start with lost middle brawls** (same 214 games, scratch `earlyd.py`, deaths before r250): in the
  caution games we die 2.84 times a game before r250 and the rivals 1.69 (other games 0.43 against 1.00). 56% of those
  early deaths of ours are in the middle; at the death four or more enemies stand within 6 in 44% (theirs 31%) and none of
  ours in 33% (22%). The victim had 76% of its health ten rounds before and was hitting camps in 19%.

## Leaving does not save champions; five a side and twelve bad maps (session 86, 10-30 16:00-17:20 IST)

Sources: bb2's pinned runs `bb2_b19p@b19p`, `bb2_b20p@b20p`, `bb2_b21p@b21p` (150 games, to r1000), the judges of bv1, ow1 and
rh1 (`data/judge_*.txt`), and our ranked listing (`cambc matches list --team ... --kind ranked --json`, 700 games from 10-29
17:00 IST, saved as `data/ranked_list.json`). Readers: `tools/replay/caution.py`, `deathfactors.py`, `capkind.py`,
`decoded.py sources`, `budget.py`, `bysize.py`; scratch `cgold.py`, `vearly.py`, `oppc.py`, `otrace.py`, `rtrace.py`.

- **Walking home from a seen threat does not cut deaths.** bv1 (leave a seen ball) and ow1 (leave when outnumbered in
  view, once our team dies fast) both missed their deaths targets on 150 games (+0.41 and +0.04 a game) and cut our kills;
  bv1 grew the massacre games from 20 to 29. In the caution games 56% of our deaths already came while walking home.
  rh1 (a help call on any lone raider on our half) raised our deaths by 0.65 a game.
- **Caution games start in the first 100 rounds.** In the 37 caution games we had died 0.5 times by r50 and 1.2 by r100
  (other games 0.0 and 0.2); the rivals' team gold there is the same as in other games (r300: 1086 against 1087), ours
  falls behind (875 against 1262). Before r150 we die 1.73 times a game there and the rivals 1.14, in team brawls (three
  or more enemies within 6 at the first hit in 48% of our deaths, two or more of our allies in 41%). The caution games
  are spread over the panel's teams (Sheeesh--- 7 of 10, the others 1-3 of 10). Trace (01gold_rush, b19p): our Heart of
  Ruin kept hitting a middle camp group with three rivals 3-5 tiles off, fled through the camps' reach under the rival
  Vesper's shots and died at r50; our Vendetta and Vesper then walked in one at a time and died by r60 without a kill.
- **Five a side is the weak size.** On the panels we won 33 of 90 five-a-side games (3- and 4-pick 32 of 60); ranked since
  bb2 45 of 100 against 50 of 85. Five a side we collect 792 a game to r1000 against 909 and tribute 620 against 676, with
  fewer deaths (3.8 against 4.5). By r600 the gap is gem-cluster gems (`decoded.py sources`: 134 against 188 a game; elk,
  wolf, gold and golem gems level). Pure gem-cluster groups: 3.2 captures a game against 9.4 five a side, 6.9 against
  12.3 four a side, 13.5 against 20.4 three a side. Both sides hit camps in 18-19% of champion-rounds (`budget.py`).
  og1 (take a harmless gem group within a 3-tile detour) added five small captures a game locally, but collection stayed
  level (+0.3%) and deaths rose 28%.
- **Twelve maps hold a fifth of our ranked losses.** Of 700 ranked games (51.3% won), adgato_gemcombat5 0 of 7,
  01starvation 1 of 10, 01boss_battle 1 of 9, 00expanse 1 of 8, 00ambush 1 of 7, 02harvest 1 of 7, 01corridors 2 of 10,
  02famine 2 of 10, 01fracture 2 of 8, 00ribs 4 of 15, 00split 3 of 11, 00vault 2 of 7: 21 of 119 together. On the panels
  we tribute nothing in our 00ribs and 01boss_battle losses (0 against 985 and 993; 0 against 880 and 627); 00split is lost
  on its golem groups (214 gems each: 2.6 captures a game against 4.4), 01starvation and adgato_gemcombat5 to massacres
  (deaths 25/0, 17/2, 12/3, 9/3), and 00expanse, 00ambush, 02harvest and 02famine by close races (we end at 800-990).

## Hoarders and giant channels; the band above us (session 86, 10-30 17:30-18:15 IST)

Sources: bb2's pinned runs `bb2_b19p@b19p`, `bb2_b20p@b20p`, `bb2_b21p@b21p` (150 games, to r1000), pz1's runs on the same
panels, the new panel `b22` (five teams ranked 20-39, 2066-2162 at 17:46; base `bb2_b22@b22`), our ranked listing (735 games
since 10-29 17:00) and the ranked listings of the top 10 teams. Readers: `decoded.py types`, `champs`, `starts`, `items`,
`byteam.py`, `deathfactors.py`, `deathspots.py`; scratch `prismbag.py`, `teamtrib.py`, `carry.py`, `chan.py`, `bigtrib.py`.

- **SilverSamurai hoards in its Prism.** On b20p (10 games) their Prism collects 781 gems a game to r1000 (our whole team
  742) and never tributes before the end: 0 bag drops while alive, mean bag 300-470, then one channel of 887-1157 gems
  (bag / 10 turns, 89-116 turns; gems captured during the channel join it). Their other four hit camps beside her and
  capture nothing (0 gems each); their Willow stays within 3 tiles of her in 70-80% of rounds. Her focus grows 1.5 a gem,
  so at 500 gems her damage spell deals about 1250 and her area spell 830: camp damage 218 a round of hitting (ours at
  most 115). We won 3 of 10. In 00monolith our five stood 20-47 tiles from her during her 75-turn final channel, and none
  held an altar lock: we buy one only once the rivals have tributed 600, which a hoarder never does before the end.
- **Giant bags decide a tenth of the panel games.** In 16 of bb2's 150 games a rival ended with a bag of 300+ or tributed
  300+ at once; we lost 14. Besides SilverSamurai (8 games) they are the guard maps (01boss_battle, 02guardians: the altar
  opens late and the first long channel wins) and two single channels of 235-330. dn1 (row dn1) acts on these.
- **Our Prism is not their Prism.** pz1 (Prism for Varg, five a side) collected 118 gems a game with 1.09 deaths (Varg 155,
  0.89): ours banks like the other four. Team collection fell 3.7%.
- **The top 10 draft the meta we draft.** Five a side: Heart of Ruin, Marcella, Vendetta, Vesper plus one of Ryth (four
  teams), Tavi (Mite, hello), Cassi and Issac (prism best girl, Intercontinental Fish) or Ren (Ad Astra). prism best girl
  (rank 1) plays Vesper, Vendetta, Heart of Ruin, Cassi and Issac on four-pick maps too. None of the top 10 hoards.
- **The band above us is far above us.** Ranked since 10:00 IST on 10-30, by the opponent's rating at 17:46: under 1950 we
  won 24 of 40, 1950-2000 63 of 115, 2000-2050 29 of 65, 2050-2100 1 of 5. On b22 bb2 won 12 of 50: procless (2162) 1 of
  10 (deaths 8 against 2 a game, collected 429 against 917), Rogue Lock Pickers 1 of 10, Jupiter 3, 0xDEADBEEF 3, Let's
  LARP again 4. procless starts 42 champion fights a game (we 28), outnumbered in 48% of them, and wins them: in the fights
  it starts we lose 4.4 champions a game and it loses 0.7, though more of ours stand within 6 (2.47 against 2.00). At r400
  their Heart of Ruin and Vendetta hold 1690 and 1830 health (Prospector, Jungle and Bruiser emblems of health), ours 870
  (Treasure first; ours die more and so hold less). Across b22, 10 of 50 games are massacres (our deaths minus theirs 6+;
  1 won; team gold at r300 680 against 1296); in them two thirds of our deaths come while we are even or outnumber them.

## The band above us: more small captures, Prospector and Bruiser builds (session 86, 10-30 18:40-19:23 IST)

Sources: bb2's base runs on the two panels of teams rated above us, `bb2_b22@b22` and `bb2_b23@b23` (100 games, ten teams
ranked 20-39, 2072-2175 at 18:25), to r1000 unless noted. Readers: `tools/replay/waste.py`, `clears.py`, `early2.py`,
`handoff2.py`, `byteam.py`, `budget.py`, `decoded.py items`, `captures`, `sources`.

- **We win 27 of 100; the economy decides even when the fights do not.** We collect 596 gems a game to r1000 against
  791 and tribute 456 against 654. By opponent, ひななー collected 1042 against our 589 with deaths level (5 and 5) and
  took 154 gems a game from our deaths (we 64); Let's LARP again 768 against 562 with fewer deaths than ours (4 and 3).
  With our deaths by r300 level with theirs we won 5 of 31; with 3+ more 1 of 14; with 2+ fewer 9 of 14.
- **Same time budget, 28% more captures.** Both sides hit camps in 19% of champion-rounds to r300 and walk about 45%
  (`budget.py`). To r1000 they made 50 captures a game against our 39, with about the same claim time (9 rounds) and
  hand-offs (`handoff2.py`). To r600 they dealt 4% more camp damage (40.4k against 37.4k a game) and took 390 gems and
  2100 gold against 306 and 1890: 16% more gems per camp damage, gold per damage level (`waste.py`). In Let's LARP
  again's and Jupiter's games they took 1.7 and 1.5 times our captures of groups under 200 health and cleared alone in
  70% of their captures (we 51-53%; 3+ hitters 6-10% against our 21-25%, `clears.py`).
- **Their builds: Prospector first, then Bruiser and Jungle of the main stat.** At r250 their Vesper holds 0.45
  Prospector-strength emblems, their Heart of Ruin and Vendetta Prospector-health shards (0.37, 0.34), their Ryth and Tavi
  Prospector shards (0.59, 0.77); ours hold Treasure (0.34-0.68 emblems). At r600 their Vesper holds 2.77 Bruiser-strength
  emblems and no Power (ours 1.05 Power, 0.45 Bruiser), their Marcella 1.01 Bruiser-focus (ours 1.35 Power-focus), and every
  type holds Jungle of the main stat (0.44-0.66) where ours hold Jungle of health (0.57-0.80). Tested as ib1 and ib2.
- **Early deaths:** rounds 100-300 cost us 1.12 deaths a game against their 0.69 (r0-100 level, 0.35 and 0.31). Tested
  as hg2 (hold before a middle group they hold).
- **Five a side the gap is the middle, not our own half** (bb2 on b22 + b23, the 47 decoded five-a-side games, to r1000,
  `decoded.py captures` and `lives` on those games only): captures in our own half 30.0 a game (373 gems) against their
  30.6 (371) in theirs, but in the middle 6.8 (151 gems) against 13.1 (308) and in the other side's half 1.5 against 4.5.
  Of the 21.3 middle group lives a game they hit first 12.7 times and we 7.8, at the same delay after the group comes up
  (median 15-16 rounds); steals are rare (0.9 by us, 1.2 by them). So they reach more middle groups, and do not take them
  from us in fights. Their capture cycle is 75 rounds a capturer (moves 47) against our 98 (60). Removing our death
  discount on contested groups (dr0p, 10-30) sent us back to the middle and cost +0.74 deaths a game with no more gems, so
  the middle follows fight strength.
- **ib1's items cut five-a-side deaths most** (`bysize.py`): five a side our deaths fell from 5.08 to 4.19 (b22p) and from
  6.56 to 5.78 (b23p); three and four a side they moved by less than 0.4.
- **Blowout losses are gold snowballs** (our last 40 ranked games before 19:50 IST on 10-30, 16 won; `ranked.py`,
  summaries in `data/summaries/`): 8 losses with 9-24 of our deaths, spread over every champion (e.g. 00reverse_spiral
  against Rogue Lock Pickers, 24 deaths to 1). In three of them the opponent earned 2.4k-7.2k gold against our 0.9k-2.5k
  (1.6 to 7.9 times ours). At the end their champions held Durability of health, Treasure of health and Jungle of strength
  emblems (𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 on 01starvation and 00galaxy), then Bruiser of strength or health (Rogue Lock Pickers on
  00reverse_spiral: 2-9 Bruiser emblems a champion by r1127, plus Capture and Prospector; their Vesper on 01starvation
  11); ours held Treasure of the main stat and Jungle of health.
- **Five a side we die more in the same situations, and are stunned more** (bb2 on b22 + b23, the 47 five-a-side games,
  to r1000; `bysz.py 5 decoded risk|starts|defend`, `bysz.py 5 budget 1000`, `stillstun.py 5`):
  - Time budget: the same shares walking (34% against 35% with an empty bag) and idle; camp hits 15.5% against 17.3%;
    dead 7.8% of champion-rounds against 4.7%.
  - We spend about as many rounds as they do in each state of enemies and allies within 6 and health, but at health above
    half we die within 10 rounds 2-2.8 times as often (two enemies and no ally: 0.072 against 0.028; three enemies and one
    ally: 0.113 against 0.040).
  - They start 36.2 fights a game and we 21.5, with the same numbers within 6 of the target (2.60 against 2.50 for them,
    2.59 against 2.55 for us); fights they start kill 3.66 of ours a game, fights we start 1.28 of theirs.
  - After a fight starts on one of our champions at half health or more, it takes no action in 28 rounds a game (theirs
    12); 58% of ours come right after an enemy cast on it (likely a stun), 36% of theirs. Their fifth pick is a stunner or
    healer (Ryth in 24 of 47 games, Willow 17, Tavi 15) where ours is Varg (the Varg swaps ry1, ta1, wl1, ry2 and pz1 were
    all rejected); their Marcella casts her stunning reset 29 times a game to our 24; the other types' cast counts match.
- **Not the cause five a side** (same 47 games, scratch reads of the decoded rows): unspent gold per champion is lower
  than theirs (42 against 57 at r400-600), so gold does not sit idle; our items are worth 9% less (431 against 475 gold
  at r400-600, 687 against 758 at r600-800) from lower income. Focus fire is level: in rounds with two or more of a side
  hitting champions, ours hit one target in 76% (theirs 67%), the lowest-health one in 87% (85%); they have 47% more such
  rounds. With a teammate hit and the nearest enemy 3-4 tiles away our healthy champions stand still in 33% of rounds
  against their 18% and hit in 16% against 26% (`bysz.py 5 decoded assist`), the gap as1 and ja1 targeted (both rejected).
- **What ib1's items change five a side** (ib1 on b22p + b23p against bb2's runs, the 47 five-a-side games, to r1000):
  P(death within 10 rounds) at health above half with one enemy within 6 falls to the band's level (no ally 0.016
  against bb2's 0.024 and their 0.015; one ally 0.011 against 0.016 and 0.009); with two or three enemies it stays 1.6-2.7
  times theirs. Deaths fall after r300 (r300-500 0.92 against 1.07 a game, r500-1000 2.41 against 2.70), not before
  (`early2.py`). Middle captures barely move (7.5 against 6.8 a game; theirs 13.6), so the middle gap stays.
- **Our Vesper buys health, theirs strength** (bb2 on b22 + b23, all 100 games, to r1000; `tools/replay/perhit.py`, the
  damage of a lone hit on a champion): our Vesper's median basic hit is 65 at r0-299, 70 at r300-599 and 135 from r600;
  the band's 65, 112 and 182 (five a side on b22-b24 the same: 70 against 110 at r300-599). The other types' hits match
  (Heart of Ruin, Marcella's spell; Vendetta within 15%). At r400 (`decoded.py items`) ours holds Jungle of health 0.70 and
  Durability 0.57 emblems against about 1.4 strength emblems; theirs about 2.3 strength emblems (Bruiser 0.67, Jungle 0.53,
  Treasure 0.42, Prospector 0.39) and 1517 max health to our 1683. Both fire about 24 shots a game five a side
  (`decoded.py shots`), so the damage gap (4339 against 3233 a game) is the size of the shot. Our shop formula weighs a
  health emblem by health growth over max health with a first-emblem bonus (Jungle +0.15, Durability +0.11), which beats
  any strength emblem for her after Treasure. ib1 (Jungle of the main stat on every type) raised her median from 70 to 90.
- **Five a side the gem gap is middle gem clusters** (bb2 on b22-b24, 75 five-a-side games, to r600;
  `tools/replay/gclass.py 600 5`): gems gained on cluster-only groups in the middle 81 a game for the band (3.7 gains)
  against our 33 (1.0); in our own half 26 against 24; mixed groups (wolves, elks) 311 against 295. `decoded.py sources`
  agrees: gems after a gem-cluster hit 202 against 105, elk 143 against 145, wolf 77 against 84. Both sides hit camps
  about 600 times a game by r600. A cluster has 120 health and no strength.
- **Our Heart of Ruin dies after its engaging dashes** (same games; scratch readers on slot-1 ground casts that land
  within 3 of an enemy and nearer than before): 2.57 a game at 80%+ health for us, 2.95 for them, with the same targets'
  health, numbers within 6 and kill rate (0.09 against 0.12 within 5 rounds), yet our Heart dies within 10 rounds after
  9.3% of them, theirs after 0.9%; it loses 129 health in the next 3 rounds against their 93, also at base health
  (1000-1099 max: 7.7% against 2.0%). hb1's extra health did not change Heart deaths (1.50 against 1.48 a game). In
  traces, their champions hit our Heart at once, while ours next to their Heart often hit nothing for 4-6 rounds.
  `decoded.py defend`: fights are started on our champions 27.9 times a game against 16.6 on theirs, and in the next 6
  rounds ours hit a champion in 23-37% of rounds by type, theirs 34-47%.

## Where the time and the deaths go (session 86, 10-30 22:00-23:11 IST)

Sources: bb2's pinned runs on b22, b23, b24 (five a side 75 games) and b25 (three a side), to r600 unless stated; readers
`tools/replay/capcycle.py`, `tools/replay/stateact.py`, `decoded.py risk|shots|champs|captures|items`, `waste.py`; scratch
`quietecon.py`, `timeuse.py`, `responder.py`, `supporter.py`, `opening5.py`.

- **The death gap is there before items differ.** To r300, at health above half, P(death within 10 rounds) is 0.083
  against 0.040 with two enemies and no ally within 6, and 0.090 against 0.040 with three enemies and one ally.
- **Near enemies but out of reach, ours drift.** With 1-3 enemies within 6 (health above half) ours make a move that
  neither closes nor opens the distance in 13-20% of rounds (the band 6-9%) and stand idle in 16-25% (11-16%); ours hit
  champions in 9-22% (13-36%). When ours hit a champion with two or more enemies near they die within 10 rounds 2-4 times
  as often. With an enemy in basic reach both sides hit in about 80% of rounds (`decoded.py shots`), so the gap is outside
  reach.
- **Between captures we walk more, away from enemies.** Our capture cycle is 80 rounds against 61 (same straight hop,
  12.6 tiles; same share of intervals with a tribute, 0.33 against 0.32). Per interval: dead 4.6 against 2.5 rounds,
  camp hits 15.6 against 11.3, moves 42.5 against 32.8, of which 33.7 against 25.8 with no enemy within 6, idle 14.1
  against 11.6. The extra walking is not near enemies; its cause (target switches, walks to groups a teammate captures,
  bank detours) is not measured yet.
- **Three a side we lose the economy even without fights.** In the 43 three-a-side games where both sides died 0-2 times
  by r600 we collected 328 against 387 and tributed 229 against 331. Our champions hit camps more (Heart of Ruin 27% of
  rounds against 19%), the team's camp damage is level (38.5k against 37.6k), but gems per 1000 own-capture damage are 7.8
  against 8.9 and gold 2006 against 2395; their Vesper hits camps for 145 a round alone to our 99 and makes 16.4 capture
  events to our 10.9. Five a side in quiet games: 399 against 429.
- **Their Vesper is a gold carry.** Five a side by r600 their Vesper makes 10.8 capture events for 1055 camp gold, ours 6.9
  for 637; at r600 she holds 2.55 Bruiser-strength emblems and 2120 max health (ours 1986) and dies 0.55 times a game by
  r1000 (ours 1.31). Their Marcella too: 11.9 events, 812 gold (ours 7.3, 567).
- **Heart of Ruin dives:** when ours lands, our allies within 6 hit camps in 8% of rounds at 2 tiles or less (theirs 1%)
  and close in 16% against 25%; when theirs lands on us, our defenders at 2 tiles or less hit it as often as theirs do
  (50% against 52%).
- **vp3's bigger Vesper hits farm, not fight.** Her median hit 70 to 95 raised collection by r600 by 3.8% and team camp
  damage by 3.4%, but her kills fell from 0.60 to 0.39 a game and her champion damage by 7%: with less health she shoots
  less. Health is also what lets the band's Vesper keep shooting.
- **Ranked by team size** (our newest 200 ranked games, 10:10-16:40 IST): three a side 15 of 33 won, four 36 of 54, five
  52 of 113.

## Pinned panels, team sizes and the Vesper build (session 86, 10-30 23:30 to 10-31 01:21 IST)

- **A pinned panel replays exactly.** `main_b24p@b24p` (00:21 IST) and `main_b25p@b25p` (00:32) gave the games of
  `bb2_b24@b24` (20:16) and `bb2_b25@b25` (21:03) to the last gem: same wins, gems and deaths. A base run on a pinned
  panel is never stale, and a fresh one only spends quota.
- **b22p, b23p and b24p mix team sizes** (`data/map_sizes.json`; 00ribs, 02crossing and adgato_gemcombat5 are 5-pick maps
  and were missing from it): over the three, 78 games three a side (with b25p), 40 four a side and 82 five a side.
  `tools/replay/sizecond.py` rebuilds a size-conditional variant's games exactly from two runs.
- **vp3's Vesper build (Jungle of strength after Treasure) by size against bb2:** five a side 82 games, tributed +4.3%,
  deaths -0.43 +- 0.29; four a side 40 games, deaths +0.75 +- 0.66, tributed level; three a side 78 games, level. On the
  fresh five-a-side panel b26p (ranks 45-49) vp3c (that build five a side only) tributed -2.5% +- 2.9% with deaths level:
  the five-a-side gain did not repeat.
- **Ranked, newest 100 games (to 01:00 IST 10-31):** 44 won; three a side 10 of 19, four 13 of 31, five 21 of 50.
  02guardians 0 of 5 with 16 of our deaths a game, nearly all to champions (9-24 a game against their 0-5).

## Where the five-a-side gap sits against ranks 41-61 (bb2 on b28 and b29, 100 games to r1000; 10-31 05:00 IST)

Scratch readers in the session scratchpad (`timeuse.py`, `campdmg.py`, `capbonus.py`, `capdeny.py`, `massacre.py`,
`shoptrips.py`); the rest from `decoded.py`, `capcycle.py`, `waste.py`, `cohesion.py`, `mapgap.py`.

- **The tributed gap is half deaths.** By r1000 we tribute 578 a game against 711 and collect 721 against 829. Gems lost
  on death are 61 against 28, so kills move about 66 of the 133: the killer takes the bag. Group captures are close:
  654 gems against 690 (own half 396 against 339, middle 245 against 311, the other half 13 against 40).
- **Camp work is level.** In r300-1000 both teams hit camps in about 495 champion-rounds a game and deal 46k against 45k
  camp damage (93 against 89 a hit round); shop trips match (recalls 5.4 against 5.3 a champion-game, walk-out to the next
  camp hit 28 against 32 rounds). Where the time goes differs: in r300-1000 we spend 1917 champion-rounds in our own half,
  792 in the middle and 91 in theirs; they 1729, 1068 and 248. Prospector adds about 1.4% to their captures.
- **Deaths start level and end outnumbered.** Walking back from each death while an enemy stays within 8: at the start of
  that contact our victims had 1.65-1.90 allies and 1.45-1.61 enemies within 8, at the death 1.3-1.5 allies and 2.9-3.7
  enemies; their victims started with 2.10-2.30 allies and ended with 1.8-2.2 allies against 1.9-2.9 of ours. We die
  1.88 times a game in our own half (they 1.19), 2.85 in the middle (2.29) and 0.41 in theirs (0.72). Cohesion (allies
  within 6, `cohesion.py`) is 1.38 against 1.72, and the gap widens late (r600-1000: 1.09 against 1.49).
- **Every one of our types dies 2-3 times as often as theirs** (b29, `decoded.py types`): Heart of Ruin 1.38 against
  0.60, Marcella 0.90 against 0.36, Vesper 0.90 against 0.33, Vendetta 1.20 against 0.67, our Varg 1.24; their extra
  picks die most (Cassi & Issac 1.76 each, Tavi 1.55, Willow 1.50). Their Heart of Ruin holds 2527 max health at r1000
  (Bruiser of health) against our 1646. Our dying Heart of Ruin typically dashes into two visible enemies with one or two
  allies, and three more arrive within two rounds.
- **They start the fights:** 38.1 a game against our 20.1 (`decoded.py fights`); their champion damage is 16.9k against
  12.2k.
- **Losses come in two kinds.** On b29 (15 of 50 won) about 11 losses are massacres (our deaths minus theirs 6 or more by
  r1000) and about 16 are quiet economy losses (three deaths or fewer each side), mostly where the rivals take the
  middle: on 00split, 02harvest and 02cuts (21 games) we capture 33.0 own-half groups to their 31.0 but 10.1 middle groups
  to their 14.7 (272 gems against 380). 00road_of_riches (0 of 4 over b28 and b29) is the worst map: they hunt us near
  our spawn (our deaths 8.5 a game against 2.0), alone against 3-5.
- **By the rivals' fifth pick** (b26, b28, b29): we won 10 of 35 against Cassi & Issac teams, 26 of 65 against Ryth
  teams, 15 of 40 against Tavi teams.
- **Close finishes are rare.** Of b29's 35 losses only 02geodes ended with our tributed plus bags above 1000 (949 + 103
  against 952): banking at the end is not the gap.

## How our champions die against ranks 41-61 (bb2 on b28 and b29, 100 five-a-side games to r1000; 10-31 07:44 IST)

Sources: `main_b28@b28` and `main_b29@b29`, decoded (`data/fights/main_b28_b28`, `main_b29_b29`); readers on
`decoded.py`'s helpers (scratch `outmeet.py`, `whocap.py`; `tools/replay/repeat.py`, `decoded.py channels`).

- **Gang-ups carry the death gap.** Our deaths 5.14 a game, theirs 4.20. By distinct enemy hitters in the victim's last
  10 rounds (0 / 1 / 2 / 3 / 4+): ours 0.07 / 1.37 / 1.40 / 1.32 / 0.98, theirs 0.91 / 1.50 / 0.96 / 0.60 / 0.23. In our
  deaths with three or more hitters (2.30 a game, theirs 0.83) the victim had 1.30 allies and 3.51 enemies within 6 at the
  first hit (theirs 2.18 and 3.57), 82% health, and 1.36 of them a game were in the middle.
- **Outnumbered meetings** (off the start area, 2+ enemies within 8 and more of them than of us within 6, after 10 rounds
  without): ours 16.7 a game, dying within 20 rounds after 18.3%; theirs 12.4 and 12.0%. At the same nearest-enemy
  distance we take about twice the hits in the next 5 rounds (5-8 tiles: 1.32 against 0.66; 3-4 tiles: 2.73 against
  1.51) and the gap to the nearest enemy grows less (3-4 tiles, after 5 rounds: +0.19 against +0.76). The first three
  rounds' moves are close (away 28% against 35%, sideways 18% against 13%, toward 21% against 22%, standing 28% against
  26%), so the difference is mostly the chasers: the rivals press an outnumbered target harder than we do.
- **Full packs.** Share of champion-rounds off the start area with all four teammates within 6: r0-40 ours 0.48 against
  0.58, r40-80 0.16 against 0.32, r80-120 0.11 against 0.22, r200-300 0.08 against 0.17, r600-1000 0.03 against 0.11.
  Other team counts are close. Our deaths r0-100 0.46 a game against their 0.12; r0-150 0.57 (0.51 to champions, with
  3.75 enemies and 1.58 allies within 6) against 0.44 (0.29; 1.91 and 1.59).
- **Caught farming.** Deaths where the victim was hitting a camp when the first enemy hit landed: ours 0.49 a game, theirs
  0.10. In the 5 rounds before that hit an enemy stood within 8 in 4.9 of them and two or more in 3.9, while the victim
  hit the camp 3.7 times; at the hit 2.86 enemies and 1.10 allies within 6 (theirs 2.80 and 2.40). pa1 (10-27) stopped
  such camp fights against packs and lost 8% of tributed.
- **Walk-out deaths.** Deaths 21-50 rounds after the champion was last on its start tiles: ours 1.01 a game, theirs 0.67,
  at a home distance of 13 with 2.93 enemies and 1.38 allies within 6 (theirs 2.09 and 2.00).
- **Our Vesper's hits feed teammates' captures.** Of the groups our Vesper hit to r600, she captured 4.0 a game (50.5 of
  her hits) and a teammate 6.6 (83.8 hits); the rivals' Vesper 5.9 and 3.3. In 4.0 of those 6.6 she stood within 2 of the
  group when the teammate's capture began, so the gold-spread claim rule moved them (Marcella 2.1, Varg 1.6, Heart of
  Ruin 1.5, Vendetta 1.4). Her gold held at r300 / r600: 314 / 687 against the rivals' 473 / 1114, with team gold level
  (1149 / 2721 against 1153 / 2792). vc1 and vg1 (10-30, 10-31) gave her those captures and lost 5% of tributed.
- **Channels.** Our bags of 30+ with an enemy within 4 during the channel complete in 69% (1.49 a game), theirs in 80%;
  an enemy cast on our channeler in 23% of those, ours on theirs in 2%. Bags over 100: 0.6 a game, 77% completed against
  0.9 and 97%.
- **Ability timing is level.** At a fight's start our Marcella's damage spell was spent on a camp in the 8 rounds before
  in 11% (theirs 7%); dashes were spent in the 8 rounds before in 47-53% of fight starts for both sides.
- **Cassi & Issac** (ci1 on b29p, ci2 on b28p, 100 games against the same bases): tributed level (+0.2 +- 23.7 a game),
  collected +2.8%, gems lost on death +25.5 a game; the pair dies 1.74 times a game each, as the rivals' pair.

## Fight openings against ranks 41-61: the rivals open twice as many, mostly with types we do not draft (10-31 08:17 IST)

Source: `tools/replay/fs_firsthit.py` on `main_b28@b28` and `main_b29@b29` (bb2, 100 five-a-side games, to r1000; output
saved in `data/fs_firsthit_bb2_b28b29.txt`). A fight start is the first hit between two champions after 15 quiet rounds.

- The rivals open 35.9 fights a game, we 18.5; their victims die within 10 rounds in 24%, ours in 16%. By distance at
  the round start: 2 tiles 4.24 against 6.53, 3 tiles 5.46 against 9.86, 4 tiles 5.08 against 12.46, 5 tiles 2.54
  against 5.64. Their openings on our champions that walked the round before: 23.58 a game (ours on theirs 12.73); on
  champions hitting a camp 2.67 (ours 0.68).
- Type for type our openers match theirs: Vesper 6.09 against 6.24, Vendetta 2.07 against 2.09, Marcella 6.27 against
  7.62, Heart of Ruin 2.47 against 3.96. The rest of the gap is the types we never draft: Tavi 5.18, Cassi 2.84, Willow
  2.75, Ryth 1.83, Prism 1.79 and Issac 1.10 openings a game (15.5 together), against our Varg's 1.60. Ranged spells
  open 7.01 of their fights and none of ours.
- **Leaving the camps loses the fights too** (platform, b28p against `main_b28@b28`, 50 games each, to r1000): a prey up
  to 8 tiles away when we outnumber around it (pp1) cut our camp-hit rounds by 12.8 a game and the rivals' deaths by 0.78
  (+-0.26) while ours rose 0.46; a higher engage bar (ft7p) cut the rivals' deaths by 0.28; walking home from enemy balls
  (bv1, 10-30, b19p-b21p) raised our deaths by 0.41 and cut theirs by 0.44. Our kills come where our champions already
  work, so the next variants keep them on their camps (sw1, sw2, ls1).

## Top-20 drafts, carriers in contact and 00road_of_riches (session 88, 10-31 09:20-09:54 IST)

Scratch readers in the session scratchpad: `topdrafts.py` (ladder JSON plus `cambc matches list --team`), `bagtrig.py`,
`bagcontact.py`, `mapdeaths.py`, `lcurve.py` (local result files).

- **The top 20 field our team with Ryth for Varg.** Their last 8 ranked games each (about 110 five-pick games, 09:45):
  Heart of Ruin, Marcella, Ryth, Vendetta, Vesper 25 times, Marcella, Ryth, Tavi, Vendetta, Vesper 9, Heart of Ruin,
  Marcella, Tavi, Vendetta, Vesper 6; Varg appears in about 10. Rank 1 (2603) plays Cassi & Issac, Heart of Ruin,
  Marcella, Vendetta, Willow. Ryth for our Varg was gated three times (ry1, dq4, ry2) and never paid.
- **Carriers in contact act as the rivals' do** (bb2 on b28 + b29, 100 games, to r1000). Episodes with a bag of 15+ and
  an enemy champion within 8 for 3+ rounds: ours 13.2 a game, theirs 11.8, bags about 43 both. In the next 10 rounds
  both sides move in 62-65% of rounds, hit camps 8-9%, hit champions 7-8%, and are nearer an altar after 10 rounds in
  45-47%. The outcome differs: within 40 rounds we die in 10% and tribute in 38%, they die in 5% and tribute in 54%; our
  altar is 7.5 tiles off at the start, theirs 5.8. Our deaths with a bag of 10+ (1.55 a game, theirs 0.75) follow about
  29 rounds of contact. So the bag losses come from the fights, not from the banking decision.
- **00road_of_riches (1 win in 7 decoded games):** our champions die in the middle (5-10 tiles from both starts) alone
  against two to four (at the death 0-1 allies within 6), most of them carrying 20-60 gems; up to 13 deaths a game by
  r1000 against the rivals' 0-3.

## The band at our level: level deaths, a gem gap (bb2 on b30 + b31, ranks 46-64; session 89, 10-31 10:20-10:52 IST)

Sources: `main_b30@b30` and `main_b31@b31` (100 five-a-side games, ten teams ranked 46-64 at 10:06, to r1000), decoded
in `data/fights/main_b30_b30` and `main_b31_b31`; `decoded.py`, `capkind.py`, `groupkind.py`, `steals.py`, `capcycle.py`,
`mapgap.py`. Our ranked games since 01:30 IST (260, `data/ranked_1031a.json` joined with `data/ladder_1006.jsonl`):
74 of 160 won against ranks 51-67 and 40 of 80 against ranks 69-85, so the rating is decided in this band.

- **Deaths are level, gems are not.** b30: deaths 4.72 a game each; collected 737 against 842 by r1000, tributed 554
  against 700. Level at r150 (86 against 82), behind from r300 (190 against 201) and most in r300-600 (430 against 501).
  Gems lost on death 69 against 38: with equal deaths our victims carry about twice the bag (14.7 gems against 8.1).
- **By group kind to r1000** (`capkind.py`): they capture more pure gem-cluster groups (7.3 a game, 136 gems, against
  5.0 and 101) and we more pure gold-cluster groups (8.7 against 7.7); team gold is level (r600 2937 against 2977). To
  r600 the gem gap is spread: own-half clusters -13, middle clusters -8.7, middle elk -10.8, middle golem -8.2, the other
  half -11.5, wolves +6.
- **The middle gem fields.** On 00lost_world (2 games) the rivals captured middle gem-cluster groups 58 times a game
  (837 gems, r200-447) against our 10.5 (181, r76-341), with our deaths 4.5 against 1.0; on adgato_gemcombat5 10.7
  against 4.7 middle gem captures. We were there first and left once it was contested.
- **Steals:** they capture 1.33 of our kills a game (31 gems, 156 gold), we 0.85 of theirs (17 gems); in the stolen ones
  our nearest champion stood 1 tile from the group at the kill and the stealer 3, and ours was on the tiles 3 rounds
  later in 14% (kept kills 66%). Holds of a defeated group's tiles end alike (captured 41.3 against 42.3 a game).
- **Per type** (`decoded.py types`): their Vesper collects 249 gems a game, ours 150, with the same champion damage (3403
  against 3440) and fewer deaths (0.55 against 0.64); the other types are level (Marcella 188 against 173, Heart of Ruin
  113 against 138, Vendetta 138 against 139, our Varg 141 against their Ryth 121).
- **Time per capture** (`capcycle.py`, to r600): 27.1 captures a game against 28.1; the capturer's cycle 81.2 rounds
  against 72.4 (dead 3.6 against 2.2, hitting camps 16.8 against 14.4, moving 44.5 against 41.4, idle 14.0 against 12.0).
- **Fuel is no factor:** our turns ran out of fuel 2.3 times a game after round 3 (theirs 23).
- **Items at r600:** our Vesper (2152 max health) and Marcella (2011) are tankier than theirs (1889, 1827); their Vesper
  holds 2.49 Bruiser-strength emblems plus Capture and Prospector ones.

## The opening: five together on 4-gem groups (local, bb2 against cand1, cp3, dh3; 10-31 10:00-10:30 IST)

- bb2 collects less than the old bots by r100 on 02treasure-box (47 against 101), 00lost-world (32 against 91),
  01corridors (8 against 39), 01big-world (15 against 49), 02cuts (22 against 51) and 02fields (22 against 37), from
  `data/runs/multi-083529` (scratch `mapopen.py`); over all 420 games it collects more by r100 (55.9 against 40.9).
- A bisect over the ladder bots against cp3 on those maps (`data/local_bisect_open.log`, `data/runs/multi-100657`, 16
  games each) puts the drops at sq2 (01big-world r100 56 to 26, 02fields 54 to 28) and tw13b (02fields 46 to 21,
  02treasure-box 69 to 41).
- A probe printing each target change: before r40 every champion scores as if alone (sq2's opening), so after the first
  capture (about r20) all five walk together to one 4-gem group after another (02fields: g0, g2, g5, g3 by r40;
  02treasure-box likewise), and at r40 they switch together; on 01big-world all five left for one far 41-gem group at
  r40-43 and captured nothing until r107.
- On the platform the opening is not where we trail the band (b30 r150: 86 against 82), and op1 (the as-if-alone opening
  ends with the first group) moved b30p's r300 collection by -2 (row op1).

## Ranked losses by kind, guarded altars and the worst maps (session 90, 10-31 13:15-14:00 IST)

Sources: the 403 ranked games of 10-30/31 with cached summaries (`data/ranked_1031a.json`, `data/summaries/`), the
decoded guard-map games in `data/fights/q_guard`, and bb2's decoded panel games. Scratch readers (session scratchpad):
`rlosses.py`, `guardtl.py`, `guardtrace.py`, `lwzone.py`, `postrace.py`.

- **Loss kinds** (a massacre: we die 6 or more times more than they do; bank: we collected at least 90% of their gems;
  econ: the rest): 193 wins, 119 econ losses, 67 massacres, 24 bank losses. In econ losses deaths are level (4.6 against
  5.3 a game) but the rivals collect 1.10 gems a round against our 0.68; in massacres we die 15.9 times against 3.7. In
  bank losses (two races to 1000 with few deaths) we held enough at the end to win in 7 of 24: 01the_farm (three of
  them; its altars are 20-35 tiles from where we farm, so bags grow to 260-320), 00expanse twice, 02crossing, 02famine.
- **Win rate by team size:** three a side 36 of 73 (0.49), four 54 of 99 (0.55), five 103 of 231 (0.45).
- **Results by an opponent champion's presence** are flat (0.48-0.49 won) for Marcella, Vesper, Heart of Ruin,
  Vendetta and Ryth; lower with Cassi and Issac (0.41 won, 0.25 massacres, 64 games) and Prism (0.28, 0.40, 25 games).
- **Guarded altars never banked.** 01boss_battle: in 5 of 6 decoded ranked games we tributed nothing while carrying up
  to 3236 gems; the altar (25,20) has one free neighbour, the guard monolith's tile (24,20), so after the guard dies the
  two teams fight over one tile, and the rivals hold it (game 28ca6268: their Vendetta, Heart, Marcella and Vesper
  stood on it in turn from r841; our Marcella got on at r913 with 369 gems and died there by r929). 02guardians: in 5
  of 13 summarised games we tributed nothing; in four of the decoded losses the rivals killed a guard (0 hits of ours)
  and tributed through its tile while we did not start a channel in the next 130-250 rounds (gf2's cause). By map,
  tributed over collected: 01boss_battle 0.00 against the rivals' 0.28, 02guardians 0.36 against 0.62,
  adgato_gemcombat5 0.44 against 0.77.
- **Maps where we farm far slower with deaths level or better** (ranked, collected per round, us against them):
  01yellow_brick_road 0.49 against 1.24 (6 games, 0 won, deaths 4.5 against 4.5; on the pinned panels the same map is
  close, 320 against 361 by r600 in 9 games, so the ranked gap is mostly the ruliad's three games), 00lost_world 0.84
  against 1.75 (9 games, 2 won, deaths 5.9 against 8.1), 01concentrated_wealth 0.47 against 0.85, 00rows 0.56 against
  0.99.
- **00lost_world is decided by the centre.** Its corridor (rows 14-16) runs between the halves and is entered only at
  its two ends, inside a monolith's reach (1,15) on the left and a golem's (33,15) on the right; it holds the centre
  altar and about a dozen gem-cluster groups. In bb2's 8 decoded panel games (all lost) the rivals spend 1089
  champion-rounds a game of rounds 100-600 in its centre (x 13-23) against our 93, and we spend 1519 in our own half
  against their 481. To r600 they make 66 captures a game (63 in the middle, 907 gems) against our 25 (213 gems), with
  a capture cycle of 29 rounds and 4-tile hops against our 76 and 10. Both teams rush the corridor's left end at the
  start; we lose that first fight (deaths by r150 2.2 against 1.0, collected 59 against 190), then farm our half's far
  side and bank at the (33,1) altar while they farm and bank in the centre.

## Stuns, idle time, rocking and gem density at our level (bb2 on b30 + b31, ranks 46-64; session 90, 10-31 morning)

All to r1000 over bb2's 100 games on b30 and b31 unless noted, us against them.

- **Base numbers:** deaths 4.29 against 4.40; collected 740 against 832; tributed 584 against 645; lost on death 53
  against 30.
- **Stuns** (`stuns.py`): we land 7.7 a game (Heart of Ruin 4.6, Marcella 3.1), they land 17.5 (Ryth 9.5 in the 80
  games it played, Cassi 6.3, Prism 4.6). 47% of our deaths had a stun on the victim in its last 6 rounds, 27% of
  theirs. ry2 (Ryth for Varg) raised ours to 12.5 a game without fewer deaths.
- **Damage** (`damage.py`): per-type damage and hit shares are level with the band; we are outnumbered in contact more
  often (Heart of Ruin 29% of its contact rounds against their Heart's 19%).
- **Captures** (`clears.py`): 41.3 against 42.4 a game; solo clears 41% against 48%. Gems per capture: groups of
  200-500 health 4.8 against 7.0, under 200 health 4.5 against 5.8: they take gem clusters, we take gold clusters
  (gold counts 0.25 gem before r1400, `camps.h`; lv1, lv15 and gw10 lowered it without a platform gain).
- **Idle stretches** (scratch `still.py`): ours about 181 champion-rounds a game, theirs 79, mostly respawn waits (81
  against 40); cw1 and ce4 showed shorter waits are no lever.
- **Two-tile rocking** (`tools/replay/osc.py`): ours 15 champion-rounds a game, theirs more (with under 20 gems and no
  enemy near: 16.4 against 4.1). On the guard maps, rocking runs with 20+ gems are 7.5 a game against 6.2.
- **Loiter windows** (`tools/replay/loiter.py`, 250 games): ours 0.43 a game, theirs 0.77: no gap.
- **Respawn blocks** (`tools/replay/blockwait.py`, 514 bb2 games): blocked rounds 14.7 against 13.8 a game, idle
  teammate-rounds 8.8 against 4.5. The local 01boss-battle freeze (gf1 row) is rare on the platform.
- **Channels near enemies** (`decoded.py channels`): with an enemy champion within 4 during the channel we complete 61%
  of bags over 30 (1.68 a game), they 83% (1.43); per-turn break rate with one enemy within 10 of the altar 0.011
  against 0.004.
- **Turn use** (audit probe au19, local): almost no caught engine error, unused attack or unused spell; walks stall in
  0.3% of turns (row au19).

## Our newest 100 ranked games: parity, massacres and the close-out (session 90, 10-31 14:15-15:05 IST)

Source: our newest 100 ranked matches at 14:15 IST (50 won), 97 decoded in `data/fights/rk1031` (`index.txt` from
`cambc matches list --json`); readers `decoded.py gems/types/items`, `deathfactors.py rk1031` (`data/df_rk1031.txt`),
`closeout.py`, `winbag.py`, `idle.py`.

- **On average we are level with the teams we meet.** To r1000: collected 714 against 711, tributed 600 against 595,
  lost on death 36 against 44, deaths 3.7 against 4.4; idle time level (`idle.py`: waits 8.0 against 7.5 per 100
  alive rounds); home visits while alive 36 against 43 a game (scratch `homevisits.py`). The opponents mostly play our
  own four (Marcella 85 of 97 games, Vesper 81, Heart of Ruin 73, Vendetta 68) with Ryth as the fifth (52).
- **The losses split by deaths.** By r1000 death difference: 9 massacres (ours minus theirs 6+, 0 won; deaths 14.4
  against 3.8, team gold at r300 740 against 1408; 54% of our deaths in our own half, 57% while fleeing), 14 mixed
  (3-5, 2 won), 74 even (46 won, 62%). Massacre maps: one each of 00packs, 01gold_rush, 02arena, 01hooks,
  01concentrated_wealth, 01starfish, adgato_gemcombat2, 00contest, 00ribs. Deaths within 60 rounds of a respawn are
  rare on both sides (0.32 against 0.37 a game).
- **By game length:** games ended before r1000 we won 20 of 29; r1000-1499 20 of 50 (in those losses tributed level at
  r300, 217 against 270 at r600, 384 against 549 at r900); r1500-1998 7 of 16.
- **Close-out:** from the first round our tributed gems plus our bags reach 1000 ("win in hand") to the game end took
  us 52 rounds (median) against the rivals' 28; we lost 6 of 53 such games, they 7 of 55. Single winning bags are
  closed as fast as theirs (`winbag.py`: 14.4 rounds to the first tribute start against 17.1), so the slow part is the
  team: 00rushbait_v2 held 924 tributed and 126 in four bags of 22-46 (none enough alone) for 40 rounds until the
  rivals' 423-gem Prism channel won; 00monolith's Vesper carried 256 at 751 tributed for 110 rounds and passed two
  altars (the bank walk avoids enemy reach); 02treasure_box sat at 980 for 140 rounds while our Heart of Ruin carried
  61 around the one enemy-held altar and died; on 01broken_curve our Heart of Ruin held 200 at 947 beside an altar, its
  channel was cancelled (a rival lock or stun) and it fled. On b30 + b31 (bb2's base runs) we lost 1 of 47 wins in
  hand (median 46 rounds), they 7 of 60 (38). Row eg1 tests the fix.
- **Per type** (`decoded.py types`, to r1000): the rivals' Vesper collects 252 gems a game against ours 160 and deals
  5053 champion damage against 3959 (their build at r600: 2.21 Bruiser-strength emblems; ours Durability-health 1.15,
  Power-strength 1.07); our Marcella, Heart of Ruin and Vendetta each collect 15-20 more than theirs. Item builds of
  this kind were tested many times (vb1, ib1, ib1r, vp1-vp4, vg1): none passed.
- **Worst maps over 600 ranked games** (`tools/platform/ourmaps.py 6`, `data/ourmaps_1031.txt`): 00lost_world 1 of 12,
  00expanse 1 of 9, 00contest 1 of 7 (0 of 6 as side b), 00great_wall, 02geodes and 01boss_battle 1 of 6; overall 289 of
  600.

## Is the bot worse than when we reached 2045? (session 90, 10-31 17:00-17:17 IST)

Question from the team at 17:00: are we still beating v1287, the version live when we reached 2045?

- **v1287 is bb2, the current main.** `bots/main` has not changed since 10-30 10:03 (bb2, version 1217). Every main
  resubmission since then has the same 75,799-byte bundle (1217 ... 1287 ... 1401, `cambc submissions list --json`;
  `--before N` pages back). The gate variants are 75,900-76,732 bytes. v1287 was uploaded at 18:25 IST on 10-30, after
  the dn1 gate, and was live at the 2045.1 reading (18:54).
- **Ranked games by the live version** at each game's creation time (exact upload times from the submission list): of
  our 600 ranked games from 10-30 18:40 to 10-31 14:30, bb2 played 580 and won 278 (48%). Gate variants played 20
  (v1392, v1332, v1318) and won 11: `gateq.sh` uploads a test bot only at :x1-:x2, so the ranked sets at :x0:05 nearly
  always meet main. Win rate per 4-hour window: 40%, 47%, 46%, 53%, 47%, 52%.
- **The rating fell with the same bot:** 2045.1 at 18:54 (10-30), 1983 at 23:45, 1957.5 at 04:00, 1992.8 at 09:28,
  1961.4 at 15:12 (rank 74). Over the same day the rating at rank 40 rose from 2042.2 to 2067.4. The field is moving
  up and our bot is not; 2045 was a peak, not a level that a regression lost.
- **No side or size fault:** side a 49% of 290, side b 48% of 310; five a side 45-46% (352 games), four 52-55%, three
  56% (a) and 42% (b) of 52 each.
- **Altar locks** (summaries of 170 games, b30 + b31 base and `rk1031`): the rivals buy 6.7 locks and 2.8 teleport
  crystals a game, we buy 3.1 locks and no crystals (crystals were tested: tp1, tp2, tpe, tpd). We hit enemy locks 13.5
  times a game (decoded attacks without a unit target; 79% at middle altars) in 3.4 episodes a game; in 82% of them
  the tribute started within 40 rounds (median 5 rounds after the first hit), and 23 of 676 episodes ended in our
  champion's death (2.6 gems a game). The rivals' locks cost us little.
- **Collection decides the long games.** Games ending r1000-1499: in our 42 wins we collected 149 / 357 / 670 gems by
  r300 / r600 / r900 against 121 / 284 / 499; in our 48 losses 123 / 294 / 508 against 135 / 358 / 694. The gap is
  already there at r300 either way.
- **Unspent gold and health** (b30 + b31, to r1000): our unspent gold is lower all game (r600 203 against 319), and the
  rivals' living champions hold about 10% more maximum health at r200-r300 (5838 against 5328 at r200), level from r600.
- **Every code change re-rolls the games.** The bot's searches are budgeted by `fuel_remaining()` (`move.h`,
  `targets.h`, `bot.cpp`), so a few added instructions change early decisions: dc1 locally differed from bb2 in 76 of
  420 games, on 01elk-arena against cp3 from round 4. Pinned panels pair game by game only identical binaries; a
  variant's 100 games are close to a fresh draw (on b30p + b31p the base won 47, five variants 42-48).

## Channel denial, close losses and Vesper's farming (session 90, 10-31 17:40-18:35 IST)

- **The rivals deny our channels; we do not deny theirs** (`tools/replay/lockopp.py`, bb2 on b30 + b31, 100 games to
  r1000). With one of their champions within 2 tiles of our altar during a channel of 30+ gems, 33% of our channels
  completed; with one of ours that near theirs, 64% did (0.55 such channels a game, 57 gems). Their locks broke 0.10 of
  our 50+ gem channels a game, ours 0.01 of theirs; they also cast on 20% of our channellers with an enemy within 4,
  we on 11% of theirs (`decoded.py channels`). Per channel turn with one enemy within 10 of the altar our channels break
  at 0.0112, theirs at 0.0043. Our deny code (`deny_channel`) acts only on a channel that wins the game, and our
  champions carried a lock only once the rivals had tributed 600. Row lx1 tests a lock on any visible channel.
- **After a rival lock breaks our channel** the carrier banks a median 65 rounds later (0.14 a game), dies first in 0.03
  and the game ends first in 0.04 (scratch `lockafter.py`).
- **Close ranked losses** (`data/fights/rk1031`, the 28 losses with level deaths): 8 ended within about 120 gems. Two
  were lost to a hoarding Prism with a win in hand of ours: 01broken_curve (947 tributed and our Heart of Ruin's 200-gem
  channel at r1027-1044, stunned by their Heart; their Prism had carried 177-284 gems for 200 rounds and won with one
  28-turn channel at r1067) and 00rushbait_v2 (we reached 924-970 with four bags of 22-58, none enough alone until
  r1272; their Prism carried 299-423 gems from r1000 and won with a 29-turn channel at (15,1); the Tribute emblem cuts
  a channel by a third). We held no lock in either (bought only after their 600). Games where a rival held 300+ gems:
  0 of 6 won on rk1031, 6 of 14 on b30 + b31.
- **The whole collection gap is Vesper** (`tools/replay/vtime.py`, b30 + b31 to r600): their Vesper makes 7.1 gem
  gains for 152 gems and 1056 gold, ours 5.0 for 91 and 748; their other four types capture as ours do (Heart 4.5 and
  4.0 gains, Marcella 5.2 and 5.0, Vendetta 4.5 and 4.2, Ryth 4.2 and our Varg 4.8), and team gold is level (2936
  against 2828). Our Vesper hits camps in more rounds (137 against 123) and has a teammate within 3 in 299 rounds
  against 241: she clears with the others while theirs farms groups of her own. To r1000: 249 gems against 150
  (`decoded.py types`). Her builds were tested many times (vp1-vp4, vp3c, vg1, vc1); the solo pick (ve1) never reached
  the platform. Row ve1r tests it. Whose captures her camp hits feed (`tools/replay/vhits.py`, to r600): ours 137
  hit rounds a game, 40% her own captures, 52% teammates', 4% the enemy's; theirs 123, 60% and 31%.
- **Fuel is not a factor now** (`tools/replay/fuel_events.py main_b30@b30 main_b31@b31`): no bot fault, 5.6-7.0
  exhausted turns a game, 4.5 of them in the setup rounds 1-3 (the rivals 10.8-35.4).
- **Ranked by team size over 600 games** (`data/ourmaps_1031.txt` with `data/map_sizes.json`): three a side 51 of 104,
  four 77 of 144, five 161 of 352. The 100-game sample `rk1031` (5 of 15 three a side) overstated the small-map gap.

## Where the collection gap sits, and what is level (session 90, 10-31 18:55-19:35 IST)

Source: bb2 on b30 + b31 (100 five-a-side games against ranks 46-64, to r1000 unless marked); readers `decoded.py`,
`vtime.py`, `typebag.py`, `dashes.py`, `closeout.py`, `lockopp.py`, scratch `bytype.py`, `casts.py`, `sib.py`.

- **Without a rival Prism the gap is wide.** In the 87 games without one the rivals tributed 419 by r600 against our
  319 and 710 against 576 by r1000, with bags level (64 against 62 at r600). In the 13 Prism games we out-tributed them
  (637 against 209 by r1000; their Prism carried 651) and won 6.
- **Every type of theirs collects more, Vesper most** (`vtime.py`, non-Prism games, gems to r600): Heart of Ruin 82
  against our 69, Marcella 118 against 106, Vendetta 83 against 74, Vesper 152 against 88; gems per gain are level
  (17-21) and they make more gains. Each of ours had a teammate within 3 in 283-309 of 600 rounds, theirs 240-264.
- **Team captures are level; the middle and the far half are not** (`decoded.py captures`): 41.3 against 42.4 a game;
  own half 30.6 (454 gems) against 29.4 (448), middle 8.7 (194) against 9.4 (232), the other half 2.0 (28) against
  3.6 (53). Per capturer a capture cycle takes 90 rounds (median 64) against 79 (56), with 54.6 moves against 49.9 for
  the same straight hop (14.5 against 15.0). We clear faster (17.3 rounds against 22.8). Team gold is level (2937
  against 2977 at r600); camp kills by r300 are level.
- **Our melee die carrying gems** (`typebag.py`): with an enemy within 4 our melee (Heart of Ruin, Marcella, Varg,
  Vendetta) carry 11.3 gems, theirs 7.5; our melee lose 45.1 gems a game on death (12.4 a death), theirs 22.4 (6.7).
  Their Heart of Ruin, Ryth and Vendetta die with 2.4-3.6 gems, ours with 8.1-11.7; all our gems lost on death 53.4
  against 29.5, which the killers take. Tribute starts per type are level (3.8-4.9 a game). Row mbk1 tests smaller
  melee bags.
- **Level, so not the cause:** dashes (`dashes.py`: 64-86 a game per dash type both sides, 7.5-10 per 100 alive rounds,
  70-80% with no enemy within 8), casts per slot with a camp hit (Vesper's reset 32 against 30 a game), holds of a
  captured group's tiles (45.9 against 47.8 a game, left early 4.6 against 5.5), unspent gold (ours lower: 53 against
  74 per champion at r600-799), the close-out of a win in hand (we lost 1 of 47, they 7 of 60), channels we break by
  walking off (none: the bot returns at once while channelling; `lockopp.py`'s "moved" are unseen causes).
- **Noise on these panels** (scratch `sib.py`, `baserank.stats` over every bot decoded on b30p + b31p): pooled collected
  bb2 740, dc1 726, eg1 750, lk1 740, lx1 723, op1 748, rd0 738, ve1r 756; wins 47, 45, 43, 48, 42, 42, 42, 40. Near-null
  variants span about 30 gems, so a collected bar under +3% sits inside the noise (ve1r met its +2% by 0.05).

## The five-a-side drop after vx1, the quiet panel and the close races (session 90, 10-31 21:30-22:34 IST)

Source: our ranked games from `cambc matches list` (`data/ourmaps_now.json`, 300 games) with the live version placed
by the `cambc submissions list` status times (scratch `byver.py`); the summaries of those games; `main_b36@b36` against
`bb2r_b36@b36`; `main_b35@b35` (`vtime.py`, `decoded.py gems`); ranked replays in `data/fights/bk1031` (scratch
`race.py`).

- **Ranked five a side fell after vx1 went live** (19:56): 7 of 32 games (vx1 5 of 18, its gate variants 2 of 14)
  against 51 of 99 under bb2 from 13:30; three and four a side, played as bb2, 10 of 18. In the 30 five-a-side games
  with summaries our deaths were 6.47 a game against 5.08, our collected 798 against 932 and the rivals' 1063 against
  861. The paired check did not reproduce it: on b36 (the five teams that beat us, run back to back) vx1 won 25 of 40
  and bb2 19 of 40, with vx1's deaths 3.20 against 3.38, tributed 613 against 589 and collected 781 against 795 (row
  bb2r). Variants live during gates won about as often as main all day (72 of 150 against 122 of 250).
- **Quiet five-a-side maps against teams above us** (b35, vx1, 50 games): collected 435 against 461 by r600 and 811
  against 893 by r1000, deaths near zero. Their Marcella 150 gems by r600 against ours 110 (23.5 gems a gain against
  18.9, gold 965 against 796); their Vesper 127 against 97 (ours farms alone: teammate within 3 in 169 rounds against
  288). Our Heart of Ruin, Varg and Vendetta sit beside a teammate in 297-313 rounds, theirs 212-257.
- **Close races lost at the end.** 02famine against OneTap: at r1600 we had 728 tributed and 229 gems in bags against
  their 922; lost 928 to 971+. 01yellow_brick_road against shoutout MAPS: 998 against 1000 at r1286. 00rushbait_v2
  against dromedaries: 865 tributed and 88 carried when they won at r936. An endgame sweep (every bag banks once the
  enemy has 800) was tested long ago (es1, es2, dr7) and did not help.

## The teammate's drunk bot (11-01 00:00 IST)

A teammate's repository `cambc-2026-drunk-bot/` (a separate C++ bot line, switches in `common.hpp`, its own ideas
ledger in `notes/IDEAS_LEDGER.md`). Its live build (`configs/v72.override.hpp`) against our main (vx1), all 70 maps
both sides locally (`data/runs/multi-235814`, `data/local_h2h_dk72.log`): vx1 won 106 of 140, margin +300 a game.
Their ledger agrees with ours on several points: copying a top team's item builds (Jungle first) lost 28-44 of 420,
tighter pull-back and refusing target switches raised deaths, and an endgame "everyone banks" rule lost. Their one
ladder gain was per-map opening tables (`maptable70.hpp`), which do not port to our target code before the lock.

## Ranked results by team size after vx1: the field moved (session 91, 11-01 01:25 IST)

Source: our newest 200 ranked games (`python -I tools/platform/ourmaps.py 2 data/ourmaps_1101_0130.json`, 18:30 IST
10-31 to 01:20 IST 11-01), split at vx1's adoption (19:56) and fin1's (01:12) by creation time; team size from the
draft length.

- **Under vx1** (19:56-01:12): five a side 38 of 94 (40%), four a side 19 of 33, three a side 14 of 23. **Under bb2**
  (18:30-19:56, the newest 45 games before vx1): five a side 14 of 27, four 6 of 7, three 10 of 11.
- vx1 plays three and four a side exactly as bb2, and there our wins still fell from 16 of 18 to 33 of 56. So the
  field moved around 20:00 IST (teams uploading for the lock), and the five-a-side fall (52% to 40%) needs no vx1
  cause. The paired checks (b36, b30p + b31p) stay the evidence; they favour vx1 over bb2.
- The ladder still rose: rank 65, 1991.4 at 01:28 IST 11-01 (`cambc ladder --json --page 3`), from rank 77, 1951.1
  at 21:33.


## fin1: level to r1000, behind over whole games (session 91, 11-01 01:50-02:00 IST)

Source: fin1's five pinned panels against vx1's runs on the same panels (b30p, b31p, b36p, b32p, b33p; 240 paired
games, rows fin1 and fin1c).

- To r1000 (`pooled.py`) fin1 and vx1 are level: margin +0.6 +- 9.6 five a side, -6.2 +- 18.0 three and four a side.
  Over the whole game (`pooled.py --round 2000`) fin1 is behind: margin -18.1 +- 12.4, our tributed -10.9 +- 8.3,
  win share 0.50 to 0.47 (-0.03 +- 0.01). lk1w's harm (the 25-turn wait at a blocked altar) sits in the endgame, where
  a long wait can lose a close race, which an r1000 window does not see.
- Platform games are deterministic: 143 of the 240 games are identical in both runs. Comparing the decoded games round
  by round (`tools/replay/whofirst.py`), the first round where any unit differs shows which side changed first. In 84 games our units diverged
  first (the opponent had played identically until fin1 acted). Of these, 10 turned from win to loss and 2 from loss
  to win (sign test p = 0.039). The 13 games where the opponent diverged first, or both sides in the same round, all
  kept their result.
- So whole-game wins can be judged when the opponent's play was identical up to our change: opponent uploads, the
  reason wins are not judged, then show up as opponent-first divergences and can be set apart. A rule for an endgame
  change (a wait, a give-up, a bank) should pool to the whole game, not to r1000.
- The same check of vx1 against bb2 (b30p, b31p, b35p and b36: bb2's runs `main_b30@b30`, `main_b31@b31`,
  `bb2r_b35p@b35p`, `bb2r_b36@b36` against vx1's `vx1_b30p@b30p`, `vx1_b31p@b31p`, `main_b35@b35`, `main_b36@b36`)
  keeps vx1: over the whole game (190 paired games) margin +29.6 +- 24.9, win share 0.45 to 0.49 (+0.04 +- 0.04); in
  the 177 games where vx1's units diverged first, 28 losses turned to wins and 21 wins to losses (b36, the 10-31
  evening neighbours: 7 to 1). vx1 changes five-a-side play from about r40, so no game is identical there.

## The teammate's bot and two programs in one (session 91, 11-01 02:43-04:25 IST)

Source: `bots/pool/bot_10` (the teammate chejibt001's bot; their team cheji bt was rank 51, 2043.5, at 02:34 IST, we
were 74), local runs `data/runs/multi-025140` (bot_10 against vx1), `multi-030914` (cmb1's screen), the cja run
(`data/local_cja_3v3.log`) and the platform gates of cmb1 (rows cmb1, cmb2, cja).

- **By team size.** Head to head against vx1 (all 70 maps, both sides) bot_10 won 87 of 140: three a side 12 of 24,
  four a side 18 of 32, five a side 57 of 84 (margin -30, +186 and +175 a game). Against our pool (cand1, cp3, dh3)
  with its log off: three a side 59 of 72 (vx1 60), four a side 77 of 96 (vx1 87), five a side 205 of 252 (vx1 180).
  So bot_10 is much the stronger five-a-side bot, vx1 the better four-a-side bot against our pool, and the two are
  level three a side.
- **Two bots in one program.** Each champion runs its own copy of the program, so a program can pick its bot once
  from the team size (`cambc::draft::team_size()` in the draft) and every champion of the team picks the same one.
  bot_10's files sit in `src/cj/` inside `namespace cjb` (its `main` renamed `run`); the build compiles `src/**/*.cpp`
  (`cmake/CMakeLists.txt`, `GLOB_RECURSE`), and quoted includes resolve in the including file's folder, so the two
  bots' same-named files (`bot.h`, `draft.cpp`, ...) do not clash. Checks: three a side cmb1 against vx1 mirrors
  exactly (00anvil 998-958 and 958-998), five a side it drafts as bot_10; 560 screen games, no bot fault.
- **On the platform it plays a different game.** cmb1 (bot_10 four and five a side) against vx1 on three panels of
  teams above us, same session (b37, b32p, b36p; 140 paired games over the whole game, `data/judge_cmb1_all.txt`): 85
  against 72 wins, margin +62.4 +- 48.4, win share 0.51 to 0.61. It fights more: our deaths 4.96 to 5.94 a game, the
  rivals' 7.11 to 9.27, our hit rounds +23 +- 9. It loses less on death (our lost 152 to 84) and the rivals collect
  113 +- 57 and tribute 44 +- 28 gems less, while our own collected is level (-23 +- 64). Where our units diverged
  first (`whofirst.py`), 34 losses turned to wins and 21 wins to losses. Four a side alone (b32p, 30 games) it is
  inside the noise: margin +65 +- 132, 20 against 17 wins.
- **bot_10 runs out of fuel more often** (8.1 and 7.8 events a game on the five-a-side panels b37 and b36p against
  vx1's 6.7 on b37), mostly in rounds 1-3 (world init on the first turn) and after round 30. A turn that runs out
  resumes on the next turn, so this costs turns, not faults: no bot fault in 140 games.
- **Four a side it is a wash in wins.** On a fourth panel (b33p, teams ranked 57-68, 30 four-a-side games) cmb1 and
  vx1 both won 22 of 50, and four a side over b32p and b33p (60 games) the win share went 0.48 to 0.53 (+0.05 +- 0.08),
  flips 10 to 9, while the margin went up 91 +- 88 and both sides died 2-3 more times a game. Five a side is where
  bot_10 helps (b37 + b36p: margin +75 +- 62, flips 27 to 17). Over all four panels (190 games): margin +64.6 +- 40.3,
  win share 0.49 to 0.56.

## Three teams' bots in one program, locally (session 91, 11-01 04:40-07:30 IST, branch night-1101)

Source: local runs only (the user stopped platform tests at 04:36 while the merged team iterates there). Bots: vx1
(`bots/main`), b10n (bot_10 with its log off, `bots/exp/b10n`), bamboo8 (Bamboo Teahouse G3, v1469) and Bamboo's #458
line (`bots/bamboo458` = v1471, `bots/bamboo458sf` = v1472, the Sprint 3 bot, `bots/bamboo479`). Runs:
`data/runs/multi-044220` (bamboo8), `multi-050246` (allocator), `multi-053221` (cmb2, cmb5, cmb6), `multi-061148`
(spell finish), `multi-062416` (the #458 line), `multi-070127` (cmb7); every bot against cand1, cp3, dh3 and the
others on all 70 maps, both sides. Rows bamboo8 to bb458cc; head to head deduplicated in `data/h2h_1101.txt`.

- **Team size follows the map, and five a side carries most games.** Of the 70 maps 42 are five a side, 16 four and
  12 three (`data/map_sizes.json`): 60%, 23% and 17% of games when maps are drawn evenly. Our 150 ranked games under
  vx1 split 63%, 22% and 15%.
- **Each bot is best at one size.** Wins against the same six opponents (the three pool bots plus the other bots),
  paired by opponent, map and side:
  - Five a side bot_10 leads clearly: against the Sprint 3 bot +0.087 +- 0.027 a game (pool 210 of 252 against 183),
    against bamboo458 +0.067 +- 0.028. Head to head it is level with the Bamboo bots (43 to 49 of 84) and beats vx1
    59 of 84.
  - Four a side Bamboo's #458 line leads: the Sprint 3 bot against vx1 +0.052 +- 0.040 (head to head 21 of 32), with
    pool wins level (84 against 87 of 96). bamboo8 beats vx1 head to head too (80 of 128 over four pairings) but
    loses more to the pool (82); the Sprint 3 bot beats bamboo8 21 of 32.
  - Three a side no bot leads: the Sprint 3 bot against vx1 +0.056 +- 0.052 over the six opponents but -0.069 +- 0.067
    against the pool alone.
- **The maps decide head to head, not chance.** Four a side bamboo8 against vx1 is 8 of 8 on 00interlock, 00oasis,
  01hooks and 02guardians and 0 of 8 on 00rushbait-v2, 00swirl and adgato-gemcombat2. A head-to-head count is less
  noisy than its size suggests, but it measures one rival only.
- **Bamboo's bots run out of fuel often, most of all five a side.** Fuel exhaustions a game (fuelExhausted events in
  the game JSON, rounds 3 on; rounds 1-2 are world init): the #458 line 29-31 three a side, 24-26 four and 117-121
  five; bamboo8, with three fuel caches on, 18, 13 and 84; five a side bot_10 3.9 and vx1 2.4. Each exhaustion
  suspends a champion until its next turn. Five a side bamboo8 beats the Sprint 3 bot 49 of 84 head to head, while
  three and four a side the Sprint 3 bot beats bamboo8 (17 of 24, 21 of 32).
- **Bamboo's free-list allocator** (`fastalloc.h`, global operator new and delete; a heap allocation costs about 400
  fuel through wasi-libc malloc) cut vx1's exhaustions from 1.16 to 0.47 a game and its median turn from 28.9k to 24.0k
  fuel, with wins level overall (-0.01 +- 0.02; three and four a side 140 against 147 of 168). In bot_10 it cut
  exhaustions by 0.43 a game, but collected fell to 97.8% and deaths rose 0.54 +- 0.27.
- **Several bots in one program work, but not game for game.** `tools/variant/nsbot.py` wraps a bot's sources in a
  namespace (its `main` becomes `run`, its includes move to the top, calls `::NAME` of its own functions become
  `::NS::NAME`). The global allocator must stay outside every namespace: `src/fastalloc_switch.h` holds it behind a
  switch (off: malloc plus the same 16-byte header, so blocks made before `main` free correctly either way), and
  `main` turns it on only for the bots tested with it. Each size then plays its bot, but the games are not identical
  to the standalone bot's: the other bots' static initialisers and the header move heap addresses and fuel timing.
  The differences stayed within one standard error per size (cmb7: -0.014 +- 0.022, +0.026 +- 0.030, +0.004 +-
  0.013), and no program faulted in 4,340 games (cmb2, cmb4, cmb5, cmb6, cmb7).
- **Bamboo's spell finish** (`kSpellFinish 1`, from Intercontinental Fish's Marcella: a ready single-target damage
  spell at the weakest visible enemy under 30% health or within 0.9 of the spell's damage) is level locally in both
  our bots: vx1 327 to 332 of 420 wins, kills +0.11 +- 0.13, deaths +0.08 +- 0.11; bot_10 -3 of 348, kills +0.04 +-
  0.10. The economy held (collected 100.7% and 100.5%). It is a fight change, so only the platform can judge it.
- **cmb7** (vx1 three a side, the Sprint 3 bot four, bot_10 five; `bots/exp/cmb7`) against the Sprint 3 bot alone:
  +0.091 +- 0.027 a game five a side and -0.069 +- 0.053 three a side over the same six opponents; head to head 66 of
  140 (five a side 43 of 84).
- **bamboo8's three fuel caches in the Sprint 3 bot** (bb458c: `kSightCache`, `kPairWalkCache`, `kScoutWindow`, which
  Bamboo marks as leaving every decision unchanged) cut its exhaustions from 82.0 to 48.7 a game (five a side 117.9 to
  71.2) with wins level (-0.015 +- 0.018) and collected 98.8%. Yet only 6 of 840 games stayed identical: when a turn
  completes instead of suspending, the game moves on a different path, so even a decision-neutral fuel change acts
  like a small random perturbation of each game. A fourth cache, `kCampCache`, added 2.2 +- 0.9 exhaustions a game.
  Five a side the cached bot still trails bot_10 (pool 185 against 210 of 252), so fuel is not the main cause of the
  Bamboo bots' five-a-side gap.
- **The platform rates the Sprint 3 bot higher five a side than our local pool does** (read only: our newest 200 ranked
  games, `tools/platform/ourmaps.py 2 data/ourmaps_1101_0757.json`, split by creation time; size from the draft length).
  Under 1472 (85 games, 05:00-07:50 IST 11-01, while the team rose to rank 44, 2057.3 at 07:55) we won three a side 4
  of 6, four a side 19 of 27 (70%) and five a side 30 of 52 (58%). Under vx1 and fin1 (95 games, 01:10-04:10 IST, rank
  about 65) we won 9 of 16, 15 of 20 (75%) and 21 of 59 (36%). Locally the Sprint 3 bot and vx1 are level five a side
  (pool 183 and 180 of 252, head to head 46 of 84 for the Sprint 3 bot), so our pool (vx1's ancestors cand1, cp3 and
  dh3) understates the Bamboo bots five a side. bot_10's local five-a-side lead over the Sprint 3 bot comes mostly from
  that pool (head to head 44 of 84 at the default fuel; 0.560 +- 0.041 over five fuel values, below), so only the
  platform can confirm its size.
- **Fuel per turn as a seed.** Local games are deterministic, so a pairing on one map and side gives one game. A fuel
  quantum 0.5-1% off the default (`multi.py --fuel 99000`, 99500, 100500, 101000) replays it on another path: bot_10
  against the Sprint 3 bot changed result in 28 and 19 of 84 five-a-side games at 99000 and 99500. Map advantages repeat
  across fuel values, so the standard error is taken over (map, side) clusters.
- **Five a side head to head over five fuel values** (420 games a pairing, runs `data/runs/multi-080001`, `-080156`, `-080355`, `-080556`
  plus the default-fuel games; rule written at 07:59 before the games):
  bot_10 against the Sprint 3 bot 235 of 420, a share of 0.560 +- 0.041 (1.5 standard errors above
  even: the head to head supports bot_10 five a side); against bamboo8 220 of 420, 0.524 +- 0.041 (level). So
  five a side bot_10 is at least level with both Bamboo bots head to head and well ahead against our pool, and
  bamboo8 is the stronger Bamboo bot there (it beat the Sprint 3 bot 49 of 84).
- **Three a side head to head over five fuel values** (120 games, `multi-080809` to `-080908`; rule written at
  08:02): vx1 against the Sprint 3 bot 56 of 120, 0.467 +- 0.077, level. So cmb7 keeps vx1 three a side.
- **Four a side head to head over five fuel values** (160 games a pairing, `multi-081059` to `-081316`; rule written
  at 08:10): the Sprint 3 bot against vx1 104 of 160, 0.650 +- 0.061 (the pick is supported), against bot_10 90 of
  160, 0.562 +- 0.063 (level). So per size the head to head agrees with the pool-based picks of cmb7: vx1 and the
  Sprint 3 bot are level three a side, the Sprint 3 bot leads four a side, bot_10 leads five a side.

## 1472 on the ladder, the draft question and the three-a-side round robin (session 91, 11-01 13:05-13:45 IST)

- **Which bot played a ranked game** is visible in our draft order: the Bamboo line (1471-1473) opens with picks
  (11, 1) five a side and (6, 1) three and four a side; the bot_10 line (1470, 1474-1476) opens (11, 6), and (11, 2)
  three a side (platform pick ids: 0 Ryth, 1 Vesper, 2 Vendetta, 3 Cassi and Issac, 4 Stellar, 5 Prism, 6 Marcella,
  7 Willow, 8 Ren, 9 Varg, 10 Tavi, 11 Heart of Ruin). Bamboo-line games since 23:23 UTC 10-31 (180,
  `data/ourmaps_1101_1310.json`): against teams rated above us (2050 at 13:35) 3 a side 5 of 17, 4 a side 7 of 20,
  5 a side 28 of 58; against teams below 5 of 8, 17 of 23, 37 of 54. bot_10-line games in the same span: 7 of 8,
  8 of 18, 17 of 34 (different hours, so different opponents).
- **Drafts explain little after rating** (`tools/platform/ladgames.py` + `draftelo.py`, 5,325 ranked games of the top
  100 teams since 10-30): result minus the Elo expectation of the side that drafted a champion the other did not is
  within about two standard errors of zero for every champion except Prism (+0.09 to +0.16 at each size), which a
  few teams (SilverSamurai, BBL, :3) drive and which rating lag on rising teams would also produce. Heart of Ruin:
  -0.012 +- 0.026 three a side, -0.042 +- 0.023 four a side, +0.017 +- 0.017 five a side. The common five-pick draft
  above us (Ryth, Vesper, Vendetta, Marcella, Heart; 1,944 sides) scores -0.001 +- 0.011; 1472's four-pick draft
  (Ryth, Vesper, Marcella, Willow) +0.087 +- 0.055. So 1472's weak three and four a side record against teams above us
  is play, not the draft.
- **Three a side round robin** of vx1, the Sprint 3 bot, bamboo8 and bot_10 over five fuel values (120 games a pair,
  `results/analysis/h2h_fuel_1101.md`): every pair within about one standard error of even; the Sprint 3 bot has the
  best mean share (0.567). cmb7 keeps vx1 three a side by the rule written before the run.

## bot_10 on far maps: the team's hybrid 1478 against 1479 (session 91, 11-01 15:40-16:35 IST)

- **The live bot changed under a gate.** A teammate made 1479 ("Bamboo v1472 + pre-started recall + field-first
  guards + wait-avoid 30") live at 15:41:28 IST, 17 seconds after the gate `l1472_b38p` started; its games and a
  second run `l1479_b38p` (15:53, 1479 live throughout) came out identical in all 90 games (result, margin and gems).
  So the whole first run was 1479, and the pinned panel repeats games exactly, as known since 10-25. `gateq_live.sh`
  now leaves a selection made by someone else in place instead of restoring over it.
- **1478 against 1479 on b38p** (nine teams ranked 21-45, opponents pinned; `rcmp.py`): 1478 43 of 90, 1479 30;
  1479 against 1478 L->W 11, W->L 24 (sign test p = 0.04), margin -59 a game.
- **1478's rule, read from its drafts** (`data/picks_l1478_b38.json`): bot_10's draft on every map whose spawn walking
  distance (`data/map_features.json`, `sd`) is 61 or more, Bamboo's on the rest; the b38 maps split exactly between sd
  60 (adgato_gemcombat4, Bamboo) and 63 (01islands, bot_10). 22 of the 70 maps are far: 20 five a side, 2 four a side
  (00rows, 01shortcut), none three a side.
- **Where 1478 gains** (b38p): five a side on far maps 16 of 30 against 1479's 6; five a side on near maps 9 of 26
  for both; four a side 10 of 21 against 12; three a side (1472 in both, 1479's flags on) 8 of 13 against 3.
- **The local head to head agrees** (bot_10 against the Sprint 3 bot five a side over five fuel values, runs
  `multi-080001` to `-080556`): bot_10 wins 133 of 160 games on far maps (0.83) and 58 of 176 on near ones (0.33).
  Per map, bot_10 loses most near maps (exceptions: 00stampede sd 55 8 of 8, 00monolith sd 49 6 of 8) and wins
  almost every far one. So bot_10 belongs on far maps only; cmb7's bot_10 on every five-a-side map gives away the
  near ones.
- **1479's flags locally** (r1479, the bot rebuilt from its note, against bamboo458sf over the same 420 games): wins
  -0.08 +- 0.05 three a side, -0.09 +- 0.05 four a side, +0.04 +- 0.03 five a side.
- **Economy changes do not carry over** (e_c3 on bb458c, e_c4 on r1479): `kElkBonus` 1.0, `kTravelWeight` 1.4 and
  `kLookahead` 0.5 raise captures by 2.8-3.7 a game on either base, but collected gems by +27 +- 16 on bb458c and
  -14 +- 19 on r1479: more small groups, not more gems.
- **Our own copy of the hybrid** (`bots/exp/hy1`): the cmb7 frame with only two parts, bamboo458sf (`src/bb`) near and
  b10n (`src/cj`) far, chosen before the draft by a walking search from our spawn region around walls, holes, altars
  and the enemy spawn (`main.cpp`). A probe build (hy1p) printed the walk on all 70 maps: the far/near split equals
  `sd >= 61` on every map (the walk equals sd on 67 maps). Its source zip is 390.0 KB against 1478's 389.8 KB, so
  1478 probably holds this bot_10 (b10n-sized; v519 and v531 are 2-3 KB larger).
- **1478 against 1472 on a second panel** (b39: nine other teams rated above us, ranks 22-39 at 16:03; a teammate
  had made 1472 live again, so the base is 1472): 1478 32 of 90, 1472 28; L->W 12, W->L 8 for 1478, margin +64 a
  game; five a side far 8 of 22 against 6, near 14 of 31 against 12. Pooled with b38p (where the base was 1479): 36
  against 19, sign test p = 0.03 (`results/analysis/rule_1478_b39.md`).

## Three a side against ranks 18-38: the Bamboo bot farms as a pack (session 92, 11-01 20:20-20:40 IST)

Source: 1478 as live on panel b40 (`l1478_b40@b40`: nine teams ranked 18-38 at 19:55, ten three-a-side games each,
89 decoded), readers `decoded.py`, `cohesion.py`, scratch `cohmap.py` (per map shared camp hits).

- **1478 wins 29 of 90 three a side.** To r1000 it collects 511 gems against 682 and tributes 439 against 584;
  deaths are level (4.4 against 4.2). The 17 ranked three-a-side games of 1472 against teams above us gave the same
  picture (473 against 701).
- **The gap is captures, not fights:** 38.4 group captures a game against 59.4 (own half 24.5 against 34.4, middle 9.0
  against 17.4). A capturer's cycle is 64 rounds (median 37) against 44 (29), with 36.8 moves against 23.9 for the
  same straight hop (9.5 against 9.0). Gem clusters give 112 gems a game by r600 against 181.
- **Our three farm together.** Per camp-hit round a teammate hits the same group 60% of the time against 31% (r0-150
  74% against 50%, r600-1000 still 48% against 23%); a champion has no ally within 6 in 21% of its rounds against
  40%. It is the same at every size (ranked games of 1472 against teams above: four a side 58% against 39%, five a
  side 81% against 47%), but three a side it costs the most: five a side the collection is near level (795 against
  859). Per map the shared share is 51-73% on ten of the twelve maps (00breadcrumbs 2%, adgato_gemcombat1 24%).
- **The other two bots draft like the teams above:** vx1 and bot_10 pick Heart of Ruin, Vendetta and Vesper three a
  side (locally hy3v 66 of 72 games, hy3b 72 of 72), the Bamboo bot Marcella, Ryth and Vesper. Locally against the
  pool, vx1 three a side makes 15.8 more captures a game than the Bamboo bot and bot_10 5.7 more (rows hy3v, hy3b).

## Two small factors: early gold clusters and tribute restart loops (session 92, 11-01 21:10-22:15 IST)

- **A heavier early gold weight moves picks, not totals.** Three a side, raising the Bamboo part's round-0 gold
  weight from 0.3 to 0.45, 0.6 or 0.9 (rows hg3a-hg3c, 72 local games each, paired with hy1) adds 1.6, 2.0 or 3.1
  gold clusters by r300 and removes 0.8, 1.8 or 2.9 gem clusters. Team gold at r300 stays level, collected to r1000
  too. The rivals' 24.9 gold clusters by r300 against our 13.2 (b40) does not come from how we weigh gold against
  gems.
- **Tribute restart loops.** The channel watch (`kChannelWatch`, `tribute_doomed`) cancels a tribute when the
  forecast says enemies within (turns left + 4) tiles kill us before it completes; the start rule (`channel_unsafe`)
  refuses only an enemy within 6 (`kChannelSafe`). A 200-gem bag (20 turns) is doomed by any enemy within 24, so the
  champion cancels and starts again in the same turn, round after round, and banks nothing. `tools/replay/loops.py`
  counts it (a restart is a tribute issued again with the same bag before the earlier channel could have completed):
  - 1478 on b40 (90 three-a-side games): 2.36 restarts a game against the rivals' 0.43; 0.36 episodes, 19.8 rounds
    each, mean bag 204. On adgato_gemcombat1 a 626-gem bag looped 110 rounds (r1194-1304) with 798 banked; that game
    was lost 798-850.
  - 1478 on b38 (90 games, all sizes): 2.47 restarts a game against 0.17; 0.32 episodes, 29.3 rounds each, bag 211.
    Of the 29 episodes 7 banked within 150 rounds, 6 ended in a death and 8 were still open at the game's end.
  - 180 ranked games of 1472: 0.48 episodes a game; 11 of 86 ended in a death. Locally hy1 restarts 5.72 times a
    game against the pool (0.58 episodes, 26.9 rounds each).
- **Both fixes end the loops locally** (90 games against cand1, cp3 and dh3): trA (the Bamboo team's own
  `start_doomed` fix, `kReviewFix` 1) 0.34 restarts a game, trB (`kKeepChannel`: keep a channel that the start rule
  would restart at once) 0.11. Deaths, gems lost on death and collected stay level; tributed to r1000 628 and 634
  against 633. The local pool makes small bags, so only the platform can show what the loops cost.
- **On the platform the loops end too** (trB, upload 1485, 180 games on b38p and b40p paired with 1478's): restarts
  2.41 to 0.09 a game, rounds stuck per game 8.3 to 0.7. Gems lost on death (+3.4 +- 6.8) and tributed to r1000
  (-6.4 +- 13.7) are level; deaths to r1000 +0.31 +- 0.23, all of it outside channels (deaths while channelling 0.06 to
  0.05 a game). Wins 68 of 180 against 72 (not judged).
- **A rarely used branch leaves the pinned games unchanged.** On the 20 games of hy1_b38q, trB (hy1 plus the one
  condition) replays hy1's games exactly to r1000 (deaths and both tributes in 20 of 20), while hy1 against 1478 (the
  same bot built from other sources) differs in 15 of 20 results. A variant is therefore best paired with a run of its
  own parent build on the same pinned panel: only the games where the change acts differ. Pairing with the team's
  build (1478) adds the build's own spread (here +0.25 deaths a game on 20 games).
- **Against its own build the fix is clean** (trB against hy1, both on b38p and b40p, 180 pinned games, 11-02
  00:50): 23 games differ, 13 better and 10 worse, one flip each way, margin +13 a game; to r1000 deaths +0.01 +-
  0.04, tributed +1.4 +- 2.5. Most of the gain is on 00anvil (five of six changed games better, 200-gem monolith
  bags banked instead of looped). The loops cost little on average: about one game in eight changes, and the result
  of about one in ninety.

## Five a side on near maps: weaker camp hits, and 00monolith (session 92, 11-02 01:30-02:45 IST)

- **Where the games are.** Of our 225 ranked games since 1478 went live (to 01:37 IST 11-02,
  `data/ranked_1102_0137.json`), 146 were five a side (65%; 71 won), 46 four a side (24 won), 33 three a side (15).
- **Five a side on near maps is the weak cell** (`l1478_b38@b38`, nine teams ranked 21-45): 9 of 26 won, against 16
  of 30 on far maps five a side (bot_10) and 8 of 19 four a side near. To r1000 in the 26 games: gems collected 705
  against 828; group captures 33.5 against 46.7, the gap in our own half (17.9 against 30.1) and late (r750-1000: 4.4
  against 9.8); deaths level (6.9 each).
- **Camp time is level, camp damage is not** (`tools/replay/campdmg.py --size 5 --near`): camp-hit champion-rounds
  794 against 811, camp health taken 60.9k against 80.8k, so 76.6 per champion-round against 99.7. We stack more
  (2.26 hitters per camp-round against 1.50) and our lone hits are weaker (89 against 128). By champion, lone hits:
  our Willow 70, Heart of Ruin 57, Vesper 115, Marcella 119, Ryth 115; theirs Vendetta 177 (drafted in every game),
  Vesper 180, Ryth 134, Marcella 115, Heart of Ruin 62. On far maps (bot_10, which drafts Vendetta) the gap is small:
  82.3 against 86.6 per champion-round, our Vendetta 162 a hit against their 124. Four a side near: 71.3 against
  84.2, lone hits 93 against 99, so there the gap is the stacking.
- **Gold.** Team gold five a side (all maps, `decoded.py gold`): 0.90 of theirs at r300, 0.85 at r600, 0.76 at r1000.
  Their Vesper earns 911 camp gold to r600 against our 587 (`decoded.py champs`, all sizes) and completes her first
  emblem at r201 (Prospector of strength in half the games) against ours at r286 (Treasure of strength in 57%;
  `emblemorder.py vesper`).
- **Vendetta in Willow's place fails locally** (dv5, five a side near maps against pool/cp3 and pool/bot_10, 24 games):
  deaths 102 to 162, wins 18 to 14, collected 984 to 888 a game; four a side (bd2) it also lost locally. Willow's
  healing probably matters more to the Bamboo bot than the damage gained.
- **The worst ranked maps by part** (`results/analysis/rule_route.md`, `tools/local/routemaps.py`, 16 local games per
  map and bot against eight pool bots): bot_10 is far better than the Bamboo bot on 00monolith (14 of 16 against 8;
  ranked, the Bamboo bot won 0 of 12 there), and better without clearing the bar of 5 wins on 01yellow_brick_road
  (9 against 5), 01boss_battle (12 against 10, margin +695 against +217) and adgato_gemcombat5 (14 against 13). On
  the far maps bot_10 plays, the Bamboo bot is worse (00expanse 8 against 12, 01big_world 4 against 13, 01fracture 4
  against 8), so their ranked losses do not come from the routing. 01elk_arena belongs to Bamboo (13 against 6).
- **hym** (hy1 with 00monolith routed to bot_10, found by width, height and spawn walk) locally: 00monolith 4 of 16
  to 14 of 16, every game on the other 50 x 50 maps unchanged.
- **A platform group must hold five different maps** (HTTP 400 "Choose exactly five different maps"), so a one-map
  panel gives one game of that map per group.
- **Ranked API champion ids are not the engine's order.** `draftPicks` in the match list uses its own ids: our
  five-a-side drafts in the 1478 era were (11, 1, 0, 6, 7) on near maps (Heart of Ruin, Vesper, Ryth and Marcella /
  Willow in decoded replays) and (11, 6, 2, 1, 7) on far maps (bot_10: with Vendetta = 2). `decoded.py`'s `NAMES`
  (engine order) must not be used on API ids: 0 Ryth and 2 Vendetta agree, but 6, 7 and 11 are Heart of Ruin,
  Marcella and Willow in some order (Prism, Marcella and Tavi in the engine).
- **New maps and a new live bot (11-02 02:20-02:30 IST).** 15 maps named `03...` joined the ranked pool (85 in all);
  1488 (a teammate's bot_10 build) went live at 02:26 and drafts (11, 6, 2, 1, 7) on near maps too.

## The teammate's 1497 and 1498 against ranks 1-20 (session 93, 11-02 15:00 IST)

- **Data.** The teammate tested each upload on one panel of 33-35 groups against teams ranked 1-20 (Mite, Intercontinental
  Fish, Univardisty, newer team, Ad Astra, NEETCoders, test4, print dont int, German Empire, policy wonk, prism best
  girl, Supaswag). Groups found by creation time in `cambc matches list` (1497: 08:16-08:22 UTC, 1498: from 08:51 UTC,
  other teams' challenges left out), logged in `results/gate.log` as `t1497_tm@tm` and `t1498_tm@tm`, decoded into
  `data/fights/`. Source of both bots is not in this repo (v548 line, bot_10 build).
- **Wins (decoded summaries):** 1497 26 of 175 (3 / 4 / 5 a side: 4/33, 6/40, 16/102); 1498 19 of 165 (2/33, 2/38,
  15/94). The match list's `result` field gave 34 for 1497; not reconciled.
- **The gap is gold, then items, then fights.** 1497: team gold 0.66 of the rivals' at r300, 0.57 at r600, 0.51 at
  r1000 (four a side 0.40); deaths 9.3 against 4.1 a game to r1000 (2.8 against 1.3 by r300); collected 568 against
  907. With our deaths to r300 at or below theirs we won 21 of 74 games; with one or more extra, 5 of 101.
- **Even fights.** P(death within 10 rounds) at high health with one enemy within 6 is 0.045-0.054 for us against
  0.011-0.015 for them, whatever the allies near (both bots). Fights the rivals start: the starter loses 0.19, kills
  0.66 per start; they cause 5.3 of our 9.3 deaths a game.
- **Farming by champion (to r600, camp gold).** 1497: Vesper 495 against 1489, Marcella 593 against 1042. 1498
  ("Vesper captures the gold groups she helped kill") lifts Vesper to 977 (rivals 1388) and her max health at r600
  from 1372 to 2234 (rivals 2608; she now builds Bruiser like them), but deaths (9.0), collected (566), team gold
  (0.64 at r600) and the even-fight death risk do not move. Marcella stays at 520 against 1064 and 1624 health against
  2602 (theirs bruiser_focus first, ours prospector_focus).
- **Willow** (drafted in 142 of 175 games; rivals 52) dies 2.4 a game, 19 gems and 1185 champion damage; attacked at
  half health or more she dies within 10 rounds 45% of the time.
- **Source (11-02 15:35 IST).** The platform's submissions page shows each version's code (`/api/v1/submissions/<id>/files`
  and `/file?path=...`, browser session). 1497 and 1498 are now in `bots/pool/v1497` and `bots/pool/v1498`; both build
  with `--release`. They differ only in `bot.h`, `farm.cpp`, `fight.cpp` and `params.h` (1497: `P_FIRE_FIRST`; 1498:
  `P_VES_HANDOFF`). Builds are `P_BUILD 4` with `P_PROSP_FIRST 1`: Marcella buys Prospector focus, then jungle focus,
  durability health and monster focus before any Bruiser emblem, which matches her low health at r600.

## How the teammate chejibt001 works, and what their uploads 1488-1502 show (session 94, 11-02 19:30 IST)

- **Method.** One frozen base, v548 (upload 1490: v546 + Willow heals by missing health + proactive self shield),
  and each upload is "v548 + one change", every change behind a `P_` flag in `params.h` and each with its own
  replay-analysis script named in the flag's comment (`shortcuts.py`, `firefirst.py`, `vhandoff.py`). Every upload
  is played at once in 135-345 unranked games (35-70 groups) against the same 15-22 teams, many of them ranks 1-20;
  a change that touches one team size (the drafts of 1501 and 1502) is tested mostly on that size. The shared quota
  (50 groups an hour) is almost all theirs: 3350 unranked games from 11-01 22:00 to 11-02 13:20 UTC, 48 of 50 used
  at 13:20 UTC. Uploads and notes: `cambc submissions list --json`; source of the v548 line is not in the repo
  except `pool/v1497` and `pool/v1498` (bot (1).zip is 1498, same size).
- **Their results, paired with 1490 on the same (opponent, map, side)** (`tools/platform/teamvers.py
  2026-11-01T20:00 1490`; version given by upload time, not proved): only 1491 (v559, dash bridges over holes and a
  spawn flash) is clearly ahead, 45 against 34 of 119, 23 losses turned to wins and 12 back. Its narrower copy 1492
  (central-altar maps only) is level (14 against 15 of 47). Level: 1489, 1498 (handoff, 40 against 43), 1499 (recall
  home, 51 and 51), 1500 (earlier bank, 48 against 49). Behind: 1493 (Vesper task values, 40 against 47), 1496
  (mstrike, hold, lock intercept, 34 against 44), 1497 (Marcella nukes, shoot then dash, 34 against 40). Draft
  changes: 1501 (three picks, Marcella for Vendetta) 0 against 5 of 14 and dropped; 1502 (four picks, Heart of
  Ruin, Marcella, Vesper, Willow) 10 against 6 of 17, live since 12:58 UTC.
- **Which files each upload changes** (hashes of the website's code viewer against 1490): 1500 only `params.h`;
  1501 and 1502 only `draft.cpp`; 1493 `farm.cpp` and `params.h`; 1497 `fight.cpp` and `params.h`; 1498 `bot.h`,
  `farm.cpp`, `params.h`; 1489, 1496 and 1499 `bot.cpp`, `bot.h`, `fight.cpp`, `params.h`; the dash-bridge line 1491,
  1492 and 1503 seven files (`bot.cpp`, `bot.h`, `farm.cpp`, `nav.h`, `params.h`, `world.cpp`, `world.h`).
  `pool/v548` is the exact 1490 source (all 13 files match the website's hashes): `bot.cpp` and `fight.cpp` of 1498,
  `bot.h` and `farm.cpp` of 1497, and 1498's `params.h` without its handoff block.
- **What we copy and what we add.** We take their base and their one-flag-per-change rule (`pool/v1502r` rebuilds
  1502 from the 1498 source: `P_VES_HANDOFF 0`, which turns every handoff line off, and the four-pick draft, which
  matches the website's `draft.cpp` of 1502 apart from a comment). Their tests are not pinned, so the opponents
  may change bots between a version and its base; ours pin the panel to the base's own games (`pin.py`), so every
  game is paired exactly, and a variant goes to the platform only after a local pass. Open lead: v559's dash bridges
  are the one change of theirs with a clear paired gain and are not live; its source is needed from the teammate.
- **The gap against ranks 1-20 is dead time** (1497 and 1498 on the teammate's panels, 340 games to r1000,
  `budget.py 1000`, `clears.py`): our champions are dead in 14.2% of champion-rounds against 6.2%, hit camps in
  14.7% against 18.7%; they capture 50.4 groups a game against our 31.5 with the same hitters per capture (1.74
  against 1.61) and about the same clear times. Deaths per game are about double theirs in every round band
  (`early2.py`: r0-100 0.75 against 0.39, r500-1000 4.22 against 1.89); outnumbered deaths 3.53 against 1.21
  (`packs.py`), and after a pack sighting we die within 15 rounds 0.129 of the time against 0.054.
- **One cast kills our carries** (1503 against ranks 1-20, `t1503_tm@t03`, 170 games to r1000). Every type of ours
  dies 2-2.7 times as often as the same type of theirs (`decoded.py types`: Heart of Ruin 2.02 against 0.76,
  Marcella 1.79 against 0.68, Vendetta 2.39 against 0.95, Vesper 1.82 against 0.89, Willow 2.36 against 1.00). With
  one enemy within 6 and none of ours, at half health or more, we die within 10 rounds 4.9% of the time against
  1.5% (`decoded.py risk`). The traces (`deftrace.py vesper`, `vendetta`) show the rivals' Marcellas (1700-4000
  max health) killing our 1000-health Vesper and Vendetta with one cast from 4 tiles while ours walk at 4-6 tiles,
  at r436-r763. At r600 (`decoded.py items`) their Vesper has 2621 max health (3.4 Bruiser-strength and 1.4
  Bruiser-health emblems) against our 1309 (Prospector, Jungle), their Marcella 2479 against 1797, their Heart of
  Ruin 1724 against 1333.

## Early massacres, pack fights and Vesper's gold (session 94, 11-02 22:20 IST)

All on `t1503_tm@t03` (1503 against ranks 1-20, 170 games, 37 won).

- **A third of the games are decided by r300.** 64 games are massacres (our deaths minus theirs by r1000 is 6 or
  more) and we win 1 of them; by r300 we have died 4.83 times in them against their 1.50, with team gold 625
  against 1607 (`deathfactors.py`, `UPTO=300`). In the 82 even games we win 34. By our deaths minus theirs to
  r300, we win 32 of 83 games at 0 or less and 5 of 87 at +1 or more (`early2.py`). The massacre deaths come in our
  own half (44%) or the middle (39%), to 3 or more killers (46%) with 4 or more enemies within 6 in the contact
  (49%), at full health when it starts (79%), and the killers were in sight 11-30 rounds before the death (82%).
- **After sighting a pack we choose as they do, but lose the fight.** A champion with at most one ally within 6
  that sights 3 or more enemies within 8 (`tools/replay/packmove.py`): over the next 5 rounds we go home 18% of the
  time (they 17%), away 13% (13%), toward the pack 29% (33%) and hold 39% (38%); when holding or going toward it we
  die within 15 rounds 19% of the time against their 7-9%. We meet such packs 3.0 times a game against their 1.7.
  The gap is fight strength (items, health) and isolation, not the retreat decision.
- **The gold gap starts at r100 and sits with Vesper and Marcella.** Team gold at r100 is 265 against 372 (0.71),
  at r150 437 against 621 (`decoded.py gold --round 100 150`). Camp gold by r150 (`decoded.py champs`): their Vesper
  263 against our 97, their Marcella 195 against 117, while our Heart of Ruin (91 against 71) and Vendetta (127
  against 85) earn more than theirs. Their Vesper's first capture is at r44 (median) against our r83, and by r150
  she takes 1.32 captures a game of groups that two or more teammates hit (102 base gold each) against our 0.43
  (59 gold; `tools/replay/soloshare.py`). Her first emblem comes at r175 against our r314, the fourth at r369
  against r540 (`emblemorder.py vesper`). In the early traces our Vesper walks up to 53 tiles alone to a gold group
  or chips wolves alone and leaves without the capture; theirs moves with 3-5 teammates, the team kills an elk or
  wolf group, and she captures it.
- **More caution in fights costs kills and farming on the platform.** h1503 (whc's thresholds on 1503) on t03p,
  pinned to `t1503_tm@t03`: our deaths -0.6 +- 0.4 a game but the rivals' -0.9 +- 0.4, collected -31 +- 16,
  margin -70 +- 29, 28 wins against 37. Locally it had passed with deaths -0.52 +- 0.21 and collected +5.4.

## The economy gap is an early-contact gap (session 94, 11-02 23:50 IST)

On `t1503_tm@t03` (`tools/replay/firstcontact.py`), by the round of first contact (a champion of ours within 4 of an enemy):

| contact by | games | wins | deaths to r100 us/them | to r300 | team gold r150 us/them | r300 | within 8 at contact us/them |
|---|---|---|---|---|---|---|---|
| r20 | 35 | 2 | 1.40/0.80 | 4.29/2.37 | 342/668 | 743/1534 | 3.6/3.9 |
| r40 | 44 | 4 | 1.00/0.61 | 3.52/2.09 | 342/542 | 703/1295 | 2.8/2.7 |
| r60 | 25 | 7 | 0.96/0.04 | 2.84/1.60 | 367/615 | 852/1263 | 2.4/2.4 |
| r90 | 18 | 5 | 0.61/0.22 | 2.17/1.28 | 481/631 | 1044/1367 | 2.1/2.3 |
| r150 | 21 | 9 | 0.05/0.00 | 0.81/0.81 | 651/639 | 1397/1551 | 2.1/1.5 |
| later | 23 | 10 | 0.04/0.00 | 0.35/0.57 | 581/663 | 1321/1477 | 1.9/1.4 |

- Without early contact our economy matches theirs. Numbers at the contact are even; what follows is not. Our champion dies first by r100
  in 68 games (7 won), theirs in 21 (4 won).
- Before r150 (`tools/replay/nearact.py`), away from enemies both sides farm alike (27-28% of rounds hitting camps, 79 and 86 gold per 100
  rounds). The rivals spend 23328 champion-rounds outnumbering us locally, we 13106; we are outnumbered in 7585 rounds at 1.57 deaths per
  100, they in 3494 at 1.03. Within 3 tiles of an enemy they hit a champion 51% of the rounds against our 45% and step away 19% against 25%,
  and die 0.96 per 100 rounds against 2.13.
- By r100 in massacre games our deaths are 66% outnumbered, 57% to three or more killers, 58% after walking out or across, Vendetta first
  (`deathfactors.py`, `UPTO=100`). Local screens cannot show this: the pool does not rush.

## Per-map differences between our bot lines, and Cassi and Issac (session 94, 11-03 01:20 IST)

**The two lines differ a lot per map, and local agrees on many of them.** `tools/platform/mapstrat.py` (since 10-31 23:00 UTC, ranked and unranked, Bamboo line minus bot_10 line within the same opponent, 9250 games):

| Bamboo ahead | points (z) | | bot_10 ahead | points (z) |
|---|---|---|---|---|
| 00interlock | +53 (4.6) | | 00expanse | -59 (-4.0) |
| 00fragment | +39 (3.8) | | 01islands | -36 |
| adgato_gemcombat1 | +32 (3.7) | | 00ambush | -31 |
| 02crossing | +29 (2.9) | | 02the_pack | -26 |
| 00corners | +31 (2.8) | | 02famine | -36 |
| 00anvil | +22 (2.7) | | 00lanes | -52 |
| 00dunes | +32 (2.5) | | 00monolith | -34 |
| 02stalactites, 00quadrants, 00collision | +25, +23, +18 (1.9) | | 02tangle, 02cuts | -33, -36 |

Near maps sum to +2.5 +- 1.6, far maps (spawn walk 61 or more) to -16.1 +- 2.8. Maps both lines lose (8-30%): 00packs, 00elkring, 01boss_battle, adgato_gemcombat5, 00swirl, 00gem_fields, 01elk_arena.

Locally (`routemaps.py`, 4 pool bots, 8 games a map) Bamboo #458 is 0.17 wins a game below v1503 overall, but it is ahead on the same near maps: 00crater 8/8 against 4/8 (margin +800 against +138), 02stalactites 7 against 4, 01corridors 8 against 5, 02crossing 7 against 4, 03one_gem 7 against 0, 00corners 8 against 6. v1503's wins on 03one_gem are 0 of 8, with a margin of -31: it barely scores there.

**The router `exp/rt1` passes locally.** One program, two bots, picked once from a map signature read before the draft (16 maps to Bamboo, the rest and unseen maps to v1503). 680 paired games against v1503: wins +0.05 +- 0.01, deaths -0.39 +- 0.16, collected +9.3 +- 7.1, no fault (`data/judge_screen_rt1.txt`). The bar and the table rule are in `results/analysis/rule_route2.md`.

**Early contact decides most games against ranks 1-20, and it is not an item gap at first.** On `t1503_tm@t03`, 79 of the 170 games have a contact by r40, and we win 6 of them. Nobody has an emblem by then, so the fight is draft and numbers. Examples of the list (`firstcontact.py`): 00stampede r24 one of ours against four, 00contest r17 three against five, 00road_of_riches r36 one against three.

**We do worst against a rival Cassi and Issac (one pick, two bodies).** Same games, five a side: against the pair we win 3 of 34, deaths to r300 3.35 against 1.18 (their count includes both bodies); against other drafts 22 of 65, 2.09 against 1.46. Four a side 3 of 19 against 4 of 20; three a side 2 of 11 against 3 of 21. Teams differ, so this is a lead. Against the pair our hit rounds fall on Issac 19.6 a game and on Cassi 7.8, of 118 (Cassi 600 + 65 health against Issac 900 + 80, and either death kills both), and the pair dies 1.55 times a game. Our target rule and fight simulation do not know the link.

**The two top teams field the pair now.** Ranked games of the top 50 teams, 11-02 05:50-19:30 UTC, 10780 games (`ladgames.py`, `mapdrafts.py --top 12`): Fish plays Heart, Marcella, Vendetta, C&I, Willow on five (90 of 133) and Mite Heart, Marcella, Vendetta, C&I, Vesper (176 of 271 with NEETCoders); on four picks both play Heart, Marcella, Vendetta, C&I. On three picks Heart, Marcella, Ryth stands out (42 of 63, +17.0 +- 5.9 against Elo; Univardisty and T1), against Heart, Vendetta, Vesper, our set (54 of 96, +0.1 +- 4.9). Residuals against Elo are small for most drafts: a draft carries the rest of its team's bot, and a team that climbed lately looks worse than it is.

**Emblem timing.** Vesper's first emblem at r314 against r175 (`emblemorder.py`); Marcella's r258 against r195; Vendetta and Heart level (r251 against r256, r282 against r284).

**How the teammate's team worked on maps (`docs/bamboo/knowledge/fish-builds-1031.md`, read 11-03).** Fish's jump in late October (52% to 79%, mostly against the top 10) came with a first emblem chosen per map: Capture first on 46 of 64 maps, main-stat Prospector first on 9 cluster-farm maps, Prospector of health or focus on 9 others, and one draft per map. Bamboo's copy of the emblem lines alone lost (45 against 54 of 250), so the gain seems to need the whole system. v1503 opens Prospector on every map and never buys Capture.

## The pack opening helps where contact comes early (session 94, 11-03 02:05 IST)

Local, 680 games paired against v1503 (`results/analysis/rule_pack.md`, `tools/local/lnear.py`). `exp/vpk1` walks as one team before r60 on every map: one group, no travel dash, front-runners wait. It takes our spread at r16 on 00contest from 13 to 5 tiles and allies within 6 from 2.0 to 4.0.

| | wins | deaths ours minus theirs r100 | r300 | team gold r150 |
|---|---|---|---|---|
| near maps (spawn walk under 61), 384 games | -0.010 +- 0.026 | -0.26 +- 0.08 | -0.38 +- 0.15 | -17 +- 14 |
| far maps, 176 games | -0.051 +- 0.040 | -0.01 +- 0.06 | +0.05 +- 0.14 | -86 +- 17 |

On a far map the pack only costs gold, since no contact comes that early. `exp/vpk2` gates every part on near maps: deaths r300 -0.21 +- 0.09 over all games, collected -3.5 +- 9.6, wins -0.007 +- 0.016; by team size, deaths r300 three a side -0.28 +- 0.17, four a side -0.72 +- 0.31, five a side -0.02 +- 0.10. Games on far maps still changed on some maps (02tangle, 00lanes, 00expanse, 02harvest, 01starvation: all 8), with gold r150 -10 +- 5, though every behaviour change is off there. The added distance field in `World::init` is the likely cause: it shifts where the fuel runs out in the first turns.

**The bot's own spawn distance** (`P_CENTRAL_MIN_STEPS` style, walls and camp tiles blocked) matches `data/map_features.json` on the maps both hold. On 01boss_battle and 03fan the spawns are not connected on foot (65535); 00reverse_spiral and 00rushbait_v2 read 1 and 02treasure_box 4: those spawns really touch, and both teams are within 3 to 5 tiles of each other at r4 (traces on `t1503_tm@t03`).

**vtg70 did not move the target on the platform.** Scoring each group as if alone until r70 leaves the first 16 rounds as they were, so the team still splits: 170 games pinned to `t1503_tm@t03`, deaths r0-100 0.74 against 0.74, deaths -0.1 +- 0.3, margin -21 +- 30, 34 wins against 37.

**Fights held longer lose more bodies locally.** `exp/wag1` (`P_HOLD_C` -0.8, `P_AVOID` -1.0, the other direction from h1503): deaths +1.01 +- 0.23, wins -0.02. Caution lost margin on the platform and boldness loses bodies locally, so v1503's thresholds stay.

**A gate can be voided half way.** On 11-03 01:37 the first 35 games of `v1472_b1p` were 1472 and the last 25 were 1513: a teammate selected 1513 at 20:07 UTC. The draft tells them apart (`matches list`, `draftPicks`: Ryth is the Bamboo line). Those 35 games: 7 wins against 4 for v1503, margin +153 +- 96. The other five groups are `results/panels/specs_b1pb.txt`.

## The exact Bamboo bot beats v1503 on the routed maps, pinned (session 94, 11-03 03:05 IST)

`v1472` against `v1512` (v1503) on panel `b1p`, 12 teams above us on 15 candidate maps, 60 games pinned to the same opponents' bots (`v1472_b1px@b1p`: the first 35 games of `v1472_b1p`, then `v1472_b1pb`, since a teammate selected 1513 during the last 25): 21 wins against 13, margin +186 +- 84 a game.

| Map | z (`mapstrat.py`) | wins base to v1472, 4 games each | margin a game |
|---|---|---|---|
| 00dunes | 2.5 | 1 to 3 | +797 |
| 00corners | 2.8 | 0 to 2 | +603 |
| 02crossing | 2.9 | 0 to 2 | +590 |
| 00anvil | 2.7 | 0 to 1 | +405 |
| adgato_gemcombat1 | 3.7 | 0 to 2 | +392 |
| 00fragment | 3.8 | 0 to 1 | +378 |
| 00interlock | 4.6 | 1 to 2 | +367 |
| 00gemfight | 1.5 | 1 to 2 | +638 |
| 01corridors | 1.5 | 1 to 1 | +148 |
| 00quadrants | 1.9 | 1 to 0 | +41 |
| 00collision | 1.9 | 1 to 1 | -30 |
| 00crater | 1.3 | 1 to 1 | -282 |
| 02treasure_box | 1.4 | 1 to 0 | -294 |
| 00rows | 1.7 | 3 to 2 | -450 |
| 02stalactites | 1.9 | 2 to 1 | -508 |

The rule written beforehand (`results/analysis/rule_route2.md`) keeps the seven maps with z of 2 or more, none of which fell behind, and adds none with z under 2 (00gemfight is ahead by one game, the rule asked for two). On those seven: 2 wins against 15 of 28. `exp/rt2` holds that table; the pinned panel `r7p` (those seven maps, the same 12 teams) tests the router itself against `v1512`.

**Capture-first lines lose gold in our bot.** `exp/vbd1` and `exp/vbd2` (`results/analysis/rule_build.md`): team gold r300 -26 and -34, wins -0.04 and -0.05 over 680 paired games. Bamboo's copy of the same lines also lost on the platform (45 against 54 of 250). The lines need the team's whole farming system; our bot does not capture more for owning the item.

**The pre-started recall.** Bamboo's notes (`docs/bamboo/knowledge/recall-cycle-1031.md`, `bot-status.md`) measure it as about one round per trip home; it lost in every ladder test, and the safe form is neutral locally. It is not a gap worth a port.

## Gem-poor maps, the 03 maps and what the router gained (session 94, 11-03 05:30 IST)

**The router's table holds on the platform.** `rt2_r7p@r7p` against `base1503_r7p@r7p`, pinned, 60 games on the seven routed maps: 15 wins against 8, flips 9 against 2, margin +152 +- 63. Those maps are about 8% of ranked games, so the gain is about 3 to 4 points of win rate overall.

**A log costs real fuel.** v1503's per-turn compact log is 5-10k fuel a turn. Without it (`exp/vnl1`, local, 680 paired) exhausted turns fall from 9.78 to 6.79 a game, gold r300 +31 +- 11, collected +15 +- 7. The Bamboo bot has no per-turn log, but it uses 44-53k fuel a turn against about 27k for v1503, and it has 27 exhausted turns a game on the routed maps (00corners 66, 00dunes 70, 02crossing 43) and 100 on the other maps.

**The t03 base is lucky.** `t1503_tm@t03` has 37 wins and margin -398; the three variants on `t03p` have 28, 34 and 30 wins, mean margin -455. A comparison against that base runs about 6 wins and 57 margin too low; compare with the mean of the variants too.

**Local per-map differences predict the platform across bot lines, not within a line.** Per map, Bamboo minus v1503 in local margin against Bamboo minus bot_10 in `mapstrat.py`: correlation 0.46 (wins 0.54) on 68 maps. The same correlation for vtg70 and vpk3 against their base on `t03p` is 0.0 to 0.17. So a map table over different lines is worth testing, and a table of small parameter changes needs its own platform check.

**15% of ranked games are on 03 maps, which no panel held.** 90 of 600 games on 11-02: 41 wins (46%, against 53% overall). By map: 03one_gem 1 of 9, 03fan 0 of 3, 03honeycomb 1 of 6, 03shrines 1 of 5, 03twisty 2 of 6, 03showdown 2 of 5, 03contours 2 of 5; 03reef 5 of 6, 03membrane 4 of 6, 03riverbed 4 of 6, 03colosseum 8 of 13. Decoded in `data/fights/q03b`. Only 03one_gem is clearly bad; the others are small samples.

**03one_gem is a special case.** The map holds one gem cluster group (7 gems, at the centre, 25,20) and 80 gold clusters; 2000 rounds play out and the score decides. v1503 gets 0 to 22 gems; its first capture comes near r700, since nearby gold clusters always score higher per step. Rivals get 104 to 197 (SquidProxyLovers from r123, every 70-80 rounds, 189-0). Locally v1503 wins 0 of 16, Bamboo 7 of 8 (130-8 against v1503, first capture r190).

**Gem income per map explains where we lose worst.** `data/map_rates.json`: per map, the sum over camps of gems / (respawn + 8). Under 2.5 gems a round (01elk_arena, 00fragment, 01hooks, 00ribs, 00oasis, 02arena, 00galaxy, 00quarry, adgato_gemcombat1, 00anvil, 01gold_rush): against ranks 1-20 (`t03`) 9 wins of 112, collected 272 against 808, deaths to r1000 14.4 against 5.0. Above: 25 to 34% wins on most bands. In ranked games on 11-02: under 1.5 gems a round 11 of 39, 1.5-2.5 28 of 66, everywhere else 53-64%. This is about 18% of games.

**How 01elk_arena goes (`t1503_tm@t03`, 63338fce).** The centre group (2 elks, 6 gem clusters, 72 gems, 19 steps from spawn) is the map's only gem income worth having; 54 gold clusters lie around it. At r30 we have five champions at the centre, 0 gold and hurt from the elks (Vendetta 350 of 1000); the rivals have sent two to the centre and three to gold (106 gold), and they win the fight, capture from r89 and hold it to the end, 973 to 0. Locally `exp/vlc1` (clusters count 1.5 times before r150) gives +451 gold r300 on this map.

## The first 100 rounds, the gold accounting and who takes the captures (session 94, 11-03 07:00 IST)

All on games against ranks 1-20 (`data/openmap_t03.txt`: 510 games; gold accounting on `h1503_t03p@t03p`; captures on `t1503_tm@t03`).

- **The opening.** Hits on camps to r100 (us / them): wolves 33 / 56, elks 44 / 48, gem clusters 10 / 14, gold clusters 11 / 14, golems 5 / 3. Team gold r50 87 / 144, r100 250 / 373, r150 409 / 613. First reward r50 / r32, third r91 / r64. Deaths to r100 0.71 / 0.34. First group per champion (`tools/replay/firstgroups.py`): first hit r25.3 / r23.1, the nearest group 0.28 / 0.37, a wolf 0.18 / 0.29, an elk 0.48 / 0.37, largest crowd 2.94 / 3.46.
- **Where the gold gap comes from.** Nominal camp-kill gold against team gold, us / them: r50 124 / 136 against 87 / 144; r100 246 / 292 against 254 / 372; r300 747 / 986 against 936 / 1432. So the r300 gap of 496 gold is about 239 from camps, 130 from kill gold (deaths to r300 2.4 / 1.1) and 127 from a higher realized share (Vesper's +33%): realized over nominal after kill gold is 111% / 121%. Kills to r300: wolf 5.4 / 7.3, elk 2.5 / 3.6, gem cluster 13.5 / 18.5, gold cluster 15.4 / 18.1. Time to claim and to clear is equal (7.7 and 13.2 / 12.9 rounds).
- **Big captures go to other champions.** Rewards of at least 60 base gold by r150 (scratch `capwho.py`, teams with a Vesper): ours go to Vendetta 0.89 a game, Heart of Ruin 0.79, Marcella 0.64, Vesper 0.36 (2.7 in all); the rivals' to Marcella 1.13, Vesper 1.11, Heart of Ruin 0.45, Vendetta 0.41 (3.5 in all). The capturer is under 45% health in only 6-13% of the events on either side, so a hurt capturer is not the cause. When someone else takes one, our Vesper is within 6 tiles in 19% of the events and theirs in 32%; within 12 about 55% on both sides. Vesper's gold by r300 is 232 in 2.8 captures against 629 in 5.5.
- **Changing routes alone loses gold locally.** Wolf-first (`vwf1`-`vwf3`) lowers team gold by 27-53 at r150 and 57-104 at r300; a detour to harmless groups on the way (`vdt1`, `vdt2`) moves nothing; shorter waits for the tank (`vpw1`, `vpw2`) move nothing or lose gold; Vesper's capture weight alone (`vcv1`) gives almost the same games, because the weights already favour her when she is there. The difference is that she is usually not there.
- **Same situation, worse result.** `decoded.py assist`, ahead and joining: a teammate dies 0.22 / 0.05, enemies die 0.25 / 0.64. `tools/replay/castfate.py` at equal numbers near: every type dies about 3 times as often and kills 2-3 times less (Vendetta's dash 0.15 / 0.05 self, 0.12 / 0.30 kills). Even fights r60-150 that they start (`tools/replay/fightband.py`): we lose 0.24 bodies, they 0.02. By r800 on `q5m` we deal 9005 damage and die 4.9 times, they deal 10611 and die 3.2 times; maximum health per body r150-400 1049 / 1228, r400-1000 1439 / 2168.
- **Map cases.** 00vault: spawns in corners, 40 gem clusters at the centre worth about 343 gems. A rival takes 40 gold beside its spawn by r10; our Vendetta dashes in alone at r21 and dies at r30 while three allies retreat; rivals capture the centre at r60. 00ribs: our five walk 60 rounds to one far target; rivals pick gold clusters first (gold r150 35 / 548). 00contest: 2 monoliths and 32 gold cluster groups; collected r1000 0 / 400, deaths 36 / 6. Gem-only maps (adgato_gemcombat4): gold is kills (gold r100 15 / 351, deaths r100 2.7 / 0.2).
- **Opening book** (`tools/replay/openbook.py`, `data/openbook_r60.txt`): rivals and we hit different groups by r60 on many maps. 00interlock wolf at 5,8: 0.85 of their games, 0.06 of ours; 00ambush elk at 31,44 0.67 / 0, elk at 22,43 0 / 0.75; 00eight elk at 12,4 1.00 / 0, elk at 12,26 0.33 / 1.00; 01boss_battle elk at 29,12 0.78 / 0.11.
- **b2p table:** `v1472_b2p@b2p` against `base1503_b2p2@b2p`: 8 against 9 of 60, margin +16 +- 84. No map passes the rule of `rule_route2.md` (ahead by 2 of 4 games and margin up by more than 300); the best are 02guardians, 01starfish and 00eight at 1 game ahead. The win rate against those 12 teams on those maps is 15%.

## Who opens the fights, and why our Marcella holds her nuke (11-03 09:00 IST, `t1503_tm@t03`, 170 games against ranks 1-20)

- **We are hit first twice as often.** To r600 the rivals open 4.5 fights a game and we open 2.4 (a fight start is a hit on a champion after 15 rounds without one; `tools/replay/opener.py`). The opening hit is a cast in 43% of their openings and 21% of ours. Per game she plays, their Marcella opens by cast 1.29 times and ours 0.63; Cassi adds 0.45 a game, and their Heart of Ruin opens by basic attack 0.68 times against our 0.35.
- **Our champions hold fire only against strong teams.** With an enemy champion within 3 tiles at the start of the round, our Vesper hits a champion in 0.39 of the rounds at r0-100 and 0.32 at r100-300 on the platform, against 0.52 and 0.42 for the rivals' Vesper (`tools/replay/inrange.py`). The same bot in local games does 0.52 and 0.48. With her nuke ready and an enemy within 4, our Marcella casts on a champion in 0.18, 0.19 and 0.15 of the rounds (r0-100, r100-300, r300-600) on the platform, against 0.34, 0.35 and 0.32 for the rivals and 0.41, 0.33 and 0.32 for our own bot locally (`tools/replay/nukeuse.py marcella 1 4`). She walks instead (0.58 against 0.47). `free_cast` fires a spell that excludes walking only when the fight sim reads above `P_FREE_EXCL_MIN` (-0.3), or when nobody can reach her, or for a kill, and against strong teams the sim reads low. `exp/vfx1` removes the sim from that test (`results/analysis/rule_nuke.md`).
- **Focus fire is not the gap.** Rounds with at least two hits by one side land all on one champion in 0.80 of the cases on both sides (`tools/replay/react.py`).
- **The reaction to a first hit differs late.** After being hit first we hit back within 6 rounds in 0.66, 0.59 and 0.45 of the fights (r0-100, r100-300, r300 and later), and the rivals in 0.75, 0.67 and 0.64. The victim dies in 0.15, 0.16, 0.28 of ours and 0.08, 0.09, 0.10 of theirs; the hitter dies in 0.02, 0.04, 0.04 and 0.10, 0.08, 0.13. Part of this is strength: in the 4 rounds after a hit taken above half health, we lose 0.26-0.31 of our health and the rivals 0.20 (`tools/replay/fleeok.py`).
- **Stepping away does not save a champion.** Among champions hit by a melee enemy while above half health, those who step away next round die within 12 rounds as often as those who hit back (us 0.25 against 0.20, them 0.10 against 0.09), and they deal 0.4 hits against 2.9 in the next 4 rounds. This is not causal: those who run were losing already.
- **Rounds with no action after a hit are stuns.** The round after a hit, our champions do nothing in 0.14 of the cases against melee hitters and 0.18 against ranged hitters, the rivals in 0.08 and 0.07 (`tools/replay/afterhit.py`). That is about 20 such rounds a game against 9, which matches the 21 stuns they land against our 9.5.

## The light-camps arm on chosen maps works on the platform (11-03 09:00 IST, `vlm1_l5p` against `rt3_l5p`, 60 pinned games each)

`exp/vlm1` plays the light-camps opening on 01hooks, 01elk_arena, 00pilgrimage, 00quarry and 00oasis, maps chosen from a table of local gold gains and confirmed in 40 local games. It wins 16 against 9, with 12 flips against 5, margin +208 +- 112. Team gold at r300 goes from 997 to 1118, at r600 from 1995 to 2227, at r1000 from 3547 to 4069, and the rivals' gold at r600 falls from 3935 to 3570. By map (12 games each, wins base / new, margin difference): 01hooks 2 / 5, +516; 01elk_arena 0 / 2, +426; 00pilgrimage 4 / 6, +210; 00quarry 1 / 2, +153; 00oasis 2 / 1, -264. This is the first opening change that passes on the platform; the same arm on all 85 maps failed because large losses on other maps cancel the gains. The workflow that gave it is written as a rule in `results/analysis/rule_arms.md`.

## Worst maps: one early fight decides them (11-03 09:00 IST, `data/mapgold_t03.txt`, `tools/replay/mapscript.py`)

We take 0 of 12 on 00vault (gold r300 221 against 1626, gems r1000 122 against 1100, deaths r300 5.1 against 0.6). 65 gem clusters at the centre are worth about 460 gems when captured. Both sides reach them at r11-14 and fight there from r21; the side that survives captures at r42-65 for 85-115 gems a champion, so the fight at r21-35 decides the game. On some of these games they bring a Cassi and Issac pair, five bodies against four. Before leaving, their champions take the gold cluster beside the spawn at r2-3 (+40 to +53 gold by r10), and ours take it at r67 or later.

## Exchanges by numbers, deaths by side, and walking hits (11-03 10:49 IST, `data/fights/t1503_tm_t03`, 170 games against ranks 1-20)

`tools/replay/exchange.py` counts rounds in contact by the bodies on each side (us / them per round).

| Numbers | r1-100: rounds a game, health lost, deaths per 100 rounds | r100-300 |
|---|---|---|
| them +2 | 1.8; 133/54; 15.6/1.3 | 2.4; 139/48; 13.1/2.0 |
| them +1 | 4.1; 88/53; 4.6/0.9 | 8.3; 90/51; 6.4/1.3 |
| even | 12.5; 51/39; 1.5/1.0 | 32.3; 48/42; 1.9/1.4 |
| us +1 | 2.6; 74/82; 1.4/1.6 | 6.4; 63/87; 2.3/3.8 |
| us +2 | 0.7; 87/121; 1.7/6.1 | 1.1; 94/131; 2.1/8.8 |

At even numbers the rivals land more: basic hits per body-round 0.40/0.48 (r1-100) and 0.42/0.44 (r100-300), casts per body-round 0.015/0.033 and 0.015/0.032. Being two down is where most deaths come from per round, and a rival two down loses far less than we do (deaths per 100 rounds 13.1 against 8.8 at r100-300).

Deaths by r150: us 1.26 a game (middle 0.77, own half 0.31, their half 0.18), rivals 0.74 (0.46, 0.20, 0.08). Allies within 6 at the death: 1.4 against 1.5, enemies within 6: 3.0 against 2.2. Allies within 6 at the first hit taken: 1.5 against 1.9.

Melee walk and hit per champion-game (`tools/replay/freehit.py`, to r1000): Heart 20.3/31.5, Vendetta 19.5/24.0, Marcella 16.1/17.2. Free hits left unused are few (0.31/0.17 a game).

Strike-first rules (`vms1`, `vms2`) cost deaths locally (+1.09, +2.24): the gap is not closed by engaging at a worse simulated outcome.

## Setup fuel: every map loses the first turn, and acting earlier does not pay locally (11-03 10:49 IST)

A probe of the setup (`exp/fp1`, `exp/fp2`, deleted; `tools/variant/mk_vfu2.py --check` rebuilds one) on all 85 maps. Mean fuel of the setup 202k: groups loop 50k (a bitboard for each group), reachability 47k, camp layout objects and tile table 25k, central gate 21k, Bot::init 18k, altars 14k, static fields 11k, altar sides 6k. Maximum 503k on 03the_front.

`Bot::play_turn` returns after the setup when under 120k fuel is left. That fires on every map, because the first turn holds 200k and the setup costs at least 76k plus 22k before `World::init`. First action: r2 on 40 maps, r3 on 28, r4 on 15, r5 and r6 on one each (mean r2.76). The rivals have far fewer exhaustions on r1-3 and hit camps at r2-3.

Draft memory can carry the numbers: the draft's first turn has 100 times the fuel and all map queries work there. `vfu2` writes steps from spawn per group, altar sides and the central flag there. With lazy group bitboards and raw camp layout words the setup ends on r1 on 78 maps of 85 (r2 on 6, r3 on 1), and a check build found 0 mismatches on all 85 maps.

Local screen (680 paired against `exp.vnl1`): acting earlier does not raise gold. `vfu1` (gate only): team gold r300 -38 +- 17, r600 -123 +- 38, deaths +0.38. `vfu2` (gate 45k): r300 -20 +- 17, r600 -88 +- 37, wins -0.03, deaths +0.08. `vfu4` (gate 80k): r300 -27 +- 18, r600 -94 +- 37, wins -0.02, deaths +0.01. The cause is not known. The local pool starts as late as we do, so moving first there means meeting further from home; the platform's rivals start earlier, so only the platform can tell.

## Per-map gold and gem weights (11-03 10:49 IST)

Doubling the weight of gold in a champion's pick before r300 (`G2`) on chosen maps gives far more than it gives on all maps. In fresh samples of 16 games a map against eight other pool bots, it raised team gold at r300 and did not lose wins on 15 of 26 maps: 02arena +562 (wins 8 to 15), 00split +477, 01elk_arena +420 (11 to 15), 01shortcut +355, 02the_pack +330, 03membrane +321, 00rows +317, 01hooks +196, 00quarry +182, 00the_line +174, 02the_pond +159, 00swirl +149, 00galaxy +126, 01fracture +113, 03shrines +105. On 03colosseum (+828, wins 15 to 8), 03fan, 02tangle, 03reef, 03riverbed, 02uncharted_lands gold rises and wins fall, because gems are the score. Light camps plus gold first (`LG`) gave +766 on 01elk_arena (wins 11 to 16). A first sample of 8 games predicted the fresh one in most cases. All of this is local; `rt7` tests it on the platform (`results/analysis/rule_arms.md`).

## rt5, rt7 and 1523 side by side (11-03 12:50 IST, pinned panels against ranks 1-20)

Over 175 pinned games (`t03pa`, `t03pb`, `a7p`) rt5 won 43 with mean margin -382, and 1523 won 46 with -378. On the same panels v1503 won 22 of 115 (-459), where rt5 has 26 and 1523 has 32. Against v1503 in pairs, rt5 gains +12 +- 57 and +52 +- 75 on parts a and b, 1523 gains +94 +- 50 and +83 +- 77. `paired` for v1503 to 1523 on part a: our deaths +0.1 +- 0.5, their deaths +0.8 +- 0.5, tributed +30 +- 23, margin to r1000 +22 +- 48.

The two win on different maps. rt5 against 1523: 01hooks 3 against 0 of 7 (margin -119 against -989), 01shortcut 5 against 1 of 8 (+106 against -418), 02the_pack 6 against 4 of 8 (+366 against +202), 00split 2 against 6 of 8 (-149 against +71); the other maps have one or two games between them.

`a7p` (6 games a map; wins and mean margin for 1523, rt5, rt7), totals 14, 17, 16 of 60:

| map | 1523 | rt5 | rt7 |
|---|---|---|---|
| 00rows | 2, -234 | 1, -326 | 3, -70 |
| 00split | 4, -5 | 1, -207 | 2, -268 |
| 00the_line | 3, -18 | 3, -69 | 1, -574 |
| 01big_world | 0, -281 | 0, -332 | 2, -104 |
| 01elk_arena | 1, -668 | 1, -674 | 0, -955 |
| 01hooks | 0, -988 | 3, +19 | 3, -3 |
| 01shortcut | 0, -530 | 4, +226 | 2, -146 |
| 02arena | 0, -762 | 0, -842 | 1, -649 |
| 02stalactites | 1, -690 | 0, -976 | 0, -876 |
| 02the_pack | 3, +261 | 4, +255 | 2, -242 |

**rt7's gold did not turn into tribute.** Against rt5: team gold r300 1109 to 1302, r600 2629 to 2917, gold against the rivals' r300 0.69 to 0.83, but to r1000 tributed -51 +- 30, collected -29 +- 33, margin -89 +- 54, final margin -96 +- 74, deaths -0.5 +- 0.4. Gold weights trade gems for gold. Camp kills to r300 in those games (us / them): gem clusters 11.8 / 20.1, gold clusters 25.8 / 23.8, elks 1.8 / 3.0, wolves 7.1 / 7.9, gems 140 / 222: after the weights we take as many gold clusters as the rivals and only 60% of their gem clusters.

## What a champion does with an enemy in reach (11-03 12:00 IST, `tools/replay/inreach.py`, `stillwhy.py`, `t1503_tm_t03`, us / them)

- r1-300: rounds in reach 80.5 / 86.0, hit 0.56 / 0.61, away 0.18 / 0.15, still 0.11 / 0.07; Vesper hits 0.42 / 0.55.
- Numbers in reach, r1-100: ahead 8.1 / 16.6 rounds, even 9.4 / 8.7, behind 9.0 / 4.4. r300-1000: equal (52.9 / 52.4, 41.4 / 41.0, 30.0 / 31.2), but when behind we hit 0.50 and they hit 0.63.
- `vpk3` moved the opening numbers (ahead 8.9 / 12.9, behind 6.9 / 4.8) and still lost on the platform.
- No-action rounds in reach 22.44 / 14.72 a game, of which stunned 16.22 / 8.32; the rest is level. Stuns landed 9.0 / 21.4 a game (Heart 6.1 / 8.2, Marcella 3.5 / 5.2; rivals' third stunner: Cassi 9.9, Ryth 9.9, Tavi 9.2). Our own pair draft `dci5f` doubled our stuns to 14.9, and the margin moved only +15 +- 50 with deaths +4.0 +- 0.8.
- Exchange at even numbers, r300-600: 45.1 rounds, health lost 67 / 48, hits 0.38 / 0.44, casts 0.011 / 0.030, deaths per 100 rounds 2.8 / 1.1.

## Neighbours decide the rating (11-03 13:30 IST, `data/rk8.json`, 800 ranked games 11-02 04:30 to 11-03 07:20 UTC)

Ranked sets run every 10 minutes against teams within about 15 ranks of us (recently ranks 27-52), never the top 20, so the pinned panels against ranks 1-20 do not measure what moves the rating. Last 800 ranked games: 407 wins; before 11-02 19:00 UTC 223 of 425, then 75 of 145, since 1523 went live 109 of 230.

- **By size:** three a side 62 of 151 (0.41), four 88 of 159 (0.55), five 257 of 490 (0.52). Three a side with our usual draft (Heart, Vendetta, Vesper) 50 of 115; the Bamboo arm's draft (Ryth, Vesper, Marcella) 9 of 32.
- **By family:** 00 0.53, 01 0.49, 02 0.55, 03 0.42, adgato 0.51. **By altars on the map:** one 0.48, two 0.50, three 0.60, four 0.50, five or more 0.52.
- **By rival:** a few teams near our rank beat us far more than their rating says: Sheeesh--- (rank 32) 12 of 45, Jupiter (rank 40) 11 of 35, jazz (rank 24) 15 of 40, MFF1 (rank 36) 14 of 35. Others above us lose to us: EE (rank 31) 20 of 30, SquidProxyLovers (rank 34) 20 of 30, QS2isLaw (rank 28) 28 of 55. The same draft can go either way: Ryth, Vesper, Vendetta, Marcella, Heart gives us 14 of 17 against EE and 15 of 20 against HBH but 6 of 20 against Jupiter, so the draft is not what separates them.
- **By rival's draft, five a side** (draft numbers in `draftPicks`: 0 Ryth, 1 Vesper, 2 Vendetta, 3 Cassi and Issac, 4 Stellar, 5 Prism, 6 Marcella, 7 Willow, 8 Ren, 9 Varg, 10 Tavi, 11 Heart; this is not the order of `decoded.NAMES`): Ryth, Vesper, Vendetta, Marcella, Heart 108 of 184; our own five 32 of 62; Vesper, Marcella, Willow, Tavi, Heart 6 of 25; Vesper, Vendetta, Cassi and Issac, Marcella, Willow 4 of 19; Vesper, Vendetta, Cassi and Issac, Willow, Heart 8 of 21.
- **Worst maps:** adgato_gemcombat5 0 of 5, 03fan 0 of 4, 03one_gem 1 of 10, 03honeycomb 1 of 9, 03shrines 1 of 8, 00anvil 2 of 13 (0 of 7 since 11-02 20:00 UTC), 01boss_battle 2 of 12, 03contours 1 of 6, adgato_gemcombat1 2 of 9, 00lanes 3 of 12, 01elk_arena 2 of 8, 02the_pond 3 of 12, 00fragment 3 of 11, 03showdown 2 of 7, 01big_world 3 of 10, 02arena 6 of 19. Local runs call several of them easy (03honeycomb 8 of 8), so the local pool misses what beats us there.

Decoded worst maps (`data/fights/q_worst`, `tools/replay/mapgold.py`; us / them):

| map | games, wins | gold r300 | deaths r300 | collected r1000 | deaths r1000 | first camp hit |
|---|---|---|---|---|---|---|
| adgato_gemcombat5 | 4, 0 | 172 / 840 | 4.8 / 1.2 | 830 / 1084 | 13.8 / 7.5 | r54 / r32 |
| 03fan | 4, 0 | 874 / 1748 | 1.5 / 1.2 | 1010 / 1132 | 6.8 / 3.2 | r5 / r4 |
| 00anvil | 7, 0 | 732 / 1193 | 1.6 / 0.9 | 353 / 631 | 8.4 / 5.0 | r5 / r5 |
| 03one_gem | 3, 0 | 2104 / 3052 | 1.7 / 0.3 | 11 / 44 | 5.3 / 2.0 | r3 / r5 |
| 03contours | 3, 0 | 1931 / 2352 | 0 / 0 | 758 / 1031 | 0.7 / 0.7 | r15 / r8 |
| 03shrines | 5, 0 | 863 / 1018 | 1.4 / 0.8 | 677 / 858 | 8.8 / 8.2 | r8 / r6 |
| 03showdown | 3, 0 | 993 / 992 | 2.7 / 2.7 | 715 / 1056 | 10.3 / 6.7 | r5 / r2 |
| 03honeycomb | 5, 1 | 1105 / 1350 | 1.0 / 1.0 | 574 / 846 | 9.0 / 4.4 | r7 / r6 |
| adgato_gemcombat1 | 9, 2 | 122 / 254 | 1.1 / 1.0 | 733 / 922 | 5.6 / 4.0 | r4 / r3 |
| 01boss_battle | 9, 2 | 2628 / 3398 | 0 / 0.2 | 2368 / 2248 | 3.6 / 6.0 | r14 / r11 |
| 00lanes | 9, 2 | 1595 / 1445 | 1.1 / 1.6 | 847 / 920 | 5.8 / 7.0 | r27 / r26 |
| 02the_pond | 5, 2 | 770 / 1026 | 1.0 / 1.2 | 641 / 544 | 5.2 / 3.4 | r15 / r12 |
| 00fragment | 7, 3 | 901 / 956 | 2.1 / 2.0 | 325 / 359 | 8.9 / 8.3 | r9 / r5 |

**01boss_battle is lost with the gems in hand.** Of 11 decoded games we held 1000 gems in hand (tributed plus bags) in 9, and lost 7 of those, 3 of them after reaching 1000 first; on no other worst map did we lose that way more than once. The only altar is (25,20); the guards are monoliths at (24,20) and (23,20), and 133 of 175 tribute starts came from (24,20): one channel at a time, at 10 gems a round, behind a one-tile corridor. We broke the guards in 9 of the 11 games (hits on the guards 146-534 against 3-72, in the other two 10 against 280 and 60 against 127). When they fell before r520 we stood there poorer: gold 3821-4654 against 6963-9710, 0 wins of 4. The two wins: rival broke them, r653 (hits 10 against 280); we broke them late, r843, gold 14982 against 11621, health 32100 against 19800. Guards come back about 150 rounds after the capture unless a champion stands on a spawn tile; a champion on (24,20) both channels and blocks their return. A rival Vesper reached 11011 health at r680 where ours had 4600. A bag of 1564 gems is a 157-round channel: our Vesper started one at r766 and lost it.
