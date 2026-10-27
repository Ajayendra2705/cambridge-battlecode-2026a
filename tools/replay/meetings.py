# Meetings at camps, to r1000: a champion hits a camp with exactly one enemy champion within 6 (off its spawn), first
# round of each episode (none in the 5 rounds before). Per side of the farmer: episodes per game, health of farmer and
# watcher, an ally of the farmer within 6, and over the next 3 rounds whether the farmer keeps farming, hits the watcher,
# ends farther from it, whether the watcher hits the farmer or camps; who dies within 20 rounds.
# usage: python -I tools/replay/meetings.py DIR...
import gzip, json, os, sys, collections
def ch(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
T = collections.Counter(); G = 0; HP = collections.defaultdict(list)
def kinds(acts):
    k = set()
    for a in acts:
        if a[0] == 'attack' and len(a) > 4: k.add(('m', a[4]) if a[3] == 'm' else ('c', a[4]))
        elif a[0] == 'cast' and len(a) > 5: k.add(('m', a[5]) if a[4] == 'm' else ('c', a[5]))
    return k
for d in sys.argv[1:]:
    for l in open(os.path.join(d, 'index.txt')):
        p = l.split()
        if len(p) < 4: continue
        f = os.path.join(d, p[0] + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if p[2] == 'a' else 1
        rows = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()]
        rows = [r for r in rows[1:] if r.get('c') and r['r'] <= 1000]
        G += 1; n = len(rows[0]['c']); tm = [c['t'] for c in rows[0]['c']]
        spawn = [(c['x'], c['y']) for c in rows[0]['c']]
        death = collections.defaultdict(list)
        for k in range(1, len(rows)):
            for i in range(n):
                if rows[k-1]['c'][i].get('x') is not None and rows[k]['c'][i].get('x') is None: death[i].append(rows[k]['r'])
        last = {}
        def P(k, i):
            c = rows[k]['c'][i]; return (c['x'], c['y']) if c.get('x') is not None else None
        for k, r in enumerate(rows):
            if k + 3 >= len(rows): break
            for i in range(n):
                me = P(k, i)
                if not me: continue
                acts = r['act'][i] if i < len(r['act']) else []
                if not any(x[0] == 'm' for x in kinds(acts)): continue
                en = [j for j in range(n) if tm[j] != tm[i] and P(k, j) and ch(P(k, j), me) <= 6
                      and min(ch(P(k, j), spawn[q]) for q in range(n) if tm[q] == tm[j]) > 3]
                if len(en) != 1: continue
                j = en[0]
                if r['r'] - last.get((i, j), -99) <= 5: last[(i, j)] = r['r']; continue
                last[(i, j)] = r['r']
                w = 'us' if tm[i] == us else 'them'
                T[w, 'n'] += 1
                keep = hitw = away = whit = wcamp = 0
                for kk in range(k + 1, k + 4):
                    fa = kinds(rows[kk]['act'][i] if i < len(rows[kk]['act']) else [])
                    wa = kinds(rows[kk]['act'][j] if j < len(rows[kk]['act']) else [])
                    if any(x[0] == 'm' for x in fa): keep += 1
                    if ('c', j) in fa: hitw += 1
                    if ('c', i) in wa: whit += 1
                    if any(x[0] == 'm' for x in wa): wcamp += 1
                d0 = ch(P(k, j), me); q1, q2 = P(k + 3, i), P(k + 3, j)
                if q1 and q2 and ch(q1, q2) > d0: away = 1
                T[w, 'farmer keeps farming 2+ of 3'] += keep >= 2
                T[w, 'farmer hits watcher'] += hitw > 0
                T[w, 'farmer farther from watcher after 3'] += away
                T[w, 'watcher hits farmer'] += whit > 0
                T[w, 'watcher hits camps'] += wcamp > 0
                T[w, 'farmer dies within 20'] += any(0 < dr - r['r'] <= 20 for dr in death[i])
                T[w, 'watcher dies within 20'] += any(0 < dr - r['r'] <= 20 for dr in death[j])
                c = r['c']
                HP[w, 'farmer'].append(c[i]['hp'] / c[i]['mhp']); HP[w, 'watcher'].append(c[j]['hp'] / c[j]['mhp'])
                a6 = sum(1 for q in range(n) if q != i and tm[q] == tm[i] and P(k, q) and ch(P(k, q), me) <= 6)
                T[w, 'farmer has an ally within 6'] += a6 > 0
print('games', G)
for w in ('us', 'them'):
    N = max(T[w, 'n'], 1)
    print('%s farming episodes with one enemy within 6: %.1f/game, farmer hp %.2f, watcher hp %.2f' % (w, T[w, 'n'] / G,
          sum(HP[w, 'farmer']) / max(len(HP[w, 'farmer']), 1), sum(HP[w, 'watcher']) / max(len(HP[w, 'watcher']), 1)))
    for k in ('farmer has an ally within 6', 'farmer keeps farming 2+ of 3', 'farmer hits watcher', 'farmer farther from watcher after 3',
              'watcher hits farmer', 'watcher hits camps', 'farmer dies within 20', 'watcher dies within 20'):
        print('   %-38s %4.0f%%' % (k, 100 * T[w, k] / N))
