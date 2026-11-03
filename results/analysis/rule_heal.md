# Rule: Willow's heal threshold (written 22:27 IST 11-03, before any game)

**Why.** Casts to r1000 on 773 decoded games (`data/fights/q_all`, `tools/replay/casts.py`): every type casts about as often as the same type on the rival side, except Willow's heal, 24.8 a game against 37.9. Both stand as close to their allies (nearest ally within 4 tiles in 65% and 68% of the rounds), and neither ever targets itself. The target misses 514 health before our heal and 341 before theirs, so the difference is the threshold: `P_HEAL_MISS` 0.6 asks for 252 missing health or more at 140 focus. No earlier row tests a lower one.

**Variant.** `exp/hm3` = `exp/ra1` with `P_HEAL_MISS` 0.3. It changes games with a Willow only (four and five picks).

**Local bar, against `exp.ra1` on the 85 maps and the four pool bots, paired:**

- Factor: our deaths to r1000 down by at least 1 SE, or margin up by at least 1 SE.
- Guards: collected and tributed to r1000 not down by more than 1 SE, team gold r600 not down by more than 1 SE, no fault.
- Heals a game up by at least 30% on a decoded sample, or the threshold did not do what it was meant to.

Wins are recorded and not judged. A pass only allows the change to join the next router's platform test; local games cannot prove a fight change.
