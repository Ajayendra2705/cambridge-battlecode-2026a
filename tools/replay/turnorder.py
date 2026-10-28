"""Who acts first in contact, from orderdump.mjs output.

usage: python -I tools/replay/turnorder.py ORDERS_DIR [FIGHTS_DIR]
Platform runs: FIGHTS_DIR is the decoded run (its index.txt gives our side). Local multi.py runs: leave it out; the file
names (CAND~OPP~MAP~SIDE) give the candidate and our side, and the lines are per candidate.
For every round (1-1000) and every pair of our champion and theirs, both alive within 2 tiles at the round start, counts
whether ours ended its turn first. An opponent "reorders" in a game when its own champions ran in 4 or more orders.
Deaths: a champion alive at a round start and dead at the next, "in contact" when an enemy stood within 2 at the start;
"enemy first" when the nearest such enemy acted before the victim in that round.
"""
import collections, json, os, sys

orders = sys.argv[1]
side = {}
if len(sys.argv) > 2:
    for line in open(os.path.join(sys.argv[2], 'index.txt'), encoding='utf-8'):
        p = line.split()
        if len(p) >= 3: side[p[0]] = 0 if p[2] == 'a' else 1
C = collections.Counter()
groups = set()
for f in sorted(os.listdir(orders)):
    stem = f[:-5]
    if side:
        if stem not in side: continue
        us = side[stem]
    else:
        parts = stem.split('~')
        if len(parts) != 4: continue
        us = 0 if parts[3] == 'A' else 1
    g = json.load(open(os.path.join(orders, f)))
    teams, rounds = g['teams'], g['rounds']
    opp = 'reorders' if len({tuple(i for i in o if teams[i] != us) for _, o, _ in rounds}) >= 4 else 'draft order'
    grp = (stem.split('~')[0] if not side else 'run', opp)
    groups.add(grp)
    C[grp, 'games'] += 1
    nxt = {r: s for r, _, s in rounds}
    for r, o, s in rounds:
        pos = {i: k for k, i in enumerate(o)}
        live = [i for i in range(len(teams)) if s[i][4] and s[i][0] >= 0]
        for i in live:
            if teams[i] != us: continue
            for j in live:
                if teams[j] == us or max(abs(s[i][0] - s[j][0]), abs(s[i][1] - s[j][1])) > 2 or i not in pos or j not in pos: continue
                C[grp, 'pairs'] += 1
                C[grp, 'ours first'] += pos[i] < pos[j]
        if r + 1 not in nxt: continue
        s2 = nxt[r + 1]
        for v in live:
            if s2[v][4]: continue
            who = 'us' if teams[v] == us else 'them'
            C[grp, who, 'deaths'] += 1
            near = [(max(abs(s[v][0] - s[j][0]), abs(s[v][1] - s[j][1])), j) for j in live if teams[j] != teams[v]]
            near = [x for x in near if x[0] <= 2]
            if not near: continue
            j = min(near)[1]
            C[grp, who, 'contact deaths'] += 1
            C[grp, who, 'enemy first'] += j in pos and v in pos and pos[j] < pos[v]
for grp in sorted(groups):
    n = C[grp, 'games']
    print('%s vs opponents in %s: %d games, ours first in %.3f of %d contact pairs' % (grp[0], grp[1], n, C[grp, 'ours first'] / max(1, C[grp, 'pairs']), C[grp, 'pairs']))
    for who in ('us', 'them'):
        cd = C[grp, who, 'contact deaths']
        print('   %-4s deaths %.2f per game, in contact %.2f (enemy first in %.2f of them)' % (who, C[grp, who, 'deaths'] / n, cd / n, C[grp, who, 'enemy first'] / max(1, cd)))
for c in sorted({g[0] for g in groups}):
    pairs = sum(C[g, 'pairs'] for g in groups if g[0] == c)
    first = sum(C[g, 'ours first'] for g in groups if g[0] == c)
    games = sum(C[g, 'games'] for g in groups if g[0] == c)
    print('%s all: %d games, ours first in %.3f of %d contact pairs' % (c, games, first / max(1, pairs), pairs))
