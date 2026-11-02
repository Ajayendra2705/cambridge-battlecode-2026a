# Top-team builds, drafts and Vendetta kit use (Oct 31 study, engine 2.0.0)

Eric's questions before the Nov 1 knockout: (a) the top teams' emblem builds for Vesper, Vendetta, Heart of Ruin (HoR) and Marcella now,
especially Bruiser Strength builds and Marcella's Health versions of Treasure / Jungle / Durability; (b) 3-pick drafts and the
Vendetta + Vesper + HoR trio; (c) how they use Vendetta's attack reset and dash ("her extra autos always used") vs ours.

**Data (all ranked, engine 2.0.0, both sides 2.0.0):**
- Drafts: every ranked match of the 12 study teams and us from 2026-10-29 00:00 to 2026-10-30 16:20 UTC - 9,940 matches, 5,805 of them
  between two study teams (`results/tb1031/matches.jsonl`, `tools/stress/tb1031list.py`). Study teams = ladder ranks 1-13 on Oct 30 16:13 UTC
  without policy wonk: prism best girl, Mite, Ad Astra, Intercontinental Fish, newer team, hello, print dont int, Trzy Kwaterki,
  Univardisty of Shingtonwash, Claudus Maximus, NEETCoders, Sponge(Albert and Bob). We never meet them in ranked (0 games).
- Builds: match summaries (`cambc matches summary`, cached in `results/sum`) of 599 matches: from a selection of 842 (per study team and pick
  count the latest 40 top-vs-top games since Oct 30 00:00 UTC, plus our latest 15 per pick count and our 9 Vendetta games;
  `results/tb1031/sumsel_rr.jsonl`), fetched round-robin over the team x pick-count cells and stopped at 599 (16-40 games a cell; the CLI
  rate limit allowed ~15 a minute). Tools `tb1031sum.py`, `tb1031report.py`.
