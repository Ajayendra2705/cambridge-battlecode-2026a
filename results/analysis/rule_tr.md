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
