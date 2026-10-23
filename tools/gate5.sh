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
# Panel 5 (2026-10-22 15:00 IST): ladder ranks 30-49 (1910-1850).
opps = ['5a103c90-b00b-4d46-8ace-6a3bb058dc72', 'ee3e7b98-f09f-46b9-8e52-348e3d07f551', '56169cfe-e8dc-45ae-815c-f2fa45368296',
        '34b36bab-66bb-4506-b032-2df6a081758d', '975c2c15-506b-489b-a439-839c8145933b', 'f9d72b03-4526-4213-bc2f-afbf06f2a933',
        'f5d4d2c9-efe4-415b-b08a-99cff7ab0c78', '83798ea3-f051-43ed-933d-e0bced90992b', '958beb45-6e30-4c1d-a250-be7052ee7566']
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
echo "$bot@p5${GATE_OFFSET:+@$GATE_OFFSET}$ids" >> tools/gate.log
until [ "$(python -I tools/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/panel_result.py $ids | tail -3
