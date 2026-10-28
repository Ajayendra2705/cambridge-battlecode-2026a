"""Tribute channels: how they end, per side.

usage: python -I tools/replay/channels.py FIGHTS_DIR...
A tribute start is a 'tribute' act (rounds_extract step kind 12). Duration D = max(1, ceil(0.1 * bag at the round start)).
Outcome, read from the champion over rounds r+1 .. r+D+1: 'died' if it died, 'done' if its bag fell to under a quarter,
'broken' otherwise (a stun or a lock: the bag is still carried). Also per side: gems in bags at the starts, gems in the
bags that died mid-channel, and how many starts had an enemy champion within 4 or within 8 at the round start.
"""
import collections, gzip, json, math, os, sys

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
        C['games'] += 1
        by = {r['r']: r for r in R}
        for r in R:
            for i, acts in enumerate(r.get('act') or []):
                if not any(a[0] == 'tribute' for a in acts): continue
                c = r['c'][i]
                side = 'us' if c['t'] == us else 'them'
                g = c.get('g', 0)
                if g <= 0 or 'x' not in c: continue
                D = max(1, math.ceil(0.1 * g))
                near = [max(abs(e['x'] - c['x']), abs(e['y'] - c['y'])) for e in r['c'] if e['t'] != c['t'] and e.get('a') and 'x' in e]
                dn = min(near) if near else 99
                out = 'broken'
                for k in range(r['r'] + 1, r['r'] + D + 2):
                    q = by.get(k)
                    if not q: break
                    cc = q['c'][i]
                    if not cc.get('a'): out = 'died'; break
                    if cc.get('g', 0) < g / 4: out = 'done'; break
                C[side, 'starts'] += 1
                C[side, 'bag'] += g
                C[side, out] += 1
                C[side, out, 'gems'] += g
                C[side, 'D'] += D
                if dn <= 4: C[side, 'near4'] += 1; C[side, 'near4', out] += 1
                elif dn <= 8: C[side, 'near8'] += 1; C[side, 'near8', out] += 1
n = max(1, C['games'])
print('%d games, per game' % C['games'])
for s in ('us', 'them'):
    st = max(1, C[s, 'starts'])
    print('%-4s starts %.1f (bag %.0f, channel %.1f turns): done %.1f, broken %.1f, died %.2f (gems in those bags %.0f)'
          % (s, C[s, 'starts'] / n, C[s, 'bag'] / st, C[s, 'D'] / st, C[s, 'done'] / n, C[s, 'broken'] / n, C[s, 'died'] / n,
             C[s, 'died', 'gems'] / n))
    for k in ('near4', 'near8'):
        m = C[s, k]
        print('     enemy %s at start: %.2f per game; done %.2f broken %.2f died %.2f' % (
            'within 4' if k == 'near4' else '5-8', m / n, C[s, k, 'done'] / n, C[s, k, 'broken'] / n, C[s, k, 'died'] / n))
