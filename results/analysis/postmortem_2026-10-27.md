# Postmortem: massacres and the damage gap (2026-10-27)

Data: `cw1` (= `bots/main`) on the four pinned panels bvp, bhp, b11p and b12p, 150 decoded platform games, both
sides, to round 1000 unless stated. "Us" is cw1, "them" is the opponent in the same game. Readers (all in
`tools/replay/`): `deathfactors.py` (massacre factors), `packresp.py`, `contact.py`, `damage.py`, `lostbag.py`,
`trace.py`, and `decoded.py captures|assist`. Outputs of this run: `data/massacre_cw1.txt`, `data/massacre_cw1_r300.txt`,
`data/damage_cw1.txt`, `data/assist_cw1.txt`.

## 1. Where the games are lost

- **Captures are equal.** 43.0 group captures per game against 43.5, worth 571 gems against 576 (`decoded.py captures`).
  The gap in gems collected (635 against 750) comes from bags: a killer takes the whole bag, we lose 92 gems per game on
  death and they lose 38.
- **Massacres hold the losses.** Split by our deaths minus theirs by r1000:

  | Class | Games | Wins | Death difference r300 / r600 | Team gold r300 (us / them) | Team gold r600 |
  |---|---|---|---|---|---|
  | massacre (6+) | 40 | 1 | +3.5 / +6.7 | 705 / 1483 | 1646 / 3643 |
  | mixed (3-5) | 16 | 2 | +1.5 / +2.4 | 904 / 1460 | 2548 / 3330 |
  | even (2 or less) | 94 | 57 | -0.6 / -1.7 | 1287 / 1038 | 2973 / 2266 |

  In even games we win 61% and kill more than we lose (3.6 deaths per game against their 6.3). In massacre games we die
  12.7 times per game against 2.1 and lose 140 gems on death against 18.
- **Massacres are concentrated.** 4-pick maps: 18 of 53 games are massacres (5-pick 21 of 86, 3-pick 1 of 11). By map:
  01concentrated_wealth 6 of 12, 00gemfight 6 of 12, 02stalactites 4 of 11, 00stampede 4 of 11, 01fracture 3 of 11,
  00swirl 2 of 2, 01shortcut 2 of 11, 00vault 2 of 10.
- **The snowball starts early.** In massacre games we die 1.9 times per game by r150 and 4.2 by r300 (they 0.7). By
  r300 their team gold is 2.1 times ours; by r600, 2.2 times. Later deaths (60% of massacre deaths fall after r300) are
  then fights against champions with twice our items.

## 2. Massacre factors

Shares are of our deaths in massacre games, with even games in brackets (`deathfactors.py`; the early column uses
`UPTO=300`).

| # | Factor | Massacre (even) | Early, by r300 |
|---|---|---|---|
| M1 | The enemy fights as a big group: 3+ enemies within 6 at some point of the fatal contact | 68% (54%) | 78%, 4+ in 53% |
| M2 | Several killers (3+ enemy champions hit the victim in its last 10 rounds) | 36% (33%) | 58% (43%) |
| M3 | Outnumbered by 2+ at the first enemy hit | 20% (13%) | 25% (17%) |
| M4 | Chain death: a teammate died within 8 tiles and 60 rounds before | 43% (20%) | 46% (24%) |
| M5 | Walking out from home in the 5 rounds before the contact | 35% (25%) | 36% (28%) |
| M6 | Death in our own half / within 10 tiles of our spawn | 49% / 28% (39% / 21%) | 41% / 28% |
| M7 | At 80%+ health when the fatal contact started | 73% (61%) | 75% (60%) |
| M8 | Saw one of the killers 11-30 rounds before dying | 75% (75%) | 75% (75%) |
| M9 | No ground gained towards home during the contact | 63% (61%) | 68% (64%) |
| M10 | Bot activity at death (D line): flee / stunned / pvp | 65% / 11% / 7% (56% / 15% / 6%) | 59% / 17% |
| M11 | No ally within 6 at the death | 47% (47%) | 45% (43%) |

Killers in massacre deaths (a death can have several): Marcella 45%, Vesper 36%, Heart of Ruin 29%, Tavi 26%, Willow 18%,
Prism 18%. Victims: Heart of Ruin 26%, Vendetta 26%, Vesper 22%, Marcella 19%, Varg 7%.