- Vendetta kit: 37 top-vs-top replays from Oct 30 06:00-16:20 UTC with Vendetta on one or both sides (74 top-team Vendetta games; with the
  17 top-team Vendettas met in our panel games below, TOP12 = 91), our 9
  ranked Vendetta games (#415 / #418, Oct 29, vs BattleCats / cheji bt; Vendetta only as a fallback pick) and 20 games of our #426 panel
  (Vendetta draft + kVendFight 103, vs the top 10, Oct 29 12:20 UTC), in `replays/builds1031/`; per-turn traces by `tools/stress/vendtrace.ts`
  (vtrace.json), tables by `tools/stress/vendkit.py`.

Separate data from guesses: everything in tables is measured; lines starting **Guess:** are interpretation.

---

## 1. Drafts by pick count (data)

Drafts are stable per team and pick count, chosen per map by some teams (not by the opponent: both teams may draft the same champion).
Ordered picks, Oct 29-30 (counts, record). Changes during the window are noted.

| Team | 3 picks | 4 picks | 5 picks |
|---|---|---|---|
| prism best girl | Ves>Ven>HoR 116 (60-56) on collision/fragment/packs/gold_rush/arena/the_pack/the_pond; Ves>HoR>Mar 52 (19-33) on anvil/broken_curve/the_farm; Prism>Mar>C&I 25 (25-0) on breadcrumbs/gemcombat1 | Ves>Ven>HoR>C&I 183 (114-69); Prism>Mar>C&I>Willow / >Ven 102 (83-19) | Ves>Ven>HoR>C&I>Mar 225 (157-68); >C&I>Ren 130; >Varg>C&I 102; Prism>Mar>C&I>Ven>Ryth 96 |
| Mite | Ves>HoR>Ven 209 (109-100) | Ves>Ven>HoR>C&I 274 (130-144) | Ves>Ven>HoR>Tavi>Mar 690 (438-252) |
| Ad Astra | HoR>Ves>Ryth 179 (122-57); HoR>Ves>Ven 30 (10-20) on breadcrumbs/gold_rush | HoR>Ves>Ryth>Mar 118 / HoR>Mar>Ves>Ryth 77 (100-95); HoR>Ren>Ves>Ven 83 (53-30) | HoR>Ren>(Mar)>Ves>Ryth(>Mar) 481 (224-257); HoR>Ren>Ves>C&I>Ven 80 (57-23) |
| Intercontinental Fish | Ves>HoR>Mar 195 (54-141); Ves>HoR>Ven 31 (17-14) on breadcrumbs/gold_rush | Ves>Ven>HoR>C&I 252 (170-82) | Ves>Ven>HoR>C&I>Mar 380 (202-178); >C&I>Ren 135; >Varg>C&I 127 (86-41); >C&I>Willow 62 (44-18) |
| newer team | mixed: Ven>Mar>HoR 68, Prism>Mar>HoR 67, Ves>Mar>HoR 36 | mixed Prism/Marcella/Willow lines | mixed (Ves>Prism>Mar>Willow>HoR 96, ...) |
| hello | Mar>Ven>Tavi 196 (119-77) | Tavi>Ven>Mar>Ryth 265 | Ves>Ryth>Ven>Tavi>Mar 735 (337-398) |
| print dont int | Ves>Mar>HoR until Oct 29 12:00; since late Oct 29 C&I>Mar>HoR 92 (47-45) | Ves>HoR>Ven>Mar 192; Prism>HoR>Ven>Mar 84 (50-34) | Ves>HoR>Ven>Ryth>Mar 609 (273-336) |
| Trzy Kwaterki | Mar>Ven>Ryth 121 (57-64) until Oct 30 morning, then Mar>Ves>HoR 78 (36-42) | since Oct 30 Mar>Ves>HoR>Ven | was Mar>Ven>Ryth>Ves>HoR (214-160); since Oct 30 Mar>Ves>HoR>Ven>Ryth |
| Univardisty | experimenting (6+ drafts a pick count) | | |
| Claudus Maximus | Ves>HoR>Ven 135 / Ves>Ven>HoR 66 (84-117) | Ves>HoR>Ven>Tavi / >Ryth | Ves>HoR>Ven>Tavi>Mar 295; Ves>HoR>Ven>Ryth>Mar 256 (152-104) |
| NEETCoders | HoR>Ven>Ves 139 (69-70); HoR>Mar>Ves 64 (43-21) on anvil/breadcrumbs/the_pack/gemcombat1 | HoR>Mar>Ven>Ves 237 (93-144) | HoR>Mar>Ryth>Ven>Ves 689 (356-333) |
| Sponge | Ryth>Ven>Mar 170 (90-80); HoR>Ryth>Mar 38 | Stellar>HoR>Ryth>Mar 166 | HoR>Ryth>Ven>Willow>Mar 560 (278-282) |
| **us** | Mar>Ves>Ryth 181 (85-96) | Mar>Ves>Ryth>Willow 282 (158-124) | HoR>Ves>Ryth>Mar>Willow 736 (357-379) |

Champion share in the study teams' 3-pick drafts: HoR 78%, Vesper 62%, Marcella 60%, Vendetta 56%, Ryth 21%, Tavi 8%, Prism 6%, C&I 5%,
Varg 3%, Ren and Willow 0%. Nobody drafts our 3-pick set (Marcella + Vesper + Ryth); the nearest is Ad Astra's HoR + Vesper + Ryth.

## 2. 3-pick drafts and the Vendetta + Vesper + HoR trio (data)

**Team-strength-adjusted results** (`tb1031draftfit.py`): a Bradley-Terry strength per team from its top-vs-top games at the OTHER pick
counts, then for each 3-pick top-vs-top game the expected win; "diff" = (wins - expected) per 100 games, +- = binomial SE (strength error not
included). 988 top-vs-top 3-pick games:

| 3-pick set | team-games | W-L | diff / 100 | who |
|---|---|---|---|---|
| HoR + Vendetta + Vesper (the trio) | 624 | 288-336 | **-7.4 +- 1.9** | Mite 199, Claudus 122, NEET 116, prism 113 |
| HoR + Marcella + Vesper | 477 | 202-275 | **-10.5 +- 2.2** | Fish 190, print 68, Trzy 63, NEET 54 |
| Marcella + Ryth + Vendetta | 204 | 100-104 | +4.3 +- 3.4 | Sponge 119, Trzy 85 |
| HoR + Ryth + Vesper | 170 | 115-55 | **+18.6 +- 3.8** | Ad Astra 169 |
| Marcella + Tavi + Vendetta | 160 | 97-63 | **+18.7 +- 3.8** | hello 160 |
| C&I + HoR + Marcella | 86 | 42-44 | +1.7 +- 5.3 | print 86 |
| HoR + Marcella + Prism | 80 | 41-39 | +5.3 +- 5.5 | newer 59, print 21 |
| HoR + Marcella + Vendetta | 79 | 42-37 | +8.0 +- 5.5 | newer 63, Univ 16 |
| C&I + Marcella + Prism | 23 | 23-0 | +34.7 +- 9.8 | prism (breadcrumbs, gemcombat1 only) |

- **The trio is the most-drafted 3-pick set (30% of study-team 3-pick drafts; Mite and Claudus always, NEET 68%, prism 60%) and it
  underperforms:** in top-vs-top games where exactly one side has it, the trio side went 183-231 (414 games), **-11.1 +- 2.4 wins per 100**
  below team-strength expectation. Oct 30 games alone: -13.2 +- 3.8 (162 games). Per map (trio side vs non-trio): negative on 9 of 12
  3-pick maps (breadcrumbs -47, the_pond -32, arena -21, the_pack -19, anvil -18, packs -14, gemcombat1 -9, gold_rush -6, fragment -3),
  positive only on broken_curve (+20), the_farm (+2), collision (+2); each map +-8-11.
- The same trio at 4 picks (with C&I, Marcella, Tavi or Ryth): -1.8 +- 1.9 (697 games); at **5 picks +11.4 +- 1.2** (1,730 games) - the trio
  core is the winning 5-pick core and a losing 3-pick one.
- **The strongest 5-pick teams lose ground at 3 picks:** vs their own strength from 4/5 picks, Fish -28.7 +- 3.2 per 100 (Ves>HoR>Mar),
  prism -11.4, Claudus -9.0, Mite -8.5 (trio); hello +18.7 (Mar>Ven>Tavi), Ad Astra +13.8 (HoR>Ves>Ryth), newer +11.0, NEET +7.6, Sponge +6.3.
- Within teams that use two sets (map-confounded - teams pick by map): NEET trio +2.9 vs HoR+Mar+Ves +17.6; Ad Astra HoR+Ryth+Ves +18.9
  vs trio -15.8; prism trio -12.6, HoR+Mar+Ves -29.6, C&I+Mar+Prism +34.7; Fish HoR+Mar+Ves -32.8, trio -2.7.

**How the trio's three dashes are used** (the section 4 replays: 74 / 58 / 64 top Vendetta / Vesper / HoR games plus 17 / 15 / 17 met in our panel; `vendctx.py` with CHAMP 1 / 2 / 12): the top teams' dashes are mostly
travel - 77-81% with no enemy champion within 6 for all three. A hit in the same turn: Vendetta 11% of dashes (9% dash then hit), Vesper
11% (9% dash then shoot), HoR 37% (13% dash then hit, 24% hit then dash - the landing stun after the hit). Ours: Vendetta 0-2%, **Vesper 0% (0
of 1,597 dashes in both samples)**, HoR 28-30% (all dash then hit, never hit then dash).

**Guess:** 3-pick maps are small fight maps; Ryth's area stun or Tavi's stun + Marcella's stun-immune tank win the 3v3 fights that a
dash trio (no stun but HoR's) loses. Vesper is in both the best (HoR+Ryth+Ves) and the worst sets, so it is the third slot that matters:
Ryth > Vendetta > Marcella beside HoR + Vesper.

## 3. Builds (data; `tb1031report.py ... md / builds / marcella / buildwin`, outputs in `results/tb1031/builds_*.txt`)

Sample: 599 summaries (1,144 study-team games of 1,630 selected, 4,812 champion-games; top-vs-top games Oct 30 00:00-16:20 UTC, roughly
16-40 per team and pick count; ours 47 latest + our 9 Vendetta games). Emblem = a completed emblem (the summary's itemCombination events,
in order). "line" = the commonest emblem at each position with its share of all that team's games and its median completion round (a
share under ~50% means the team varies there); "end emblems / game" = emblems held at the game's end (median game 900-1,200 rounds, so
the late stack dominates); "stat at end" = shard equivalents of the final items (an emblem = 5 of its stat, a leftover shard 1). Short
names: Tre Treasure, Jun Jungle, Bru Bruiser, Dur Durability, Pro Prospector, Cap Capture, Hun Hunter, Mon Monster, Pow Power, Hom Home;
-S / -F / -H = Strength / Focus / Health.

### 3.1 Vesper

