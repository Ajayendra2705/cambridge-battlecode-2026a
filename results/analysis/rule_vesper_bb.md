# Bamboo arm: more of the gold to Vesper (rule written 00:08 IST 11-04, before any game)

Factor: team gold on the maps the router gives to the Bamboo arm. On several of them Bamboo's Vesper earns almost nothing while doing a quarter of the monster damage (`tools/local/lidle.py` on `exp.rall`: 00quadrants 50 gold with 10343 damage, Marcella 2118). A reward she takes pays +33% gold. The arm already has switches for this, both off: `kVesperFeed` (a champion leaves a gold reward to Vesper when she is near and coming) and `kVesperSolo` (the others hold beside a gold reward while she takes it).

Variants, each `rh1` with one constant changed in `src/bb/bot.cpp`:

- `vf1`: `kVesperFeed = 5` (leave it to her, only with no enemy in view and her health at 50% or more).
- `vf2`: `kVesperSolo = 1` (hold beside a reward of 20 gold or more while she is within 8 tiles, at most 12 rounds).

Local screen: the 17 maps of `rh1`'s table, 4 pool bots, both sides, 136 games a variant, paired with `exp.rh1`.

Bar: team gold at r600 and at r1000 both up by at least 1 SE. Guards: deaths r1000 not up by more than 1 SE, margin not down by more than 1 SE, no fault. Wins are recorded, not judged. A variant that passes may go to the platform only with the user's approval, on a pinned panel of routed maps against its base.

Third variant, same bar: `vf3`, `kMarcGems = 1` (gem-dominant rewards go to Marcella, who earns 2 gold per gem she tributes).
