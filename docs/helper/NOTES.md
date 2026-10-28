# Helper agent h2: stale-state audit (notes for the lead)

Newest entries first. Bots are `bots/exp/h2*` (gitignored), scripts `tools/helper/`, outputs `data/helper/`.
Everything here is local only: nothing was submitted or gated.

## 10-28 13:30 IST: Job 1 summary for the lead (7 confirmed bugs, patches ready for tg1 or go1)

wb1 was rejected and deleted at 12:55, so my folders are built on `bots/exp/h2base`, a byte-identical copy of wb1 made
before. Every fix touches code that tg1, uf1 and go1 share unchanged: the patches in `docs/helper/patches/` apply with
`patch -p1 < .../h2X.patch` inside a bot folder (dry-run on a copy of tg1: all seven apply).

| Bug | Fix (patch) | Mechanism check | Local effect, paired to the same games (two 60-game sets) |
|---|---|---|---|
| Focus call re-read as fresh every 32 rounds | `h2fc1` | twin `h2cx2l`: stale focus reads 77 -> 0 in the same 18 games | set 1: margin +27 +- 39, deaths +0.03 +- 0.37 (15 games changed) |
| Respawn broadcast decoded 256 rounds late | `h2bc1` | twin: late broadcasts 10 -> 0 | set 1: 3 games changed, margin -5 +- 4 |
| Dead or resumed turns write claims and help from a stale cache | `h2sm2` (supersedes `h2sm1`) | twin with `h2sm1`: dead-turn reverts 17 -> 0; 2 ghost-claim events left came from turns resumed after running out of fuel, which `h2sm2` covers (it reads bytes 0-4 inside each write) | `h2sm1` set 1: margin +0 +- 33, deaths +0.20 +- 0.38; `h2sm2` set 2: margin -2 +- 55, deaths -0.10 +- 0.36 |
| Group back up keeps 0 health for members out of view | `h2hz1` | (in the twin: built on `h2sm1`'s twin) | set 1: collected -40 +- 26, deaths -0.22 +- 0.30; set 2: collected +23 +- 28, deaths -0.45 +- 0.25 |
| Help call: clears erase another's call, erased calls never rewritten | `h2hl1` | probe 2: 227 erasing clears, 13% of calling turns without the call | set 1: deaths -1.07 +- 0.50 (00contest -7.0 per game over 6 games, the rest -0.33); set 2: deaths +0.03 +- 0.23, collected +26 +- 26 |
| Shop picks the next emblem on the strength from before this turn's purchases | `h2ss1` | probe 3: 217 emblem starts in 18 games differ (12 per game), mostly Bruiser-strength bought where the formula gives Durability | item change: local runs cannot judge it |
| D line names the activity of the turn before the last | one line (section 7 below) | probe 2: 68 of 177 D lines | logging only |

Combinations: `h2cx3` = `h2fc1` + `h2bc1` + `h2sm2` (set 2: margin -41 +- 61, deaths +0.43 +- 0.44, their deaths -0.62 +-
0.54); `h2cx1` (with `h2sm1`) set 1: margin +3 +- 50, deaths +0.40 +- 0.56; `h2cx2` (= `h2cx1` + `h2hz1`) set 1: margin
-52 +- 44, deaths +0.53 +- 0.46. Read with `python -I tools/helper/h2_localpair.py BASE_RUN BASE_CAND NEW_RUN CAND...`.
Set 1 = the lead's 10 maps (base wb1 `data/runs/multi-120939`; `multi-124154`, `multi-130103`), set 2 = 01boss-battle,
00rows, 02gift-wrapping, 00split, 00swirl, 01elk-arena, 00corners, 02the-pack, 00lanes, 00stampede (base `h2base` in the
same run, `data/runs/multi-131553`). Decoded (set 1, r1000, `decoded.py gems`): wb1 collected 826, tributed 688, lost on
death 73, deaths 5.3; `h2fc1` 829 / 689 / 70 / 5.3; `h2sm1` 827 / 677 / 86 / 5.7; `h2cx1` 817 / 669 / 85 / 5.7.

My reading: none of the fixes moves a local number beyond noise (local games are our own pool bots; fights and items need
the platform). The four knowledge fixes (`h2fc1`, `h2bc1`, `h2sm2`, `h2hz1`) make the bot act on what it means to know, at
no measurable local cost; if the lead wants one gate for them, `h2cx3` + `h2hz1` is the bundle, judged by the usual
deaths and tribute guards. `h2hl1` (more help reaches callers) and `h2ss1` (strength users buy more health emblems) change
behaviour in a direction only the platform can judge; note that `h2ss1` moves our strength users further from the top
teams' strength-heavy builds, so the current build is partly this bug.

Round 4 (probe `h2pr4l`, 00eight, 00crater, 01yellow-brick-road, 00contest, 24 games, `data/runs/multi-132348`), two
more real but minor ones, not fixed:

- **Held-walk detector counts fighting as a held way** (`bot.cpp`, `Bot::play_turn`, `held_turns`): a walk activity that
  ends on the start tile twice while moves avoid danger bans the target for 20 rounds. 123 bans in 24 games; in 35 the
  champion had attacked or cast in a held turn instead of walking (32 in both turns), including 23 of the 29 bans of a
  ranged champion, which cannot walk after a basic attack. All 123 had 1-3 enemies in view (nearest 2-6 tiles), so the
  group is contested anyway; a fix would add `!S.attacked && me.can_cast()` to the condition, effect unclear.
- **A bank give-up outlives a death or a trip home** (`bank_blocked_until` is never cleared): 2 give-ups in 24 games (wb1's
  reset made them rare), and both still blocked banking after the carrier had been home (00contest r1718: 200 gems, 32
  more rounds blocked). Fix if wanted: `bank_blocked_until = 0` at spawn and on death.

Smaller findings of round 3 (probe `h2pr3l`, 18 games, `data/runs/multi-130742`): the calibration `cal_f` takes 6% of its
predicted damage from samples after a skipped turn (death, channel), which lowers it by about 1% (1.307 against 1.322):
no fix. A live group whose members in view are all dead keeps those members' old health (`update_knowledge`, second
branch, raw state 1): 607 events, almost all gem or gold clusters (mean stale strength 4): minor, not fixed.

