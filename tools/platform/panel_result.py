"""Total wins and gems for a panel: python -I tools/platform/panel_result.py GROUP_ID..."""
import json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'platform', 'group.py'), *sys.argv[1:]], capture_output=True, text=True, encoding='utf-8').stdout
print(out)
rows = re.findall(r'^\S+\s+(WIN |loss)\s+(\d+) -\s+(\d+)', out, re.M)
print('wins', sum(r[0] == 'WIN ' for r in rows), 'of', len(rows), 'our gems', sum(int(r[1]) for r in rows), 'their gems', sum(int(r[2]) for r in rows))
d = re.findall(r'deaths us\s+(\d+) them\s+(\d+)', out)
print('deaths us', sum(int(a) for a, b in d), 'them', sum(int(b) for a, b in d))
