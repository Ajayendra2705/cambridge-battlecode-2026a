"""Pinned panel on a chosen list of maps: python -I tools/platform/mappanel.py PINNED_PANEL NAME MAP1,MAP2,... [GROUPS_PER_TEAM]

A change that acts only on some maps (a per-map router, a map table) changes only those games, so a panel of those maps tests it
with no wasted games. Reads results/panels/specs_PINNED_PANEL.txt (team:maps:sides:source group) and writes
results/panels/specs_NAME.txt: one group per team (default) with five maps taken in turn from the list, sides alternating, each group
keeping the team's first source group, so the opponents play their bots of that run. Play the base and the variant on the same
panel: games pair exactly. Map names use underscores (a hyphen makes `match-groups create` fail).
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src, name, maps = sys.argv[1], sys.argv[2], sys.argv[3].replace('-', '_').split(',')
per = int(sys.argv[4]) if len(sys.argv) > 4 else 1
specs = open(os.path.join(ROOT, 'results', 'panels', f'specs_{src}.txt'), encoding='utf-8').read().split()
first = {}
for s in specs:
    t, _, _, g = s.split(':')
    first.setdefault(t, g)
out, k = [], 0
for rep in range(per):
    for n, (t, g) in enumerate(first.items()):
        ms = [maps[(k + i) % len(maps)] for i in range(5)]
        k += 5
        sides = 'a,b,a,b,a' if (n + rep) % 2 else 'b,a,b,a,b'
        out.append(f'{t}:{",".join(ms)}:{sides}:{g}')
open(os.path.join(ROOT, 'results', 'panels', f'specs_{name}.txt'), 'w', encoding='utf-8').write(' '.join(out) + '\n')
print(len(out), 'groups', 5 * len(out), 'games on', len(maps), 'maps')