| team / picks | n | W-L | line: emblem at positions 1-5 (share, median round) | most common first three | emblems by r600 | end emblems / game | stat at end |
|---|---|---|---|---|---|---|---|
| prism | 91 | 54-37 | Tre-S 77% r85 > Jun-S 63% r144 > Pro-S 51% r178 > Bru-S 35% r270 (/Dur-H 24%) > Bru-S 56% r349 (/Dur-H 22%) | Tre-S > Jun-S > Pro-S (46%) | 11.0 | Bru-S 21.7, Tre-S 1.0, Jun-S 0.9, Pro-S 0.8 | S 96% F 0% H 4% |
| Mite | 95 | 56-39 | Jun-S 73% r161 > Bru-H 44% r320 > Mon-S 32% r452 > Dur-H 33% r417 > Cap-S 20% r536 | Jun-S > Bru-H > Mon-S (25%) | 4.5 | Bru-H 2.3, Jun-S 0.8, Mon-S 0.7, Dur-H 0.7 | S 59% F 0% H 41% |
| AdAstra | 98 | 55-43 | Pro-S 41% r68 (/Hun-S 33%) > Cap-S 54% r180 (/Pro-S 22%) > Hun-S 23% r155 (/Jun-S 23%) > Jun-S 38% r322 (/Dur-H 24%) > Dur-H 37% r343 | Pro-S > Cap-S > Hun-S (19%) | 7.8 | Bru-S 8.3, Bru-H 6.3, Cap-S 0.8, Jun-S 0.8 | S 64% F 0% H 36% |
| Fish | 92 | 46-46 | Tre-S 67% r131 > Jun-S 48% r244 > Bru-H 55% r320 > Dur-H 38% r345 (/Bru-S 28%) > Bru-S 43% r392 (/Dur-H 22%) | Tre-S > Jun-S > Bru-H (40%) | 6.5 | Bru-S 10.7, Bru-H 1.7, Tre-S 0.9, Jun-S 0.8 | S 84% F 0% H 16% |
| newer | 32 | 17-15 | Pro-S 75% r117 > Jun-S 16% r454 > Tre-S 22% r352 > Jun-S 25% r351 > Jun-S 16% r591 | Pro-S (16%) | 3.6 | Bru-S 3.2, Pro-S 0.8, Jun-S 0.7, Pow-S 0.6 | S 79% F 0% H 21% |
| hello | 27 | 10-17 | Tre-S 44% r159 (/Dur-H 37%) > Mon-S 26% r292 > Pow-S 33% r583 (/Pro-S 22%) > Pow-S 19% r521 > Jun-H 15% r695 | Tre-S > Mon-S > Pro-S (11%) | 4.6 | Bru-S 2.3, Bru-H 0.9, Dur-H 0.9, Pow-S 0.8 | S 68% F 0% H 32% |
| print | 34 | 19-15 | Tre-S 88% r135 > Pow-S 53% r327 (/Dur-H 32%) > Dur-H 62% r389 (/Pow-S 29%) > Pro-S 47% r388 (/Mon-S 32%) > Jun-H 38% r539 (/Mon-S 35%) | Tre-S > Pow-S > Dur-H (53%) | 7.4 | Bru-S 4.8, Bru-H 1.5, Tre-S 1.0, Pow-S 1.0 | S 77% F 0% H 23% |
| Trzy | 83 | 39-44 | Pro-S 57% r95 > Tre-S 48% r140 > Jun-S 31% r232 > Jun-S 12% r209 > Mon-S 16% r340 | Pro-S > Tre-S > Jun-S (24%) | 8.4 | Bru-S 5.1, Bru-H 3.4, Pow-S 2.3, Pro-S 1.2 | S 72% F 1% H 28% |
| Univ | 36 | 18-18 | Pow-S 92% r213 > Pow-S 83% r398 > Pow-S 75% r438 > Pow-S 67% r415 > Pow-S 50% r493 | Pow-S > Pow-S > Pow-S (75%) | 3.7 | Pow-S 4.6, Bru-H 4.1 | S 52% F 0% H 48% |
| Claudus | 85 | 36-49 | Tre-S 76% r127 > Jun-S 66% r211 > Pow-S 31% r301 (/Mon-S 29%) > Dur-H 46% r365 > Bru-S 47% r399 | Tre-S > Jun-S > Pow-S (28%) | 6.4 | Bru-S 7.7, Bru-H 3.9, Tre-S 0.8, Jun-S 0.7 | S 68% F 0% H 32% |
| NEET | 83 | 28-55 | Pro-S 52% r114 > Tre-S 36% r156 > Tre-S 13% r237 > Hom-S 13% r270 > Hom-S 14% r379 | (none) (8%) | 7.4 | Bru-S 7.3, Bru-H 2.1, Pro-S 0.8, Tre-S 0.7 | S 74% F 0% H 26% |
| Sponge | 5 | 2-3 | Jun-S 100% r276 > Tre-S 100% r450 > Pow-S 80% r411 > Pow-S 80% r648 > Pow-S 80% r823 | Jun-S > Tre-S > Pow-S (80%) | 3.2 | Pow-S 4.8, Tre-S 1.0, Jun-S 1.0 | S 100% F 0% H 0% |
| us | 54 | 30-24 | Tre-S 81% r265 > Pro-S 41% r282 (/Jun-S 31%) > Jun-S 39% r352 > Dur-H 44% r519 > Bru-S 56% r575 | Tre-S > Pro-S > Jun-S (39%) | 3.3 | Bru-S 7.4, Tre-S 0.8, Jun-S 0.7, Dur-H 0.6 | S 93% F 0% H 7% |
| all top, 3 picks | 239 | 116-123 | Tre-S 35% r84 (/Pro-S 28%) > Jun-S 30% r193 > Jun-S 15% r175 > Dur-H 29% r321 > Bru-S 25% r372 | (none) (10%) | 8.6 | Bru-S 12.7, Bru-H 4.0, Jun-S 0.8, Dur-H 0.7 | S 77% F 0% H 23% |
| all top, 4 picks | 244 | 123-121 | Tre-S 32% r129 > Jun-S 22% r185 > Pow-S 12% r333 > Dur-H 20% r362 > Bru-S 17% r409 | (none) (13%) | 5.7 | Bru-S 5.6, Bru-H 2.0, Pow-S 0.9, Jun-S 0.6 | S 76% F 0% H 24% |
| all top, 5 picks | 278 | 141-137 | Tre-S 38% r125 > Jun-S 24% r209 > Pow-S 13% r352 > Dur-H 17% r427 > Bru-S 14% r415 | Tre-S > Jun-S > Pro-S (5%) | 6.6 | Bru-S 5.1, Bru-H 2.1, Pow-S 0.9, Tre-S 0.7 | S 74% F 0% H 26% |

### 3.2 Vendetta

