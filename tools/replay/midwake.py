# Strong-camp wakes (elk, golem, monolith) by who woke them, to r1000 (env UPTO), per decoded run dir (index.txt).
# usage: python -I tools/replay/midwake.py DIR... [--maps a,b] [--skipmaps a,b]
# A wake is the first hit of a camp life by one team. Zone by straight-line distance from both teams' spawns (own: nearer
# us by 7+, mid: within 6, far: nearer them by 7+). Support k = the waker's team within 6 of the camp at the wake.
# Outcome for the waker: kill (its team made the last hit), stolen (the other team did), open (alive at the end or slept
# and respawned). Also: elk-class damage the waker's team took during the life (the camp hits its nearest champion within
# its reach every awake round), the waker team's deaths within 30 rounds of the wake, and second wakes (a mid wake while
# another mid strong camp within 12 tiles, woken by the same team, is still alive and was hit in the last 3 rounds).
import gzip, json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
STRONG = {1: 60, 4: 200, 5: 120}  # camp type -> strength
REACH = {1: 4, 4: 5, 5: 4}
args = sys.argv[1:]
maps = skip = None
if '--maps' in args: i = args.index('--maps'); maps = args[i + 1].split(','); del args[i:i + 2]
if '--skipmaps' in args: i = args.index('--skipmaps'); skip = args[i + 1].split(','); del args[i:i + 2]
UPTO = int(os.environ.get('UPTO', 1000))
T = collections.Counter(); G = 0
def ch(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
for d in args:
    for l in open(os.path.join(d, 'index.txt')):
        if not l.strip(): continue
        mid, mp, side, res = l.split()[:4]
        if maps and not any(m in mp for m in maps): continue
        if skip and any(m in mp for m in skip): continue
        f = os.path.join(d, mid + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if side == 'a' else 1
        rows = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()]
        meta, rows = rows[0], [r for r in rows[1:] if r.get('c') and r.get('r', 0) <= UPTO]
        if not rows: continue
        types = {int(k): v for k, v in meta.get('camps', {}).items()}
        n = len(rows[0]['c']); G += 1
        spawn = [(c['x'], c['y']) for c in rows[0]['c']]; tm = [c['t'] for c in rows[0]['c']]
        deaths = collections.defaultdict(list)
        for k in range(1, len(rows)):
            for i in range(n):
                if rows[k - 1]['c'][i].get('x') is not None and rows[k]['c'][i].get('x') is None: deaths[tm[i]].append(rows[k]['r'])
        pos = {}; life = {}
        def close(cid, outcome):
            L = life.pop(cid); t = L['team']; w = 'us' if t == us else 'them'
            key = (w, L['zone'], min(L['k'], 3))
            T[key] += 1; T[key + (outcome,)] += 1; T[key + ('took',)] += L['took']
            T[key + ('dead30',)] += sum(1 for dr in deaths[t] if 0 <= dr - L['r0'] <= 30)
            if L['second']: T[(w, L['zone'], 'second')] += 1; T[(w, L['zone'], 'second', outcome)] += 1
        for r in rows:
            cs = r['c']; mh = r['mh']
            live = [(c['t'], (c['x'], c['y'])) for c in cs if c.get('x') is not None and c.get('hp', 0) > 0]
            hits = collections.defaultdict(set)
            for i, acts in enumerate(r.get('act', [])):
                if i >= n: continue
                for a in acts:
                    if a[0] == 'attack' and len(a) >= 5 and a[3] == 'm' and types.get(a[4]) in STRONG:
                        pos.setdefault(a[4], (a[1], a[2])); hits[a[4]].add(tm[i])
            for cid, ts in hits.items():
                if cid in life:
                    if len(ts) == 1: life[cid]['last'] = next(iter(ts))
                    life[cid]['hit'] = r['r']
                    continue
                if len(ts) != 1: continue
                t = next(iter(ts)); p = pos[cid]
                k = sum(1 for tt, q in live if tt == t and ch(q, p) <= 6)
                so = min(ch(p, spawn[j]) for j in range(n) if tm[j] == t); st = min(ch(p, spawn[j]) for j in range(n) if tm[j] != t)
                zone = 'own' if so - st < -6 else 'mid' if so - st <= 6 else 'far'
                second = zone == 'mid' and any(L['team'] == t and L['zone'] == 'mid' and r['r'] - L['hit'] <= 3 and ch(pos[o], p) <= 12
                                               for o, L in life.items())
                life[cid] = {'team': t, 'k': k, 'r0': r['r'], 'hit': r['r'], 'last': t, 'zone': zone, 'took': 0, 'second': second}
            for cid in list(life):
                L = life[cid]; p = pos[cid]
                if mh[cid] == 0: close(cid, 'kill' if L['last'] == L['team'] else 'stolen'); continue
                if cid in hits: L['awake'] = True; L['quiet'] = 0
                if not L.get('awake'): continue
                best = None; bd = 99
                for t, q in live:
                    dd = ch(q, p)
                    if dd <= REACH[types[cid]] and dd < bd: bd, best = dd, t
                if best is None:
                    L['quiet'] += 1
                    if L['quiet'] >= 2: L['awake'] = False
                elif best == L['team']: L['took'] += STRONG[types[cid]]
        for cid in list(life): close(cid, 'open')
print(f'games {G} (to r{UPTO})')
for w in ('us', 'them'):
    print(w)
    for z in ('own', 'mid', 'far'):
        for k in (1, 2, 3):
            key = (w, z, k); m = T[key] or 1
            print(f"  {z:3} woken with {k}{'+' if k == 3 else ' '} within 6: {T[key] / max(G, 1):5.2f}/game  kill {T[key + ('kill',)] / m:4.0%}"
                  f" stolen {T[key + ('stolen',)] / m:4.0%} open {T[key + ('open',)] / m:4.0%}  dmg taken {T[key + ('took',)] / m:5.0f}"
                  f"  team deaths within 30 {T[key + ('dead30',)] / m:.2f}")
    s = T[(w, 'mid', 'second')]
    print(f"  mid second wakes {s / max(G, 1):.2f}/game (stolen {T[(w, 'mid', 'second', 'stolen')] / max(s, 1):.0%})")
for w in ('us', 'them'):
    lo = sum(T[(w, 'mid', k)] for k in (1, 2)); al = sum(T[(w, 'mid', k)] for k in (1, 2, 3))
    st = sum(T[(w, 'mid', k, 'stolen')] for k in (1, 2, 3)); dd = sum(T[(w, 'mid', k, 'dead30')] for k in (1, 2, 3))
    print(f"RULE {w}: mid wakes with under 3 within 6 {lo / max(G, 1):.2f}/game, mid wakes {al / max(G, 1):.2f}/game, stolen {st / max(al, 1):.0%},"
          f" team deaths within 30 of a mid wake {dd / max(G, 1):.2f}/game, second wakes {T[(w, 'mid', 'second')] / max(G, 1):.2f}/game")
