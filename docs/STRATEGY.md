# Strategy from first principles

Written 2026-10-29 (evening IST) after the user asked (10-29) to stop tuning metric gaps one at a time and to study how strong Battlecode teams think, and what this game rewards, before changing the bot. Sources: the rules (`docs/MECHANICS.md`, engine 2.0.0), our decoded measurements (`docs/findings.md`), and the postmortems and write-ups summarised in `docs/STUDY.md` (MIT Battlecode 2019-2026, UNSW Battlecode 2026, other bot-programming contests). Sections 2.8-2.12 (added 10-29 evening) derives numbers from the rules; they are computed, not measured. The public Cambridge 2026 repositories on GitHub (seven found on 10-29) belong to weak teams (the most developed one reports wins against the starter bot only), so the only window on how the top teams of this game play is their replays, which we already decode.

## 1. How strong Battlecode teams work

The postmortems agree on a short list. None of them is about one metric.

1. **Micro is a per-tile evaluation, not a chain of if statements.** Cout for Clout started with "lots of if statements and a combat BFS"; it became "too complicated to modify". They copied XSquare's framework: for every tile the unit could end on, compute a few numbers (damage it can deal from there, damage it can take there, distance to allies and targets), compare the tiles with one fixed rule, and move to the best. That single change took them from about 1850 to 1950 rating and then past 2000. SPAARK (2025) did the same, with every resource converted to one score and both orders (move then attack, attack then move) tried.
2. **Bucket the behaviour by cooldowns and ranges.** XSquare's rule: if your attack is ready, go to the best tile from which you can hit with the fewest enemies able to hit you back; if it is not ready, go to the best tile that no enemy can hit. 4 Musketeers wrote the same as four rules: outnumbered or very low, back off (attack first if possible); ready and in range, attack then back off; ready and out of range, step in and attack; hurt allies, retreat and heal together, then return together.
3. **Fight as a group (Lanchester's square law).** With aimed fire, a side's fighting strength grows with the square of its numbers times the quality of each unit, so one extra unit is worth far more to the larger side. Cout for Clout sent units to "combat locations" so that they arrived together instead of one by one, and moved towards hurt, stunned and low-health allies. Their sitting-duck test (three units guarding home against two) lost 90% of games because it took two units out of the fight.
4. **Copy the macro of the top teams, often.** XSquare: "all top teams copy". Macro (what to farm, when to bank, what to buy, what to draft) is visible in replays and cheap to copy; micro and infrastructure are where a team's own work pays.
5. **Simple, robust primitives first:** pathing, communication, micro, testing. Approximate global coordination with identical local rules on each unit, because units do not share one brain.
6. **Test against older versions on many maps and both sides; watch replays and think.** Do not discard an upgrade that sits near 50% too fast, and do not make last-minute changes before a lock.

## 2. What this game rewards (derived from the rules)

### 2.1 Gold compounds, gems only score

- Gems are the score and do nothing until tributed. Gold is the only source of power: there is no passive income and no assist gold, every shard (30 gold) is one growth step of a stat, and a champion that does not capture stays at base stats.
- Power raises the farming rate (damage per hit on camps) and the fight rate. So gold grows like interest: an early lead compounds. Measured: the top 12 collect as many gems as we do by r300 with about 40% more team gold, and the gap opens in the first 100 rounds (findings, "The gold gap is items held and starts in the opening").
- Consequence: in the opening, rank targets by gold and safety (wolves, gold clusters), not by gems. Gems are collected later at a higher rate by stronger champions.

### 2.2 What one death costs

A top-12 team of five earns about 4.7 camp gold and 0.57 gems per round by r300, about 0.9 gold and 0.11 gems per champion-round (findings, b9 and top 12). One death costs the victim's team:

- 60 rounds of that champion's farming: about 55 gold and 7 gems;
- the whole bag, which goes to the killer (average bags are 33-39 gems at tribute time);
- 100 gold to the killer's team (150 with a Hunter emblem).

The swing is about 155 gold plus 40 gems, which is about 33 rounds of a whole team's gold income. A kill is the single largest event in the economy. Any rule that trades a 10% higher farming rate for one extra death per game loses.

### 2.3 Stuns are the strongest effect in fights

- A stun removes the target's next turn: no move, no attack, no cast, and it breaks a tribute or recall channel. At base stats a champion focused by three enemies dies in about 4-7 rounds (2.9; measured deaths bleed over about 13-16 rounds, findings "PvP"), so one stun removes one of its last 4-7 turns and, more importantly, pins it inside the attackers' reach for one more round of their hits (about 150-240 damage from three attackers at base stats).
- Every stun is on an 8-turn cooldown, and **enemy cooldowns are readable** (`docs/MECHANICS.md`, section 5). So each side knows exactly when the other's stuns are spent.
- Stunners: Heart of Ruin (dash landing, radius 1), Marcella (enhanced attack), Ryth (area radius 1, roots), Ren, Tavi, Prism (single target, range 4, roots), Cassi (no damage). The top-20 draft (Marcella, Heart of Ruin, Vendetta, Vesper, Ryth) fields three stunners, one of them an area stun. Ours (Varg in place of Ryth) fields two.
- Measured: they stun us 20.6 times per game and we stun them 7.2; 53% of our deaths had a stun on the victim in its last 6 rounds (findings, "Shots, spells and stuns from beyond our reach").
- Consequence: **the engage window is when the enemy's stuns are spent and ours are ready**, and the danger window is the reverse. A ready stunner reaches 4 or 5 tiles with one turn (Ryth's area stun 5, Cassi 5 after a walk, Heart of Ruin 4 with a walk and the dash, Prism, Ren and Tavi 4, Marcella 2) and one more when it gets two turns before our next one (Ren three more: walk and dash, then the stun at 7). Table in 2.8.

