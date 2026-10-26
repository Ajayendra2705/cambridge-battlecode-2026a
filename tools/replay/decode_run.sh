#!/bin/bash
# Decode every game of a platform run for tools/replay/decoded.py:
#   bash tools/replay/decode_run.sh RUN@PANEL [JOBS]
# Downloads the replays (gdl.py), extracts per-round datasets (rounds_extract.mjs, JOBS parallel, default 3) into
# data/fights/<RUN>_<PANEL>/ and writes a clean index.txt there. Needs Node 22 and data/vis/ (tools/replay/vis_assets.py).
set -e
cd "$(dirname "$0")/../.."
run="$1"; jobs="${2:-3}"
[ -n "$run" ] || { echo "usage: decode_run.sh RUN@PANEL [JOBS]"; exit 1; }
name="${run/@/_}"
python -I tools/replay/gdl.py "$run" | tail -1
src="data/replays/platform/$name"
out="data/fights/$name"
mkdir -p "$out"
tr -d '\r' < "$src/index.txt" > "$out/index.txt"
# Native processes (pextract.py), not xargs: Git Bash failed to start them under load and decodes came back empty.
python -I tools/replay/pextract.py "$out" "$jobs" "$src"/*.repl26a | tail -3
echo "decoded into $out ($(find "$out" -name '*.jsonl.gz' | wc -l) games)"
