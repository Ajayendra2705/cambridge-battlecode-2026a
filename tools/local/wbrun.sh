#!/bin/bash
# Targeted local screen for a change that acts only once our hand reaches 1000:
#   bash tools/local/wbrun.sh NAME [JOBS] [BASE_RUN] [BASE] [MIN_RIVAL]
# Builds exp/NAME, plays the games `wbsel.py` picks from the base run (data/runs/NAME), and writes `wbcmp.py` to data/judge_NAME.txt.
cd "$(dirname "$0")/../.."
name=$1; jobs=${2:-4}; base_run=${3:-data/runs/multi-142332}; base=${4:-exp.b30}; min_rival=${5:-700}
CAMBC="$LOCALAPPDATA/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/Scripts/cambc.exe"
"$CAMBC" build "bots/exp/$name" --release > "data/build_$name.log" 2>&1 || { echo "build failed $name"; tail -20 "data/build_$name.log"; exit 1; }
mkdir -p "data/runs/$name"
python -I tools/local/wbsel.py "$base_run" "$base" "exp.$name" "data/runs/$name/matches.txt" "$min_rival"
"$CAMBC" run-batch "data/runs/$name/matches.txt" --jobs "$jobs" --release > "data/runs/$name/run.log" 2>&1
python -I tools/local/wbcmp.py "$base_run" "$base" "data/runs/$name" "exp.$name" > "data/judge_$name.txt" 2>&1
cut -c1-170 "data/judge_$name.txt"