| team / picks | n | W-L | line: emblem at positions 1-5 (share, median round) | most common first three | emblems by r600 | end emblems / game | stat at end |
|---|---|---|---|---|---|---|---|
| prism | 97 | 61-36 | Tre-H 73% r191 > Jun-S 53% r314 > Bru-H 59% r420 > Dur-H 53% r489 > Bru-S 49% r599 | Tre-H > Jun-S > Bru-H (49%) | 4.4 | Bru-S 5.3, Pow-S 1.3, Tre-H 0.8, Jun-S 0.8 | S 76% F 0% H 24% |
| Mite | 94 | 55-39 | Jun-S 85% r203 > Bru-H 57% r387 > Mon-S 48% r444 > Dur-H 35% r539 > Cap-S 27% r532 | Jun-S > Bru-H > Mon-S (45%) | 4.2 | Bru-H 2.6, Jun-S 0.9, Mon-S 0.8, Bru-S 0.6 | S 59% F 0% H 41% |
| AdAstra | 18 | 11-7 | Jun-S 83% r282 > Pro-S 61% r515 > Dur-H 39% r691 > Mon-S 22% r605 > Bru-H 17% r733 | Jun-S > Pro-S > Dur-H (39%) | 1.7 | Jun-S 0.8, Pro-S 0.6, Dur-H 0.5, Bru-S 0.5 | S 72% F 0% H 28% |
| Fish | 61 | 36-25 | Tre-H 57% r231 > Jun-S 49% r341 > Bru-H 43% r407 > Dur-H 38% r470 > Bru-S 36% r571 | Tre-H > Jun-S > Bru-H (38%) | 4.2 | Bru-S 4.4, Pow-S 1.7, Tre-H 0.7, Jun-S 0.6 | S 79% F 0% H 21% |
| newer | 34 | 17-17 | Hun-H 76% r183 > Pro-S 68% r291 > Tre-S 35% r417 (/Jun-S 26%) > Mon-S 44% r445 (/Jun-S 26%) > Jun-S 21% r485 | Hun-H > Pro-S > Tre-S (26%) | 5.6 | Bru-S 2.2, Pow-S 1.3, Mon-S 0.9, Jun-S 0.9 | S 72% F 0% H 28% |
| hello | 91 | 46-45 | Pro-S 37% r219 (/Tre-S 21%) > Jun-S 22% r334 > Bru-H 14% r375 > Dur-S 20% r530 > Dur-S 11% r528 | (none) (12%) | 3.8 | Bru-S 2.6, Bru-H 2.4, Pro-S 0.6, Jun-S 0.6 | S 69% F 0% H 31% |
| print | 56 | 29-27 | Tre-S 86% r317 > Dur-H 57% r453 > Pro-S 41% r569 > Mon-S 25% r622 > Jun-H 18% r804 | Tre-S > Dur-H > Pro-S (34%) | 2.3 | Tre-S 0.9, Dur-H 0.7, Jun-H 0.6, Mon-S 0.5 | S 72% F 0% H 28% |
| Trzy | 52 | 23-29 | Jun-H 29% r333 (/Pro-H 27%) > Tre-S 15% r463 > Jun-H 10% r777 > Dur-S 8% r753 > Mon-H 4% r628 | (none) (33%) | 1.0 | Jun-H 0.4, Pro-H 0.3, Dur-S 0.2, Tre-S 0.2 | S 39% F 3% H 58% |
| Univ | 55 | 23-32 | Bru-H 56% r262 (/Pow-S 25%) > Bru-H 76% r418 > Bru-H 65% r542 > Bru-H 62% r641 > Bru-H 44% r700 | Bru-H > Bru-H > Bru-H (47%) | 2.7 | Bru-H 5.6, Pow-S 0.4, Bru-S 0.1, Dur-H 0.1 | S 15% F 0% H 85% |
| Claudus | 85 | 36-49 | Tre-H 82% r205 > Jun-S 75% r345 > Pow-S 34% r363 (/Mon-S 28%) > Dur-H 54% r540 > Bru-S 56% r601 | Tre-H > Jun-S > Pow-S (33%) | 3.5 | Bru-S 3.2, Bru-H 1.4, Tre-H 0.9, Jun-S 0.8 | S 61% F 0% H 39% |
| NEET | 78 | 24-54 | Pro-S 29% r303 (/Pro-H 23%) > Tre-S 24% r476 > Mon-S 9% r642 > Mon-S 9% r655 > Cap-S 8% r938 | (none) (21%) | 1.9 | Bru-S 0.7, Bru-H 0.5, Pro-S 0.5, Tre-S 0.4 | S 60% F 0% H 40% |
| Sponge | 42 | 19-23 | Jun-S 93% r172 > Tre-S 88% r307 > Pow-S 79% r423 > Mon-S 76% r492 > Dur-S 64% r539 | Jun-S > Tre-S > Pow-S (79%) | 4.5 | Pow-H 2.3, Bru-H 1.6, Bru-S 1.3, Pow-S 1.0 | S 59% F 0% H 41% |
| us | 9 | 5-4 | Tre-H 100% r192 > Jun-S 89% r329 > Bru-H 78% r429 > Dur-H 78% r544 > Bru-S 56% r672 | Tre-H > Jun-S > Bru-H (78%) | 3.2 | Bru-S 3.1, Tre-H 1.0, Jun-S 0.9, Dur-H 0.8 | S 62% F 0% H 38% |
| all top, 3 picks | 195 | 92-103 | Jun-S 28% r173 (/Tre-H 25%) > Jun-S 25% r276 (/Bru-H 23%) > Bru-H 24% r374 > Dur-H 28% r485 > Bru-S 22% r530 | Tre-H > Jun-S > Bru-H (11%) | 4.7 | Bru-S 4.2, Bru-H 2.7, Jun-S 0.7, Mon-S 0.4 | S 64% F 0% H 36% |
| all top, 4 picks | 265 | 135-130 | Tre-H 25% r209 > Jun-S 22% r350 > Bru-H 17% r519 > Dur-H 21% r557 > Bru-S 16% r632 | (none) (17%) | 2.6 | Bru-S 1.4, Bru-H 1.2, Pow-S 0.5, Jun-S 0.5 | S 63% F 0% H 37% |
| all top, 5 picks | 303 | 153-150 | Tre-H 23% r231 > Jun-S 23% r353 > Bru-H 16% r509 > Dur-H 16% r506 > Bru-S 14% r583 | (none) (10%) | 3.2 | Bru-S 1.3, Bru-H 1.0, Pow-S 0.6, Jun-S 0.5 | S 64% F 0% H 36% |

### 3.3 Heart of Ruin

