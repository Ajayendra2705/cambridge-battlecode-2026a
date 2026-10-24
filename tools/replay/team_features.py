"""Per-team, per-game behaviour features from decoded replays (tools/replay/rounds_extract.mjs), averaged for winners
vs losers. usage:
  python -I tools/replay/team_features.py ranked FIGHTDIR                    rival-vs-rival (winner = higher final tribute)
  python -I tools/replay/team_features.py ours FIGHTDIR INDEX.txt...         our games (gdl.py index: match map side result)
Features: tributed gems by r300 / r600, tributes made, deaths (before r300 / all), kills, mean teammates within 5,
share of rounds on the enemy half, share of camp hits shared with a teammate within 3, mean bag carried."""
import collections, glob, gzip, json, os, sys

d = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1]))
KEYS = ('sub300', 'sub600', 'tributes', 'deaths300', 'deaths', 'kills', 'pack', 'deep', 'shared', 'bag')


def features(path):
    rows = [json.loads(l) for l in gzip.open(path, 'rt')]
    meta, rows = rows[0], rows[1:]
    n = max(len(x['c']) for x in rows)
    rows = [x for x in rows if len(x['c']) == n]
    if not rows: return None
    home = {}
    for c in rows[0]['c']:
        if 'x' in c: home.setdefault(c['t'], []).append((c['x'], c['y']))
    home = {t: (sum(x for x, _ in v) / len(v), sum(y for _, y in v) / len(v)) for t, v in home.items()}
    F = {t: collections.Counter() for t in (0, 1)}
    cnt = {t: collections.Counter() for t in (0, 1)}
    prev = None
    for row in rows:
        r = row['r']
        for t in (0, 1):
            if r <= 300: F[t]['sub300'] = row['sg'][t]
            if r <= 600: F[t]['sub600'] = row['sg'][t]
        pos = [(c['x'], c['y']) if c['a'] and 'x' in c else None for c in row['c']]
        for i, c in enumerate(row['c']):
            t = c['t']
            if pos[i] is None: continue
            F[t]['pack'] += sum(1 for j, o in enumerate(row['c']) if j != i and o['t'] == t and pos[j] and d(pos[i], pos[j]) <= 5)
            if t in home and 1 - t in home: F[t]['deep'] += d(pos[i], home[1 - t]) < d(pos[i], home[t])
            F[t]['bag'] += c.get('g', 0)
            cnt[t]['alive'] += 1
        hits = {}
        for i, acts in enumerate(row['act'][:n]):
            for a in acts:
                if a[0] == 'tribute': F[row['c'][i]['t']]['tributes'] += 1
                if a[0] in ('attack', 'cast') and len(a) >= 5 and a[-2] == 'm' and i not in hits:
                    hits[i] = (a[1], a[2]) if a[0] == 'attack' else (a[2], a[3])
        for i, p in hits.items():
            t = row['c'][i]['t']
            cnt[t]['hits'] += 1
            F[t]['shared'] += any(j != i and row['c'][j]['t'] == t and d(p, q) <= 3 for j, q in hits.items())
        if prev:
            for i, c in enumerate(row['c']):
                if prev['c'][i]['a'] and not c['a']:
                    F[c['t']]['deaths'] += 1
                    if r < 300: F[c['t']]['deaths300'] += 1
                    F[1 - c['t']]['kills'] += 1
        prev = row
    for t in (0, 1):
        F[t]['pack'] /= max(1, cnt[t]['alive'])
        F[t]['deep'] /= max(1, cnt[t]['alive'])
        F[t]['bag'] /= max(1, cnt[t]['alive'])
        F[t]['shared'] /= max(1, cnt[t]['hits'])
    final = rows[-1]['sg']
    return F, final


def show(groups):
    print(f"{'':10}" + ''.join(f'{k:>10}' for k in KEYS))
    for name, fs in groups:
        if not fs: continue
        print(f'{name:10}' + ''.join(f'{sum(f[k] for f in fs) / len(fs):10.2f}' for k in KEYS) + f'   n={len(fs)}')


def main():
    mode, fdir = sys.argv[1], sys.argv[2]
    W, L = [], []
    if mode == 'ranked':
        for p in glob.glob(os.path.join(fdir, '*.jsonl.gz')):
            out = features(p)
            if not out: continue
            F, final = out
            if final[0] == final[1]: continue
            w = 0 if final[0] > final[1] else 1
            W.append(F[w]); L.append(F[1 - w])
        show((('winners', W), ('losers', L)))
    else:
        side_of = {}
        for f in sys.argv[3:]:
            for l in open(f):
                p = l.split()
                if len(p) >= 4: side_of[p[0]] = (0 if p[2] == 'a' else 1, p[3])
        UW, UL, TW, TL = [], [], [], []
        for p in glob.glob(os.path.join(fdir, '*.jsonl.gz')):
            mid = os.path.basename(p).split('.')[0]
            if mid not in side_of: continue
            out = features(p)
            if not out: continue
            F, _ = out
            us, res = side_of[mid]
            (UW if res == 'win' else UL).append(F[us])
            (TL if res == 'win' else TW).append(F[1 - us])
        show((('us won', UW), ('us lost', UL), ('them won', TW), ('them lost', TL)))


if __name__ == '__main__':
    main()
