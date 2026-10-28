# Ability readiness at fight starts: for every fight start on a champion (first enemy champion hit on it after 15
# quiet rounds), to R, the victim's slot 0 and slot 1 state (ready = no cast of that slot in the 8 rounds before the
# start), by type and side; P(victim dies within 10) by ready / on cooldown. Also: casts per game by type, slot and
# what they hit (enemy champion near: an enemy champion within 4 of the caster; else 'camp/none').
# usage: python -I tools/replay/fs_ready.py [--size N] [--upto R] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
SIZE = None; R = 1000; args = sys.argv[1:]
while args and args[0].startswith('--'):
    if args[0] == '--size': SIZE = int(args[1]); args = args[2:]
    elif args[0] == '--upto': R = int(args[1]); args = args[2:]
C = collections.Counter(); CA = collections.Counter(); ng = 0; GT = collections.Counter()
def p(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1
    for c in rows[0]['c']: GT[(D.who(c['t'], us), D.NAMES[c['ty']])] += 1
    lastcast = {}  # (i, slot) -> row index
    last = {}
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > R: break
        for i in range(n):
            for x in D.enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j))
                fresh = k - last.get(key, -99) > 15
                last[key] = k
                if not fresh: continue
                v = a['c'][j]
                if not p(v): continue
                w = D.who(v['t'], us); ty = D.NAMES[v['ty']]
                died = any(not rows[t]['c'][j]['a'] for t in range(k + 1, k + 11))
                for s in (0, 1):
                    rd = k - lastcast.get((j, s), -99) >= 8
                    st = 'ready' if rd else 'cd'
                    C[(w, ty, s, st)] += 1; C[(w, ty, s, st, 'd')] += died
        for i, c in enumerate(a['c']):
            acts = a['act'][i] if i < len(a['act']) else []
            for y in acts:
                if y[0] == 'cast':
                    lastcast[(i, y[1])] = k
                    if p(c):
                        near = any(p(o) and o['t'] != c['t'] and D.dist(p(c), p(o)) <= 4 for o in a['c'])
                        CA[(D.who(c['t'], us), D.NAMES[c['ty']], y[1], 'champ near' if near else 'none near')] += 1
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r{R}: at fight starts on a champion, its slots ready (no cast in the 8 rounds before)')
for ty in sorted(set(k[1] for k in C)):
    for s in (0, 1):
        line = []
        for w in ('us', 'them'):
            r_, cd = C[(w, ty, s, 'ready')], C[(w, ty, s, 'cd')]
            if r_ + cd < 20: line.append(f'{w:4}  -'); continue
            line.append(f'{w:4} starts {(r_ + cd) / max(1, GT[(w, ty)]):5.2f}/game-with-type ready {r_ / (r_ + cd):.2f} (dies {C[(w, ty, s, "ready", "d")] / max(1, r_):.2f} vs on cd {C[(w, ty, s, "cd", "d")] / max(1, cd):.2f})')
        print(f'  {ty:9} slot {s}: ' + '   '.join(line))
print('casts per game-with-type, by slot: with an enemy champion within 4 / without')
for ty in sorted(set(k[1] for k in CA)):
    line = []
    for w in ('us', 'them'):
        g = GT[(w, ty)]
        if g < 10: continue
        line.append(f'{w}: ' + ', '.join(f's{s} {CA[(w, ty, s, "champ near")] / g:.1f}/{CA[(w, ty, s, "none near")] / g:.1f}' for s in (0, 1)))
    if line: print(f'  {ty:9} ' + '   '.join(line))
