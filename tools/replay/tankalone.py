# Strong camps tanked alone beside busy teammates (tk1's mechanism), to r1000 (env UPTO), per decoded run dir (index.txt).
# usage: python -I tools/replay/tankalone.py DIR... [--maps a,b] [--skipmaps a,b]
# A strong camp (elk, golem, monolith) counts as awake in a round if a champion hit it in that round or the 2 before
# (direct hits only: a camp woken by a hit on another camp of its group is missed). It hits its nearest champion within its
# reach (rounds with a tie between the teams are skipped). Per side and game: tank rounds (that champion is on the side),
# solo (no other champion of the side hit that camp in the round) and split (solo, and another champion of the side
# within 6 of the camp hit a different camp in the round).
import gzip, json, os, sys, collections
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
        mid, mp, side = l.split()[:3]
        if maps and not any(m in mp for m in maps): continue
        if skip and any(m in mp for m in skip): continue
        f = os.path.join(d, mid + '.jsonl.gz')
        if not os.path.exists(f): continue
        us = 0 if side == 'a' else 1
        rows = [json.loads(x) for x in gzip.open(f, 'rt') if x.strip()]
        meta, rows = rows[0], [r for r in rows[1:] if r.get('c') and r.get('r', 0) <= UPTO]
        if not rows: continue
        types = {int(k): v for k, v in meta.get('camps', {}).items()}
        n = len(rows[0]['c']); tm = [c['t'] for c in rows[0]['c']]; G += 1
        cpos, last = {}, {}
        for r in rows:
            cs, mh = r['c'], r['mh']
            alive = {i: (c['x'], c['y']) for i, c in enumerate(cs) if c.get('x') is not None and c.get('hp', 0) > 0}
            hits = collections.defaultdict(set)  # camp -> champions that hit it this round
            for i, acts in enumerate(r.get('act', [])):
                if i >= n: continue
                for a in acts:
                    if a[0] == 'attack' and len(a) >= 5 and a[3] == 'm': cid, p = a[4], (a[1], a[2])
                    elif a[0] == 'cast' and len(a) >= 6 and a[4] == 'm': cid, p = a[5], (a[2], a[3])
                    else: continue
                    cpos.setdefault(cid, p); hits[cid].add(i); last[cid] = r['r']
            for cid, t in types.items():
                if t not in STRONG or cid not in cpos or r['r'] - last.get(cid, -99) > 2 or mh[cid] <= 0: continue
                p = cpos[cid]
                ds = {i: ch(q, p) for i, q in alive.items() if ch(q, p) <= REACH[t]}
                if not ds: continue
                m = min(ds.values()); near = sorted(i for i, v in ds.items() if v == m)
                if len({tm[i] for i in near}) != 1: continue
                tank = near[0]; s = tm[tank]; w = 'us' if s == us else 'them'
                T[w, 'tank'] += 1
                if any(j != tank and tm[j] == s for j in hits[cid]): continue
                T[w, 'solo'] += 1
                if any(j != tank and tm[j] == s and j in alive and ch(alive[j], p) <= 6
                       for c2, hs in hits.items() if c2 != cid for j in hs):
                    T[w, 'split'] += 1
print('games', G)
for w in ('us', 'them'):
    print(w, ' '.join('%s %.1f/game' % (k, T[w, k] / max(G, 1)) for k in ('tank', 'solo', 'split')),
          ' solo share %.0f%%  split share of solo %.0f%%' % (100 * T[w, 'solo'] / max(T[w, 'tank'], 1), 100 * T[w, 'split'] / max(T[w, 'solo'], 1)))
