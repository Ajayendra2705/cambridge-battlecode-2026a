#!/bin/bash
# Finishing round vs starter on farming-race maps (lower is better).
cd "$(dirname "$0")/.."
python -I tools/batch.py "$1" starter-cpp --jobs 10 --maps rows,lanes,expanse,corners,eight,interlock,monolith,ambush,packs,elkring 2>&1 | tail -1
