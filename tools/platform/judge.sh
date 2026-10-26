#!/bin/bash
# Judge a b9p run against a base b9p run: wait for 120 results, compare, decode (8 jobs), print the metrics.
# Usage: bash tools/platform/judge.sh RUN BASE   (both without @b9p, e.g. hc1_b9p dq3_b9p); output to a file
cd "$(dirname "$0")/../.."
run="$1"; base="$2"
until grep -q "^$run@b9p " results/gate.log; do sleep 20; done
ids=$(grep "^$run@b9p " results/gate.log | tail -1 | cut -d' ' -f2-)
until [ "$(python -I tools/platform/group.py $ids 2>/dev/null | grep -cE 'WIN|loss')" -ge 120 ]; do sleep 20; done
sleep 20
python -I tools/platform/rcmp.py "$base@b9p" "$run@b9p" 2>&1 | tail -4
bash tools/replay/decode_run.sh "$run@b9p" 11 2>&1 | tail -1
for d in "${base}_b9p" "${run}_b9p"; do
  echo "== $d"
  python -I tools/replay/decoded.py holds "data/fights/$d" | tail -2
  python -I tools/replay/decoded.py captures "data/fights/$d" | sed -n 2,3p
  python -I tools/replay/decoded.py gems "data/fights/$d" --round 600 1000 | cut -c1-150
  python -I tools/replay/decoded.py gold "data/fights/$d" --round 600 | sed -n 2p
done
python -I tools/replay/bysize.py "data/fights/${base}_b9p" "data/fights/${run}_b9p"
