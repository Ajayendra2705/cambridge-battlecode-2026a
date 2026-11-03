# Decision rule: later siege on gated altars, written 11-03 13:35 IST before any game

**Factor.** The altar race on gated altars. On 01boss_battle the only altar (25,20) sits behind two monoliths at (24,20) and (23,20), and the only tile from which anyone tributes is (24,20), so throughput is one channel at a time, 10 gems a round. Ranked games against neighbours (`data/fights/q_worst`, 11 games, 2 wins): we held 1000 gems in hand in 9 and lost 7 of those. We broke the guards in 9 of 11 (hits 201-534 against 3-72), and then stood at the altar poorer than the rival: when the guards fell before r520 our gold was 3800-4650 against 7000-9700 (0 wins of 4); at r843 it was 14982 against 11621 (a win).

**Change.** `mk_vsg.py`: P_SIEGE_FROM 400 becomes r700, r900 or r1200 on gated maps only (`vsg7`, `vsg9`, `vsg12`).

**Local bar, 01boss-battle only.** Paired with `vnl1` over the same opponents and sides, against bots of the v1503 line and others that break the guards (the pool's older bots lose to the base 8 of 8 here, so they do not count alone). Metric: wins and margin of tributed gems. A candidate passes if wins are up by at least 0.15 and margin is not down. Guards: on other maps every game is identical to the base (the change reads `W.gated`).

**Platform.** With the user's OK only. A local pass is needed, not enough.
