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
- Pushing to GitHub is allowed since 10-28 13:50 IST (user: "now you can push whatever you want to the repo"; the 10-26 rule kept commits local). Push the working branch with a plain `git push`, never force. To read the teammate's work, `git fetch origin` and merge `origin/master` into the local branch.
- Before each step ask: is it needed, and how can this idea be better?
- One factor at a time: compare us with the teams above us, pick the largest gap, name a target metric, and stay on it until matched.
- Platform tests are about 20 games (`tools/platform/gate.sh`). Run the base at the same time, with a unique run name. A panel pinned to the rivals' bots replays exactly (11-03: v1531 twice on `nb1`, every margin equal), so a pinned base played once stays valid, and a game's difference between two bots is chaos from small changes, not platform noise.
- Local wins do not prove a fighting, item or draft change. Only the platform does.
- A variant goes to the platform only after it passes its local screen (user, 11-02 02:25 IST: "if its passes local then only it can go to platform, otherwise not"). Write the local bar before the screen; a local pass is needed, not enough (see the line above). On 11-02 dv5 failed its screen and its gate was stopped before any game.
- Decision rules judge the targeted factor, not wins (user, 10-26 22:50: "Opponents are changing their bots rapidly. Don't set the bar on the number of wins"). Name the factor's metric, a bar for it, and guards that the other metrics hold; record wins without judging them.
- Keep v1523 live until a better bot is found (user, 11-03 12:20 IST: "keep live as v1523 until you find any better things"). A match group plays the team's active version and `cambc` has no version option, so a gate makes the tested bot live for about 20 minutes, and an upload takes the live selection by itself: ask the user before any gate or upload, and select the bot that was live again after it. A teammate uploaded v1530 (`bots/bamboo1530`, 1523 plus review fixes) and then v1531 (router: Bamboo 1472 on 7 near maps, 26 of 80 wins against 1530's 12 on their panel). The user then kept v1531 (11-03 15:48 IST). v1533 (`bots/bamboo1533` = v1531 plus the Vesper gold fix `ra1`) went live at 19:40 IST (user: "Yes, v1533 live"). A teammate then uploaded v1534 "RT32" (v1531 plus a nav fuel fix and Willow changes) and v1535 "RT33" (top-5 drafts with Cassi and Issac on five picks; sources of both are not in the repo), and at about 21:21 IST v1531 was selected again. The user selected v1536 (`bots/bamboo1536` = v1533 plus 8 more Bamboo maps and Marcella's stun first) at 23:30 IST: **the live bot is v1536 unless `cambc submissions list` says otherwise.** The user's plan: keep improving until about 03:10 IST 11-04 (extended twice, last at 01:10 IST: "take 2 more hours"), then combine; the lock is 05:29 IST 11-04. Read `cambc submissions list` before a gate and do not flip a teammate's choice back without asking. A teammate's test also needs the live slot: `tools/platform/waitteam.py` waits for it to end.
- All ranked matches should be played by the best bot (user, 11-04 00:49 IST: "try to arrange in such a way such that all ranked matches are played by best bot"). Ranked rounds usually start at :x0:05 and our set lasts about 40 seconds. A selection stays `queued` for 2 to 9 minutes (nothing seen triggers it), so select right after a set starts, create all the bot's panels at once when it goes active (a 50-game panel finishes in seconds), and select the live bot again straight away: `tools/platform/gate_slot.sh`. This makes a ranked set on the test bot unlikely, not impossible. The user cancelled a selection on the website at 00:47 IST to keep v1536 on a ranked set, and the retry loop in `gateq_fast.sh` (`select_wait`) selected it again 48 seconds later: never run a selection loop while a person may be deciding.
- Full permission until the lock (user, 11-04 01:31 IST: "keep working till 5 29 / you have full permissions from my side / If you are 100 percent sure that that you have build a model that is better than the best one you had at that time. you can use that as live."). Gates and uploads need no further question tonight; a bot goes live only when its evidence clearly beats the live bot, and the selected bot must be checked before 05:29 IST.
- Gates submit bots. Never run two gate chains at once. After testing, make sure `main` is submitted, especially near a Sprint lock.
- Never ship logging bots (`*l`) or heavy prints: they cost fuel and change play.
- Heavy local runs: the team allowed all cores (10-26). Check free RAM first: `--jobs 11` needs about 0.4 GB, a decode job about 140 MB. With under 2 GB free, use `--jobs 6` or fewer.
- Keep `bots/main` changes verifiable: a pure refactor must give a byte-identical wasm (`sha256sum bots/main/.cambc/build-release/bot.wasm`).

## Lessons from the 10-24/25 session (agent)

- A 50-game platform result moves by about 3 wins between near-identical bots. The team agreed batch panels of 40-90 games (`results/panels/`, one gate over a combined panel such as `b56`); judge with decoded metrics (`tools/replay/decode_run.sh`, `tools/replay/decoded.py`), and write the decision rule down before the result arrives.
- Opponents change bots during the day: run the base in the same session (`main` line in the `gatechain.sh` plan), never against a base from hours earlier.
- Run gates only through `tools/platform/gatechain.sh` (it refuses to start beside another gate). Find or stop processes with `tools/platform/procs.sh`: Git Bash `ps` does not show command lines.
- Start a runner script (a chain plus its judge) once, with the tool's background option, and check `procs.sh` first (it lists `*/run_*.sh` and `*/judge_*.sh` since 10-29). A `cmd &` inside a tool call keeps running after the call returns: on 10-29 a second copy of a runner started a duplicate chain, which submitted the variant and stopped only on the full hour quota.
- A running chain reads its plan through an open file: skip a line by writing `#` over its first character in place. `sed -i` replaces the file, and the chain plays the old lines (10-27).
- A chain with `GATE_RESTORE=none` leaves its last bot live, so it needs a running session to select the live bot after it. When a chat is about to close, stop the chain first (11-03). Stop it by pid from `tools/platform/procs.sh`: stopping only the background task leaves its children running.
- A `live` gate plays whatever is active. On 11-03 21:21 IST a teammate selected another version during a chain of `live` gates, and 24 groups replayed that bot under the wrong name. Set `LIVE_EXPECT=N` for such a chain (`gateq_fast.sh`), and read `data/gate_live.log` and each game's draft before trusting a run.
- Never edit a shell script while it runs: bash reads the file as it goes, so on 11-03 an edit to `tools/local/screen.sh` during a screen made it start the whole run a second time.
- Never delete `data/runs/` while a local run writes there. Edit bot code with the editor, not through shell or Python string escapes.
- Docs have LF endings, except `docs/experiments.md`, which has CRLF in every commit (origin/master too; checked 10-29 21:30 with `git ls-files --eol`). An earlier note here said it had LF: that check used `grep -c $'\r'`, which in Git Bash counts every line of a file and none of a pipe, so it proves nothing. Keep each file's endings: the Edit tool does; in Python read and write with `newline=''` and keep the endings found (a plain write turns every line into a diff).
