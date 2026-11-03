"""Opening of each champion on one map: python -I mapscript.py MAP RMAX N DIR...  Reward events and deaths, camp hits compressed to the first of each camp id, positions every 20 rounds."""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D
MP, RMAX, N, dirs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4:]
seen = 0
for us, res, mp, meta, rows in D.games(dirs):
    if mp != MP:
        continue
    seen += 1
    if seen > N:
        break
    print('==', mp, 'we', res, 'camps', meta.get('camps') and len(meta['camps']))
    for t in (0, 1):
        print(' ', D.who(t, us))
        for i, c0 in enumerate(rows[0]['c']):
            if c0['t'] != t:
                continue
            ev = []
            campseen = set()
            for a, b in zip(rows, rows[1:]):
                if b['r'] > RMAX:
                    break
                p, c = a['c'][i], b['c'][i]
                for x in D.camp_hits(b, i):
                    if x[-1] not in campseen:
                        campseen.add(x[-1])
                        ev.append(f"r{b['r']}:h{x[-3]},{x[-4] if False else ''}" if False else f"r{b['r']}:hit@{x[-4]},{x[-3]}")
                for x in (b['act'][i] if i < len(b['act']) else []):
                    if x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' and x[-1] < len(b['c']) and b['c'][x[-1]]['t'] != c0['t']:
                        if not ev or not ev[-1].startswith('PVP') or int(ev[-1].split('r')[1]) < b['r'] - 5:
                            ev.append(f"PVPr{b['r']}")
                if p['a'] and c['a']:
                    d = D.gold_held(meta, c) - D.gold_held(meta, p); dg = c.get('g', 0) - p.get('g', 0)
                    if d > 0 or dg > 0:
                        ev.append(f"r{b['r']}:+{d}g{dg}e")
                if p['a'] and not c['a']:
                    ev.append(f"r{b['r']}:DIED")
                if b['r'] % 25 == 0 and 'x' in c:
                    ev.append(f"[{b['r']}@{c['x']},{c['y']}]")
            print('   ', D.NAMES[c0['ty']][:5], (c0.get('x'), c0.get('y')), ' '.join(ev))
