# Champions and drafts

## Enums (SDK 3.0.1)

| Index | `champion_draft` | `champion_type` |
|---|---|---|
| 0 | ryth | ryth |
| 1 | vesper_vale | vesper_vale |
| 2 | vendetta | vendetta |
| 3 | cassi_and_issac | cassi |
| 4 | stellar | issac |
| 5 | prism | stellar |
| 6 | marcella | prism |
| 7 | willow | marcella |
| 8 | ren | willow |
| 9 | varg | ren |
| 10 | tavi | varg |
| 11 | heart_of_ruin | tavi |
| 12 | — | heart_of_ruin |

The platform's match listing reports `draftPicks` in `champion_draft` numbering and `characters` in `champion_type`
numbering. Cassi & Issac is one pick that brings two champions who die together.

Patch changes per champion are in `patch-2026-10-20.md`.

## The new meta (October 20, ~13:00 UTC: 30 recent ranked games each)

By the afternoon of October 20 the leaders had moved to **Heart of Ruin + Ren (+ Ryth)** on every map:

| Team | Record | Drafts | Camp deaths / enemy deaths a game |
|---|---|---|---|
| procless | 15/30 | 20× HoR, Marcella, Ren, Ryth, Tavi; 3 picks HoR, Ren, Ryth; 4 picks + Tavi | **0.7** / 8.1 |
| Sponge (Albert and Bob) | 18/30 | 19× HoR, Ren, Ryth, Stellar, Varg; 3 picks HoR, Ren, Stellar | 1.6 / 5.7 |
| Sneaky Bush Campers | 20/30 | HoR, Ren, Ryth in all 30, + Stellar/Tavi or C&I | 5.8 / 7.5 |
| Nyx | 19/30 | still C&I, Ren, Ryth, Stellar, Varg | 9.5 / 8.3 |
| Bamboo7 v193 (80 bench games) | 19/80 | see `bot-status.md` | 3.8 camp-only |

**Builds: defence first, damage from ~round 650** (`scratchpad/ft/buildorder.ts`):

- procless: HoR and Marcella Jungle Strength (r200) → Durability Health (r330) → Monster → Bruiser Strength stack;
  Ren and Ryth Bruiser Health → Durability Health → Monster → Bruiser stack.
- Sponge: Treasure Health first on every tank (Stellar Treasure Focus) → Jungle → Bruiser Health → Durability Health →
  Power (Focus on HoR and Ren).
- Sneaky: HoR Treasure Health → Jungle Focus → Bruiser/Durability Health → Power Focus; Ren and Ryth Bruiser Health →
  Jungle → Durability Health → Power.
- Jungle (−30% camp damage) is owned by r600 by 73–100% of their champions. Bruiser is a stat emblem (5 of the chosen
  stat, 1 of each other) with no passive.

They capture ~85 groups a game (procless, Nyx; their opponents ~60), mostly clusters and wolves; monoliths are rare
(0.1–0.4 a game, first around r1,000–1,800).

## What the top teams drafted (morning of October 20, right after the patch)

Nobody had adapted their drafts yet:

- Nyx: Ren, Stellar, Cassi & Issac, Ryth, Varg.
- Univardisty of Shingtonwash: Stellar, Cassi & Issac, Tavi, Ren, Prism.
- KratosMessi: Cassi & Issac, Stellar, Varg, Ryth, Ren.

## Who buys the Treasure emblem (160 ladder games, October 20)

| Team | Treasure emblem on |
|---|---|
| Nyx | almost every champion: Ren 32/32, Stellar 34/34, Cassi 40/40, Issac 39/40, Ryth 30/32, Varg 30/32 |
| Univardisty of Shingtonwash | Tavi only (32/34) |
| Mite, procless | almost never |
| Bamboo7 up to v189 | the strength carriers (Varg, Issac, Ryth, Vendetta), never the casters |

The emblem's passive pays 5–10% of a team's gold over a game, most on the maps that reach round 2,000 (contest 1,537,
boss-battle 2,417 treasure gold for the opponents). From v190, every champion buys it first on scaling maps
(`kTreasureBuild`, see `bot-status.md`).

## Our draft tests (local, strong bench, after the patch)

