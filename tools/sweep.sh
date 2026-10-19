#!/bin/bash
# Panel-test a list of one-substitution variants of bots/main, then resubmit RESTORE.
# usage: bash tools/sweep.sh RESTORE  (variants are read from tools/sweep.txt: name#old#new per line)
cd "$(dirname "$0")/.."
restore="$1"
while IFS='#' read -r name old new; do
  [ -z "$name" ] && continue
  rm -rf "bots/$name"
  python tools/variant.py "$name" < /dev/null --sub bot.cpp "$old" "$new" || { echo "$name variant failed"; continue; }
  res=$(timeout 1500 bash tools/ptest30.sh "$name" < /dev/null 2>&1 | tail -2 | tr '\n' ' ')
  echo "$(date +%H:%M) $name $res" >> replays/sweep.log
done < tools/sweep.txt
powershell -File tools/bc.ps1 submit "$restore" 2>&1 | tail -1 >> replays/sweep.log
