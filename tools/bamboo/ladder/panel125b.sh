#!/bin/sh
# Oct 31 ~10:00: x1r cut to 6 groups (24 / panel), panel B + 1 group vs Fish's bot pinned at 09:59 (bench_fishnew.txt / p458_fn); cmp pairs games (pairsum.awk). Backups *.bak1031.
# panel125.sh (panel.sh with the random-map bench cut to its first 7 groups: 25 groups, 125 games, two tests an hour) - queue TAG | cmp BASETAG CANDTAG : the pinned 140-game panel (Oct 29, Eric's item 1 "fix the measurement"): four stored #405
# benches replayed against the SAME opponent bots (bench2qs.sh --source-group): top-10 (bench_top10 / p445f_top, 50), Fish sets (bench_fish405c /
# fish405c, 20; bench_fish405a / fish405a, 20), random-map top-10 (bench_x1 / x1_405, 50). queue: the live bot plays all four as TAG_top,
# TAG_f1, TAG_f2, TAG_x1, then waits until every game is finished (allfinished.sh). cmp: per bench and in total, wins and margin of
# CANDTAG against BASETAG (the same games, deterministic engine) via benchcmp.ts.
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
case "$1" in
queue)
  T=$2
  sh "$SP/bench2qs.sh" "${T}_top" "$SP/bench_top10.txt" p445f_top > /dev/null 2>&1
  sh "$SP/bench2qs.sh" "${T}_f1" "$SP/bench_fish405c.txt" p445f_f1 > /dev/null 2>&1
  sh "$SP/bench2qs.sh" "${T}_f2" "$SP/bench_fish405a.txt" p445f_f2 > /dev/null 2>&1
  sh "$SP/bench2qs.sh" "${T}_x1r" "$SP/bench_x1r6.txt" p445f_x1r6 > /dev/null 2>&1  # Oct 31: 6 random-map groups (quota room)
  echo "queued $(cat "$SP/scrim_${T}_top.ids" "$SP/scrim_${T}_f1.ids" "$SP/scrim_${T}_f2.ids" "$SP/scrim_${T}_x1r.ids" | grep -c .) groups $(date -u +%H:%M:%S)"
  sh "$SP/allfinished.sh" "${T}_top" "${T}_f1" "${T}_f2" "${T}_x1r" ;;
cmp)
  B=$2; X=$3; tw=0; tb=0; mw=0; mb=0; tn=0
  for k in top f1 f2 x1r; do
    [ -s "$SP/scrim_${B}_$k.ids" ] && [ -s "$SP/scrim_${X}_$k.ids" ] || continue
    out=$(deno run -A "$SP/benchcmp.ts" "${B}_$k" "${X}_$k" 2>/dev/null | awk -f "$SP/pairsum.awk")
    echo "$k: $out"
    set -- $out; n=$2; wb=$5; wx=$6; mbb=$8; mxx=$9
    tn=$((tn + n)); tb=$((tb + wb)); tw=$((tw + wx)); mb=$((mb + mbb)); mw=$((mw + mxx))
  done
  echo "TOTAL paired $tn games: $B $tb wins $mb | $X $tw wins $mw | diff $((tw - tb)) wins $((mw - mb))" ;;
esac
