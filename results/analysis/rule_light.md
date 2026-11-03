# Rule for light camps first in the opening (written 11-03 03:25 IST, before the local screen)

**Factor.** Early team gold. On `t1503_tm@t03` plus `base1503_s3p@s3p` (`tools/replay/mapgap.py`) team gold at r300 is under 0.4 of the rivals' on 12 maps, and under 0.2 on four. On 01corridors (trace `9648827e`) our whole team walks to one heavy group and takes 260 gold at r81, then no one else earns until r126; the rivals send a pair and a lone champion to clusters and hold 259 gold by r60, and they make 13 captures to r300 against our 5. Our Vesper still has 0 gold at r420 in that game. Over the 170 games: 16.0 captures against 12.2 to r300 (`decoded.py captures`). Bamboo's study found the same gap against Fish: light camps 15.3 against 25.7 a game (`docs/bamboo/knowledge/recall-cycle-1031.md`).

**Cause in the code.** `choose_task` in `farm.cpp`: a heavy group that needs helpers scores `P_ENABLE` (1.6) times, and each champion's score is split among the `n_team` the group needs, so the team piles on.

**Variants on `pool/v1503`.** Before round `P_LIGHT_R`: harmless groups (clusters only, `g.dps` 0) count `P_LIGHT_W` times and the enabler multiplier is `P_ENABLE_EARLY`.

| Variant | `P_LIGHT_W` | `P_ENABLE_EARLY` | `P_LIGHT_R` |
|---|---|---|---|
| `exp/vlc1` | 1.5 | 1.6 | 150 |
| `exp/vlc2` | 1 | 1 | 150 |
| `exp/vlc3` | 1.5 | 1 | 150 |
| `exp/vlc4` | 2 | 1 | 250 |

**Local bar** (`pool/v1503`, same pool and 85 maps, 680 paired). Target: team gold at r300 up by 1 standard error or more (`lgold2.py`). Guards: deaths not up by more than 0.3 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault.

**Platform.** Only a pass goes on: `t03p` parts pinned to `t1503_tm@t03`. Target: team gold at r300 up by 1 standard error or more (`decoded.py gold`, paired where possible); margin and collected not down by more than 1 standard error. Wins recorded.

## Result of the whole-map screen, and a per-map arm (written 11-03 05:14 IST, before the arm's screen)

vlc1 to vlc4 failed their bar on all maps (`data/runs/multi-033046`, gold r300 -30, -62, -114, -174), but the effect differs strongly per map. vlc1 at r300: 01elk-arena +451, 00oasis +176, 01hooks +147, 00pilgrimage +88, 00quarry +87; 03colosseum -971, 01boss-battle -639. These five are gem-poor maps where the top teams send a pair to the centre and the rest to gold (01elk_arena, `t1503_tm@t03`: us 0 gold at r50 and five champions on the elks, them 106), so the rule has a cause and is not only a selection from noise; the selection still inflates the gain.

`exp/vlm1` is `exp/vnl1` with vlc1's numbers (`P_LIGHT_W` 1.5, `P_ENABLE_EARLY` 1.6, `P_LIGHT_R` 150) on those five maps only (`kLightMaps` by map signature). Local bar on those five maps, 40 games against `exp.vnl1`: gold r300 up, margin not down, deaths r300 not up by more than 0.5 a game, wins not down by more than 2 of 40. Every other map must be byte for byte the same game (no check needed beyond the table: the flag stays false).

Platform, only after that pass: pinned on the five maps, a panel with the 12 teams of `b1p`, base and variant in the same session. Target: team gold at r300 on these maps up by 1 standard error or more. Guards: margin not down by more than 1 standard error, deaths r300 not up by more than 1 standard error. Wins recorded.

