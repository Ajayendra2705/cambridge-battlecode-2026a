#!/bin/bash
# Test gate panel: submit BOT (pass "nosubmit" as 2nd arg to skip) and play 90 unranked games (10 maps each) vs nine teams
# spread from rank 1 to just above us. Group ids are appended to tools/gate.log as "BOT ids...".
# Compare two runs with: python -I tools/paired.py OLD NEW   (run them back to back; opponents change bots)
cd "$(dirname "$0")/.."
bot=$1
[ "$2" = "nosubmit" ] || powershell -File tools/bc.ps1 submit "$bot" 2>&1 | tail -1 >&2
ids=""
# GATE_OFFSET (default 0) shifts every opponent's map window, giving a fresh sample of games.
specs=$(python -I - "${GATE_OFFSET:-0}" <<'PY'
import os, sys
off = int(sys.argv[1])
maps = ('00corners 01hooks 00contest 01gold_rush 00lanes 01islands 00eight 01boss_battle 00expanse 01broken_curve 00fragment '
        '01big_world 00elkring 01concentrated_wealth 00interlock 01corridors 00monolith 01elk_arena 00collision 01fracture 00ambush '
        '00packs 01shortcut 00pilgrimage 01starfish 00quadrants 01starvation 00reverse_spiral 01the_farm 00rows 01yellow_brick_road '
        '00rushbait_v2 00split 00stampede 00swirl 00gem_fields 00gemfight 00great_wall 00lost_world 00road_of_riches').split()
# Panel 3 (2026-10-22): ladder top 10 except :3 (already in panel 2).
opps = ['1890540d-1ffc-4847-adbf-d0d08772f268', '8df7e1cd-0d60-413b-9331-f5427ce9ca88', 'a1e82708-dfd3-4609-8b9a-69f652d12185',
        '26824601-d225-427f-bd2d-ce8aa9faa392', '547efb5b-57e5-4355-8501-3b331f506d62', '3ec4a701-a9b5-498f-9361-eea4a6dd1cde',
        '36258abf-3fd0-4827-8fa5-2a217438cf6f', '93fd07ff-2f73-4ed4-9911-356cc1034ba5', '882106d4-9deb-40cc-9d5c-8522c1d32129']
for k, o in enumerate(opps):
    m = [maps[(2 * k + off + j) % len(maps)] for j in range(10)]
    print(o + ':' + ','.join(m[:5]))
    if os.environ.get('GATE_HALF') != '1': print(o + ':' + ','.join(m[5:]))
PY
)
for spec in $specs; do
  set -- ${spec/:/ }
  until out=$(powershell -File tools/bc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do
    echo "$out" | grep -q "eligible bot" && { echo "skip $1: $out" >&2; break; }
    sleep 30
  done
  echo "$out" | grep -q groupId || continue
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
echo "$bot@p3${GATE_OFFSET:+@$GATE_OFFSET}$ids" >> tools/gate.log
until [ "$(python -I tools/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/panel_result.py $ids | tail -3
