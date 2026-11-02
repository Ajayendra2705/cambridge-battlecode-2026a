"""Capture events of one champion type by how many teammates shared them, us vs the rivals, to a round.

usage: python -I tools/replay/soloshare.py TYPE DIR [DIR ...] [--round R]   (TYPE as in decoded.py NAMES, e.g. vesper)

A capture event is a round in which the champion's gold or gems rose with no champion death that round (as in
decoded.py champs); its base gold divides Vesper's +33% out. Sharers are teammates within 2 tiles at that round (the
reward is split among the allies on the region). Per champion-game: events, base gold and gems per event, by sharers
0 / 1 / 2+ and by helpers (teammates that hit a camp within 4 tiles in the 25 rounds before), and the round of the first event and of the first 150 gold of camp gold. Default round 150.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

args = sys.argv[1:]
R = 150
if '--round' in args:
    k = args.index('--round'); R = int(args[k + 1]); del args[k:k + 2]
want, dirs = args[0], args[1:]
C = collections.Counter(); first = collections.defaultdict(list); f150 = collections.defaultdict(list)
for us, res, mp, meta, rows in D.games(dirs):
    n = len(rows[0]['c'])
    mine = [i for i, c in enumerate(rows[0]['c']) if D.NAMES[c['ty']] == want]
    for i in mine:
        w = D.who(rows[0]['c'][i]['t'], us)
        C[(w, 'n')] += 1
        got = None; camp = 0; at150 = None
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            p, c = a['c'][i], b['c'][i]
            if not (p['a'] and c['a']): continue
            died = any(a['c'][j]['a'] and not b['c'][j]['a'] for j in range(n))
            d = D.gold_held(meta, c) - D.gold_held(meta, p)
            dg = c.get('g', 0) - p.get('g', 0)
            if died or not (d > 0 or dg > 0): continue
            base = max(0, d) / (1.33 if want == 'vesper' else 1.0)
            sh = sum(1 for j, o in enumerate(b['c']) if j != i and o['a'] and 'x' in o and o['t'] == c['t']
                     and 'x' in c and D.dist((o['x'], o['y']), (c['x'], c['y'])) <= 2)
            k = '0' if sh == 0 else '1' if sh == 1 else '2+'
            C[(w, 'ev', k)] += 1; C[(w, 'gold', k)] += base; C[(w, 'gems', k)] += max(0, dg)
            # Helpers: teammates that hit a camp within 4 tiles of the capture in the 25 rounds before it.
            if 'x' in c:
                kb = rows.index(b)
                helpers = set()
                for rr in rows[max(0, kb - 25):kb]:
                    for j in range(n):
                        o = rr['c'][j]
                        if j == i or o['t'] != c['t'] or 'x' not in o or not D.camp_hits(rr, j): continue
                        if D.dist((o['x'], o['y']), (c['x'], c['y'])) <= 4: helpers.add(j)
                hk = 'h0' if not helpers else 'h1' if len(helpers) == 1 else 'h2+'
                C[(w, 'ev', hk)] += 1; C[(w, 'gold', hk)] += base
            if got is None: got = b['r']
            camp += max(0, d)
            if at150 is None and camp >= 150: at150 = b['r']
        first[w].append(got if got is not None else R + 1)
        f150[w].append(at150 if at150 is not None else R + 1)

print(f'{want} capture events to r{R}, per champion-game, by teammates within 2 at the event (base gold and gems each)')
for w in ('us', 'them'):
    g = max(1, C[(w, 'n')])
    parts = []
    for k in ('0', '1', '2+'):
        e = C[(w, 'ev', k)]
        parts.append(f'{k}: {e / g:.2f} ({C[(w, "gold", k)] / max(1, e):.0f} gold, {C[(w, "gems", k)] / max(1, e):.1f} gems)')
    parts.append('helpers ' + ' '.join(f'{k[1:]}: {C[(w, "ev", k)] / g:.2f} ({C[(w, "gold", k)] / max(1, C[(w, "ev", k)]):.0f} gold)'
                                      for k in ('h0', 'h1', 'h2+')))
    fs = sorted(first[w]); hs = sorted(f150[w])
    med = fs[len(fs) // 2] if fs else 0; med150 = hs[len(hs) // 2] if hs else 0
    print(f'  {w:4} n={C[(w, "n")]:3}  ' + '  '.join(parts) + f'  | first event r{med} (median), 150 camp gold by r{med150} '
          f'(median; {R + 1} = not by r{R})')
