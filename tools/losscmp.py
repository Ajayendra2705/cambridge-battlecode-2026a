"""Compare runs game by game keyed by (opponent name, map): python -I tools/losscmp.py RUN1 RUN2 ...
Rows show W/L and our-their gems per run; a run without that game shows '-'."""
import re, subprocess, sys, collections
runs = sys.argv[1:]
res = collections.defaultdict(dict)
for run in runs:
    ids = [l.split()[1:] for l in open('tools/gate.log') if l.split()[:1] == [run]][-1]
    out = subprocess.run(['python', '-I', 'tools/panel_result.py', *ids], capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
    for m in re.finditer(r'^(\S+)\s+(WIN|loss)\s+(\d+)\s*-\s*(\d+)\s+r\s*(\d+).*vs (.+)$', out, re.M):
        key = (m.group(6).strip(), m.group(1))
        res[key][run] = ('W' if m.group(2) == 'WIN' else 'L') + f' {m.group(3)}-{m.group(4)}'
print(f"{'opponent':22} {'map':22} " + ' '.join(f'{r:16}' for r in runs))
tot = collections.Counter()
for key in sorted(res):
    if not all(r in res[key] for r in runs[1:]): continue
    print(f'{key[0][:22]:22} {key[1]:22} ' + ' '.join(f'{res[key].get(r, "-"):16}' for r in runs))
    for r in runs:
        if res[key].get(r, ' ')[0] == 'W': tot[r] += 1
print('wins on these games:', dict(tot))
