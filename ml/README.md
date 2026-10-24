# ml/ — learned fight decision

Goal: a learned `Q(situation, action) -> predicted outcome` that replaces or backs up `simulate_fight` in the engage decision (`bots/main/src/bot.cpp`, the `winning` block). Trained by supervised learning on platform replays near our rank. Target: the final (18 Nov). Owner: Michael.

Python project managed with uv: `cd ml && uv sync`, then `uv run python common.py`. Outputs go to `data/ml/` (gitignored).

## Decisions so far

| Decision | Value | Why |
|---|---|---|
| Learning setup | Supervised Q(s, a), one-step (contextual bandit), Monte Carlo label | Too few games for RL; the engage call is one decision with a delayed outcome |
| Data | 1,328 ranked platform games on engine 1.0.3 (ranks 40-90 and their opponents), extracted by `tools/replay/rounds_extract.mjs` into `data/fights/ranked/` | Same distribution the bot will face |
| Event trigger | A (champion, enemy) pair seen for the first time, or again after a gap > 3 rounds | Vision gap histogram (`vis_gaps.py`); the bot must use the same rule at test time |
| Model family | Set encoder (phi 6->16, pool, head 32->16->1), about 3k fuel with SIMD | Measured in `bots/exp/fuelm` (`docs/findings.md`) |
| Split | By game: 930 train / 199 val / 199 test (`data/ml/games.parquet`, seed 0) | Rows from one game are correlated |
| Inputs | Only what the champion can see in-game (its `vis` list, plus its own team) | Feature parity with the bot |

## Files

| File | Use |
|---|---|
| `common.py` | `load_game(id)` -> `(meta, rounds)` without draft rounds. `load_games()` -> games table (`game, map, team_a, team_b, rank_a, rank_b, winner, split`; `winner` 0 = A, 1 = B). Run it to rebuild `data/ml/games.parquet`. `cooldowns(rounds)` -> `cd[round_idx][champ][slot]`, rounds until ready at round start. |
| `vis_gaps.py` | Histogram of vision gaps per (champion, enemy) pair -> `data/ml/vis_gaps.png` |

Data notes:
- `meta["outcome"]` in the extracted files is always 0 (extractor bug). Use `winner` from `load_games()`.
- Cooldowns are derived from cast history: exact for 12 champions (0 errors in 24k casts), an overestimate on 17% of Vendetta's casts (camp kills reset her and are not in the data). The bot reads enemy cooldowns live (`docs/MECHANICS.md`), so they are a legal feature.
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
- Whether the bot can read enemy items in fog is unchecked (`item_count()` in `cambc.h` does not say).
