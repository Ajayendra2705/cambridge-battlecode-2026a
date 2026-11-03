# Decision rule: per-map opening arms in the router, written 11-03 08:38 IST before any result of the fresh sample

**Factor.** Gold at r300 on single maps. No opening rule helps on all maps, because the gains are large on some and large losses on others (`data/armtable_r300.json`: nine variants on 85 maps, 8 games a map, against the pool cmb7, bot_10, cp3, dh3). `vlm1` (light camps first on five maps chosen from such a table,
confirmed in 40 local games) beat `rt3` on the platform on those maps: 16 against 9 of 60, flips 12 against 5, margin +208 +- 112, gold r300 997 to 1118, r600 1995 to 2227, the rivals' gold r600 3935 to 3570 (`vlm1_l5p`, `rt3_l5p`).

**Arms.** `L` (light 1.5, enable 1.6, r150), `L3` (light 1.5, enable 1, r150), `W1` (light 1.5, enable 1.6, wolves counted as light, r120), `W2` (heavy 0.6, enable 1.2, r120), `B1` and `B2` (opening book, as `vbk1` and `vbk2`), each only on the maps where the first table shows at least +100 and at least 8% of the base's gold (`data/arm_candidates.json`).
Maps already routed to Bamboo or already in `rt5`, and 00oasis (it lost on the platform), are left out.

**Fresh sample.** 16 games a map against eight other pool bots (v1498, v1502r, v1491, v548, cmb2, hb4, mi8, rz20), paired with `exp/rt3`, whose v1503 arm is the bot under change on those maps.

**Table rule.** An arm goes in the table for a map when its gold r300 gain in the fresh sample is at least +100 and at least 8% of the base's gold there, and its wins on that map in the fresh sample are not below the base's. With several arms passing, the largest mean of the two samples wins.

**Platform rule.** The new table (`rt6`) against `rt5` on a panel of the table's maps (`mappanel.py`, 12 teams, 60 games, pinned, same session): team gold at r300 up by at least 1 SE, margin not down by more than 1 SE, deaths to r300 not up by more than 1 SE, no fault. Wins recorded, not judged.

**Fresh sample, 11-03 09:33 IST (`data/arm2_table.txt`, base `exp.rt3`, 16 games a map).** Passing: 02stalactites B2 (+566 on 701, wins 13/15, margin +116; first table +520), 01big_world B2 (+410 on 914, wins 11/11, margin +91; first table +393), 01broken_curve W1 (+191 on 1117, wins 9/13, margin +288), 01fracture L (+170 on 1196, wins 11/13, margin +136), 01big_world B1 (+167, wins 11/14), 03twisty W1 (+145 on 505, wins 13/13, margin +82), 00lost_world B1 (+128 on 730, wins 13/13, margin +21). Failing, most of them regressing toward zero as expected: L on 00collision (+84), 02famine (+63, wins 11/9), 03contours (+58), 01yellow_brick_road (-97, though wins 6/12 and margin +364); L3 on 01big_world, 00collision, 03contours, 00the_line, 00crater (-258); W1 on 02tangle (wins 14/8), 03riverbed (-300); W2 on all (00ambush +155 with wins 10/9, 02treasure_box -364); B1 on 02stalactites (+384, wins 13/10), adgato_gemcombat5, 00vault, 02guardians, 00crater, 01yellow_brick_road, 00quadrants; B2 on 00rows (+107, wins 12/10), 02guardians (+87), 00crater.

**Table of `rt6`.** `rt5`'s four L maps plus 01fracture L, 01broken_curve W1, 03twisty W1, 01big_world B2, 02stalactites B2. 00lost_world B1 is left out: the book arm in the router has one setting, B2's.

**Gold-weight arms, written 11-03 09:44 before their fresh sample.** The screens of `vge2` (`P_GOLD_W_EARLY` 2) and `vgw2` (`P_GEM_W` 2) failed on all maps, but per map (`tools/local/armscan.py`, `data/armscan1.json`) many maps show large gains in gold with more wins and a better margin: 00the_line, 01fracture, 01elk_arena, 00crater, 00rows, 02the_pack, 00galaxy, 02arena, 01starfish. Arms `G2` and `GW` in `mk_rt.py` set those weights per map. Fresh sample and table rule as above (16 games a map, same eight pool bots, against `exp.rt3`).

