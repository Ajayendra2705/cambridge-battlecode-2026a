"""Show each slot's target group and activity per round from "W round slot target activity" lines."""
import collections, glob, os, re, sys, zipfile

root = os.path.join(os.path.dirname(__file__), '..', 'replays')
team = sys.argv[1] if len(sys.argv) > 1 else 'a'
path = sys.argv[2] if len(sys.argv) > 2 else max(glob.glob(os.path.join(root, '**', '*.repl26a'), recursive=True), key=os.path.getmtime)
text = re.sub(r'[^\x20-\x7e\n]', '', zipfile.ZipFile(path).read(f'team-{team}.stdout').decode('latin1'))
rows = collections.defaultdict(dict)
for m in re.finditer(r'^W (\d+) (\d+) (-?\d+) (\S+)', text, re.M):
    rows[int(m.group(1))][int(m.group(2))] = f'g{m.group(3)}:{m.group(4)[:9]}'
slots = sorted({s for r in rows.values() for s in r})
for r in sorted(rows):
    print(f'{r:4} ' + ' '.join(f'{rows[r].get(s, "-"):16}' for s in slots))
