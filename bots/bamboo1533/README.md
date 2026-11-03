# bamboo1533 (router with the Vesper gold fix; platform version 1533)

The exact source of **v1533**, uploaded to Velvet Tributers on 3 Nov and live since 19:40 IST (user: "Yes, v1533 live"). Build it with `cambc build bamboo1533`. Its test copy was `bots/exp/ra2`.

It is the design of the teammate's v1531: one program with two bots, picked once per game from a map signature read before the draft (`src/main.cpp`).

| Arm | Where | Bot |
|---|---|---|
| `src/bb` (namespace `bbt`) | 00interlock, 00fragment, adgato_gemcombat1, 02crossing, 00corners, 00anvil, 00dunes | Bamboo v1472, as v1531 plays it |
| `src/cj` (namespace `cjb`) | every other map, unseen maps too | `ra1` = `bots/bamboo1530` plus the map arms in `results/analysis/a8.json` and the Vesper gold rules |

Against v1531 on the pinned neighbour panels `nb1` and `nb2`, 125 games: team gold r300 +60 +- 38, margin +3 +- 48, tributed r1000 -6 +- 22, deaths r1000 +0.3 +- 0.3, wins 65 against 62 (`results/analysis/rule_arms.md`). It is a modest gain, not a large one.