`exp/vlm1` local (`data/runs/multi-051136`, 40 games on the five maps against `exp.vnl1`; 11-03 05:13 IST): gold r150 +203 +- 46, r300 +269 +- 76, r600 +524 +- 188, wins +0.12 +- 0.06, margin +193 +- 108, collected +70 +- 40, deaths -3.27 +- 1.32, no fault. These are the games that chose the maps, so the numbers only show the table works; they are not new evidence. Bar passed. Platform: `rt3_l5p@l5p` (version 1522, whose arm on these maps is `exp/vnl1`) against `vlm1_l5p@l5p`.

## Gem and gold weights in the camp choice (written 11-03 05:18 IST, before the screen)

Team gold at r300 is 0.62 of the rivals' against ranks 1-20, and they capture more of every kind (gold groups 12.7 against 7.9 a game, wolf and gold 7.9 against 4.5). `choose_task` values a group at `gems * P_GEM_W + gold * gold_w`, with `P_GEM_W` 3 and `gold_w` 1 before r300. These numbers have not been tested on the bot_10 line. Variants on `exp/vnl1`: `exp/vgw2` (`P_GEM_W` 2), `exp/vge15` (`P_GOLD_W_EARLY` 1.5), `exp/vge2` (`P_GOLD_W_EARLY` 2).

Local bar (base `exp.vnl1`, `multi-031107`, 680 paired): team gold r300 up by 1 standard error or more. Guards: deaths not up by more than 0.3 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault. Platform only after a pass, on `t03p` parts: gold r300 up by 1 standard error or more; margin and collected not down by more than 1 standard error.

## Vesper's opening (written 11-03 05:24 IST, before the screen)

Gold gained to r300 per Vesper: us 232 in 2.8 captures, rivals 629 in 5.5 captures (`t1503_tm@t03`). Our Vesper's turns to r300: walking to a task 16%, hitting camps 27%, waiting (`wait_respawn`, `wait_tank`, `gather`) 18%, capturing 7%, fighting 20%. She earns a third more gold from her share, and on a harmless group she needs no tank and no gathering. Variants on `exp/vnl1`: `exp/vvg1` (harmless groups with gold count twice in her pick before r200), `exp/vvg2` (all harmless groups twice before r300).

Local bar (base `exp.vnl1`, `multi-031107`, 680 paired): Vesper's gold r300 and team gold r300 up by 1 standard error or more. Guards: deaths not up by more than 0.3 a game, wins not down by more than 0.03, collected not down by more than 2 standard errors, no fault.

## Results of the gem and gold weights and of Vesper's opening (11-03 06:10 IST)

`data/judge_screen_vgw.txt` (`multi-051518`) and `data/judge_screen_vvg.txt` (`multi-051923`), 680 paired games each against `exp.vnl1`:

- `exp/vgw2`: gold r300 +38.6 +- 14.7, margin -33.7 +- 16.3, collected -12.9 +- 8.1. Passes the bar by the letter; the margin falls by 2 standard errors. Held.
- `exp/vge15`: gold r300 +37.6 +- 14.7, margin -31.5 +- 15.9, collected -16.6 +- 8.4. The same. Held.
- `exp/vge2`: gold r300 +66.8 +- 16.5, deaths -0.35 +- 0.17, collected -33.6 +- 9.1. Fails the collected guard. A higher weight on gold trades gems for gold about one for one.
- `exp/vvg1`: team gold r300 +16.7 +- 8.2, Vesper's gold r300 +37.1 +- 9.5, wins +0.01, margin +6.8 +- 10.2, collected -3.8 +- 6.3, deaths +0.04 +- 0.10. **Passes.**
- `exp/vvg2`: team gold r300 -18.7 +- 8.6, Vesper's gold r300 -22.8 +- 9.1. Fails.

Platform rule for `exp/vvg1` (written now, before any game): `t03p` parts pinned to `t1503_tm@t03`. Target: Vesper's gold at r300 up by 1 standard error or more (`decoded.py types` or `gold`). Guards: margin and collected not down by more than 1 standard error. Wins recorded, not judged.
