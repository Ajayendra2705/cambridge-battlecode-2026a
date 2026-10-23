#!/bin/bash
# Play BOT against every line of tools/loss_spec.txt (submits BOT first), logged as BOT@L6 in tools/gate.log.
cd "$(dirname "$0")/.."
bot=$1
powershell -File tools/bc.ps1 submit "$bot" 2>&1 | tail -1
ids=""
while IFS=: read opp maps sides; do
  for try in 1 2 3 4 5 6; do
    out=$(powershell -File tools/bc.ps1 match-groups create $opp --maps "$maps" --json 2>&1 | tail -1)
    id=$(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read()).get('groupId',''))" 2>/dev/null)
    [ -n "$id" ] && break
    sleep 5
  done
  [ -z "$id" ] && echo "FAILED $opp: $out"
  ids="$ids $id"
done < "${SPEC:-tools/loss_spec.txt}"
echo "$bot@${TAG:-L6}$ids" >> tools/gate.log
echo "$bot@${TAG:-L6} groups: $(echo $ids | wc -w)"
