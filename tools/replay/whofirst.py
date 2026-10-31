# Whole-game result changes that our change caused. Platform games are deterministic, so for each paired game of two
# runs (paired as in paired.py, both decoded) the first round where any unit differs (position, alive, bag) shows
# which side played differently first: "us" (our change acted while the opponent was identical), "them" (the
# opponent uploaded a new bot or acted differently first) or "both" in that round. Prints per class the games that
# went win to loss and loss to win, then each changed result with its map and divergence round.
# usage: python -I tools/replay/whofirst.py BASE NEW [BASE NEW ...]   (runs as in results/gate.log)
import sys, gzip, json, os, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, 'tools/replay'); import paired as P
def idx(run):
    d = os.path.join('data', 'fights', run.replace('@', '_'))
    rows = {l.split()[0]: l.split() for l in open(os.path.join(d, 'index.txt')) if len(l.split()) >= 4}
    return d, rows, {tuple(v): k for k, v in P.match_map(run).items()}
def load(d, mid):
    L = [json.loads(l) for l in gzip.open(os.path.join(d, mid + '.jsonl.gz'), 'rt')]
    return {r['r']: r['c'] for r in L[1:] if r.get('c')}
def key(c): return (c.get('x'), c.get('y'), c['a'], c.get('g', 0))
tally = collections.defaultdict(collections.Counter); flips = []
for b, n in zip(sys.argv[1::2], sys.argv[2::2]):
    db, ib, kb = idx(b); dn, inn, kn = idx(n)
    for k in kb:
        if k not in kn or kb[k] not in ib or kn[k] not in inn: continue
        rb, rn = ib[kb[k]], inn[kn[k]]
        A, B = load(db, kb[k]), load(dn, kn[k]); us = 0 if rb[2] == 'a' else 1
        cls, split = 'same', None
        for r in sorted(set(A) & set(B)):
            ca, cb = A[r], B[r]
            if len(ca) != len(cb): cls, split = 'both', r; break
            sides = {c['t'] for c, e in zip(ca, cb) if key(c) != key(e)}
            if sides: cls, split = ('us' if sides == {us} else 'them' if sides == {1 - us} else 'both'), r; break
        wb, wn = rb[3] == 'win', rn[3] == 'win'
        fl = 'W->L' if wb and not wn else 'L->W' if wn and not wb else '='
        tally[cls][fl] += 1
        if fl != '=': flips.append((n.split('@')[1], k[0][:16], k[1], cls, split, fl))
for c in ('same', 'us', 'them', 'both'):
    t = tally[c]; print(f'{c:5s} games {sum(t.values()):3d}  W->L {t["W->L"]:2d}  L->W {t["L->W"]:2d}  same result {t["="]:3d}')
for f in flips: print('  ', *f)
