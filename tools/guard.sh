#!/bin/bash
# At a fixed local time, stop panel sweeps and submit the bot named in replays/final_bot.txt.
cd "$(dirname "$0")/.."
target="$1"   # HH:MM
while [ "$(date +%H:%M)" \< "$target" ]; do sleep 20; done
kill 460 466 2>/dev/null; sleep 2
bot=$(cat replays/final_bot.txt)
powershell -File tools/bc.ps1 submit "$bot" 2>&1 | tail -1 > replays/guard.log
echo "$(date +%H:%M) submitted $bot" >> replays/guard.log
