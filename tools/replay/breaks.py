"""Broken tribute channels by cause, us vs them: python -I tools/replay/breaks.py DIR...  (run from the repo root)
A channel starts on a 'tribute' action; it should end ceil(g/10) turns later. Broken = the team's tributed total did not
rise by 90% of the bag. Cause: death of the channeler inside the window; else an enemy cast on it in the window (stun);
else 'other' (a new enemy lock, or a cancel). Also the turn of the break (first round the channeler acts again)."""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
A = collections.Counter(); ng = 0; G = collections.Counter()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    for k, b in enumerate(rows):
        for i, acts in enumerate(b['act'][:n]):
            if not any(x[0] == 'tribute' for x in acts): continue
            c = b['c'][i]; g = c.get('g', 0)
            if g <= 0: continue
            turns = max(1, -(-g // 10)); j = min(len(rows) - 1, k + turns + 2)
            if k + turns + 2 >= len(rows) or b['sg'][c['t']] + g >= 1000: continue
            ok = rows[j]['sg'][c['t']] - b['sg'][c['t']] >= g * 0.9
            w = D.who(c['t'], us)
            size = '<=50' if g <= 50 else '51-100' if g <= 100 else '>100'
            A[(w, size, 'n')] += 1
            if ok: continue
            # Find the break: first later round in the window where the channeler is dead or acts.
            cause, at = 'other', None
            for kk in range(k + 1, j + 1):
                r = rows[kk]; me = r['c'][i]
                stunned = any(x[0] == 'cast' and x[-1] == i for e in range(n) for x in D.enemy_hits(rows[kk - 1], e, n))
                if not me['a']: cause, at = 'death', kk - k; break
                if stunned: cause, at = 'cast', kk - k; break
                if r['act'][i] if i < len(r['act']) else []: at = kk - k; break
            A[(w, size, cause)] += 1; G[(w, cause)] += g
            near = 0
            if at is not None:
                r = rows[min(len(rows) - 1, k + at)]; me = r['c'][i]
                if 'x' in me: near = sum(1 for o in r['c'] if o['a'] and 'x' in o and o['t'] != c['t'] and D.dist((me['x'], me['y']), (o['x'], o['y'])) <= 2)
            A[(w, cause, 'enemy within 2 at break', min(near, 2))] += 1
            A[(w, cause, 'turn', 'early' if at is not None and at <= turns / 2 else 'late')] += 1
print(f'{ng} games: channels and breaks per game by bag size, cause of break')
for w in ('us', 'them'):
    for size in ('<=50', '51-100', '>100'):
        nn = A[(w, size, 'n')]
        print(f'  {w:4} {size:6} channels {nn / ng:4.1f}  broken by death {A[(w, size, "death")] / ng:.2f}  by enemy cast {A[(w, size, "cast")] / ng:.2f}  other (lock) {A[(w, size, "other")] / ng:.2f}')
    print(f'  {w:4} gems in broken channels per game: ' + '  '.join(f'{c} {G[(w, c)] / ng:.1f}' for c in ('death', 'cast', 'other')))
    for c in ('death', 'cast', 'other'):
        print(f'    {c:6} enemy within 2 at the break: ' + ' '.join(f'{v}:{A[(w, c, "enemy within 2 at break", v)] / ng:.2f}' for v in (0, 1, 2))
              + f'   early/late: {A[(w, c, "turn", "early")] / ng:.2f}/{A[(w, c, "turn", "late")] / ng:.2f}')
