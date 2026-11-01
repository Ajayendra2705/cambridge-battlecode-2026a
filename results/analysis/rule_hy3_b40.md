# Three a side: vx1 or bot_10 in place of the Bamboo bot (hy3v, hy3b against 1478 on b40)

Written Sun, Nov  1, 2026, 19:59 IST (last edit 20:03), before any game of panel b40 (the first gate started 20:04:57).

## Why

Three a side is the widest gap against teams above us. In 95 decoded ranked games of 1472 against teams rated above us
(`data/fights/rk1472_above`, three-a-side part `data/fights/rk1472_above3`, 17 games): wins 5 of 17; gems collected
by r1000 473 against 701; deaths 4.41 against 3.35; middle captures 11.9 a game (121 gems) against 21.8 (258 gems);
our Vesper collects 128 and dies 1.24 times, theirs 280 and 0.43. Since 1478 went live (17:20-19:30 IST), ranked
three a side against teams above: 2 of 7. 1478 plays the Bamboo bot (1472) on every three-a-side map (none is far).
Locally all candidates are level three a side (`results/analysis/h2h_fuel_1101.md`), so only the platform can choose.

## Bots

- Base: 1478, the team's live bot, played as live (`live`, no selection) on b40, then pinned (b40p).
- hy3v (`bots/exp/hy3v`): vx1 three a side; 1478's rule elsewhere (Bamboo bot near, bot_10 far by spawn walk 61).
- hy3b (`bots/exp/hy3b`): bot_10 (b10n) three a side; 1478's rule elsewhere.

Panel b40 (`results/panels/specs_b40.txt`, `mkpanel.py --size 3 4001`): nine teams ranked 18-38 at 19:55 IST
(Supaswag, procless, SSSA, conqueror_of_openai, SkuBap, BattleCats, Jupiter, QS2isLaw, SquidProxyLovers), ten
three-a-side games each, five on each side: 90 games.

## Rule

Target metric: our gems collected by r1000 per game, paired game by game against the base (`paired.py`).
A variant passes if all hold:
1. collected by r1000: paired mean at least +40 a game and more than 1.5 standard errors above zero;
2. guard, deaths by r1000: paired mean not above +0.5 a game;
3. guard, the whole game: L->W flips at least as many as W->L (wins are recorded, not judged beyond this).

If both pass, the one with the larger collected gain is proposed. A pass is a proposal to the team, not a switch:
1478 is the teammate's build, so either the three-a-side part goes into the team's build or our build (hy3v or hy3b)
replaces it, and that needs hy1's games on b38q to match 1478's (identity check `hy1_b38q`, last in the same chain).
Locally the four- and five-a-side games of hy3v and hy3b are not byte-identical to hy1's (8 and 3 of 18 differ in
length; the extra code changes fuel use or memory layout), but all 18 have the same winner (run `multi-195654`).
A run during which the active version changed by someone else's hand is void.

## Addendum: hy3s (written 20:53 IST, before any hy3s game)

hy3s (`bots/exp/hy3s`) is hy1 with one change in the Bamboo part (`kSolo3`): three a side, control maps too, the
champions farm solo after the opening (`quiet()` true; squad size 1 instead of `kControlSquad` 2). Why: on b40 our
three share 60% of camp-hit rounds against the rivals' 31% and capture 38.4 groups a game against 59.4 (findings,
"Three a side against ranks 18-38"); ten of the twelve three-a-side maps are control maps (spawn walk 45 or less),
where the Bamboo bot farms in pairs whenever an enemy is in sight.

Same rule as above (collected to r1000 +40 a game and more than 1.5 standard errors; deaths not up by more than 0.5;
L->W at least W->L), plus a mechanism check that must hold for the change to count as working: the shared camp-hit
share (`cohesion.py`, r0-1000) falls from 0.60 to 0.45 or less. Four and five a side are not affected.
