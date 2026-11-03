"""Index a folder of local decoded games: python -I tools/replay/index_local.py RUN_DIR CAND OUT

For decoded replays of a local run (`pextract.py OUT JOBS RUN_DIR/CAND~...repl26a`): drops the dots from the file names and writes
the `index.txt` that `decoded.py` reads, with the result from each game's statistics JSON. Only games decoded so far are listed.
"""
import glob, json, os, sys
run, cand, out = sys.argv[1:]
for g in glob.glob(os.path.join(out, cand + '~*.jsonl.gz')):
    stem = os.path.basename(g)[:-len('.jsonl.gz')]
    os.replace(g, os.path.join(out, stem.replace('.', '-') + '.jsonl.gz'))
have = set(os.path.basename(x)[:-len('.jsonl.gz')] for x in glob.glob(os.path.join(out, '*.jsonl.gz')))
with open(os.path.join(out, 'index.txt'), 'w', encoding='utf-8') as f:
    for js in sorted(glob.glob(os.path.join(run, cand + '~*.json'))):
        game = os.path.basename(js)[:-5]
        side = game.split('~')[-1]
        mp = game.split('~')[2]
        won = json.load(open(js, encoding='utf-8'))['match']['outcome'] == ('teamA' if side == 'A' else 'teamB')
        if game.replace('.', '-') in have:
            f.write(game.replace('.', '-') + ' ' + mp + ' ' + ('a' if side == 'A' else 'b') + ' ' + ('win' if won else 'loss') + '\n')
print(len(have), 'games indexed in', out)
