"""First contact of a game: when a champion first comes within 4 of an enemy, and what follows, by contact round band.

usage: python -I tools/replay/firstcontact.py DIR [DIR ...]

Per band of the first-contact round (to 20, 40, 60, 90, 150, later): games, wins, deaths of each side to r100 and r300,
team gold at r150 and r300, then at the contact: each side's champions within 8 of the contact point, the contact's place
(fraction of the way from our spawn to theirs, Chebyshev), and each side's mean allies within 6 per alive champion in rounds 1
to the contact. Last, a list of the games with contact by r40: map, opponent side's champions, round, numbers, result.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

BANDS = (20, 40, 60, 90, 150, 9999)
C = collections.defaultdict(collections.Counter)
listing = []
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    spawn = {t: [(c['x'], c['y']) for c in rows[0]['c'] if c['t'] == t and 'x' in c] for t in (0, 1)}
    ks = None; pt = None
    for k, a in enumerate(rows):
        al = [c for c in a['c'] if c['a'] and 'x' in c]
        for ci in al:
            if ci['t'] != us: continue
            for cj in al:
                if cj['t'] != us and D.dist((ci['x'], ci['y']), (cj['x'], cj['y'])) <= 4:
                    ks = k; pt = (ci['x'], ci['y']); break
            if ks is not None: break
        if ks is not None: break
    if ks is None: continue
    r0 = rows[ks]['r']
    b = next(x for x in BANDS if r0 <= x)
    c = C[b]; c['g'] += 1; c['w'] += res == 'win'
    for a, bb in zip(rows, rows[1:]):
        if bb['r'] > 300: break
        for i in range(n):
            if a['c'][i]['a'] and not bb['c'][i]['a']:
                w = D.who(a['c'][i]['t'], us)
                c[w + ' d300'] += 1
                if bb['r'] <= 100: c[w + ' d100'] += 1
    for R in (150, 300):
        row = next((r for r in rows if r['r'] >= R), rows[-1])
        for o in row['c']:
            c[D.who(o['t'], us) + f' gold{R}'] += D.gold_held(meta, o)
    a = rows[ks]
    nu = sum(1 for o in a['c'] if o['a'] and 'x' in o and o['t'] == us and D.dist((o['x'], o['y']), pt) <= 8)
    nt = sum(1 for o in a['c'] if o['a'] and 'x' in o and o['t'] != us and D.dist((o['x'], o['y']), pt) <= 8)
    c['nu'] += nu; c['nt'] += nt
    du = min(D.dist(pt, s) for s in spawn[us]); dt = min(D.dist(pt, s) for s in spawn[1 - us])
    c['frac'] += du / max(1, du + dt)
    for r in rows[:ks + 1]:
        al = [o for o in r['c'] if o['a'] and 'x' in o]
        for o in al:
            w = D.who(o['t'], us)
            c[w + ' coh'] += sum(1 for p in al if p is not o and p['t'] == o['t'] and D.dist((o['x'], o['y']), (p['x'], p['y'])) <= 6)
            c[w + ' cohn'] += 1
    if r0 <= 40:
        them = ' '.join(D.NAMES[o['ty']][:3] for o in rows[0]['c'] if o['t'] != us)
        listing.append(f'{mp:26} r{r0:3} us {nu} them {nt} at {du}/{du + dt} {res:5} deaths r300 us vs them | {them}')
print('contact by | games wins | deaths to r100 us/them, to r300 | team gold r150, r300 us/them | at contact within 8 us/them, place | allies within 6 before it us/them')
for b in BANDS:
    c = C[b]; g = max(1, c['g'])
    print(f"r{b:5} | {c['g']:3} {c['w']:3} | {c['us d100'] / g:.2f}/{c['them d100'] / g:.2f} {c['us d300'] / g:.2f}/{c['them d300'] / g:.2f} | "
          f"{c['us gold150'] / g:.0f}/{c['them gold150'] / g:.0f} {c['us gold300'] / g:.0f}/{c['them gold300'] / g:.0f} | {c['nu'] / g:.1f}/{c['nt'] / g:.1f} {c['frac'] / g:.2f} | "
          f"{c['us coh'] / max(1, c['us cohn']):.2f}/{c['them coh'] / max(1, c['them cohn']):.2f}")
print('\n'.join(sorted(listing)))
