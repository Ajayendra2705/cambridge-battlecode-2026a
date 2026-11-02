"""How much each side moves as a pack, by round band: mean teammates within 6 (and within 3) of a living champion.

usage: python -I tools/replay/packindex.py DIR [DIR ...] [--by-opp]

Sampled every 5 rounds. Per band: mean allies within 6 and within 3, share of champion-rounds with no ally within 6,
share of team-rounds where the largest cluster (allies within 6 of one champion, plus itself) holds all living champions.
Team sizes are mixed, so the same is printed per team size. Spawn rounds (a champion on its team's spawn tiles) count as they are.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

BANDS = [(1, 50), (51, 100), (101, 150), (151, 300), (301, 600), (601, 1000), (1001, 2000)]


def band(r):
    for lo, hi in BANDS:
        if lo <= r <= hi: return (lo, hi)
    return None


C = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    size = sum(1 for d in meta['drafts'][us] for _ in ([0, 1] if d == 3 else [0]))  # Cassi fields two bodies
    picks = len(meta['drafts'][us])
    for row in rows[::5]:
        b = band(row['r'])
        if not b: continue
        al = [c for c in row['c'] if c['a'] and 'x' in c]
        for t in (0, 1):
            w = D.who(t, us)
            mine = [(c['x'], c['y']) for c in al if c['t'] == t]
            if not mine: continue
            big = 0
            for p in mine:
                a6 = sum(1 for q in mine if q != p and D.dist(p, q) <= 6) + (mine.count(p) - 1)
                a3 = sum(1 for q in mine if q != p and D.dist(p, q) <= 3) + (mine.count(p) - 1)
                big = max(big, a6 + 1)
                for key in ((w, b), (w, b, picks)):
                    C[key + ('n',)] += 1; C[key + ('a6',)] += a6; C[key + ('a3',)] += a3; C[key + ('alone',)] += (a6 == 0)
            for key in ((w, b), (w, b, picks)):
                C[key + ('tn',)] += 1; C[key + ('share',)] += big / len(mine)
for picks in (None, 3, 4, 5):
    print('all sizes' if picks is None else f'{picks} picks')
    for b in BANDS:
        parts = []
        for w in ('us', 'them'):
            key = (w, b) if picks is None else (w, b, picks)
            n = max(1, C[key + ('n',)])
            parts.append(f'{w:4} a6 {C[key + ("a6",)] / n:4.2f} a3 {C[key + ("a3",)] / n:4.2f} alone {C[key + ("alone",)] / n:4.2f} biggest {C[key + ("share",)] / max(1, C[key + ("tn",)]):4.2f}')
        print(f'  r{b[0]:4}-{b[1]:4} | ' + ' | '.join(parts))
