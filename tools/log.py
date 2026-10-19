"""Print a team's stdout from the newest (or given) replay bundle, filtered by an optional regex."""
import glob, os, re, sys, zipfile

root = os.path.join(os.path.dirname(__file__), '..', 'replays')
args = sys.argv[1:]
team = 'a'
path = None
pattern = None
for a in args:
    if a in ('a', 'b'): team = a
    elif a.endswith(('.repl26a', '.zip')): path = a
    else: pattern = re.compile(a)
if path is None:
    path = max(glob.glob(os.path.join(root, '**', '*.repl26a'), recursive=True), key=os.path.getmtime)
text = zipfile.ZipFile(path).read(f'team-{team}.stdout').decode('latin1')
text = re.sub(r'[^\x20-\x7e\n]', '', text)
for line in text.splitlines():
    if line.strip() and (pattern is None or pattern.search(line)):
        print(line)
