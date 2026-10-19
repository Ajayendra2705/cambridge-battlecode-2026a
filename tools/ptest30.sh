#!/bin/bash
# Submit BOT (optional: pass "nosubmit" as 2nd arg) and run a 30-game panel vs six ~1700-rated teams.
cd "$(dirname "$0")/.."
[ "$2" = "nosubmit" ] || powershell -File tools/bc.ps1 submit "$1" 2>&1 | tail -1 >&2
ids=""
for spec in "5095aa78-11de-4a63-ad5d-b30dae825f5e swirl,fragment,corners,packs,elkring" \
            "3ad833e0-635d-4164-9f86-26d82c5f18b0 eight,collision,contest,pilgrimage,rows" \
            "36258abf-3fd0-4827-8fa5-2a217438cf6f rows,lanes,eight,stampede,expanse" \
            "05c4d857-1412-4c63-8c8e-ad05df77f193 collision,interlock,monolith,rushbait_v2,contest" \
            "969212e5-03c6-4643-8015-e6c565e9ed6b ambush,pilgrimage,swirl,elkring,fragment" \
            "772c398c-6856-4e72-a709-a20db9f67569 packs,corners,lanes,interlock,monolith"; do
  set -- $spec
  until out=$(powershell -File tools/bc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do sleep 30; done
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
until ! python -I tools/group.py $ids 2>/dev/null | grep -qE 'queued|running'; do sleep 60; done
sleep 20
echo "$ids"
python -I tools/panel_result.py $ids | tail -3
