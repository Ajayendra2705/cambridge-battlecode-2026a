#!/bin/bash
# Candidate vs a pool of earlier versions on all maps, both sides. Prints total wins.
cd "$(dirname "$0")/.."
total=0; games=0
for opp in c9 c12 c14 c15; do
  line=$(python -I tools/batch.py "$1" $opp --jobs 10 2>&1 | tail -1)
  w=$(echo "$line" | sed -E 's/wins ([0-9]+)\/([0-9]+).*/\1/'); n=$(echo "$line" | sed -E 's/wins ([0-9]+)\/([0-9]+).*/\2/')
  echo "vs $opp: $w/$n"
  total=$((total + w)); games=$((games + n))
done
echo "pool total $total/$games"
