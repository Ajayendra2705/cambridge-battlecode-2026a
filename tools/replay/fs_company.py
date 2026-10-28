# Company and fight starts: per champion-round (alive, off both spawns, to R), teammates within 6, by side and team
# size; fight starts on a champion (first hit between the pair after 15 quiet rounds, decoded.py's starts) per 1000 such
# rounds by the victim's teammates within 6 at the round start, and P(the victim dies within 10 rounds).
# usage: python -I tools/replay/fs_company.py [--upto R] [--size N] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R = 1000; SIZE = None; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--upto': R = int(args[1]); args = args[2:]
    elif args[0] == '--size': SIZE = int(args[1]); args = args[2:]
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1; last = {}
    spawn = set((c['x'], c['y']) for c in rows[0]['c'] if 'x' in c)
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > R: break
        ph = 'r1-150' if a['r'] <= 150 else 'r151-400' if a['r'] <= 400 else 'r401+'
        mates = {}
        for i, c in enumerate(a['c']):
            if not c['a'] or 'x' not in c: continue
            q = (c['x'], c['y'])
            m = sum(1 for j, o in enumerate(a['c']) if j != i and o['t'] == c['t'] and o['a'] and 'x' in o and D.dist(q, (o['x'], o['y'])) <= 6)
            mates[i] = min(m, 2)
            if q in spawn: continue
            w = D.who(c['t'], us)
            C[(w, ph, mates[i])] += 1; C[(w, ph)] += 1
        for i in range(n):
            for x in D.enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j))
                fresh = k - last.get(key, -99) > 15
                last[key] = k
                if not fresh or j not in mates: continue
                v = a['c'][j]
                if (v['x'], v['y']) in spawn: continue
                w = D.who(v['t'], us)
                dead = any(not rows[t]['c'][j]['a'] for t in range(k + 1, k + 11))
                C[(w, ph, mates[j], 'start')] += 1; C[(w, ph, mates[j], 'dead')] += dead
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r{R}: champion-rounds off spawn by teammates within 6 (share), fight starts on them per 1000 such rounds, P(victim dies in 10)')
for ph in ('r1-150', 'r151-400', 'r401+'):
    for w in ('us', 'them'):
        tot = C[(w, ph)]
        if not tot: continue
        print(f'  {ph:9} {w:4} ' + '   '.join(f'{m}{"+" if m == 2 else ""} mates {C[(w, ph, m)] / tot:.2f} starts {1000 * C[(w, ph, m, "start")] / max(1, C[(w, ph, m)]):5.1f} dies {C[(w, ph, m, "dead")] / max(1, C[(w, ph, m, "start")]):.2f}' for m in (0, 1, 2))
              + f'   all starts {1000 * sum(C[(w, ph, m, "start")] for m in (0, 1, 2)) / tot:5.1f}/1000')
