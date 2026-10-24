#!/bin/bash
# Final chain, reordered 01:52: the sp3_b6 gate (gateq PID in $1) finishes first. ab2_b6 dropped: ab2 = sp1 + the guard
# fix, and sp1_b6 already has those games except boss_battle. No gate starts after 03:30 IST.
cd "$(dirname "$0")/.."
while [ -e /proc/$1 ]; do sleep 15; done
run() { [ "$(date +%H%M)" -lt 0330 ] || return; echo "$1 $2" > data/gate_queue.txt; GATE_SPECS="$(cat data/specs_$3.txt)" GATE_PANEL=$3 bash tools/platform/gateq.sh >> data/gateq_b1.log 2>&1; }
run exp/cf1 cf1_b56 b56
run exp/ab2 ab2_b5 b5
run exp/dr3g dr3g_b56 b56
run exp/sp3 sp3_b5 b5
echo CHAIN8 DONE >> data/gateq_b1.log
