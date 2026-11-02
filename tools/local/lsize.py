"""Paired local result of candidates against a base, per team size: python -I tools/local/lsize.py RUNDIR BASE [CAND ...]

RUNDIR is a multi.py run folder holding the base's games too (files CAND~POOL~MAP~SIDE.json, as tools/local/screen.sh leaves them; CAND with '/' as '.'). The team size of a map
comes from data/maps_size3.txt, maps_size4.txt and maps_size5.txt. For every candidate and size: paired games, wins per game and gem margin per game, new minus base with its
standard error, and the number of bodies that died per game. A draft change for one size should show its effect there and nothing on the other sizes.
"""
import collections, glob, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
run, base = sys.argv[1], sys.argv[2].replace('/', '.')
cands = [c.replace('/', '.') for c in sys.argv[3:]]
size = {}
for k in (3, 4, 5):
    for m in open(os.path.join(ROOT, 'data', f'maps_size{k}.txt'), encoding='utf-8').read().strip().split(','):
        size[m] = k
G = collections.defaultdict(dict)
for f in glob.glob(os.path.join(run, '*.json')):
    n = os.path.basename(f)[:-5].split('~')
    if len(n) != 4:
        continue
    cand, pool, mp, side = n
    if cand != base and cands and cand not in cands:
        continue
    try:
        j = json.load(open(f, encoding='utf-8'))
    except ValueError:
        continue
    us = 'team' + side
    gems = {t['team']: float(t['submittedGems']) for t in j['teams']}
    G[(pool, mp, side)][cand] = (1.0 if j['match']['outcome'] == us else 0.0,
                                 sum(v if k == us else -v for k, v in gems.items()),
                                 sum(float(c['metrics']['deaths']) for c in j['champions'] if c['team'] == us))
names = sorted({c for g in G.values() for c in g if c != base})


def ms(v):
    n = len(v)
    m = sum(v) / n
    return m, math.sqrt(sum((x - m) ** 2 for x in v) / max(1, n - 1) / n)


print(f'{"candidate":14} size games | wins new-base        | margin new-base   | deaths new base | changed games')
for c in names:
    for k in (3, 4, 5, 0):
        rows = [g for key, g in G.items() if c in g and base in g and (k == 0 or size.get(key[1]) == k)]
        if not rows:
            continue
        dw, se = ms([g[c][0] - g[base][0] for g in rows])
        dm, sm = ms([g[c][1] - g[base][1] for g in rows])
        dn = sum(g[c][2] for g in rows) / len(rows)
        db = sum(g[base][2] for g in rows) / len(rows)
        ch = sum(1 for g in rows if g[c][:2] != g[base][:2])
        print(f'{c:14} {k or "all":>4} {len(rows):5} | {dw:+.3f} +- {se:.3f} | {dm:+7.1f} +- {sm:5.1f} | {dn:5.2f} {db:5.2f} | {ch}')
