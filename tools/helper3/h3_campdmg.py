"""Damage per camp hit, us vs them, by round band, to round 1000 (h3, 10-28).

usage: python -I tools/helper3/h3_campdmg.py DIR [DIR ...]   (decoded runs, pooled)

For every camp and round in which champions of only one side hit it (attack or cast on the camp), the camp's health
drop that round (`mh`, camps act and are hit within the round; a camp that died counts its health before) is that
side's damage; per side and band: damage per hit and hits per round of such single-side camp hits, overall and for
elks only (the camp type from the meta line). Splash (Varg) and area spells on camps beside the target count toward
the target's side only when they hit the same camp, so damage per hit is a lower bound for splash users.
"""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
BANDS = ((1, 300), (301, 600), (601, 1000))
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    camps = {int(k): v for k, v in meta.get('camps', {}).items()}
    for k in range(1, len(rows)):
        q, r = rows[k - 1], rows[k]
        if r['r'] > 1000: break
        band = next(f'r{lo}-{hi}' for lo, hi in BANDS if lo <= r['r'] <= hi)
        by = collections.defaultdict(lambda: [0, 0])  # camp -> hits by team 0, team 1
        for i in range(n):
            for x in D.camp_hits(r, i): by[x[-1]][r['c'][i]['t']] += 1
        for j, (h0, h1) in by.items():
            if (h0 and h1) or j >= len(r['mh']) or j >= len(q['mh']): continue
            t = 0 if h0 else 1
            drop = q['mh'][j] - r['mh'][j]
            if drop <= 0: continue
            w = 'us' if t == us else 'them'
            kind = D.CAMPS.get(camps.get(j), '?')
            for kk in ('all', kind):
                C[w, band, kk, 'dmg'] += drop; C[w, band, kk, 'hits'] += h0 + h1
print(f'{ng} games: damage per camp hit (single-side hit rounds), us / them')
for kk in ('all', 'elk'):
    print('  ' + kk + ': ' + '   '.join(f'{lo}-{hi} {C["us", f"r{lo}-{hi}", kk, "dmg"] / max(1, C["us", f"r{lo}-{hi}", kk, "hits"]):5.0f} / '
                                     f'{C["them", f"r{lo}-{hi}", kk, "dmg"] / max(1, C["them", f"r{lo}-{hi}", kk, "hits"]):5.0f}' for lo, hi in BANDS))
