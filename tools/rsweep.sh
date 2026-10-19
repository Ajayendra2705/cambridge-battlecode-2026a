#!/bin/bash
# Farming sweep: one-substitution variants of BASE (lines name#old#new in LIST) raced against the starter bot
# on all maps, one side. Prints the average finishing round (lower is better); BASE is printed first.
cd "$(dirname "$0")/.."
base=$1; list=${2:-tools/rsweep.txt}
race() { echo "$(python -I tools/batch.py "$1" starter-cpp --jobs ${JOBS:-12} --one-side 2>&1 | tail -1 | sed -E 's/.*avg round \(loss=2000\) ([0-9]+).*/\1/') $1"; }
race "$base"
while IFS='#' read -r name old new; do
  [ -z "$name" ] && continue
  python -I tools/mkvar.py "$base" "$name" bot.cpp "$old" "$new" >/dev/null || { echo "skip $name"; continue; }
  race "$name"
done < "$list"
