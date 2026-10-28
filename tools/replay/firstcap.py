"""First rewards per side, to r150: the round of each side's first reward event (a champion's gems, gold or shards rise
without a kill: a capture, or a tribute), the round of its third, reward events by r100, and team gold earned
(carried gold plus 30 per shard, an emblem 5 shards) at r50 and r100. Rounds without an event count as 151.

usage: python -I tools/replay/firstcap.py DIR...   (decoded runs, `decode_run.sh` or `local_decode.sh`)
"""
import collections, gzip, json, os, statistics, sys
C = collections.defaultdict(list)
for d in sys.argv[1:]:
    for line in open(os.path.join(d, 'index.txt'), encoding='utf-8'):
        p = line.split()
        if len(p) < 3: continue
        f = os.path.join(d, p[0] + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if p[2] == 'a' else 1
        R = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()][1:]
        R = [r for r in R if r.get('c') and r['r'] <= 150]
        if not R: continue
        tm = [c.get('t') for c in R[0]['c']]
        prev = {}
        events = {0: [], 1: []}
        gold = {}
        for r in R:
            for i, c in enumerate(r['c']):
                t = c.get('t')
                if t is None: continue
                tot = c.get('g', 0) + c.get('au', 0) + 30 * sum(cnt * (5 if iid % 2 else 1) for iid, cnt in c.get('it', []))
                if tot > prev.get(i, 0) and c.get('k', 0) == prev.get((i, 'k'), 0):
                    events[t].append(r['r'])
                prev[i] = tot; prev[i, 'k'] = c.get('k', 0)
            if r['r'] in (50, 100):
                for s in (0, 1):
                    gold[s, r['r']] = sum(c.get('au', 0) + 30 * sum(cnt * (5 if iid % 2 else 1) for iid, cnt in c.get('it', [])) for c in r['c'] if c.get('t') == s)
        for s in (0, 1):
            w = 'us' if s == us else 'them'
            ev = sorted(events[s])
            C[w, 'first'].append(ev[0] if ev else 151)
            C[w, 'third'].append(ev[2] if len(ev) > 2 else 151)
            C[w, 'n100'].append(sum(1 for x in ev if x <= 100))
            C[w, 'g50'].append(gold.get((s, 50), 0)); C[w, 'g100'].append(gold.get((s, 100), 0))
for w in ('us', 'them'):
    print('%-4s games %d: first reward r%.0f (median r%.0f), third r%.0f, reward events by r100 %.1f, team gold r50 %.0f r100 %.0f' % (
        w, len(C[w, 'first']), statistics.mean(C[w, 'first']), statistics.median(C[w, 'first']), statistics.median(C[w, 'third']),
        statistics.mean(C[w, 'n100']), statistics.mean(C[w, 'g50']), statistics.mean(C[w, 'g100'])))
