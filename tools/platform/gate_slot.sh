#!/bin/bash
# One test panel fitted between two ranked sets, so the ranked sets play the live bot:
#   bash tools/platform/gate_slot.sh VERSION RUN PANEL[,PANEL...] RESTORE [noselect]   (run names RUN_PANEL@PANEL)
#
# What the timing rests on (measured 11-04 00:42-01:05 IST): a panel's 50 games finish within seconds of the last group's creation
# when the platform is not busy, so the live time a test needs is short. A selection does not switch at once: it stays `queued` for
# 2 to 9 minutes, and neither a match finishing nor the end of a ranked set was seen to trigger it reliably. Selected 00:51:53, active
# about 00:56:25; selected 00:56:49, with the panel's last game finishing at 00:56:53, active only between 01:03:57 and 01:04:52.
# Earlier: 1:42, 1:45, 2:18, 2:51, 4:38, 5:00, 9:14. Ranked rounds usually start at :x0:05 and our set lasts about 40 seconds.
# 1. Select VERSION at :x0:15, right after our ranked set has started (noselect: the selection is already queued).
# 2. As soon as VERSION is active, create the panel's groups.
# 3. Right after the last group is created, select RESTORE, which leaves the most time before the next round.
# The two waits can add up to more than 10 minutes, so this makes a ranked set on the test bot unlikely, not impossible.
# Put every panel a bot needs into one active period (a PANEL argument may list several, comma-separated).
# Groups bound at creation: on 11-04 nr4's drafts show v1537's arm in every game checked.
# Selects once and repeats only a failed call: a loop of selections undid the user's cancel on 11-04 00:48 IST. A version selected by
# anyone else ends the slot and stays as it is.
cd "$(dirname "$0")/../.."
ver=$1; run=$2; panel=$3; restore=$4; noselect=$5
C="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
log() { echo "$(date '+%m-%d %H:%M:%S') slot $run: $*" | tee -a data/gate_live.log; }
state() { "$C" submissions list --json 2>/dev/null | python -I -c "
import json, sys
s = sys.stdin.read()
d = json.loads(s[s.index('{'):])
print((d.get('active') or {}).get('version', 0), (d.get('selected') or {}).get('version', 0))" 2>/dev/null | tr -d '\r'; }
t() { echo $(( 10#$(date +%M) % 10 * 60 + 10#$(date +%S) )); }
pick() {  # select $1 once; repeat only if the call failed or the selection does not read back
  local a s
  until "$C" submissions activate "$1" > /dev/null 2>&1 && read -r a s < <(state) && [ "$s" = "$1" ]; do sleep 15; done
}
for p in ${panel//,/ }; do [ -f "results/panels/specs_$p.txt" ] || { log "no specs for $p"; exit 1; }; done
if [ "$noselect" != noselect ]; then
  until [ "$(t)" -ge 15 ] && [ "$(t)" -lt 40 ]; do sleep 2; done
  pick "$ver"
  log "selected $ver"
fi
until read -r a s < <(state) && [ "$a" = "$ver" ]; do
  if [ -n "$s" ] && [ "$s" != "0" ] && [ "$s" != "$ver" ]; then log "selection is $s, not $ver: someone changed it; slot ends"; exit 2; fi
  sleep 10
done
log "$ver active; creating the groups"
pids=""
for p in ${panel//,/ }; do
  r="${run}_$p"
  GATE_SPECS="$(cat "results/panels/specs_$p.txt")" GATE_PANEL="$p" bash tools/platform/gate.sh live nosubmit "$r" > "data/slot_$r.log" 2>&1 &
  g=$!; pids="$pids $g"
  until grep -q "^$r@$p " results/gate.log; do
    kill -0 $g 2>/dev/null || { log "gate.sh for $p ended before logging its groups"; break; }
    sleep 1
  done
done
read -r a s < <(state)
if [ "$s" = "$ver" ]; then
  pick "$restore"
  log "groups created ($panel); selected $restore"
else
  log "selection is $s when the groups are created: left as it is"
fi
until read -r a s < <(state) && [ "$a" = "$s" ]; do sleep 15; done
log "active $a at :$(t)s"
wait $pids
log "panels done ($panel)"
