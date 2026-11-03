"""Make a pinned panel from match groups a teammate played: python -I tools/platform/panelof.py MATCHES.json NAME RUN FROM TO [--skip GROUP8,...]

MATCHES.json comes from tools/platform/recentgroups.py --out. Takes our unranked groups created between the ISO times FROM and TO, and writes results/panels/specs_NAME.txt with one line per group,
`TEAM:m1,..,m5:s1,..,s5:SOURCE_GROUP`, so a gate plays the same opponents' bots on the same maps and sides. Appends `RUN@NAME group-ids...` to results/gate.log, so those groups serve as the base without a rerun. Other
teams' scrims against us land in the same list: read the printed lines before using the panel.
"""
import collections, json, sys

args = sys.argv[1:]
skip = set()
if '--skip' in args:
    k = args.index('--skip')
    skip = set(args[k + 1].split(','))
    del args[k:k + 2]
src, name, run, a, b = args
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
ms = json.load(open(src, encoding='utf-8'))
G = collections.OrderedDict()
for m in ms:
    G.setdefault(m['groupId'], []).append(m)
rows = []
for gid, gs in G.items():
    gs = sorted(gs, key=lambda m: m['position'])
    t = gs[0]['createdAt']
    if not a <= t < b or len(gs) != 5 or gid[:8] in skip:
        continue
    opp = [x for x in gs[0]['teams'] if x['teamId'] != OUR][0]
    me = [[x for x in m['teams'] if x['teamId'] == OUR][0] for m in gs]
    rows.append((t, gid, opp['teamId'], opp['name'], [m['map'] for m in gs], [x['side'] for x in me], sum(x['result'] == 'win' for x in me)))
rows.sort()
lines = [f"{r[2]}:{','.join(r[4])}:{','.join(r[5])}:{r[1]}" for r in rows]
open(f'results/panels/specs_{name}.txt', 'w', encoding='utf-8').write(' '.join(lines) + '\n')
open('results/gate.log', 'a', encoding='utf-8').write(f"{run}@{name} " + ' '.join(r[1] for r in rows) + '\n')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
for r in rows:
    print(r[0][11:16], r[1][:8], r[3][:18], ','.join(r[4])[:66], ''.join(r[5]), r[6])
print(len(rows), 'groups,', sum(r[6] for r in rows), 'wins of', 5 * len(rows))
