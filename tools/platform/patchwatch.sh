#!/bin/bash
# Wait for a game patch: bash tools/platform/patchwatch.sh [MINUTES]
# Every MINUTES (default 10) checks the newest cambc release on PyPI and the engine of the newest finished ranked match
# on the platform (its summary's engineVersion and engineBuildHash). Prints a line and exits as soon as either differs
# from the values when it started, so a background run gives one notification. Sprint 3 patch notes came on Discord
# (10-26) before the platform or the SDK changed; this tells when they land.
cd "$(dirname "$0")/../.."
C="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
tmp=data/cache/patchwatch.json
mkdir -p data/cache
pypi() { python -m pip index versions cambc 2>/dev/null | grep -oE '^cambc \([0-9.]+\)' | grep -oE '[0-9.]+' ; }
engine() {
  for m in $("$C" matches list --kind ranked --limit 15 2>/dev/null | grep -E '^[0-9a-f-]{36}\s+finished' | cut -c1-36); do
    rm -f "$tmp"; "$C" matches summary "$m" --json -o "$tmp" > /dev/null 2>&1 || continue
    python -I -c "import json,sys; m=json.load(open(sys.argv[1],encoding='utf-8'))['match']; print(m['engineVersion'], m['engineBuildHash'][:12])" "$tmp" 2>/dev/null && return
  done
}
v0=$(pypi); e0=$(engine)
echo "start $(date '+%m-%d %H:%M'): pypi cambc $v0, engine $e0"
while sleep $(( ${1:-10} * 60 )); do
  v=$(pypi); e=$(engine)
  [ -n "$v" ] && [ "$v" != "$v0" ] && { echo "$(date '+%m-%d %H:%M') new cambc on PyPI: $v0 -> $v (engine $e)"; exit 0; }
  [ -n "$e" ] && [ "$e" != "$e0" ] && { echo "$(date '+%m-%d %H:%M') platform engine changed: $e0 -> $e (pypi $v)"; exit 0; }
done