### 2.4 Tempo: who acts first, and double moves

- Teams alternate one champion at a time, and the starting team swaps every round. Within a team, `set_priority` sets the order from the next round.
- So between two of our turns an enemy can act twice (end of round N, start of round N+1). Which enemy gets two actions on which of our champions is known in advance from the round parity and the two teams' orders (`docs/MECHANICS.md`, section 2).
- Measured on pairs of champions: acting first within 3 tiles gains about 26 net hits per 100 pair-rounds at distance 1 (findings, "Turn order"). The top teams act first in contact and put hurt champions first.
- Consequence: the threat on a tile is not "what can hit me once" but "what can hit me in the actions the enemy gets before my next turn", which is one or two per enemy depending on order. A per-tile evaluator can count this exactly.

### 2.5 Information is local; coordination must come from identical rules

- Vision is not shared, and shared memory is 8 bytes (all used: claims, help call, respawn broadcast, focus call; `docs/ARCHITECTURE.md`).
- So a team "plan" cannot be broadcast in detail. Group behaviour has to emerge from every champion running the same local rules that make them converge: move towards allies in or near fights, towards hurt and stunned allies, towards the lowest-health enemy that allies can also reach.

### 2.6 Camps are free damage on whoever stands nearest

- Camps never move or chase, sleep until hit, then hit the nearest champion every round. A woken group next to a teammate gets the teammate hit; a camp at reach 3 cannot touch a caster at 4 (wolves and clusters only).
- In fights near camps, the tile choice decides who the camps hit. A per-tile evaluator should count camp damage on each tile the same way it counts champion damage.

### 2.7 The map decides how much contact there is

- Whole-map gem income runs from 1.2 to 15.7 gems per round (`docs/MECHANICS.md`, section 15); on gem-poor maps the tiebreak (tributed gems, then gold earned) decides.
- Our ranked win rate rises with the spawn-to-spawn walk and falls with strong camps per tile (findings, "Why we lose"): our bot does well when it can avoid fights and badly when the map forces them. The top 20 draft the same champions on every map and win equally on our bad and good maps. So the bad maps are bad for our fighting, not harder maps.

### 2.8 Reach: who can hit whom before our next turn

