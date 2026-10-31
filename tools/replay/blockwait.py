# Respawn blocks to r1000, us vs them: rounds in which every camp of a group has been dead for 70+ rounds (past any
# respawn timer) while a champion of one side stands on one of its tiles (it holds the respawn back), and how many of
# that side's other champions wait idle within 3 of the group meanwhile (no action, same tile). Per game: blocked
# rounds by the blocking side, idle teammate-rounds beside the block, and the longest blocks (map, start, length,
# blocker type, tile, its bag). Found bb2's boss_battle freeze (10-31): our Vesper on an elk tile at the map edge with
# every other neighbour a group tile or a teammate, and all five waited 1300 rounds with 1153 gems unbanked.
# usage: python -I tools/replay/blockwait.py DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
C = collections.Counter(); ng = 0; ex = []
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    R = min(len(rows), 1000)
    dead_since = {}
    run = {}
    for k in range(R):
        r = rows[k]
        for g, js in members.items():
            if all(r['mh'][j] == 0 for j in js): dead_since.setdefault(g, k)
            else: dead_since.pop(g, None)
        for g, k0 in dead_since.items():
            if k - k0 < 70: continue
            on = [(i, c) for i, c in enumerate(r['c']) if c['a'] and 'x' in c and (c['x'], c['y']) in gtiles[g]]
            for s in ('us', 'them'):
                mine = [(i, c) for i, c in on if D.who(c['t'], us) == s]
                if not mine: run.pop((g, s), None); continue
                C[(s, 'blocked')] += 1
                run.setdefault((g, s), (k, mine[0][1]))
                for i, c in enumerate(r['c']):
                    if (i, c) in mine or not c['a'] or 'x' not in c or D.who(c['t'], us) != s: continue
                    p = (c['x'], c['y'])
                    if min(D.dist(p, t) for t in gtiles[g]) <= 3 and not (r['act'][i] if i < len(r['act']) else []):
                        C[(s, 'idle_mates')] += 1
        for (g, s), (k0, c) in list(run.items()):
            if g not in dead_since or k == R - 1:
                ex.append((k - k0, s, mp, rows[k0]['r'], D.NAMES[c['ty']], (c['x'], c['y']), c.get('g', 0)))
                run.pop((g, s))
print(f'{ng} games to r1000: rounds a game with a group dead 70+ rounds and a champion on its tiles (idle teammate-rounds within 3)')
for s in ('us', 'them'): print(f"  {s:4} blocked {C[(s, 'blocked')] / ng:6.1f}  idle mates {C[(s, 'idle_mates')] / ng:6.1f}")
print('longest (rounds, side, map, start, blocker, tile, bag):')
for e in sorted(ex, reverse=True)[:20]: print('  ', e)
