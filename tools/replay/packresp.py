# Responses to a pack sighting, to r1000: a champion (off spawn) gets 3+ enemy champions within 8 that outnumber its
# side there (itself + allies within 6) after 5 rounds without. Its next 5 rounds are classed: left (nearest pack member
# 2+ tiles farther), fought (hit champions in 2+ rounds), stood (no move in 3+ rounds; on or beside camps that are
# dead = capture or respawn wait, alive = gather or camp fight), farmed (camp hits in 2+ rounds), closed (nearest pack
# member 2+ tiles nearer), other. Per side: episodes per game, share by response, P(death within 15) per response.
# usage: python -I tools/replay/packresp.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    start = {t: [(o['x'], o['y']) for o in rows[0]['c'] if 'x' in o and o['t'] == t] for t in (0, 1)}
    if not start[0] or not start[1]: continue
    def off(o): return o['a'] and 'x' in o and min(D.dist((o['x'], o['y']), q) for q in start[o['t']]) > 1
    grp, members, gtiles = D.camp_groups(rows, n)
    camp_tile = {}
    for g, ts in gtiles.items():
        for tl in ts: camp_tile[tl] = g
    quiet = [0] * n
    for k in range(len(rows) - 16):
        b = rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            c = b['c'][i]
            if not off(c): quiet[i] = 0; continue
            t = c['t']; p = (c['x'], c['y'])
            pack = [j for j in range(n) if b['c'][j]['t'] != t and off(b['c'][j]) and D.dist(p, (b['c'][j]['x'], b['c'][j]['y'])) <= 8]
            al = sum(1 for j in range(n) if j != i and b['c'][j]['t'] == t and off(b['c'][j]) and D.dist(p, (b['c'][j]['x'], b['c'][j]['y'])) <= 6)
            if len(pack) < 3 or al + 1 >= len(pack):
                quiet[i] += 1; continue
            fresh = quiet[i] >= 5; quiet[i] = 0
            if not fresh: continue
            w = D.who(t, us)
            def near(r, q): return min((D.dist(q, (r['c'][j]['x'], r['c'][j]['y'])) for j in pack if r['c'][j]['a'] and 'x' in r['c'][j]), default=99)
            d0 = near(b, p); still = hitc = hitm = 0; alive5 = True; last = b
            for kk in range(k, k + 5):
                r0, r1 = rows[kk], rows[kk + 1]
                if not (r1['c'][i]['a'] and 'x' in r1['c'][i]): alive5 = False; break
                q0 = (r0['c'][i]['x'], r0['c'][i]['y']); q1 = (r1['c'][i]['x'], r1['c'][i]['y'])
                still += q0 == q1; hitc += bool(D.enemy_hits(r0, i, n)); hitm += bool(D.camp_hits(r0, i)); last = r1
            q5 = (last['c'][i]['x'], last['c'][i]['y']) if last['c'][i]['a'] and 'x' in last['c'][i] else p
            d5 = near(last, q5)
            if d5 >= d0 + 2: resp = 'left'
            elif hitc >= 2: resp = 'fought'
            elif still >= 3:
                # On or beside a camp tile: dead camps there -> capture or respawn wait, live -> gather or camp fight.
                g = next((camp_tile[(p[0] + dx, p[1] + dy)] for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (p[0] + dx, p[1] + dy) in camp_tile), None)
                if g is None: resp = 'stood (no camp)'
                else: resp = 'stood (dead group)' if all(b['mh'][j] == 0 for j in members[g]) else 'stood (live group)'
            elif hitm >= 2: resp = 'farmed'
            elif d5 <= d0 - 2: resp = 'closed in'
            else: resp = 'other'
            dies = any(not rows[kk]['c'][i]['a'] for kk in range(k + 1, k + 16))
            hb = 'hp80+' if c.get('hp', 0) >= 0.8 * max(1, c.get('mhp', 1)) else 'hp<80'
            for key in ((w, resp), (w, 'all'), (w, hb, resp), (w, hb, 'all')):
                C[key] += 1; C[key + ('d',)] += dies
            C[(w, 'dist0', min(d0, 8))] += 1
RESP = ('left', 'fought', 'stood (dead group)', 'stood (live group)', 'stood (no camp)', 'farmed', 'closed in', 'other')
print(f'{ng} games to r1000: pack sightings (3+ enemies within 8 outnumbering us, after 5 quiet rounds); response in the next 5 rounds')
for w in ('us', 'them'):
    m = max(1, C[(w, 'all')])
    print(f"  {w:4} {C[(w, 'all')] / ng:5.2f} per game, P(death in 15) {C[(w, 'all', 'd')] / m:.3f}; nearest pack member at sighting: "
          + ' '.join(f"{d}:{C[(w, 'dist0', d)] / m:.0%}" for d in range(1, 9)))
    for r in RESP:
        k = C[(w, r)]
        if k: print(f"      {r:20} {k / m:5.1%}  P(death) {C[(w, r, 'd')] / k:.3f}   (hp80+: {C[(w, 'hp80+', r)] / max(1, C[(w, 'hp80+', 'all')]):5.1%} P {C[(w, 'hp80+', r, 'd')] / max(1, C[(w, 'hp80+', r)]):.3f})")
