# ml/ — learned fight decision

Goal: a learned `Q(situation, action) -> predicted outcome` that replaces or backs up `simulate_fight` in the engage decision (`bots/main/src/bot.cpp`, the `winning` block). Trained by supervised learning on platform replays near our rank. Target: the final (18 Nov). Owner: Michael.

Python project managed with uv: `cd ml && uv sync`, then `uv run python common.py`. Outputs go to `data/ml/` (gitignored).

## Decisions so far

| Decision | Value | Why |
|---|---|---|
| Learning setup | Supervised Q(s, a), one-step (contextual bandit), Monte Carlo label | Too few games for RL; the engage call is one decision with a delayed outcome |
| Data | 1,328 ranked platform games on engine 1.0.3 (ranks 40-90 and their opponents), extracted by `tools/replay/rounds_extract.mjs` into `data/fights/ranked/` | Same distribution the bot will face |
| Decision point | Every round a champion sees an enemy within `max(its range, 4)` (the bot's own `prey` condition) | First-sight events (gap > 3) were tried: engagement after first sight is spread over 20+ rounds with no drop-off, because champions walk in from up to 8 tiles. Re-deciding every round matches the bot |
| Action | Per enemy in reach: engage = this round it attacked or cast on that enemy, or moved closer to it; else don't engage | Matches the bot's engage branch (hit the prey or step toward it) |
| Model family | Set encoder (phi 6->16, pool, head 32->16->1), about 3k fuel with SIMD | Measured in `bots/exp/fuelm` (`docs/findings.md`) |
| Split | By game: 930 train / 199 val / 199 test (`data/ml/games.parquet`, seed 0) | Rows from one game are correlated |
| Label constants | Carried gem = 0.71 tributed gem, a death (lambda) = 50 tributed gems | Logistic regression of game result on team differences (tributed, carried, alive) over train snapshots every 50 rounds (`snapshots.py`), boss_battle excluded. lambda is likely inflated (strong teams both survive and win) |
| Horizon H | 20 rounds | Engaged-minus-not label gap / std peaks flat at H = 10-20 (0.32), then falls; a 1v1 from full hp takes about 12-20 rounds plus 0-3 to close in |
| boss_battle | Excluded from training; the bot keeps `simulate_fight` there | Tributing is blocked until the monolith dies, so carried gems mean something else; 38 games are too few to fit or train separately |
| Inputs | Only what the champion can see in-game (its `vis` list, plus its own team) | Feature parity with the bot |

## Files

| File | Use |
|---|---|
| `common.py` | `load_game(id)` -> `(meta, rounds)` without draft rounds. `load_games()` -> games table (`game, map, team_a, team_b, rank_a, rank_b, winner, split`; `winner` 0 = A, 1 = B). Run it to rebuild `data/ml/games.parquet`. `cooldowns(rounds)` -> `cd[round_idx][champ][slot]`, rounds until ready at round start. |
| `simfight.py` | Python port of the bot's engage rule: `engage_decision(rnd, cds, i)` -> prey, engage, winning/finisher/rich, sim result. Baseline for offline eval. Stat table checked: max hp from items matches the replay on all 18,399 champion-rounds of one game. Differences from the bot: no spawn-tile rules, no team focus calls, calibration factor fixed at 1. |
| `events.py` | Decision points -> `data/ml/events.parquet` (`game, idx, r, champ, enemy, team, dist, split`; `idx` indexes `rounds`). 1.88M (champion, enemy) rows, 1.42M decisions. |
| `actions.py` | `engaged(rounds, idx, champ)` -> set of enemies engaged this round |
| `coverage.py` | Action counts per `simulate_fight` outcome group -> `data/ml/coverage.parquet` |
| `labels.py` | `label(rounds, idx, champ, H, lam)`: team gem swing (carried x 0.71) + lam x death difference over H rounds |
| `snapshots.py` | Team differences every 50 rounds + game result -> `data/ml/snapshots.parquet` (fit of the label constants) |
| `features.py` | Per decision: self, ally and enemy unit vectors, game features, actions, label -> `data/ml/dataset.npz` |
| `dataset.py` / `model.py` / `train.py` | Standardisation (train stats), FightQ (shared phi, sum pooling, engage and stay heads, masked loss), training with early stopping -> `data/ml/model.pt` |
| `export_weights.py [BOT]` | Writes `bots/BOT/src/fightq_weights.h` (default `exp/fq1`) |
| `parity.py BUNDLE EXTRACTED` | Compares the features a logging bot printed (`FQ` lines, team A) with Python's features from the same replay |
| `vis_gaps.py` | Histogram of vision gaps per (champion, enemy) pair -> `data/ml/vis_gaps.png` |

Data notes:
- `meta["outcome"]` in the extracted files is always 0 (extractor bug). Use `winner` from `load_games()`.
- Cooldowns are derived from cast history: exact for 12 champions (0 errors in 24k casts), an overestimate on 17% of Vendetta's casts (camp kills reset her and are not in the data). The bot reads enemy cooldowns live (`docs/MECHANICS.md`), so they are a legal feature.
- Each round has `vis[i]` (enemies champion i sees) and `avis[i]` (allies it sees). Vision is not shared, and 7% of allies within 8 tiles are hidden, so use `avis`, not distance.
- Item counts of visible champions (allies and enemies) are readable in-game (`docs/MECHANICS.md` section 8), so items are a legal feature.
- Champion `ty` ids follow `champion_type` in `sdk/cpp/cambc.h` (0 Ryth ... 12 Heart of Ruin).

## Pipeline

| Step | Output | Done check |
|---|---|---|
| 1 Events | `data/ml/events.parquet` | Events per game plausible; one event confirmed in the visualiser |
| 2 Features, action, label | `data/ml/dataset.pt` | 3 events hand-checked against raw rounds; base rates per action |
| 3 Train | model weights | Val loss beats a constant predictor (mean label) |
| 4 Offline eval | table vs `simulate_fight` (Python port) | Test games only, once |
| 5 Bot | variant with C++ SIMD forward pass | Feature parity within 1e-5, local sanity run, platform gate |

Stop rules:
- Step 3 cannot beat the constant predictor: fix features or label, not the net.
- Step 4 does not beat `simulate_fight`: no C++ port. Record why in `docs/experiments.md`.

## Known gaps

- Vendetta cooldowns are approximate (see above).
- Actions are what other teams' bots did. Situations where no bot engages have few "engaged" examples, so Q is least reliable there (selection bias).

## Ideas to try later

- Hybrid label: add the deciding champion's own carried-gem change on top of the team swing (extra weight for its own bag). Compare against the pure team label in the offline eval.
- Carried weight 0.38 (all-maps fit) vs 0.71, compared in the offline eval.
- Recently seen enemies: a self feature counting enemies seen in the last ~10 rounds but not visible now (their reinforcements decide our fatal fights, `docs/findings.md`). Needs matching memory code in the bot.
- Shields and stuns: buffs of visible champions are readable in-game but not extracted yet (needs a `rounds_extract.mjs` re-run).
- Durability emblems: -10% damage taken is invisible to the strength/focus features.
- Drop `range` from the unit features (it is a fixed function of type).
