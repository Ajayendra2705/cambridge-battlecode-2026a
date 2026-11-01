"""Camp damage per side to r1000: how hard each side's camp hits land, overall and by champion.

usage: python -I tools/replay/campdmg.py [--size N] [--near | --far] DIR...   (decoded folders, each printed apart)

Per game: camp health taken (rounds where one side alone hit that camp), camp-hit champion-rounds, health per
champion-round, hitters per camp-round; then single-hitter rounds that kill nothing (no stacking, no overkill): health
per hit by champion type, with hits and picks per game. --size keeps games of N champions a side; --near / --far keep
maps whose spawn walk (data/map_features.json sd) is under / at least 61, 1478's split between the Bamboo bot and
bot_10. Made for row dv5 (11-02): five a side near, ours 76.6 per champion-round against the rivals' 99.7.
"""
import collections, json, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
args = sys.argv[1:]
size = cls = None
if '--size' in args:
    j = args.index('--size'); size = int(args[j + 1]); args = args[:j] + args[j + 2:]
for c in ('--near', '--far'):
    if c in args: cls = c[2:]; args.remove(c)
F = {r['map'].replace('-', '_'): r for r in json.load(open(os.path.join(ROOT, 'data', 'map_features.json'), encoding='utf-8'))}

for d in args:
    C = collections.Counter(); ng = 0
    for us, res, mp, meta, rows in D.games([d]):
        n = len(rows[0]['c'])
        f = F.get(mp.replace('-', '_'))
        c = 'far' if f and (f['sd'] or 0) >= 61 else 'near'
        if (size and n // 2 != size) or (cls and c != cls): continue
        ng += 1
        for ch in rows[0]['c']: C[(D.who(ch['t'], us), 'pick', D.NAMES[ch['ty']])] += 1
        for a, b in zip(rows, rows[1:]):
            if b['r'] > 1000: break
            hitters = collections.defaultdict(list)
            for i in range(n):
                for x in D.camp_hits(a, i): hitters[x[-1]].append(i)
            for j, hs in hitters.items():
                sides = {D.who(a['c'][i]['t'], us) for i in hs}
                if len(sides) != 1 or j >= len(a['mh']) or j >= len(b['mh']): continue
                w = sides.pop(); dmg = max(0, a['mh'][j] - b['mh'][j])
                C[(w, 'dmg')] += dmg; C[(w, 'hits')] += len(hs); C[(w, 'camprounds')] += 1
                if len(set(hs)) == 1 and b['mh'][j] > 0:
                    ty = D.NAMES[a['c'][hs[0]]['ty']]
                    C[(w, 'single', ty, 'dmg')] += dmg; C[(w, 'single', ty, 'n')] += 1
                    C[(w, 'single dmg')] += dmg; C[(w, 'single n')] += 1
    print(f'{d}: {ng} games' + (f' ({size} a side)' if size else '') + (f' ({cls} maps)' if cls else '') + ', to r1000, us / them')
    if not ng: continue
    print(f"  camp health taken {C[('us', 'dmg')] / ng:7.0f} / {C[('them', 'dmg')] / ng:7.0f}   camp-hit champion-rounds {C[('us', 'hits')] / ng:5.0f} / {C[('them', 'hits')] / ng:5.0f}")
    for w in ('us', 'them'):
        tys = sorted({k[2] for k in C if k[0] == w and k[1] == 'single'}, key=lambda t: -C[(w, 'single', t, 'n')])
        print(f"  {w:4} health per champion-round {C[(w, 'dmg')] / max(1, C[(w, 'hits')]):6.1f}, hitters per camp-round "
              f"{C[(w, 'hits')] / max(1, C[(w, 'camprounds')]):.2f}, single hit {C[(w, 'single dmg')] / max(1, C[(w, 'single n')]):6.1f}: "
              + ', '.join(f"{t} {C[(w, 'single', t, 'dmg')] / C[(w, 'single', t, 'n')]:.0f} ({C[(w, 'single', t, 'n')] / ng:.0f} hits, picks {C[(w, 'pick', t)] / ng:.2f})" for t in tys[:8]))