## 10-28 13:00 IST: second round: a fourth knowledge bug (groups back up keep 0 health out of view), help-call desync, stale shop strength

Probe `bots/exp/h2pr2l` (wb1 plus event prints, never ship) on 00eight, 00crater, 01yellow-brick-road, 01boss-battle and
02guardians against pool/cand1, cp3, dh3, both sides (30 games, `data/runs/multi-125121`; the tagged lines are saved in
`data/helper/h2pr2l_*.txt`).

| Suspect | Where | Verdict | Probe numbers (30 games) | Fix folder |
|---|---|---|---|---|
| A group seen back up keeps the dead group's 0 health for members out of view | `knowledge.h` `update_knowledge` | **bug, confirmed** | 994 times (977 after a respawn, 17 after a reward); 294 left an elk-sized member or bigger at 0; 359 picks chose such a group (yellow_brick_road 194, boss_battle 126); 18 gather waits skipped only because of it | `h2hz1` |
| `my_help` is what we wrote, not what the help field holds | `comms.h` `write_help` | **bug, confirmed** | 227 clears on live turns (5 on dead turns) erased another champion's live call; of 5328 calling turns, the caller's call was missing in 700 (13%: 423 overwritten, 277 erased) and is never written again | `h2hl1` |
| Shop choices use the snapshot's strength after this turn's purchases | `shop.h` `shop`, `S.str` | **bug, confirmed** | probe 3 (18 games): 552 emblems were started after a purchase in the same turn had raised strength, and 217 of them (12 per game) were a different emblem than the current strength gives: Bruiser-strength for Durability 141, Power for Durability 40, Power for Jungle 23, Power for Bruiser 13 (at 45 strength against the real 70 after the Treasure emblem, Power beats Durability); `my_dps` used a strength from before a purchase in 4437 of 74597 fight evaluations (6%) | `h2ss1` |
| Reward (state 1) held in knowledge after it was gone | `knowledge.h` | fog, no fix | 110 of 5784 reward observations ended 11+ rounds after we last saw them (31 found the group alive again, 79 respawning) | - |
| Guard-blocked banking let through by an enemy tribute first noticed late | `targets.h` `bank_gems` (`enemy_rise`) | real, rare | 1 game of 10 on guard maps: 02guardians r1872-1900 (noticed r1798, rose r1742) | none |
| D line names the activity of the turn before the last | `state.h` `record_death_ctx` (`last_activity`) | **logging bug** | 68 of 177 deaths name a different activity than the last live turn (flee for stunned 12, pvp for flee 8, flee for pvp 6) | one line, below |

`h2cx2` = `h2cx1` + `h2hz1` (the four knowledge fixes: focus call, broadcast, dead-turn writes, zeroed members).
`h2hl1` and `h2ss1` change behaviour in a direction I cannot judge locally (more help reaches callers; strength users buy
health emblems after a strength emblem instead of another strength one), so they are kept separate.

### 4. Groups back up keep 0 health out of view (`knowledge.h` `update_knowledge`)

