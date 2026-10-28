#!/bin/bash
# List running gate, chain, local-run and replay-decode processes: bash tools/platform/procs.sh [kill]
# Git Bash `ps` shows only /usr/bin/bash, not the command line, so a `ps | grep gateq` kill matches nothing (2026-10-25:
# two gate chains ran at once that way). This reads /proc/PID/cmdline instead. With "kill", it stops them all.
# Decode jobs count too: a session's background decode chain outlives the session (10-25: a second decoder of the same
# runs was started beside one left by the previous session).
# Runner and judge scripts (`*/run_*.sh`, `*/judge_*.sh`) count too: a `cmd &` inside an agent's tool call outlives the
# call, and on 10-29 a second copy of a runner that this list did not show started a duplicate chain.
for p in /proc/[0-9]*; do
  c=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null) || continue
  case "$c" in
    *procs.sh*) ;;
    *gatechain.sh*|*gateq.sh*|*gate.sh*|*gate_full.sh*|*multi.py*|*rr.py*|*decode_run.sh*|*decode_chain*|*after_run*|*gdl.py*|*/run_*.sh*|*/judge_*.sh*)
      echo "${p#/proc/} ppid=$(awk '{print $4}' "$p/stat" 2>/dev/null) :: ${c:0:100}"
      [ "$1" = kill ] && kill "${p#/proc/}" 2>/dev/null ;;
  esac
done
