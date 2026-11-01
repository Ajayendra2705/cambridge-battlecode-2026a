#!/bin/sh
# allfinished.sh TAG... : block until every match of every group in scrim_TAG.ids reports finished or error (API poll every 10 s, up to
# 40 min), then 60 s more. Use before re-activating another version: ladder games are played by the LIVE bot at play time, and
# topwait.sh / benchcmp.ts can print a table with games still pending (Oct 29 00:45: #412's table came out at 4/10 with 40 pending).
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
ids=""; for T in "$@"; do ids="$ids $(cat "$SP/scrim_$T.ids")"; done
want=$(( $(echo $ids | wc -w) * 5 ))
for i in $(seq 1 240); do
  n=$(deno eval 'let n = 0; await Promise.all(Deno.args.map(async (g) => { try { const d = await (await fetch("https://2026a.battlecode.co.uk/api/v1/match-groups/" + g)).json(); n += (d.matches ?? []).filter((m) => m.status === "finished" || m.status === "error").length; } catch {} })); console.log(n);' $ids 2>/dev/null)
  [ "${n:-0}" -ge "$want" ] && { sleep 60; echo "all $want games finished $(date -u +%H:%M:%S)"; exit 0; }
  sleep 10
done
echo "allfinished: timed out with ${n:-0}/$want"
