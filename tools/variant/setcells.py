# Set the platform (5th) and verdict (6th) cells of the docs/experiments.md row whose first cell is NAME, keeping CRLF.
# Usage: python -I tools/variant/setcells.py NAME PLATFORM VERDICT  (an empty string keeps that cell; a VERDICT starting with '+' is appended)
import sys
name, plat, verdict = sys.argv[1], sys.argv[2], sys.argv[3]
p = 'docs/experiments.md'
with open(p, encoding='utf-8', newline='') as f: s = f.read()
lines = s.split('\r\n')
hits = [k for k, l in enumerate(lines) if l.startswith('| ' + name + ' |')]
assert len(hits) == 1, hits
k = hits[0]
cells = [c.strip() for c in lines[k][1:-1].split('|')]  # empty cells ("| |") count too
assert len(cells) == 6, len(cells)
if plat: cells[4] = plat
if verdict: cells[5] = (cells[5] + ' ' + verdict[1:]).strip() if verdict.startswith('+') else verdict
lines[k] = '| ' + ' | '.join(cells) + ' |'
with open(p, 'w', encoding='utf-8', newline='') as f: f.write('\r\n'.join(lines))
print(lines[k][:300])
