# Insert a row into docs/experiments.md after the row whose first cell is AFTER, keeping CRLF.
# Usage: python -I tools/variant/addrow.py AFTER "| name | parent | change | local | platform | verdict |"
import sys
after, row = sys.argv[1], sys.argv[2]
p = 'docs/experiments.md'
with open(p, encoding='utf-8', newline='') as f: s = f.read()
lines = s.split('\r\n')
i = next(k for k, l in enumerate(lines) if l.startswith('| ' + after + ' |'))
lines.insert(i + 1, row)
with open(p, 'w', encoding='utf-8', newline='') as f: f.write('\r\n'.join(lines))
print('inserted after line', i + 1)
