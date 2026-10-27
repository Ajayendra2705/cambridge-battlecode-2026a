# 00ribs opening per game (decoded run dirs with index.txt; only 00ribs games): the round each champion first reaches the
# hill (y >= 58) per side, each side's first death, and each side's champions on the hill at r60, r75, r90 and r120.
# usage: python -I tools/replay/ribsopen.py DIR...
import gzip, json, os, sys
for d in sys.argv[1:]:
    for l in open(os.path.join(d, 'index.txt')):
        p = l.split()
        if len(p) < 4 or 'ribs' not in p[1]: continue
        us = 0 if p[2] == 'a' else 1
        rows = [json.loads(x) for x in gzip.open(os.path.join(d, p[0] + '.jsonl.gz'), 'rt') if x.strip()]
        rows = [r for r in rows[1:] if r.get('c') and r['r'] <= 200]
        n = len(rows[0]['c']); tm = [c['t'] for c in rows[0]['c']]
        arr = {0: [], 1: []}; seen = set(); first_death = {}; on = {}
        alive_prev = [True] * n
        for r in rows:
            for i, c in enumerate(r['c']):
                w = 0 if tm[i] == us else 1
                if c.get('x') is None:
                    if alive_prev[i] and r['r'] > 5: first_death.setdefault(w, r['r'])
                    alive_prev[i] = False; continue
                alive_prev[i] = True
                if c['y'] >= 58 and i not in seen: seen.add(i); arr[w].append(r['r'])
            if r['r'] in (60, 75, 90, 120):
                on[r['r']] = tuple(sum(1 for i, c in enumerate(r['c']) if c.get('x') is not None and c['y'] >= 58 and (0 if tm[i] == us else 1) == w) for w in (0, 1))
        print(p[0][:8], p[3], 'us arrive', sorted(arr[0]), 'them', sorted(arr[1]), 'first death us', first_death.get(0), 'them', first_death.get(1), 'on hill r60/75/90/120 (us,them)', [on.get(k) for k in (60, 75, 90, 120)])
