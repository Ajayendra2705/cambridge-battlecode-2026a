#!/bin/bash
# Submit a bot and queue the fixed 15-game panel. Prints group ids on one line.
cd "$(dirname "$0")/.."
powershell -File tools/bc.ps1 submit "$1" 2>&1 | tail -1 >&2
sleep 60
ids=""
for spec in "5095aa78-11de-4a63-ad5d-b30dae825f5e swirl,fragment,corners,packs,elkring" "3ad833e0-635d-4164-9f86-26d82c5f18b0 swirl,fragment,corners,packs,elkring" "36258abf-3fd0-4827-8fa5-2a217438cf6f rows,lanes,eight,stampede,expanse"; do
  set -- $spec
  id=$(powershell -File tools/bc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1 | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")
  ids="$ids $id"
done
echo $ids
