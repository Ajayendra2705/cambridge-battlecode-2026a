#!/bin/sh
# queuelatest.sh TAG SPECFILE : like bench2qs.sh but WITHOUT --source-group - each line's opponent plays its CURRENT live bot (Eric, Nov 1
# ~10:00: "use the opponents latest bots"). Same maps and sides as the spec. Group ids into scrim_TAG.ids; retries while the hourly quota is full.
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
C="${CAMBC:-$LOCALAPPDATA/cambc/bin/cambc-4.0.0.exe}"
T=$1; SPEC=$2; : > "$SP/scrim_$T.ids"
while read line; do
  set -- $line; team=$1; maps=$2; side=$3; sidesarg=$4
  [ -z "$team" ] && continue
  for try in $(seq 1 60); do
    out=$(timeout 120 "$C" match-groups create "$team" --maps "$maps" $( [ "$side" = "--sides" ] && echo "--sides $sidesarg" || echo "${side:+--side $side}") --json 2>&1)
    id=$(echo "$out" | grep -o '"groupId": *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
    if [ -n "$id" ]; then echo "$id" >> "$SP/scrim_$T.ids"; break; fi
    case "$out" in *"eligible bot"*|*"HTTP 409"*|*"not found"*) echo "skip $team: $out" >&2; break ;; esac
    echo "retry $try: $(echo "$out" | tail -1)" >&2
    sleep 60
  done
done < "$SPEC"
date -u +%H:%M:%S