| Draft | Result vs our map-dependent lists |
|---|---|
| Old meta forced on every map (C&I, Stellar, Varg, Ryth, Ren) | −122 ± 56 |
| C&I, Willow, Varg, Vendetta, Prism | −376 ± 59 |
| C&I, Stellar, Willow, Vendetta, Varg | −242 ± 53 |
| Heart of Ruin, C&I, Willow (one game, collision) | 27 deaths to 3; our fight code mishandled unfamiliar champions (before `kRuinKit`) |
| Marcella instead of C&I wherever our lists pick C&I (`kTwinSwap` 1, one seed) | −4 ± 48 (87 vs 85 wins of 126): eight −750, interlock +253, broken-curve +229, fracture +286 |
| Vesper Vale instead of C&I (`kTwinSwap` 2, one seed) | −46 ± 48 |

| Marcella for C&I, current base (`kTwinSwap` 1, two seeds) | +35 ± 51, +59 ± 41 (174 vs 162 wins of 252) |
| Heart of Ruin for C&I (`kTwinSwap` 3, two seeds, with `kRuinKit`) | +18 ± 51, −10 ± 45 (neutral) |
| Heart of Ruin for Varg (`kVargSwap` 5) | +1 ± 29; with Marcella for C&I +41 ± 44, +60 ± 39 |
| In Tavi's slot (`kTaviSwap`): Marcella / Vesper Vale / Vendetta / Prism / Heart of Ruin | −20 / −62 / −110 / +11 / −8 (only the 9 maps where we draft Tavi) |
| Stun draft on farming maps (`kStunDraft` 1: Heart of Ruin, Ryth, Stellar, Ren, Marcella; two seeds) | +27 ± 24; with `kMeleeEase` 0.75 +34 ± 22 (eight +535, concentrated-wealth +264, lanes +187; expanse −166, monolith −155) |
| ... plus `kChainStun` (global) | −46 vs the draft alone: neutral on farming maps, −200 to −420 on contest, corners, collision |
| ... counter-picking on other maps when the enemy's revealed picks are mostly ranged (`kStunDraft` 2) | −56 (fragment −673, elk-arena −846) |
| Marcella for C&I + stun draft + `kMeleeEase` 0.75 (two seeds) | **+53 ± 33** (173 vs 162 wins of 252): v193 |

Willow drafts have lost in every test so far: our bot doesn't use a healer well. Marcella for Cassi & Issac (user's
suggestion, Oct 20) is level locally; the local bench may not show the twins' mid-late weakness against stronger teams,
so it is a ladder candidate.

## The second patch (October 21) and our drafts

Numbers in `patch-2026-10-20.md`. What it changes for drafting:

- **Stellar** (650 HP, 70 Focus) is now the weakest caster: her burst (2 × 70 = 140) is below Prism's stun (1.5 × 80 =
  120 at no gems, 180 with a 40-gem bag) and Tavi's (1.4 × 110 = 154). Our farming-map stun draft (`kStunDraft` 1) and
  most of our lists still take her as the ranged burst.
- **Prism** gains 1.5 Focus per carried gem: a 40-gem bag is +60 Focus (a 80-gem bag +120, more than doubling his
  spells). Eric's plan (Oct 21): draft Prism on farming maps and make him the squad's gem carrier (`kPrismFarm` in
  draft.cpp, `kPrismCarry`/`kPrismBag` in bot.cpp; see bot-status.md for the screen).
- **Heart of Ruin** at 30 Strength and a 1.5 × Focus dash (150 at 100 Focus) is a weaker camp clearer; the stun and
  the shield are unchanged. Still first in the stun draft until measured on the ladder (the local engine cannot).
- **Ren**'s stun does 75 instead of 125; his retaliation and dash are unchanged.
- **Vendetta** (1000 HP), **Vesper Vale** (1000 HP, 55 Strength) and **Tavi** (900 HP, 110 Focus) are sturdier picks
  than before; the party-size model (`camps-and-maps.md`, elk camps) favours melee health, so Vendetta is a better
  farming-map tank now.

## What the top six draft now, by map type (144 ranked games since the Heart of Ruin nerf, October 20 21:30 → 21 05:30 UTC)

24 ranked games each (downloaded with `scratchpad/ft/list_team.ts` + `cambc matches download`, tallied with
`ft/drafttally.sh` from the match records' `draftPicks`; the replays were deleted again in the October 21 clean-up and
are re-downloadable; farming/contest split as in `camps-and-maps.md`).
**Every team drafts Heart of Ruin and Ren in every game, on farming and contest maps alike**; nobody drafts Prism or
Willow, and the composition does not change with the map type, only with the pick count:

