"""Robust game-by-game comparison of platform runs: python -I tools/platform/rcmp.py BASE NEW [NEW2 ...]
Fetches every group of each run (results/gate.log) with retries until it has 5 results (losscmp.py drops games on
HTTP 429), caches them in data/cache/res_<run>.json, and compares each NEW run with BASE on the shared
(opponent, map) games: wins, flips, margin (our - their gems) and a sign test. A run may be several runs joined with +
(`dr3_b5@b5+dr3_b6@b6`) to compare with one gate over a combined panel (`cp3_b56@b56`)."""
import json, math, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # team names are not all Latin
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'data', 'cache')
os.makedirs(OUT, exist_ok=True)
ROW = re.compile(r'^(\S+)\s+(WIN|loss)\s+(\d+)\s*-\s*(\d+)\s+r\s*(\d+).*vs (.+)$', re.M)


def fetch(run):
    # 'A@b5+B@b6' merges runs in order, as one gate over both panels (results/panels/specs_b56.txt = b5 then b6) would
    # log them: a (opponent, map) seen again gets a '+' suffix. So a b56 run compares with separate b5 and b6 runs.
    if '+' in run:
        res = {}
        for part in run.split('+'):
            for k, v in fetch(part).items():
                while k in res: k = (k[0], k[1] + '+')
                res[k] = v
        return res
    cache = os.path.join(OUT, 'res_' + run.replace('@', '_') + '.json')
    if os.path.exists(cache):
        return {tuple(k.split('|')): v for k, v in json.load(open(cache)).items()}
    ids = [l.split()[1:] for l in open(os.path.join(ROOT, 'results', 'gate.log')) if l.split()[:1] == [run]][-1]
    res = {}
    for g in ids:
        rows = []
        for attempt in range(12):
            out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'platform', 'group.py'), g], capture_output=True,
                                 text=True, encoding='utf-8', errors='replace').stdout
            rows = ROW.findall(out)
            if len(rows) >= 5: break
            time.sleep(5 + 5 * attempt)
        if len(rows) < 5: print('WARN', run, g, len(rows), 'results', file=sys.stderr)
        for mp, wl, a, b, rnd, opp in rows:
            k = (opp.strip(), mp)
            while k in res: k = (k[0], k[1] + '+')  # same opponent and map twice in one run
            res[k] = [wl == 'WIN', int(a) - int(b), int(a), int(b)]
    json.dump({'|'.join(k): v for k, v in res.items()}, open(cache, 'w'))
    return res


base, news = sys.argv[1], sys.argv[2:]
B = fetch(base)
print(base, len(B), 'games', sum(v[0] for v in B.values()), 'wins')
for new in news:
    N = fetch(new)
    keys = [k for k in N if k in B]
    up = [k for k in keys if N[k][0] and not B[k][0]]
    down = [k for k in keys if B[k][0] and not N[k][0]]
    better = sum(N[k][1] > B[k][1] for k in keys)
    worse = sum(N[k][1] < B[k][1] for k in keys)
    dm = sum(N[k][1] - B[k][1] for k in keys)
    n = better + worse
    z = (better - worse) / math.sqrt(n) if n else 0
    p = math.erfc(abs(z) / math.sqrt(2))
    print(f'{new}: {len(keys)} shared games | wins {sum(N[k][0] for k in keys)} vs base {sum(B[k][0] for k in keys)} | '
          f'L->W {len(up)} W->L {len(down)} | margin diff {dm:+d} ({dm / max(1, len(keys)):+.0f}/game) | '
          f'better {better} worse {worse} p={p:.3f}')
    print('  up:', ' '.join(f'{k[0][:10]}/{k[1][2:12]}' for k in up))
    print('  down:', ' '.join(f'{k[0][:10]}/{k[1][2:12]}' for k in down))