When a group is not up (reward or respawning) its member health is 0. Seeing it up again with only some spawn tiles in
view takes the first branch (`group_live_now`), which sets the state to 0 and reads the visible members, but never resets
the rest; the second branch does reset (`g.state == 0 && prev == 2`), the first does not. The members out of view keep
health 0 until each is seen, so `hp_left`, `strength_left` and `hardest` read low: `pick_group` finds the group cheap
(00crater group 2 read as strength 0 with its 60-strength elk out of view), the gather rule for 200+ strength does not
start, the retreat rejoin pressure is low, and those members make no phantoms. A broadcast (`read_broadcast` fills 0)
leads into the same branch.

Fix (`h2hz1`): `if (g.state != 0) g.reset();` before `g.state = 0;` in that branch (a group comes back whole at full
health).

### 5. Help call: `my_help` desync (`comms.h` `write_help`)

`write_help` skips when `v == my_help` and clears unconditionally. When two champions call, the later write wins; the
first caller keeps `my_help` and never writes again, and when either stops calling it writes 0 over whatever the field
holds, erasing the other's live call. Fix (`h2hl1`): clear only when the field holds our own call, and write our call
again when the field is empty. Overwriting another's live call keeps the old rule (a new call wins), so callers do not
alternate.

```cpp
    const int field = static_cast<int>(claim_bits() >> 30 & 1023);
    if (v == 0 && field != my_help) { my_help = 0; return; }
    if (v == my_help && !(v != 0 && field == 0)) return;
```

### 6. Shop and `my_dps` use the strength from before the purchase (`shop.h`)

`shop()` judges each new emblem with `S.str`, the strength at the snapshot. In one spree the loop completes an emblem and
starts the next, so after a strength emblem the next choice still sees the old strength: `6 gm / main` is too high and the
choice leans to Power or Bruiser of strength over health (Vesper, Vendetta, Varg; focus users read `me.focus()` fresh;
Heart of Ruin's `v_str` reads `S.str`). `my_dps()` is recomputed after a purchase but from the same `S.str`, and cached for
10 rounds. Fix (`h2ss1`): `S.str = me.strength();` after `me.buy(choice)`. An item change: only the platform can judge it.

### 7. D-line activity is one turn old (logging only)

`record_death_ctx` stores `last_activity`, which at that point is the activity of the previous turn (`play_turn_core`
sets `last_activity = activity` before this turn sets its own). Every reader of D lines (the `flee` column of `multi.py`,
`dact.py`, the D-line activity in `deathfactors.py`) sees the turn before the last. Fix: store `activity` at the end of the
turn (for example `death_ctx.act = activity;` after `play_turn_core()` in `Bot::play_turn`), which changes no play.

## 10-28 12:45 IST: Job 1, first round: three confirmed shared-memory bugs in wb1

Probe `bots/exp/h2pr1l` (wb1 plus event prints, never ship) on 00eight, 00crater and 01yellow-brick-road against
pool/cand1, cp3 and dh3, both sides (18 games, `data/runs/multi-123627`). Read it with
`python -I tools/helper/h2_probe_sum.py data/runs/multi-123627`.

| Suspect | Where | Verdict | Probe numbers (18 games) | Fix folder |
|---|---|---|---|---|
| Focus call read as fresh every 32 rounds | `enemies.h` `focus_target` | **bug, confirmed** | 77 stale reads (ages 32-35, 64-67, 96-99, 160-163); 74 gave a champion a prey it did not have, 17 started an engagement | `h2fc1` |
| Respawn broadcast decoded 256 rounds late | `comms.h` `read_broadcast` | **bug, confirmed** | 2 games: 00eight's north double elk (group 0, real respawn r330) held as respawning by all five from r395 to r586; a yellow_brick_road group from r194 to r385 | `h2bc1` |
| Dead turns write shared bytes 0-4 from the last live turn's cache | `bot.cpp` dead branch, `write_help` / `write_claim` | **bug, confirmed** | 33 dead-turn writes: 17 reverted a teammate's claim (22 slots), 2 erased another champion's live help call; 27 ghost claims seen by their owners, 184 rounds in all, longest 39, 3 on a reward ready to capture | `h2sm1` |
| Enemy tribute history read where it was never written | `bot.cpp` bank stage, `enemy_hist` | bug, confirmed, **fix not recommended** | 17% of bank evaluations read a history entry that was never written (0); 199 bank decisions changed, all towards banking earlier (153 by a smaller batch, 22 by the deadline rule) | none |
| `enemy_seen_at` ("mirrors enemy_seen_round") is set only on unexplained hits | `move.h` `go_home` | code differs from its comment; **no fix** | 398 of 959 recalls start with an enemy seen within 6 in the last 3 rounds; 5% of them are cut off (2% of the others), 2 deaths | none |
| My help call overwritten, or cleared over another's | `comms.h` `write_help`, `my_help` | real, small | see the SW row; a separate count is pending | pending |
| Claim encoding `(group + 1) & 63` | `comms.h` | not a bug | the largest map has 51 groups (00road-of-riches) | - |

`h2cx1` is all three fixes together (`h2fc1` + `h2bc1` + `h2sm1`).

### 1. Focus call wraps every 32 rounds (`enemies.h` `focus_target`)

Byte 7 holds `(enemy index + 1) << 5 | (round & 31)`, and a call counts while `((round - (b & 31)) & 31) <= 3`. Nothing
clears the byte, so 32 rounds after the last call it reads as fresh again (rounds R+32..R+35, R+64..R+67, ...) until a new
call replaces it. Every champion that then sees the called enemy within 8 tiles takes it as prey. In the probe this
happened 77 times in 18 games (4.3 per game), almost always to a champion with no prey of its own (74), and 17 times it
started an engagement (the pvp branch) that would not have happened. A ghost prey also blocks the flee rule
`hit_by_enemy && !prey`.

Fix (`h2fc1`): a champion that reads an expired call clears byte 7 (only on a fresh turn: `!stale()`). Fresh calls read
exactly as before.

```cpp
    if (b == 0) return nullptr;
    if (((S.round - (b & 31)) & 31) > 3) {
        if (!stale()) write_byte(7, 0), shared_cache[7] = std::byte{0};
        return nullptr;
    }
```

### 2. Respawn broadcast decoded 256 rounds late (`comms.h` `read_broadcast`)

Bytes 5-6 hold the last observed respawn (group + 1, respawn round & 255) and are never cleared. The reader rebuilds the
round in the window [round - 64, round + 192]. Once the real respawn R is more than 64 rounds past, the window holds
R + 256 instead, which is in the future while round - R is 65-255. Every champion that cannot see that group's spawn
tiles then sets it to respawning until R + 256 (and again each time it loses sight of it), so `pick_group` ignores a live
group. It needs 65 rounds without a new broadcast: 2 of 18 games in the probe, each time all five champions; on 00eight
it was the north double elk (37 gems, 200 gold) from r395 to r586 (1664 champion-turns with a ghost in force over the
18 games).

Fix (`h2bc1`): once the decoded respawn round has passed, the reader clears byte 5 (fresh turns only). A fresh broadcast
decodes as before.

```cpp
    if (r <= S.round) {
        if (!stale()) write_byte(5, 0), shared_cache[5] = std::byte{0};
        return;
    }
```

### 3. Dead turns write shared memory from a stale cache (`bot.cpp`, dead branch)

`write_help` and `write_claim` rewrite bytes 0-4 (all six claims and the help call) from `shared_cache`. Live turns
refresh the cache first (`refresh_claims`); dead turns return before that, so the first dead turn of a champion that died
holding a claim or a help call writes back the bytes as they were at its last live turn. Teammates' claim changes in that
window are undone, and a claim's owner never rewrites it while its own target is unchanged (`write_claim` skips
`group == my_claim`), so the ghost stays until the owner's target changes. In the probe 17 of 33 dead-turn writes reverted
a teammate's claim; the owners saw 27 ghost claims (184 rounds, median 1-2, longest 39), 3 of them on a defeated group,
where a ghost claim stops every other champion from taking the capture (`pick_group`: `others > 0 && i != current`). Two
writes erased another champion's live help call.