| Team (rank) | 5 picks | 4 picks | 3 picks |
|---|---|---|---|
| Intercontinental Fish (1) | C&I, HoR, Ren, Ryth, Stellar (14/14) | C&I, HoR, Ren, Stellar | HoR, Ren, Stellar |
| :3 (2) | HoR, Ren, Varg, Vendetta, Vesper (10); HoR, Marcella, Ryth, Stellar, Vesper (3) | HoR, Ren, Vendetta, Vesper | HoR, Ren, Vendetta |
| FürFortnite (3) | HoR, Marcella, Ren, Ryth, Stellar (12/12) | HoR, Ren, Ryth, Stellar | HoR, Ren, Stellar |
| EMPEROR Tung (4) | HoR, Ren, Ryth, Stellar, Varg (17/17) | HoR, Ren, Ryth, Stellar | HoR, Ren, Stellar or HoR, Ren, Ryth |
| Nyx (5) | HoR, Ren, Ryth, Stellar, Tavi (17/17) | HoR, Ren, Ryth, Stellar | HoR, Ren, Ryth |
| procless (7) | HoR, Marcella, Ren, Ryth, Stellar (13/13) | HoR, Ren, Ryth, Stellar | HoR, Ren, Ryth |

The consensus core is **HoR + Ren**, then Ryth and Stellar, then a fifth of taste (Marcella, Tavi, Varg, C&I). :3 is the
outlier (Vendetta + Vesper Vale gold farming). Our v203 three-pick draft (HoR, Ryth, Stellar) differs from the
consensus (HoR, Ren, Stellar / HoR, Ren, Ryth) by Ren; our farming-map five-pick stun draft (HoR, Ryth, Stellar, Ren,
Marcella) is exactly FürFortnite's and procless's; our contest-map lists (Marcella for C&I, Stellar, Tavi, Ren ...)
are the ones that differ from everyone.

## Intercontinental Fish's drafts per map (70 ranked games since the Heart of Ruin nerf, October 21)

Fish's draft depends **only on the number of picks**, never on the map or its type. Pick order as recorded:

| Picks | Draft (in pick order) | Maps | Record |
|---|---|---|---|
| 3 | Stellar → HoR → Ren | collision, fragment, packs, broken_curve, the_farm (contest); gold_rush (farming) | 11/22 |
| 4 | Stellar → HoR → Ren → C&I | hooks, swirl, reverse_spiral, rushbait_v2 (contest); shortcut, rows (farming) | 11/12 |
| 5 | Stellar → HoR → Ren → C&I → Ryth | every other five-pick map, contest and farming | 23/33 |
| 5, boss map | Ryth → Stellar → Prism → HoR → Ren | stampede (one 17k-health camp holds the gems) | 3/3 |

So the "must have" core is **Stellar + Heart of Ruin + Ren** in every one of the 70 games; Cassi & Issac joins at four
picks and Ryth at five. The only exception is the boss map, where Prism (area damage plus Focus from the carried
gems) replaces C&I and Ryth goes first. The other five leaders also draft HoR + Ren in every game (table above); their
fourth is Ryth (FürFortnite, Tung, Nyx, procless) rather than C&I. Stellar is Fish's first pick and its gold carry
("Who holds the gold" below), which is the pattern behind the order: the carry is secured first, the two melee stunners
that protect it next, then bodies.

Our draft differs in three places: three-pick maps (v203: HoR, Ryth, Stellar — no Ren), four-pick maps (our contest
lists: C&I swapped for Marcella, Tavi, Ren, Stellar), and contest five-pick maps (Stellar, Prism, Ren, Tavi, Ryth).
`kFishDraft` (draft.cpp; 1 Fish's lists, 2 the other leaders' consensus) drafts by pick count only.

## procless's and :3's drafts (70 ranked games each, October 21 05:10–07:30 UTC)

**procless** changed its draft at a resubmission around 06:30 UTC; inside each period the draft depends only on the
pick count, never on the map:

| Picks | Before ~06:30 (40 games) | Since ~06:30 (30 games) |
|---|---|---|
| 3 | HoR → Ryth → Ren (2 of 11 won) | HoR → Vesper → Ryth (7 of 7 won) |
| 4 | HoR → Ryth → Ren → Stellar (6/8) | HoR → Vesper → Ryth → Marcella (6/8) |
| 5 | HoR → Ryth → Ren → Stellar → Marcella (7/21) | HoR → Vesper → Ryth → Marcella → Vendetta (7/15) |

