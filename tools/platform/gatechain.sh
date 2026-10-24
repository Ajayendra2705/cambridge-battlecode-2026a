#!/bin/bash
# Run platform gates one after another: bash tools/platform/gatechain.sh PLAN [CUTOFF]
# PLAN is a file of lines "BOT RUN_NAME PANEL" (panel specs in results/panels/specs_PANEL.txt), e.g.
#   exp/cp3 cp3_b56 b56
#   main    base_b56 b56        (main is already on the platform: no upload)
# Each line runs through gateq.sh, which uploads BOT, plays the panel, logs RUN_NAME@PANEL in results/gate.log and
# resubmits main. CUTOFF=HHMM (local time) stops starting new gates after that time (for a Sprint lock).
# Refuses to start while another gate or chain runs: two chains at once make each gate play the other's upload.
cd "$(dirname "$0")/../.."
plan="$1"; cutoff="${2:-2400}"
[ -f "$plan" ] || { echo "usage: gatechain.sh PLAN [CUTOFF]"; exit 1; }
others=$(bash tools/platform/procs.sh | grep -E "gateq\.sh|gate\.sh|gate_full\.sh")
[ -n "$others" ] && { echo "another gate is running:"; echo "$others"; exit 1; }
# The plan is read on fd 3: powershell (the uploads) reads stdin and would eat the remaining lines.
while read -r bot run panel <&3; do
  [ -z "$bot" ] || [ "${bot:0:1}" = "#" ] && continue
  [ "$(date +%H%M)" -lt "$cutoff" ] || { echo "cutoff $cutoff reached, not starting $run"; break; }
  specs="results/panels/specs_$panel.txt"
  [ -f "$specs" ] || specs="data/specs_$panel.txt"
  echo "$bot $run" > data/gate_queue.txt
  GATE_SPECS="$(cat "$specs")" GATE_PANEL="$panel" bash tools/platform/gateq.sh
done 3< "$plan"
echo "chain done $(date +%H:%M)"
