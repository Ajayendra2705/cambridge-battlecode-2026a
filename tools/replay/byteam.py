"""One decoded run split by opponent: python -I tools/replay/byteam.py RUN@PANEL [ROUND]   (run from the repo root)

Per opponent (from `cambc match-groups show`, cached as paired.py does): games, wins, and per game to ROUND (default
1000) our and their deaths, gems collected, tributed and lost on death; then each game's map, result and final
tribute margin. Sorted by win share, worst first.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paired as P
run = sys.argv[1]
R = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
S = P.stats(run, R)
F = P.stats(run, 2001)  # whole game, for the final margin
by = collections.defaultdict(list)
for k in S: by[k[0]].append(k)
print(f'{run}: {len(S)} decoded games to r{R}, per game us/them')
for opp, ks in sorted(by.items(), key=lambda t: sum(S[k]['win'] for k in t[1]) / len(t[1])):
    n = len(ks)
    cols = '  '.join(f'{f} {sum(S[k]["us " + f] for k in ks) / n:.0f}/{sum(S[k]["them " + f] for k in ks) / n:.0f}'
                     for f in ('deaths', 'coll', 'trib', 'lost'))
    print(f'{opp[:22]:22} {sum(S[k]["win"] for k in ks)}/{n}  {cols}')
    print('    ' + '  '.join(f'{k[1][2:]}{"W" if F[k]["win"] else "L"}{F[k]["us trib"] - F[k]["them trib"]:+d}' for k in sorted(ks, key=lambda k: k[1])))
