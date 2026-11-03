# Decision rule: per-map draft arms, written 11-03 11:07 IST before any new game

**Factor.** Fights and score on single maps through the draft. Rivals' teams hold an extra stunner, and 47% of our deaths had a stun on the victim in its last 6 rounds against 27% of theirs (`docs/findings.md`, Stuns). On all maps together, a stunner for Willow fails locally (`d5r` wins -0.07, `d5t` -0.09), but per map the gains are large: 03one_gem 0 of 8 to 7 of 8 (`d5t`) and 6 of 8 (`d5r`), 00lost_world margin +283, 01starfish +184, 03contours +156, 00pilgrimage +155, 00monolith +127.

**First sample.** 8 games a map against cmb7, bot_10, cp3, dh3 (paired with `exp.vnl1`, multi-031107): at 4 picks `d4v` (Heart, Marcella, Vendetta, Vesper), `d4r` (Ryth for Vesper's slot), `d4t` (Tavi), `d4rv` (Heart, Marcella, Ryth, Vesper); at 3 picks `d3m` (Heart, Marcella, Vesper), `d3v` (Marcella, Vendetta, Vesper). Maps from `data/maps_size4.txt` and `data/maps_size3.txt`. At 5 picks the table of `multi-230533` serves (`data/armscan_d5.json`).

**Candidates for the fresh sample.** A map and draft with margin gain at least +100 and wins not below the base's.

**Table rule.** Fresh sample of 16 games a map against the same eight other pool bots as the arms, paired with `exp/rt3`. A draft goes in the table for a map when its margin gain is at least +100, its wins are not below the base's, and its deaths are not up by more than 1 a game. Several drafts: the largest mean margin gain of both samples.

**Platform bar.** The router with the table against the same router without it, on a panel of the table's maps: margin up by at least 1 SE, stuns landed per game up by at least 1 SE where the draft adds a stunner, guards: deaths r300 minus theirs not up by more than 1 SE, team gold r300 not down by more than 1 SE, no fault. Wins recorded.

## Results, 11-03 11:32 IST

**Five picks, fresh sample (`data/dr5_*.log`, 16 games a map).** Tavi: 03one_gem wins 5 to 13, margin +39; 00lost_world 13 to 12, +183; 03contours 8 to 12, +79; 01starfish 11 to 7, -144; 03twisty 13 to 12, -79. Ryth: 03one_gem 5 to 11, +26; 00pilgrimage 13 to 8, -447; 00monolith 14 to 11, -106; adgato_gemcombat4 9 to 9, +5; 03riverbed 10 to 10, -2. No entry passes: the first sample's margins were mostly noise. On 03one_gem the gem weight arm GN wins 15 of 16 with margin +235, and it needs no other pick.

**Four picks, first sample (`data/armscan_dz4.json`).** Overall worse (`d4t` wins -0.12, margin -227; `d4v` -0.08, -170). Candidates for the fresh sample: 00the_line Tavi 7 of 8 against 4, +560, and Ryth 7 of 8, +386; 02stalactites Vesper 6 against 4, +507; 02guardians Vesper 7 against 6, +332; adgato_gemcombat3 Tavi 8 against 6, +146, Vesper 8, +130.

## Fresh sample of the four-pick candidates (`data/dr4_*.log`, 16 games a map against `exp.rt3`)

`rda`: adgato_gemcombat3 Tavi wins 11/12, margin +29; 02guardians Vesper 12/9, -352; 00the_line Tavi 9/6, -291; 02stalactites Vesper 13/6, -797. `rdb`: adgato_gemcombat3 Vesper 11/13, +84; 00the_line Ryth 9/5, -421. No map passes the table rule (margin gain at least +100, wins not below base). The first sample's gains (+130 to +560 on 8 games) did not repeat, so no draft arm goes in the router. Three a side: `d3m` on the first sample of 120 games shows wins +0.07 +- 0.04, margin +116 +- 47, deaths -0.59 +- 0.34, but the same change was rejected on the platform earlier (row d3m: collected -29.9 +- 25, margin -12 +- 37); only 03homonoliths (3/7, +650) and 00packs (6/8, +387) stand out, and both are single first samples.
