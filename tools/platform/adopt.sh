#!/bin/bash
# Make bots/exp/NEW the ladder bot: bash tools/platform/adopt.sh NEW OLD_NAME
# Moves the current bots/main to bots/pool/OLD_NAME, copies bots/exp/NEW over bots/main (without .cambc), runs one
# local game as a build check and submits main until the platform answers "Submitted". Refuses while a gate runs
# (the gate would resubmit or replace main mid-way). Afterwards: docs/lineage.md, docs/status.md, docs/experiments.md.
set -e
cd "$(dirname "$0")/../.."
new="$1"; old="$2"
[ -n "$new" ] && [ -n "$old" ] || { echo "usage: adopt.sh NEW OLD_NAME"; exit 1; }
[ -d "bots/exp/$new" ] || { echo "no bots/exp/$new"; exit 1; }
[ -e "bots/pool/$old" ] && { echo "bots/pool/$old exists"; exit 1; }
[ -n "$(bash tools/platform/procs.sh | grep -E 'gateq|gate\.sh|gatechain')" ] && { echo "a gate is running"; exit 1; }
mv bots/main "bots/pool/$old"
rm -rf "bots/pool/$old/.cambc"
cp -r "bots/exp/$new" bots/main
rm -rf bots/main/.cambc
python -I tools/local/multi.py main --pool pool/tf3 --maps 00ambush --jobs 2 | grep -E "^main|error" || true
until powershell -File tools/cambc.ps1 submit main 2>&1 | tail -1 | tee /dev/stderr | grep -q Submitted; do sleep 30; done