**What a massacre death looks like** (`trace.py`, 00stampede, three of our deaths before r300 in one game): all five
enemies (Heart of Ruin, Vesper, Marcella, Ryth, Vendetta) shadow one or two of our champions at 4-6 tiles for 10-20
rounds. Ours are at full health. They keep walking outwards to their target, or stand still 3-4 rounds (most likely holding
a capture or waiting at a group) while the pack closes. Then a stun lands and the champion dies 4-6 rounds after the
first hit. A pack of individually weak enemies creates no danger tiles (each enemy's burst is under 30% of our health), so
for the bot a healthy champion is "not in danger" and keeps working.

**Pack sightings explain the whole death gap** (`packresp.py`: 3+ enemies within 8 that outnumber us, after 5 quiet
rounds). We have 19.4 per game and die within 15 rounds after 15.3% of them, i.e. 2.97 deaths per game. They have 15.0
and 9.5%, 1.42 deaths. The difference, 1.55 per game, equals the total death gap (6.36 against 4.82). Responses over the
next 5 rounds:

| Response | Us: share, P(death) | Them: share, P(death) |
|---|---|---|
| left (2+ tiles farther) | 22.9%, 0.033 | 27.9%, 0.018 |
| fought (hit champions 2+ rounds) | 17.5%, 0.293 | 20.7%, 0.178 |
| closed in (2+ tiles nearer, no fight) | 17.0%, 0.221 | 12.5%, 0.146 |
| stood still (capture, gather, waiting) | 14.4%, 0.07-0.10 | 10.4%, 0.00-0.10 |
| farmed | 3.7%, 0.165 | 1.8%, 0.025 |
| other | 24.6%, 0.154 | 26.7%, 0.104 |

With their response mix and our death rates we would still die after 15.1% of sightings. So the response mix is not the
gap. We die more for every response, which points to how our fights go (section 3) and how often we meet packs (19.4
against 15.0).

**Contacts by numbers** (`contact.py`: an enemy within 4 after 10 quiet rounds; numbers = allies within 6 including the
champion minus enemies within 6):

| Numbers, health | Us: per game, P(death 15), P(kill 15), hit share | Them |
|---|---|---|
| +1, 80%+ | 10.8, 0.046, 0.176, 0.19 | 17.2, 0.043, 0.308, 0.28 |
| even, 80%+ | 8.3, 0.081, 0.109, 0.23 | 7.8, 0.049, 0.143, 0.29 |
| -1, 80%+ | 3.0, 0.168, 0.130, 0.23 | 1.8, 0.056, 0.192, 0.27 |
| -2 or worse, 80%+ | 1.3, 0.304, 0.108, 0.21 | 0.4, 0.113, 0.226, 0.27 |

When we have the numbers we die as rarely as they do but kill 43% less. When numbers are even or worse we die 1.7 to 3
times as often.

**Bags do not make our champions careful** (`lostbag.py`): deaths per 1000 alive rounds with 0 / 1-19 / 20-49 / 50-99 /
100+ gems: us 1.78 / 1.63 / 1.54 / 1.74 / 2.38, them 1.43 / 0.96 / 0.84 / 0.88 / 0.33. Rounds spent carrying are equal
(e.g. 618 against 609 per game at 20-49), so the bag gap is the death rate, not the exposure.

## 3. Damage factors

They deal about 17.1k champion damage per game and we about 13.1k (target health lost, split among the round's hitters;
`damage.py`, weighted by champion-games). Damage = contact rounds (an enemy champion within reach+1) x hit share x damage
per hit round.

| # | Champion | Damage per champion-game | Contact rounds | Hit share | Damage per hit round (main-stat shards) | On champions dying within 10 |
|---|---|---|---|---|---|---|
| D1 | Vesper | 3050 vs 4907 | 96.6 vs 91.5 | **0.29 vs 0.43** | 108 vs 119 (**9.0 vs 14.6**) | 24% vs 32% |
| D2 | Marcella | 4024 vs 5228 | **25.7 vs 36.8** | 0.65 vs 0.69 | 162 vs 147 (8.3 vs 7.4) | 24% vs 31% |
| D3 | Vendetta | 2661 vs 3028 | 35.0 vs 35.6 | 0.60 vs 0.68 | 111 vs 114 (5.6 vs 6.7) | 24% vs 36% |
| D4 | Heart of Ruin | 2803 vs 2819 | 45.8 vs 53.4 | 0.62 vs 0.71 | 89 vs 69 (6.5 vs 7.0) | 22% vs 33% |
| D5 | Fifth pick | our Varg 1496 | | | | 14% |

Their fifth picks deal more: Ryth 1997, Willow 2237, Tavi 5571, Prism 6074, Cassi + Issac 3309.

- **D1 Vesper wastes contact rounds.** In her contact rounds without a hit she moved with an enemy in reach 23% (theirs
  16%), did nothing with an enemy in reach 8% (4%), and cast without hitting a champion 8% (4%). A ranged champion that
  moves cannot shoot. Her hit share is lower in every state: outnumbering 0.31 vs 0.45, even 0.30 vs 0.43, outnumbered
  0.25 vs 0.35. She is also poorer: 9.0 strength shards while hitting against 14.6 (camp gold by r600 658 against 878,
  kill gold 54 against 122, `decoded.py champs`).
- **D2 Marcella fights less and in worse numbers.** 36% of her contact rounds are outnumbered (theirs 16%).
- **D6 Our damage does not finish targets.** 22-24% of our champion damage lands on champions that die within 10 rounds,
  31-36% of theirs. Damage that does not kill is healed at their spawn.
- **D7 We join fights less.** A healthy champion whose teammate within 6 is hit (`decoded.py assist`): with the enemy 3-4
  tiles away we hit in 17% of rounds (they 30%), stand still 26.5% (18.5%), keep hitting camps 8.3% (3.8%). With the
  numbers on our side they join 10.0 times per game, we 4.8; after their joins 0.53 enemies die within 10 rounds, after
  ours 0.32.
- **D8 Why we do not engage when ahead.** Local probe np0 (40 games against cand1 and cp3): in rounds with an enemy within
  4, our side outnumbering within 6 and health 80%+, we engage in 73%; the fight simulation says "not winning" in 21%
  and the carrier rule blocks 6%. The simulation plays 3 rounds with the enemy first and calls a fight won only on more
  enemy deaths, or on equal deaths with our remaining health fraction 0.2 above theirs. Sides 3-5 tiles apart barely
  meet in 3 rounds, so the margin is rarely reached.

## 4. Already tried, by factor (rows in `docs/experiments.md`)

- Leaving or avoiding packs (M1, M3, M9): ob1, kb1, ro1, pa1, kz1, kz2, dm1. None cut deaths; pa1 and kb1 cost 4-8% of
  gems. kb1 widened danger radii, but packs below the burst filter have no danger tiles to widen.
- Staying together (M11): du1 (pairs) raised deaths 0.5 per game; os1 (opening stack) rejected locally.
- Vesper shooting more (D1): vh1m raised her hit share 49% to 57% and her deaths 22% (b9, 10-26); vs1 was never gated.
- Fight thresholds (D8): fb1 and fb3 (power threshold 0.9 to 1.2) mixed, fb2 (calibration clamp) rejected, sh1 (horizon
  5, 10-24) rejected on 25 games judged by wins on an old bot; fp3 (engaging on even simulations) -2 wins on b2.
- Fifth pick (D5): dq4 and ry1 (Ryth instead of Varg) rejected; Tavi, Willow and Prism untested.
- Items (D1 stats): mc1, mc2 (Marcella), pr2 (Prospector) rejected.

## 5. Plan, one factor at a time

1. **ja1, joining when ahead (D7, D8, the +1 row of the contact table).** When we outnumber (allies within 5 including
   us against enemies within 6), our power is at least theirs and health is 70%+, a fight the simulation does not show
   us dying in counts as won. Factor metric: P(kill within 15) in contacts at +1 numbers (`contact.py`, 0.171). Guards:
   P(death within 15) at +1 (0.064), total deaths, gems collected and tributed.
2. **Vesper's wasted contact rounds (D1).** A narrower vs1: at high health and outside kill range she shoots instead of
   stepping. Factor metric: her hit share in contact (0.29).
3. **Chain deaths (M4).** Champions walking into the spot where a teammate just died.
4. **Fifth pick (D5).** Tavi or Willow instead of Varg on 5-pick maps.
