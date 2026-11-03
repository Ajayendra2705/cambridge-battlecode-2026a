# What the top-15 opponents do differently, from their own replay action streams (Opus 5.5 high, 24 Oct 2026)

Method: 54 batch2 replays decoded (`zcat replay.repl26a.gz | node references/scripts/replay_dump.mjs /dev/stdin`): 29 unique matches (every 6th) for rounds 1-200,
plus 25 matches to round 300 (all 9 games on map 6a4203ae = the closest losses, a208aa29, d0596933, d26f859a, 13 spread). Exact damage per attacking round is not
in the data; proxy = monsterDamageDone (summary timeline) / rounds in which the champion made at least one basic attack on a camp tile ("AC rounds").

## Correction to the earlier "damage per attacking round" finding (exps/h1-camp-decomp)
Live, our team damage per alive round is 1.74x lower (11.4 vs 19.8) = share of alive rounds attacking camps 0.170 vs 0.245 (1.44x) x damage per AC round 67 vs 81
(1.20x). So the gap is mostly time not spent attacking, and the per-AC-round gap comes almost entirely from **Heart of Ruin (HoR)**.

| champion | AC share ours / theirs | damage per AC round ours / theirs |
|---|---|---|
| Heart of Ruin | .285 / .221 | **32 / 75** |
| Vesper Vale | .189 / .278 | 58 / 73 |
| Marcella | .146 / .206 | 68 / 83 |
| Ryth | **.137 / .239** | 91 / 94 |
| Vendetta | .209 / .319 | 85 / 86 |
| Tavi | **.067 / .227** | 72 / 75 |
| Willow | .056 / .174 | 54 / 55 |
| Prism | .150 / .221 | 133 / 117 |
| team | .170 / .245 | 67 / 81 |
HoR is ~24% of our AC rounds; lifting 32 to 75 alone moves the team figure from 67 to ~77.

Not causes (equal on both sides): reset use (second attack in 12-23% of AC rounds); focusing the same camp as a teammate (0.86-0.89); ranged champions
attacking from distance 3 (~90%); turn order (mostly Attack, or Cast then Attack); who hits a camp group first (~0.46 for Vesper/Vendetta); allies near at engagement
(1.0-1.6); attacking camps with an enemy within 5 (0.03-0.16); fuel rollovers (228 in rounds 2-300 over 174 matches).

## Their turn logic, reconstructed from actions (not their code)
```
set_priority(role)            // every turn: HoR 100 > Vesper 99/897 > Marcella 98 > Ryth 97 > Vendetta 96
if HoR and shield ready and (hitting a camp this turn or an enemy within 5): shield()
if HoR and dash ready and fighting a camp: dash to the tile within 1 of the most living members; attack
if a living camp is in range: damage spell when ready (gap 8, i.e. on cooldown); attack; reset; attack
elif the camp is dead or an ally is capturing: go to the next group right away (no waiting in range)
if gold >= 150-230: go home and buy a full emblem (first shop round 32-51)
```

## Ranked causes
1. **We idle next to dead or captured camps** (MEASURED symptom). Team attacks camps in 0.208 of alive rounds vs 0.277. Rounds standing inside basic range of a camp
   tile without attacking: melee at distance 1 8.4% vs 2.8%; ranged at distance 3 8.4% vs 0.8%; all champions off the tile within 3: 11.4% vs 4.6%. 35% of our
   capture-reward rounds pay 2+ champions vs 7% of theirs (58/165 vs 19/258); they complete more captures by r300 (258 vs 165). Cause HYPOTHESIS:
   `farm.cpp:farm` case `Known::respawning` calls `wait_near`, parking the champion on attack tiles; `score_group` uses `eta = max(d, wait)` so a near group that
   respawns late scores like a far live group; `V::FILL_IN` defaults to 0.
2. **HoR's dash is spent on travel instead of camps** (MEASURED). Dashes per 100 alive rounds: theirs 10.0 (gap 8, on cooldown) vs ours 4.3; landing within 1 of a camp
   tile 53% (n=574) vs 21% (n=233); dash while already fighting a camp 38% vs almost never; camp attack within 2 rounds after the dash 46% vs 9%. Code:
   `farm.cpp:engage` lines ~603 and ~678 call `try_dash` for travel; with `TH::HOR_DASH = 1`, `nav.cpp:dash_strike` is never used on camps.
