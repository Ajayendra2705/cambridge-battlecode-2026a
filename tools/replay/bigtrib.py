# Rival score jumps: per game, the largest single rise of the rivals' tributed score between rows, and the round;
# games where it is 300+ listed with result. python -I bigtrib.py DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
big = collections.Counter(); n = 0
for d in sys.argv[1:]:
    for us, res, mp, meta, rows in D.games([d]):
        n += 1
        best = (0, 0); prev = rows[0]['sg'][1 - us]
        for r in rows:
            j = r['sg'][1 - us] - prev; prev = r['sg'][1 - us]
            if j > best[0]: best = (j, r['r'])
        # Final channel past the decoded rows: rivals' max bag at the end plus their score.
        endbag = max([c.get('g', 0) for c in rows[-1]['c'] if c['a'] and D.who(c['t'], us) == 'them'] + [0])
        if best[0] >= 300 or endbag >= 300:
            big[res] += 1
            print(d.split('/')[-1][4:8], mp, res, 'end', rows[-1]['r'], 'max jump', best, 'their final', rows[-1]['sg'][1 - us], 'their max bag at end', endbag)
print(n, 'games', dict(big))
