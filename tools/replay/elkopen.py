# Strong-camp damage taken before the first enemy contact, per side, per decoded run dir (index.txt).
# usage: python -I tools/replay/elkopen.py DIR... [--maps a,b] [--skipmaps a,b] [--games]
# Contact is the first round in which a champion hits a champion of the other side (attack or cast). Before it, each
# strong camp (elk, golem, monolith) counts as awake in a round if a champion hit it in that round or the 2 before
# (direct hits only, as tankalone.py) and hits its nearest champion within its reach for its strength (ties between the
# teams skipped). Per side and game: that damage, the number of tank rounds and the champions it went to, champions
# that died or stood under half health at contact, and the hill count (y >= 58, 00ribs only) at contact.
import gzip, json, os, sys, collections
STRONG = {1: 60, 4: 200, 5: 120}  # camp type -> strength
REACH = {1: 4, 4: 5, 5: 4}
args = sys.argv[1:]
maps = skip = None
games = '--games' in args
if games: args.remove('--games')
if '--maps' in args: i = args.index('--maps'); maps = args[i + 1].split(','); del args[i:i + 2]
if '--skipmaps' in args: i = args.index('--skipmaps'); skip = args[i + 1].split(','); del args[i:i + 2]
T = collections.Counter(); G = 0
def ch(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
for d in args:
    for l in open(os.path.join(d, 'index.txt')):
        if not l.strip(): continue
        mid, mp, side = l.split()[:3]
        if maps and not any(m in mp for m in maps): continue
        if skip and any(m in mp for m in skip): continue
        f = os.path.join(d, mid + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if side == 'a' else 1
        rows = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()]
        meta, rows = rows[0], [r for r in rows[1:] if r.get('c')]
        if not rows: continue
        types = {int(k): v for k, v in meta.get('camps', {}).items()}
        n = len(rows[0]['c']); tm = [c['t'] for c in rows[0]['c']]
        G += 1
        cpos, last = {}, {}
        dmg = collections.Counter(); tank = collections.Counter(); tanks = collections.defaultdict(set)
        contact = None; deaths = collections.Counter()
        for k, r in enumerate(rows):
            cs, mh = r['c'], r['mh']
            if k and any(rows[k - 1]['c'][i].get('x') is not None and cs[i].get('x') is None for i in range(n)):
                for i in range(n):
                    if rows[k - 1]['c'][i].get('x') is not None and cs[i].get('x') is None: deaths['us' if tm[i] == us else 'them'] += 1
            alive = {i: (c['x'], c['y']) for i, c in enumerate(cs) if c.get('x') is not None and c.get('hp', 0) > 0}
            hit_champ = False
            for i, acts in enumerate(r.get('act', [])):
                if i >= n: continue
                for a in acts:
                    if a[0] == 'attack' and len(a) >= 5: kind, cid, p = a[3], a[4], (a[1], a[2])
                    elif a[0] == 'cast' and len(a) >= 6: kind, cid, p = a[4], a[5], (a[2], a[3])
                    else: continue
                    if kind == 'm': cpos.setdefault(cid, p); last[cid] = r['r']
                    elif kind == 'c' and cid < n and tm[cid] != tm[i]: hit_champ = True
            if hit_champ:
                contact = r; break
            for cid, t in types.items():
                if t not in STRONG or cid not in cpos or r['r'] - last.get(cid, -99) > 2 or mh[cid] <= 0: continue
                p = cpos[cid]
                ds = {i: ch(q, p) for i, q in alive.items() if ch(q, p) <= REACH[t]}
                if not ds: continue
                m = min(ds.values()); near = sorted(i for i, v in ds.items() if v == m)
                if len({tm[i] for i in near}) != 1: continue
                w = 'us' if tm[near[0]] == us else 'them'
                dmg[w] += STRONG[t]; tank[w] += 1; tanks[w].add(near[0])
        if contact is None: contact = rows[-1]
        cr = contact['r']; T['contact'] += cr
        for w in ('us', 'them'):
            side_i = [i for i in range(n) if (tm[i] == us) == (w == 'us')]
            dead = sum(1 for i in side_i if contact['c'][i].get('x') is None)
            low = sum(1 for i in side_i if contact['c'][i].get('x') is not None and contact['c'][i]['hp'] < 0.5 * contact['c'][i]['mhp'])
            hill = sum(1 for i in side_i if contact['c'][i].get('x') is not None and contact['c'][i]['y'] >= 58) if 'ribs' in mp else 0
            T[w, 'dmg'] += dmg[w]; T[w, 'tank'] += tank[w]; T[w, 'tanks'] += len(tanks[w]); T[w, 'deaths'] += deaths[w]
            T[w, 'dead'] += dead; T[w, 'low'] += low; T[w, 'hill'] += hill
        if games:
            print(mid[:8], mp, 'contact r%d' % cr, ' '.join('%s dmg %d tank %d by %d deaths %d' % (w, dmg[w], tank[w], len(tanks[w]), deaths[w]) for w in ('us', 'them')))
print('games', G, 'first contact at r%.0f on average' % (T['contact'] / max(G, 1)))
for w in ('us', 'them'):
    print(w, 'strong-camp damage before contact %.0f/game, tank rounds %.1f, tanks %.1f, deaths %.2f, dead at contact %.2f, under half health %.2f, on the hill %.2f'
          % tuple(T[w, k] / max(G, 1) for k in ('dmg', 'tank', 'tanks', 'deaths', 'dead', 'low', 'hill')))
