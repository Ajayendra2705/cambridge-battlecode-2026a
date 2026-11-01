# latestpanel.sh (Eric ~10:00 UTC: 11-scrim test of v1479 vs v1472 against the opponents' LATEST bots): v1479 (live via follow-newest)
# plays fresh groups (queuelatest.sh: top-10 + Fish newest specs, no --source-group) as L1479; then, once Eric re-selects v1472, v1472 replays
# those exact groups (bench2qs --source-group L1479) as L1472; paired comparison.
SP="${BAMBOO_SP:-$(cd "$(dirname "$0")" && pwd)}"
C="${CAMBC:-$LOCALAPPDATA/cambc/bin/cambc-4.0.0.exe}"
waitlive() { for i in $(seq 1 480); do l=$(timeout 60 "$C" submissions list 2>/dev/null | grep "^Live:"); echo "$l" | grep -q "^Live: $1 " && return 0; sleep 15; done; return 1; }
waitlive 1479 || { echo "1479 never went live: stop"; exit 1; }
date -u +"live 1479 %H:%M:%S"; sleep 90
sh "$SP/queuelatest.sh" L1479_top "$SP/bench_top10.txt"
sh "$SP/queuelatest.sh" L1479_fn "$SP/bench_fishnew.txt"
echo "queued $(cat $SP/scrim_L1479_top.ids $SP/scrim_L1479_fn.ids | grep -c .) groups"
sh "$SP/allfinished.sh" L1479_top L1479_fn
timeout 60 "$C" submissions list 2>/dev/null | grep "^Live:"
cd "$SP"; echo "v1479 vs latest bots: top $(deno run -A benchcmp.ts L1479_top 2>/dev/null | grep -E '^wins|^margin' | tr -s ' ' | tr '\n' ' ') | fn $(deno run -A benchcmp.ts L1479_fn 2>/dev/null | grep -E '^wins|^margin' | tr -s ' ' | tr '\n' ' ')"
echo "PHASE1DONE - waiting for Live 1472"
waitlive 1472 || { echo "1472 never went live again: stop"; exit 1; }
date -u +"live 1472 %H:%M:%S"
sh "$SP/bench2qs.sh" L1472_top "$SP/bench_top10.txt" L1479_top > /dev/null 2>&1
sh "$SP/bench2qs.sh" L1472_fn "$SP/bench_fishnew.txt" L1479_fn > /dev/null 2>&1
sh "$SP/allfinished.sh" L1472_top L1472_fn
for k in top fn; do echo "$k: $(deno run -A benchcmp.ts L1472_$k L1479_$k 2>/dev/null | awk -f pairsum.awk)"; done
echo alldone
