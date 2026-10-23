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
# Panel 2 (2026-10-21): ladder neighbours above us, ranks 30-78 (1884-1761 rating); we were 95 at 1740.
opps = ['7b219a14-b935-46b6-8c2d-ad2aaaf21f25', 'bed04918-82d1-40d2-ba15-b977a2906943', '589be06f-219f-4af6-9139-cd1109c62316',
        'f9d72b03-4526-4213-bc2f-afbf06f2a933', 'd4086267-bcda-495e-b632-4b7ab155fbf4', '2dba5fac-6e54-493c-8f0e-d7a32d898d9a',
        '6d389a3b-413e-451e-b7d0-f1c6b9b34e51', '30d8d10c-a7ce-4449-a394-42a76621c1db', '1e25877b-9ea9-4821-bd54-236e44c5e650']
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
echo "$bot@p2${GATE_OFFSET:+@$GATE_OFFSET}$ids" >> tools/gate.log
until [ "$(python -I tools/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/panel_result.py $ids | tail -3
