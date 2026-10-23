#!/bin/bash
# Continuous platform gate queue: bash tools/gq.sh LADDER
# Pops the first line of tools/gate_queue.txt ("PANEL BOT OFFSET BASELINE", e.g. "gate5 ev1 40 ea3@p5@40"), waits for
# 9 free quota groups, runs it through gate_safe (the ladder bot is resubmitted afterwards), appends the paired
# comparison against BASELINE to tools/gq.out, and repeats. An empty queue is polled every 30 s; a line "stop" ends it.
cd "$(dirname "$0")/.."
ladder=$1
touch tools/gate_queue.txt
while :; do
  line=$(head -1 tools/gate_queue.txt)
  if [ -z "$line" ]; then sleep 30; continue; fi
  sed -i '1d' tools/gate_queue.txt
  [ "$line" = "stop" ] && break
  set -- $line
  panel=$1 bot=$2 off=${3:-0} base=$4
  echo "== $(date +%H:%M) start $panel $bot offset $off" >> tools/gq.out
  bash tools/qwait.sh 9
  if [ "$off" = 0 ]; then GATE_HALF=1 bash tools/gate_safe.sh "$panel" "$bot" "$ladder" >> tools/gq.out 2>&1
  else GATE_HALF=1 GATE_OFFSET=$off bash tools/gate_safe.sh "$panel" "$bot" "$ladder" >> tools/gq.out 2>&1; fi
  tag="p${panel#gate}"
  run="$bot@$tag"; [ "$off" != 0 ] && run="$run@$off"
  [ -n "$base" ] && python -I tools/paired.py "$base" "$run" 2>&1 | tail -3 >> tools/gq.out
  echo "== $(date +%H:%M) done $run" >> tools/gq.out
done
