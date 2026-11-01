# One small factor: tribute restart loops (trA, trB)

Written Sun, Nov  1, 2026, 21:51 IST, before any trA or trB game (local or platform).

## Factor

A champion that starts a tribute and has it cancelled by its own channel watch (`kChannelWatch`, `tribute_doomed`)
starts it again in the same or the next turn, round after round: it stands at the altar and banks nothing. The start
rule (`channel_unsafe`) refuses only with an enemy within 6 (`kChannelSafe`); the cancel forecast counts every enemy
within (turns left + 4) tiles, so a 200-gem bag (20 turns) is "doomed" by any enemy within 24. Bags that big come from
monoliths and long bags. Measured with a scratch reader (`loops.py`: a restart is a tribute issued with the same bag
before the earlier channel could have completed; an episode is a run of restarts):
- b40 base (1478, 90 three-a-side games): restarts 2.36 a game (rivals 0.43); 0.36 episodes a game, mean bag 204,
  19.8 rounds each; a 626-gem bag looped 110 rounds on adgato_gemcombat1 with 798 banked, and that game was lost
  798-850.
- 180 ranked games of 1472 (all sizes): 0.48 episodes a game, bag 241, 14.6 rounds; 11 of 86 ended in a death.
- local hy1 (90 games): restarts 5.72 a game, 0.58 episodes, 26.9 rounds each.

## Changes (one condition each, in the Bamboo part only; all sizes)

- trA: the Bamboo team's own fix, `kReviewFix` bit 1 (`start_doomed`): start no tribute the cancel forecast would
  abort.
- trB: `kKeepChannel`: the channel watch does not cancel a channel that the start rule would start again at once
  (`!channel_unsafe()`); it still cancels when an enemy is within 6 and no start exception holds.

## Local rule (15 maps of `multi-195654` against cand1, cp3, dh3, both sides: 90 games each, paired with hy1)

Target: restarts per game down by at least 75% (from 5.72). Guards (paired, `econpair.py` and `paired`-style means
from the local decode): deaths not up by more than 0.3 a game; gems lost on death not up by more than 10 a game;
gems collected not down by more than one standard error; no bot fault. If both pass, the one with the larger tributed
gain goes to the platform; trB first if tied (it banks, trA only waits).

## Platform rule (b38p, pinned to `l1478_b38@b38`, all sizes, and b40p, pinned to `l1478_b40@b40`; 180 paired games)

Target: restarts per game down by at least 75%. Guards: deaths to r1000 not up by more than 0.3 a game; gems lost on
death (`paired.py` "us lost") not up by more than 10 a game; our tributed to r1000 not down by more than one standard
error. Wins are recorded, not judged. A run during which the active version changed by someone else's hand is void.

## Result on 1478's games, and an addendum (written 23:40 IST, before any hy1 game on b38p or b40p)

trB on b38p (upload 1485, 22:21) and b40p (1485 selected, 22:46), 180 games paired with 1478's: restarts 2.41 to
0.09 a game (-96%, target met); gems lost on death +3.4 +- 6.8 and tributed to r1000 -6.4 +- 13.7 hold; deaths to
r1000 +0.306 +- 0.234 a game, just above the 0.3 bar: by the rule above trB fails its deaths guard. Deaths while
channelling (to r1000) did not rise (b38 0.08 to 0.04 a game, b40 0.04 to 0.06); the rise is in other deaths. On the
20 games that hy1 played too (`hy1_b38q`), trB's games are identical to hy1's to r1000 (deaths and both tributes in 20
of 20), and hy1 itself has +0.25 deaths a game against 1478 there. So the base was the wrong build: hy1 differs from
1478 (fuel and memory layout) and that difference, not the change, moves the deaths.

Addendum: hy1 (platform version 1484, selected, no upload) plays b38p and b40p, and trB is paired with hy1 on the 180
games. Pinned games of the same build replay exactly, so the two runs differ only in games where the change acted.
Same target (restarts down at least 75%) and the same guards (deaths to r1000 not up by more than 0.3 a game, gems
lost on death not up by more than 10, tributed to r1000 not down by more than one standard error); also reported: the
number of games that differ and their flips. The verdict on 1478's games above stands as recorded; this run decides
whether the change itself costs deaths.
