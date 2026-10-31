# One guard-map game: every STEP rounds from R0, who stands on the tiles beside the altar, and per champion of ours
# position, altar distance, bag, hp and actions. usage: guardtrace.py FILE R0 R1 STEP
import sys
sys.path.insert(0, r'C:\Users\ajiit\Desktop\Future\Projects\Cambridge Battlecode\tools\replay')
import decoded as D
f, r0, r1, st = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
for us, res, mp, meta, rows in D.games([f]):
    n = len(rows[0]['c']); altar = (25, 20) if 'boss' in mp else (20, 20)
    print(mp, res, 'us team', us)
    for k in range(r0, min(r1, len(rows)), st):
        r = rows[k]
        near = [(D.who(c['t'], us), D.NAMES[c['ty']], c['x'], c['y'], c.get('g', 0)) for c in r['c'] if c['a'] and 'x' in c and D.dist((c['x'], c['y']), altar) <= 1]
        print(f"r{r['r']} sg {r['sg']} at altar: {near}")
        for i in range(n):
            c = r['c'][i]
            if D.who(c['t'], us) != 'us': continue
            if not c['a'] or 'x' not in c: print(f"    {D.NAMES[c['ty']]:9} dead"); continue
            print(f"    {D.NAMES[c['ty']]:9} ({c['x']:2},{c['y']:2}) d{D.dist((c['x'], c['y']), altar):2} g{c.get('g', 0):4} hp{c.get('hp', 0):5} {r['act'][i] if i < len(r['act']) else ''}")
