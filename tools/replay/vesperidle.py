# Our and their Vesper's rounds with no action (no move, attack or cast) while the nearest enemy champion (off its spawn) is
# 1-3 tiles away, to r1000: share with a stun cause in that round or the one before (an enemy Heart of Ruin's dash
# landing within 1 of her, an enemy Ryth's area cast centred within 1, a Marcella basic attack on her after her slot-0
# cast within the 3 rounds before, an enemy Ren / Prism / Cassi stun cast on her), and the rest by her gem bag, health and
# whether she stands on the tile she held the round before.
# usage: python -I tools/replay/vesperidle.py DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
from decoded import games, who, NAMES, dist
args = sys.argv[1:]
V = NAMES.index('vesper')
N = {w: collections.Counter() for w in ('us', 'them')}; G = collections.Counter()
def pos(c): return (c['x'], c['y'])
def tname(rows, r, k): return NAMES[rows[r]['c'][k]['ty']]
for us, res, mp, meta, rows in games(args):
    n = len(rows[0]['c'])
    spawn = {t: set(pos(c) for c in rows[0]['c'] if c['t'] == t and 'x' in c) for t in (0, 1)}
    for i, c0 in enumerate(rows[0]['c']):
        if c0['ty'] != V: continue
        w = who(c0['t'], us); G[w] += 1
        for r in range(2, len(rows) - 1):
            if rows[r]['r'] > 1000: break
            me = rows[r]['c'][i]
            if not me['a'] or 'x' not in me: continue
            p = pos(me)
            ens = [e for e in rows[r]['c'] if e['a'] and 'x' in e and e['t'] != me['t'] and pos(e) not in spawn[e['t']]]
            if not ens or min(dist(p, pos(e)) for e in ens) > 3: continue
            acts = rows[r]['act'][i] if i < len(rows[r]['act']) else []
            if acts: continue
            nx = rows[r + 1]['c'][i]
            if nx['a'] and 'x' in nx and pos(nx) != p: continue
            stun = None
            for rr in (r - 1, r):
                for k in range(n):
                    if rows[rr]['c'][k]['t'] == me['t'] or k >= len(rows[rr]['act']): continue
                    tn = tname(rows, rr, k)
                    for x in rows[rr]['act'][k]:
                        if x[0] != 'cast' and x[0] != 'attack': continue
                        if tn == 'heart' and x[0] == 'cast' and x[1] == 1 and len(x) >= 4 and dist((x[2], x[3]), pos(rows[rr]['c'][i]) if 'x' in rows[rr]['c'][i] else p) <= 1: stun = 'heart dash'
                        if tn == 'ryth' and x[0] == 'cast' and x[1] == 0 and len(x) >= 4 and dist((x[2], x[3]), p) <= 1: stun = 'ryth area'
                        if tn in ('ren', 'prism', 'cassi') and x[0] == 'cast' and len(x) >= 6 and x[-2] == 'c' and x[-1] == i: stun = tn + ' cast'
                        if tn == 'marcella' and x[0] == 'attack' and len(x) >= 5 and x[-2] == 'c' and x[-1] == i:
                            if any(y[0] == 'cast' and y[1] == 0 for q in range(max(0, rr - 3), rr + 1) if k < len(rows[q]['act']) for y in rows[q]['act'][k]): stun = 'marcella stun hit'
            key = stun or ('no stun seen: ' + ('bag 30+' if me.get('g', 0) >= 30 else 'hp<50' if me['hp'] < 0.5 * me['mhp'] else 'other'))
            N[w]['all'] += 1; N[w][key] += 1
print(f"no-action rounds with an enemy within 3 (to r1000), per game; games us {G['us']} them {G['them']}")
for k in sorted(set(N['us']) | set(N['them'])):
    print(f"  {k:28} " + '   '.join(f"{w} {N[w][k] / max(1, G[w]):5.2f} ({N[w][k] / max(1, N[w]['all']):.2f})" for w in ('us', 'them')))
