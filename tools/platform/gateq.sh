#!/bin/bash
# Gate queue: bash tools/platform/gateq.sh [WAIT_RUN]. Runs gate.sh for each line "BOT RUN_NAME" of data/gate_queue.txt,
# one at a time, popping lines as it goes (edit the file to reorder or add), and resubmits main after each gate.
# Honours GATE_SPECS / GATE_PANEL. With WAIT_RUN, first waits until that gate.log run has all its games finished.
cd "$(dirname "$0")/../.."
if [ -n "$1" ]; then
  until ids=$(grep "^$1 " results/gate.log | tail -1 | cut -d' ' -f2-) && [ -n "$ids" ] \
        && [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
fi
while line=$(head -1 data/gate_queue.txt 2>/dev/null) && [ -n "$line" ]; do
  sed -i 1d data/gate_queue.txt
  set -- $line
  echo "== $1 $2 $(date +%H:%M)"
  # main is already on the platform (resubmitted after every gate): skip its upload (limit 20 per hour).
  mode=submit; [ "$1" = main ] && mode=nosubmit
  bash tools/platform/gate.sh "$1" $mode "$2" 2>&1 | tail -3
  # Submit failed (upload limit): put the line back and wait.
  if [ "${PIPESTATUS[0]}" = 3 ]; then { echo "$1 $2"; cat data/gate_queue.txt; } > data/gate_queue.tmp && mv data/gate_queue.tmp data/gate_queue.txt; sleep 90; continue; fi
  [ "$1" = main ] || until powershell -File tools/cambc.ps1 submit main 2>&1 | tail -1 | tee /dev/stderr | grep -q Submitted; do sleep 60; done
done
