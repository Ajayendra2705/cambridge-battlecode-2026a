#!/bin/bash
# Decode platform runs as their games finish: bash tools/replay/decode_chain.sh JOBS RUN@PANEL...
# Waits until each run is in results/gate.log with every game finished, then decodes it (decode_run.sh, JOBS
# extractions at once) and counts its fuel events (fuel_events.py). Run it in the background beside a gate chain:
# it only reads from the platform. Output: one "== RUN ready" line, the decoded count and the fuel line per run.
cd "$(dirname "$0")/../.."
jobs=$1; shift
for run in "$@"; do
  until ids=$(grep "^$run " results/gate.log | tail -1 | cut -d' ' -f2-) && [ -n "$ids" ] \
        && [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
  echo "== $run ready $(date +%H:%M)"
  bash tools/replay/decode_run.sh "$run" "$jobs" 2>&1 | tail -1
  python -I tools/replay/fuel_events.py "$run" 2>&1 | grep '^=='
done
echo "all decoded $(date +%H:%M)"
