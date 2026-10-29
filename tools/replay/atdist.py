# One type (default vesper), to r1000, by side: rounds whose start has the nearest enemy champion (off its spawn) at exactly
# distance D (default 2) and no enemy within D-1: what she did (shot / shot+k0 / k0+walk+shot / walk away / walk level /
# walk closer / k1 dash (+walk) / nothing), split by whether that nearest enemy is melee, with the next round start's
# nearest-enemy distance and P(she is adjacent to an enemy at the next round start) and P(die in 10).
# usage: python -I tools/replay/atdist.py [--type NAME] [--d D] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist, enemy_hits
TY = 'vesper'; DD = 2; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--type': TY = args[1]
    elif args[0] == '--d': DD = int(args[1])
    args = args[2:]
T = NAMES.index(TY)
MELEE = {NAMES.index(x) for x in ('heart', 'marcella', 'vendetta', 'ryth', 'varg', 'ren', 'issac') if x in NAMES}
R = {w: collections.Counter() for w in ('us', 'them')}; A = {w: collections.Counter() for w in ('us', 'them')}
D = {w: collections.Counter() for w in ('us', 'them')}; ND = {w: collections.Counter() for w in ('us', 'them')}
G = collections.Counter()
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    n = len(rows[0]['c'])
    spawn = {t: set(pos(c) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    for i, c0 in enumerate(rows[0]['c']):
        if c0['ty'] != T: continue
        w = who(c0['t'], us); G[w] += 1
        death = [r for r in range(1, len(rows)) if not rows[r]['c'][i]['a'] and rows[r - 1]['c'][i]['a']]
        for r in range(len(rows) - 1):
            if rows[r]['r'] > 1000: break
            me, nx = rows[r]['c'][i], rows[r + 1]['c'][i]
            if not me['a'] or 'x' not in me: continue
            p = pos(me)
            ens = [e for e in rows[r]['c'] if e['a'] and 'x' in e and e['t'] != me['t'] and pos(e) not in spawn[e['t']]]
            if not ens: continue
            dn = min(dist(p, pos(e)) for e in ens)
            if dn != DD: continue
            e = min(ens, key=lambda e: dist(p, pos(e)))
            kind = 'melee' if e['ty'] in MELEE else 'ranged'
            acts = rows[r]['act'][i] if i < len(rows[r]['act']) else []
            shot = bool(enemy_hits(rows[r], i, n))
            casts = [x[1] for x in acts if x[0] == 'cast' and len(x) > 1]
            moved = nx['a'] and 'x' in nx and pos(nx) != p
            if moved:
                dd = dist(pos(nx), pos(e)) - dist(p, pos(e))
                mv = 'away' if dd > 0 else 'closer' if dd < 0 else 'level'
            what = ('shot' if shot else '') + ''.join(f'+k{c}' for c in casts) + (f'+walk {mv}' if moved else '')
            what = what.strip('+') or 'nothing'
            key = (kind, what)
            R[w][key] += 1; A[w][(kind, 'all')] += 1
            if not nx['a']: continue
            nd = min((dist(pos(nx), pos(x)) for x in rows[r + 1]['c'] if x['a'] and 'x' in x and x['t'] != me['t']), default=9)
            ND[w][key] += min(nd, 6); ND[w][(kind, 'adj')] += 0
            D[w][key] += any(0 < dr - r <= 10 for dr in death)
            R[w][key + ('adj next',)] += nd <= 1
print(f'{TY}: rounds with the nearest enemy at {DD} (to r1000), per game: share of such rounds (next nearest distance, P adjacent next, P die in 10)')
for kind in ('melee', 'ranged'):
    for w in ('us', 'them'):
        tot = A[w][(kind, 'all')]
        print(f'  {kind} {w}: {tot / max(1, G[w]):.1f} per game')
        items = sorted([k for k in R[w] if k[0] == kind and len(k) == 2], key=lambda k: -R[w][k])[:9]
        print('    ' + '  '.join(f"{k[1]} {R[w][k] / max(1, tot):.2f} ({ND[w][k] / max(1, R[w][k]):.1f}, {R[w][k + ('adj next',)] / max(1, R[w][k]):.2f}, {D[w][k] / max(1, R[w][k]):.2f})" for k in items))
