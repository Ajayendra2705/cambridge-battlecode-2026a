"""Monolith sieges per map, us against them: python -I tools/replay/monohits.py DIR [DIR ...]

For each map with monoliths: games, wins, then us / them per game: hits on monoliths, first hit round (mean over games with a hit), monoliths brought down (the side with more hits on one counts it),
champion-rounds with a hit on a monolith before r1000, deaths within 40 rounds of a hit by that side's own champion, and collected gems to r1000. The whole team on a monolith earns nothing until it falls,
and it deals 200 a round, so the sum shows whether a siege pays on that map.
"""
import collections, sys
sys.path.insert(0, 'tools/replay')
import decoded as D

dirs = sys.argv[1:]
T = collections.defaultdict(collections.Counter)
for us, res, mp, meta, rows in D.games(dirs):
    mono = {int(i) for i, v in meta['camps'].items() if v == 4}
    if not mono:
        continue
    n = len(rows[0]['c'])
    t = T[mp]
    t['n'] += 1
    t['w'] += res == 'win'
    first = {}
    per = collections.defaultdict(collections.Counter)
    last_hit = {}
    prev = None
    wasdead = {m: False for m in mono}
    for x in rows:
        for m in mono:
            dead = m < len(x['mh']) and x['mh'][m] <= 0
            if dead and not wasdead[m]:
                c = per[m]
                if c:
                    t['down_' + c.most_common(1)[0][0]] += 1
                per[m] = collections.Counter()
            wasdead[m] = dead
        for j, acts in enumerate(x['act'][:n]):
            cc = x['c'][j]
            w = D.who(cc['t'], us)
            hit = False
            for a in acts:
                if a[0] == 'attack' and len(a) > 4 and a[3] == 'm' and a[4] in mono:
                    hit = True
                    t['hits_' + w] += 1
                    per[a[4]][w] += 1
                    first.setdefault(w, x['r'])
            if hit:
                last_hit[j] = x['r']
                if x['r'] <= 1000:
                    t['crounds_' + w] += 1
            if prev is not None and prev['c'][j]['a'] and not cc['a'] and x['r'] - last_hit.get(j, -999) <= 40:
                t['dead_' + w] += 1
        prev = x
    for w in ('us', 'them'):
        if w in first:
            t['first_' + w] += first[w]
            t['nf_' + w] += 1
print('map                       n  w | hits us/them | first hit | brought down | champ-rounds on it to r1000 | deaths within 40 of a hit')
for mp, t in sorted(T.items(), key=lambda kv: -kv[1]['hits_us'] / max(1, kv[1]['n'])):
    k = max(1, t['n'])
    print(f"{mp:24s} {t['n']:3d} {t['w']:2d} | {t['hits_us'] / k:5.0f} /{t['hits_them'] / k:5.0f} | {t['first_us'] / max(1, t['nf_us']):5.0f} /{t['first_them'] / max(1, t['nf_them']):5.0f} | {t['down_us'] / k:4.1f} /{t['down_them'] / k:4.1f} | {t['crounds_us'] / k:5.0f} /{t['crounds_them'] / k:5.0f} | {t['dead_us'] / k:4.1f} /{t['dead_them'] / k:4.1f}")
A = collections.Counter()
for t in T.values():
    A.update(t)
k = max(1, A['n'])
print(f"all {A['n']} games {A['w']} wins: hits {A['hits_us'] / k:.0f}/{A['hits_them'] / k:.0f}, brought down {A['down_us'] / k:.2f}/{A['down_them'] / k:.2f}, champ-rounds {A['crounds_us'] / k:.0f}/{A['crounds_them'] / k:.0f}, deaths {A['dead_us'] / k:.2f}/{A['dead_them'] / k:.2f}")
