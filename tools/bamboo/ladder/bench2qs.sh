#!/bin/sh
# bench2qs.sh TAG SPECFILE SRCTAG : queue the bench sets in SPECFILE against the opponents' EXACT bots of a previous run (Eric, Oct 28 23:55:
# "there is an option to verse the exact same bots that we did previously"): line i of SPECFILE is queued with --source-group = line i of
# scrim_SRCTAG.ids (the group the same spec line produced earlier; cambc 4.0.0 `match-groups create --source-group`). Same maps and sides,
# same opponent versions, deterministic engine: the candidate's games pair exactly with the earlier run's, no same-time baseline needed.
# Group ids into scrim_TAG.ids; retries while the hourly quota is full.
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
C="${CAMBC:-$LOCALAPPDATA/cambc/bin/cambc-4.0.0.exe}"
T=$1; SPEC=$2; SRC=$3; : > "$SP/scrim_$T.ids"
[ "$(grep -c . "$SPEC")" = "$(grep -c . "$SP/scrim_$SRC.ids")" ] || { echo "spec / ids line counts differ: $(grep -c . "$SPEC") vs $(grep -c . "$SP/scrim_$SRC.ids")" >&2; exit 1; }
paste -d '|' "$SPEC" "$SP/scrim_$SRC.ids" | while IFS='|' read line gid; do
  set -- $line; team=$1; maps=$2; side=$3; sidesarg=$4
  [ -z "$team" ] && continue
  for try in $(seq 1 60); do
    out=$(timeout 120 "$C" match-groups create "$team" --source-group "$gid" --maps "$maps" $( [ "$side" = "--sides" ] && echo "--sides $sidesarg" || echo "${side:+--side $side}") --json 2>&1)
    id=$(echo "$out" | grep -o '"groupId": *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
    if [ -n "$id" ]; then echo "$id" >> "$SP/scrim_$T.ids"; break; fi
    case "$out" in *"eligible bot"*|*"HTTP 409"*|*"not found"*) echo "skip $team ($gid): $out" >&2; break ;; esac
    echo "retry $try: $(echo "$out" | tail -1)" >&2
    sleep 60
  done
done
date -u +%H:%M:%S
cat "$SP/scrim_$T.ids"
