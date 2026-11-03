# Bamboo arm: more of the gold to Vesper (rule written 00:08 IST 11-04, before any game)

Factor: team gold on the maps the router gives to the Bamboo arm. On several of them Bamboo's Vesper earns almost nothing while doing a quarter of the monster damage (`tools/local/lidle.py` on `exp.rall`: 00quadrants 50 gold with 10343 damage, Marcella 2118). A reward she takes pays +33% gold. The arm already has switches for this, both off: `kVesperFeed` (a champion leaves a gold reward to Vesper when she is near and coming) and `kVesperSolo` (the others hold beside a gold reward while she takes it).

Variants, each `rh1` with one constant changed in `src/bb/bot.cpp`:

- `vf1`: `kVesperFeed = 5` (leave it to her, only with no enemy in view and her health at 50% or more).
- `vf2`: `kVesperSolo = 1` (hold beside a reward of 20 gold or more while she is within 8 tiles, at most 12 rounds).

Local screen: the 17 maps of `rh1`'s table, 4 pool bots, both sides, 136 games a variant, paired with `exp.rh1`.

Bar: team gold at r600 and at r1000 both up by at least 1 SE. Guards: deaths r1000 not up by more than 1 SE, margin not down by more than 1 SE, no fault. Wins are recorded, not judged. A variant that passes may go to the platform only with the user's approval, on a pinned panel of routed maps against its base.

Third variant, same bar: `vf3`, `kMarcGems = 1` (gem-dominant rewards go to Marcella, who earns 2 gold per gem she tributes).

## Result (00:25 IST 11-04), `multi-001003`, 136 games each, paired with `exp.rh1`

| Variant | Team gold r600 | Team gold r1000 | Margin | Deaths | Wins | Verdict |
|---|---|---|---|---|---|---|
| `vf1` `kVesperFeed = 5` | -291 +- 60 | down | -106 +- 46 | +1.04 +- 0.41 | -0.09 +- 0.04 | rejected |
| `vf2` `kVesperSolo = 1` | -336 +- 61 | down | -174 +- 48 | +0.32 +- 0.41 | -0.16 +- 0.04 | rejected |
| `vf3` `kMarcGems = 1` | +20 +- 18 | +36 +- 23 | +29 +- 10 | -0.21 +- 0.12 | +0.04 +- 0.02 | passes the local bar |

Leaving rewards to Vesper costs far more than her +33% brings: the others stand idle or she arrives late, and the team loses a tenth of its gold. So a starved Bamboo Vesper is not a cheap fix; the flags were right to be off.

`vf3` changes only 8 of the 17 maps by r1000 (02crossing +314, 03shrines +226, 00dunes +74, 00quadrants +37, 02gift-wrapping +33, 00breadcrumbs +2, adgato-gemcombat1 -25, 02uncharted-lands -43). Bamboo's own earlier local test of this switch, on all maps and an older bot, read -9 (`docs/bamboo/knowledge/bot-status.md`, line 1112), so the prior is about zero. A local pass is needed, not enough: only the platform can accept it.

Fourth variant, same bar, written 00:29 IST before its games: `vf4`, `kMarcGems = 3` (also Vesper's rewards need gold of at least 6 times the gems, her break-even with Marcella). It is judged against `exp.rh1` and then against `vf3` on the same games; the one with more team gold at r1000 goes forward if both pass.

## Platform rule for the Marcella flag, written 00:30 IST 11-04, before any game (user approved the upload at 00:29 IST)

The bot that goes up is `rh1` plus the better of `vf3` and `vf4`. It plays `nr4` first, judged by the bar for the five maps in `rule_route2.md`: the flag changes almost nothing there locally (00eight, 00vault, 01broken-curve exactly nothing by r1000).

Then `nr3` against `rf1_nr3@nr3`, pinned, 50 games. Its five maps are on the Bamboo arm in both bots, so the flag is the only change. Metric: team gold r1000 up by at least 1 SE. Guards: margin not down by more than 1 SE, deaths r1000 not up by more than 1 SE, no fault. Wins are recorded, not judged. If the metric misses, the flag stays out of the final bot even if the five maps pass.

**`vf4` result (00:33 IST).** `multi-002854`, 136 paired against `exp.rh1`: team gold r600 about -10, r1000 +58 +- 62, margin +24 +- 25, deaths 0.0 +- 0.2. It misses the bar on both gold rounds, so `vf3` is the variant that goes to the platform.
