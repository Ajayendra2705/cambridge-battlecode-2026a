#!/bin/bash
# Wait until every group of RUN (results/gate.log) has 5 finished matches.
cd "$(dirname "$0")/../.."
ids=$(grep "^$1 " results/gate.log | tail -1 | cut -d' ' -f2-)
C="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
while true; do
  done_n=0
  for g in $ids; do
    n=$("$C" match-groups show $g 2>/dev/null | grep -c " finished ")
    [ "$n" -ge 5 ] && done_n=$((done_n+1))
  done
  echo "$(date +%H:%M) $done_n/$(echo $ids | wc -w)"
  [ "$done_n" -ge "$(echo $ids | wc -w)" ] && break
  sleep 90
done
