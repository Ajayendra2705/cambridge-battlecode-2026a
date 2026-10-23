#!/bin/bash
# Test gate panel: submit BOT (pass "nosubmit" as 2nd arg to skip) and play 90 unranked games (10 maps each) vs nine teams
# spread from rank 1 to just above us. Group ids are appended to results/gate.log as "BOT ids...".
# Compare two runs with: python -I tools/platform/rcmp.py OLD NEW   (run them back to back; opponents change bots)
cd "$(dirname "$0")/../.."
bot=$1
[ "$2" = "nosubmit" ] || powershell -File tools/cambc.ps1 submit "$bot" 2>&1 | tail -1 >&2
ids=""
# GATE_OFFSET (default 0) shifts every opponent's map window, giving a fresh sample of games.
specs=$(python -I - "${GATE_OFFSET:-0}" <<'PY'
import os, sys
off = int(sys.argv[1])
maps = ('00corners 01hooks 00contest 01gold_rush 00lanes 01islands 00eight 01boss_battle 00expanse 01broken_curve 00fragment '
        '01big_world 00elkring 01concentrated_wealth 00interlock 01corridors 00monolith 01elk_arena 00collision 01fracture 00ambush '
        '00packs 01shortcut 00pilgrimage 01starfish 00quadrants 01starvation 00reverse_spiral 01the_farm 00rows 01yellow_brick_road '
        '00rushbait_v2 00split 00stampede 00swirl 00gem_fields 00gemfight 00great_wall 00lost_world 00road_of_riches').split()
# Panel 8 (2026-10-23 02:50 IST): ladder ranks 60-69 (1838-1817): bentheboss, PENTAKILL, team, SkibidiSloppers, kitfunso,
# meow, Patient Builder, KratosMessi, Hidden Altar Keepers, Gem Simons (we are rank 70, 1817).
opps = ['a4247250-fa1e-4d33-811d-d94667bf7a2b', '6fd448fc-cec3-4dc1-8d6a-b384b1127d47', '5711f738-37e5-4e2c-a6d5-4554a1078440', '67e6d408-0d7f-4f95-af3d-c2b7bad5e8aa', 'b6eddc2e-0bba-4bb8-ab8b-0938ba05f6b4', 'f6e2d7fe-9ae5-44b6-b4ad-a79d2443cb89', '38a622d3-32ed-490d-b78a-cf93ab734a6a', '6599a236-7801-436f-a863-4acbb6aafa91', '19a21cd3-4d97-4bbb-adb6-242bf2d676ff', '772c398c-6856-4e72-a709-a20db9f67569']
for k, o in enumerate(opps):
    m = [maps[(2 * k + off + j) % len(maps)] for j in range(10)]
    print(o + ':' + ','.join(m[:5]))
    if os.environ.get('GATE_HALF') != '1': print(o + ':' + ','.join(m[5:]))
PY
)
for spec in $specs; do
  set -- ${spec/:/ }
  until out=$(powershell -File tools/cambc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do
    echo "$out" | grep -q "eligible bot" && { echo "skip $1: $out" >&2; break; }
    sleep 30
  done
  echo "$out" | grep -q groupId || continue
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
echo "$bot@p8${GATE_OFFSET:+@$GATE_OFFSET}$ids" >> results/gate.log
until [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/platform/panel_result.py $ids | tail -3
