# usage: python -I tools/replay/waste.py ROUND DIR...
# Camp hits by outcome, us vs them, to round R: each camp hit is credited to the group's next capture (by own side,
# by the other side, or none before R/respawn). Also damage dealt to camps per hit, and gems captured per 1000 camp damage.
import sys, collections
sys.path.insert(0, 'tools/replay')
import decoded as D
R = int(sys.argv[1]); dirs = sys.argv[2:]
H = collections.Counter(); ng = 0
for us, res, mp, meta, rows in D.games(dirs):
    ng += 1
    n = len(rows[0]['c'])
    grp, members, gtiles = D.camp_groups(rows, n)
    open_hits = collections.defaultdict(lambda: collections.Counter())  # group -> side -> hits since last capture
    open_dmg = collections.defaultdict(lambda: collections.Counter())
    pending = set()
    for a, b in zip(rows, rows[1:]):
        if b['r'] > R: break
        hit_by = collections.defaultdict(set)
        for i in range(n):
            for x in D.camp_hits(a, i):
                j = x[-1]
                if j in grp:
                    w = D.who(a['c'][i]['t'], us); open_hits[grp[j]][w] += 1; hit_by[j].add(w)
        for j, (h0, h1) in enumerate(zip(a['mh'], b['mh'])):
            if j in grp and h1 < h0 and len(hit_by.get(j, ())) == 1: open_dmg[grp[j]][next(iter(hit_by[j]))] += h0 - h1
        for g, js in members.items():
            if g not in pending and any(a['mh'][j] > 0 for j in js) and all(b['mh'][j] == 0 for j in js): pending.add(g)
        for i, c in enumerate(b['c']):
            pc = a['c'][i]
            if not (c['a'] and pc['a'] and 'x' in c) or (c.get('g', 0) <= pc.get('g', 0) and c.get('au', 0) <= pc.get('au', 0)) or c.get('k', 0) > pc.get('k', 0): continue
            p = (c['x'], c['y'])
            g = next((g for g in pending if p in gtiles[g]), None)
            if g is None: continue
            pending.discard(g)
            w = D.who(c['t'], us)
            for side in ('us', 'them'):
                k = 'own' if side == w else 'lost'
                H[(side, k)] += open_hits[g][side]; H[(side, 'dmg_' + k)] += open_dmg[g][side]
            H[(w, 'gems')] += c['g'] - pc['g']; H[(w, 'gold')] += c.get('au', 0) - pc.get('au', 0)
            open_hits.pop(g, None); open_dmg.pop(g, None)
    for g, c in open_hits.items():
        for side in ('us', 'them'): H[(side, 'none')] += c[side]; H[(side, 'dmg_none')] += open_dmg[g][side]
for s in ('us', 'them'):
    tot = H[(s, 'own')] + H[(s, 'lost')] + H[(s, 'none')]
    dmg = H[(s, 'dmg_own')] + H[(s, 'dmg_lost')] + H[(s, 'dmg_none')]
    print(f"{s:4} camp hits {tot / ng:6.1f}/game: to own capture {H[(s, 'own')] / tot:.2f}, to the other side's {H[(s, 'lost')] / tot:.2f}, uncaptured {H[(s, 'none')] / tot:.2f}; "
          f"damage {dmg / ng:7.0f}/game ({dmg / max(1, tot):.0f}/hit, solo-credited); captured {H[(s, 'gems')] / ng:.0f} gems {H[(s, 'gold')] / ng:.0f} gold; gems per 1000 own-capture damage {1000 * H[(s, 'gems')] / max(1, H[(s, 'dmg_own')]):.1f}")
