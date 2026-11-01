#!/bin/sh
# widescan.sh TAG SRC EDITSFILE : bots/T<TAG> = bots/<SRC>/src + EDITSFILE, built; all 70 maps x 2 sides vs B7Live (wideT<TAG>), genscan summary.
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
C="${CAMBC:-$LOCALAPPDATA/cambc/bin/cambc-4.0.0.exe}"
cd "$(git rev-parse --show-toplevel)" || exit 1
T=$1; SRC=$2; EF=$3
rm -rf "bots/T$T"; mkdir -p "bots/T$T" && cp -r "bots/$SRC/src" "bots/T$T/" || exit 1
python3 tools/bamboo/local/apply_edits.py "bots/T$T/src/bot.cpp" "$(cat "$EF")" || { echo EDIT_FAILED; exit 1; }
"$C" build "T$T" > "bots/T$T/build.log" 2>&1 && echo BUILD_OK || { echo BUILD_FAILED; tail -20 "bots/T$T/build.log"; exit 1; }
W="$SP/wideT$T"; rm -rf "$W"; mkdir -p "$W"
sh "$SP/mkmanifest.sh" "T$T" "${SCAN_OPP:-BambooB7Live}" "$W"  # all maps, both sides
"$C" run-batch "$W/l.txt" --jobs ${JOBS:-8} > "$W/run.log" 2>&1
deno run -A tools/bamboo/replay/genscan.ts "@$W/list.txt" > "$W/scan.txt" 2>&1
tail -4 "$W/scan.txt"
