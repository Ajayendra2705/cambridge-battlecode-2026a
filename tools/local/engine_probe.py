"""Print the engine probe's output (tools/local/engine_probe.patch) from a local replay bundle: champion designs,
game settings, the item table, and the item names per index for tools/replay/decoded.py ITEMS.
usage: python -I tools/local/engine_probe.py BUNDLE.repl26a   (from `cambc run exp/ps1 exp/ps1 --rounds 30 -o DIR`)"""
import re, sys, zipfile

STAT = {'strength': 'str', 'focus': 'focus', 'health': 'hp'}
z = zipfile.ZipFile(sys.argv[1])
raw = z.read('replay.repl26a')
engine = f'v{raw[8]}_{raw[9]}_{raw[10]}'
# Probe lines carry NUL bytes before them in the bundle's stdout.
lines = [m.group(1).split() for l in z.read('team-a.stdout').decode('utf-8', 'replace').splitlines()
         if (m := re.search(r'(P[SGNI] .*)', l))]
print(f'engine {engine}')
print('\n| Champion | Health | Strength | Focus | Camp damage |\n|---|---|---|---|---|')
for p in lines:
    if p[0] == 'PS': print(f'| {p[1]} | {p[3]} | {p[5]} | {p[7]} | {p[9]} |')
for p in lines:
    if p[0] == 'PG': print('\nsettings: ' + ' '.join(p[1:]))
count = next((int(p[1]) for p in lines if p[0] == 'PN'), 0)
items = {int(p[1]): p for p in lines if p[0] == 'PI'}
print(f'\n{count} item types\n\n| i | Item | Cost | Combine | hp | str | focus | Passive | Magnitude | Buyable |\n|---|---|---|---|---|---|---|---|---|---|')
for i in sorted(items):
    p = items[i]
    print(f'| {i} | {p[2]} | {p[4]} | {p[6]} | {p[8]} | {p[10]} | {p[12]} | {p[14]} | {p[16]} | {p[18]} |')
missing = [i for i in range(count) if i not in items]
if missing: print(f'\nmissing item lines {missing}: run more rounds')
names = []
for i in range(count):
    m = re.match(r'(\w+?)_(shard|emblem)_of_(strength|focus|health)$', items[i][2]) if i in items else None
    names.append(f'{m.group(1)}_{STAT[m.group(3)]} {m.group(2)}' if m else items.get(i, [None, None, f'item{i}'])[2])
print(f"\ndecoded.py ITEMS entry:\n    '{engine}': {names},")
