#!/bin/bash
# Extra 10 games vs two ~1700-rated teams for BOT already live. Prints group ids and summary.
cd "$(dirname "$0")/.."
ids=""
for spec in "05c4d857-1412-4c63-8c8e-ad05df77f193 collision,interlock,monolith,rushbait_v2,contest" "969212e5-03c6-4643-8015-e6c565e9ed6b ambush,pilgrimage,swirl,elkring,fragment"; do
  set -- $spec
  until out=$(powershell -File tools/bc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do sleep 30; done
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
until ! python -I tools/group.py $ids 2>/dev/null | grep -qE 'queued|running'; do sleep 60; done
sleep 20
echo "$ids"
python -I tools/panel_result.py $ids | tail -14
