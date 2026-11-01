# Recall cycles, pre-started recalls and "clockwork" farming (Oct 31 study, engine 2.0.0)

Eric (Oct 31 ~02:00 UTC, grant #13): Fish's farming "works like clockwork with the recalls and group being perfectly timed while also
accounting for each champion's build"; should champions split off and rejoin the main group when the recall and farming paths cross;
and can we copy the top teams' pre-started recall? Everything below is measured from replays; guesses are marked.

## Data and tools

- **Games:** 203 ranked games, 406 team-games: 36 of Fish's Oct 30 16:00 version (`replays/fishnew1031`, label FishB: 12 close /
  12 contest / 12 farm), the 140 top-13 games of `replays/top1031` (Oct 29-30; Fish there is mostly its older version, FishA), and 27
  of ours (`replays/us1031`, #45x, vs mid-ladder teams, 9 per class). Map classes by spawn walk: close <= 30, contest 31-60, farm > 60
  (top-teams-grouping-1031.md).
- **Tools (`tools/stress/`):** `rcsel.py` (selection), `rccycle.py` (per-game recall / trip / group-cycle / capture events, JSONL),
  `capkinds.py` / `capstate.py` (captures by camp kind / capturer state), `campyield.py` (camp damage and yield), `rcoutbound.py`
  (home -> first camp), `rcdepart.py` / `rcwhy.py` (departures / recall causes from a logging build),
  `rcsum.py` (tables; `results/rc1031/tables.md` holds the full output), `timeuse.py` (where champion-rounds go), `rcwalks.py` (map
  classes). Local diagnosis: `bots/D458` = #458 printing a `TT` line every round (`kTargetLog` every round + `kLogActivity`), 30 games
  vs PoolLive on 10 contest + 5 farm maps in `results/act1031d` (traces + stdout).
- **Definitions:** a *genuine recall* starts 3+ steps from home and ends within 1 step of a start tile; a *pre-start* is a recall
  started at a turn end and cancelled at the next turn start (`c1`); *main group* / *away* / *split episode* as in
  top-teams-grouping-1031.md (link radius 6, away = 8+ tiles from every main member, an episode = 20+ away rounds).

## 1. Pre-started recalls

| team | pre-start share of active rounds | genuine recalls that were kept pre-starts | acted in the recall's start round |
|---|---|---|---|
| Fish (Oct 30) | 91% | 85% | 64% |
| Mite | 88% | 94% | 41% |
| print dont int | 90% | 91% | 60% |
| Ad Astra | 74% | 68% | 52% |
| prism best girl | 1% | 1% | 20% |
| NEETCoders | 1% | 0% | 0% |
| us (#45x) | 1% | 0% | 0% |

- Four top teams start a recall at every turn end; the kept ones save one round per trip (the trip counts the start turn).
  **Two of the top five (prism best girl, NEETCoders) never do**, so it is not what separates the top from us.
- Ours: `kEarlyRecall` (edit_earlyrecall.py) starts next turn's retreat recall at this turn's end - the same saving on every trip we
  can predict, without a blanket pre-start (91 `can_move` / `can_attack` / `can_cast` reads and 30 `is_recalling()` readers in our
  decision code would misread a pre-start). Screened **+4 +-11** (2,240 games): neutral, ride-along.

## 2. Recall timing and synchronisation: we are already more synchronised than the top teams

| team | genuine recalls / champion / 1000 alive rounds | health at recall (median) | a mate's recall within 2 rounds | group recalls (2+ within 5 rounds) per game | champions per group recall | share of recalls inside a group recall |
|---|---|---|---|---|---|---|
| Fish (Oct 30) | 8.7 | 0.53 | 28% | 5.9 | 2.3 | 34% |
| Mite | 11.5 | 0.71 | 30% | 6.5 | 2.3 | 30% |
| Ad Astra | 13.4 | 0.87 | 37% | 8.5 | 2.4 | 41% |
| prism best girl | 8.8 | 0.40 | 20% | 3.4 | 2.2 | 21% |
| NEETCoders | 9.6 | 0.65 | 21% | 2.6 | 2.2 | 17% |
| us | 9.0 | 0.91 | **40%** | 7.0 | **2.7** | **46%** |

- The top teams' cycle is **individual**: a group recall is 2.2-2.4 champions every 58-122 rounds (median period), and only 17-41% of
  their recalls are in one. Ours bring 2.7 home together and 46% of our recalls are joint (kRecallSync 8 + kSyncFar 30, live).
- Our full-health recalls are mostly travel, not wasted shopping (local D458 logs, 1,438 recalls, 770 of them at 90%+ health):
  at 90%+ health 40% are `recall_hop` (kRecallHop 3: recall + walk from home beats the walk from here), 35% `recall_capture`, 16%
  retreats (shop trips), 7% `sync_recall`. Below 50% health 75% are retreats and 13% `loop_recall`.

## 3. Where the time goes (share of champion-rounds, alive or dead)

| team | camp (dealt camp damage / earned) | walk out (left home, no camp hit yet) | walk between camps | walk back | enemy within 4 | recall channel | home | dead |
|---|---|---|---|---|---|---|---|---|
| Fish (Oct 30) | 19% | 21% | 25% | 6% | 9% | 4% | 7% | 9% |
| top-13 (Oct 29-30, 150 team-games) | 15-19% | 21-27% | 19-24% | 5-8% | 8-12% | 4-7% | 3-5% | 9-15% |
| us | 16% | **28%** | 22% | 7% | 9% | 4% | 4% | 9% |

- Our extra time is the **walk out**: on contest maps 30% (Fish 19%). From home to the first camp hit: contest median 19 rounds
  (Fish 12), first camp 18.5 steps away (Fish 16), p75 waste 8 rounds over the walk (Fish -1).
- Cause (D458 logs, 1,337 departures): **84% of our departures (87% on contest maps) head for a camp a teammate holds** (the
  squad's camp: whole-team squads on 48 of 70 maps). Contest maps: those take 21 rounds to the first hit (walk 21), solo departures 10
  (walk 13); the squad has moved on in half of them (first hit != departure target 48%).

## 4. What "clockwork" is in the data: light camps taken away from the main group

Captures before round 1000, per team-game (nominal gems: wolf 4, elk 15, gem cluster 7, golem 36, monolith 200):

| team | elk camps | cluster-only groups with gem clusters | gold-cluster-only groups | wolf camps (+ clusters) | golem / monolith | nominal gems from cluster-only groups | nominal gems / game |
|---|---|---|---|---|---|---|---|
| Fish (Oct 30) | 9.6 | 8.2 | 7.8 | 9.7 | 1.3 | 217 | 808 |
| us | 9.1 | 4.7 | 4.3 | 6.3 | 0.9 | 51 | 512 |

- **Elk camps: equal. Light camps: Fish 25.7 a game, us 15.3.** Clusters alone are ~70% of Fish's nominal-gem lead (217 vs 51 from
  cluster-only groups, 107 vs 64 from wolf+cluster groups).
- **Who takes them:** of Fish's light-camp captures 34% (gem clusters), 43% (gold clusters), 31% (wolves) are by a champion *away*
  from its main group; ours 6% / 25% / 16%. Fish's elk camps stay main-group work (75%, ours 78%).
- Split episodes: Fish's away champion hits 1 camp per episode (ours 0: our "episodes" are mostly a champion walking back to a far
  squad); 63% end by rejoining. On farm maps the top teams' splitter camps 16 steps from home while the main group is at 40 (Fish 11
  vs 42).
