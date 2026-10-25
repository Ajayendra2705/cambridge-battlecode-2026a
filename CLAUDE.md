# Agent instructions

All project memory lives in this repo. Do not use or write a private memory directory. Record what you learn here.

## Read first

1. `README.md`: layout and where everything is.
2. `docs/status.md`: current bot, deadline, next steps.
3. `docs/ARCHITECTURE.md` before touching `bots/main`, and `docs/WORKFLOW.md` before running tests.
4. `docs/MECHANICS.md` for any rule or number. `docs/reference/GameRules.md` has outdated numbers.

Look things up through the "Where is ..." table in `README.md` instead of searching the tree.

## Keep the repo current

- Every variant tested gets a row in `docs/experiments.md` (bot, parent, change, local, platform, verdict). Then delete its `bots/exp/` folder.
- When `bots/main` changes or the plan changes, update `docs/status.md` (and `docs/lineage.md` if a new bot is accepted).
- New measured facts go in `docs/findings.md`. New engine rules go in `docs/MECHANICS.md` with a source tag.
- New tools go in the right `tools/<dir>/` and get a row in `tools/README.md`. Run outputs go in `data/` (gitignored), or in `results/analysis/` if worth keeping.
- `docs/journal/` is a frozen history. Do not append to it.

## Working rules (from the team)

- Chat replies: caveman ultra style (terse, no filler). Files, docs and commits use normal prose.
- Before each step ask: is it needed, and how can this idea be better?
- One factor at a time: compare us with the teams above us, pick the largest gap, name a target metric, and stay on it until matched.
- Platform tests are about 20 games (`tools/platform/gate.sh`). Run the base at the same time, with a unique run name.
- Local wins do not prove a fighting, item or draft change. Only the platform does.
- Gates submit bots. Never run two gate chains at once. After testing, make sure `main` is submitted, especially near a Sprint lock.
- Never ship logging bots (`*l`) or heavy prints: they cost fuel and change play.
- Heavy local runs: the team allowed all cores (10-26). Check free RAM first: `--jobs 11` needs about 0.4 GB, a decode job about 140 MB. With under 2 GB free, use `--jobs 6` or fewer.
- Keep `bots/main` changes verifiable: a pure refactor must give a byte-identical wasm (`sha256sum bots/main/.cambc/build-release/bot.wasm`).

## Lessons from the 10-24/25 session (agent)

- A 50-game platform result moves by about 3 wins between near-identical bots. The team agreed batch panels of 40-90 games (`results/panels/`, one gate over a combined panel such as `b56`); judge with decoded metrics (`tools/replay/decode_run.sh`, `tools/replay/decoded.py`), and write the decision rule down before the result arrives.
- Opponents change bots during the day: run the base in the same session (`main` line in the `gatechain.sh` plan), never against a base from hours earlier.
- Run gates only through `tools/platform/gatechain.sh` (it refuses to start beside another gate). Find or stop processes with `tools/platform/procs.sh`: Git Bash `ps` does not show command lines.
- Never delete `data/runs/` while a local run writes there. Edit bot code with the editor, not through shell or Python string escapes.
- `docs/experiments.md` has CRLF line endings: edit it with the editor, or in Python open it with `newline=''` for reading as well as writing (a plain read turns every line into a diff).
