# Five a side, near maps: Vendetta in Willow's place (dv5 against hy1 on b41)

Written Mon, Nov  2, 2026, 01:55 IST, before any game of panel b41.

## Why

Five a side is 65% of our ranked games (146 of 225 since 1478 went live, 49% won). On the decoded 1478 panels against
ranks 21-45 (`l1478_b38@b38`), the near maps (spawn walk under 61, where 1478 plays the Bamboo bot) are the weak cells:
five a side 9 of 26 and four a side 8 of 19 games won, against 16 of 30 on far maps five a side (bot_10). Five a side
near, to r1000 (the 26 games):

- gems collected 705 against 828; group captures 33.5 against 46.7, the whole gap in our own half (17.9 against 30.1);
- champion-rounds spent hitting camps are level (794 against 811), but the camp health they take is not (60.9k against
  80.8k): 76.6 per champion-round against 99.7. With one hitter alone on a camp (no stacking), 89 per hit against 128;
- by champion, single hits: our Willow 70, Heart of Ruin 57, Vesper 115, Marcella 119, Ryth 115; theirs Vendetta 177,
  Vesper 180, Ryth 134, Marcella 115, Heart of Ruin 62, Prism 222. We draft Heart, Vesper, Ryth, Marcella, Willow in
  every game; they draft Vendetta in 100% (Willow 31%);
- deaths are level (6.9 against 6.9).

So the economy gap at five a side comes from damage per camp hit, and the draft's fifth pick is the largest single
part of it. The Bamboo draft already has the switch (`kFifthPick = 4`, edit_vendfive.py: Vendetta in Willow's place,
five picks only); it was never measured five a side (row bd2 measured Vendetta for Willow four a side locally: wins down;
five a side was not run). Far maps (bot_10) and three and four a side are unchanged.

## Bots and panel

- Base: hy1 (platform 1484, selected), our copy of 1478, on b41 (unpinned), then the panel is pinned to its groups (b41p).
- dv5 (`bots/exp/dv5`): hy1 with `kFifthPick = 4` in `src/bb/draft.cpp`. Five picks on near maps: Heart of Ruin, Vesper,
  Ryth, Marcella, Vendetta.
- Panel b41 (`results/panels/specs_b41.txt`, `mkpanel.py --size 5 --maxsd 61 4101`): nine teams ranked 34-48 at 00:57
  IST 11-02 (Let's LARP again, 剑桥夜爬者, QS2isLaw, ひななー, Zarzorki, SilverSamurai, Nameless, The Party of Heroes,
  SkibidiSloppers), ten five-a-side near-map games each, five on each side: 90 games, 21 maps.

## Rule

Target metric: our gems collected to r1000 per game, paired game by game (`paired.py hy1_b41@b41 dv5_b41p@b41p 1000`).
dv5 passes if all hold:
1. collected to r1000: paired mean at least +40 a game and more than 1.5 standard errors above zero;
2. mechanism: our camp health taken per camp-hit champion-round (`tools/replay/campdmg.py`, to r1000) is higher than
   hy1's;
3. guard, deaths to r1000: paired mean not above +0.5 a game;
4. guard, kills (their deaths to r1000): paired mean not below -0.5 a game;
5. guard, the whole game: the final margin per game (`rcmp.py`, "margin diff ... (X +- SE/game)") not below zero by
   more than one standard error.

Wins are recorded, not judged. A pass is a proposal to the user and the team: the change is one constant in the
Bamboo part of 1478 (`src/bot` draft list). A run during which the active version changed by someone else's hand is void.

## Result (02:30 IST)

Not run on the platform. The local screen (`data/runs/multi-022145`, hy1 and dv5 against pool/cp3 and pool/bot_10 on six
five-a-side near maps, both sides, 24 games each) ran beside the base gate and failed: wins 18 to 14, deaths 102 to 162
(+2.5 a game), kills 217 to 166, collected 984 to 888 a game. The user then set the rule that a variant goes to the
platform only after it passes locally, so dv5's gate was stopped before its games (1487 cancelled, 1478 selected again).
The base run `hy1_b41@b41` (41 of 90 won) and the pinned panel b41p remain for the next five-a-side near-map variant.
