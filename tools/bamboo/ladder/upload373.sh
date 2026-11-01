#!/bin/sh
# upload.sh N SRC "EDITS" "NOTE" PREVTAG... : make bots/Up<N> from bots/<SRC>/src + EDITS (apply_edits.py `s/old/new/@@...`, "" for
# none) with kBotVersion = N (the platform number it will get), build it, run the 24-game stress scan (mkmanifest.sh: 12 maps x 2 sides), submit
# it only when the scan passes (stuck <= 2, wins >= 12) and the platform assigns N, wait for the compile, queue the Fish bench
# (bench_fishmix.txt, tag fish<N>), wait for it and print benchcmp's table plus paired differences against each PREVTAG.
# State in $BENCH_SP (the session scratchpad, BAMBOO_SP, default this folder).
set -u
N=$1; SRC=$2; EDITS=$3; NOTE=$4; shift 4
R="$(git rev-parse --show-toplevel)"
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
SPW=$(cd "$SP" && pwd -W)
C="${CAMBC:-$LOCALAPPDATA/cambc/bin/cambc-4.0.0.exe}"; C5="$C"
cd "$R" || exit 1
for t in 1 2 3 4 5 6; do
  rm -rf "bots/Up$N" 2>/dev/null; mkdir -p "bots/Up$N" && cp -r "bots/$SRC/src" "bots/Up$N/" 2>/dev/null || { sleep 2; continue; }
  if [ -n "$EDITS" ]; then python3 tools/bamboo/local/apply_edits.py "bots/Up$N/src/bot.cpp" "$EDITS" || { sleep 2; continue; }; fi
  python3 - "$N" "$NOTE" <<'PY' && break
import re, sys
n, note = sys.argv[1], sys.argv[2]
p = "bots/Up%s/src/bot.cpp" % n; s = open(p, encoding="utf-8").read()
s2 = re.sub(r"constexpr int kBotVersion = \d+;[^\n]*", "constexpr int kBotVersion = %s;  // = the platform submission number: %s" % (n, note), s, count=1)
assert s2 != s; open(p, "w", encoding="utf-8", newline="\n").write(s2)
PY
  sleep 2
done
grep -o "constexpr int kBotVersion = [0-9]*" "bots/Up$N/src/bot.cpp"
"$C" build "Up$N" > "bots/Up$N/build.log" 2>&1 && echo BUILD_OK || { echo BUILD_FAILED; tail -20 "bots/Up$N/build.log"; exit 1; }
rm -rf "$SP/scan$N"; mkdir -p "$SP/scan$N"
# Codex C026: each row also exports the official statistics (bot faults, fuelExhausted events) beside its replay
sh "$SP/mkmanifest.sh" "Up$N" "${SCAN_OPP:-BambooB7Live}" "$SP/scan$N" 00corners 00expanse 00interlock 00lanes 00packs 00rows 01big-world 01corridors 01elk-arena 01fracture 01islands 01yellow-brick-road  # the 12-map stress set, both sides
"$C" run-batch "$SP/scan$N/l.txt" --jobs 8 > "$SP/scan$N/batch.log" 2>&1
deno run -A tools/bamboo/replay/genscan.ts "@$SPW/scan$N/list.txt" > "$SPW/scan$N/scan.txt" 2>&1
line=$(grep -m1 "^games" "$SPW/scan$N/scan.txt"); echo "$line"
faults=$(python3 - "$SPW/scan$N/l.txt" "Up$N" <<'PY'
import json, os, re, sys
rows = [re.findall(r'"([^"]*)"', l) for l in open(sys.argv[1]) if l.strip()]
faults = fuel = missing = 0
for r in rows:
    a, stats = r[0], r[4] if len(r) > 4 else ""
    side = "teamA" if a.replace("\\", "/").rstrip("/").endswith(sys.argv[2]) else "teamB"
    if not stats or not os.path.exists(stats): missing += 1; continue
    d = json.load(open(stats))
    faults += int(d["diagnostics"]["botFaults"][side])
    fuel += sum(len(e.get("entries", [])) for e in d.get("events", []) if e.get("kind") == "fuelExhausted" and e.get("owner", {}).get("team") == side)
print(faults + 1000 * missing, fuel)
PY
)
echo "official: our bot faults (+1000 per missing stats file) ${faults% *}, our fuelExhausted events ${faults#* }"
wins=$(echo "$line" | sed -n 's/.*wins \([0-9]*\).*/\1/p'); stuck=$(echo "$line" | sed -n 's/.*stuck \([0-9]*\) (.*/\1/p')
games=$(echo "$line" | sed -n 's/^games \([0-9]*\):.*/\1/p'); reps=$(ls "$SPW"/scan$N/*.repl26a 2>/dev/null | wc -l)
# Codex C018: every manifest game present and decoded, not just enough wins
srnd=$(echo "$line" | sed -n 's/.*stuck [0-9]* (\([0-9]*\) rounds).*/\1/p')
# stuck: at most 4 cases and 60 rounds in all (STUCK_ROUNDS overrides the 60 as a recorded exception) (the old "2 cases" gate dates from 1,000-round freezes; 289 had 3 cases / 29 rounds)
[ "${faults% *}" = "0" ] && [ "${games:-0}" -eq 24 ] && [ "$reps" -eq 24 ] && [ "${stuck:-9}" -le "${STUCK_CASES:-4}" ] && [ "${srnd:-999}" -le "${STUCK_ROUNDS:-60}" ] && [ "${wins:-0}" -ge 12 ] || { echo "STRESS FAILED (games ${games:-?}, replays $reps): not submitted"; exit 1; }
[ -n "${NOSUBMIT:-}" ] && { echo "NOSUBMIT set: stopping before the upload"; exit 0; }
WEBNOTE=$(printf "Bamboo %s" "$NOTE" | cut -c1-80); sub=$("$C5" submit "Up$N" --note "$WEBNOTE" 2>&1 | tail -1); echo "$sub"; date -u +"submitted %H:%M:%S UTC"
echo "$sub" | grep -q "^Submitted bot version $N\b" || { echo "NUMBER MISMATCH: fix kBotVersion and resubmit"; exit 1; }
echo "revert upload: no bench (candidate 369)"
exit 0
