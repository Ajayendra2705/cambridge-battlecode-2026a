# data/ (not in git)

Bulky or regenerable files. Everything here except this README is gitignored. Delete freely, except `replays/top`, which took effort to collect.

| Path | Content | Written by / how to get it again |
|---|---|---|
| `summaries/<match>.json` | Platform match summaries (per-champion metrics, events) | `tools/platform/group.py`, `gdl.py` (download on demand) |
| `replays/platform/<run>/` | Platform replay bundles of one gate run + `index.txt` (match map side result) | `python -I tools/replay/gdl.py RUN` |
| `replays/top/` | Summaries of top-10 ranked games, with `index.json` | downloaded from the ladder 2026-10-21 |
| `replays/ours/` | Summaries of our own ranked games | downloaded 2026-10-21 |
| `runs/` | Local run output (`multi-*`, `rr-*`): summaries per game, replays only with `--keep` | `tools/local/*.py` |
| `cache/` | `rcmp.py` result cache per run name | `tools/platform/rcmp.py` |
| `probe_out/` | Per-map camp group dumps from the probe bots | `bots/probe/*` |
| `old/` | Leftovers from before the cleanup (unsorted replays, debug output) | safe to delete |
