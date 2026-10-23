#!/bin/bash
# Block until the unranked quota has at least N (default 9) free match groups: bash tools/platform/qwait.sh [N]
cd "$(dirname "$0")/../.."
need=${1:-9}
while :; do
  free=$(powershell -File tools/cambc.ps1 match-groups quota --json 2>/dev/null | python -c "
import sys,json
s=sys.stdin.read(); j=json.loads(s[s.index('{'):]) if '{' in s else {}
q=j.get('quota',{}); print(q.get('limit',0)-q.get('used',99))" 2>/dev/null)
  [ -n "$free" ] && [ "$free" -ge "$need" ] && break
  sleep 30
done
