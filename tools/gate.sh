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
maps = 'rows corners packs stampede contest lanes eight expanse swirl fragment elkring interlock monolith collision pilgrimage ambush rushbait_v2'.split()
opps = ['1890540d-1ffc-4847-adbf-d0d08772f268', '36258abf-3fd0-4827-8fa5-2a217438cf6f', '5095aa78-11de-4a63-ad5d-b30dae825f5e',
        '772c398c-6856-4e72-a709-a20db9f67569', '3ad833e0-635d-4164-9f86-26d82c5f18b0', '05c4d857-1412-4c63-8c8e-ad05df77f193',
        '969212e5-03c6-4643-8015-e6c565e9ed6b', '66548120-e844-40b2-baff-9badde2a1f5a', '598ea864-6da9-41d1-984f-63136069bc50']
for k, o in enumerate(opps):
    m = [maps[(2 * k + off + j) % 17] for j in range(10)]
    print(o + ':' + ','.join(m[:5]))
    print(o + ':' + ','.join(m[5:]))
PY
)
for spec in $specs; do
  set -- ${spec/:/ }
  until out=$(powershell -File tools/bc.ps1 match-groups create $1 --maps "$2" --json 2>&1 | tail -1) && echo "$out" | grep -q groupId; do sleep 30; done
  ids="$ids $(echo "$out" | python -c "import sys,json; print(json.loads(sys.stdin.read())['groupId'])")"
done
echo "$bot${GATE_OFFSET:+@$GATE_OFFSET}$ids" >> tools/gate.log
until [ "$(python -I tools/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge 90 ]; do sleep 60; done
sleep 20
echo "$bot$ids"
python -I tools/panel_result.py $ids | tail -3