Derived from the turn rules (`docs/MECHANICS.md` sections 3 and 6): one walk, one basic attack and one cast per turn; a ranged champion's walk spends its shot unless an attack reset follows the walk; dash then shot and shot then dash both work; a rooting spell allows no walk in its turn; spells reach 4 and area spells 5; each slot once per 8 turns. Distances are Chebyshev, on open ground, to a target that does not move. R1 is the largest distance at which the champion can deal damage (or stun) with one turn, R2 with two turns in a row. Burst is the most damage on one target in one turn with everything ready; the last column is the damage per turn over an 8-turn cycle in reach of one target (8 basic hits, one more per reset, each damaging spell once). All at base stats, engine 2.0.0. Computed 10-29 by a scratch script from these rules, not measured.

| Champion | Damage R1 | Damage R2 | Stun R1 | Stun R2 | Burst | Damage per turn |
|---|---|---|---|---|---|---|
| Ryth | 5 (area) | 6 | 5 | 6 | 145 | 63 |
| Vesper Vale | 5 (dash, then shot) | 7 | - | - | 90 | 51 |
| Vendetta | 4 (walk, dash, hit) | 5 | - | - | 140 | 79 |
| Cassi | 4 (spell) | 5 | 5 (walk, then stun) | 6 | 230 | 55 |
| Issac | 4 (walk, dash, hit) | 5 | - | - | 90 | 51 |
| Stellar | 5 (area) | 6 | - | - | 170 | 60 |
| Prism | 5 (area) | 6 | 4 | 5 | 155 | 60 |
| Marcella | 4 (spell) | 5 | 2 (walk, enhanced hit) | 3 | 165 | 66 |
| Willow | 4 (walk, reset, shot) | 5 | - | - | 110 | 62 |
| Ren | 4 | 7 (walk and dash, then the spell) | 4 | 7 | 145 | 49 |
| Varg | 2 (plus splash radius 1) | 3 | - | - | 90 | 51 |
| Tavi | 4 | 5 | 4 | 5 | 221 | 73 |
| Heart of Ruin | 4 (walk, dash landing) | 5 | 4 | 5 | 180 | 49 (up to 1.5 times when hurt) |

What follows:

