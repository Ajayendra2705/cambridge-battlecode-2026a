# Trace fights started on one of our champions of TYPE at 50%+ health that end in its death within 10 rounds:
# per round its position, health, actions, and each champion within 7 (side, type, position, health, actions).
# usage: python -I tools/replay/deftrace.py TYPE MAXN DIR...
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
want, maxn = sys.argv[1], int(sys.argv[2]); shown = 0
for us, res, mp, meta, rows in D.games(sys.argv[3:]):
    n = len(rows[0]['c']); last_hit = {}
    for k, a in enumerate(rows):
        if a['r'] > 1000 or k + 11 >= len(rows): break
        for i in range(n):
            for x in D.enemy_hits(a, i, n):
                j = x[-1]; key = frozenset((i, j)); fresh = k - last_hit.get(key, -99) > 15; last_hit[key] = k
                dc = a['c'][j]
                if not fresh or 'x' not in dc or dc['hp'] < 0.5 * dc['mhp'] or D.who(dc['t'], us) != 'us' or D.NAMES[dc['ty']] != want: continue
                if not any(rows[s]['c'][j]['a'] and not rows[s + 1]['c'][j]['a'] for s in range(k, k + 10)): continue
                shown += 1
                print(f"=== {mp} {meta['file'][:8]} r{a['r']} our {want} #{j} attacked by #{i} ({D.NAMES[a['c'][i]['ty']]})")
                for s in range(max(0, k - 3), k + 11):
                    r = rows[s]; me = r['c'][j]
                    if not me['a']: print(f"  r{r['r']} dead"); break
                    mp_ = (me['x'], me['y'])
                    acts = ' '.join(f"{y[0][:3]}{'>' + str(y[-1]) if y[0] in ('attack', 'cast') and len(y) >= 5 else ''}" for y in (r['act'][j] if j < len(r['act']) else []))
                    near = []
                    for m in range(n):
                        o = r['c'][m]
                        if m == j or not (o['a'] and 'x' in o) or D.dist(mp_, (o['x'], o['y'])) > 7: continue
                        oa = ' '.join(f"{y[0][:3]}{'>' + str(y[-1]) if y[0] in ('attack', 'cast') and len(y) >= 5 else ''}" for y in (r['act'][m] if m < len(r['act']) else []))
                        near.append(f"{'A' if o['t'] == dc['t'] else 'E'}{m}:{D.NAMES[o['ty']][:4]}@{D.dist(mp_, (o['x'], o['y']))} {o['hp']}/{o['mhp']} [{oa}]")
                    print(f"  r{r['r']} {mp_} {me['hp']}/{me['mhp']} g{me.get('g', 0)} [{acts}] | " + '; '.join(near))
                if shown >= maxn: sys.exit()
