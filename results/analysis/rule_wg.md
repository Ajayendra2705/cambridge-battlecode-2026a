# Decision rule: winning-bag discipline (`exp/wg1`), written 11-03 16:57 IST before any game

**Factor.** A bag (or the biggest bags together) that lifts our tributed gems to 1000 and is not banked at once. On the ranked set `q_all` (773 games, 385 lost), 28 losses on non-gated maps held 1000 in hand, 20 of them in one bag (`tools/replay/lastrace.py`, `bagtrace.py`). The traces show the carrier recalling away from an altar 6 tiles off (02cuts, 02the_pond), going home to heal 10 tiles from an altar (00collision), walking away from an altar it had reached (00great_wall) and fighting 1 tile from one (03fan).

**Change.** `P_WB` on `bots/bamboo1530`: a champion whose bag is needed to reach 1000 walks the shortest way to the nearest altar, may dash past enemies, keeps its channel, and cancels a recall unless home and the walk back are shorter. With enemies in view this holds only for bags up to 120 gems. No capture+recall when the reward completes the win. Gated maps are unchanged.

**Local screen.** Local games replay exactly and the change acts only once our hand reaches 1000, so only those games are played (`tools/local/wbsel.py`): of the 680 games of `exp.b30` in `data/runs/multi-142332`, every loss that held 1000 in hand (11) and every win that held it with the rivals at 700 or more (149), paired game by game.

**Bar.** Target: rounds from our first winning bag to the game's end, mean over the paired games with a winning bag, at most 80% of the base's; losses that held 1000 in hand at most 7 of the base's 11. Guards: no bot fault; deaths in the paired games at most 102% of the base's; a win lost for a win gained counts against no bar, but wins in these games must not fall by more than 2 (recorded, not judged beyond that).

**Platform.** Asking the user first. Same factor on a pinned panel with the same session's base: rounds from the first winning bag to the end and losses holding a winning bag; guards on deaths and collected. A pass here is needed, not enough.

## Results of the first sample, and a new bar written 11-03 17:19 IST before the fresh sample

160 paired games, base 149 wins, 28.34 rounds from the first winning bag to the end, 11 losses that held 1000 in hand, 462 deaths, margin 28929.

| Variant | Change | Wins (up, down) | Rounds to the end | Losses holding 1000 | Deaths | Margin |
|---|---|---|---|---|---|---|
| wg1 | as above, with the team rule | 135 (3, 17) | 26.59 | 13 | 468 | 25767 |
| wg2 | one bag alone only | 148 (2, 3) | 23.27 | 11 | 468 | 28804 |
| wg3 | wg2, threat-avoiding walk, direct altar only for a detour of 6+ | 148 (2, 3) | 23.79 | 11 | 470 | 28819 |
| wg4 | wg3, recall cancelled only when healthy (60%+), unseen and 8+ rounds shorter; the walk beside enemies only if it outlives them | 149 (2, 2) | 24.43 | 10 | 462 | 29303 |
| wg5 | wg4, the same test before skipping a capture+recall | 149 (0, 0) | 25.78 | 10 | 462 | 29333 |

**Every variant misses the bar above** (rounds at most 80%, at most 7 losses holding 1000). wg1's team rule is rejected: it sends the biggest bags to an altar as soon as the team's hand reaches 1000, which can be far from the end of the game, and 17 wins became losses. wg2 and wg3 flipped three games to losses by cancelling recalls that heal and shop and by walking into enemies. Of the 11 losses, 5 ended within 25 rounds of the first winning bag or on a gated map, so no walk could change them, and the bar on them was set without knowing that.

**New bar for wg5, on a fresh sample so it cannot lean on what was just seen.** `exp.b30` and wg5 against pool bots they have not been tuned on (`pool/v1498`, `pool/hb4`, `pool/cmb2`, `pool/rz20`), all 85 maps, both sides, with `tools/local/wbsel.py` picking wg5's games. Target: rounds from the first winning bag to the end at most 93% of the base's. Losses that held 1000 in hand not above the base's. Guards: no bot fault; games flipped to a loss at most those flipped to a win plus 1; deaths at most 101%; margin not below the base's.

