#!/bin/bash
# Gate a bot between ranked slots so the test bot never plays a ranked match:
#   bash tools/gate_safe.sh PANEL BOT LADDER   (PANEL = gate2 or gate3; GATE_OFFSET / GATE_HALF pass through)
# Ranked matches start every 10 minutes (:00, :10, ...). We wait until one minute after a slot, run the gate
# (it submits BOT and creates its match groups; unranked matches finish seconds after creation), and resubmit
# LADDER as soon as the gate has finished, or at the latest one minute before the next slot (a background
# guard), whichever comes first. Needs a fresh hourly quota (45 matches) so every group is created in one burst.
cd "$(dirname "$0")/.."
panel=$1 bot=$2 ladder=$3
# Wait for minute ending in 1 (one minute after a ranked slot).
while :; do
  m=$(date +%M); s=$(date +%S)
  [ $((10#$m % 10)) -eq 1 ] && [ $((10#$s)) -lt 30 ] && break
  sleep 10
done
start=$(date +%s)
# Guard: resubmit the ladder bot before the next slot (8 minutes from now) even if the gate is still running.
( sleep 470; if [ ! -f tools/.gate_safe_done ]; then powershell -File tools/bc.ps1 submit "$ladder" 2>&1 | tail -1; echo "guard resubmitted $ladder" >&2; fi ) &
guard=$!
rm -f tools/.gate_safe_done
bash "tools/$panel.sh" "$bot"
touch tools/.gate_safe_done
kill $guard 2>/dev/null
powershell -File tools/bc.ps1 submit "$ladder" 2>&1 | tail -1
echo "gate_safe: $bot exposed for $(( $(date +%s) - start )) s"
