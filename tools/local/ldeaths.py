"""Paired deaths to a round in a local run: python -I tools/local/ldeaths.py RUNDIR BASE CAND [ROUND ...]   (default rounds 100 300 1000)

RUNDIR is a multi.py run folder holding both candidates' games. A pair of Cassi and Issac dies together, so its death counts once on either side (Issac's death is not counted).
For each round: our deaths and theirs per game for base and candidate, and the paired change of our deaths minus theirs with its standard error.
"""
import collections, glob, json, math, os, sys

run, base, cand = sys.argv[1], sys.argv[2].replace('/', '.'), sys.argv[3].replace('/', '.')
rounds = [int(x) for x in sys.argv[4:]] or [100, 300, 1000]
G = collections.defaultdict(dict)
for f in glob.glob(os.path.join(run, '*.json')):
    n = os.path.basename(f)[:-5].split('~')
    if len(n) != 4 or n[0] not in (base, cand):
        continue
    try:
        j = json.load(open(f, encoding='utf-8'))
    except ValueError:
        continue
    us = 'team' + n[3]
    d = []
    for e in j['events']:
        if e['kind'] != 'death' or e['owner'].get('name') == 'Issac':
            continue
        for x in e['entries']:
            d.append((x['timestamp']['round'], e['owner'].get('team') == us))
    G[(n[1], n[2], n[3])][n[0]] = d
for R in rounds:
    diff = []
    s = collections.Counter()
    for g in G.values():
        if base not in g or cand not in g:
            continue
        v = {}
        for c in (base, cand):
            u = sum(1 for r, mine in g[c] if r <= R and mine)
            t = sum(1 for r, mine in g[c] if r <= R and not mine)
            s[c + ' us'] += u
            s[c + ' them'] += t
            v[c] = u - t
        diff.append(v[cand] - v[base])
    if not diff:
        continue
    n = len(diff)
    m = sum(diff) / n
    se = math.sqrt(sum((x - m) ** 2 for x in diff) / max(1, n - 1) / n)
    print(f'r{R}: {n} pairs; {base} us {s[base + " us"] / n:.2f} them {s[base + " them"] / n:.2f}; {cand} us {s[cand + " us"] / n:.2f} them {s[cand + " them"] / n:.2f}; us minus them {m:+.2f} +- {se:.2f}')