- Against the meta draft (Marcella, Heart of Ruin, Vendetta, Vesper, Ryth) every enemy threatens 4-5 tiles with one turn and 5-7 with two. A tile out of all their reach is 6-8 tiles away, outside the fight. Avoiding reach is not a fight plan (rz3's 4-5 tile berth from ready shooters cost 2.2 deaths per game locally); a fight is an exchange, decided by how many hitters each side brings into the same rounds (2.9).
- Which enemy gets two turns follows from the order. With one champion per team in turn and the starting team swapping every round, the enemy at the same rank as ours acts twice between two of our turns in one parity and not at all in the other; every other enemy acts once (equal team sizes). Teams change ranks with `set_priority`, from the next round.
- A stun landed right after our turn removes our next one, so the stunner's team gets a whole extra round of actions on the victim.

### 2.9 How fast champions die: numbers first, then items

- At base stats a champion deals 49-79 damage per turn (2.8) and has 600-1200 health. One attacker needs 13-20 turns to kill a 1000-health champion, two need 6-10, three 4-7. A champion caught by three dies before its own damage matters.
- Lanchester's square law for aimed fire: a side's strength is its number squared times the damage and health of each unit. Five against four is 25 against 16, and the five win with about three left; three against two leave about two. One more champion in the fight weighs more than any item.
- Items scale both factors. A shard adds one growth step, about 10% of base health or strength. With 15 shards (the rivals' count per champion by r500) health and damage are each about 1.6-1.8 times base and the power of one champion about 3 times. A 40% shard lead is about 1.4 to 1 in power at equal numbers (findings, "Early gold, strong camps tanked alone").
- So the order of what wins a fight is: numbers in the same rounds, then items, then micro. Our measured gap is the first: rounds with two or more of a side hitting champions, 31.2 per game for them against our 16.9; with three or more enemies and two or more allies within 6, our chance of dying within 5 rounds is 0.107 per round against their 0.019 (findings, "Against teams 34-60 we lose the group fights").

### 2.10 What camps are worth per champion-round

Derived from the camp table (`docs/MECHANICS.md` section 7) for one camp of each kind: kill time = health / (k champions x damage per champion-round), damage taken = kill time x the camp's strength (the nearest champion takes every hit), plus the 5-round capture for every champion present. Base damage is 60 per champion-round (2.8).

| Camp | k | Rounds to kill | Damage taken | Gold per champion-round | Gems per champion-round |
|---|---|---|---|---|---|
| Gem cluster (120 health, harmless) | 1 | 2 | 0 | 0 | 1.00 |
| Gold cluster (120, harmless) | 1 | 2 | 0 | 2.86 | 0 |
| Wolf (1350, 20 a round, reach 3) | 1-2 | 11-23 | 225-450 | 1.2-1.5 | 0.12-0.15 |
| Elk (2400, 60, reach 4) | 3 | 13 | 800 | 1.64 | 0.27 |
| Golem (5000, 120, reach 4) | 5 | 17 | 2000 | 1.48 | 0.33 |
| Monolith (20000, 200, reach 5) | 5 | 67 | 13300 | 0.84 | 0.56 |

At about 150 damage per champion-round (the shard counts of r600) the strong camps double their yield: an elk with three 2.9 gold and 0.48 gems per champion-round, a golem with five 2.7 and 0.62, a monolith with five 1.9 and 1.26.

- Clusters give the most gems per champion-round at every stage and cost no health. The 5-round capture is most of their cost, so they want one champion per cluster group: a second champion nearly halves the yield (0.58). The Capture emblem cuts the capture to 3 rounds.
- Wolves give the fewest gems per round and cost health; in the opening they are a gold source only.
- Strong camps need numbers or items: an elk alone at base deals 2400 damage before it dies, more than any champion's health. Their yield rises fastest with items, so they belong to the mid game, and the monolith (200 gems, a fifth of the win) to a strong full team that rotates who stands nearest.
- Every awake camp of a group hits each round, so a group multiplies the damage in this table.
- Measured: the rivals took pure gem-cluster groups 11.0 times per game against our 5.8 (nm2 on b13p2; lv1 raised ours to 7.6; findings, "Gems per camp hp").

### 2.11 Tribute, bags and Marcella

- A tribute takes ceil(gems / 10) turns next to an altar: 4 for 33 gems, 10 for 100. Damage does not break it; a stun, death or a new altar lock does. A killer takes the whole bag. Small bags tributed often cut both the loss on death and the window for a stun. On brkp the rivals start 20.7 tributes per game against our 9.5, with bags of the same size (33-39 gems).
- Marcella is stun-immune, so only death or a lock can break her tribute, and she earns +2 gold per gem she tributes. Gems reach a bag only through a capture (split among the champions present, the remainder to the lowest ID) or a kill; `docs/MECHANICS.md` lists no way to pass them on. So gem-rich captures are worth most in her bag. Our `pick_group` (`targets.h`) counts her bonus when two of our champions claim the same group, weighed against the shards each already owns.
- An altar lock (10 gold, removed by 5 hits) cancels and then blocks the enemy's tributes at that altar.

### 2.12 What a champion can read, and what it cannot

- Of a visible enemy: health, the cooldowns of both slots, `damage_amount(target)`, items, carried gems and buffs; not its gold. Nothing out of the champion's own view (vision 8, its ward 6; teammates' views are not shared).
- So each champion can compute exactly which visible enemies can stun or burst it before its next turn (2.8, with their live cooldowns), and which carry a bag worth a kill: a carrier of 100 gems is a tenth of the win.
- Teammates see different things, so group behaviour has to come from identical local rules plus the 8 shared bytes. The 1024-byte draft memory is written during the draft (the first draft turn has 100 times the fuel) and read by every champion all game: room for a map analysis computed once (group values, routes, altars, choke points) instead of in the opening turns, where fuel is short. Our bot does not use it.

## 3. Where our bot departs from the doctrine

These are structural, not metric gaps.

1. **Micro is a priority chain.** `Bot::play_turn` (`bot.cpp`, steps 9-11 of the pipeline in `docs/ARCHITECTURE.md`) runs `pvp`, then the threat branch (`kite`, `duel`, `flee`), then attack on sight, and each branch moves with its own primitive (`step_next_to`, `step_away`, `step_out_of_danger`, `walk_home`, `flee_dash`). No step compares all reachable tiles under one rule, and the order of move and attack is fixed per branch. This is the stage Cout for Clout left behind because it could no longer be modified safely. Our record shows the same symptom: since 10-24 most fight changes moved one metric and broke another (`docs/experiments.md`).
2. **Danger is per enemy, not summed, and ignores tempo.** A tile is dangerous only when one visible enemy's burst reaches 30% of our health (`knowledge.h`). Three shooters at 11% each leave the tile "safe"; a stunner with its stun ready is not distinguished from one with its stun spent; the second enemy action between our turns is not counted. rz21 tried summing bursts inside the old chain and failed (our deaths +1.31 per game on b19p).
3. **No convergence rule.** Allies move towards a fight only through the help call (3-14 tiles, our half, healthy, nothing in view). Measured: they fight with two or more champions hitting in 31.2 rounds a game, we in 16.9, at equal focus (73% against 75% on one target).
4. **Fights are not timed to cooldowns.** Engage is decided by `simulate_fight` (3 rounds, live cooldowns, no heals) and thresholds; there is no rule of the kind "go in when their stuns are down, stay at 5+ when they are up".
5. **Draft has one stunner fewer than the meta** (Varg for Ryth). ry1 (Ryth) cut their hit rounds on us by 12.2 per game and was rejected on a tribute margin that two panels disagreed on.

The macro (targets, banking, shop) has been compared with the top teams many times and moved towards theirs (gold weight, Jungle in the main stat, tribute batch); it is not where the doctrine says the next large gain is.

## 4. The plan this leads to

One line of work, not many small variants: **replace the fight branches with a per-tile micro evaluator**, in the XSquare / SPAARK form, sized to this game.

For every candidate end tile (stay, the 8 steps, and for dash champions the dash landings), and for both orders where the champion's kit allows (hit then move, move then hit; ranged champions cannot do both, a dash still works after a ranged shot):

- `canHit`: best damage we can deal this turn from that tile (basic attack, ready spells), with kill and stun flags for the target hit.
- `threat`: damage the visible enemies can deal on that tile before our next turn, summed, counting one or two actions per enemy from the turn order, ranges including a dash or a step, and ready stuns (a ready stun doubles the following threat, since we lose a turn inside it). Camps that would target us on that tile count too.
- `support`: allies that can hit the enemies threatening that tile before their next turn (the same tempo count from their side).
- `distance` to the chosen prey, to the nearest hurt or stunned ally, and to home.

Choose the tile with one fixed comparison, bucketed by state as XSquare does:

- **Ready** (attack available and, for the main stun, ready): prefer tiles where we hit the prey, then the lowest threat net of support, then nearer to allies.
- **Not ready** (ranged shot used this turn or the key spell on cooldown, or the enemy's stuns ready and ours spent): prefer tiles with zero threat, then nearest to the fight (kiting at reach + 1), then nearer to allies.
- **Chicken** (health below a threshold that grows with the enemies' combined burst): zero threat first, then towards home and allies; hit only if free.

Convergence comes from the same evaluator on every champion: the `distance` term pulls healthy champions towards allies under fire and towards the team's focus target, which uses the existing focus byte.

### How to build and test it

1. Build it as a new file (`micro.h`) that returns a tile and an order, and call it in place of steps 9-11 only when an enemy champion is within 8 tiles. Everything else (targets, banking, shop, camps) stays.
2. Write the decision rule before results, as the team requires: the targeted factor is our deaths per game in five-a-side games and the share of our deaths with a stun on the victim; guards are gems collected, tributed and team gold at r600.
3. Local first: against `pool/` old mains on all 70 maps, both sides, to catch breakage. Then platform panels of 40-90 games beside a same-session base run, judged with decoded metrics.
4. Draft: test Ryth for Varg again once the evaluator is in, since a third stun is worth more when the micro times fights to cooldowns.

### Deadline

The Sprint 3 lock is Sat 31 Oct 23:59 GMT (Sun 1 Nov 05:29 IST). The evaluator is a rewrite of the fight layer; the postmortems' rule is not to make last-minute changes. So Sprint 3 keeps the current main unless the evaluator passes its rule on the platform before the lock, and the evaluator is the main line of work for the final tournament (season end 18 Nov).
