#!/bin/bash
# Read only: watch_live.sh VERSION [HHMM]. Ends and reports as soon as the active or selected version is not VERSION, or at HHMM (IST),
# so the session can act on the live-slot rule in CLAUDE.md. A newly uploaded version counts as a change.
want=$1
until=${2:-}
C="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
while :; do
  r=$("$C" submissions list --json 2>/dev/null | python -I -c "
import json,sys
s=sys.stdin.read()
d=json.loads(s[s.index('{'):])
print((d.get('active') or {}).get('version'),(d.get('selected') or {}).get('version'),d['submissions'][0]['version'])" 2>/dev/null | tr -d '\r')
  if [ -n "$r" ]; then
    set -- $r
    if [ "$1" != "$want" ] || [ "$2" != "$want" ]; then echo "$(date +%H:%M:%S) active $1 selected $2 newest $3"; exit 0; fi
  fi
  if [ -n "$until" ] && [ "$(date +%H%M)" -ge "$until" ]; then echo "$(date +%H:%M:%S) no change: active and selected $want"; exit 0; fi
  sleep 20
done