## Third fresh sample: gold weight on more maps, written 11-03 10:08 IST before any game

G2 passed the table rule on 10 of the 12 maps of the second sample (02arena +562, 00split +477, 01elk_arena +420, 02the_pack +330, 00rows +317, 01hooks +196, 00quarry +182, 00the_line +174, 00galaxy +126, 01fracture +113); GW on 00the_line +191, 01fracture +149, 00quadrants +111. The first sample gain predicted the fresh one well enough to test the rest of the list.

**Sample.** The same eight pool bots, 16 games a map, paired with `exp/rt3`. G2 on the maps with a first sample gain of at least +100 that are not yet tested and not routed to Bamboo: 03colosseum, 03riverbed, 03fan, 03reef, 00collision, 03membrane, 02uncharted_lands, 00ambush, 02tangle, 01shortcut, 03shrines, 00swirl, 01islands, 02the_pond. LG (L and G2 together) on the maps where both passed or L is proven on the platform: 01elk_arena, 01hooks, 00quarry, 01fracture, 00pilgrimage.

**Rule.** The table rule above, unchanged: gain at least +100 and at least 8% of the base, wins not below the base. L stays on 01elk_arena, 01hooks, 00quarry and 00pilgrimage unless LG or G2 has a gain at least 100 above L's in the same fresh base; those maps have L proven on the platform.

## Results of the third sample and rt7, written 11-03 10:34 IST before rt7's screen

G2 passed on 01shortcut +355, 03membrane +321, 02the_pond +159, 00swirl +149, 03shrines +105. It raised gold but lost wins on 03colosseum (+828, wins 15 to 8), 03fan, 02tangle, 03reef, 03riverbed, 02uncharted_lands and 01islands, so they stay out. LG passed on 01elk_arena +766 (wins 11 to 16), 01hooks +250, 01fracture +237, 00quarry +140.

**rt7's table.** LG: 01elk_arena, 01hooks. L: 00quarry, 00pilgrimage (L is proven on the platform; no other arm is 100 above it). GW: 01fracture, 00the_line, 00quadrants. G2: 02arena, 00split, 02the_pack, 00rows, 00galaxy, 01shortcut, 03membrane, 02the_pond, 00swirl, 03shrines. W1: 01broken_curve, 03twisty. Book B2: 01big_world, 02stalactites. Vesper's gold value (vgv2: gems 1, gold 2 before r300) replaces vvk1's rules on every map of the v1503 arm.

**Local bar for rt7** (680 paired games against `exp.vnl1`): team gold r300 up by at least 2 SE, wins not down by more than 0.03, deaths not up by more than 0.3, no fault.

**Platform bar.** rt7 against rt5 on `a7p` (02arena, 00split, 01elk_arena, 02the_pack, 00rows, 01shortcut, 02stalactites, 01big_world, 00the_line, 01hooks): team gold r300 up by at least 1 SE, margin not down by more than 1 SE, deaths r300 not up by more than 1 SE, no fault. 1523 plays the same panel so we see whether rt7 passes it on those maps; that comparison is recorded and decides the live bot only together with the t03 parts.

## Fourth fresh sample: gold weight 3, written 11-03 11:02 IST before any game

G3 (gold 3, gems 3) on the G2 maps and LG3 on 01elk_arena and 01hooks, the same eight pool bots, 16 games a map, paired with `exp/rt3`. An arm replaces the table's entry on a map when its fresh gain is at least 100 above the entry's fresh gain and its wins are not below the entry's.

rt7's local screen (11:01, multi-104334, 680 paired against `exp.vnl1`): team gold r150 +37, r300 +75.5 +- 14.5, r600 +86 +- 32, deaths -0.50 +- 0.18, wins +0.01, margin +32 +- 16, collected -0.5, no fault. It passes.

