"""Combat calibration: actual vs predicted champion damage taken, from C lines (C round slot pred actual n_enemies).

usage: python tools/calib.py DIR [DIR...]
Prints the overall ratio sum(actual)/sum(pred), per game ratio spread, and a binned reliability table.
Platform replays are named sK_xxxxxxxx (K = panel slot) by the copy step; local multi/pvp names hold the map.
"""
import collections, glob, os, re, sys, zipfile

rows = []
for d in sys.argv[1:]:
    for path in glob.glob(os.path.join(d, '*.repl26a')):
        base = os.path.basename(path)
        m = re.match(r'(.+?)~(.+?)~(.+?)~([AB])\.repl26a', base)
        try:
            z = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            continue
        name = f'team-{m[4].lower()}.stdout' if m else [n for n in z.namelist() if n.endswith('.stdout')][0]
        grp = m[2] if m else base.split('_')[0]
        text = z.read(name).decode('latin1')
        for c in re.finditer(r'^C (\d+) (\d) (\d+) (\d+) (\d+)', text, re.M):
            rows.append((grp, base, int(c[3]), int(c[4])))
print('samples', len(rows))
P = sum(r[2] for r in rows); A = sum(r[3] for r in rows)
print(f'overall actual/pred = {A}/{P} = {A / max(P, 1):.3f}')
by = collections.defaultdict(lambda: [0, 0])
for g, b, p, a in rows: by[g][0] += p; by[g][1] += a
for g, (p, a) in sorted(by.items()): print(f'  {g:12} pred {p:8} actual {a:8} ratio {a / max(p, 1):.3f}')
bins = collections.defaultdict(lambda: [0, 0, 0])
for g, b, p, a in rows:
    k = 0 if p == 0 else min(6, 1 + p // 150)
    bins[k][0] += 1; bins[k][1] += p; bins[k][2] += a
print('pred bin   n    mean_pred  mean_actual')
for k in sorted(bins):
    n, p, a = bins[k]
    print(f'  {k:3} {n:6} {p / n:9.0f} {a / n:9.0f}')
