#!/bin/bash
# Make a size-dispatch combination with another Bamboo bot at four a side, from cmb7's frame:
#   bash tools/variant/mkcmb.sh NAME BAMBOO_BOT [FRAME]   (from the repo root; builds nothing)
# Copies FRAME (default pool/cmb7: vx1 three a side, Bamboo four a side in src/bb, bot_10 five a side in src/cj) to
# bots/exp/NAME and replaces src/bb with bots/BAMBOO_BOT wrapped in namespace bbt (tools/variant/nsbot.py). The
# Bamboo bot's own fastalloc.h is dropped: the frame's src/fastalloc_switch.h holds the same allocator, switched on
# four a side. Then: powershell -File tools/cambc.ps1 build exp/NAME --release
set -e
name=$1; bb=$2; frame=${3:-pool/cmb7}
[ -n "$name" ] && [ -n "$bb" ] || { echo "usage: mkcmb.sh NAME BAMBOO_BOT [FRAME]"; exit 1; }
[ -d "bots/$bb/src" ] && [ -f "bots/$frame/src/fastalloc_switch.h" ] || { echo "no bots/$bb/src or frame bots/$frame"; exit 1; }
rm -rf "bots/exp/$name"
mkdir -p "bots/exp/$name"
cp -r "bots/$frame/src" "bots/exp/$name/"
cp "bots/$frame/.gitignore" "bots/exp/$name/" 2>/dev/null || true
rm -rf "bots/exp/$name/src/bb"
python -I tools/variant/nsbot.py "$bb" "exp/$name" bb bbt neighbour_value > /dev/null
rm -f "bots/exp/$name/src/bb/fastalloc.h"
grep -q "::bbt::neighbour_value" "bots/exp/$name/src/bb/bot.cpp" || echo "note: no ::neighbour_value call rewritten (check the build)"
echo "made bots/exp/$name: four a side $bb; edit the comment at the top of src/main.cpp"
