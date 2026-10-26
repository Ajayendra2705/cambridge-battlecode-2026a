#!/bin/bash
# Small test gate: bash tools/platform/gate.sh BOT [submit|nosubmit] [RUN_NAME]. Submits BOT (unless nosubmit) and plays 20 unranked
# games (4 groups of 5 maps). Appends "RUN_NAME@p8s group-ids..." to results/gate.log (RUN_NAME defaults to the bot name).
# Compare two runs with: python -I tools/platform/rcmp.py OLD NEW   (run them back to back; opponents change bots)
cd "$(dirname "$0")/../.."
bot=$1
name=${3:-${bot##*/}}  # run name in results/gate.log: 3rd arg, else the bot name without its folder
# A failed submit (upload limit: 20 bots per hour) would play the games with whatever bot is on the platform: abort.
if [ "$2" != "nosubmit" ]; then
  out=$(powershell -File tools/cambc.ps1 submit "$bot" 2>&1 | tail -1); echo "$out" >&2
  echo "$out" | grep -q "Submitted" || { echo "submit failed, gate aborted" >&2; exit 3; }
fi
ids=""
# Default: the 20-game p8s panel, 4 groups of 5 maps (the most sensitive p8 games; user 2026-10-23: tests ~20 games).
# A pinned panel (specs_b9p.txt) ends each line with a match group id taken from one base run.
specs=${GATE_SPECS:-"b6eddc2e-0bba-4bb8-ab8b-0938ba05f6b4:01the_farm,00rows,01yellow_brick_road,00rushbait_v2,00split
38a622d3-32ed-490d-b78a-cf93ab734a6a:00split,00stampede,00swirl,00gem_fields,00gemfight
67e6d408-0d7f-4f95-af3d-c2b7bad5e8aa:01starvation,00reverse_spiral,01the_farm,00rows,01yellow_brick_road
a4247250-fa1e-4d33-811d-d94667bf7a2b:00ambush,00packs,01shortcut,00pilgrimage,01starfish"}
for spec in $specs; do
  set -- ${spec//:/ }  # TEAM:MAP,MAP,MAP,MAP,MAP[:SIDE,SIDE,SIDE,SIDE,SIDE[:GROUP]] (our side per game, default a;
  # GROUP: play the opponent's bot from that earlier match group, so every run meets the same versions)
  until out=$(powershell -File tools/cambc.ps1 match-groups create $1 --maps "$2" ${3:+--sides "$3"} ${4:+--source-group $4} --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do
    echo "$out" | grep -q "eligible bot" && { echo "skip $1: $out" >&2; break; }
    echo "retry $1: $out" >&2; sleep 30
  done
  echo "$out" | grep -q groupId || continue
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
echo "$name@${GATE_PANEL:-p8s}$ids" >> results/gate.log
until [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 20; done
sleep 20
echo "$bot$ids"
python -I tools/platform/panel_result.py $ids | tail -3
