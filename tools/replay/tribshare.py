"""Gems tributed and gold by type: python -I tribshare.py DIR...  Gem drops while alive (tribute) per champion type, per team-game with that type, at r300, r600, r1000, and the same type's total gold earned by r300, r600, r1000."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
RS = (150, 300, 600, 1000)
T = collections.Counter(); N = collections.Counter(); G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    for i, c0 in enumerate(rows[0]['c']):
        w = D.who(c0['t'], us); ty = D.NAMES[c0['ty']]
        N[(w, ty)] += 1
        trib = 0; earned = 0; R = 0
        ks = 0
        for a, b in zip(rows, rows[1:]):
            p, c = a['c'][i], b['c'][i]
            if p['a'] and c['a']:
                dg = p.get('g', 0) - c.get('g', 0)
                if dg > 0:
                    trib += dg
                d = D.gold_held(meta, c) - D.gold_held(meta, p)
                if d > 0:
                    earned += d
            while ks < len(RS) and b['r'] >= RS[ks]:
                T[(w, ty, RS[ks])] += trib; G[(w, ty, RS[ks])] += earned
                ks += 1
        while ks < len(RS):
            T[(w, ty, RS[ks])] += trib; G[(w, ty, RS[ks])] += earned
            ks += 1
for ty in ('marcella', 'vesper', 'vendetta', 'heart', 'willow', 'cassi', 'issac', 'tavi', 'ryth'):
    for w in ('us', 'them'):
        n = N[(w, ty)]
        if n < 10:
            continue
        print(f"{ty:9} {w:4} n {n:3} | tributed " + ' '.join(f"r{R}:{T[(w,ty,R)]/n:4.0f}" for R in RS) + " | gold " + ' '.join(f"r{R}:{G[(w,ty,R)]/n:5.0f}" for R in RS))
