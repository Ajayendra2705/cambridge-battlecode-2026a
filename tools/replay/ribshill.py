# 00ribs hill deaths (y>=58) to r1000 per side: how the fatal stretch began. Contact = first round after hill entry with
# an enemy champion within 6. Prints what the victim did in the 3 rounds before contact, enemies within 8 and allies within
# 6 at contact, who hit first, rounds contact->death, and whether it gained distance in the next 3 rounds.
# usage: python -I tools/replay/ribshill.py DIR... (decoded runs with index.txt; only 00ribs games are read)
import gzip, json, os, sys, collections
def ch(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
C = collections.defaultdict(collections.Counter); N = collections.Counter(); DT = collections.defaultdict(list)
for d in sys.argv[1:]:
    for l in open(os.path.join(d, 'index.txt')):
        p = l.split()
        if len(p) < 4 or 'ribs' not in p[1]: continue
        us = 0 if p[2] == 'a' else 1
        rows = [json.loads(x) for x in gzip.open(os.path.join(d, p[0] + '.jsonl.gz'), 'rt') if x.strip()]
        rows = [r for r in rows[1:] if r.get('c') and r['r'] <= 1000]
        n = len(rows[0]['c']); tm = [c['t'] for c in rows[0]['c']]
        def pos(k, i):
            c = rows[k]['c'][i]; return (c['x'], c['y']) if c.get('x') is not None else None
        enter = [None] * n
        for k in range(1, len(rows)):
            for i in range(n):
                q, pq = pos(k, i), pos(k - 1, i)
                if q and q[1] >= 58 and (not pq or pq[1] < 58): enter[i] = k
                if pq and not q and pq[1] >= 58 and enter[i] is not None:
                    w = 'us' if tm[i] == us else 'them'; N[w] += 1
                    k0 = enter[i]; kc = None
                    for kk in range(k0, k):
                        me = pos(kk, i)
                        if me and any(tm[j] != tm[i] and pos(kk, j) and ch(pos(kk, j), me) <= 6 for j in range(n)): kc = kk; break
                    if kc is None: C[w]['no contact'] += 1; continue
                    me = pos(kc, i)
                    act = collections.Counter()
                    for kk in range(max(k0, kc - 3), kc):
                        a = rows[kk]['act'][i] if i < len(rows[kk]['act']) else []
                        kinds = {x[0] if x[0] != 'attack' else ('champ' if len(x) > 3 and x[3] == 'c' else 'camp') for x in a}
                        if 'camp' in kinds: act['camp'] += 1
                        elif 'champ' in kinds: act['champ'] += 1
                        elif 'move' in kinds: act['move'] += 1
                        else: act['still'] += 1
                    C[w]['before: ' + (act.most_common(1)[0][0] if act else 'entered')] += 1
                    e8 = sum(1 for j in range(n) if tm[j] != tm[i] and pos(kc, j) and ch(pos(kc, j), me) <= 8)
                    a6 = sum(1 for j in range(n) if j != i and tm[j] == tm[i] and pos(kc, j) and ch(pos(kc, j), me) <= 6)
                    C[w]['enemies8 %d' % min(e8, 4)] += 1; C[w]['allies6 %d' % min(a6, 3)] += 1
                    first = None
                    for kk in range(kc - 2, k):
                        for j in range(n):
                            a = rows[kk]['act'][j] if j < len(rows[kk]['act']) else []
                            for x in a:
                                tgt = x[4] if x[0] == 'attack' and len(x) > 4 and x[3] == 'c' else (x[5] if x[0] == 'cast' and len(x) > 5 and x[4] == 'c' else None)
                                if tgt is None: continue
                                if j == i and tm[tgt] != tm[i]: first = first or 'victim'
                                if tgt == i and tm[j] != tm[i]: first = first or 'enemy'
                        if first: break
                    C[w]['first hit: ' + (first or 'none')] += 1
                    DT[w].append(k - kc)
                    def ne(kk):
                        m = pos(kk, i)
                        if not m: return None
                        ds = [ch(pos(kk, j), m) for j in range(n) if tm[j] != tm[i] and pos(kk, j)]
                        return min(ds) if ds else None
                    d0, d3 = ne(kc), ne(min(kc + 3, k - 1))
                    if d0 is not None and d3 is not None: C[w]['after 3: ' + ('away' if d3 > d0 else 'closer' if d3 < d0 else 'same')] += 1
for w in ('us', 'them'):
    print(w, 'hill deaths', N[w], ' contact->death median', sorted(DT[w])[len(DT[w]) // 2] if DT[w] else None)
    for k, v in sorted(C[w].items()): print('   %-22s %3d  %3.0f%%' % (k, v, 100 * v / max(N[w], 1)))
