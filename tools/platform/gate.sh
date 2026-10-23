#!/bin/bash
# Small test gate: submit BOT (pass "nosubmit" as 2nd arg to skip) and play 20 unranked games (4 groups of 5). Group ids are appended to results/gate.log as "BOT ids...".
# Compare two runs with: python -I tools/platform/rcmp.py OLD NEW   (run them back to back; opponents change bots)
cd "$(dirname "$0")/../.."
bot=$1
[ "$2" = "nosubmit" ] || powershell -File tools/cambc.ps1 submit "$bot" 2>&1 | tail -1 >&2
ids=""
# 20-game panel (user 2026-10-23: keep tests ~20 games). Groups must have exactly 5 maps, so: 4 panel-8 opponents x their
# first @20 map window, chosen as the 4 groups whose outcomes varied most across hb4l, hb4l2, fp1l, th2l, bt8l @p8@20
# (most sensitive games). Same (opponent, map) games as gate8 @20, so rcmp can compare with full-panel runs.
specs="b6eddc2e-0bba-4bb8-ab8b-0938ba05f6b4:01the_farm,00rows,01yellow_brick_road,00rushbait_v2,00split
38a622d3-32ed-490d-b78a-cf93ab734a6a:00split,00stampede,00swirl,00gem_fields,00gemfight
67e6d408-0d7f-4f95-af3d-c2b7bad5e8aa:01starvation,00reverse_spiral,01the_farm,00rows,01yellow_brick_road
a4247250-fa1e-4d33-811d-d94667bf7a2b:00ambush,00packs,01shortcut,00pilgrimage,01starfish"
for spec in $specs; do
  set -- ${spec/:/ }
  until out=$(powershell -File tools/cambc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do
    echo "$out" | grep -q "eligible bot" && { echo "skip $1: $out" >&2; break; }
    echo "retry $1: $out" >&2; sleep 30
  done
  echo "$out" | grep -q groupId || continue
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
echo "$bot@p8s$ids" >> results/gate.log
until [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/platform/panel_result.py $ids | tail -3
