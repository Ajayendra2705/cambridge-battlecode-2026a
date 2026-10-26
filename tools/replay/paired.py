"""Pair the decoded games of two platform runs on (opponent, map, repeat) and compare them game by game.

usage: python -I tools/replay/paired.py BASE_RUN NEW_RUN [ROUND] [--drop OPP1,OPP2] [--type NAME]   (runs as in
       results/gate.log, e.g. cand6_b3456@b3456; --drop skips opponents whose names start so, e.g. the ones sandwich.py
       found changed; --type counts only champions of that type, as named in decoded.py NAMES, in games where we have
       one in both runs, and adds each side's max health of that type at r600)

Both runs must be decoded first (tools/replay/decode_run.sh RUN). The opponent of each match comes from
`cambc match-groups show` (cached in data/cache/mm_<run>.json). Platform games are deterministic, so on opponents that
did not change bots every difference between the two games comes from our change, but chaotically: a neutral change
flips a quarter of the games. Paired per-game differences of continuous metrics (with their standard error) are the
sharper test. Prints, by flip class (L->W, W->L, same), our and their deaths, gems collected, tributed, lost on death and
rounds with a hit on an enemy champion (to ROUND, default 1000), then the paired mean differences with standard errors.
"""
import collections, gzip, json, math, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\cambc.exe')
OUR = '118dbffc-87ec-48a6-ac9c-dc1e371ba364'
PAT = re.compile(r'^(\S{36})\s+\S+\s+(\S+)\s*\n((?:[ \t]+\S{36}.*\n?){2})', re.M)
FIELDS = ['us deaths', 'them deaths', 'us coll', 'them coll', 'us trib', 'them trib', 'us lost', 'them lost',
          'us hitrounds', 'them hitrounds']


def show(group):
    found = []
    for _ in range(8):  # the listing comes back empty under HTTP 429
        text = subprocess.run([CAMBC, 'match-groups', 'show', group], capture_output=True, text=True, encoding='utf-8').stdout
        found = PAT.findall(text)
        if len(found) >= 5: break
        time.sleep(15)
    return found


def match_map(run):
    """match id -> [opponent name, map, repeat index of that (opponent, map) in the run]"""
    path = os.path.join(ROOT, 'data', 'cache', 'mm_' + run.replace('@', '_') + '.json')
    if os.path.exists(path): return json.load(open(path, encoding='utf-8'))
    ids = [l.split()[1:] for l in open(os.path.join(ROOT, 'results', 'gate.log'), encoding='utf-8') if l.split()[:1] == [run]][-1]
    out, seen = {}, collections.Counter()
    for g in ids:
        for mid, mp, body in show(g):
            opp = [l.split(None, 1)[1].rsplit(' [', 1)[0].strip() for l in body.strip().split('\n') if not l.strip().startswith(OUR)]
            key = (opp[0] if opp else '?', mp)
            out[mid] = [key[0], mp, seen[key]]
            seen[key] += 1
    if len(out) == 5 * len(ids):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
    return out


def stats(run, R, ty=None):
    d = os.path.join(ROOT, 'data', 'fights', run.replace('@', '_'))
    side = {}
    for line in open(os.path.join(d, 'index.txt'), encoding='utf-8'):
        p = line.split()
        if len(p) >= 4: side[p[0]] = (0 if p[2] == 'a' else 1, p[3])
    out = {}
    for mid, (opp, mp, k) in match_map(run).items():
        f = os.path.join(d, mid + '.jsonl.gz')
        if mid not in side or not os.path.exists(f): continue
        rows = [r for r in (json.loads(l) for l in list(gzip.open(f, 'rt'))[1:]) if r.get('c')]
        if not rows: continue
        n = max(len(r['c']) for r in rows)
        rows = [r for r in rows if len(r['c']) == n]
        us, res = side[mid]
        keep = [ty is None or c['ty'] == ty for c in rows[0]['c']]
        if not any(k and c['t'] == us for k, c in zip(keep, rows[0]['c'])): continue
        C = collections.Counter()
        last = rows[0]
        for a, b in zip(rows, rows[1:]):
            if b['r'] > R: break
            last = b
            for i, c in enumerate(b['c']):
                if not keep[i]: continue
                pc = a['c'][i]; w = 'us' if c['t'] == us else 'them'
                if pc['a'] and not c['a']: C[w + ' deaths'] += 1; C[w + ' lost'] += pc.get('g', 0)
                if c['a'] and pc['a'] and c.get('g', 0) > pc.get('g', 0): C[w + ' coll'] += c['g'] - pc['g']
                if a['r'] < 600 <= b['r']: C[w + ' mhp600'] += c.get('mhp', 0)
            for i in range(n):
                if keep[i] and D.enemy_hits(a, i, n): C[('us' if a['c'][i]['t'] == us else 'them') + ' hitrounds'] += 1
        for t in (0, 1): C[('us' if t == us else 'them') + ' trib'] += last['sg'][t]
        C['win'] = res == 'win'
        out[(opp, mp, k)] = C
    return out


if __name__ == '__main__':
    args = sys.argv[1:]
    drop = []
    if '--drop' in args:  # opponents that changed bots between the runs (sandwich.py names them): name prefixes
        j = args.index('--drop'); drop = args[j + 1].split(','); args = args[:j] + args[j + 2:]
    ty = None
    if '--type' in args:
        j = args.index('--type'); ty = D.NAMES.index(args[j + 1]); args = args[:j] + args[j + 2:]
        FIELDS += ['us mhp600', 'them mhp600']
    base, new = args[0], args[1]
    R = int(args[2]) if len(args) > 2 else 1000
    A, B = stats(base, R, ty), stats(new, R, ty)
    keys = [k for k in A if k in B and not any(k[0].startswith(d) for d in drop)]
    print(f'{len(keys)} paired decoded games (to r{R}); base -> new')
    cls = collections.defaultdict(list)
    for k in keys:
        a, b = A[k]['win'], B[k]['win']
        cls['L->W' if b and not a else 'W->L' if a and not b else 'same W' if a else 'same L'].append(k)
    for c in ('L->W', 'W->L', 'same W', 'same L', 'all'):
        ks = keys if c == 'all' else cls[c]
        if ks: print(f'{c:7} {len(ks):3} games  ' + '  '.join(
            f'{f} {sum(A[k][f] for k in ks) / len(ks):.1f}->{sum(B[k][f] for k in ks) / len(ks):.1f}' for f in FIELDS))
    for c in ('W->L', 'L->W'):
        print(c, ', '.join(f'{k[0][:10]}/{k[1][2:]}' for k in sorted(cls[c], key=lambda k: k[1])))
    print('paired mean difference (new - base) +- standard error:')
    for f in FIELDS + ['margin']:
        ds = [((B[k]['us trib'] - B[k]['them trib']) - (A[k]['us trib'] - A[k]['them trib'])) if f == 'margin' else B[k][f] - A[k][f]
              for k in keys]
        m = sum(ds) / len(ds)
        se = math.sqrt(sum((x - m) ** 2 for x in ds) / max(1, len(ds) - 1) / len(ds))
        print(f'  {f:16} {m:+8.1f} +- {se:6.1f}')
