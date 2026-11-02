"""Which local variant does best on which map, against v1503: python -I tools/local/maptable.py [--base pool.v1503] [--min-margin N] [--min-wins N] [--out FILE.json] RUN_DIR ...

Reads every game of multi.py runs (data/runs/multi-*), and pairs each candidate's game with the base's game of the same (opponent, map, side), wherever that base game is.
Per (map, candidate): games, base wins, wins difference and margin difference per game. Prints each map's best candidates over the bars (default margin +200 a game, wins +1), the
correlation of a candidate's per-map margin between the first two and the last two opponents of the pool (is a map effect real, or noise?), and writes the table to --out.
A map's sampling error is about 150 of margin with 8 games, so one number decides nothing: this makes a list to test on the platform, it does not choose.
"""
import collections, glob, json, math, os, sys
from concurrent.futures import ProcessPoolExecutor


def one(f):
    try:
        b, o, m, s = os.path.basename(f)[:-5].split('~')
        d = json.load(open(f, encoding='utf-8'))
        us = 'team' + s
        mg = sum(int(t['submittedGems']) * (1 if t['team'] == us else -1) for t in d['teams'])
        return b, o, m, s, mg, d['match']['outcome'] == us, sum(int(x['metrics']['deaths']) for x in d['champions'] if x['team'] == us)
    except Exception:
        return None


def main():
    args = sys.argv[1:]
    def opt(name, dflt):
        if name in args:
            k = args.index(name); v = args[k + 1]; del args[k:k + 2]
            return v
        return dflt
    base = opt('--base', 'pool.v1503'); mm = float(opt('--min-margin', '200')); mw = float(opt('--min-wins', '1')); out = opt('--out', '')
    G = collections.defaultdict(dict)
    # One summary file per run: a game's JSON is large and a run holds thousands (data/cache/maptable_<run>.json).
    for run in args:
        cache = os.path.join('data', 'cache', 'maptable_' + os.path.basename(os.path.normpath(run)) + '.json')
        if os.path.exists(cache):
            res = json.load(open(cache))
        else:
            files = glob.glob(os.path.join(run, '*.json'))
            with ProcessPoolExecutor(2) as ex:
                res = [r for r in ex.map(one, files, chunksize=50) if r]
            json.dump(res, open(cache, 'w'))
        for b, o, m, s, mg, w, d in res:
            G[b].setdefault((o, m, s), (mg, w, d))
    B = G[base]
    T = collections.defaultdict(dict)
    print('candidate    games  wins/g   margin/g  deaths/g  r(pool halves)')
    for c, g in sorted(G.items()):
        if c == base:
            continue
        keys = [k for k in g if k in B]
        if not keys:
            continue
        opps = sorted({k[0] for k in keys})
        half = set(opps[:len(opps) // 2])
        X = collections.defaultdict(lambda: [[], []])
        for k in keys:
            d = g[k][0] - B[k][0]
            X[k[1]][0 if k[0] in half else 1].append(d)
            t = T[k[1]].setdefault(c, [0, 0, 0, 0])
            t[0] += 1; t[1] += B[k][1]; t[2] += g[k][1] - B[k][1]; t[3] += d
        xs = [sum(a) / len(a) for a, b in X.values() if a and b]
        ys = [sum(b) / len(b) for a, b in X.values() if a and b]
        r = 0.0
        if len(xs) > 2:
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
            r = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx * sy else 0.0
        n = len(keys)
        print(f'{c:12} {n:5} {sum(g[k][1] - B[k][1] for k in keys) / n:+6.3f} {sum(g[k][0] - B[k][0] for k in keys) / n:+8.1f} {sum(g[k][2] - B[k][2] for k in keys) / n:+7.2f}   {r:+.2f}')
    print()
    rows = {}
    for mp, cs in sorted(T.items()):
        good = sorted(((v[3] / v[0], v[2], v[0], v[1], c) for c, v in cs.items() if v[3] / v[0] >= mm and v[2] >= mw), reverse=True)
        rows[mp] = [(c, round(m), w, n, bw) for m, w, n, bw, c in good]
        if good:
            print(f'{mp:24} ' + ' '.join(f'{c}({m:+.0f},w{w:+d}/{n})' for m, w, n, bw, c in good[:6]))
    if out:
        json.dump(rows, open(out, 'w'), indent=0)


if __name__ == '__main__':
    main()
