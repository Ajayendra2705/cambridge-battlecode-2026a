#!/bin/sh
# mkmanifest.sh BOT OPP OUTDIR [MAP...] : a cambc run-batch manifest OUTDIR/l.txt playing bots/BOT against bots/OPP on every map in maps/
# (or the MAPs given, names without .map26a), both sides, replays OUTDIR/MAP__OPP__A.repl26a (BOT is team A) and __B (BOT is team B), each
# with its --statistics JSON; OUTDIR/list.txt lists the replays (genscan.ts @list.txt). Paths are written the way cambc wants them on Windows
# (Git Bash pwd -W) and plain elsewhere.
BOT=$1; OPP=$2; OUT=$3; shift 3
ROOT=$(cd "$(git rev-parse --show-toplevel)" && (pwd -W 2>/dev/null || pwd))
mkdir -p "$OUT"; OUTW=$(cd "$OUT" && (pwd -W 2>/dev/null || pwd))
MAPS="$*"; [ -z "$MAPS" ] && MAPS=$(cd "$(git rev-parse --show-toplevel)/maps" && ls *.map26a | grep -v '^sprint' | sed 's/\.map26a$//')
: > "$OUT/l.txt"; : > "$OUT/list.txt"
for m in $MAPS; do
  echo "\"$ROOT/bots/$BOT\" \"$ROOT/bots/$OPP\" \"$ROOT/maps/$m.map26a\" \"$OUTW/${m}__${OPP}__A.repl26a\" --statistics \"$OUTW/${m}__${OPP}__A.json\" --json" >> "$OUT/l.txt"
  echo "\"$ROOT/bots/$OPP\" \"$ROOT/bots/$BOT\" \"$ROOT/maps/$m.map26a\" \"$OUTW/${m}__${OPP}__B.repl26a\" --statistics \"$OUTW/${m}__${OPP}__B.json\" --json" >> "$OUT/l.txt"
  echo "$OUTW/${m}__${OPP}__A.repl26a" >> "$OUT/list.txt"; echo "$OUTW/${m}__${OPP}__B.repl26a" >> "$OUT/list.txt"
done
