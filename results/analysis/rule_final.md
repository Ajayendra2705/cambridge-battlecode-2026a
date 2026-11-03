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
