"""Tribute restart loops per side: a restart is a tribute issued again with the same bag before the earlier channel
(ceil(bag / 10) turns) could have completed; an episode is a champion's run of restarts. For each episode: the bag, the
rounds it lasted, and the bag's fate within 150 rounds of its end (banked: the score rose by 90% of the bag while the
bag emptied; died; dropped; open at the game's end; other).

usage: python -I tools/replay/loops.py [--list] DIR...   (decoded folders; made for rows trA and trB, 11-01)
--list also prints, per game with a loop of ours, the map, result, final scores and each of our episodes.
"""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
C = collections.Counter(); ng = 0; bysize = collections.Counter()
LIST = '--list' in sys.argv
for us, res, mp, meta, rows in D.games([a for a in sys.argv[1:] if a != '--list']):
    ng += 1
    mine = []  # our episodes: (first round, last round, bag, fate)
    n = len(rows[0]['c'])
    last_start = {}
    episode = {}
    for k, r in enumerate(rows):
        for i in range(n):
            a = r['act'][i] if i < len(r['act']) else []
            c = r['c'][i]
            if not any(x[0] == 'tribute' for x in a) or c.get('g', 0) <= 0: continue
            g = c['g']; turns = max(1, -(-g // 10))
            w = D.who(c['t'], us)
            prev = last_start.get(i)
            if prev is not None and r['r'] - prev[0] < prev[1] and prev[2] == g:
                C[(w, 'restarts')] += 1
                ep = episode.setdefault(i, [prev[0], r['r'], g, k])
                ep[1] = r['r']
            else:
                # close the previous episode of this champion
                if i in episode:
                    ep = episode.pop(i); C[(w, 'episodes')] += 1; C[(w, 'stuck rounds')] += ep[1] - ep[0] + 1
                    C[(w, 'episode gems')] += ep[2]
                    # fate: look ahead from the episode end
                    fate = 'other'
                    for q in rows[ep[3]:ep[3] + 150]:
                        me = q['c'][i]
                        if not me['a']: fate = 'died'; break
                        if me.get('g', 0) < ep[2] * 0.5:
                            fate = 'banked' if q['sg'][me['t']] - rows[ep[3]]['sg'][me['t']] >= ep[2] * 0.9 else 'dropped'; break
                    C[(w, 'fate ' + fate)] += 1
                    if w == 'us': mine.append((ep[0], ep[1], ep[2], fate))
            last_start[i] = (r['r'], turns, g)
    for i, ep in episode.items():
        w = D.who(rows[0]['c'][i]['t'], us); C[(w, 'episodes')] += 1; C[(w, 'stuck rounds')] += ep[1] - ep[0] + 1; C[(w, 'episode gems')] += ep[2]; C[(w, 'fate open at end')] += 1
        if w == 'us': mine.append((ep[0], ep[1], ep[2], 'open at end'))
    if LIST and mine:
        sg = rows[-1]['sg']
        print(f"{mp} {res} {sg[us]}-{sg[1 - us]} r{rows[-1]['r']}: " + '; '.join(f'r{a}-{b} bag {g} {f}' for a, b, g, f in sorted(mine)))
print(f'{ng} games')
for w in ('us', 'them'):
    e = max(1, C[(w, "episodes")])
    print(f"  {w:4} restarts {C[(w,'restarts')]/ng:.2f}/game  episodes {C[(w,'episodes')]/ng:.2f}/game  mean bag {C[(w,'episode gems')]/e:.0f}  rounds stuck/episode {C[(w,'stuck rounds')]/e:.1f}  fates: "
          + ', '.join(f"{k[1][5:]} {v}" for k, v in sorted(C.items()) if k[0] == w and k[1].startswith('fate')))
