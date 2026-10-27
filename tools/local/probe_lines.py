"""Print our side's stdout lines starting with TAG from every replay of PREFIX in a `multi.py --keep` run folder.

Each line is prefixed with the replay's map, so a reader can count per game: `probe_lines.py RUNDIR exp.fw2l FW | ...`.
"""
import glob, os, re, sys, zipfile

run, prefix, tag = sys.argv[1], sys.argv[2], sys.argv[3]
for path in sorted(glob.glob(os.path.join(run, prefix + '~*.repl26a'))):
    parts = os.path.basename(path)[:-len('.repl26a')].split('~')
    team = parts[-1][0].lower()  # ~A / ~B is our side.
    text = re.sub(r'[^\x20-\x7e\n]', '', zipfile.ZipFile(path).read(f'team-{team}.stdout').decode('latin1'))
    for line in text.splitlines():
        if line.startswith(tag + ' '):
            print(parts[-2] + '~' + parts[-1], line)
