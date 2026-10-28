"""Who opens fights: engagement starts between champion pairs, per side.

usage: python -I tools/replay/opens.py DIR...   (decoded runs with index.txt; rounds 1-1000)
An engagement starts at the first hit (basic attack or cast) between one of our champions and one of theirs after 15
rounds without a hit between that pair. Per side: engagements opened per game, and in those the share where the
opener's target died within the next 10 rounds and where the opener died; then the share of engagements we opened.
"""
import collections, gzip, json, os, sys

C = collections.Counter()
for d in sys.argv[1:]:
    for line in open(os.path.join(d, 'index.txt'), encoding='utf-8'):
        p = line.split()
        if len(p) < 3: continue
        f = os.path.join(d, p[0] + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if p[2] == 'a' else 1
        R = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()][1:]
        R = [r for r in R if r.get('c') and r['r'] <= 1000]
        if not R: continue
        n = len(R[0]['c'])
        tm = [c['t'] for c in R[0]['c']]
        alive = [[c.get('a', 0) for c in r['c']] for r in R]
        last = {}
        C['games'] += 1
        for k, r in enumerate(R):
            acts = r.get('act') or []
            for i in range(min(n, len(acts))):
                for a in acts[i]:
                    if a[0] == 'attack' and len(a) >= 5 and a[3] == 'c': j = a[4]
                    elif a[0] == 'cast' and len(a) >= 6 and a[4] == 'c': j = a[5]
                    else: continue
                    if j >= n or tm[j] == tm[i]: continue
                    pair = (min(i, j), max(i, j))
                    if r['r'] - last.get(pair, -99) > 15:
                        side = 'us' if tm[i] == us else 'them'
                        later = alive[k + 1:k + 11]
                        C[side, 'opened'] += 1
                        C[side, 'target died'] += any(not q[j] for q in later)
                        C[side, 'opener died'] += any(not q[i] for q in later)
                    last[pair] = r['r']
g = max(1, C['games'])
for s in ('us', 'them'):
    o = C[s, 'opened']
    print('%-4s opened %.1f per game; target died within 10 in %.3f, opener died in %.3f'
          % (s, o / g, C[s, 'target died'] / max(1, o), C[s, 'opener died'] / max(1, o)))
print('%d games, share opened by us %.3f' % (C['games'], C['us', 'opened'] / max(1, C['us', 'opened'] + C['them', 'opened'])))
