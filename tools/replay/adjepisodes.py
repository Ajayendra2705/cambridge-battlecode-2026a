# Adjacency episodes of one type (default vesper), to r1000, by side: a run of round starts with an enemy champion (off its
# spawn) within 1. Length, how it ended (she died, the adjacent enemies all died, she got 3+ away from every enemy that was
# adjacent, else separated to 2), per game; and over the episode's rounds: her hits on champions, enemy champion hits on
# her, her damage taken share (health share lost), allies within 3 at the start.
# usage: python -I tools/replay/adjepisodes.py [--type NAME] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist, enemy_hits
TY = 'vesper'; args = sys.argv[1:]
if args and args[0] == '--type': TY = args[1]; args = args[2:]
T = NAMES.index(TY)
S = {w: collections.Counter() for w in ('us', 'them')}; G = collections.Counter()
def pos(c): return (c['x'], c['y'])
for us, res, mp, meta, rows in games(args):
    n = len(rows[0]['c'])
    spawn = {t: set(pos(c) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    for i, c0 in enumerate(rows[0]['c']):
        if c0['ty'] != T: continue
        w = who(c0['t'], us); G[w] += 1; C = S[w]
        def adj(r):
            me = rows[r]['c'][i]
            if not me['a'] or 'x' not in me: return []
            return [k for k, e in enumerate(rows[r]['c']) if e['a'] and 'x' in e and e['t'] != me['t'] and dist(pos(me), pos(e)) <= 1 and pos(e) not in spawn[e['t']]]
        r = 0
        while r < len(rows) and rows[r]['r'] <= 1000:
            a = adj(r)
            if not a: r += 1; continue
            start = r; foes = set(a); hits_mine = hits_theirs = 0
            hp0 = rows[r]['c'][i]['hp'] / max(1, rows[r]['c'][i]['mhp'])
            al = sum(1 for j, e in enumerate(rows[r]['c']) if j != i and e['a'] and 'x' in e and e['t'] == rows[r]['c'][i]['t'] and dist(pos(rows[r]['c'][i]), pos(e)) <= 3)
            while r < len(rows) and adj(r):
                foes |= set(adj(r))
                hits_mine += bool(enemy_hits(rows[r], i, n))
                hits_theirs += sum(1 for k in range(n) if rows[r]['c'][k]['t'] != rows[r]['c'][i]['t']
                                   for x in (rows[r]['act'][k] if k < len(rows[r]['act']) else []) if x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' and x[-1] == i)
                r += 1
            L = r - start
            if r >= len(rows): end = 'game end'
            else:
                me = rows[r]['c'][i]
                if not me['a']: end = 'she died'
                elif all(not rows[r]['c'][k]['a'] for k in foes): end = 'adjacent foes died'
                elif all(not rows[r]['c'][k]['a'] or ('x' in rows[r]['c'][k] and dist(pos(me), pos(rows[r]['c'][k])) >= 3) for k in foes): end = 'got 3+ away'
                else: end = 'separated to 2'
            C['episodes'] += 1; C['rounds'] += L; C['end: ' + end] += 1
            C['len ' + ('1' if L == 1 else '2-3' if L <= 3 else '4+')] += 1
            C['her hits'] += hits_mine; C['hits on her'] += hits_theirs
            C['start hp full' if hp0 >= 0.95 else 'start hp 50-95' if hp0 >= 0.5 else 'start hp <50'] += 1
            C[f'allies within 3 at start: {min(al, 2)}'] += 1
print(f'{TY}: adjacency episodes to r1000, per game; games us {G["us"]} them {G["them"]}')
for k in sorted(set(S['us']) | set(S['them'])):
    cells = [f"{w} {S[w][k] / max(1, G[w]):6.2f}" for w in ('us', 'them')]
    print(f'  {k:32} ' + '   '.join(cells))
for w in ('us', 'them'):
    C = S[w]; e = max(1, C['episodes'])
    print(f"  {w}: rounds per episode {C['rounds'] / e:.2f}, her hits per episode {C['her hits'] / e:.2f}, hits on her per episode {C['hits on her'] / e:.2f}, P(she died) {C['end: she died'] / e:.3f}")