So procless dropped Ren and Stellar for **Vesper Vale** (the gold-bonus ranged champion, buffed to 1000 HP / 55
Strength in the pending patch) and added Vendetta at five picks. Heart of Ruin first and Ryth in every draft.

**:3** keeps **two drafts and picks between them by map**, consistently (every game on a map uses the same one):

| Picks | Family A (Vendetta/Varg) | Family B (Ryth/Marcella/Stellar) |
|---|---|---|
| 3 | HoR → Vendetta → Ren (8/12) | HoR → Ryth → Vesper (fragment, 0/1) |
| 4 | HoR → Vendetta → Ren → Vesper (4/11) | HoR → Ryth → Vesper → Marcella (hooks, 0/1) |
| 5 | HoR → Vendetta → Ren → Vesper → Varg (**23/31**) | HoR → Ryth → Vesper → Marcella → Stellar (8/14) |

Family B maps: 00contest, 00elkring, 00stampede, 01hooks (no wolves at all: monoliths, elks or one boss camp),
00eight, 00pilgrimage, 01concentrated_wealth (few wolves, elk camps) and 00fragment. Family A everywhere else: maps
with wolf packs and clustered hitters (`scratchpad/mapfeat.txt`: e.g. boss_battle 30 wolves / 74 packed hitters,
swirl 24 / 42, the_farm 24 / 44), where Varg's splash and Vendetta's kill resets clear packs fast. It is the only top
team whose draft follows the map, and the rule looks like **"wolf packs → Vendetta + Varg; no wolves (elks, bosses) →
Ryth + Marcella + Stellar"**, with Heart of Ruin first and Vesper Vale in both. :3 is the second-ranked team.

