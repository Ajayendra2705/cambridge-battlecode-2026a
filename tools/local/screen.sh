#!/bin/bash
# Fast local screen of candidates against a base whose games are already played (local games replay exactly):
#   bash tools/local/screen.sh NAME BASE_RUN_DIR BASE_CAND "exp/a,exp/b" JOBS [POOL] [BAR]
# Plays only the candidates (POOL default pool/cmb7,pool/bot_10: 340 games each on the 85 maps), copies the base's games of the same
# pairings from BASE_RUN_DIR into the run, then writes lscreen.py, lgold2.py and lbar.py output to data/judge_screen_NAME.txt.
# SCREEN_MAPS=data/maps_size3.txt plays one map list instead of the 85 (a draft change for one team size); lscreen pairs on the games that exist in both.
cd "$(dirname "$0")/../.."
name=$1; base_run=$2; base=$3; cands=$4; jobs=$5; pool=${6:-pool/cmb7,pool/bot_10}; bar=${7:-item}
python -I tools/local/multi.py "$cands" --pool "$pool" --maps "$(cat "${SCREEN_MAPS:-data/maps85.txt}")" --jobs "$jobs" > "data/screen_$name.log" 2>&1
d=$(grep '^dir ' "data/screen_$name.log" | sed 's/^dir //')
# Hard links: the base's 1360 files are 1.4 GB, and a full disk stopped two screens on 11-03.
for p in ${pool//,/ }; do cp -l "$base_run/$base~${p/\//.}~"*.json "$d/" 2>/dev/null || cp "$base_run/$base~${p/\//.}~"*.json "$d/"; done
python -I tools/local/lscreen.py "$d" "$base" 1000 > "data/judge_screen_$name.txt" 2>&1
python -I tools/local/lgold2.py "$d" "$base" >> "data/judge_screen_$name.txt" 2>&1
python -I tools/local/lbar.py "data/judge_screen_$name.txt" --bar "$bar" >> "data/judge_screen_$name.txt" 2>&1
echo "$name done $(date +%H:%M)" >> data/autoq.log