- A split ends with the group, not on a timer: 39% of rejoins happen because the group moved towards the splitter, 26% while the group
  walks homeward. Group recalls are not what brings them together (a main member recalls within 2 rounds of a splitter's recall: 13%).

## 5. Per-damage yield and power (r < 1000, per champion)

| team | camp rounds | damage / camp round | camp damage | gems | gold | gems / 1k camp damage |
|---|---|---|---|---|---|---|
| Fish (Oct 30) | 154 | 107 | 16,493 | 200 | 1,018 | **12.1** |
| Mite | 178 | 130 | 23,221 | 215 | 1,314 | 9.2 |
| Ad Astra | 145 | 128 | 18,546 | 171 | 1,192 | 9.2 |
| NEETCoders | 159 | 121 | 19,179 | 164 | 1,126 | 8.5 |
| prism best girl | 167 | 117 | 19,431 | 169 | 1,022 | 8.7 |
| us | 161 | 97 | 15,577 | 138 | 944 | 8.9 |

- Against Mite / Ad Astra / NEET / prism the gap is **damage output** (+21-34% per camp round, +19-49% camp damage); their gem yield
  per damage is ours. Against Fish it is **yield**: the same damage buys 36% more gems (the cluster loop above).
- By type (damage per camp round): Fish's Marcella 207 (ours 130), Vendetta 167, Vesper 179 (ours 106); other top Vespers 152.

## 6. What we tried with it (switches, all off unless stated)

- `kEarlyRecall` (edit_earlyrecall.py): the pre-started-recall saving on predicted trips. +4 +-11 locally.
- `kClockSat` / `kClockMeet` / `kClockDetour` / `kClockTtk` / `kClockKinds` (edit_clockwork.py, B535x): timed light-camp splits on
  whole-team squads - a member the squad's camp does not need takes a light camp it can clear, capture and walk back from before the
  squad is done there; a member walking back to a far squad camp takes light camps on that walk. Results in bot-status.md (s_clock).
- Earlier attempts at the same idea, all local: kPartyShare 2 satellites -21, kRejoinFarm -60 / -95, kClusterOne -43 (ladder -4.4k),
  cluster solo -37, kHomeFarm -32.

## 7. Throughput root causes (Oct 31 morning; same replays, 5-pick games unless stated)

| team | captures by r600 | elk by r600 | groups hit per 10 rounds | champions per elk clear | per wolf+cluster | per cluster group | time within 3 of an ally | time 13+ from any ally (share of it hitting camps) | still beside a capture (champion-rounds per capture) |
|---|---|---|---|---|---|---|---|---|---|
| us | 20.2 | 5.4 | **0.84** | 4.0 | 3.2 | 1.9 | **68%** | 8.6% (9.5%) | 3.9 |
| Fish | 29.5 | 7.6 | 1.37 | 4.1 | 2.8 | 1.5 | 61% | 9.3% (15%) | 0.9 |
| Mite | 31.1 | 10.6 | 1.49 | 2.6 | 1.8 | 1.4 | 47% | 15.3% (24.5%) | 0.9 |
| Ad Astra | 26.1 | 4.8 | 1.20 | 3.3 | 2.3 | 1.3 | 47% | 19.1% (18%) | 0.9 |
| NEETCoders | 26.8 | 7.5 | 1.42 | 3.0 | 2.1 | 1.1 | 40% | 18.0% (22%) | 0.4 |

- Clear times are equal (elk 24-26 rounds first hit to capture): our extra fighters add nothing; the top teams work ~1.4 groups at once.
- **Isolation is not deadly for them:** deaths to enemies per 1,000 isolated (13+) champion-rounds: ours 1.37, Fish 2.76, Mite 1.59, Ad Astra
  1.52, NEET 1.92 - the same as grouped play (1.3-2.1). Their isolated champions farm; ours walk.
- **Camp damage per hit:** Vesper per auto ours 94 vs 138-161 (same autos per round): her gold earned by r400 is 368 vs 720-1,035; team gold
  at r600 ours 2,198 vs 3,043-4,405 (captures 1,256 vs 1,779-3,224). Marcella casts on camps 14 per 100 camp rounds vs 21-26.
- **Still beside a capture** (D458 logs, results/act1031d): 30% `guard` (a mate holds the reward: known_ = respawning, the member guards
  it), 31% `fight_camp`, 11% `fight_enemy` - ~0.4-0.7% of our champion time; small.
- Tools (tools/stress): damsplit.py (autos vs casts), openuse.py (opening time use), partysize.py (credited champions, gold share),
  clears.py (fighters per clear, groups hit per 10 rounds), isodeath.py (isolation time and deaths), capstill.py (still beside a capture),
  capwait.py (D458 activities beside a capture), goldsrc.py (gold by source). The rc1031 ones read results/rc1031/*.jsonl; env TEAMS,
  END, PICKS.
- **Camp spells held near enemies (tools/stress/castgap.py; camp rounds r < 1000 with the slot off cooldown, enemy champion within 8 -
  cast / held):** Marcella's 2x Focus spell ours 79 / 383, Fish 260 / 24, Ad Astra 165 / 4; Ryth's area stun ours 156 / 196, Ad Astra
  261 / 7, NEET 46 / 3; HoR slot 1 ours 109 / 119, Fish 322 / 21. With no enemy near, Marcella's spell ours 429 / 241 (Fish 726 / 28): she
  steps and hits instead (melee; the spell excludes walking). kSaveSpells 8 is the hold; the top teams do not hold. Local screens of
  kSaveSpells 4 / 0 (-32 / -64) were against our own clones only; edit_marccast.py (B554, kMarcSaveNear) + kMeleeOpen screen s_marc.