Across Fish, procless and :3 the common pattern is: **Heart of Ruin in every draft (first for procless and :3, second
for Fish behind its Stellar carry)**, a melee stunner beside it (Ren or Ryth), and a gold engine (Fish: Stellar as the
carry; procless and :3: Vesper Vale's +33% gold); nobody drafts by "PvP vs farming map".

## Where the top teams put their items, by map type (October 20 sets, 30 games a team; `tools/stress/buildorder.ts`)

The item order of every team is the **same on farming and contest maps**; what differs is the team's style. Median
round of each emblem (1st → 4th) and the share of champions holding the kind by round 600:

| Team | Style | Heart of Ruin | Ren / Ryth | Casters (Stellar, Cassi, Tavi) |
|---|---|---|---|---|
| procless | Jungle first, Power late | Jungle Str r200 → Durability HP r330 → Monster Str r470 → Bruiser/Power Str r560 (by r600: Jungle 97%, Durability 86%, Monster 69%) | Bruiser HP r255 → Durability HP r345 → Monster r455 → Bruiser r560 | Tavi: Bruiser Str r325 → Durability HP r630 → Monster → Bruiser |
| Sponge | Treasure first on everyone | Treasure HP r200 → Jungle Focus r280 → Bruiser HP r405 → Durability HP r525 → Power Focus r575 | Treasure HP → Bruiser HP → Jungle Focus → Durability HP → Power Focus (r865) | Stellar: Treasure Focus r380 → Power Focus r605 → Durability HP r895 |
| Sneaky Bush Campers | Treasure on HoR, Power on casters | Treasure HP r205–305 → Jungle Focus → Bruiser HP → Durability HP → Power Focus r615–775 | Bruiser HP r185–275 → Jungle r440–470 → Durability HP → Power | Stellar: Power Focus r160–300 → Jungle Focus → Durability Focus → Bruiser HP |
| Nyx | Treasure first on everyone (also Issac and Varg) | — (no HoR on Oct 20) | Ren: Treasure HP r140–195 → Bruiser HP → Durability HP → Power Focus r435–535; Ryth: Treasure → Bruiser HP → Durability HP → Power Str | Cassi/Stellar: Treasure Focus r80–195 → Jungle Focus → Durability Focus → Bruiser HP → Power Focus r485–560 |
| Intercontinental Fish (pre-patch games) | Power first, Home HP second | — | Ren: Bruiser/Durability HP r115–150 → Power Focus r295 | Stellar: Power Focus r105–130 → Home HP r160–255 → Durability HP |

Common to all (except pre-patch Fish): a **defensive core by round 600** (a Health or Jungle emblem first or second,
Durability Health third; Bruiser Health on the melee), damage (Power, or Bruiser Strength for procless) only from
round 550–800, and Monster only on procless. On contest maps the games run longer and gold piles up (Nyx 19k gold on
PvP maps vs 8k on farming maps), but the order does not change. Our `kMetaBuild` 1 copies procless's order; the fresh
(post-nerf) sets are being profiled the same way.

## The same question on the fresh games (144 ranked games since the nerf, October 21; `scratchpad/top21split/`)

Again **no team changes its emblem order with the map type**. What changed since October 20: **Treasure first is
now universal** (5 of the 6 teams open with a Treasure emblem on every champion by round 180–330, procless included,
which opened with Jungle on October 20), and the damage emblem comes earlier for the leaders:

| Team (rank) | Heart of Ruin | Ren / Ryth | Stellar (or the caster) | Notes |
|---|---|---|---|---|
| Intercontinental Fish (1) | Treasure Focus r160–180 → **Power Focus r240** → Home HP r285–395 → Durability HP → Power | Ren: Bruiser HP r340–385 → Durability HP → Power Focus r520–550; Ryth: Bruiser HP → Durability HP → Power Str | Treasure Focus r90 → **Power Focus r180** → Durability/Home HP → Power | the most aggressive builder; Issac Treasure Str → Power Str → Home HP |
| :3 (2) | Jungle Focus r175–230 → Treasure → Monster Focus → Durability HP → Bruiser Focus | Ren: Jungle HP → Treasure Str → Monster Str → Durability HP → Bruiser; Vendetta: Jungle HP r145–195 → Treasure HP → Monster HP → Durability Str → Bruiser | Vesper: Bruiser HP → Treasure Str → Monster → Durability | the only Jungle-first team; 0.1 camp deaths a game on farming maps |
| FürFortnite (3) | Treasure Focus r90–190 → Bruiser Focus → Durability HP → Bruiser Focus stack | Ren: Treasure Str → Bruiser Str → Durability HP → Bruiser; Ryth: Treasure HP → Bruiser HP → Durability HP | Treasure Focus r180–305 → Bruiser Focus → Durability HP → Bruiser | no Jungle, no Power at all: Treasure + Bruiser stats |
| EMPEROR Tung (4) | Treasure HP r235 → Jungle Focus r300–360 → Bruiser HP → Durability HP → Bruiser Focus r525–560 | Treasure HP → Jungle Str → Bruiser HP → Durability HP → Bruiser Str | Treasure Focus r240–300 → Jungle Focus → Bruiser HP/Durability HP → Bruiser Focus | Varg: Treasure HP → Jungle Str → Durability HP → Bruiser Str |
| Nyx (5) | Treasure Str r275–400 → Power Str r380–485 → Durability HP → Power Str | Ren: Treasure HP → Bruiser HP → Durability HP → Power Focus r470–520; Ryth: Treasure HP → Jungle HP → Durability HP → Power Str | Treasure Focus r120–175 → Jungle Focus r230 → Durability Focus → Bruiser HP → Power Focus r500 | Tavi: Treasure Focus → Power Focus |
| procless (7) | Treasure Focus r180–200 → Durability HP r255 → Home HP r340–390 → Power Focus r455–535 | Bruiser HP r135–245 → Durability HP → Monster → Bruiser (as on Oct 20) | Treasure Focus r285–375 → Durability HP → Home HP → Power Focus | Marcella keeps Jungle Str → Durability HP → Monster → Bruiser |

What this means for us: our `kTreasureBuild` 1 buys Treasure first only on scaling maps and `kMetaBuild` 1 copies
procless's October 20 order (Jungle, Durability, Monster, Bruiser); the top six now open with Treasure on every map,
and Fish and Nyx go to Power second or third on casters and Heart of Ruin. Candidates to screen next: Treasure first
everywhere, then Durability HP, then Power/Bruiser (Fish/procless), with Jungle only on the melee that tanks camps.

## Who holds the gold (144 fresh games; `tools/stress/goldconc.ts`)

Mean earned gold and emblems per champion at round 300 and 600, and the share of the team's gold its richest champion
holds. Our own numbers are v203 in 8 local games against B7Base (and v201 in Eric's two games against Nyx).

| Team | Team gold r300 → r600 | Richest holds | The carry at r300 → r600 | Second |
|---|---|---|---|---|
| Intercontinental Fish | 1,519 → 3,682 | 49% → 46% | **Stellar** 592 g, 3.0 emblems → 1,505 g, 9.0 (richest in 58–65% of games) | Heart of Ruin 491 g, 2.5 → 1,108 g, 6.3 |
| Nyx | 1,223 → 3,229 | 47% → 44% | **Stellar** 546 g, 3.0 → 1,382 g, 8.5 (richest in 71–77%) | Ren 269 → 717 g |
| FürFortnite | 1,189 → 2,836 | 55% → 49% | **Heart of Ruin** 602 g, 3.2 → 1,373 g, 8.3 (richest in 75–79%) | Stellar 225 → 609 g |
| procless | 1,273 → 3,264 | 41% | **Heart of Ruin** 404 g, 2.0 → 1,125 g, 6.7 | Ryth 372 g, 2.0 → 859 g, 5.0 |
| EMPEROR Tung | 1,219 → 3,007 | 38% → 36% | Heart of Ruin 359 g → 901 g, 4.7 | Varg 302 → 670 g |
| :3 | 1,234 → 2,814 | 43% → 45% | spread: Marcella, Vendetta, HoR, Ryth each 340–440 g at r300 | — |
| **Bamboo7 v203 (local)** | 731 → 1,717 | 46% → 47% | Ren 319 g, 1.5 emblems → 628 g, 3.3 | Ryth 231 → 545 g |
| Bamboo7 v201 vs Nyx (2 ladder games) | 780 → 2,033 | 37% → 29% | Ren 275 g, 1.5 → 537 g, 2.5 | Nyx's Stellar in those games: 896 g, 5.5 emblems → 2,336 g, 15.5 |

Two gaps, both large: the top teams **earn 1.6–2× our gold by round 300**, and they **funnel it into one champion**
(Stellar for Fish and Nyx, Heart of Ruin for FürFortnite and procless) who holds 3 emblems by round 300 and 8–9 by
round 600, while our richest holds 1.5 and 3.3. That is the champion that one-shots ours in the early fights. Our
rewards go to whoever stands on the tiles (`kSingleCapturer`, carriers only for Varg and Vendetta), so the gold spreads
over the melee. A designated carry switch (`kCarry` 1 Stellar / 2 Heart of Ruin: the carry walks onto every reward
its squad clears, the others step off) is being screened with Treasure-first-everywhere (`kTreasureBuild` 2).

## Heart of Ruin in our bot (`kRuinKit`, October 20)

Nerfed the evening of October 20: +4 Strength and +12 Focus a shard (were 5 and 15); see `patch-2026-10-20.md`.

Its dash (range 2, landing hit 1.75 × Focus and a 1-turn stun within radius 1) is cast as an attack: `ruin_dash` lands
beside the target on the free tile whose radius holds the most visible enemy champions; the basic attack follows. It
builds Power Focus and Durability Health (+15 Focus a shard vs +5 Strength). In six test games it landed the hit 11–33
times a game on camps and up to 4 times on champions, and died 1.5 times a game.

## Top-10 builds and kit use on engine 2.0.0 (October 27)

Builds and per-champion numbers from 25 ranked games per top-10 team plus ours (`scratchpad/builds2.py`, summaries in
`results/sum`); kit use from 122 top-10 bench replays of #380-#382 (`scratchpad/kituse.py`, `horshield.py` on `extract1.ts` traces).

| Champion | Top teams' line (first three, then the end mix) | Ours (live #388) | Gold by r600 top / ours |
|---|---|---|---|
| HoR | Treasure H > Jungle F > Bruiser H or Durability H; ends Bruiser F 1.2, Bruiser H 1.1 (Focus 52%) | Treasure H > Jungle F > Bruiser H forever (Health 85%) | 449 / 525 |
| Vendetta | Treasure S > Prospector S > Jungle H, or Hunter S > Jungle S > Durability H; ends Bruiser S 2.2, Bruiser H 1.4 | never drafted | 645 / - |
| Vesper | Treasure S > Jungle S > Bruiser H or Power S; ends Bruiser S 5.4, Bruiser H 2.6 | Treasure/Jungle S > Durability H; Bruiser S (Str 91%) | **1,114 / 481** |
| Marcella | Treasure F > Durability H > Bruiser F; ends Bruiser F 3.5, H 2.0, S 1.8 | Treasure F > Jungle F > Bruiser F (Focus 100%) | 946 / 854 |
| Ryth | often nothing until r440; Health 69% | Treasure H > Jungle H > Bruiser H | **303 / 571** |

- **Gold distribution:** by r600 the top teams earn 3,100 gold a game to our 2,015; Vesper takes 32% of theirs (her passive adds 33%),
  ours 22%, while our Ryth takes 25% (theirs 5%). `kVesperCarry` only acts in squads; after the opening we farm solo.
- **HoR shield** (slot 0, cooldown 8): top 4.9 casts per 100 rounds vs ours 3.1; 27% of theirs at full health (ours 6%), 18% with an
  enemy champion 4-6 tiles away and no camp (ours 6%). Ours waits for 85% health or an enemy within 3 (`kShieldEarly`).
- **HoR dash:** top lands next to an enemy in 11% of dashes and dashes away in 7%; ours 7% / 13%. Attacks on champions 4.9 vs 3.8 per
  100 rounds; frontline (closest of its team) in 79% vs 74% of rounds with an enemy within 5.
- **Vendetta (top):** attack reset 5.1 per 100 rounds, two thirds with no enemy near (camp kills reset it); dash 7.9 per 100 rounds,
  70% plain travel (kills refresh it); frontline 76%.
- **Willow / Vesper:** the top teams keep them out of contact - Willow has an enemy within 3 in 1.2% of rounds (ours 6.1%), Vesper
  5.7% (ours 8.3%); our Vesper dashes away from enemies in 24% of dashes (theirs 11%).
- Local screens (Oct 26-27, #388 config, H340 + B7Live): Focus-heavy HoR lines `kRuinBuild` 1/2/3 -11/-12/-25, passive-aware odds
  `kRuinOdds` -5, HoR escape line 0.3 +2 (all ±6-10); Vendetta for Willow (`kDraftAlt` 2, default build) -125.

## Intercontinental Fish on engine 2.0.0 (October 27; 75 ranked games, replays/p2/fish_rk)

| Picks | Draft (games) |
|---|---|
| 3 | Vesper > HoR > Marcella (13/14) |
| 4 | Vesper > Vendetta > HoR > Cassi & Issac (13/15) |
| 5 | Vesper > Vendetta > HoR > Cassi & Issac > Marcella (25/46); Varg / Ren / Willow 7 each - the same fifth on a map whatever the opponent |

| Champion | Emblem line (median completion round) | Recalls a game (median health / gold) |
|---|---|---|
| Vesper | Treasure S 150 > Jungle S 225 > Bruiser H 280 > Durability H 385 > Bruiser S on | 9.1 (62% / 183) |
| Vendetta | Treasure H 200 > Jungle S 310 > Bruiser H 395 > Durability H 465 > Bruiser S on | 8.9 (40% / 156) |
| Marcella | Treasure H 100 > Jungle S 175 > Bruiser H 240 > Durability H 285 > Bruiser S on | 5.5 (68% / 228) |
| HoR | Treasure H 350 > Jungle F 495 > Bruiser H on | 9.2 (39% / 44) |
| Cassi | Power F 400 > Durability F 600 > Bruiser H | 4.0 (40%) |
| Issac | Treasure S 365 > Power S 520 > Home H 745 > Durability H > Power S | 5.9 (33%) |

Camp aggro: the priority word is minus the health quartile, so the healthiest adjacent champion soaks (engine-mechanics.md).
Copied as kFishNow / kFishBuild / kFishRecall (tools/edits/edit_fishcopy.py, bots/B413x).

## Update Oct 31 (engine 2.0.0, 12 top teams, ranked Oct 29-30): see `top-builds-1031.md`

Supersedes the Oct 27 build tables above. In short (599 match summaries, 9,940 listed matches, 66 traced replays):
- Vesper ends 64-96% Strength (Bruiser S stack; prism 21.7 a game); Vendetta opens Treasure H > Jungle S > Bruiser H > Durability H, then
  Bruiser S (prism / Fish / Claudus); HoR never Strength (Treasure H > Jungle F > Bruiser H); Marcella has no consensus but 6 of 12 teams take
  Durability Health in 76-96% of games (ours 17%).
- 3 picks: the Vendetta + Vesper + HoR trio is the most-drafted set and -11 wins per 100 below team strength; Ryth / Tavi sets +19.
- Vendetta's reset: in fight turns where she hits a champion with the reset ready the top teams double 83%, ours 56-65% ("hit, then step");
  after a kill they spend the refreshed reset 64% of the time when a target is in reach, ours ~1%.
