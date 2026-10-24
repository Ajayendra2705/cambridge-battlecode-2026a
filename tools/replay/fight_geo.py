"""Team geometry from per-round replay datasets (tools/replay/rounds_extract.mjs): how each team groups and where and
how its champions die. usage: python -I tools/replay/fight_geo.py FIGHTDIR INDEX.txt...  (INDEX = gdl.py index files:
"match map side result"; side a = team 0). Prints us vs them by game phase:
  near   mean Chebyshev distance to the nearest living teammate
  pack   mean teammates within 5 tiles
  deep   share of champion-rounds on the enemy's half (nearer the enemy start than our own)
and, at each death, allies and enemies within 6 of the victim in the round before."""
import collections, glob, gzip, json, os, sys

PHASES = ((0, 300), (300, 900), (900, 2001))
d = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def phase(r):
    return next(i for i, (lo, hi) in enumerate(PHASES) if lo <= r < hi)


def main():
    fdir, idx = sys.argv[1], sys.argv[2:]
    side_of, res_of = {}, {}
    for f in idx:
        for l in open(f):
            p = l.split()
            if len(p) >= 4: side_of[p[0]], res_of[p[0]] = 0 if p[2] == 'a' else 1, p[3]
    acc = {res: {who: collections.defaultdict(list) for who in 'UT'} for res in ('win', 'loss')}
    deaths = {res: {who: [] for who in 'UT'} for res in ('win', 'loss')}
    for f in glob.glob(os.path.join(fdir, '*.jsonl.gz')):
        mid = os.path.basename(f).split('.')[0]
        if mid not in side_of: continue
        us, res = side_of[mid], res_of[mid]
        rows = [json.loads(l) for l in gzip.open(f, 'rt')][1:]
        n = max(len(x['c']) for x in rows)
        rows = [x for x in rows if len(x['c']) == n]
        start = {}
        for c in rows[0]['c']:
            if 'x' in c: start.setdefault(c['t'], []).append((c['x'], c['y']))
        home = {t: (sum(x for x, _ in v) / len(v), sum(y for _, y in v) / len(v)) for t, v in start.items()}
        prev = None
        for row in rows:
            r, ph = row['r'], phase(row['r'])
            pos = [(c['x'], c['y']) if c['a'] and 'x' in c else None for c in row['c']]
            for i, c in enumerate(row['c']):
                if pos[i] is None: continue
                who = 'U' if c['t'] == us else 'T'
                mates = [pos[j] for j, o in enumerate(row['c']) if j != i and o['t'] == c['t'] and pos[j]]
                a = acc[res][who]
                if mates:
                    a[('near', ph)].append(min(d(pos[i], m) for m in mates))
                    a[('pack', ph)].append(sum(d(pos[i], m) <= 5 for m in mates))
                own, opp = home.get(c['t']), home.get(1 - c['t'])
                if own and opp: a[('deep', ph)].append(d(pos[i], opp) < d(pos[i], own))
            if prev and len(prev['c']) == len(row['c']):
                for i, c in enumerate(row['c']):
                    pc = prev['c'][i]
                    if pc['a'] and not c['a'] and 'x' in pc:
                        at = (pc['x'], pc['y'])
                        allies = sum(1 for j, o in enumerate(prev['c']) if j != i and o['t'] == pc['t'] and o['a'] and 'x' in o and d(at, (o['x'], o['y'])) <= 6)
                        enemies = sum(1 for o in prev['c'] if o['t'] != pc['t'] and o['a'] and 'x' in o and d(at, (o['x'], o['y'])) <= 6)
                        deaths[res]['U' if pc['t'] == us else 'T'].append((prev['r'], allies, enemies))
            prev = row
    for res in ('loss', 'win'):
        print(f'== games we {res.upper()}')
        for key in ('near', 'pack', 'deep'):
            line = []
            for ph, (lo, hi) in enumerate(PHASES):
                u, t = acc[res]['U'][(key, ph)], acc[res]['T'][(key, ph)]
                if u and t: line.append(f'r{lo}-{hi - 1}: us {sum(u) / len(u):5.2f} them {sum(t) / len(t):5.2f}')
            print(f'  {key:5}', ' | '.join(line))
        for who, name in (('U', 'our deaths'), ('T', 'their deaths')):
            ds = deaths[res][who]
            if not ds: continue
            early = sum(1 for r, *_ in ds if r < 300)
            outn = sum(1 for _, a, e in ds if e > a + 1)
            print(f'  {name}: {len(ds)} ({early} before r300); mean allies within 6 {sum(a for _, a, _ in ds) / len(ds):.2f}, '
                  f'enemies {sum(e for *_, e in ds) / len(ds):.2f}; victim outnumbered (enemies > allies + 1) {outn / len(ds):.0%}')


if __name__ == '__main__':
    main()
