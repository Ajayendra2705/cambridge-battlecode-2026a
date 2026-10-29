# Outnumbered play, us vs them, games with five a side, to r1000 (or --round R): deaths per game by the enemy and allied
# champions within 6 of the victim; then rounds per game with 3+ enemies within 6, by allies within 6, with P(dies
# within 5 rounds); then, for 3+ enemies and at most one ally, the health, nearest enemy distance, attacks, and the
# move's effect on the nearest enemy distance (away / level / closer), idle rounds and health lost by the next round;
# then the same rounds by the nearest enemy's distance: rounds per game, P(dies within 5), and the moves.
# usage: python -I tools/replay/outnumbered.py [--round R] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, dist
args = sys.argv[1:]; RMAX = 1000
if args and args[0] == '--round': RMAX = int(args[1]); args = args[2:]
DE = collections.Counter(); EX = collections.Counter(); A = collections.Counter(); BD = collections.Counter(); G = 0
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    if len(rows[0]['c']) != 10: continue
    G += 1
    for r in range(len(rows) - 1):
        if rows[r]['r'] > RMAX: break
        row, nxt = rows[r], rows[r + 1]
        live = [(k, c) for k, c in enumerate(row['c']) if c['a'] and 'x' in c]
        for k, c in live:
            at = pos(c); w = who(c['t'], us)
            ens = [pos(e) for j, e in live if e['t'] != c['t'] and dist(at, pos(e)) <= 6]
            al = sum(1 for j, e in live if j != k and e['t'] == c['t'] and dist(at, pos(e)) <= 6)
            if not nxt['c'][k]['a']: DE[(w, min(len(ens), 3), min(al, 2))] += 1
            if len(ens) < 3: continue
            EX[(w, min(al, 2))] += 1
            EX[(w, min(al, 2), 'die')] += any(not rows[q]['c'][k]['a'] for q in range(r + 1, min(len(rows), r + 6)))
            if al > 1: continue
            key = (w, al); A[key] += 1
            A[key + ('hp',)] += c['hp'] / c['mhp'] if c.get('mhp') else 1
            dmin = min(dist(at, q) for q in ens); A[key + ('dmin',)] += dmin
            acts = row['act'][k] if k < len(row['act']) else []
            if any(x[0] == 'attack' for x in acts): A[key + ('attack',)] += 1
            if not acts: A[key + ('idle',)] += 1
            mv = [x for x in acts if x[0] == 'move' and len(x) >= 5]
            mk = 'none'
            if mv:
                d2 = min(dist((mv[-1][3], mv[-1][4]), q) for q in ens)
                mk = 'away' if d2 > dmin else 'closer' if d2 < dmin else 'level'
                A[key + (mk,)] += 1
            dk = (w, 'd', min(dmin, 5)); BD[dk] += 1; BD[dk + (mk,)] += 1
            BD[dk + ('die',)] += any(not rows[q]['c'][k]['a'] for q in range(r + 1, min(len(rows), r + 6)))
            if nxt['c'][k]['a']: A[key + ('lost',)] += max(0, c['hp'] - nxt['c'][k]['hp'])
G = max(1, G)
print(f'{G} games with five a side, to r{RMAX}')
print('deaths per game by enemies (en) and allies (al) within 6 of the victim')
for en in range(4):
    print(f'  en{en}{"+" if en == 3 else " "} ' + '   '.join(
        f'al{al}{"+" if al == 2 else " "} us {DE[("us", en, al)] / G:.2f} them {DE[("them", en, al)] / G:.2f}' for al in range(3)))
print('rounds per game with 3+ enemies within 6, by allies within 6: P(dies within 5 rounds)')
for al in range(3):
    print(f'  al{al}{"+" if al == 2 else " "} ' + '   '.join(
        f'{w} {EX[(w, al)] / G:5.1f} r/g P {EX[(w, al, "die")] / max(1, EX[(w, al)]):.3f}' for w in ('us', 'them')))
print('with 3+ enemies within 6 and at most one ally: share of rounds')
for al in (0, 1):
    for w in ('us', 'them'):
        key = (w, al); n = max(1, A[key])
        print(f'  al{al} {w:4} hp {A[key + ("hp",)] / n:.2f} nearest {A[key + ("dmin",)] / n:.2f} attack {A[key + ("attack",)] / n:.2f}'
              f' away {A[key + ("away",)] / n:.2f} level {A[key + ("level",)] / n:.2f} closer {A[key + ("closer",)] / n:.2f}'
              f' idle {A[key + ("idle",)] / n:.2f} health lost {A[key + ("lost",)] / n:.0f}/round')
print('the same rounds by the nearest enemy distance: rounds per game, P(dies within 5), moves away / level / closer / none')
for d in range(1, 6):
    print(f'  d={d}{"+" if d == 5 else " "} ' + '   '.join(
        f'{w} {BD[(w, "d", d)] / G:5.1f} r/g P {BD[(w, "d", d, "die")] / max(1, BD[(w, "d", d)]):.3f} ' + ' '.join(
            f'{m} {BD[(w, "d", d, m)] / max(1, BD[(w, "d", d)]):.2f}' for m in ('away', 'level', 'closer', 'none')) for w in ('us', 'them')))
