# Poked rounds, to r1000, us vs them: a champion off its spawn takes a hit from an enemy champion standing beyond the
# champion's own reach (a shooter's basic attack or a spell, measured from the hitter's tile at the round start to the
# hit entry's tile; melee basic attacks and melee casts other than Marcella's never count) and itself hits no enemy
# champion that round. Per game: poked rounds and episodes (a poke after 5+ quiet rounds starts one); for episodes:
# what it does over the next 3 rounds (net distance to the poker: closer / level / away; any champion hit; camp hits),
# P(it dies within 10), and the same by melee / ranged and by enemies within 6 (1 / 2 / 3+). Also how many of an
# episode's next 3 rounds it is hit again from beyond reach (end-of-round tiles).
# usage: python -I tools/replay/poked.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
def pos(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    spawn = {t: {pos(c) for c in rows[0]['c'] if c['t'] == t and pos(c)} for t in (0, 1)}
    last = {}
    L = len(rows)
    for k in range(L - 11):
        a = rows[k]
        if a['r'] > 1000: break
        pokes = collections.defaultdict(list)
        for e in range(n):
            # The hitter's place at the hit: a shooter cannot walk and shoot in one turn, so its start (the last row);
            # the victim's place: the hit entry's tile. Melee basic attacks are never pokes.
            pe = pos(rows[k - 1]['c'][e]) if k else None
            for x in D.enemy_hits(a, e, n):
                if D.RANGE.get(a['c'][e]['ty'], 1) <= 1 and (x[0] == 'attack' or D.NAMES[a['c'][e]['ty']] != 'marcella'): continue
                j = x[-1]; at = (x[2], x[3]) if x[0] == 'cast' else (x[1], x[2])
                if pe and D.dist(pe, at) > D.RANGE.get(a['c'][j]['ty'], 1): pokes[j].append(e)
        for j, es in pokes.items():
            c = a['c'][j]; p = pos(c)
            if not p or p in spawn[c['t']] or D.enemy_hits(a, j, n): continue
            w = D.who(c['t'], us); C[(w, 'rounds')] += 1
            fresh = k - last.get(j, -99) > 5; last[j] = k
            if not fresh: continue
            e = es[0]; pe = pos(a['c'][e]); d0 = D.dist(p, pe)
            hit = camp = again = 0; d3 = None
            for t in range(1, 4):
                r = rows[k + t]; q = pos(r['c'][j])
                if not q: break
                hit |= bool(D.enemy_hits(r, j, n)); camp |= bool(D.camp_hits(r, j))
                for e2 in range(n):
                    pe2 = pos(r['c'][e2])
                    if pe2 and any(x[-1] == j for x in D.enemy_hits(r, e2, n)) and D.dist(pe2, q) > D.RANGE.get(c['ty'], 1): again += 1; break
                pe_t = pos(r['c'][e])
                if pe_t: d3 = D.dist(q, pe_t)
            dies = any(not rows[k + t]['c'][j]['a'] for t in range(1, 11))
            resp = 'hit' if hit else 'camp' if camp else 'dead/none' if d3 is None else 'closer' if d3 < d0 else 'away' if d3 > d0 else 'level'
            en = sum(1 for o in a['c'] if o['t'] != c['t'] and pos(o) and D.dist(p, pos(o)) <= 6)
            kind = 'melee' if D.RANGE.get(c['ty'], 1) <= 1 else 'ranged'
            for key in ('all', kind, f'en{min(en, 3)}'):
                C[(w, key, 'n')] += 1; C[(w, key, resp)] += 1; C[(w, key, 'die')] += dies; C[(w, key, 'again')] += again
                C[(w, key, resp, 'die')] += dies
RESP = ('hit', 'camp', 'closer', 'level', 'away', 'dead/none')
print(f'{ng} games to r1000: poked = hit by an enemy champion beyond own reach, no own champion hit that round')
for w in ('us', 'them'):
    print(f'  {w:4} poked rounds {C[(w, "rounds")] / ng:5.1f}/g, episodes {C[(w, "all", "n")] / ng:5.1f}/g')
    for key in ('all', 'melee', 'ranged', 'en1', 'en2', 'en3'):
        m = C[(w, key, 'n')]
        if not m: continue
        print(f'    {key:6} {m / ng:5.1f}/g  P(dies 10) {C[(w, key, "die")] / m:.3f}  hit again from beyond reach {C[(w, key, "again")] / m:.2f}/3r  next 3 rounds: '
              + ', '.join(f'{x} {C[(w, key, x)] / m:.2f} (P {C[(w, key, x, "die")] / max(1, C[(w, key, x)]):.2f})' for x in RESP))
