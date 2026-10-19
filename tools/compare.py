"""Compare finishing rounds per match across batch directories: python tools/compare.py batch-A batch-B ..."""
import os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def load(d):
    log = open(os.path.join(ROOT, 'replays', d, 'batch.log')).read()
    out = {}
    for m in re.finditer(r'\[\+\] TEAM ([AB]) WIN \(([^)]*)\).*?Round (\d+)/\d+\s*\n\s*Replay: .*?([^\\/]+\.repl26a)', log):
        out[m.group(4)] = (m.group(2), int(m.group(3)))
    return out


runs = [load(d) for d in sys.argv[1:]]
keys = sorted(set().union(*runs))
print(f'{"match":24}' + ''.join(f'{d[-6:]:>14}' for d in sys.argv[1:]))
for k in keys:
    print(f'{k:24}' + ''.join(f'{(r[k][0][:8] + ":" + str(r[k][1])) if k in r else "-":>14}' for r in runs))
