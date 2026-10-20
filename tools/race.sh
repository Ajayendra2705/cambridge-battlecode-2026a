#!/bin/bash
# Finishing round vs starter on farming-race maps (lower is better).
cd "$(dirname "$0")/.."
python -I tools/batch.py "$1" starter-cpp --jobs 10 2>&1 | tail -1
