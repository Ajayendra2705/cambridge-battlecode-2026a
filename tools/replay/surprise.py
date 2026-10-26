"""Deaths to enemy champions where the dead champion hit no enemy champion in its last K rounds, us vs them, to round R.
usage: python -I tools/replay/surprise.py R DIR... 
Per such death: what it did in those K rounds (camp hits, tribute channel = bag fell to 0 without dying, standing still),
how much damage camps vs champions dealt to it (health lost to hits it took from enemy champions vs the rest), the
enemies within 6 at the death, the round of the first enemy within 6, whether that enemy came from out of sight
(no enemy within 8 one round earlier), and whether the dead champion was in an enemy's basic reach for 2+ rounds."""
import collections, os, sys
sys.path.insert(0, os.path.join(os.getcwd(), 'tools', 'replay'))
import decoded as D
R, K = int(sys.argv[1]), 10
A = collections.Counter(); ng = 0; tot = collections.Counter(); S = collections.defaultdict(list)
def pos(o): return (o['x'], o['y'])
for us, res, mp, meta, rows in D.games(sys.argv[2:]):
    ng += 1
    n = len(rows[0]['c'])
    hitby = collections.defaultdict(lambda: -99)
    for k in range(1, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > R: break
        for i in range(n):
            for x in D.enemy_hits(a, i, n): hitby[x[-1]] = a['r']
        for i in range(n):
            if not (a['c'][i]['a'] and not b['c'][i]['a']) or a['r'] - hitby[i] > 3: continue
            lo = max(0, k - 1 - K)
            if not rows[lo]['c'][i]['a'] or 'x' not in rows[lo]['c'][i]: continue
            me = rows[lo]['c'][i]
            w = D.who(me['t'], us); tot[w] += 1
            if any(D.enemy_hits(rows[kk], i, n) for kk in range(lo, k)): continue
            A[(w, 'n')] += 1
            camp = sum(1 for kk in range(lo, k) if D.camp_hits(rows[kk], i))
            A[(w, 'camp hits', '0' if camp == 0 else '1-4' if camp <= 4 else '5+')] += 1
            # Damage taken from enemy champions vs other (camps), over the window.
            ch_dmg = 0
            for kk in range(lo, k):
                r0 = rows[kk]
                for j in range(n):
                    if r0['c'][j]['t'] == me['t']: continue
                    for x in (r0['act'][j] if j < len(r0['act']) else []):
                        if x[0] in ('attack', 'cast') and len(x) >= 5 and x[-2] == 'c' and x[-1] == i: ch_dmg += 1
            A[(w, 'enemy hits on it', '1-3' if ch_dmg <= 3 else '4-6' if ch_dmg <= 6 else '7+')] += 1
            # Bag dropped to zero inside the window without a death = tribute.
            trib = any(rows[kk]['c'][i].get('g', 0) > 0 and rows[kk + 1]['c'][i].get('g', 0) == 0 and rows[kk + 1]['c'][i]['a'] for kk in range(lo, k - 1))
            A[(w, 'tributed in window', str(trib))] += 1
            still = sum(1 for kk in range(lo + 1, k) if 'x' in rows[kk]['c'][i] and 'x' in rows[kk - 1]['c'][i] and pos(rows[kk]['c'][i]) == pos(rows[kk - 1]['c'][i]))
            A[(w, 'rounds still', '0-2' if still <= 2 else '3-6' if still <= 6 else '7+')] += 1
            # First round an enemy was within 6; was it seen within 8 the round before?
            first = None
            for kk in range(lo, k):
                c = rows[kk]['c'][i]
                if 'x' not in c: continue
                if any(o['a'] and 'x' in o and o['t'] != me['t'] and D.dist(pos(c), pos(o)) <= 6 for o in rows[kk]['c']):
                    first = kk; break
            if first is not None:
                c = rows[max(0, first - 1)]['c'][i]
                seen8 = 'x' in c and any(o['a'] and 'x' in o and o['t'] != me['t'] and D.dist(pos(c), pos(o)) <= 8 for o in rows[max(0, first - 1)]['c'])
                A[(w, 'enemy within 8 the round before it came within 6', str(seen8))] += 1
                A[(w, 'rounds from enemy within 6 to death', '0-3' if k - first <= 3 else '4-6' if k - first <= 6 else '7+')] += 1
            else:
                A[(w, 'rounds from enemy within 6 to death', 'never within 6')] += 1
            dc = rows[k - 1]['c'][i]
            e_at = sum(1 for o in rows[k - 1]['c'] if o['a'] and 'x' in o and 'x' in dc and o['t'] != me['t'] and D.dist(pos(dc), pos(o)) <= 6)
            al_at = sum(1 for j, o in enumerate(rows[k - 1]['c']) if j != i and o['a'] and 'x' in o and 'x' in dc and o['t'] == me['t'] and D.dist(pos(dc), pos(o)) <= 6)
            A[(w, 'at death e/a within 6', f'e{min(e_at, 3)} a{min(al_at, 2)}')] += 1
            A[(w, 'hp 10 before', 'full' if me['hp'] >= 0.9 * me['mhp'] else 'hi' if me['hp'] >= 0.5 * me['mhp'] else 'lo')] += 1
            A[(w, 'type', D.NAMES[me['ty']])] += 1
            A[(w, 'bag', '30+' if me['g'] >= 30 else '1-29' if me['g'] else '0')] += 1
print(f'{ng} games to r{R}: champion-kill deaths per game us {tot["us"] / ng:.2f} them {tot["them"] / ng:.2f}; of them without a hit '
      f'on a champion in the last {K} rounds: us {A[("us", "n")] / ng:.2f} them {A[("them", "n")] / ng:.2f}. Breakdown per game, us/them:')
for cat in sorted({k[1] for k in A if len(k) == 3}):
    keys = sorted({k[2] for k in A if len(k) == 3 and k[1] == cat})
    print(f'  {cat}: ' + '  '.join(f'{v} {A[("us", cat, v)] / ng:.2f}/{A[("them", cat, v)] / ng:.2f}' for v in keys))