3. **HoR's shield is only reactive** (MEASURED). Shield casts per 100 alive rounds: theirs 5.8 (59% while hitting a camp, 32% with an enemy within 5), ours 2.1
   (100% while hitting a camp, 9% with an enemy within 5). shieldingDone 11.9k vs 1.1k. Code: `combat.cpp:maybe_shield` needs `hurt_last_round`, only called from
   `attack_camp`; `strike` never shields. Earlier local tests were mixed (mx1 shield -21 (16), deaths -0.87; as IF add-on -52).
4. **Item tempo for strength champions** (MEASURED). Damage per AC round Vesper 58 vs 73, Marcella 68 vs 83. spentGold at r100: Vesper 0 vs 90, Marcella 0 vs 40; at r200
   Vesper 0 vs 240, Marcella 60 vs 190. First shop round / gold held: theirs Vesper r32 / 226, Marcella r35 / 180, HoR r51 / 150; ours Vesper r82 / 76, Marcella
   r48 / 100, HoR r121 / 95. Code `farm.cpp:shop`, SHOP_TRIP_GOLD 460. Shop-at-120 alone scored -80 (25) on v3e: retest only together with fix 1.
5. **Recall instead of walking home** (HYPOTHESIS). Their champions issue a Recall step in 18% of alive rounds at median HP 0.9-1.0, not at spawn (181 of 5,945), usually
   with 0 gems; their long walks 13.6% of alive rounds vs 18.7% for us. Meaning unresolved.
6. **Turn priority** (HYPOTHESIS, minor). They call `set_priority` every turn and HoR acts first; v3e never does. Their large values (e.g. `10 << 24`) look like messages.

## Specs (all switches default to current v3e behaviour)
**S1 stop waiting at respawning groups.** `variant.h`: `WAIT_SLACK = 100000` (off); existing `FILL_IN` stays 0 by default. `farm.cpp:score_group`, after `wait` is
computed: `if (g.known == Known::respawning && wait - d > V::WAIT_SLACK) return -1;`. `farm.cpp:farm` case `respawning` is covered by `FILL_IN & 4`. First check the
cause: 6 local games with `BOT_DEBUG`, log `g_phase` every round, count rounds in `farm/wait`, the engage help-wait, and `capture` with an ally on the region; if
co-capture is large, move the second capturer on at once (in the `capture()` solo branch, after `skip_until`, choose a new target in the same turn).
Variants: `WAIT_SLACK` in {5, 12}, each with `FILL_IN` 0 and 4. Metrics: share of rounds idle within basic range of a camp (`tools/lab/activity.py`) ~19% to <= 12%;
camp-attack share up; collectedGems@200; monsterDamageDone@200/@400.

**S2 HoR dashes into camp fights.** `variant.h`: `HOR_FIGHT_DASH = 0`. When on and the champion is HoR, skip the two `try_dash` calls in `farm.cpp:engage`
(~603, ~678); the retreat call at `combat.cpp:247` stays. New `nav.cpp:dash_aoe_camp(const Group& g, int ci)`:
```
if (!on || type != HoR || !can_cast || w.moved || dash not ready || !camp_alive(ci)) return false
for each tile t within Chebyshev 2 of w.pos, t != w.pos, walkable(t, w), dist(t, camp[ci]) <= 1:
    hits = number of living members of g within 1 of t
    key  = hits*10 - (danger_tiles().is_set(t) ? 5 : 0) - (|dx| + |dy|)
if best hits >= 1: ab.use(best); update w.pos, w.moved, w.at_spawn and refresh_occ() as dash_strike does
```
Call site: in `engage`, before `if (d <= w.range) {`: `if (V::HOR_FIGHT_DASH) dash_aoe_camp(g, ci);` then recompute `d`; order = dash, `cast_on_camp`, `attack_camp`.
Metrics: dashes per 100 alive rounds 4.3 to ~10; landings within 1 of a camp > 50%; HoR damage per AC round 32 to > 60; monsterDamageDone@200.

**S3 proactive shield.** `variant.h`: `SHIELD_MODE = 0` (0 = current `maybe_shield`). Shield is a self-cast (`ab.use()`). In `combat.cpp:attack_camp` before `me.attack`:
if mode 1, shield ready, and a living group member with str > 0 is within 3, cast. In `combat.cpp:handle_enemies`, before `strike(*best)` and before `retreat(...)`:
if mode 1 and any enemy is within `e.reach + 1`, cast. Test alone and together with S2 (their full HoR kit). Metrics: shield casts per 100 alive rounds 2.1 to ~6;
shieldingDone@200; deaths before r150; monsterDamageTaken.

**Test protocol (all three):** variant vs frozen v3e, 40 maps x 2 sides, `--release`, full length, paired against the v3e mirror baseline (as g1). Accept only if the
paired margin is positive by >= 1 SE and there are no faults.
