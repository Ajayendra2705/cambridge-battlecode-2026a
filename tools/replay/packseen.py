# Our deaths to r1000 outnumbered by 2+ within 6 (enemies minus allies): was the pack seen earlier? For the 2+ enemies
# within 6 of the victim at its last alive round, in the 30 rounds before: (a) did the victim itself have 2+ of them
# within 8, (b) did a teammate have 2+ of them within 8 while the victim did not, and how far the victim was from that
# teammate then; (c) neither. Also the victim's distance to the pack's centre 15 rounds before. Us vs them.
# usage: python -I tools/replay/packseen.py DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
C = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    ng += 1
    n = len(rows[0]['c'])
    for k in range(31, len(rows)):
        a, b = rows[k - 1], rows[k]
        if b['r'] > 1000: break
        for i in range(n):
            pc, c = a['c'][i], b['c'][i]
            if not pc['a'] or c['a'] or 'x' not in pc: continue
            t = pc['t']; w = D.who(t, us); p = (pc['x'], pc['y'])
            foes = [j for j in range(n) if a['c'][j]['a'] and 'x' in a['c'][j] and a['c'][j]['t'] != t and D.dist((a['c'][j]['x'], a['c'][j]['y']), p) <= 6]
            al = sum(1 for j in range(n) if j != i and a['c'][j]['a'] and 'x' in a['c'][j] and a['c'][j]['t'] == t and D.dist((a['c'][j]['x'], a['c'][j]['y']), p) <= 6)
            if len(foes) - al < 2: continue
            C[(w, 'n')] += 1
            self_seen = mate_seen = None
            for kk in range(k - 30, k - 3):
                r = rows[kk]
                me = r['c'][i]
                def sees(q):
                    return q['a'] and 'x' in q and sum(1 for j in foes if r['c'][j]['a'] and 'x' in r['c'][j] and D.dist((q['x'], q['y']), (r['c'][j]['x'], r['c'][j]['y'])) <= 8) >= 2
                if self_seen is None and sees(me): self_seen = k - kk
                if mate_seen is None and not sees(me):
                    for j in range(n):
                        if j != i and r['c'][j]['t'] == t and sees(r['c'][j]): mate_seen = k - kk; break
            if self_seen is not None: C[(w, 'self')] += 1; C[(w, 'self_lead')] += self_seen
            elif mate_seen is not None: C[(w, 'mate')] += 1; C[(w, 'mate_lead')] += mate_seen
            else: C[(w, 'none')] += 1
print(f'{ng} games to r1000: deaths outnumbered by 2+ within 6, and who saw 2+ of that pack within 8 in the 30 rounds before (3+ rounds before)')
for w in ('us', 'them'):
    nn = max(1, C[(w, 'n')])
    print(f"  {w:4} {C[(w, 'n')] / ng:.2f}/game: victim saw them {C[(w, 'self')] / nn:.2f} (lead {C[(w, 'self_lead')] / max(1, C[(w, 'self')]):.0f} rounds), "
          f"only a teammate saw them first {C[(w, 'mate')] / nn:.2f} (lead {C[(w, 'mate_lead')] / max(1, C[(w, 'mate')]):.0f}), nobody {C[(w, 'none')] / nn:.2f}")