Results of the fourth sample (11-03 11:12): G3 replaces G2 only on 00split (+646 against +477, wins 11 and 11). On 02arena (+614 against +562), 02the_pack (+386 against +330), 01shortcut (+288 against +355), 00rows (+238 against +317), 00swirl (+191 against +149) and the rest the difference is under 100, and on 03membrane, 00quarry, 03shrines and 02the_pond G3 loses wins. LG3 on 01elk_arena (+567) is below LG (+766).

## Gem weight on gem-scarce maps, written 11-03 11:25 IST

03one_gem (one gem cluster, 0.12 gems a round): GN (gem weight 12) and GM (30) against rt3, fresh sample: wins 5 to 15 of 16 for both, margin +235 and +241, gold r300 -93 and -156. On this map gems decide and gold is plentiful, so the arm is judged on margin and wins, not gold: GN goes in the table.

Test on the other gem-scarce maps without an arm: 03ultrastarvation, 00ribs, 00oasis, 01gold_rush, 00packs, 00stampede, 00contest, 00crater (under 2.6 gems a round). Same sample. Rule: margin gain at least +100, wins not below the base's, deaths not up by more than 1 a game.

## First sample of combined arms, written 11-03 11:34 IST before any game

LG (light and gold), WG (wolves count as light, and gold), HG (heavy 0.6, and gold), each on all 78 maps not routed to Bamboo, 8 games a map against cmb7, bot_10, cp3, dh3, paired with `exp.vnl1`. A map with gain at least +100 and wins not below the base's goes to a fresh sample under the table rule. Rt7's entries stay unless the fresh gain is 100 above theirs.

## Gem weight 12 on gem-scarce maps (`exp/ragp`, `data/arm8_*.log`, 16 games a map against `exp.rt3`), judged under the gem-scarce rule

00crater wins 10/11, margin +162, deaths recorded by the table only as gold -95; 00contest level; 00stampede 11/11, -113; 03ultrastarvation 12/9, -63; 00oasis 8/7, -99; 00ribs 11/10, -57; 00packs 9/9, -48; 01gold_rush 12/1, -909. Only 00crater reaches +100 and it stands alone among eight, so it goes to one more sample before any table entry. The arm stays on 03one_gem only (wins 5/15, margin +235).

## rt7 on the platform and the table of rt8, written 11-03 12:45 IST before rt8's screen

`rt7_a7p` against `rt5_a7p` (60 pinned games): team gold r300 1109 to 1302, r600 2629 to 2917, us/them at r300 0.69 to 0.83; deaths to r1000 -0.5 +- 0.4; collected to r1000 -29 +- 33, tributed -51 +- 30, margin to r1000 -89 +- 54, final margin -96 +- 74, wins 16 against 17. The gold target moved; the margin guard is breached, so rt7 is rejected. Gold weights trade gems for gold: camp kills to r300 show the rivals ahead on gem clusters, not on gold clusters. 1523 on the same panel: 14 wins; rt5 against it margin +99 +- 90.

By map, rt7 against rt5 (6 games a map; wins, margin): 00rows 3/1 +256, 01big_world 2/0 +228, 02arena 1/0 +193, 02stalactites 0/0 +100, 01hooks 3/3 -22, 00split 2/1 -61, 01elk_arena 0/1 -281, 01shortcut 2/4 -372, 02the_pack 2/4 -497, 00the_line 1/3 -505.

