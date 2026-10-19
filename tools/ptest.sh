#!/bin/bash
# Submit BOT (copied from bots/SRC if given) and queue the 15-game panel, retrying on quota. Prints group ids.
cd "$(dirname "$0")/.."
powershell -File tools/bc.ps1 submit "$1" 2>&1 | tail -1 >&2
ids=""
for spec in "5095aa78-11de-4a63-ad5d-b30dae825f5e swirl,fragment,corners,packs,elkring" "3ad833e0-635d-4164-9f86-26d82c5f18b0 swirl,fragment,corners,packs,elkring" "36258abf-3fd0-4827-8fa5-2a217438cf6f rows,lanes,eight,stampede,expanse"; do
  set -- $spec
  until out=$(powershell -File tools/bc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do sleep 30; done
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
until ! python -I tools/group.py $ids 2>/dev/null | grep -qE 'queued|running'; do sleep 60; done
sleep 20
echo "$ids"
python -I tools/panel_result.py $ids | tail -3
