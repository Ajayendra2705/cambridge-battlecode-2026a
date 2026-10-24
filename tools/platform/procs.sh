#!/bin/bash
# List running gate, chain and local-run processes: bash tools/platform/procs.sh [kill]
# Git Bash `ps` shows only /usr/bin/bash, not the command line, so a `ps | grep gateq` kill matches nothing (2026-10-25:
# two gate chains ran at once that way). This reads /proc/PID/cmdline instead. With "kill", it stops them all.
for p in /proc/[0-9]*; do
  c=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null) || continue
  case "$c" in
    *procs.sh*) ;;
    *gatechain.sh*|*gateq.sh*|*gate.sh*|*gate_full.sh*|*multi.py*|*rr.py*)
      echo "${p#/proc/} ppid=$(awk '{print $4}' "$p/stat" 2>/dev/null) :: ${c:0:100}"
      [ "$1" = kill ] && kill "${p#/proc/}" 2>/dev/null ;;
  esac
done
