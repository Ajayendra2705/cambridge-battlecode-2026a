"""Pinned panel on the maps of one team size: python -I tools/platform/sizepanel.py PINNED_PANEL SIZE NAME [GROUPS_PER_TEAM]

A draft change for one team size changes only the games of that size, so a panel of those maps alone tests it with no
wasted games. Reads results/panels/specs_PINNED_PANEL.txt (team:maps:sides:source group) and writes
results/panels/specs_NAME.txt: one group per team (default) with five maps of the size from data/maps_size<SIZE>.txt, taken in
turn so the panel covers the list, sides alternating, each group keeping the team's first source group, so the opponents
play their bots of that run. Play the base and the variant on the same panel: games pair exactly.
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src, size, name = sys.argv[1], sys.argv[2], sys.argv[3]
per = int(sys.argv[4]) if len(sys.argv) > 4 else 1
specs = open(os.path.join(ROOT, 'results', 'panels', f'specs_{src}.txt'), encoding='utf-8').read().split()
# The list holds local file names; the platform's map names use underscores for their hyphens (a hyphen makes
# `match-groups create` fail, and gate.sh retries that group for ever: 11-02 base1503_s3p).
maps = open(os.path.join(ROOT, 'data', f'maps_size{size}.txt'), encoding='utf-8').read().strip().replace('-', '_').split(',')
first = {}
for s in specs:
    t, _, _, g = s.split(':')
    first.setdefault(t, g)
out, k = [], 0
for rep in range(per):
    for t, g in first.items():
        ms = [maps[(k + i) % len(maps)] for i in range(5)]
        k += 5
        sides = 'a,b,a,b,a' if (k // 5 + rep) % 2 else 'b,a,b,a,b'
        out.append(f'{t}:{",".join(ms)}:{sides}:{g}')
open(os.path.join(ROOT, 'results', 'panels', f'specs_{name}.txt'), 'w', encoding='utf-8').write(' '.join(out) + '\n')
print(len(out), 'groups', 5 * len(out), 'games on', len(maps), 'maps')
