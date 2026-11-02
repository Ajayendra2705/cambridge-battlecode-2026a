"""Paired local result of a candidate against a base on near and far maps: python -I tools/local/lnear.py RUNDIR BASE CAND [CUT]

A map is far when its spawn walk (`data/map_features.json`, sd) is CUT or more (default 61, the line the bots use). For near, far, each team size and all: paired games, wins, gem margin, our
deaths minus theirs to r100 and r300, and team earned gold at r150 and r300, each as new minus base per game with its standard error. A pair of Cassi and Issac counts one death.
"""
import collections, glob, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
run, base, cand = sys.argv[1], sys.argv[2].replace('/', '.'), sys.argv[3].replace('/', '.')
cut = int(sys.argv[4]) if len(sys.argv) > 4 else 61
feat = {f['map']: f for f in json.load(open(os.path.join(ROOT, 'data', 'map_features.json'), encoding='utf-8'))}


def walk(mp):
    f = feat.get(mp) or feat.get(mp.replace('-', '_')) or feat.get(mp.replace('_', '-'))
    return f.get('sd') if f else None


def gold_at(runs, r):
    """Value of a run-length encoded timeline at round r."""
    k = 0
    for x in runs:
        k += x['duration']
        if r < k:
            return float(x['value'])
    return float(runs[-1]['value']) if runs else 0.0


def load(path, side):
    j = json.load(open(path, encoding='utf-8'))
    us = 'team' + side
    gems = {t['team']: float(t['submittedGems']) for t in j['teams']}
    out = {'w': 1.0 if j['match']['outcome'] == us else 0.0, 'm': sum(v if k == us else -v for k, v in gems.items())}
    d = [0, 0]
    for e in j['events']:
        if e['kind'] != 'death' or e['owner'].get('name') == 'Issac':
            continue
        for x in e['entries']:
            r = x['timestamp']['round']
            s = 1 if e['owner'].get('team') == us else -1
            if r <= 100:
                d[0] += s
            if r <= 300:
                d[1] += s
    out['d100'], out['d300'] = d
    g = [0.0, 0.0]
    for t in j.get('championTimelines', []):
        if t['metric'] != 'earnedGold' or t['owner'].get('team') != us:
            continue
        g[0] += gold_at(t['runs'], 150)
        g[1] += gold_at(t['runs'], 300)
    out['g150'], out['g300'] = g
    return out


G = collections.defaultdict(dict)
for f in glob.glob(os.path.join(run, '*.json')):
    n = os.path.basename(f)[:-5].split('~')
    if len(n) != 4 or n[0] not in (base, cand):
        continue
    try:
        G[(n[1], n[2], n[3])][n[0]] = load(f, n[3])
    except (ValueError, KeyError):
        continue


def ms(v):
    k = len(v)
    m = sum(v) / k
    return m, math.sqrt(sum((x - m) ** 2 for x in v) / max(1, k - 1) / k)


unknown = sorted({k[1] for k in G if walk(k[1]) is None})
if unknown:
    print('no spawn walk for:', ' '.join(unknown))
size = {}
for n in (3, 4, 5):
    for m in open(os.path.join(ROOT, 'data', f'maps_size{n}.txt'), encoding='utf-8').read().strip().split(','):
        size[m] = n
for name, test in (('near', lambda k: walk(k[1]) is not None and walk(k[1]) < cut), ('far', lambda k: walk(k[1]) is not None and walk(k[1]) >= cut), ('3', lambda k: size.get(k[1]) == 3),
                   ('4', lambda k: size.get(k[1]) == 4), ('5', lambda k: size.get(k[1]) == 5), ('all', lambda k: True)):
    rows = [g for k, g in G.items() if base in g and cand in g and test(k)]
    if not rows:
        continue
    parts = []
    for key, fmt in (('w', '{:+.3f} +- {:.3f}'), ('m', '{:+.0f} +- {:.0f}'), ('d100', '{:+.2f} +- {:.2f}'), ('d300', '{:+.2f} +- {:.2f}'), ('g150', '{:+.0f} +- {:.0f}'), ('g300', '{:+.0f} +- {:.0f}')):
        parts.append(key + ' ' + fmt.format(*ms([g[cand][key] - g[base][key] for g in rows])))
    print(f'{name:5} {len(rows):4} games | ' + ' | '.join(parts))
