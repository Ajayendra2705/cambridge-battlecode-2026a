# How Battlecode is solved: a study of postmortems

Written 2026-10-29 after the user asked (10-29) to spend a day studying how teams in general solve Battlecode problems (MIT Battlecode 2019-2026, UNSW and others), not only this game, and to study our own problem statement in depth before changing the bot. `docs/STRATEGY.md` applies the conclusions to our game; this file keeps the evidence: what each source says, in its own terms, and what the sources agree on.

Status: complete for the sources in the table (read 10-29). Sections: 1 the sources; 2 the MIT postmortems one by one; 3 UNSW Battlecode 2026; 4 other bot-programming contests; 5 what the sources agree on; 6 what this means for our game.

## 1. Sources

MIT Battlecode is a yearly January competition (about three weeks, sprints, qualifiers, finals) in Java with a bytecode limit per turn; the game changes every year. Its postmortems are PDFs at battlecode.org/assets/files/postmortem-YEAR-TEAM.pdf, linked from the MIT site; the copies read here were kept in the session scratchpad, not in the repo. The UNSW and other sources are linked in sections 3 and 4.

| Year | Team (place) | Game in one line | Read |
|---|---|---|---|
| 2019 | smite (1st; the postmortem is dated 2019-02-01, before the final) | Crusade: castles, churches, pilgrims, crusaders, prophets, preachers; karbonite and fuel | yes |
| 2019 | Big Red Battlecode (8th), Oak's Last Disciple (33rd-48th) | same | yes |
| 2020 | Java Best Waifu (1st; XSquare's team) | Soup economy, flooding water level, miners, landscapers, drones | yes |
| 2020 | The High Ground (4th), Bowl of Chowder (5th-6th), confused (high-school 2nd) | same | yes |
| 2020 | Battlegaode | same | no (site down) |
| 2021 | Baby Ducks (1st) | Politicians empower in a radius, slanderers earn influence, muckrakers expose; vote count tiebreak | yes |
| 2021 | Malott Fat Cats (4th), wololo (7th), 3 Musketeers (9th) | same | yes |
| 2022 | 5 Musketeers (7th) | Archons, miners, soldiers, sages, lead and gold, anomalies | yes |
| 2023 | Gone Fishin' (2nd; first seed into the finals) | Headquarters, carriers, launchers, amplifiers, islands, wells | yes |
| 2023 | 4 Musketeers, don't @ me (finalist), no thoughts head empty | same | yes |
| 2024 | Cout for Clout | Ducks, flag capture, traps, crumbs, global upgrades | yes |
| 2025 | Just Woke Up (1st), confused, Om Nom | Paint, towers, soldiers, moppers, splashers; tile painting score | yes |
| 2025 | SPAARK, The Kragle (top 16 US) | same | yes |
| 2026 | Generalized Stroke's Theorem (2nd) | Rats, Rat Kings, neutral cats; cheese economy; vision cone | yes |
| 2026 | food (9th-12th), Lorem Ipsum (13th-16th) | same | yes |
| any | XSquare's guide | General guide to Battlecode by a multi-year finalist | yes |
| 2026 UNSW | zitianqin (sprint seed 13 of 591; his merged team 3rd) | Dragons: snake-like units on a torus, pearls, splitting, sonar-only messages; 500 rounds | yes |
| 2026 UNSW | juntegral's "meow" (ladder peak 23rd), Team 777 (153rd), UnderTheC (ladder peak 16th) | same | yes |
| 2016 | Russian AI Cup, CodeWizards: DragoonXen (2nd) | A simplified DotA: five wizards a side, lanes, towers, skills on cooldowns | yes |
| 2011 | Google AI Challenge, Ants: xathis (1st), through the LessWrong postmortem | Ants on a grid: food, hills, fights decided by local numbers | yes |
| 2017-19 | Halite II (reCurse 1st, no write-up), Halite III (Stone Tao) | Fleets docking on planets with automatic fights; mining halite | yes (III) |
| 2023-24 | CodinGame challenges: reCurse (1st, 1st, 2nd) | Small, fully specified games that simulate cheaply | yes |

## 2. What each source says

### smite, 2019 (1st)

- "The first to move in range of the opponent dies": in a symmetric fight the side that steps into range gives the other side the first shot.
- Every loss in their final weeks was traced to a bug, not to strategy: they replayed losses until they found the cause.
- Maps are symmetric, so controlling one cluster on the enemy side creates an income asymmetry the opponent cannot match.
- "There is no dominant strategy but rather counters for every approach": scout the opponent's approach early and pick the counter.

### Java Best Waifu, 2020, and XSquare's guide

- Micro is a per-square evaluation with a fixed comparison: for each square the unit can end on, compute a few numbers and compare squares with ordered tie-breakers. Ready to attack: go to the square where you can attack with the fewest enemies able to hit you back. Not ready: go to a square no enemy can hit.
- "All top teams copy" macro from each other; macro is visible in replays.
- Simplicity, robustness and structured code; robust primitives first (pathing, communication, micro, testing). When the strategy changes, rewrite from scratch rather than patch.
- Do not discard a change that sits near 50% too fast; do not make last-minute changes before a deadline.

### Baby Ducks, 2021 (1st)

- One scalar metric for the key action (empower): 100 x (kills - 2) + (influence drained - conviction spent). Every candidate action is scored on that one number.
- They built two bots with opposite styles and tested them against each other, so that each change was tested against a style the ladder did not yet show.

### wololo, 2021 (7th)

- Theory first. A resource is something such that "if your team had none of it, you've probably lost; you could remove it from the opponent; it could be difficult to obtain if the opponent was trying to prevent you". List the resources, find the exchange rates between them, and analyse which trades are forced and which positions are near equilibrium.
- Optimal empower radius computed, not tuned; move direction picked by a minimax over immediate trades.
- Pipeline: a micro step returns all tied-best moves, and a macro step chooses among them, so macro never overrides a micro-worse move.
- Roles per unit; a dynamic switch between rushing and turtling based on what is seen.

### 4 Musketeers, 2023

Four micro rules: outnumbered or very low, back off (attack first if possible); ready and in range, attack then back off; ready and out of range, step in and attack; hurt allies retreat and heal together, then return together.

### Gone Fishin', 2023 (2nd; first seed into the finals, which Producing Perfection won)

- "ALWAYS kiting back after an attack is better": attack, then step out of range, so the enemy must step in to answer and gives the first shot back.
- The lower-health unit stays behind the healthier ones.
- Spawn formation (who spawns where and acts first) won about 2/3 of games against the version without it.
- "Macro +5%, micro +30-50%": their estimate of the win-rate effect of each.
- Stack-based bug navigation (later adopted by others).
- They lost the final on a map-specific bet: map-specific code is risky.

### Cout for Clout, 2024

- Started with "lots of if statements and a combat BFS"; it became too complicated to modify. Switched to XSquare's framework (per-square evaluation): about 1850 to 1950 rating, then past 2000.
- Squadrons sent to "combat locations" so that units arrive together (Lanchester's square law: fighting strength grows with the square of the number of units). Units move towards hurt, stunned and low-health allies.
- A "sitting duck" test, three units guarding home against two, lost 90% of games: it took units out of the fight.
- A/B testing against old versions on all maps, both sides (camel_case's script).
- Closing pages: "Most teams use the same ideas; it's the execution of those ideas that make most of the difference, only possible through careful analysis of scrimmages and your code." Traps were placed where they would be triggered soonest (count of enemies within reach, tiles between the enemy and the goal), with a spacing rule so that one enemy does not set off several at once.

### Just Woke Up, 2025 (1st)

- Synchronise entering range: units step into the enemy's range together, so a defender can hit only one of them per turn.
- State machines (`determineState`) instead of if-chains.
- 57 versions in about 25 days; A/B test plus automated scrims against the top teams, then watch the losses.
- Kept features that lost in self-play but should beat specific opponent styles (defence towers, resurrection).

### confused, 2025

Form a "game philosophy" of two core principles from extensive replay analysis, then align all development to it.

### Om Nom, 2025

- Replay study revealed "obvious things", for example: do not go home blindly at a threshold, finish the job first.
- Do not exceed the bytecode budget on the first turns: snowballing matters most early.
- Units should live useful lives.
- Infer hidden information (the opponent's tower count from its income; map symmetry checks).
- Bit-shifted BFS for pathing at a fraction of the cost.

### SPAARK, 2025

Every resource converted into one score; for each candidate square both orders are tried (move then attack, attack then move).

### Generalized Stroke's Theorem, 2026 (2nd)

The 2026 game was the first MIT game with neutral threats (cats), the closest to our camps.

- Structure: a State Updater picks a Behaviour each turn (micro, explore, collect); each Behaviour is a singleton that keeps its own state. It replaced 3000-line files and kept iteration fast late in the season.
- Communication: a small message protocol with a 3-bit type header and one class per message type.
- Pathing: unrolled BFS plus stack-based bug navigation, switching when BFS stops making progress; a digging cost tuned the "laziness" of units. A bit-shift reachability check (about 300 bytecodes) stopped units from trying to micro through walls.
- Macro: "best improved by scrimmaging against good teams, and copying what they do". Queue scrims against teams above on the ladder, reverse-engineer their macro ("much easier than reverse engineering micro"), copy it, keep it if it helps. Their unit counts and timings came from this.
- Micro: XSquare style, each of the 9 squares scored on passability and distance to allies, enemies and cats, compared with a chain of if/else tie-breakers.
- Information maximisation: in micro every unit broadcast its health and its nearest enemy every turn, even at the cost of going over the bytecode budget in crowded fights, because enemies to the side or behind decide fights.
- Neutral threats: avoid the cat's vision; if not possible, avoid the 2-3 squares in its path. Distance to cats mattered but "could not be prioritized too heavily at the cost of making worse decisions regarding enemies": enemies are smarter and more predictable than cats, so enemy threat came first.
- Throws: enumerate every reasonable move + turn + throw combination and score the outcome (cat, enemy, wall, ally, nothing); some combinations were removed after trial because they led units into danger.
- Improving micro: "by far the best way is to watch a lot of games", follow single units into combat, find each stupid decision and fix it with minimal effect on other decisions; watch teams with better micro and reverse-engineer them.
- "We spent far more time reviewing scrims than actually writing code"; try many strategies rather than getting attached to one.

### food, 2026 (9th-12th; solo, first year)

- Before the specs came out, read postmortems and past code for days; called it "exceptionally beneficial".
- Five states only (find king, collect, explore, build king, return), chosen by ordered conditions with coin flips to split roles. Few states make behaviour easy to debug, shared across situations, and coordinated, because more units are in the same state.
- Infrastructure: symmetry found by eliminating the symmetries that a sensed tile contradicts; a king heartbeat bit and an SOS bit in the shared array; enemy positions relayed hop by hop by units that hear them.
- Pathing: XSquare's bug navigation all season; most maps favoured greedy movement.
- Combat theory: in a duel the best play is never to step into the enemy's reach. A passive team beats an aggressive one; two passive teams stand off for hundreds of turns and both lose map control and income. Answer: "play aggressively when you have the numbers advantage or good positioning, and passive otherwise. Even if you end up losing rats by playing aggressively, your opponent will also, and then you can win with smart economy management."
- Combat movement: score the 9 squares. Negative terms: impassable, near cats, near enemies (more if the enemy has more health), in a projectile path, squares from which an enemy can always reach you next turn. Positive terms, in order: a square from which we capture by position, capture by health, hit the king, finish an enemy ("to prevent the enemy unit from being able to do another attack next turn"), hit an enemy; then near the enemy king; then closer to the destination. Attack greedily, then move, then attack again.
- Context switches the weights: near a king under attack the enemy-proximity penalty is inverted (units run at the enemy), and it is halved when allies outnumber enemies 2 to 1.
- Spend extra resource on a hit only when it finishes a kill or equalises health (which denies the enemy's capture next turn); a constant small boost was removed after replays showed it was meaningless.
- A trap that costs 30 almost always gets a kill worth 40-50 to the enemy: count trades in resources.
- Mistake found after the finals: a fixed unit count (16) was right on big maps and wrong on small combat maps, where units are traded faster and a high count means paying more per traded unit than the enemy. The count should scale with the map.
- "Many matches were won simply by who formed a rat king first" (the second economic base).
- Fleeing a neutral threat: move sideways out of its path while increasing distance, not straight away.
- Advice: ignore sprint results and the ladder; build fundamentals. Beware overfitting: "if you use an older version of your bot as a baseline, and accept any change that increases your win rate, you'll see rapid improvements locally, but you might not perform any better against actual teams". Derive behaviour from one core principle. Do not obsess over win rate: ideas often get worse before they get better. Step through single units' turns and ask what a human would do there. Test a behaviour on 3-5 maps built for it and watch the replays; running 20-30 maps at once hides why the bot won or lost.

### Lorem Ipsum, 2026 (13th-16th; solo, first year, ladder 30th-60th)

A weaker finalist, useful as a contrast.

- Roles (soldier, miner, scout) were removed because scouts and soldiers kept ending up in 1v3 fights and dying; removing them "significantly increased the survivability". Lost units are expensive.
- Carry limit raised from 40 to 100 after scrims with a stronger team showed the slowdown did not matter: copied from a better team.
- The same profile as ours: "my bot seemed to do well on open maps with plenty of cheese with less influence from the opposing side, whereas they generally did not do well in situations where there was head to head combat (specifically with teams higher rated than me)". Its first combat code was AI-written and "got destroyed in almost all head to head combat scenarios".
- Testing: one to three maps where the change should show, then all maps against old versions (accepted at about 50%), then scrims against teams of similar rating, pulled back if worse.
- Hidden dependencies: cutting messages broke every feature that counted nearby allies; fixing pathing broke king formation, which had relied on units clumping. Both were found only by analysing tournament games.

### The Kragle, 2025 (top-16 US, just missed the finals; rated 1200-1500 in earlier years, about 1800 this year)

Their postmortem is about "the leap" from a mid-ladder team to a contender.

- Reuse before you build: they took XSquare's code structure, bug navigation and micro, which got a strong bot out much sooner than in earlier years. Time spent re-doing XSquare's pathing, and on a "survive" behaviour that "never really impacted the result of any matches", was wasted.
- Do the arithmetic of the economy. A table of costs and rates showed that upgrading a tower is never better than building a new one, and that money towers produce the second resource faster than paint towers do (by destroying and rebuilding them). The same insight won another team the "most innovative" prize. This is wololo's exchange-rate analysis applied.
- Opening: a soldier pair captures an uncontested ruin before turn 20 on 90% of their test maps, and rushes only when every nearby ruin is contested. Out of the opening they often led even top teams, then threw the lead.
- How leads were thrown: floating resources (paint stuck in towers in amounts too small to use) and idle time (units "derping around" far from the fight, or walking back to refill). Broadcasting the nearest battlefront gave "massive improvements" by cutting idle exploring. They noticed late that no other top team refilled at all, which halved their units' idle time once copied: "Other teams beat your bot for a reason, and the easiest way to improve is to copy what they do better than you."
- Decision framework they recommend: a priority queue of goals, each goal type with `shouldStart`, `execute` and `shouldStop`, so that a unit pulled into a fight resumes its task afterwards instead of forgetting it.
- XSquare's micro as they describe it: `doMicro` decides when micro runs (enemies seen, or low health with enemies remembered); `computeMicroArray` fills one `MicroInfo` per square (9 options) with the factors that make it attractive or dangerous; `isBetterThan` compares two squares. Micro moves only; attacking is simple: "target the lowest hp enemy possible, attack whenever possible".
- Economy first: "Battlecode games are often snow-bally, where any small resource lead can very quickly turn into a large advantage", so optimise the opening for resources, then work on converting the economy into the win condition.
- Constants across years: maps 20x20 to 60x60, symmetric by rotation or reflection, and finding the symmetry is "Battlecode 101". Do not upload untested bots before deadlines.

### don't @ me, 2023 (finalist, 8th-12th seed)

- Control flow per turn: sense (store everything seen once), think (pick a control state from senses, messages and the previous state), act.
- Target value: unit type value + damage dealt + half the target's missing health + 100 on a kill; targets already in range first.
- Kiting "every single time movement is available": shoot, then step away, possibly out of the enemy's vision, which gives a free hit when we move first in the round and lets allies step up behind.
- Step up: if an ally is already in range of an enemy, step towards it instead of kiting, because a unit can hit only one enemy per turn anyway.
- Follow first: "we were losing early 3v3 duels left and right": the better teams' units stayed constantly adjacent and took grouped trades against isolated units. Fix: each unit follows the first nearby ally that moved this turn, so groups move as one; out of combat, all units move on even turns only so that they stay together.
- Fall back: below half health and out of combat, go to the nearest healing island and stay until full unless an enemy appears. Rejected early ("we would rather have the map presence ... even if it was low health"), then re-adopted after healing was buffed: units then soaked 5-9 hits per trip.
- "Whichever team won the beginning launcher duel would go on to win the whole match."
- Messages that must survive turn order were double-buffered: on even rounds read the odd half and write the even half, so the last unit in the turn order is not wiped before the others read it.
- Teams that hard-coded for the three ladder maps broke on the tournament's new maps; general code won upsets ("Code > Elo").
- At the top, "generality and robustness starts to take a back seat to legitimate higher-level strategy": specific plans for specific map states.
- When copying a top team, "you have to actively attempt to improve upon the inspired algorithm, or else it'll never be as good". Three games say little; they paired ten-game online sets against ladder teams with all-map local runs against their old versions.

### XSquare across years: Oak's Last Disciple 2019 (33rd-48th) and Malott Fat Cats 2021 (4th)

XSquare (Ivan Geffner) placed 3rd (2017), 4th (2018), 33rd-48th (2019), 1st (2020) and 4th (2021); other teams call his open-sourced micro, exploration and bug navigation the best available and copy them.

- 2019, why he went out early: the meta was a cycle, "Rush > Greedier/Cheesier bots > Greedy/Cheesy bots > Eco bots > Rush", and his team picked the most consistent strategy assuming an even mix of opponents. At the tournament almost no rush bots were left and conservative bots were "heavily punished by not fully investing into expansion". His own verdict: "we barely scrimmed after seeding ... and we didn't see the meta shift that was happening right in front of our eyes". "In Battlecode, experience has told me that consistency is really valuable."
- 2019, synchronised attack: after the attack signal at round t0, a unit does not advance while its distance d to the target satisfies d < C - (t - t0)/k (C = 60, k = 3), so every unit holds the same, shrinking distance and all engage at once.
- 2019, turn-order exploit: build a base and a ranged unit in range of a lone enemy in the same turn, because the turn queue lets the new unit shoot first.
- 2021, priorities: while the rules were still changing, build what stays stable (communication, pathing); pathing "could be improved at any time with no game-changing effect on the rest of the strategy", communication was "the backbone of any non-trivial strategy".
- 2021, micro as an exchange: a unit attacks only if the value of the attack (health removed from enemies + health restored to allies + 17 per unit killed) exceeds the unit's own value (its health, which it spends by attacking).
- 2021, hidden information: the enemy's unit type was inferred from its maximum health, because economic units came in a few optimal sizes.
- 2021, build order by weights: build the unit type with the lowest accumulated weight, then add its weight; weights change with the game phase.
- 2021, why 4th despite holding the ladder's top spot for the whole second half: the economy/offence balance "was heavily map dependent (economy being better the larger the map)", and they tuned it on the sprint maps. The final maps were huge and hard to cross, and their mid-game army arrived after the enemy's defences were built. "Relying on previous maps turned out to be a pretty bad idea." The Kragle (2025) notes the same tendency: the organisers' final maps are larger and slower, which favours economy.

### 5 Musketeers, 2022 (7th; Carnegie Mellon, second year)

- State handling: a state stack "led to tons of bugs and stacks a mile high"; replaced by one control step at the start of each turn that maps the current state plus observations to the next state.
- Oscillation: a distress call made soldiers run home when an enemy blinked into a base's vision and back out next turn, so they shuttled uselessly. Fix: target running averages of where enemies are seen (up to three clusters); one intruder does not move an average.
- Heal starvation: units below a health threshold went home to heal; replays showed units waiting over 1000 rounds while others were healed first, which left the field outnumbered. "Even though the soldier needed healing, it was more advantageous for them to just go into the fight and do their best, even if it meant death." A heal cap and a timeout made them first on the ladder for several days. Later the bases themselves moved towards the fight so healing was close.
- Ranged unit with longer vision: stay outside the enemy's vision, move away from the average enemy position, never retreat onto worse ground (no cornering).
- Choose between single-target and area attacks by a damage score with kill bonuses (more for valuable units).
- Tiebreak exploit: with the game even near round 2000, make a little of the second tiebreak resource.
- Testing: 20 versions (one per major change); every small change tested against several recent versions, and a spreadsheet tracked every change against every version on every map from the start of the season.
- After a balance patch "within hours ... the rankings completely shifted": be ready to rebuild around a new meta.

### The High Ground, 2020 (4th; six years of Battlecode, three top-4 finishes)

- They skipped the sprint, watched the meta, then "shamelessly" copied the leading team's strategy from its replays, with a few improvements, and for a while had a better bot than the team they copied. "The most tried and true strategy in Battlecode is to copy whatever better teams are doing." An original strategy that demolished everyone: "in all our years we have done this exactly 0 times".
- "The main difference between the better and worse teams is not coding skill or speed but prioritization." Do not note every flaw in a replay and fix them all; keep a ranked list and do the item with the largest expected win-rate gain first.
- They ignored the neutral units (cows) because other work ranked higher, and were knocked out by smite on two cow-heavy maps: "it was fair for us to get eliminated based on not dealing with an important aspect of the game". In our game the neutral camps are a central element, not a side one.
- Against a persistent rush that stalled their economy, a blunt rule (return to the normal build order at round 400 whatever happens) won games a cleverer response had lost.
- Constants were never tuned robustly: they could only test against their own bots, wanted to beat both turtles and rushes, and kept changing the bot.
- Between qualifying and the final deadline: 2019 too cautious (fell from the top to 4th), 2020 too many changes (each half-done). "Choose one or two impactful improvements to your bot, and make them very well."
- Hiding last-minute changes from the main rivals (not scrimming them) left bugs that appeared only against those rivals undiscovered.

### 3 Musketeers, 2021 (9th; first year)

- Control flow: states switched in several places caused wasted turns and state stacks over 100 deep. Rewritten as one prioritised check at the start of the turn ("Can we do our first priority? If so, go into that state. If not, move on to priority number 2"), decided once and then executed.
- They copied formations from the top teams after the first sprint: "Whereas our bots were very individual and did what was best for them, the top teams had coordinated groups of units."
- Every unit reported enemies seen, and the team kept an average enemy direction: economic units stayed and spawned away from it, attackers answered attack calls towards it.
- Turn order as a weapon: units act in the order they were created, so a small unit built just before a big one acts just before it and clears the way.
- Opponent modelling: a binary search on bids converged on the opponent's average bid, then bid one more.
- Bugs were found by watching games frame by frame, "even in wins". "Read the specs again. and again, and again", and the full API.
- They quote XSquare (2020): "every time I'd try to implement a sophisticated strategy that requires a lot of coordination it would always flop since everything that can go wrong does go wrong. Usually the bots that perform the best are those that perform the basics really well (navigation, communication, micro, macro, etc.) ... It is usually more effective to spend your time on the basics and then figure out the optimal strategy depending on what other players do than trying to devise the optimal strategy from the go. Also, if the code undergoes drastic changes ... I would suggest to do a bot from scratch."

### Big Red Battlecode, 2019 (8th)

- The meta moved in steps: an early rush that beat everything; a rock-paper-scissors between three rushes and defences; after a rules patch, ranged lattices and economy; finally one dominant balanced strategy with small edges on top. The teams that had written economy bots from the start were a tier above those that switched late.
- "Prophet waves": units move towards the enemy in a line, in discrete waves, so that more of them fire at once and too few die on the way in to lose the exchange (the same idea as XSquare's synchronised attack and Just Woke Up's synchronised entry).
- smite's winning formation: a sparse, cheap defensive lattice that kept the economy strong and condensed into a dense one as soon as units saw enemies.
- Lessons: build a working, improvable bot fast; good infrastructure so parts can be swapped when the meta changes; "scrimmage and test constantly ... theorycrafting can only get you so far"; and reverse-engineer competitors: they rebuilt the leading rush bot from scrimmage observations and tested their defence against that copy locally, because ladder data alone is limited.

### confused, 2020 (high-school 2nd, 6th on the scrimmage ladder)

- In rush against rush it was better not to defend at all: defence spent resources that would otherwise go to offence, and a half-successful rush still left the defender's base hard to rebuild. They added a "rush cost" so offence always ranked first early.
- Coding a rush took an hour and lifted a team from about 40th to the top 10 within two hours: early ladders reward simple aggression until the counters appear.
- Do not scrim the team your new counter targets right before a deadline: the rival saw it and answered with a counter of its own just before the lock.
- Pathing was the cause of "virtually all of our losses"; workarounds that relied on other units (carrying lost units) failed exactly when they mattered.

### no thoughts head empty, 2023 (first year)

- Kiting rule written out: if an enemy is in reach at the start of the turn, shoot then move out of its vision; otherwise move, look again, then shoot.
- Map-size rules: on small maps, attackers go to the centre until map control; on big maps they stay home for the first 50 turns against rushes.
- "At the final tournament we found out that many top teams had built up custom systems for quickly running many matches in parallel for A/B testing"; they could not tell whether changes helped without long manual testing.

### Bowl of Chowder, 2020 (5th-6th; Stone Tao, solo)

Source: stonet2000.github.io/battlecode/2020.

- Build infrastructure that survives rebalances (pathing, communication, building), and do not switch metas too often.
- Test edge-case maps early.
- Time spent on a special counter (a drone-wall buster) would have been better spent tuning what already existed.
- Whether a rush succeeds depends on the map: a rush result on a few maps says little.

## 3. UNSW Battlecode 2026: teams that built their bots with AI agents

UNSW Battlecode 2026 (battlecode.au; toolkit github.com/unswcpmsoc/unswbc) was run by UNSW CPMSoc with Jump Trading and HRT as sponsors: sprint 10-01, qualifier 10-10, grand final 10-17 at UNSW Sydney. 973 teams from 41 countries entered; 591 played the sprint and about 1,000 were on the ladder. The grand final was won by "chad gdp" (no write-up found).

The game, "dragons": a torus board of 11 to 64 tiles a side, with kelp (a wall that kills) and portals. Each team controls up to 64 snake-like dragons. Pearl beds grow a pearl after a random countdown; eating one adds a segment; a dead dragon drops a pearl on every second segment. A dragon dies by entering kelp, its own body or another dragon's body, and two heads meeting kill both. From rules 1.2.3 a dragon of length L gets ceil(L/4) free steps per turn and each further step costs a segment. `SPLIT n` cuts the last n segments into a new dragon. Dragons act one at a time in id order, so later movers see earlier moves. Vision is a 7x7 window around the head. Each dragon is its own process with private memory (a split child starts with none), and the only channel between teammates is sonar: a 64-bit word sent in a straight line to the first living dragon it reaches, which an enemy can intercept. Each turn has a budget of 100M wasm CPU points. A game lasts at most 500 rounds and a team with no dragons loses; from 10-01 dragons 0 and 1 are queens, and at round 500 the longer queen wins (a dead queen counts as length 0), then the longest living dragon, then total length.

Why it matters to us: the problem has our shape (many units with private memory, a narrow channel between them, a CPU budget per turn in wasm, unseen tournament maps, a public ladder where opponents change daily), and unlike the MIT teams, several of these teams ran AI coding agents at scale, as we do. Their write-ups are the nearest thing to a postmortem of our own process.

### zitianqin (solo: sprint seed 13 of 591, ladder peak 6th; then merged into a team that went into the grand final as top seed, finished 3rd and won the award for the fastest algorithm)

Source: github.com/zitianqin/unsw-battlecode-2026 (README).

- Bot: C++ heuristics, no global search and no single evaluation function. Each dragon, each turn: (1) observe: update its view, merge teammates' sonar reports into a shared belief map, fill unseen cells by map symmetry; (2) pick a target, usually a pearl or spawn tile it reaches before any teammate, otherwise unexplored ground; (3) take forced moves first: ram an enemy head, sprint out of danger, split when a shorter enemy could ram it, feed a longer teammate late; (4) otherwise score each move for survival room and progress to the target, with "a short search for moves an enemy could punish"; (5) communicate.
- Scale: 523 experiments, 97 promoted champions, 1,275 ideas and over 740,000 games in 8 days on 15 machines.
- Ideas: a ranked backlog. "About 80-90% of the ideas that made the bot better were mine"; the rest came from replay audits, studies of top teams and post-mortems of failed experiments. A coding agent took one idea, implemented it with tests, and the diff was reviewed independently.
- Testing: paired, side-swapped SPRT against the current champion, on freshly generated maps, against rotating opponents; normalised Elo bounds 0 and +15, 5% error rates, up to 2,400 game pairs. "The bounds are fixed before a test starts and a separate judge reviews each result."
- Gates before promotion: CPU limits on the 99th percentile and on the maximum time per turn, passing tests, and a screen against frozen opponent bots. Winners were uploaded automatically; each loser got a post-mortem that queued a corrected idea; idle machines tuned parameters, swept variants and searched for maps the bot loses on. A native judge produced replays byte-identical to the official engine's with a third less CPU.
- Regrets: no refactoring ("the code grew by accretion"); the agents shaped the architecture because the author did not set module boundaries early; no routine simplification pass. Advice: set the architecture yourself early, refactor at quiet points, make simplification part of every review.

### juntegral, team "meow" (ladder 32nd when the team formed, peak 23rd, 41st at the deadline; seeded 39th; out in the knockout on 10-10)

Source: github.com/juntegral/unsw-battlecode-portfolio. Most code and analysis came from Claude Code sessions and Codex workers; the author designed the operation (who decides, who analyses, how briefs are written, how reports are checked, how sessions hand over).

- The card loop: each idea is a GitHub issue whose state is one label, and a runner calls an AI only when a card needs work. Steps: clarify with the author; build behind a compile-time switch that is off by default; prove the all-off build is byte-identical to the previous program; the author reviews selected replays; outcome test; written verdict; candidate pull request. "People approve; the loop never uploads." The byte-identical rule allowed 21 live versions in 16 hours without a crash or a timeout. The final bot was one C++ file of 8,657 lines plus a profile of 49 switch values.
- Twelve times a confident agent report turned out wrong, and each case added a check. Six successive lead sessions, with standing rules each tied to an incident.
- What went wrong:
  - "Structured testing on unseen-style maps came 13 hours before the deadline", and it showed the live version losing to an older bot on new maps.
  - Versions were judged on 15-game online sets: the same bot scored 8/15, then 4/15 two hours later.
  - Two harmful switches stayed live for 3 to 4.5 hours because versions were compared by overall wins, not map by map.
  - The largest class of losses, falling behind in unit count in the first 150 rounds, "never got a fix".
  - "Ranked games requested in the last hour to improve the seed cost rating instead."

### Team 777 (coleseven, solo; rank 153 of 1,001 on 10-12, rating 1604, when rank 100 was 1813)

Source: github.com/coleseven/unsw-battlebot-research.

- Python heuristics, a learned linear ranker for moves, a C++ port, CMA-ES tuning of parameters, and queen tactics.
- Versions were judged on large batches with intervals: v12z won 741 of 1,224 games against 671 for v12x, +5.7 percentage points with interval [+2.4, +9.1]; then a head-to-head check (91 of 136 games over 17 maps, both sides, four fresh seeds). Their caution: these are local results, not estimated ladder gains, and a single-seed replay is not evidence of strength.

### UnderTheC (four members; best ladder rank 16 at 2139; sprint: lost 3-4 in the round of 16)

Source: eight posts at battlecode-underthec.github.io (2026-10-11). The project was "vibe coded": LLM agents wrote the bots, simulators, league, arena, scalers and scripts.

- Post 0, why LLMs: the team came from NYPC (Nexon's programming competition), whose AI-battle track was won with reinforcement learning and whose rules ban "calling LLMs en masse in an automated manner". "If a competition bothers to ban that, it probably works."
- Post 1, reinforcement learning abandoned. Four GPUs and a vectorised C++ simulator (7.7M dragon-turns per second on 14 cores, up from about 20k) went mostly into making training fit; the 2.7 MB of weights first blew the CPU budget, and a decision still cost about 23M of the 100M points; a ram reward of 0.3 taught the policy to spend its dragons ramming. The policy was never evaluated against outside bots. A scripted bot written in under five hours went 10-0-12 on the official maps, and after a few changes beat the RL policy 79-1-0 on 40 training maps (both sides) and 22-0-0 on the 11 official maps.
- Post 2, mass code generation: hundreds of LLM-written variants ranked by a local league instead of one trained bot. "Throwing more tokens at the problem does win": the rating rose roughly linearly with tokens spent. The largest single step was building on a teammate's bot; lines climbed by single-change iterations, each beating its parent.
- Post 3, the arena. Principle: "the official engine is the only judge". A C++ port of the judge's glue was used only where it gave byte-identical replays, and 1 game in 50 ran on both judges ("All 4,535 spot checks matched"); their earlier fast simulator "had also disagreed with the official judge". A draft played its parent and the current top 3 from both seats on several suites: official maps, tournament maps rebuilt from replays, a server suite with the first two seeds the server used on each map, weekly generated maps, "trick" maps, and a hidden holdout; duels used fresh seeds. 291,668 games over 680 submissions by 10-09. Auto-submit gate: #1 on the arena, at least 55% of at least 60 games against the live bot, holds on the holdout and server suites, under 70M CPU points at the 99th percentile, at most one upload per 4 hours. "Local wins aren't server wins."
- Post 4, the metrics engine. Replays decoded every 10 rounds into per-team metrics, and a logistic model of P(win) from five differences: log dragon count, board control (the share of tiles our heads reach before the enemy's), longest dragon, queen alive, and a round-500 leader term. Board control and dragon count predicted best from round 50 to 350 (AUC 0.80-0.84); "kills predicted nothing on their own". 150 of 287 server losses (52%) were already decided by round 60 (P(win) below 0.5): board control of 0.2-0.3 at round 60 won 32% of games, 0.7-0.8 won 90%. Top teams lost their queens more often yet won 53% of those games (UnderTheC 23%), because by round 300 they had far more total length. Before round 300 UnderTheC lost 171 dragons to self-inflicted deaths, top teams 113. In 69 of 75 losses where the queen died head-on, P(win) was already below 0.35 before: the visible cause of a loss was often a symptom.
- Post 5, the LLM loop. An orchestrator (one long Claude Code session that launched agents, checked their numbers, kept a `KNOWLEDGE.md` and handled submissions) was not allowed to design strategy, because a single view "narrows the search and carries its mistakes through whole generations". Read-only analysts diagnosed losses from replays into a ranked report; 2-3 strategists per round proposed ranked single changes, each with evidence, a base bot and a success test, and wrote no code; workers each made one change to one bot ("Don't sweep parameters or bundle a second idea"). Noise: 78 games is about +-9 wins, so 38-40 or 41-37 is a tie and calls for more games. Rules added after failures: no map hardcoding (every new threshold names the observed cause it responds to); the full brief at launch and no steering of running analysts (the orchestrator's messages had made them confirm its own conclusions); no unrequested builds; line names describe the mechanism; give an idea 2-3 tries if its target moves, because single noisy pass/fail verdicts threw away partial successes; build on the best bot and add one radical behaviour, no bots from scratch. In one round about 15 verdicts landed inside noise, and one line climbed through "three promotions that are all inside noise".
- Post 6, what the factory made. The biggest server gain came from a teammate's hand-designed idea (park the queen in a ring and grow her late), not from the search. Arena leaders failed on the server: a depth-8 lookahead line scored 62.2% in the local round-robin and beat the live bot 184-115 on unseen seeds, then went 0-5 in its first server battle; a queen-guard line was #1 on the arena and went 60-0-73 on the server. "The arena overrated what it was fitted to." A race to the centre bed cluster gained on the server but lost 64-96 on 40 fresh anti-centre maps. Top teams farmed the best beds with a tip split ("150 to 6" on one map) and won on mid-game army rather than queen safety. Consistent findings: economy before round 300 decides games; "consolidation never paid"; many short dragons early beat fewer long ones.
- Post 7, results and what they would change. Their ladder rating sat about 90 above their rating-adjusted performance. Where local testing misled: the arena used two fixed seeds per map and their own bots as opponents, which "rewards beating our own habits"; "A/B tests against our own parents couldn't see these weaknesses at all", so they added clones of real opponents. The gap to the top was always economy before round 300: their heads covered 23% of the board by round 100, the lowest of 17 teams measured. Long-running workers drifted; bundled merges mixed effects; replays were once reviewed with the sides swapped (identify your own side by your own messages, never by name); Apple clang's FMA contraction made native builds diverge from the wasm judge until `-ffp-contract=off`. What they would change: judge on the server per map, rating-adjusted, from day one; use the arena only as a filter; test openings on generated map families.

### What UNSW adds to the MIT postmortems

- The ideas that moved the rating most came from people: 80-90% of zitianqin's kept ideas were his own, and UnderTheC's best line was a teammate's design. Agents were strong at building and testing one change at a time, and weak at choosing what to change.
- The failures of agent-driven teams repeat: verdicts on small or noisy sets (15 games; 78 games is +-9 wins), versions judged by overall wins instead of per map, an opponent pool made of one's own bots, a local judge that overrates what it was fitted to, unseen-map testing left to the end, drifting long runs, bundled changes, and confident agent reports that were wrong.
- What worked: fixed statistical rules decided before the test (SPRT with bounds), side-swapped pairs on fresh generated maps, clones of real opponents, a holdout, the official engine (or a byte-identical port) as the only judge, CPU gates at the 99th percentile, default-off switches with a byte-identical all-off build, and humans approving every upload.
- Where games are decided: early. 52% of UnderTheC's losses were decided by round 60 and their gap was always economy before round 300; juntegral's largest loss class was unit count in the first 150 rounds; kills alone predicted nothing, material did.

## 4. Other bot-programming competitions

Battlecode is one of a family of contests where a program plays a game against other programs: the Google AI Challenge (Planet Wars 2010, Ants 2011), Two Sigma's Halite (2016-2020), the Russian AI Cup (yearly since 2012), CodinGame's seasonal challenges, Kaggle's Lux AI. The games differ; the methods of the winners repeat.

### Russian AI Cup 2016, CodeWizards (a simplified DotA): DragoonXen, 2nd in the final

Source: habr.com/en/articles/318878 (in Russian). The closest game to ours: five wizards per side, three lanes, minions, towers, skills with cooldowns and mana, level-ups, bonuses on the map; in the final one program controlled all five wizards. About 10 ms per tick.

- Movement by a grid of scores around the wizard: each cell holds usefulness minus danger, with separate danger terms for minions, wizards and buildings, the best attack zone, zones around wounded enemies (worth experience), and hand-set terms for special cases (bonuses, spawn zones, forest, corners). The wizard walks to the best cell by a path search whose edge cost is danger, not distance.
- An enemy wizard's danger zone depends on its facing, its cooldowns, its mana and mana regeneration, so the bot knows when an enemy cannot attack and may be approached. Minion danger was split into the zone the minion attacks and the zone where it would choose to attack the wizard; this stopped the bot circling behind minions.
- Projectiles are dodged by simulation: expected damage standing still, then sideways or backward moves at the speed for that direction, then full-speed moves in every direction, keeping the least damage. Aim at the target and at a point slightly ahead, so that fleeing forward and backward cost the same.
- Targets by remaining health share, with wizards and towers weighted 5-6 times minions; fast or hasted wizards are not chased.
- Danger mode: two enemy wizards and no ally near rotates the search grid to look further behind than ahead.
- Focus fire in the final: wizards within about 350 px of their mean form a cluster; a cluster of more than two looks for an isolated enemy within about 900 px without tower or ally cover and charges it together. A small penalty for standing next to an ally (ignored in danger) and a pull towards allies within 600 px kept the group together without stacking. Attack the enemy base only with a clear numbers advantage, or after one of its second towers falls.
- Specific counters: against teams that marched all five wizards into the first tower, ignore that tower's danger and rush in to split them; a counter for one named opponent's weak micro. Each was tested locally against the previous version, then live against the teams it targeted.
- Process: a local runner for thousands of version comparisons, a visualiser to inspect single fights (which found bugs the numbers missed: a dodge check that failed in open terrain went unseen for a week), a profiler (the per-cell scoring was the hot spot). Fixed late bugs: a broken self-haste that ruined 1v2 dodging; a cluster that did not form when one wizard was far away; a final submission whose wizards learned no skills.

### Google AI Challenge 2011, Ants: xathis (1st)

Sources: LessWrong's "AI Challenge: Ants post mortem" and its comments (xathis's own page was unreachable). The final playoff had 100 bots.

- xathis held first place for almost the whole contest with his first version. In his words every move "depends entirely on the local environment of the ant": no global ant counts, no change of play when winning or losing.
- Combat: list every local fight so that the search runs on small groups, then a min-max over the moves of the ants in that fight with heavy heuristic pruning. A competitor called the result "a lot of little pieces done well" rather than a few overarching principles.
- The same competitor's mistakes: too much time fine-tuning doomed approaches; an untested assumption that he could not afford as many local searches as xathis; and, his biggest, searching for "the Deep Underlying Principle" so that the right behaviour would emerge, instead of writing code that directly did what he wanted.

### Halite II and III (Two Sigma)

- Halite II (2017-18, about 6,000 players) was won by reCurse; ships fought automatically (damage to the enemies in range each turn, no attack command), so grouping and numbers decided fights. No write-up by the winner was found.
- Halite III (2018-19), Stone Tao (#66 overall, #5 of high-school players): keep it simple; his more sophisticated mining score did worse than his simple one; a local match runner with sides switched, because results differed even without randomness; parameters tuned by self-play; credits reCurse's (3rd) "Battlestation" workflow and models of the game as the edge he lacked.

### CodinGame challenges: reCurse (1st Fall 2023, 1st Winter 2024, 2nd Summer 2024)

Sources: three post-mortem gists by reCurs3 (github.com/reCurs3). CodinGame games are small, fully specified and simulated cheaply, which is why learning works there.

- Methods: a policy network trained by PPO in self-play (Fall 2023, no search at all); the same plus a shallow alpha-beta search with the policy giving the top 4 moves per player (Winter 2024, 50 ms per turn); a policy and value network inside a simultaneous-move MCTS (Summer 2024), because "even a very good policy network could not be as competitive on its own anymore".
- A multi-threaded C++ referee linked to the bot, validated against the official one: cumbersome but "100% worth it".
- The near-failure of the winning 2023 bot was overfitting: self-play against only the current network, without a league of past opponents. "Don't be dumb and always respect overfitting."
- "Most games are effectively decided by turn 10 at most." "I cannot emphasize enough the importance of local testing." Noise added to the search policy was "always worse" locally but helped on the leaderboard: the local arena and the ladder disagree even for the best.

### What these add

- The MOBA bot (CodeWizards) solved our exact problem with a scored grid of positions whose danger terms read enemy cooldowns, facing and mana; with grouped focus fire on isolated enemies; and with a numbers rule for attacking. That is XSquare's per-square micro and the "aggressive with numbers" rule from the Battlecode postmortems, found independently.
- Search pays where the game can be simulated cheaply and exactly (Ants combat on small groups, CodinGame); elsewhere the winners use scored candidate moves plus a little lookahead for punishable moves (zitianqin).
- Learning needs a simulator, compute and a league of diverse opponents; without them (UnderTheC) a hand-written bot wins in hours.
- Everyone validates the local judge against the official one, tests against many opponents rather than only the previous version, and inspects single fights visually.

## 5. What the sources agree on

The games change every year; the habits of the teams at the top do not. Each point below is held by several sources independently; the names in brackets say where to read more (sections 2-4).

### 5.1 Process: where the time goes

- **Know the rules, then do the arithmetic.** List the resources, their exchange rates and the forced trades before tuning anything (wololo; The Kragle's cost table, which showed that an obvious upgrade was never worth it; 3 Musketeers: "Read the specs again. and again, and again"). What can be computed is computed, not tuned (wololo's empower radius).
- **Robust primitives first, reused where possible.** Pathing, communication, micro and a test runner come before strategy, and the public ones (XSquare's bug navigation and micro) are taken rather than rewritten (XSquare, The Kragle, Generalized Stroke's Theorem, Bowl of Chowder). When the strategy changes, rewrite rather than patch (XSquare, 3 Musketeers).
- **Copy what better teams do, then improve it.** Macro is visible in replays and everyone at the top copies it (Java Best Waifu: "all top teams copy"; The High Ground: "the most tried and true strategy in Battlecode"; Generalized Stroke's Theorem; The Kragle: "Other teams beat your bot for a reason"; Lorem Ipsum's carry limit). A copy that is not improved stays behind the original (don't @ me).
- **Prioritise.** Keep a ranked list of flaws and do the one with the largest expected gain first; between qualifying and the deadline, one or two improvements done well (The High Ground). Time spent on rare cases did not pay (Bowl of Chowder's special counter, The Kragle's "survive" behaviour).
- **Watch games, unit by unit.** The habit named most often: follow single units into lost fights and fix each wrong decision with the least effect on the others (Generalized Stroke's Theorem: "far more time reviewing scrims than actually writing code"; food; 3 Musketeers, frame by frame "even in wins"; smite traced every late loss to a bug; Om Nom found "obvious things"; DragoonXen's visualiser found a dodge bug that the numbers had hidden for a week).
- **People choose, tools execute.** In the UNSW teams that ran AI agents at scale, the changes that moved the rating were people's ideas; the agents built and tested single changes well and chose what to change badly (zitianqin, UnderTheC, juntegral).

### 5.2 Micro: how fights are won

- **Score every square the unit can end on, and compare squares with ordered tie-breakers.** XSquare's `doMicro` / `computeMicroArray` / `isBetterThan` is the shared core (Java Best Waifu; Cout for Clout's switch from if-chains, about 1850 to 1950 rating and then past 2000; Generalized Stroke's Theorem; food; The Kragle). DragoonXen's CodeWizards grid is the same idea found independently, with danger terms that read the enemies' cooldowns, facing and mana.
- **Ready and not ready.** Ready: attack from the square with the fewest enemies able to answer. Not ready: a square no enemy can reach (XSquare; 4 Musketeers). Attack, then step back, so that the enemy must step in and give the first shot back (Gone Fishin': "ALWAYS kiting back after an attack is better"; don't @ me; no thoughts head empty). "The first to move in range of the opponent dies" (smite).
- **Numbers decide, so arrive together.** Lanchester's square law is cited by name (Cout for Clout) and applied by every finalist that describes its fights: synchronised entry (Just Woke Up, XSquare 2019, Big Red's prophet waves), squads sent to one combat location (Cout for Clout), each unit following the first ally that moved (don't @ me, after "losing early 3v3 duels left and right"), clusters charging an isolated enemy (DragoonXen). Aggression follows the numbers: "aggressively when you have the numbers advantage or good positioning, and passive otherwise" (food); DragoonXen attacks a base only with a clear numbers advantage; 4 Musketeers back off when outnumbered.
- **Targets:** the lowest-health enemy in reach, attacking whenever possible (XSquare, as The Kragle quotes him); finishing blows first, because a dead enemy does not attack next turn (food); a value with a kill bonus (don't @ me, 5 Musketeers).
- **Trades are counted.** Attack only when what the attack removes exceeds what the attacker spends (XSquare 2021); price a trap or a unit by what it trades (food).
- **Healing and retreat must not starve the fight.** Fall back when healing is fast (don't @ me), but a heal queue that keeps units at home loses the fight they left (5 Musketeers); hurt units retreat and return together (4 Musketeers); the lower-health unit stands behind (Gone Fishin').

### 5.3 Macro: the economy decides early

- Games snowball, and the side ahead early usually wins: "any small resource lead can very quickly turn into a large advantage" (The Kragle); the opening launcher duel decided the match (don't @ me); so did the first second base (food); do not overspend the CPU budget on the first turns (Om Nom); 52% of UnderTheC's losses were decided by round 60, always by economy before round 300; juntegral's largest loss class was unit count in the first 150 rounds; "decided by turn 10 at most" (reCurse).
- Leads are thrown by idle units and floating resources (The Kragle) and by units that die alone (Lorem Ipsum removed the roles that kept ending in 1v3 fights).
- The balance between economy and fighting depends on the map: size, distances, neutral threats. Tournament maps tend to be larger and slower than the ladder's (XSquare 2021, The Kragle), and one fixed count is wrong on some maps (food). Neutral units cannot be ignored (The High Ground went out on cow maps), but in micro enemies come before neutral threats (Generalized Stroke's Theorem).
- The meta moves (Big Red, XSquare 2019, 5 Musketeers after a patch): keep playing the top teams up to the deadline.

### 5.4 Engineering

- One decision point per turn: sense, choose a state from what is seen and the previous state, act (don't @ me, 5 Musketeers, 3 Musketeers, Just Woke Up's `determineState`, Generalized Stroke's Theorem's behaviours, The Kragle's goals with `shouldStart`, `execute` and `shouldStop`). State switched in several places wastes turns and builds deep stacks.
- Stay inside the CPU budget, above all early (Om Nom); cheap pathing (bit-shifted BFS, bug navigation).
- Infer hidden information from what is visible (Om Nom: the tower count from income; XSquare 2021: the unit type from maximum health), and share what decides fights (Generalized Stroke's Theorem: health and nearest enemy, every turn).
- General code beats map-specific code at the tournament (don't @ me: "Code > Elo"; Gone Fishin' lost the final on a map-specific bet).

### 5.5 Testing

- Every change is played against older versions on all maps, both sides, in parallel (Cout for Clout, Just Woke Up, 5 Musketeers' spreadsheet of every change against every version on every map; no thoughts head empty found at the final that all top teams had such a runner), and against the strong teams' real bots (Just Woke Up's automated scrims, don't @ me's ten-game sets). Self-play alone overfits (food; reCurse's league of past opponents; the UNSW teams whose pool held only their own bots).
- The statistics are fixed before the test: sequential tests with bounds, side-swapped pairs on fresh maps, a holdout (UNSW). Small sets lie: 78 games is about +-9 wins (UnderTheC); three games say little (don't @ me).
- A behaviour is tested first on the 3-5 maps built to show it, watching the replays; 20-30 maps at once hide why (food). Edge-case maps early (Bowl of Chowder).
- No untested or last-minute uploads before a deadline (XSquare, The Kragle); do not show a rival the counter aimed at it just before the lock (confused 2020).

## 6. What this means for our game

### 6.1 What we already do

- Platform tests against the real opponents: gates on panels of (opponent, map) pairs, pinned to the bots the opponents played earlier (`cambc match-groups create TEAM --source-group`, `docs/WORKFLOW.md`), with the base run in the same session, the decision rule written before the result, one change at a time, and metrics from decoded replays. That is the UNSW list, without its self-play pool.
- Local games run on the official engine (`cambc run-batch`, version pinned in `cambc.toml`), so a ported judge cannot disagree with the platform. The local pool is our own past bots, which the sources warn about; our rules already count local runs as crash and breakage checks, not as verdicts on fights.
- We copied measured habits of the top teams (findings: the lowest-health target in reach, a chase of 3 turns at most, recall at about 46% health), the turn order in contact (go1, `set_priority`), and enemy bags in the target value (`knowledge.h`).

### 6.2 Where we depart from them

1. **We read counts more than fights.** Our verdicts come from decoded metrics, as theirs partly do, but their strongest single habit is following units through lost fights and fixing each wrong decision. The tools exist (`cambc view`, `tools/replay/vis_assets.py`, the death traces in findings): before a fight change, read the lost fights it targets one by one, and after it, the same fights again.
2. **Our fight code is a rule tree, the structure the sources moved away from.** The threat branch, `simulate_fight` and hand rules decide our fights; the sources' answer is a per-tile evaluator with ordered comparisons. Our measured gap is what that evaluator addresses: the rivals have 31.2 rounds a game with two or more of them hitting champions against our 16.9 (findings, "Against teams 34-60 we lose the group fights"), and 53% of our deaths had a stun on the victim in its last 6 rounds against 31% of theirs (b19; findings, "Shots, spells and stuns from beyond our reach"; 49% against 32% on 10-27's panels). The per-tile `micro.h` of `docs/STRATEGY.md` section 4, with danger terms from live enemy cooldowns (the reach table, STRATEGY 2.8) and a rule to arrive together, is that answer. It waits for the user's go.
3. **We tuned against gaps before doing the arithmetic.** `docs/STRATEGY.md` 2.8-2.12 now holds the exchange rates: reach, time to kill, camp yield per champion-round, tribute.
4. **The economy decides early, and early is where we trail on the bad maps.** On brkp our team gold at r100 was 238 against 345, and 49 of that gap of 107 was kill gold (findings, "Early gold, strong camps tanked alone"); on the normal panels we are level by r300 (findings, "Gems per camp hp"), and the collection gap left is gem clusters on 5-champion maps.
5. **One lever in the rules is unused: the 1024-byte draft memory.** The draft bot sees the whole map and its first turn has 100 times the fuel, so a map analysis (group values, routes, altars, choke points) can be computed once there and read by every champion all game, instead of in the opening turns, where fuel runs short (in the platform games of 10-25, 5-7 of each game's fuel exhaustions came in rounds 1-3; findings, "Code audit with check builds").
6. **Priorities before the lock.** One or two improvements done well, nothing untested before a deadline. Sprint 3 locks Sat 31 Oct 23:59 GMT (Sun 1 Nov 05:29 IST); `bots/main` must be the submitted bot then.
