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
import sys
off = int(sys.argv[1])
maps = ('00corners 01hooks 00contest 01gold_rush 00lanes 01islands 00eight 01boss_battle 00expanse 01broken_curve 00fragment '
        '01big_world 00elkring 01concentrated_wealth 00interlock 01corridors 00monolith 01elk_arena 00collision 01fracture 00ambush').split()
# Engine 3.0 panel (2026-10-20): teams with post-patch bots, ranks 3, 6, 19, 40, 70, 100, 155, 220, 255.
opps = ['6f7fd199-4115-4fe0-8752-525bd8ccad8d', '59f5706f-16db-4ae0-bb3f-deadb41cdc50', '36258abf-3fd0-4827-8fa5-2a217438cf6f',
        '2728f025-48ee-4adb-bd24-d7d26878a47e', 'c5fe98e9-c795-4c67-a36b-2c66bac443e8', '5d63d901-6a2a-4bcb-9487-f1315b1fd76d',
        '4f0fd54e-7c31-4763-b989-b47ad1061876', '7bbbe71d-04d3-453a-9cf7-34f698c93fca', '944811b7-2ee8-43df-9167-735e811713fe']
for k, o in enumerate(opps):
    m = [maps[(2 * k + off + j) % len(maps)] for j in range(10)]
    print(o + ':' + ','.join(m[:5]))
    print(o + ':' + ','.join(m[5:]))
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
echo "$bot${GATE_OFFSET:+@$GATE_OFFSET}$ids" >> tools/gate.log
until [ "$(python -I tools/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $(( $(echo $ids | wc -w) * 5 )) ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/panel_result.py $ids | tail -3
