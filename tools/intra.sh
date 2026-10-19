#!/bin/bash
# Intra-team round robin: every pair of the given bots plays all maps on both sides locally.
# Prints one line per pair (wins of the first bot out of the games played) and a final table of total wins.
cd "$(dirname "$0")/.."
bots=("$@")
declare -A total
for ((i = 0; i < ${#bots[@]}; i++)); do
  for ((j = i + 1; j < ${#bots[@]}; j++)); do
    a=${bots[i]} b=${bots[j]}
    line=$(python -I tools/batch.py "$a" "$b" --jobs 10 2>&1 | tail -1)
    w=$(echo "$line" | sed -E 's/.*wins ([0-9]+)\/([0-9]+).*/\1/') n=$(echo "$line" | sed -E 's/.*wins ([0-9]+)\/([0-9]+).*/\2/')
    echo "$a vs $b: $line"
    total[$a]=$(( ${total[$a]:-0} + w )) total[$b]=$(( ${total[$b]:-0} + n - w ))
  done
done
echo "== total wins"
for b in "${bots[@]}"; do echo "${total[$b]} $b"; done | sort -rn
