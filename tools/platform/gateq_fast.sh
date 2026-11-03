#!/bin/bash
# gateq_live.sh without the restore after each gate: each change of the active bot waits for the running ranked set, so a
# restore between two gates costs a full 10-minute cycle (11-03 05:55: 20 minutes a gate). The bot under test stays live
# until the next line selects its own, so select the team's live bot by hand when the plan ends. GATE_RESTORE is ignored.
# Gate queue that keeps the team's live bot by selection, not by upload:
#   GATE_RESTORE=VERSION bash tools/platform/gateq_live.sh
# Like gateq.sh, it runs gate.sh for each line "BOT RUN_NAME" of data/gate_queue.txt (honouring GATE_SPECS and
# GATE_PANEL), but it never uploads bots/main. BOT "live" plays the version selected now (no upload); BOT "vN" selects
# platform version N for the gate (no upload); any other BOT is uploaded, then selected. Before the games start it waits
# until the bot under test is the active version (an upload compiles in about 1.5 minutes); after the games it selects
# GATE_RESTORE (the team's live bot) and waits until that is active again, unless someone else selected a version during
# the games (theirs then stays live; a "live" gate never selects). An upload takes the selection (`selected` is the
# new version, `pinned` false) and goes live by itself once it compiles, so uploads too wait for the ranked window, and
# a second gate of the same code should select the version (`vN`) instead of uploading it again. Selecting another
# version while an upload is still queued cancels that upload (1486, 11-01 22:33). Each gate's versions go to
# data/gate_live.log, with a WARNING when the active version changed during the games (someone else uploaded or
# selected: the run is then void). With QWAIT=N it first waits for N free unranked groups, so an upload is not left on
# the ladder while gate.sh waits for quota. Run it through gatechain.sh with GATE_Q=gateq_live.sh.
cd "$(dirname "$0")/../.."
[ -n "$GATE_RESTORE" ] || { echo "set GATE_RESTORE=VERSION (the team's live bot) or auto (the version live before each gate)"; exit 1; }
C="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
# "ACTIVE NEWEST": the active version and the newest submitted version.
ver() {
  "$C" submissions list --json 2>/dev/null | python -I -c "
import json, sys
s = sys.stdin.read()
d = json.loads(s[s.index('{'):])
print((d.get('active') or {}).get('version', 0), d['submissions'][0]['version'])" 2>/dev/null | tr -d '\r'
  # Windows python ends the line in CRLF: without the tr, "1482\r" fails the -gt test after an upload and the gate
  # waits for ever (11-01 20:22, hy3v_b40p).
}
select_wait() {  # select version $1 and wait until it is the active one; the first refusal goes to the log
  local n=0 out
  until out=$("$C" submissions activate "$1" 2>&1) && [ "$(ver | cut -d' ' -f1)" = "$1" ]; do
    n=$((n + 1)); [ $n -eq 1 ] && log "select $1 waits: $(echo "$out" | tail -1 | tr -d '\r')"
    sleep 15
  done
}
log() { echo "$(date '+%m-%d %H:%M:%S') $*" | tee -a data/gate_live.log; }
window() {  # as gateq.sh: ranked sets start at :x0:05; change the active bot only from :x1:00 to :x2:59
  [ -n "$NO_RANKED_WINDOW" ] && return
  until s=$(( 10#$(date +%M) % 10 * 60 + 10#$(date +%S) )); [ "$s" -ge 60 ] && [ "$s" -lt 180 ]; do sleep 5; done
}
while line=$(head -1 data/gate_queue.txt 2>/dev/null) && [ -n "$line" ]; do
  sed -i 1d data/gate_queue.txt
  set -- $line; bot=$1; run=$2
  echo "== $bot $run $(date +%H:%M)"
  [ -n "$QWAIT" ] && bash tools/platform/qwait.sh "$QWAIT"
  # QUIET=N: wait until no unranked match of the team started in the last N seconds (a teammate's panel may be playing).
  [ -n "$QUIET" ] && python -I tools/platform/quiet.py "$QUIET"
  # A failed read (rate limit, network) left new0 empty and the wait after the upload never ended (11-03 03:22, vpk3b).
  until read -r act0 new0 < <(ver) && [ -n "$new0" ]; do sleep 10; done
  # GATE_RESTORE=auto: restore the version that was live just before this gate (a teammate may have changed it).
  restore=$GATE_RESTORE; [ "$restore" = auto ] && restore=$act0
  if [ "$bot" = live ]; then
    want=$act0
  elif [[ "$bot" =~ ^v[0-9]+$ ]]; then
    want=${bot#v}; window; select_wait "$want"
  else
    window  # the upload goes live by itself once it compiles (about 1.5 minutes)
    # Upload name for teammates: bots/<bot>/NOTE.txt says what the bot improves (website limit: 80 characters).
    note="test $run"; [ -f "bots/$bot/NOTE.txt" ] && note="$(head -1 "bots/$bot/NOTE.txt" | tr -d '') [$run]"
    out=$(powershell -File tools/cambc.ps1 submit "$bot" -n "${note:0:80}" 2>&1 | tail -1); echo "$out"
    if ! echo "$out" | grep -q Submitted; then
      { echo "$bot $run"; cat data/gate_queue.txt; } > data/gate_queue.tmp && mv data/gate_queue.tmp data/gate_queue.txt
      log "$run upload failed: $out"; sleep 90; continue
    fi
    until read -r a n < <(ver) && [ -n "$n" ] && [ "$n" -gt "$new0" ]; do sleep 10; done
    want=$n; select_wait "$want"
  fi
  log "$run start bot=$bot version=$want (was active $act0, newest $new0)"
  bash tools/platform/gate.sh "$bot" nosubmit "$run" 2>&1 | tail -3
  until read -r act1 new1 < <(ver) && [ -n "$new1" ]; do sleep 10; done
  log "$run done active=$act1 newest=$new1"
  # Restore only what this gate changed: if someone else selected a version during the games, theirs stays live
  # (on 11-01 a teammate made 1479 live during a "live" gate, and the restore would have put 1472 back over it).
  if [ "$act1" != "$want" ]; then
    log "WARNING: active version changed during $run ($want -> $act1): run void; $act1 stays live"
  fi
  # gateq_fast.sh: no restore here (see the header); the next line's selection replaces this bot directly.
done
