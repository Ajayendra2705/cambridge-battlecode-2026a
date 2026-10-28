#!/bin/bash
# Wait until Windows reports at least MIN_MB of free physical memory (helper agent h2).
#   usage: bash tools/helper/h2_ramwait.sh MIN_MB MAX_MINUTES && <the heavy command>
# Checks every 30 s. Exits 0 (and prints the free MB) as soon as the bar is met, or 1 after MAX_MINUTES without it, so a
# chained local run never starts on a machine that is short of memory (the team's rule: wait while under 2.5 GB free).
min="${1:?usage: h2_ramwait.sh MIN_MB MAX_MINUTES}"; max="${2:?usage: h2_ramwait.sh MIN_MB MAX_MINUTES}"
for ((i = 0; i <= max * 2; i++)); do
    free=$(powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)")
    if [ "${free:-0}" -ge "$min" ]; then echo "free ${free} MB at $(date +%H:%M:%S)"; exit 0; fi
    [ "$i" -lt $((max * 2)) ] && sleep 30
done
echo "gave up at $(date +%H:%M:%S): free ${free} MB, under ${min} MB for ${max} minutes"
exit 1
