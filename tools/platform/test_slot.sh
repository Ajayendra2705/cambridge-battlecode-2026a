#!/bin/bash
# One platform test, as the user asked (11-04 02:48 IST): make the bot active, queue all its matches, make the best bot live again.
#   bash tools/platform/test_slot.sh exp/BOT RUN PANEL[,PANEL...] RESTORE
# Run names are RUN_PANEL@PANEL. Upload first, so nothing waits while the test bot is live:
# 1. Wait until the quota holds every group of the panels.
# 2. Start only in the three minutes after our ranked set (clock :x0:50 to :x3:00), so the next set plays the live bot: upload to active takes about a minute, the games up to two, and the switch back about 1:20 with no game running.
# 3. Upload the bot (an upload takes the selection), then tools/platform/gate_slot.sh creates the groups and selects RESTORE once.
# Stops without uploading if the live or selected version is not RESTORE: someone else may be using the slot.
# Read tools/platform/procs.sh before starting and after stopping this: killing it can leave gate_slot.sh running (11-04 02:26 IST).
cd "$(dirname "$0")/../.."
bot=$1; run=$2; panel=$3; restore=$4
C="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
log() { echo "$(date '+%m-%d %H:%M:%S') test $run: $*" | tee -a data/gate_live.log; }
ver() { "$C" submissions list --json 2>/dev/null | python -I -c "
import json, sys
s = sys.stdin.read()
d = json.loads(s[s.index('{'):])
print((d.get('active') or {}).get('version', 0), (d.get('selected') or {}).get('version', 0), d['submissions'][0]['version'])" 2>/dev/null | tr -d '\r'; }
free() { "$C" match-groups quota --json 2>/dev/null | python -I -c "
import json, sys
s = sys.stdin.read()
q = json.loads(s[s.index('{'):])['quota']
print(q['limit'] - q['used'])" 2>/dev/null | tr -d '\r'; }
need=0
for p in ${panel//,/ }; do
  [ -f "results/panels/specs_$p.txt" ] || { log "no specs for $p"; exit 1; }
  need=$((need + $(tr ' ' '\n' < "results/panels/specs_$p.txt" | grep -c .)))
done
log "needs $need groups"
until f=$(free) && [ -n "$f" ] && [ "$f" -ge "$need" ]; do sleep 15; done
log "quota free: $f"
while :; do
  m=$(( 10#$(date +%M) % 10 * 60 + 10#$(date +%S) ))
  if [ "$m" -ge 50 ] && [ "$m" -lt 180 ]; then break; fi
  sleep 5
done
until read -r a s n0 < <(ver) && [ -n "$n0" ]; do sleep 10; done
if [ "$a" != "$restore" ] || [ "$s" != "$restore" ]; then log "active $a selected $s, not $restore: not uploading"; exit 2; fi
note="$(head -1 "bots/$bot/NOTE.txt" | tr -d '\r') [${bot##*/}]"
out=$(powershell -File tools/cambc.ps1 submit "$bot" -n "${note:0:80}" 2>&1 | tail -1); log "$out"
echo "$out" | grep -q Submitted || { log "upload failed"; exit 3; }
until read -r a s n < <(ver) && [ -n "$n" ] && [ "$n" -gt "$n0" ]; do sleep 10; done
log "uploaded as $n"
exec bash tools/platform/gate_slot.sh "$n" "$run" "$panel" "$restore" noselect
