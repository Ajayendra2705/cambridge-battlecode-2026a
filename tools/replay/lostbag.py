# Deaths to r1000 by the bag carried: deaths and gems lost per game per bag bucket, us vs them, with the share that died
# within 8 tiles of an altar (tribute tiles seen in the game) and the mean rounds since the champion last tributed.
# usage: python -I tools/replay/lostbag.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
B = ((0, 0), (1, 19), (20, 49), (50, 99), (100, 10**6))
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1; n = len(rows[0]['c'])
    altars = {(x[1], x[2]) for b in rows for acts in b['act'][:n] for x in acts if x[0] == 'tribute'}
    last_trib = [0] * n
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        for i in range(n):
            if any(x[0] == 'tribute' for x in (a['act'][i] if i < len(a['act']) else [])): last_trib[i] = a['r']
            pc, c = a['c'][i], b['c'][i]
            if pc['a']: C[(D.who(pc['t'], us), next(j for j, (lo, hi) in enumerate(B) if lo <= pc.get('g', 0) <= hi), 'rounds')] += 1
            if not (pc['a'] and not c['a']): continue
            w = D.who(pc['t'], us); g = pc.get('g', 0)
            k = next(j for j, (lo, hi) in enumerate(B) if lo <= g <= hi)
            near = 'x' in pc and altars and min(D.dist((pc['x'], pc['y']), q) for q in altars) <= 8
            C[(w, k)] += 1; C[(w, k, 'g')] += g; C[(w, k, 'near')] += bool(near); C[(w, k, 'since')] += a['r'] - last_trib[i]
print(f'{ng} games to r1000: deaths per game by bag carried (gems lost, share within 8 of an altar, rounds since own last tribute)')
for w in ('us', 'them'):
    print(f'  {w:4}\n    ' + '\n    '.join(f"{lo}-{hi if hi < 10**6 else '+'}: {C[(w, k)] / ng:.2f} ({C[(w, k, 'g')] / ng:.0f} g, near {C[(w, k, 'near')] / max(1, C[(w, k)]):.0%}, {C[(w, k, 'since')] / max(1, C[(w, k)]):.0f} r, alive {C[(w, k, 'rounds')] / ng:.0f} r, {1000 * C[(w, k)] / max(1, C[(w, k, 'rounds')]):.2f}/1000)"
                             for k, (lo, hi) in enumerate(B)))