**Table of rt8.** An arm of rt7 stays only where the platform margin is at least +100 and wins are not below rt5's, and the fresh local sample agreed: 00rows G2, 02arena G2, 01big_world book, 02stalactites book. Also rt5's L on 01elk_arena, 01hooks, 00quarry, 00pilgrimage (vlm1's platform gain), L on 01fracture (fresh +170, wins 11/13, margin +136) and GN on 03one_gem (wins 5/15, margin +235). Vesper's rules as rt5 (vvk1). Plus vpa1 (`rule_pair.md`).

**Local bar of rt8 (680 paired against `exp.vnl1`).** Wins not down by more than 0.02, margin not down by more than 1 SE, deaths not up by more than 0.2, collected not down by more than 2 SE, no fault.

**Platform, only with the user's OK for a gate.** rt8 against rt5 on a panel of the changed maps, the base in the same session: margin not down by more than 1 SE and tributed to r1000 up by at least 1 SE.

**Result of rt8's local screen (680 paired against `exp.vnl1`, `data/judge_screen_rt8.txt`).** Wins +0.02 +- 0.01, margin +21 +- 15, collected +2.2 +- 7.5, tributed +3.9 +- 7.4, their tributed -2.4 +- 7.6, deaths -0.29 +- 0.16, kills +0.15 +- 0.17, team gold r150 +19.7 +- 6.4, r300 +23.9 +- 13.7, r600 +24.9 +- 30.8, no fault. Passes the local bar. Platform waits for the user's OK (1523 stays live until then).

## ra1: the arms on the new base (11-03 14:45 IST)

v1530 (teammate's `bots/bamboo1530`, live since 08:28 UTC on 11-03) is the base now. `exp/ra1` is v1530 with rt8's table (the same arms, book, Vesper rules and vpa1), built with `SRC=src tools/variant/mk_rt.py`, `mk_vbk2.py` and `mk_rt8.py`. It has no router: every map plays 1530's program.

**Local bar (680 paired against `exp.b30`, before the screen).** The factor is team gold by r300 on the arm maps and overall. Team gold r300 not below 0 overall, deaths not up by more than 0.2, margin not down by more than 1 SE, collected not down by more than 2 SE, no fault. Wins are recorded and not judged. A pass allows a request for a gate, nothing more.

**Result of ra1's local screen (680 paired against `exp.b30`, `data/judge_screen_ra1.txt`).** Team gold r150 +27.8 +- 5.5, r300 +45.1 +- 10.3, r600 +87.8 +- 24.9, captures +1.27 +- 0.35, wins +0.01 +- 0.01, margin +9 +- 14, collected +4 +- 7, tributed +11 +- 6, their tributed +0.6 +- 6, deaths -0.15 +- 0.17, no fault. Passes the local bar. A gate waits for the user's OK. Platform bar, to be judged on a panel of the neighbours with the live bot in the same session: team gold at r300 up by 1 SE, margin not down by more than 1 SE, tributed to r1000 not down by more than 1 SE; wins recorded and not judged.

**ra1 on the platform (user's OK at 15:30 IST: "test it on platform once on the one my other teamates are testing"; written before the games).** Panel `tm1`: the teammate's 16 groups of 09:51-09:52 UTC (ranks 1-12, the seven near maps 00interlock, 00fragment, adgato_gemcombat1, 02crossing, 00corners, 00anvil, 00dunes), pinned to the same opponents' bots, with the teammate's 1530 games (`e1530_tm1`) as the base. None of ra1's map arms act on these maps, so this tests only Vesper's rules and `vpa1`. Bar: Vesper's gold at r300 up by 1 SE (the target), team gold at r300 not down, margin not down by more than 1 SE, tributed to r1000 not down by more than 1 SE. Wins are recorded and not judged. 1530 goes back live right after.

**ra1 on the neighbours (written 11-03 16:05 IST, before the games; user: "queue all ours").** Panel `nb1`: 10 ranked groups of 1530 from 08:30 to 10:00 UTC, one per rival (ranks about 25-50), pinned to those rivals' bots; 6 of ra1's 10 arm maps appear. 1530's own games are the base (`e1530_nb1`, 26 of 50). Bar: team gold at r300 up by 1 SE, margin not down by more than 1 SE, tributed to r1000 not down by more than 1 SE; wins recorded and not judged. v1531 plays the same panel next, as a reference.

**Result of ra1 on `tm1` (v1532, 80 games paired with the teammate's 1530 games, `data/pgold_tm1.txt`).** Target: Vesper's gold at r300 +72.4 +- 25.5 (base 263), passes and agrees with the local +71. Guards: team gold at r300 +35.2 +- 23.4, margin +14 +- 33, tributed to r1000 +0.4 +- 20.8, all hold. Recorded: wins 12 against 12. The gain fades by r1000 (Vesper +30 +- 47, team +48 +- 88), and no map arm acts on this panel, so this speaks for Vesper's rules only.
