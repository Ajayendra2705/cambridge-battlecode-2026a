#!/bin/bash
# Wait for a game patch: bash tools/platform/patchwatch.sh [MINUTES]
# Every MINUTES (default 10) checks the newest cambc release on PyPI, the CLI the platform publishes for download
# (/api/v1/distribution, the source `cambc` itself is fetched from) and the engine of the newest finished ranked match
# on the platform (its summary's engineVersion and engineBuildHash). Prints a line and exits as soon as one differs
# from the values when it started, so a background run gives one notification. Sprint 3 patch notes came on Discord
# (10-26) before the platform or the SDK changed; the platform engine moved to 2.0.0 at about 04:20 IST that day while
# PyPI and the distribution still had cambc 3.0.5.
cd "$(dirname "$0")/../.."
C="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
tmp=data/cache/patchwatch.json
mkdir -p data/cache
pypi() { python -m pip index versions cambc 2>/dev/null | grep -oE '^cambc \([0-9.]+\)' | grep -oE '[0-9.]+' ; }
dist() { curl -s -m 60 https://2026a.battlecode.co.uk/api/v1/distribution | python -I -c "import json,sys; print(next(p['published']['version'] for p in json.load(sys.stdin)['platforms'] if p['platform'] == 'windows-x64'))" 2>/dev/null ; }
engine() {
  for m in $("$C" matches list --kind ranked --limit 15 2>/dev/null | grep -E '^[0-9a-f-]{36}\s+finished' | cut -c1-36); do
    rm -f "$tmp"; "$C" matches summary "$m" --json -o "$tmp" > /dev/null 2>&1 || continue
    python -I -c "import json,sys; m=json.load(open(sys.argv[1],encoding='utf-8'))['match']; print(m['engineVersion'], m['engineBuildHash'][:12])" "$tmp" 2>/dev/null && return
  done
}
v0=$(pypi); d0=$(dist); e0=$(engine)
echo "start $(date '+%m-%d %H:%M'): pypi cambc $v0, distribution $d0, engine $e0"
while sleep $(( ${1:-10} * 60 )); do
  v=$(pypi); d=$(dist); e=$(engine)
  [ -n "$v" ] && [ "$v" != "$v0" ] && { echo "$(date '+%m-%d %H:%M') new cambc on PyPI: $v0 -> $v (engine $e)"; exit 0; }
  [ -n "$d" ] && [ "$d" != "$d0" ] && { echo "$(date '+%m-%d %H:%M') new cambc on the platform: $d0 -> $d (engine $e)"; exit 0; }
  [ -n "$e" ] && [ "$e" != "$e0" ] && { echo "$(date '+%m-%d %H:%M') platform engine changed: $e0 -> $e (pypi $v)"; exit 0; }
done
