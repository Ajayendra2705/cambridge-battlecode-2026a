"""Team fights: do teammates fight beside one of us who is hit? Reads decoded runs (data/fights/<run>/).
usage: python -I tools/replay/teamfight.py [--upto R] DIR...

Prints per side (us / them), to round R (default 1000):
- rounds per game with one, and with two or more, champions of the side hitting enemy champions, and the share of
  multi-hitter rounds with every hitter on one target;
- after a hit at 40-80% health with the side not outnumbered within 6 (allies and itself against enemies; one event per
  champion per 20 rounds): what the hit champion does over the next 3 rounds ('fight' = hits an enemy champion in 2+,
  'flee' = steps away from the nearest enemy in 2+ and hits in at most 1, else 'other'), P(it dies within 15 rounds),
  P(an enemy champion within 6 of it dies within 15), and its allies within 6: the share of their next five rounds
  hitting an enemy champion, and hitting camps only.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

def pos(c): return (c['x'], c['y']) if c.get('a') and 'x' in c else None
def frac(c): return c.get('hp', 0) / max(1, c.get('mhp', 1))

def main(argv):
    upto = 1000
    if argv[:1] == ['--upto']: upto, argv = int(argv[1]), argv[2:]
    T = {w: collections.Counter() for w in ('us', 'them')}
    ng = 0
    for us, res, mp, meta, rows in D.games(argv):
        ng += 1
        n = len(rows[0]['c'])
        last = {}
        for k in range(1, len(rows) - 1):
            r = rows[k]
            if r['r'] > upto: break
            hitters = {'us': {}, 'them': {}}
            hit_on = collections.defaultdict(list)
            for e in range(n):
                hs = D.enemy_hits(r, e, n)
                if hs: hitters[D.who(r['c'][e]['t'], us)][e] = {x[-1] for x in hs}
                for x in hs: hit_on[x[-1]].append(e)
            for w, h in hitters.items():
                if not h: continue
                T[w]['hit_rounds'] += 1
                if len(h) >= 2:
                    T[w]['multi'] += 1
                    tg = collections.Counter(t for s in h.values() for t in s)
                    T[w]['one_target'] += tg.most_common(1)[0][1] == len(h)
            if k >= len(rows) - 16: continue
            for i in hit_on:
                c = rows[k + 1]['c'][i]; p = pos(c)
                if not p or not (0.4 <= frac(c) < 0.8) or r['r'] - last.get(i, -99) < 20: continue
                team = c['t']
                al = [j for j, o in enumerate(rows[k + 1]['c']) if j != i and pos(o) and o['t'] == team and D.dist(p, pos(o)) <= 6]
                en = [j for j, o in enumerate(rows[k + 1]['c']) if pos(o) and o['t'] != team and D.dist(p, pos(o)) <= 6]
                if len(al) + 1 < len(en) or not en: continue
                last[i] = r['r']
                hits = away = 0
                for kk in range(k + 1, k + 4):
                    if D.enemy_hits(rows[kk], i, n): hits += 1
                    q0, q1 = pos(rows[kk]['c'][i]), pos(rows[kk + 1]['c'][i])
                    ens = [pos(rows[kk]['c'][j]) for j in range(n) if rows[kk]['c'][j]['t'] != team and pos(rows[kk]['c'][j])]
                    if q0 and q1 and ens and min(D.dist(q1, e) for e in ens) > min(D.dist(q0, e) for e in ens): away += 1
                ch = 'fight' if hits >= 2 else 'flee' if away >= 2 and hits <= 1 else 'other'
                C = T[D.who(team, us)]
                C[ch] += 1
                C[ch + 'd'] += any(rows[kk]['c'][i]['a'] and not rows[kk + 1]['c'][i]['a'] for kk in range(k + 1, k + 16))
                C[ch + 'k'] += any(rows[kk]['c'][j]['a'] and not rows[kk + 1]['c'][j]['a'] for kk in range(k + 1, k + 16) for j in en)
                for kk in range(k + 1, k + 6):
                    for j in al:
                        C[ch + 'ar'] += 1
                        if D.enemy_hits(rows[kk], j, n): C[ch + 'ah'] += 1
                        elif D.camp_hits(rows[kk], j): C[ch + 'ac'] += 1
    for w in ('us', 'them'):
        C = T[w]
        print(f"{w:4}: per game rounds hitting champions {C['hit_rounds']/max(1,ng):.1f}, with 2+ hitters {C['multi']/max(1,ng):.1f} "
              f"(all on one target {C['one_target']/max(1,C['multi']):.0%})")
        tot = sum(C[x] for x in ('fight', 'flee', 'other'))
        ar = sum(C[x + 'ar'] for x in ('fight', 'flee', 'other'))
        print(f"      hit at 40-80%, not outnumbered: {tot/max(1,ng):.1f} per game; allies' next five rounds hitting a champion "
              f"{sum(C[x+'ah'] for x in ('fight','flee','other'))/max(1,ar):.3f}, camps only {sum(C[x+'ac'] for x in ('fight','flee','other'))/max(1,ar):.3f}")
        for x in ('fight', 'flee', 'other'):
            m = max(1, C[x]); a = max(1, C[x + 'ar'])
            print(f"      {x:5} {C[x]/max(1,tot):.0%}: P(dies in 15) {C[x+'d']/m:.3f}, P(kill in 15) {C[x+'k']/m:.3f}; "
                  f"allies hitting a champion {C[x+'ah']/a:.3f}, camps only {C[x+'ac']/a:.3f}")
    print(f"games: {ng}")

if __name__ == '__main__':
    main(sys.argv[1:])
