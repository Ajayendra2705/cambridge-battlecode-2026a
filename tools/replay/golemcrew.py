"""Golem crews, to r1000: per round, each side's champions hitting a golem (camp hits in the replay), and per golem life
(first hit to death) who dealt the last hit, its length in rounds, the largest crew and champion-rounds of hitting.
usage: python -I tools/replay/golemcrew.py DIR [DIR ...] [--map SUBSTR]
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
args = sys.argv[1:]; ONLY = None
if '--map' in args:
    k = args.index('--map'); ONLY = args[k + 1]; args = args[:k] + args[k + 2:]
GOLEM = 5
crew = collections.Counter(); lives = collections.defaultdict(list); ng = 0; maps = collections.Counter()
for us, res, mp, meta, rows in D.games(args):
    if ONLY and ONLY not in mp: continue
    ctype = {int(k): v for k, v in (meta.get('camps') or {}).items()}
    gol = {j for j, t in ctype.items() if t == GOLEM}
    if not gol: continue
    ng += 1; maps[mp] += 1
    n = len(rows[0]['c'])
    life = {}
    for a, b in zip(rows, rows[1:]):
        if b['r'] > 1000: break
        hit = collections.defaultdict(lambda: {'us': set(), 'them': set()})
        for i in range(n):
            for x in D.camp_hits(a, i):
                if x[-1] in gol: hit[x[-1]][D.who(a['c'][i]['t'], us)].add(i)
        for j, h in hit.items():
            for w in ('us', 'them'):
                if h[w]: crew[(w, min(len(h[w]), 5))] += 1
            L = life.setdefault(j, {'start': a['r'], 'max': {'us': 0, 'them': 0}, 'cr': {'us': 0, 'them': 0}, 'last': None})
            for w in ('us', 'them'):
                L['max'][w] = max(L['max'][w], len(h[w])); L['cr'][w] += len(h[w])
                if h[w]: L['last'] = w
        for j in list(life):
            if b['mh'][j] == 0 and a['mh'][j] > 0:
                L = life.pop(j)
                lives[L['last']].append((b['r'] - L['start'], L['max'], L['cr'], mp))
print(f'{ng} games with golems: {dict(maps)}')
for w in ('us', 'them'):
    tot = sum(crew[(w, k)] for k in range(1, 6))
    print(f'  {w:4} golem-hit rounds per game {tot / max(1, ng):6.1f}; crew size 1-5 shares: ' + ' '.join(f'{crew[(w, k)] / max(1, tot):.2f}' for k in range(1, 6)))
for k in ('us', 'them'):
    L = lives.get(k) or []
    if not L: print(f'  killed by {k}: none'); continue
    print(f'  killed by {k:4}: {len(L) / ng:4.2f} per game, life {sum(l[0] for l in L) / len(L):5.1f} rounds, max crew {sum(l[1][k] for l in L) / len(L):.2f}, '
          f'hit champion-rounds {sum(l[2][k] for l in L) / len(L):5.1f} (other side {sum(l[2]["them" if k == "us" else "us"] for l in L) / len(L):4.1f})')
