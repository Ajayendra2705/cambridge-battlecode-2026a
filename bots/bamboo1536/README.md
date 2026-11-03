# bamboo1536 (router on 15 maps with the Vesper gold fix and Marcella's stun first; platform version 1536)

The exact source of **v1536**, uploaded to Velvet Tributers on 3 Nov at 22:31 IST and selected by the user at 23:30 IST. Build it with `cambc build bamboo1536`. Its test copy was `bots/exp/rf1`. This same source was uploaded again, unchanged, as **v1545** at 04:33 IST on 4 Nov, because `cambc` cannot rename a version and the user asked for a note saying it is v1536 with no changes.

It is the design of the teammate's v1531: one program with two bots, picked once per game from a map signature read before the draft (`src/main.cpp`).

| Arm | Where | Bot |
|---|---|---|
| `src/bb` (namespace `bbt`) | v1531's seven maps (00interlock, 00fragment, adgato_gemcombat1, 02crossing, 00corners, 00anvil, 00dunes) and 01corridors, 00quadrants, 00gemfight, 00breadcrumbs, 00reverse_spiral, 03shrines, 00contest, 00gem_fields | Bamboo v1472, as v1531 plays it |
| `src/cj` (namespace `cjb`) | every other map, unseen maps too | `ra1` = `bots/bamboo1530` plus the map arms in `results/analysis/a8.json` and the Vesper gold rules, plus `fa4` (Marcella next to a target hits and resets before the nuke) |

Against v1531 on the eight added maps, pinned: 37 against 29 of 75 on `nr2`, then on five of them 26 against 22 of 50 on the fresh panel `nr3`. Together 63 against 51 of 125, margin +133 +- 58, team gold r1000 +541 +- 142, our deaths r1000 -1.6 +- 0.5. The gain sits mostly on two maps: 00breadcrumbs 2 to 10 of 19 and 01corridors 5 to 10 of 20. The written bar on `nr3` missed on wins by a hair (`results/analysis/rule_route2.md`). `fa4` has played no game on those panels, because they play only the Bamboo arm.

Whole bot against v1531 on `nb1` and `nb2`, 125 pinned games: 71 against 62, margin +56 +- 53. All pinned games together, 250: 134 against 113, flips 46 up and 25 down, margin +94 +- 39.
