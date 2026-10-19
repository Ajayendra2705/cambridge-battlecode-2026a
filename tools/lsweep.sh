#!/bin/bash
# Local sweep: each line of tools/lsweep.txt (name#old#new) makes a one-substitution variant of BASE, which plays
# all maps on both sides against every bot in POOL. Prints total wins per variant; BASE itself is the reference.
# usage: bash tools/lsweep.sh BASE "pool bots" [extra existing bots to score]
cd "$(dirname "$0")/.."
base=$1; pool=$2; extra=$3
score() {
  local total=0 games=0
  for opp in $pool; do
    line=$(python -I tools/batch.py "$1" $opp --jobs ${JOBS:-10} 2>&1 | tail -1)
    w=$(echo "$line" | sed -E 's/.*wins ([0-9]+)\/([0-9]+).*/\1/'); n=$(echo "$line" | sed -E 's/.*wins ([0-9]+)\/([0-9]+).*/\2/')
    total=$((total + ${w:-0})); games=$((games + ${n:-0}))
  done
  echo "$total/$games $1"
}
score "$base"
for b in $extra; do score "$b"; done
while IFS='#' read -r name old new; do
  [ -z "$name" ] && continue
  python -I tools/mkvar.py "$base" "$name" bot.cpp "$old" "$new" >/dev/null || { echo "skip $name"; continue; }
  score "$name"
done < "${LIST:-tools/lsweep.txt}"
