"""Paired early-gold readout of decoded runs: gold and gem clusters our side killed by r300, our team gold at r300 and
r600, the rivals' gold clusters by r300.

usage: python -I tools/replay/goldpair.py BASE NEW [NEW...]

Each argument is a platform run as in results/gate.log (l1478_b40@b40, decoded into data/fights/<run>_<panel>/, paired
on (opponent, map, repeat) as paired.py does) or a local decoded folder (data/fights/local_<multi run>_<cand>/, paired
on opponent, map and side from the game names). Kills are credited to the side that hit the camp last (as
`decoded.py gold`); team gold is unspent gold plus 30 per shard owned. Prints base means and, per NEW, the paired mean
difference with its standard error. Made for the gold-cluster factor of rows hg3a-hg3c (11-01).
"""
import glob, gzip, json, math, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
KEYS = ['gold clusters r300', 'gem clusters r300', 'team gold r300', 'team gold r600', 'their gold clusters r300']


def per_game(d):
    """game id -> metrics (None where the game ended before the round)"""
    side = {}
    for line in open(os.path.join(d, 'index.txt'), encoding='utf-8', errors='replace'):
        p = line.split()
        if len(p) >= 4: side[p[0]] = 0 if p[2] == 'a' else 1
    out = {}
    for f in sorted(glob.glob(os.path.join(d, '*.jsonl.gz'))):
        mid = os.path.basename(f).split('.')[0]
        if mid not in side: continue
        lines = [json.loads(l) for l in gzip.open(f, 'rt')]
        rows = [r for r in lines[1:] if r.get('c')]
        if not rows: continue
        n = max(len(r['c']) for r in rows)
        rows = [r for r in rows if len(r['c']) == n]
        us, meta = side[mid], lines[0]
        types = {int(k): v for k, v in meta.get('camps', {}).items()}
        m = dict.fromkeys(KEYS, 0.0)
        byr = {r['r']: r for r in rows}
        for R in (300, 600):
            r = byr.get(R)
            m[f'team gold r{R}'] = sum(D.gold_held(meta, c) for c in r['c'] if c['t'] == us) if r else None
        last, prev = {}, None
        for r in rows:
            if r['r'] > 300: break
            for i in range(n):
                for x in D.camp_hits(r, i): last[x[-1]] = D.who(r['c'][i]['t'], us)
            if prev is not None:
                for ci, hp in enumerate(r['mh']):
                    if prev['mh'][ci] > 0 and hp == 0 and ci in last:
                        t = D.CAMPS.get(types.get(ci))
                        if t == 'gold': m['gold clusters r300' if last[ci] == 'us' else 'their gold clusters r300'] += 1
                        elif t == 'gem' and last[ci] == 'us': m['gem clusters r300'] += 1
            prev = r
        out[mid] = m
    return out


def keyed(arg):
    if os.path.isdir(arg):  # local: drop the candidate from the game name
        return {k.split('~', 1)[1]: v for k, v in per_game(arg).items()}
    import paired
    mm = paired.match_map(arg)
    d = os.path.join(ROOT, 'data', 'fights', arg.replace('@', '_'))
    return {tuple(mm[k]): v for k, v in per_game(d).items() if k in mm}


def mean_of(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / max(1, len(vals))


base = keyed(sys.argv[1])
print(f'base {sys.argv[1]}: {len(base)} games; means ' + ', '.join(f'{k} {mean_of(v[k] for v in base.values()):.1f}' for k in KEYS))
for arg in sys.argv[2:]:
    new = keyed(arg)
    common = [k for k in base if k in new]
    print(f'{arg}: {len(common)} paired games')
    for k in KEYS:
        diffs = [new[g][k] - base[g][k] for g in common if new[g][k] is not None and base[g][k] is not None]
        if len(diffs) < 2: continue
        mu = sum(diffs) / len(diffs)
        se = math.sqrt(sum((x - mu) ** 2 for x in diffs) / (len(diffs) - 1) / len(diffs))
        print(f'  {k:26s} {mu:+7.1f} +- {se:5.1f}   (base {mean_of(base[g][k] for g in common):.1f})')