| team / picks | n | W-L | line: emblem at positions 1-5 (share, median round) | most common first three | emblems by r600 | end emblems / game | stat at end |
|---|---|---|---|---|---|---|---|
| prism | 91 | 54-37 | Tre-H 69% r333 > Jun-F 60% r535 > Bru-H 55% r649 > Bru-H 53% r730 > Bru-H 37% r819 | Tre-H > Jun-F > Bru-H (46%) | 2.2 | Bru-H 2.6, Tre-H 0.8, Jun-F 0.8, Pow-F 0.6 | S 0% F 29% H 71% |
| Mite | 95 | 56-39 | Jun-F 79% r193 > Bru-H 52% r383 (/Mon-H 23%) > Mon-H 42% r409 > Dur-H 35% r519 (/Bru-F 21%) > Bru-F 38% r596 | Jun-F > Bru-H > Mon-H (37%) | 3.7 | Bru-H 2.7, Bru-F 1.7, Jun-F 0.9, Mon-H 0.7 | S 6% F 41% H 54% |
| AdAstra | 98 | 55-43 | Jun-F 54% r254 (/Hun-F 31%) > Jun-F 30% r337 (/Dur-H 23%) > Pro-F 26% r421 > Dur-H 18% r632 > Mon-F 16% r649 | Hun-F > Jun-F > Pro-F (20%) | 2.4 | Bru-F 1.2, Jun-F 0.8, Dur-H 0.6, Bru-H 0.6 | S 0% F 73% H 27% |
| Fish | 95 | 49-46 | Tre-H 67% r431 > Jun-F 52% r599 > Bru-H 35% r683 > Bru-H 32% r779 > Bru-H 27% r898 | Tre-H > Jun-F > Bru-H (32%) | 1.8 | Bru-H 1.9, Tre-H 0.7, Pow-F 0.7, Jun-F 0.6 | S 0% F 34% H 66% |
| newer | 70 | 31-39 | Hun-F 30% r224 (/Hun-H 20%) > Pro-F 26% r304 > Cap-F 11% r378 > Jun-F 11% r499 > Bru-F 10% r645 | (none) (23%) | 2.3 | Bru-F 1.2, Bru-H 0.5, Pro-F 0.4, Hun-F 0.4 | S 0% F 69% H 31% |
| print | 85 | 44-41 | Tre-F 87% r250 > Pow-F 72% r419 > Hom-H 47% r466 > Dur-H 44% r612 > Pro-F 29% r649 (/Mon-F 21%) | Tre-F > Pow-F > Hom-H (44%) | 2.7 | Tre-F 0.9, Pow-F 0.8, Hom-H 0.7, Bru-F 0.6 | S 0% F 68% H 32% |
| Trzy | 82 | 38-44 | Pro-H 27% r239 > Jun-F 9% r456 > Jun-F 7% r436 > Mon-H 12% r534 > Dur-F 6% r598 | (none) (30%) | 1.4 | Bru-H 0.5, Bru-F 0.5, Pro-H 0.4, Jun-H 0.3 | S 2% F 36% H 61% |
| Univ | 67 | 33-34 | Pow-F 84% r281 > Pow-F 60% r397 > Pow-F 49% r530 (/Bru-H 24%) > Bru-H 33% r709 (/Pow-F 33%) > Pow-F 39% r652 | Pow-F > Pow-F > Pow-F (30%) | 2.6 | Pow-F 4.0, Bru-H 2.1, Bru-S 0.2, Pro-F 0.1 | S 7% F 61% H 32% |
| Claudus | 85 | 36-49 | Tre-H 82% r313 > Jun-F 66% r470 > Dur-H 51% r630 > Bru-F 52% r684 > Bru-F 45% r739 | Tre-H > Jun-F > Dur-H (48%) | 2.0 | Bru-F 2.0, Tre-H 0.8, Jun-F 0.7, Bru-H 0.7 | S 0% F 55% H 45% |
| NEET | 86 | 28-58 | Pro-H 51% r352 > Tre-F 17% r422 > Bru-H 13% r742 > Bru-F 8% r888 > Bru-F 7% r714 | (none) (21%) | 1.6 | Bru-H 0.6, Pro-H 0.5, Bru-F 0.5, Bru-S 0.4 | S 16% F 41% H 43% |
| Sponge | 58 | 25-33 | Jun-F 72% r218 > Tre-H 55% r461 > Bru-H 40% r448 > Bru-F 36% r553 > Mon-F 31% r581 | Jun-F > Tre-H > Bru-H (38%) | 1.9 | Bru-H 0.8, Jun-F 0.7, Bru-F 0.6, Tre-H 0.6 | S 9% F 45% H 46% |
| us | 21 | 10-11 | Tre-H 90% r241 > Jun-F 86% r434 > Bru-F 57% r547 > Bru-H 62% r673 > Bru-F 48% r721 | Tre-H > Jun-F > Bru-F (57%) | 2.2 | Bru-H 1.8, Bru-F 1.7, Tre-H 0.9, Jun-F 0.9 | S 0% F 47% H 53% |
| all top, 3 picks | 295 | 144-151 | Tre-H 30% r332 > Jun-F 29% r475 > Bru-H 19% r656 > Bru-H 16% r818 > Bru-F 14% r665 | (none) (15%) | 2.4 | Bru-H 1.7, Bru-F 1.0, Jun-F 0.5, Tre-H 0.4 | S 5% F 47% H 49% |
| all top, 4 picks | 302 | 145-157 | Jun-F 22% r237 (/Tre-H 21%) > Jun-F 20% r466 > Bru-H 17% r585 > Bru-F 13% r598 > Bru-F 9% r722 | (none) (19%) | 2.0 | Bru-H 1.0, Pow-F 0.6, Bru-F 0.6, Jun-F 0.5 | S 2% F 54% H 44% |
| all top, 5 picks | 316 | 160-156 | Jun-F 25% r245 (/Tre-H 20%) > Jun-F 19% r489 > Bru-H 15% r563 > Bru-F 15% r616 > Bru-H 11% r694 | (none) (11%) | 2.3 | Bru-H 1.0, Bru-F 0.6, Pow-F 0.6, Jun-F 0.5 | S 3% F 52% H 45% |

### 3.4 Marcella

