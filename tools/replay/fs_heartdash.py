# Heart of Ruin slot 1 casts (the striking dash: 2 tiles, landing 1.5 x focus in radius 1 + stun 1) with an enemy
# champion within 3 of the landing, to R: per game by side, the landing's enemy champions within 1 (stunned) and within
# 3, allies within 3 of the landing, the Heart's health before, and P(the Heart dies within 10 rounds), P(an enemy
# within 3 of the landing dies within 10). Also Heart slot 0 (shield) casts per game and the share cast with an enemy
# within 3. Split: before r150 and after.
# usage: python -I tools/replay/fs_heartdash.py [--size N] DIR...
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
SIZE = None; args = sys.argv[1:]
if args and args[0] == '--size': SIZE = int(args[1]); args = args[2:]
C = collections.Counter(); ng = 0
HEART = D.NAMES.index('heart')
def p(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
for us, res, mp, meta, rows in D.games(args):
    n = len(rows[0]['c'])
    if SIZE and n != 2 * SIZE: continue
    ng += 1
    for k in range(len(rows) - 11):
        a = rows[k]
        if a['r'] > 1000: break
        for i, c in enumerate(a['c']):
            if c['ty'] != HEART or not p(c): continue
            acts = a['act'][i] if i < len(a['act']) else []
            w = D.who(c['t'], us); ph = 'r<=150' if a['r'] <= 150 else 'r>150'
            for y in acts:
                if y[0] != 'cast': continue
                if y[1] == 0:
                    ens3 = sum(1 for o in a['c'] if p(o) and o['t'] != c['t'] and D.dist(p(c), p(o)) <= 3)
                    C[(w, ph, 'shield')] += 1; C[(w, ph, 'shield3')] += ens3 > 0
                    continue
                if y[1] != 1: continue
                land = (y[2], y[3])
                e1 = [j for j, o in enumerate(a['c']) if p(o) and o['t'] != c['t'] and D.dist(land, p(o)) <= 1]
                e3 = [j for j, o in enumerate(a['c']) if p(o) and o['t'] != c['t'] and D.dist(land, p(o)) <= 3]
                if not e3: C[(w, ph, 'dash_noenemy')] += 1; continue
                al = sum(1 for j, o in enumerate(a['c']) if j != i and p(o) and o['t'] == c['t'] and D.dist(land, p(o)) <= 3)
                hd = any(not rows[t]['c'][i]['a'] for t in range(k + 1, k + 11))
                ed = any(not rows[t]['c'][j]['a'] for j in e3 for t in range(k + 1, k + 11))
                kk = (w, ph)
                C[kk + ('dash',)] += 1; C[kk + ('e1',)] += len(e1); C[kk + ('e3',)] += len(e3); C[kk + ('al',)] += al
                C[kk + ('hp',)] += c.get('hp', 0) / max(1, c.get('mhp', 1)); C[kk + ('hd',)] += hd; C[kk + ('ed',)] += ed
                C[kk + ('e1z',)] += len(e1) == 0
                b = 'e3>al+1' if len(e3) > al + 1 else 'e3<=al+1'
                C[kk + (b,)] += 1; C[kk + (b, 'hd')] += hd; C[kk + (b, 'ed')] += ed
print(f'{ng} games{" of team size " + str(SIZE) if SIZE else ""}, to r1000: Heart of Ruin casts per game')
for ph in ('r<=150', 'r>150'):
    for w in ('us', 'them'):
        kk = (w, ph); d = max(1, C[kk + ('dash',)])
        print(f'  {ph:6} {w:4}: striking dashes near enemies {C[kk + ("dash",)] / ng:.2f}/g (no enemy within 3 of the landing {C[kk + ("dash_noenemy",)] / ng:.2f}); per dash: enemies within 1 {C[kk + ("e1",)] / d:.2f} (none {C[kk + ("e1z",)] / d:.2f}), within 3 {C[kk + ("e3",)] / d:.2f}, allies within 3 {C[kk + ("al",)] / d:.2f}, hp {C[kk + ("hp",)] / d:.2f}; Heart dies in 10 {C[kk + ("hd",)] / d:.2f}, an enemy near dies {C[kk + ("ed",)] / d:.2f}'
              + ''.join(f'; {b} {C[kk + (b,)] / ng:.2f}/g (Heart dies {C[kk + (b, "hd")] / max(1, C[kk + (b,)]):.2f}, enemy dies {C[kk + (b, "ed")] / max(1, C[kk + (b,)]):.2f})' for b in ('e3>al+1', 'e3<=al+1'))
              + f'; shields {C[kk + ("shield",)] / ng:.2f}/g ({C[kk + ("shield3",)] / max(1, C[kk + ("shield",)]):.2f} with an enemy within 3)')
