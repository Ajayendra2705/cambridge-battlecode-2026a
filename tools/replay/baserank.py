"""How lucky is the base? Ranks a base run against every other bot decoded on the same pinned panels, to r1000.
usage: python -I tools/replay/baserank.py BASE PANEL... [--only BOT,BOT...] [--jobs N]
Reads data/fights/<bot>_<panel>_<panel> for every bot found (or only the bots listed). Games on a pinned panel are
deterministic, so one base run is one fixed draw that every later variant is compared with; siblings (variants of the
base) show where that draw sits.
Per panel: the base's wins, deaths (ours and theirs), gems collected and tributed against the siblings' mean, with the
base's rank and its distance from the mean in sibling standard deviations. Then the pooled bias the base carries into a
pooled judgment: the base minus the siblings' mean, weighted by the panels' games.
"""
import collections, concurrent.futures, contextlib, io, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decoded as D

KEYS = ('wins', 'deaths us', 'deaths them', 'collected', 'tributed')

def stats(d):
    ng = w = du = dt = 0
    for us, res, mp, meta, rows in D.games([d]):
        ng += 1; w += res == 'win'; n = len(rows[0]['c'])
        for k in range(1, len(rows)):
            if rows[k]['r'] > 1000: break
            for i in range(n):
                if rows[k - 1]['c'][i]['a'] and not rows[k]['c'][i]['a']:
                    if rows[k - 1]['c'][i]['t'] == us: du += 1
                    else: dt += 1
    out = io.StringIO()
    with contextlib.redirect_stdout(out): D.cmd_gems([d], [1000])
    m = re.search(r'us collected (\d+) tributed (\d+)', out.getvalue())
    return ng, {'wins': w, 'deaths us': du / ng, 'deaths them': dt / ng, 'collected': int(m[1]), 'tributed': int(m[2])}

def main(argv):
    jobs, only = 8, None
    if '--jobs' in argv: i = argv.index('--jobs'); jobs = int(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    if '--only' in argv: i = argv.index('--only'); only = set(argv[i + 1].split(',')); argv = argv[:i] + argv[i + 2:]
    base, panels = argv[0], argv[1:]
    runs = [(b, p) for p in panels for b in sorted({f[:-len(f'_{p}_{p}')] for f in os.listdir('data/fights') if f.endswith(f'_{p}_{p}')})
            if only is None or b in only or b == base]
    with concurrent.futures.ProcessPoolExecutor(jobs) as ex:
        R = dict(zip(runs, ex.map(stats, [f'data/fights/{b}_{p}_{p}' for b, p in runs])))
    bias, tot = collections.Counter(), 0
    for p in panels:
        if (base, p) not in R: print(f'{p}: no {base} run'); continue
        ng, B = R[(base, p)]; sib = [v for (b, q), (_, v) in R.items() if q == p and b != base]
        if len(sib) < 2: print(f'{p}: fewer than two siblings'); continue
        tot += ng
        cells = []
        for key in KEYS:
            xs = [s[key] for s in sib]; m, sd = statistics.mean(xs), statistics.stdev(xs) or 1e-9
            rank = 1 + sum((x < B[key]) if key == 'deaths us' else (x > B[key]) for x in xs)
            cells.append(f"{key} {B[key]:.4g} (mean {m:.4g}, {(B[key] - m) / sd:+.1f} sd, rank {rank}/{len(xs) + 1})")
            bias[key] += ng * (B[key] / ng if key == 'wins' else B[key]) - ng * (m / ng if key == 'wins' else m)
        print(f"{p} ({ng} games, {len(sib)} siblings): " + '; '.join(cells))
    if tot:
        print(f"pooled bias of {base} over {tot} games (base minus siblings' mean, per game): " +
              ', '.join(f"{k} {bias[k] / tot:+.3f}" for k in KEYS))

if __name__ == '__main__':
    main(sys.argv[1:])