| team / picks | n | W-L | line: emblem at positions 1-5 (share, median round) | most common first three | emblems by r600 | end emblems / game | stat at end |
|---|---|---|---|---|---|---|---|
| prism | 54 | 37-17 | Pro-S 59% r162 (/Dur-F 33%) > Dur-F 46% r243 (/Pro-S 30%) > Jun-H 48% r299 > Jun-H 26% r278 (/Bru-F 24%) > Bru-F 33% r421 | Pro-S > Dur-F > Jun-H (28%) | 5.8 | Bru-H 5.5, Pro-S 0.9, Dur-F 0.9, Jun-H 0.8 | S 18% F 16% H 67% |
| Mite | 32 | 23-9 | Jun-F 78% r225 > Bru-H 44% r504 (/Mon-F 25%) > Mon-F 34% r412 (/Dur-H 22%) > Mon-F 25% r717 (/Bru-H 22%) > Cap-F 34% r634 (/Dur-H 31%) | Jun-F > Bru-H > Mon-F (22%) | 4.7 | Bru-H 2.8, Jun-F 1.0, Mon-F 0.9, Dur-H 0.9 | S 0% F 59% H 41% |
| AdAstra | 52 | 25-27 | Pro-H 58% r190 (/Jun-F 23%) > Cap-F 54% r312 > Hun-F 48% r394 > Jun-F 42% r499 > Dur-F 35% r668 | Pro-H > Cap-F > Hun-F (44%) | 5.4 | Bru-F 4.7, Bru-H 1.1, Jun-F 0.8, Mon-F 0.8 | S 3% F 79% H 18% |
| Fish | 49 | 25-24 | Tre-H 78% r97 > Jun-S 45% r277 (/Bru-H 33%) > Bru-H 59% r323 > Dur-H 49% r416 (/Bru-S 29%) > Bru-S 59% r395 (/Dur-H 22%) | Tre-H > Jun-S > Bru-H (43%) | 9.0 | Bru-S 18.2, Bru-H 1.2, Dur-H 1.0, Tre-H 0.9 | S 83% F 3% H 14% |
| newer | 72 | 34-38 | Pro-H 32% r224 (/Pro-F 26%) > Cap-H 14% r395 > Cap-H 11% r453 > Bru-F 14% r518 > Jun-F 10% r422 | (none) (6%) | 4.6 | Bru-F 2.4, Bru-S 1.6, Bru-H 1.1, Dur-H 0.4 | S 28% F 42% H 30% |
| hello | 92 | 46-46 | Pro-F 41% r225 (/Tre-F 36%) > Tre-F 41% r337 > Jun-F 18% r560 > Mon-F 18% r605 > Dur-H 17% r543 | Pro-F > Tre-F > Jun-F (11%) | 5.3 | Bru-F 3.7, Bru-H 3.0, Tre-F 0.9, Dur-H 0.8 | S 14% F 55% H 31% |
| print | 85 | 44-41 | Tre-F 78% r159 (/Dur-H 20%) > Dur-H 74% r284 > Pro-F 42% r373 (/Mon-F 39%) > Mon-F 27% r413 (/Jun-H 24%) > Jun-H 40% r438 (/Cap-F 22%) | Tre-F > Dur-H > Pro-F (39%) | 6.1 | Bru-F 7.1, Tre-F 1.0, Dur-H 0.9, Mon-F 0.9 | S 0% F 88% H 12% |
| Trzy | 83 | 39-44 | Pro-F 27% r191 (/Tre-H 20%) > Tre-F 14% r285 > Jun-H 13% r277 > Dur-H 12% r511 > Bru-F 13% r564 | Tre-H > Pro-S > Jun-H (5%) | 6.0 | Bru-H 3.7, Bru-F 2.1, Bru-S 1.0, Pro-F 0.7 | S 15% F 36% H 49% |
| Univ | 33 | 18-15 | Bru-H 91% r217 > Bru-H 88% r358 > Bru-H 82% r426 > Bru-H 58% r545 > Bru-H 39% r628 (/Pow-S 21%) | Bru-H > Bru-H > Bru-H (76%) | 3.5 | Bru-H 5.4, Pow-S 2.1, Bru-S 0.3, Dur-H 0.1 | S 35% F 0% H 65% |
| Claudus | 34 | 14-20 | Jun-S 71% r309 > Dur-H 74% r435 > Bru-F 65% r546 > Bru-H 50% r581 > Bru-S 29% r599 | Jun-S > Dur-H > Bru-F (56%) | 2.7 | Bru-S 1.4, Bru-H 1.0, Jun-S 0.9, Dur-H 0.9 | S 47% F 14% H 38% |
| NEET | 60 | 24-36 | Pro-F 68% r216 > Tre-F 28% r279 > Tre-F 22% r354 > Bru-H 17% r505 > Bru-H 22% r691 | Pro-F > Tre-F > Jun-H (8%) | 5.2 | Bru-F 2.5, Bru-H 2.1, Bru-S 0.9, Pro-F 0.8 | S 11% F 53% H 36% |
| Sponge | 70 | 33-37 | Jun-F 97% r141 > Tre-F 90% r224 > Mon-F 81% r313 > Bru-H 79% r381 > Dur-H 77% r435 | Jun-F > Tre-F > Mon-F (81%) | 6.5 | Bru-H 7.1, Bru-S 3.7, Jun-F 1.0, Tre-F 0.9 | S 25% F 23% H 52% |
| us | 54 | 30-24 | Tre-F 63% r202 (/Tre-H 35%) > Pro-F 50% r287 (/Jun-F 28%) > Jun-F 48% r299 (/Bru-F 24%) > Bru-F 69% r419 > Bru-F 69% r472 | Tre-F > Pro-F > Jun-F (44%) | 5.4 | Bru-F 9.1, Bru-S 1.1, Jun-F 0.8, Tre-F 0.6 | S 10% F 85% H 5% |
| all top, 3 picks | 206 | 107-99 | Tre-F 19% r135 > Tre-F 23% r222 > Mon-F 20% r282 (/Bru-H 20%) > Bru-H 17% r387 > Dur-H 20% r395 | Jun-F > Tre-F > Mon-F (12%) | 6.7 | Bru-S 5.0, Bru-H 3.9, Bru-F 3.6, Dur-H 0.6 | S 34% F 35% H 31% |
| all top, 4 picks | 214 | 102-112 | Pro-F 20% r240 > Tre-F 21% r348 > Mon-F 14% r485 > Bru-H 14% r526 > Dur-H 12% r568 | (none) (9%) | 4.1 | Bru-H 2.0, Bru-F 2.0, Bru-S 0.5, Tre-F 0.5 | S 11% F 53% H 36% |
| all top, 5 picks | 296 | 153-143 | Jun-F 21% r155 > Dur-H 20% r337 > Mon-F 15% r342 > Bru-H 21% r492 > Dur-H 13% r516 | Jun-S > Dur-H > Bru-F (6%) | 5.9 | Bru-H 2.6, Bru-F 2.0, Bru-S 1.4, Dur-H 0.6 | S 20% F 44% H 37% |

**Marcella's Health versions** (share of Marcella games that complete the emblem, median round):

| team | n | Tre-F | Tre-H | Jun-F | Jun-H | Jun-S | Dur-F | Dur-H |
|---|---|---|---|---|---|---|---|---|
| prism | 54 | - | - | - | **81% r285** | - | 87% r226 | - |
| Mite | 32 | - | - | 97% r217 | - | - | - | **88% r545** |
| Ad Astra | 52 | - | - | 85% r311 | - | - | 60% r538 | 23% r342 |
| Fish | 49 | - | **92% r116** | 6% | - | 92% r227 | - | **96% r325** |
| newer | 72 | 19% | 25% r534 | 42% r352 | - | 21% | - | 44% r768 |
| hello | 92 | 89% r236 | - | 34% r438 | - | 50% r313 | 1% | **76% r437** |
| print | 85 | 98% r191 | - | - | **80% r465** | - | - | **94% r280** |
| Trzy | 83 | 40% r303 | 40% r175 | 29% r362 | 46% r384 | 11% | 33% r521 | 43% r503 |
| Univardisty | 33 | - | - | - | - | 3% | - | 9% |
| Claudus | 34 | - | - | - | - | 88% r302 | - | **85% r428** |
| NEET | 60 | 55% r284 | 25% r403 | 32% r411 | 30% r371 | - | 7% | 20% r817 |
| Sponge | 70 | 94% r224 | - | 97% r141 | - | - | - | **83% r420** |
| **us** | 54 | 63% r202 | 35% r188 | 76% r303 | - | 17% r180 | - | 17% r415 |
| all 12 pooled | 716 | 43% r225 | 16% r209 | 35% r258 | 23% r386 | 20% r295 | 15% r390 | **57% r419** |

- **Durability Health on Marcella is the norm:** 6 of 12 teams in 76-96% of their games (Fish, print, Mite, Claudus, Sponge, hello), 4 more in
  20-44%; prism takes Durability Focus instead (87%). Ours 17%.
- **Treasure Health:** Fish only as a rule (92%, r116); Trzy 40%, newer / NEET 25%; ours 35% (19 of 54, at every pick count). **Jungle Health:** prism (81%) and
  print (80%); Trzy 46%, NEET 30%; ours never.
- Marcella's end stats vary most of all four champions: Fish 83% Strength (Bruiser S stack, 18 a game), prism 67% Health (Bruiser H),
  print 88% Focus (Bruiser F), AdAstra 79% Focus; pooled 11-34% S / 35-53% F / 31-37% H by pick count. **Ours is 85% Focus (Bruiser F stack).**

**Summary per champion (data):**
- **Vesper - "Bruiser Strength" is the universal late game:** every team ends Strength-heavy (52-100%); prism stacks 21.7 Bruiser S a game
  (96% Strength, 11 emblems by r600), Fish 10.7 (84%), Claudus 7.7. Openers: Treasure S (prism r85, Fish r131, Claudus r127, print r135) or
  Prospector S (Ad Astra r68, Trzy r95, NEET r114, newer r117); Jungle S second; Durability H usually 4th-5th (r345-430); Mite alone goes
  Jungle S > Bruiser H > Monster S (41% Health). 3-pick Vespers are much richer (8.6 emblems by r600 vs 5.7-6.6; 12.7 Bruiser S at the end).
