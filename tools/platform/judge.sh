#!/bin/bash
# Judge a run against a base run: wait for all its results, compare, decode (11 jobs), print the metrics.
# Usage: bash tools/platform/judge.sh RUN BASE   (RUN@PANEL and BASE@PANEL, e.g. sc1_b10p@b10p mw1_b10@b10; a name
# without @ means @b9p, e.g. hc1_b9p dq3_b9p); output to a file
cd "$(dirname "$0")/../.."
run="$1"; base="$2"
[[ "$run" == *@* ]] || run="$run@b9p"
[[ "$base" == *@* ]] || base="$base@b9p"
until grep -q "^$run " results/gate.log; do sleep 20; done
ids=$(grep "^$run " results/gate.log | tail -1 | cut -d' ' -f2-)
games=$(( $(echo $ids | wc -w) * 5 ))
until [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge $games ]; do sleep 20; done
sleep 20
python -I tools/platform/rcmp.py "$base" "$run" 2>&1 | tail -4
bash tools/replay/decode_run.sh "$run" 11 2>&1 | tail -1
for d in "${base/@/_}" "${run/@/_}"; do
  echo "== $d"
  python -I tools/replay/decoded.py holds "data/fights/$d" | tail -2
  python -I tools/replay/decoded.py captures "data/fights/$d" | sed -n 2,3p
  python -I tools/replay/decoded.py gems "data/fights/$d" --round 600 1000 | cut -c1-150
  python -I tools/replay/decoded.py gold "data/fights/$d" --round 600 | sed -n 2p
done
python -I tools/replay/bysize.py "data/fights/${base/@/_}" "data/fights/${run/@/_}"
python -I tools/replay/paired.py "$base" "$run" 1000 2>&1 | tail -13
