# Winning bags (wn1): from a champion's first round with a bag that alone lifts its team to 1000 tributed, the rounds
# until its first tribute start (or the game end), and what it did meanwhile (camp hits, champion hits, moves, idle).
# Per side, all games. python -I tools/replay/winbag.py DIR...
import sys, os, collections, statistics
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
A = collections.defaultdict(list); C = collections.defaultdict(collections.Counter); seen = set()
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    key = (mp, meta['rounds'], tuple(meta['submittedGems']))
    if key in seen: continue
    seen.add(key)
    for side in (us, 1 - us):
        w = 'us' if side == us else 'them'
        first = None
        for r in rows:
            for i, c in enumerate(r['c']):
                if c['t'] == side and c.get('a') and c.get('g', 0) > 0 and r['sg'][side] + c['g'] >= 1000 and r['sg'][side] < 1000:
                    first = (r['r'], i); break
            if first: break
        if not first: continue
        r0, i = first
        won = (res == 'win') == (w == 'us')
        n = 0
        for r in rows:
            if r['r'] < r0: continue
            acts = r['act'][i] if i < len(r['act']) else []
            if any(x[0] == 'tribute' for x in acts): C[w]['started'] += 1; break
            if not r['c'][i].get('a'): C[w]['died'] += 1; break
            n += 1
            if any(x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'm' for x in acts): C[w]['camp'] += 1
            elif any(x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' for x in acts): C[w]['champ'] += 1
            elif any(x[0] == 'move' for x in acts): C[w]['move'] += 1
            else: C[w]['idle'] += 1
        else:
            C[w]['ended first'] += 1
        A[w].append(n); C[w]['bags'] += 1; C[w]['lost' if not won else 'won'] += 1
for w in ('us', 'them'):
    v = sorted(A[w])
    print(w, f'winning bags {len(v)}, rounds to first tribute start mean {sum(v)/max(1,len(v)):.1f} median {v[len(v)//2] if v else 0} p90 {v[int(len(v)*0.9)] if v else 0}', dict(C[w]))