Fix (`h2sm1`): read bytes 0-4 into the cache at the top of the dead branch.

```cpp
    if (!was_alive) {
        cambc::shared_memory.read(0, std::span{shared_cache.data(), 5});
        write_help(0);
```

### 4. Bank-stage enemy history with holes (`bot.cpp`, bank stage; fix not recommended)

`enemy_hist[round]` is written only on turns that reach the bank stage (not dead, channelling, fighting, fleeing or
healing), but `e_rate` reads `enemy_hist[round - 150]` as if every round were there. An unwritten entry is 0, so the
enemy's whole tributed total counts as tributed in the last 150 rounds: `t_end` shrinks (389 against 941 in one case),
the hazard term `1 / t_end` grows and the batch falls (55 against 66). The probe compared every bank evaluation with an
every-turn history: 17% read a hole, and 199 decisions changed in 18 games, all towards banking earlier. Fixing it would
make carriers bank later, against the current factor (gems lost on death), so I do not propose the fix on its own; if the
order-quantity rule is ever refitted, write the history every turn first.

### 5. `go_home` recall rule (no fix)

`enemy_seen_at` is commented as mirroring `enemy_seen_round` but is set only on unexplained damage, so `go_home` recalls
with an enemy at 6-8 tiles in view or one seen within 6 a round ago (docs describe the rule as "none seen for 3 rounds").
41% of recalls start that way; 5% of those are cut off against 2% of the rest. Walking instead would give up many recalls
that complete (93%), so the code is probably better than the comment.

### Local check of the fixes

Done: see the 13:30 summary at the top (`data/runs/multi-124154`, decoded in `data/fights/local_multi-124154_exp.h2*`).
