#!/bin/bash
# Decode the kept replays of one candidate in a local multi.py --keep run for tools/replay/decoded.py:
#   bash tools/local/local_decode.sh RUNDIR CAND [JOBS]
# CAND as multi.py names it in the file names (exp.gw2, main). Writes data/fights/local_<run>_<cand>/ with one
# <game>.jsonl.gz per replay (rounds_extract.mjs, JOBS parallel, default 3; about 25 s and 140 MB per 2000-round game) and
# an index.txt ("game map side result", side a when the candidate was team A, result from the statistics JSON).
# Local opponents are our own pool bots, so this reads economy and opening metrics (decoded.py gold, gems, captures),
# not fights.
set -e
cd "$(dirname "$0")/../.."
run="$1"; cand="$2"; jobs="${3:-3}"
[ -d "$run" ] && [ -n "$cand" ] || { echo "usage: local_decode.sh RUNDIR CAND [JOBS]"; exit 1; }
out="data/fights/local_$(basename "$run")_$cand"
mkdir -p "$out"
ls "$run"/"$cand"~*.repl26a | xargs -P "$jobs" -n 4 node tools/replay/rounds_extract.mjs "$out" 2>&1 | grep -c '^ok' || true
# decoded.py takes a game's id up to the first dot of its file name: drop the dots from the names ("exp.gw2" -> "exp-gw2").
python -I - "$run" "$cand" "$out" <<'EOF'
import glob, json, os, sys
run, cand, out = sys.argv[1:]
for g in glob.glob(os.path.join(out, cand + '~*.jsonl.gz')):
    stem = os.path.basename(g)[:-len('.jsonl.gz')]
    os.replace(g, os.path.join(out, stem.replace('.', '-') + '.jsonl.gz'))
with open(os.path.join(out, 'index.txt'), 'w', encoding='utf-8') as f:
    for js in sorted(glob.glob(os.path.join(run, cand + '~*.json'))):
        game = os.path.basename(js)[:-5]
        side = game.split('~')[-1]
        mp = game.split('~')[2]
        won = json.load(open(js, encoding='utf-8'))['match']['outcome'] == ('teamA' if side == 'A' else 'teamB')
        f.write(f'{game.replace(".", "-")} {mp} {"a" if side == "A" else "b"} {"win" if won else "loss"}\n')
EOF
echo "decoded into $out ($(ls "$out"/*.jsonl.gz | wc -l) games)"
