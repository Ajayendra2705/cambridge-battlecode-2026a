# usage: python -I tools/replay/giftstay.py DIR... (decoded dirs with index.txt)
# Contested deaths of groups we hit most (an enemy champion within 8 of the group at its death, one of ours within 3):
# capture outcome by how many of ours were within 3 at the death and how many stayed on the group (within 1) 4 rounds later.
import gzip, json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
tab = collections.defaultdict(collections.Counter)
for d in sys.argv[1:]:
    for mid, mp, side, res in [l.split() for l in open(os.path.join(d, 'index.txt')) if l.strip()]:
        f = os.path.join(d, mid + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if side == 'a' else 1
        rows = [r for r in (json.loads(l) for l in gzip.open(f, 'rt') if l.strip()) if 'act' in r and r.get('r', 0) <= 1100]
        pos = {}; hits = []
        for r in rows:
            for i, acts in enumerate(r['act']):
                if i >= len(r['c']): continue
                for a in acts:
                    if a[0] == 'attack' and len(a) >= 5 and a[3] == 'm': pos[a[4]] = (a[1], a[2]); hits.append((r['r'], r['c'][i]['t'], a[4]))
        ids = list(pos); par = {i: i for i in ids}
        def fd(i):
            while par[i] != i: par[i] = par[par[i]]; i = par[i]
            return i
        for a in ids:
            for b in ids:
                if a < b and max(abs(pos[a][0]-pos[b][0]), abs(pos[a][1]-pos[b][1])) <= 1: par[fd(a)] = fd(b)
        mem = collections.defaultdict(list)
        for i in ids: mem[fd(i)].append(i)
        dd = lambda c, g: min(max(abs(c['x']-pos[m][0]), abs(c['y']-pos[m][1])) for m in mem[g])
        state = {}; last_end = collections.defaultdict(int)
        for k, r in enumerate(rows):
            mh = r['mh']
            for g in mem:
                alive = any(m < len(mh) and mh[m] > 0 for m in mem[g])
                st = state.get(g)
                if not alive and not isinstance(st, dict):
                    cs = [c for c in r['c'] if c.get('x') is not None]
                    later = rows[k + 4]['c'] if k + 4 < len(rows) else []
                    state[g] = {'dead': r['r'], 'cnt': collections.Counter(),
                                'us3': sum(1 for c in cs if c['t'] == us and dd(c, g) <= 3),
                                'them8': sum(1 for c in cs if c['t'] != us and dd(c, g) <= 8),
                                'stay': sum(1 for c in later if c.get('x') is not None and c['t'] == us and dd(c, g) <= 1),
                                'fate': [('dead' if (j >= len(later) or later[j].get('x') is None) else ('far%d' % min(9, dd(later[j], g))), round(c['hp']/c['mhp'], 1), c.get('g', 0))
                                         for j, c in enumerate(r['c']) if c['t'] == us and c.get('x') is not None and dd(c, g) <= 3]}
                elif not alive:
                    for c in r['c']:
                        if c.get('x') is not None and dd(c, g) <= 1: st['cnt'][c['t']] += 1
                elif isinstance(st, dict):
                    hs = [t for rr, t, cid in hits if fd(cid) == g and last_end[g] <= rr <= st['dead']]
                    last_end[g] = r['r']; state[g] = 'alive'
                    if not hs or sum(1 for t in hs if t == us) < 0.5 * len(hs): continue
                    if st['them8'] == 0 or st['us3'] == 0: continue
                    cap = st['cnt'].most_common(1)[0][0] if st['cnt'] else None
                    out = 'us' if cap == us else 'them' if cap is not None else 'none'
                    tab[('at death', min(st['us3'], 3))][out] += 1
                    tab[('stayed', min(st['stay'], 3))][out] += 1
                    if st['stay'] == 0:
                        for fate, hp, bag in st['fate']:
                            kind = 'dead' if fate == 'dead' else 'near2-3' if fate in ('far2','far3') else 'gone4+'
                            tab[('fate0', kind)][out] += 1
                            tab[('hp0', 'low' if hp < 0.5 else 'high')][out] += 1
                else: state[g] = 'alive'
for k in sorted(tab):
    c = tab[k]; n = sum(c.values())
    print(f"{k[0]:9} {str(k[1]):8}: {n:4d} lives, we capture {c['us']/n:5.1%}, they {c['them']/n:5.1%}")
