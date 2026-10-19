"""Summarise a `cambc matches summary --json` file: final value of each metric per owner, plus top-level keys."""
import json, sys

data = json.load(open(sys.argv[1]))
print('keys', list(data.keys()))
for k, v in data.items():
    if k != 'championTimelines' and not isinstance(v, list):
        print(k, json.dumps(v)[:400])
rows = {}
for t in data.get('championTimelines', []):
    o = t['owner']
    name = f"{o['team']}:{o['name']}"
    runs = t['runs']
    rows.setdefault(name, {})[t['metric']] = runs[-1]['value'] if runs else None
metrics = sorted({m for r in rows.values() for m in r})
print('metrics', metrics)
for name, r in sorted(rows.items()):
    print(name, {m: r.get(m) for m in metrics})
for k, v in data.items():
    if isinstance(v, list) and k != 'championTimelines':
        print(k, len(v), json.dumps(v[:3])[:600])
