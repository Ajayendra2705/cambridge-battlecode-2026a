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
| `fights/<RUN>_<PANEL>/` | Decoded per-round datasets of a platform run (`*.jsonl.gz` + `index.txt`) | `bash tools/replay/decode_run.sh RUN@PANEL`; read with `tools/replay/decoded.py` |
| `fights/ranked2/` | 96 decoded rival-vs-rival ranked games (ranks 55-80, 10-24) with camp types | `fetch_ranked.py` then `rounds_extract.mjs` |
| `fights/ranked/` | 1,328 decoded ranked games on engine 1.0.3 (ranks 40-90 and their opponents, with `avis`): the ML training set | `fetch_ranked.py`, then `rounds_extract.mjs` (`ml/README.md`) |
| `ml/` | ML datasets and models (`games.parquet`, `events.parquet`, `dataset.npz`, `fpr_dataset.npz`, `*.pt`) | `ml/*.py` (`ml/README.md`) |
| `replays/ranked/` | Ranked replays of other teams + `index.jsonl` | `python -I tools/replay/fetch_ranked.py RANKS` |
| `vis/` | Official visualiser engine (WASM + JS) used by the decoders | `python -I tools/replay/vis_assets.py REPLAY` |
| `specs_*.txt` | Working copies of the panels; the kept ones are in `results/panels/` | `tools/platform/gatechain.sh` reads `results/panels/` first |
| `gate_queue.txt`, `gateq_*.log`, `ladder_*.jsonl` | Gate queue file and gate logs; ladder snapshots | `gateq.sh`; `cambc ladder --page N --json` |
