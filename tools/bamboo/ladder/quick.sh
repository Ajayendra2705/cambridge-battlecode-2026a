#!/bin/sh
# quick.sh (Eric, Oct 31 ~14:40: less quota a test, more tests) - queue TAG | cmp BASE CAND: panel A's top-10 set (bench_top10 / p445f_top,
# 10 groups, 50 games) + Fish's newest pinned (bench_fishnew / p458_fn, 1 group, 5 games) = 11 groups, ~4 tests an hour; paired vs #458's
# games (BASE tags p458_top / p458_fn). For screening only: a candidate that looks good gets the full panels.
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
case "$1" in
queue)
  T=$2
  sh "$SP/bench2qs.sh" "${T}_top" "$SP/bench_top10.txt" p445f_top > /dev/null 2>&1
  sh "$SP/bench2qs.sh" "${T}_fn" "$SP/bench_fishnew.txt" p458_fn > /dev/null 2>&1
  echo "queued $(cat "$SP/scrim_${T}_top.ids" "$SP/scrim_${T}_fn.ids" | grep -c .) groups $(date -u +%H:%M:%S)"
  sh "$SP/allfinished.sh" "${T}_top" "${T}_fn" ;;
cmp)
  B=$2; X=$3; tw=0; tb=0; mw=0; mb=0; tn=0
  for k in top fn; do
    [ -s "$SP/scrim_${B}_$k.ids" ] && [ -s "$SP/scrim_${X}_$k.ids" ] || continue
    out=$(deno run -A "$SP/benchcmp.ts" "${B}_$k" "${X}_$k" 2>/dev/null | awk -f "$SP/pairsum.awk")
    echo "$k: $out"
    set -- $out; n=$2; wb=$5; wx=$6; mbb=$8; mxx=$9
    tn=$((tn + n)); tb=$((tb + wb)); tw=$((tw + wx)); mb=$((mb + mbb)); mw=$((mw + mxx))
  done
  echo "TOTAL paired $tn games: $B $tb wins $mb | $X $tw wins $mw | diff $((tw - tb)) wins $((mw - mb))" ;;
esac
