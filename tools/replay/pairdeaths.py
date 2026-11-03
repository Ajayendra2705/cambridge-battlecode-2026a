"""How the Cassi and Issac pair dies, us vs them, from decoded games: python -I tools/replay/pairdeaths.py [--round 1000] DIR...

Per pair life to the round: deaths per game, which body fell first (lower health share in the row before), the two bodies' distance and health shares in the row
before, enemies within 6 of the fallen body, its own allies within 6, its bag, and over all alive rounds the mean distance between the bodies and the share of rounds
they stand within 3 and within 8 of each other. Other bodies' deaths per game on the same teams, for comparison.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

args = sys.argv[1:]
last = 1000
if '--round' in args:
    k = args.index('--round')
    last = int(args[k + 1])
    del args[k:k + 2]
CASSI, ISSAC = D.NAMES.index('cassi'), D.NAMES.index('issac')
T = {w: collections.Counter() for w in ('us', 'them')}
O = {w: collections.defaultdict(collections.Counter) for w in ('us', 'them')}
ng = 0


def pos(c):
    return (c['x'], c['y']) if c.get('a') and 'x' in c else None


for us, res, mp, meta, rows in D.games(args):
    ng += 1
    n = len(rows[0]['c'])
    for team in (0, 1):
        idx = [j for j in range(n) if rows[0]['c'][j]['t'] == team]
        ca = next((j for j in idx if rows[0]['c'][j]['ty'] == CASSI), None)
        ia = next((j for j in idx if rows[0]['c'][j]['ty'] == ISSAC), None)
        if ca is None or ia is None:
            continue
        w = D.who(team, us)
        S = T[w]
        S['teams'] += 1
        for j in idx:
            if j not in (ca, ia):
                O[w][D.NAMES[rows[0]['c'][j]['ty']]]['teams'] += 1
        for k in range(1, len(rows)):
            r = rows[k]
            if r['r'] > last:
                break
            pr = rows[k - 1]
            for j in idx:
                if j not in (ca, ia) and pr['c'][j]['a'] and not r['c'][j]['a']:
                    O[w][D.NAMES[r['c'][j]['ty']]]['deaths'] += 1
            c0, i0 = pr['c'][ca], pr['c'][ia]
            pc, pi = pos(c0), pos(i0)
            if pc and pi:
                d = D.dist(pc, pi)
                S['alive'] += 1
                S['dsum'] += d
                S['w3'] += d <= 3
                S['w8'] += d <= 8
            if c0['a'] and i0['a'] and not (r['c'][ca]['a'] and r['c'][ia]['a']):
                S['deaths'] += 1
                band = 'r<300' if r['r'] < 300 else 'r<600' if r['r'] < 600 else 'r<1000'
                S[band] += 1
                cs, is_ = c0['hp'] / max(1, c0['mhp']), i0['hp'] / max(1, i0['mhp'])
                f = ca if cs <= is_ else ia
                S['fell cassi' if f == ca else 'fell issac'] += 1
                S['hp cassi'] += cs
                S['hp issac'] += is_
                if pc and pi:
                    S['d at death'] += D.dist(pc, pi)
                    S['d>8'] += D.dist(pc, pi) > 8
                pf = pos(pr['c'][f])
                if pf:
                    S['en6'] += sum(1 for j in range(n) if pr['c'][j]['t'] != team and pos(pr['c'][j]) and D.dist(pos(pr['c'][j]), pf) <= 6)
                    S['al6'] += sum(1 for j in idx if j != f and j not in (ca, ia) and pos(pr['c'][j]) and D.dist(pos(pr['c'][j]), pf) <= 6)
                S['bags'] += c0.get('g', 0) + i0.get('g', 0)
print(ng, 'games, to round', last)
for w in ('us', 'them'):
    S = T[w]
    t = max(1, S['teams'])
    dn = max(1, S['deaths'])
    print(f"{w}: {S['teams']} pair teams, pair deaths a game {S['deaths'] / t:.2f} (r<300 {S['r<300'] / t:.2f}, r<600 {S['r<600'] / t:.2f}, r<1000 {S['r<1000'] / t:.2f})")
    print(f"   fell first: Cassi {S['fell cassi'] / dn:.2f}, Issac {S['fell issac'] / dn:.2f}; health share the row before: Cassi {S['hp cassi'] / dn:.2f}, Issac {S['hp issac'] / dn:.2f}; bodies apart at death {S['d at death'] / dn:.1f} (over 8: {S['d>8'] / dn:.2f}); enemies within 6 of the fallen {S['en6'] / dn:.2f}, other allies within 6 {S['al6'] / dn:.2f}; both bags {S['bags'] / dn:.1f}")
    al = max(1, S['alive'])
    print(f"   all rounds: mean distance {S['dsum'] / al:.1f}, within 3 {S['w3'] / al:.2f}, within 8 {S['w8'] / al:.2f}")
    print('   other bodies, deaths a game:', {k: round(v['deaths'] / max(1, v['teams']), 2) for k, v in sorted(O[w].items()) if v['teams'] >= 3})
