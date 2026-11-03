# Which bot enters the International Qualifiers (lock 05:29 IST 11-04)

**Rule (written 11-03 20:25 IST, before any game of v1534 on these panels).** At 20:23 IST a teammate's upload v1534 ("Bamboo RT32: v1531 + nav fuel fix + Willow peel/no-trade/HP build/behind") went live and selected, so it enters unless the team changes it. It has not been played on our pinned panels. It plays them now with a `live` gate, which uploads nothing and selects nothing: `e1534_nb1@nb1` and `e1534_nb2@nb2`, 125 pinned games against the neighbours, the same rivals' bots as v1531 (`e1531_nb1`, `e1531_nb2`) and v1533 (`ra2_nb1`, `ra2_nb2`). A pinned panel replays exactly, so the games pair exactly.

- **Metric:** paired mean final margin over the 125 games, v1534 minus v1533 and v1534 minus v1531, with its standard error. Tributed and deaths to r1000 and team gold to r600 are read as guards, and wins are recorded.
- **Keep v1534** when its margin is not below v1533's by more than 1 SE. It is the team's selection and carries fixes on top of v1531, and a level result gives no reason to change it.
- **Recommend v1533 to the user** when v1534's margin is below v1533's by more than 1 SE and its wins are below too. The user and the teammate decide; nothing is selected without their word.
- **Near-map panels are read separately.** v1534 and v1533 play the same Bamboo arm on the 7 routed maps unless RT32 changed it, and `tm1` (ranks 1-12) tests those maps. It is played only if the 125 games leave the choice open.

What is known before the games: on the 125 games v1533 against v1531 has wins 65 against 62, margin +3 +- 48, team gold r300 +60 +- 38. These two are level.

A merged bot (v1534's default arm with `ra1`'s map arms and Vesper gold) needs v1534's source, which is not in the repo at 20:25 IST. It would need its own local screen and the same 125 games.

## Does `ra1` still gain with Cassi and Issac in the draft (written 11-03 21:25 IST, before any game)

v1535 plays Heart, Marcella, Vendetta, Vesper, Cassi and Issac on five picks, and `ra1` (Vesper's gold rules and the map arms) was measured with Willow as the fifth pick. Its source is not in the repo, so two stand-ins are played locally: `exp/c30` is v1530 with that draft and the six-body fix (`results/patches/six.patch`), `exp/c31` is `ra1` with the same two changes.

- **Fix check.** A build with the fix and no draft change must replay `exp.b30`'s games on three and four picks, and all its games must be free of faults. In `c30`, Issac must cast and attack like the other bodies (`tools/replay/casts.py --six`).
- **Metric.** `c31` against `c30`, paired, on the 51 five-pick maps against pool/cmb7, pool/bot_10, pool/cp3, pool/dh3, both sides: team gold at r300 up by at least 1 SE.
- **Guards.** Deaths not up by more than 0.3, margin not down by more than 1 SE, collected not down by more than 2 SE, no fault. Wins are recorded, not judged.
- **Use.** A pass keeps `ra1.patch` in the combine for all maps. A fail on five picks means its map arms and Vesper rules go in for three and four picks only, unless the failure is one map's arm, which is then dropped.
- **Also read.** `c30` against `exp.b30` (Willow fifth, `data/runs/multi-145148`) on the same games: how the pair compares with Willow once Issac works. That is a local reading of a draft change, so it decides nothing.

## v1535 enters the comparison (written 11-03 21:32 IST, before any game of v1535 on `nb1` or `nb2`)

At 20:46 IST the teammate's v1535 replaced v1534 as live and selected. On the teammate's top-team panel it pairs with the burst of 14:51 UTC (probably v1534) at 10 wins against 15 of 48, flips 2 up and 7 down, margin -108 +- 74 (`data/tmp_pairburst.py`): under v1534 by 1.5 SE, against ranks 1-14. The same rule as above now reads with v1535: `e1535_nb1@nb1` and `e1535_nb2@nb2`, `live` gates that upload and select nothing, 125 pinned games.

- **Metric:** paired mean final margin over the 125 games against v1533 and v1531, with its SE. Guards read: tributed and deaths to r1000, team gold to r600. Wins recorded.
- **Keep v1535** when its margin is not below v1533's by more than 1 SE.
- **Tell the user and the teammate** when it is below by more than 1 SE and its wins are below too, and recommend the better measured bot. v1534 has 50 of these 125 games (`e1534_nb1`); its other 75 need the live slot, so they are played only if the user asks. Nothing is selected without their word.

**Result of `c31` against `c30` (11-03 21:39 IST, `data/runs/multi-212627`, 416 paired games on five-pick maps).** Team gold r300 +61.2 +- 16.6, so the metric passes. Guards: deaths -0.35 +- 0.27, margin +9.5 +- 17.1, collected +19.3 +- 9.8, no fault. Wins -0.03 +- 0.02, recorded. `ra1.patch` stays in the combine for all maps. In `c30` Issac deals 11621 damage a game against Cassi's 10231 (1575 without the fix). The fix replays 16 of 16 games on three and four picks.

**Also read, decides nothing:** `c30` against `exp.b30`, the pair for Willow on the same games: wins -0.04 +- 0.02, margin -74 +- 24, deaths +3.89 +- 0.34, team gold r300 +7.8 +- 22, r600 +0.3 +- 48. The pair dies 2.41 times a game, Willow 1.27; the two bodies count twice, so deaths overstate it, but each death hands over both bags.

**The live bot changed again (21:43 IST).** A teammate selected v1531 at about 21:21 IST. So the comparison above for v1535 was not played; `e1535_nb1` replayed v1531 exactly (0 flips, margin +0) and is logged as `e1531c_nb1`, and 8 groups of `nb2` replayed it too before the chain was stopped. v1534 and v1535 stay unmeasured on `nb2`. With v1531 selected, the base's source is in the repo (`bots/bamboo1533` less `ra1`), so `exp/rf1` is itself a combined bot: v1531 + `ra1` + 8 more Bamboo maps + `fa4`.
