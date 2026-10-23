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
# Panel 4 (2026-10-22 14:30 IST): ladder ranks 20-28 (1966-1921).
opps = ['cfa40068-99c1-4038-b52d-b9ed4c10f9fb', '4851bec0-9af2-4413-a07b-c70bbb4cde21', '1570a113-57fd-4f15-84fb-0d764b12799b',
        '21b63196-9d0e-436f-bf5d-25c55bdc4eaf', 'ec2b57be-fa43-4e3e-9eb0-57b266624d27', 'd559d741-ac53-411e-bc4e-36b8f3d12d5a',
        '40cf616f-378f-48c7-b381-fe323bce3773', '6fd448fc-cec3-4dc1-8d6a-b384b1127d47', '4d0fe2ae-015f-4365-9705-463ff71e4291']
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
echo "$bot@p4${GATE_OFFSET:+@$GATE_OFFSET}$ids" >> tools/gate.log
until [ "$(python -I tools/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/panel_result.py $ids | tail -3
