#!/bin/bash
# Gate queue: bash tools/platform/gateq.sh [WAIT_RUN]. Runs gate.sh for each line "BOT RUN_NAME" of data/gate_queue.txt,
# one at a time, popping lines as it goes (edit the file to reorder or add), and resubmits main after each gate.
# Honours GATE_SPECS / GATE_PANEL. With WAIT_RUN, first waits until that gate.log run has all its games finished.
cd "$(dirname "$0")/../.."
if [ -n "$1" ]; then
  until ids=$(grep "^$1 " results/gate.log | tail -1 | cut -d' ' -f2-) && [ -n "$ids" ] \
        && [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 20; done
fi
while line=$(head -1 data/gate_queue.txt 2>/dev/null) && [ -n "$line" ]; do
  sed -i 1d data/gate_queue.txt
  set -- $line
  echo "== $1 $2 $(date +%H:%M)"
  # main is already on the platform (resubmitted after every gate): skip its upload (limit 20 per hour).
  mode=submit; [ "$1" = main ] && mode=nosubmit
  # Ranked sets are created every 10 minutes at :x0:05 and play out within a minute (10-30 listings): upload a test bot
  # only from :x0:25 to :x2:59, so that the gate (3-6 minutes) ends and main is back before the next set. Ranked games
  # are then played by main, not by the bot under test. NO_RANKED_WINDOW=1 skips the wait.
  if [ "$mode" = submit ] && [ -z "$NO_RANKED_WINDOW" ]; then
    until s=$(( 10#$(date +%M) % 10 * 60 + 10#$(date +%S) )); [ "$s" -ge 25 ] && [ "$s" -lt 180 ]; do sleep 5; done
  fi
  bash tools/platform/gate.sh "$1" $mode "$2" 2>&1 | tail -3
  # Submit failed (upload limit): put the line back and wait.
  if [ "${PIPESTATUS[0]}" = 3 ]; then { echo "$1 $2"; cat data/gate_queue.txt; } > data/gate_queue.tmp && mv data/gate_queue.tmp data/gate_queue.txt; sleep 90; continue; fi
  [ "$1" = main ] || until powershell -File tools/cambc.ps1 submit main 2>&1 | tail -1 | tee -a /dev/stderr | grep -q Submitted; do sleep 20; done
done
