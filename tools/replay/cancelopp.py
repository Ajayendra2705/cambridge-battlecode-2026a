"""Chances to cancel enemy tributes with a lock, us vs them: python -I tools/replay/cancelopp.py DIR...  (run from the repo root)
For each tribute channel of side X that completed, was a champion of the other side within 2 (lock reach) of the altar
on some channel turn, or within 4? Gems in those channels per game."""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
A = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    for k, b in enumerate(rows):
        for i, acts in enumerate(b['act'][:n]):
            tr = [x for x in acts if x[0] == 'tribute']
            if not tr: continue
            c = b['c'][i]; g = c.get('g', 0)
            if g <= 0: continue
            turns = max(1, -(-g // 10)); j = min(len(rows) - 1, k + turns + 2)
            if k + turns + 2 >= len(rows): continue
            ok = rows[j]['sg'][c['t']] - b['sg'][c['t']] >= g * 0.9
            if not ok: continue
            altar = (tr[0][1], tr[0][2])
            best = 99; first2 = None
            for kk in range(k, k + turns):
                for o in rows[kk]['c']:
                    if o['t'] != c['t'] and o['a'] and 'x' in o:
                        d = D.dist(altar, (o['x'], o['y'])); best = min(best, d)
                        if d <= 2 and first2 is None: first2 = kk - k
            w = D.who(c['t'], us)  # the channeling side
            A[(w, 'n')] += 1; A[(w, 'g')] += g
            if best <= 2: A[(w, 'opp<=2')] += 1; A[(w, 'g<=2')] += g; A[(w, 'left', 'early' if first2 < turns - 1 else 'last')] += 1
            elif best <= 4: A[(w, 'opp<=4')] += 1; A[(w, 'g<=4')] += g
print(f'{ng} games: completed tribute channels per game, and those with an opposing champion within 2 / 3-4 of the altar on a channel turn')
for w in ('us', 'them'):
    print(f'  {w} channel: {A[(w, "n")] / ng:.1f} ({A[(w, "g")] / ng:.0f} gems); opponent within 2: {A[(w, "opp<=2")] / ng:.2f} ({A[(w, "g<=2")] / ng:.0f} gems, '
          f'before the last turn {A[(w, "left", "early")] / ng:.2f}); within 3-4: {A[(w, "opp<=4")] / ng:.2f} ({A[(w, "g<=4")] / ng:.0f} gems)')