- **Vendetta - Health first, then Strength:** prism / Fish / Claudus: Treasure H (r191-231) > Jungle S (r314-345) > Bruiser H or Power S >
  Durability H (r470-540) > Bruiser S stack (r571-601); end 61-79% Strength. Mite: Jungle S > Bruiser H > Monster S > Durability H (59% S).
  Sponge Jungle S > Treasure S > Power S > Monster S; print Treasure S > Durability H > Prospector S. Univardisty is the only Health stack.
- **HoR - never Strength (0-9% for 11 teams, NEET 16%):** prism / Fish Treasure H > Jungle F > Bruiser H stack (66-71% Health; their HoR is
  poor: 1.8-2.2 emblems by r600, Treasure H only at r333-431); Claudus Treasure H > Jungle F > Durability H > Bruiser F; Mite Jungle F >
  Bruiser H > Monster H > Durability H; print Treasure F > Power F > Home H; Ad Astra / newer Hunter / Jungle / Prospector Focus.
- **"Bruiser Strength" on Vendetta and HoR:** Vendetta yes, but only after 3-4 Health/defence emblems (Bruiser S from ~r570); HoR no.

**Build vs result (within team, so team strength cancels; wins vs the team's own expectation, per 100 games):**

| champion | class (first four emblems' stats, or first two) | games | wins vs expected | per 100 |
|---|---|---|---|---|
| Vesper | 4 Strength | 133 | 81 vs 69.1 | +8.9 |
| Vesper | 1 Health + 3 Strength | 294 | 158 vs 144.3 | +4.7 |
| Vesper | 2 Health + 2 Strength | 98 | 54 vs 49.2 | +4.9 |
| Vesper | late stack (emblems 5+) Strength / mixed / Health | 378 / 106 / 39 | | +8.1 / +9.4 / -0.8 |
| Vendetta | 2 Health + 2 Strength | 173 | 105 vs 85.6 | **+11.2** |
| Vendetta | 3 Health + 1 Strength | 94 | 63 vs 54.7 | +8.8 |
| Vendetta | 1 Health + 3 Strength | 91 | 49 vs 45.4 | +4.0 |
| Vendetta | Treasure H > Jungle S first | 140 | 84 vs 73.9 | +7.2 |
| Vendetta | late stack Strength / mixed / Health | 274 / 79 / 61 | | +11.6 / +17.2 / +1.8 |
| HoR | 2 Focus + 2 Health | 188 | 119 vs 88.7 | **+16.1** |
| HoR | 3 Focus + 1 Health | 113 | 71 vs 59.1 | +10.5 |
| HoR | 1 Focus + 3 Health | 138 | 85 vs 76.4 | +6.2 |
| HoR | Treasure H > Jungle F first | 152 | 84 vs 77.5 | +4.3 |
| HoR | late stack Focus / mixed / Health | 183 / 102 / 89 | | +11.0 / +27.1 / +10.9 |
| Marcella | 3 Focus + 1 Health | 174 | 99 vs 85.7 | +7.6 |
| Marcella | 2 Focus + 2 Health | 90 | 50 vs 46.1 | +4.3 |
| Marcella | late stack mixed / Focus / Health / Strength | 193 / 152 / 106 / 43 | | +9.8 / +10.2 / -1.3 / +10.7 |

Every class that reaches four emblems beats expectation because games with no emblem (low gold) lose (-16 to -44 per 100); only the
differences between rows of one champion carry information, and they are small (SE ~+-4 per 100 at 150 games). A late Health stack is the
weakest late class on Vesper, Vendetta and Marcella (-1 to +2 per 100), not on HoR (+11).


## 4. Vendetta's kit: resets, dashes, autos (data; `vendkit.py`, `vendctx.py` on `vendtrace.ts` traces)

Kit (replay ability props): slot 0 attack reset (no payload, cooldown 8), slot 1 dash (range 2, no landing damage, cooldown 8); a kill
(champion or camp member) resets both cooldowns. A turn = one champion turn alive at its start; "fight turn" = an enemy champion within 2
(Chebyshev) at the turn start; a fight = fight turns no more than 2 rounds apart. TOP12 = 91 top-team Vendetta games (53 won; 74 from the
37 top-vs-top replays of Oct 30, 17 from the opponents in our panel games of Oct 29);
us#426 = 20 panel scrims vs the top 10 (Oct 29, Vendetta draft + kVendFight 103, 1 won); us-rk = 9 ranked games (#415 / #418 vs BattleCats /
cheji bt, 5 won). Our live code since #428 adds kResetMore 2 (melee_free / free_kill follow-up resets) - no Vendetta games of it exist.

| per 100 alive turns | resets | dashes | basic attacks | on champions | on camps | champion kills | camp-member kills | fight turns |
|---|---|---|---|---|---|---|---|---|
| TOP12 (79,959 turns) | 5.8 | 7.7 | 28.4 | 3.3 | 25.0 | 0.2 | 4.8 | 3.5% |
| us#426 (16,289) | 3.8 | 7.0 | 21.4 | 2.8 | 18.3 | 0.0 | 2.0 | 4.6% |
| us-rk (8,064) | 4.7 | 7.2 | 25.6 | 2.3 | 23.2 | 0.1 | 3.1 | 3.1% |

Spread among the 12 teams: resets 4.7-8.3, dashes 4.6-9.0, attacks 25.0-31.9 per 100 turns (prism 6.5 / 7.0 / 30.4, Fish 6.8 / 7.1 / 31.6).

| in fights | fights / game | turns (median) | attacks / fight | resets / fight | dashes / fight | attacks / fight turn | fight turns with 0 / 1 / 2 hits |
|---|---|---|---|---|---|---|---|
| TOP12 | 8.0 | 3 | 3.2 | 0.72 | 0.29 | 0.9 | 33% / 48% / 19% |
| us#426 | 7.8 | 4 | 3.0 | 0.58 | 0.55 | 0.6 | 51% / 37% / 12% |
| us-rk | 6.3 | 4 | 3.3 | 0.60 | 0.40 | 0.8 | 38% / 48% / 14% |

No turn of any Vendetta had 3+ hits (one ability cast a turn, so a reset gives at most one extra hit; a kill refresh matters only on a
turn that has not cast yet).

**Reset discipline.** The reset is ready at the start of 78-81% of alive turns for everyone (it idles; she attacks in only ~9% of them).
- **Fight turns with the reset ready in which she hits an enemy champion: TOP12 doubles (reset + second hit) in 83% (505 of 610); us#426
  56% (88 of 156), us-rk 65% (32 of 49).** The misses are "hit, then step" without the reset: ours 31% of these turns (49 of 156 and 15 of 49), theirs 10% (60 of 610);
  "step, then hit" (no reset) theirs 5%, ours 10% / 2%. Per team the top doubles 77-100% (Claudus 65%, Univardisty 37% are the outliers).
- Fight turns with the reset ready that hit an enemy champion at all: TOP12 60%, us#426 46%, us-rk 52%. Turns with no hit although an enemy
  or camp member stood in reach at the end: 7% / 6% / 8% (no gap).
- **Kill refreshes** (a hit that kills and leaves both cooldowns at 0) on a turn with no cast yet, so reset + hit was possible: TOP12 2,535
  (96% camp members), then another hit 509 (20%), nothing hit although a target stood in reach 286 (11%), nothing in reach 1,740 (69%) - with
  a target in reach they take the extra hit **64%** of the time; **us#426 211: 1 hit after, 58 left in reach (2%); us-rk 153: 0 and 49 (0%)**.
  Our Vendetta never spends a refreshed reset (the "a kill saves the reset" rule in hit(); kResetMore 1 / kKillChain is off).
- All chances for an extra auto (doubles + refreshes used + one-hit turns with a target left in reach + resets with no hit after + refreshes
  left): TOP12 83% taken (4,577 of 5,541), us#426 85%, us-rk 82% - overall equal, because most chances are camp turns where we double as often as they do
  (84-92% of all resets hit a camp member next for both). The gap is in champion fights and after kills.
- Where the resets go: TOP12 11% of resets precede a champion hit, 84% a camp hit; 82% with no enemy champion within 6 (ours 8-14% /
  86-92%; 77-84%).

**Dashes.** TOP12: 89% plain travel or escape (no hit that turn), 9% dash then hit (engage), 2% hit then dash; 79% with no enemy within 6,
18% with one 3-6 away, 3% within 2. **Ours: 100% / 98% no-hit dashes (0 engage dashes in 1,144 #426 dashes)**, 7% / 4% within 2 of an
enemy, and 0.55 / 0.40 dashes per fight vs their 0.29.

**Guess:** our fight code takes the free melee hit and then the escape / reposition step (`melee_free`, `strike_while_escaping`, kVendFight's
exits) without first spending the ready reset - the 31% "hit, then step" turns. kResetMore 2 (live since #428) targets exactly the
melee_free / free_kill hits, so part of this gap may already be closed; it has never been measured on a Vendetta. The kill-refresh gap
(1 of 108 usable refreshes with a target in reach taken, theirs 64%) is not touched by any live switch.

Vesper for comparison (same tools, CHAMP=1): when she hits an enemy champion in a fight turn with the reset ready, ours doubles 100% (#426
59 of 59, ranked 11 of 11) vs TOP12 87% (218 of 252) - the Vesper reset is fine; Vendetta's is not.


## 5. What we should copy

**From data (each item names the measurement; exact emblem sequences in our item names):**

1. **Vendetta's extra autos (only if we draft her).** On a fight turn with the reset ready: hit -> cast the reset -> hit again -> only then
   step or dash (the top teams double 83% of such turns, ours 56-65%; our misses are 31% "hit, then step"). After a kill on a turn with no
   cast yet: cast the reset and hit the next target in reach (top 64% when one is in reach, ours 1 of 108). Both teams take 2 hits at most a
   turn (one cast a turn).
2. **Vendetta's line (if drafted): Treasure Emblem of Health -> Jungle Emblem of Strength -> Bruiser Emblem of Health -> Durability Emblem
   of Health -> Bruiser Emblem of Strength, repeated** (= the existing `kFishBuild` bit 8 line {th, js, bh, dh, bs}; prism completes the five at r191 / r314 / r420 / r489 /
   r599, Fish at r231 / r341 / r407 / r470 / r571). Within teams, Vendetta games whose first four emblems were 2 Health + 2 Strength won
   +11 per 100 over the team's own rate (173 games), 3 Health + 1 Strength +9, 1 Health + 3 Strength +4 (weak evidence, see section 3).
3. **Vesper: Treasure Emblem of Strength -> Jungle Emblem of Strength -> Prospector Emblem of Strength (prism) or Bruiser / Durability
   Emblem of Health (Fish) -> Bruiser Emblem of Strength, repeated**; she ends at
   64-96% Strength in every top team except Mite / Univardisty (Health 41-48%). Our kVespBuild 6 (Treasure S, Jungle S, Durability H,
   Bruiser S) is already this line; the gap is timing (our Treasure S at median r265 vs prism r85, Fish r131) - gold, not the build.
4. **HoR: never Strength** (Strength 0-9% for 11 of 12 teams, NEET 16%). The top line is Treasure Health -> Jungle Focus -> Bruiser
   Health (prism, Fish) or -> Durability Health -> Bruiser Focus (Claudus). Ours (kRuinBuild 4: Treasure H, Jungle F, then Bruiser F / H
   alternating) is the same family; within teams the 2 Focus + 2 Health opening four won +16 per 100 over the team rate (188 games) vs
   3 Health + 1 Focus +6 (138) - our alternating line already gives 2 + 2.
5. **Marcella: add Durability Health.** 6 of 12 teams complete Durability Emblem of Health on Marcella in 76-96% of games, 4 more in
   20-44% (pooled 57%, median r419); ours 17%. Health Treasure: only Fish as a rule (92%, r116), Trzy 40%, newer / NEET 25%; Health Jungle:
   prism (81%) and print (80%). Our Marcella (Bruiser Focus stack, 85% Focus at the end) is closest to print's (88%) and Ad Astra's (79%),
   but both take a Durability emblem (print Durability H 94%, Ad Astra Durability F 60%) and we rarely do (17%). The existing kMarcBuild 9 = Treasure F, Jungle F, Durability H, Bruiser F matches the commonest top shape (print:
   Treasure F -> Durability H; Sponge / Mite: Jungle F ... Durability H).
6. **3 picks: do not switch to the trio.** HoR + Vendetta + Vesper is the most-drafted 3-pick set and the worst performer against team
   strength (-11 per 100 vs non-trio drafts); the sets that beat expectation hold Ryth or Tavi (HoR + Ryth + Vesper +19, Marcella + Tavi +
   Vendetta +19, Marcella + Ryth + Vendetta +4).
7. **Vesper's dash with a shot:** the top Vespers shoot in 11% of the turns they dash (9% dash then shoot); ours never did (0 of 1,597).

**Guesses (not measured):**
- Our 3-pick Marcella + Vesper + Ryth has never met a top team in ranked; it shares Ryth + Vesper with the best set (Ad Astra's HoR + Ryth +
  Vesper). HoR for Marcella (copying Ad Astra) has not been screened; HoR for Ryth at 3 picks lost locally (-47 / -251, MASTER section 8),
  and a local screen cannot judge a draft against the top teams anyway.
- The Vendetta reset gap may already be smaller in the live code (kResetMore 2 since #428 adds a reset after melee_free / free_kill hits);
  a 10-game probe with a Vendetta draft would show it (vendtrace.ts + vendkit.py on the bundles).
- Win rates by build are confounded by gold: every class that reaches 4+ emblems beats its team's average and "no emblem" loses; only the
  comparisons between classes of the same length mean anything, and those differences are 2-16 per 100 on 90-190 games.