## wh1: Bamboo's finish set on the main line, written 11-03 17:24 IST before any game

Bamboo's `bot.cpp` holds the same leak with its own ranked stories (rows against Peaky: 891 tributed and 231 carried, three carriers recalled home to shop; expanse against Cabbage: a shopping recall the round before the capture that made 1002; interlock against Team SKKU: 980 tributed, two carriers with 36 each hovering 24 rounds beside the altar). Its note on the set: `kFinishDeliver` alone +3 +- 3, with `kFinishGuard` and `kFinishBudget` +25 +- 10 and wins +16 of 408 on local seeds.

**Change on wg5.** (1) Team rule inside a window of 400 tributed gems: the carriers nearest an altar whose bags cover the rest bank now, the others keep farming (`finish_carrier`). (2) No shopping trip once tributed plus all bags are within 100 of 1000 (`kFinishNoShop`, `kNoShopSlack`). (3) A champion without a bag, with a carrier at an altar within 6 tiles and an enemy within 6 of that carrier, hits the weakest such enemy if our side there is the stronger (`kFinishGuard`). (4) Tributed plus bags plus the camp under way reach 1000 and no enemy seen for 10 rounds: no trip home above 5% health (`kFinishBudget`).

**Local screen.** All 680 games against `exp.b30`'s run (`data/runs/multi-142332`, pools cmb7, bot_10, cp3, dh3), since (2) and (4) act just before the hand reaches 1000. **Bar:** rounds from the first winning bag to the end at most 93% of the base's; losses that held 1000 in hand not above the base's; no bot fault; games flipped to a loss at most those flipped to a win plus 1; deaths at most 101%; margin not below the base's. The bar is judged again on the fresh sample, which wh1 has not been tuned on.

## Results of all 680 games on both samples, 11-03 19:05 IST

The selected games lean (only close wins and hand losses are picked) and a change can re-roll a game through fuel, so the full runs decide. Base `exp.b30`: first sample `data/runs/multi-142332` (pools cmb7, bot_10, cp3, dh3; 575 wins), fresh sample `data/runs/multi-172019` (pools v1498, hb4, cmb2, rz20; 553 wins). Readers: `tools/local/wbcmp.py`, `tools/local/divround.py`; outputs `data/judge_wh1_all.txt`, `wh1f_all`, `wg5_all`, `wg5f_all`.

| metric | wg5 first | wg5 fresh | wh1 first | wh1 fresh |
|---|---|---|---|---|
| wins (base 575, 553) | 578 | 553 | 568 | 550 |
| flips up / down | 3 / 0 | 4 / 4 | 7 / 14 | 10 / 13 |
| rounds from the first winning bag to the end, % of base | 90.0 | 93.1 | 93.4 | 86.6 |
| losses that held 1000 (base 11, 14) | 10 | 14 | 15 | 15 |
| deaths, % of base | 99.1 | 99.6 | 101.4 | 100.3 |
| margin, change | +2303 | -537 | -6066 | -846 |
| bot faults | 0 | 0 | 0 | 0 |

**wh1: rejected.** On the first sample it fails the rounds bar, the losses bar, the flips bar, the deaths bar and the margin bar; on the fresh sample the losses bar, the flips bar and the margin bar. No single part of the set explains the flips (switch-off runs wh2 to wh5). Only 183 of 680 games stay identical, 444 part after the hand reached 600, and those give flips 3 up and 9 down.

**wg5: passes the first sample, misses the fresh one by a hair.** On the fresh sample the rounds bar reads 93.1 against 93 and the margin guard -537 against "not below" (-0.8 a game). The bars stay as written, so wg5 has not passed and does not go to the platform as it is. Its games are mostly untouched: 503 of 680 stay identical on both samples, and on the first sample the 154 that part after the hand reached 600 flip none. Together over 1360 games: wins +3, flips 7 up and 4 down, rounds 92% of base, deaths 99%, margin +1766.
