"""Extract replays in parallel with native processes: python -I tools/replay/pextract.py OUTDIR JOBS REPLAY...

Runs `node tools/replay/rounds_extract.mjs OUTDIR FILE` for each replay, JOBS at a time, and prints the extractor's
"ok" lines and a count. Replaces `xargs -P` in decode_run.sh: under load Git Bash fails to start processes
("fork: Permission denied") and a whole decode came back with 0 games. Replays whose .jsonl.gz already exists are
skipped, so a rerun finishes the rest.
"""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

out, jobs, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
here = os.path.dirname(os.path.abspath(__file__))
todo = [f for f in files if not os.path.exists(os.path.join(out, os.path.basename(f).replace('.repl26a', '.jsonl.gz')))]


def run(f):
    r = subprocess.run(['node', os.path.join(here, 'rounds_extract.mjs'), out, f], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    ok = [l for l in r.stdout.splitlines() if l.startswith('ok')]
    if not ok: print('FAIL', os.path.basename(f), (r.stderr.strip().splitlines() or [''])[-1], flush=True)
    return len(ok)


with ThreadPoolExecutor(jobs) as ex: done = sum(ex.map(run, todo))
print(f'extracted {done} of {len(todo)} ({len(files) - len(todo)} already there)')
