"""A pinned panel of our newest ranked groups: python -I tools/platform/rkpanel.py OURMAPS.json NAME NGROUPS [--since ISO] [--per-team N]

OURMAPS.json comes from tools/platform/ourmaps.py (it must hold `group` and `oppId`). Writes results/panels/specs_NAME.txt with one line per group, `TEAM:m1,..,m5:s1,..,s5:SOURCE_GROUP`, newest
groups first and at most N (default 1) per rival, so a gate replays the rivals near our rank on the maps ranked play gave us, against the bots they had then. These teams decide the rating, and the
panels against ranks 1-20 do not measure them. With --since set to the time the live bot went live, the panel's source groups are that bot's own games, so they serve as its base without a rerun:
results for the base go to data/cache/res_RUN_NAME.json (rcmp.py's format) as RUN = `live_NAME`.
"""
import collections, json, os, sys
args = sys.argv[1:]
since = None
per = 1
if '--since' in args:
    k = args.index('--since')
    since = args[k + 1]
    del args[k:k + 2]
if '--per-team' in args:
    k = args.index('--per-team')
    per = int(args[k + 1])
    del args[k:k + 2]
src, name, n = args[0], args[1], int(args[2])
games = json.load(open(src, encoding='utf-8'))
if since:
    games = [g for g in games if g['created'] >= since]
G = collections.OrderedDict()
for g in games:
    G.setdefault(g['group'], []).append(g)
seen = collections.Counter()
lines, base, chosen = [], {}, []
for gid, gs in G.items():
    if len(gs) != 5:
        continue
    t = gs[0]['oppId']
    if seen[t] >= per:
        continue
    seen[t] += 1
    gs = sorted(gs, key=lambda x: x['created'])
    lines.append(f"{t}:{','.join(x['map'] for x in gs)}:{','.join(x['side'] for x in gs)}:{gid}")
    chosen.append((gs[0]['opp'], gs[0]['created'][:16], sum(x['result'] == 'win' for x in gs)))
    if len(lines) == n:
        break
os.makedirs('results/panels', exist_ok=True)
open(f'results/panels/specs_{name}.txt', 'w', encoding='utf-8').write(' '.join(lines) + '\n')
print(len(lines), 'groups, our wins in them', sum(c[2] for c in chosen))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
for c in chosen:
    print(' ', c[0][:24], c[1], c[2], 'of 5')
