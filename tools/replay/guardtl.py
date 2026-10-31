# Guard maps: per game the altar, guard camps (within 1 of the altar), their first hit and death round, hits by side,
# our/their bags at checkpoints, first tribute rounds, and our champions near the altar after the guard died.
import sys, collections
sys.path.insert(0, r'C:\Users\ajiit\Desktop\Future\Projects\Cambridge Battlecode\tools\replay')
import decoded as D
for us, res, mp, meta, rows in D.games(sys.argv[1:]):
    n = len(rows[0]['c'])
    altar = None; trib = collections.defaultdict(list)
    pos = {}
    for r in rows:
        for i in range(min(n, len(r.get('act', [])))):
            for x in r['act'][i]:
                if x[0] == 'tribute':
                    altar = altar or (x[1], x[2]); trib[D.who(r['c'][i]['t'], us)].append(r['r'])
            for x in D.camp_hits(r, i): pos[x[-1]] = (x[-4], x[-3])
    if altar is None:
        altar = (25, 20) if 'boss' in mp else (20, 20)
    guards = [j for j, p in pos.items() if max(abs(p[0] - altar[0]), abs(p[1] - altar[1])) <= 1]
    info = []
    for j in guards:
        hits = collections.Counter(); first = None; death = None
        for a, b in zip(rows, rows[1:]):
            for i in range(n):
                for x in D.camp_hits(a, i):
                    if x[-1] == j:
                        hits[D.who(a['c'][i]['t'], us)] += 1; first = first or a['r']
            if death is None and a['mh'][j] > 0 and b['mh'][j] == 0: death = b['r']
        info.append(f"guard{j}@{pos[j]} first {first} dead {death} hits us {hits['us']} them {hits['them']}")
    def bags(r):
        z = collections.Counter()
        for c in r['c']:
            if c['a']: z[D.who(c['t'], us)] += c.get('g', 0)
        return z
    cps = []
    for R in (300, 600, 900, 1200):
        if R < len(rows): b = bags(rows[R - 1]); cps.append(f"r{R} {b['us']}/{b['them']}")
    first_us = trib['us'][0] if trib['us'] else None; first_th = trib['them'][0] if trib['them'] else None
    print(f"{mp:14} {res:4} r{len(rows):5} altar {altar} | " + '; '.join(info))
    print(f"   bags us/them {' '.join(cps)} | tribute starts us {len(trib['us'])} first {first_us}, them {len(trib['them'])} first {first_th} | final sg {rows[-1]['sg']} us={us}")
