"""Per-map head to head of two whole bots on the same local games, for choosing which part of a hybrid plays a map.

usage: python -I tools/local/routemaps.py RUNDIR CAND_A CAND_B [--now A|B per map: MAP=A,MAP=B ...] [--bar N]

RUNDIR is a multi.py run folder (files CAND~POOL~MAP~SIDE.json, CAND with '/' as '.'). For every map: each candidate's
wins, games, gem margin per game and deaths per game against the same pool bots and sides; then whether the other
part clears the bar (rule_route.md, 11-02: at least N more wins, default 5, and a higher margin) over the part that
plays the map now. --now names the current part per map (default: A on every map).
"""
import collections, glob, json, os, sys

args = sys.argv[1:]
bar = 5
if '--bar' in args:
    j = args.index('--bar'); bar = int(args[j + 1]); args = args[:j] + args[j + 2:]
now = {}
if '--now' in args:
    j = args.index('--now'); now = dict(x.split('=') for x in args[j + 1].split(',')); args = args[:j] + args[j + 2:]
run, A, B = args[0], args[1].replace('/', '.'), args[2].replace('/', '.')
S = collections.defaultdict(collections.Counter)
for f in glob.glob(os.path.join(run, '*.json')):
    cand, pool, mp, side = os.path.basename(f)[:-5].split('~')
    if cand not in (A, B): continue
    j = json.load(open(f, encoding='utf-8'))
    us = 'team' + side
    g = {t['team']: int(t['submittedGems']) for t in j['teams']}
    s = S[(cand, mp)]
    s['n'] += 1
    s['w'] += j['match']['outcome'] == us
    s['m'] += sum(v if k == us else -v for k, v in g.items())
    s['d'] += sum(float(c['metrics']['deaths']) for c in j['champions'] if c['team'] == us)
maps = sorted({mp for _, mp in S})
print(f'{"map":22} {A[:14]:>14} {"":14} {B[:14]:>14} {"":14}  now  other clears the bar?')
for mp in maps:
    a, b = S[(A, mp)], S[(B, mp)]
    cur = now.get(mp, 'A')
    c, o = (a, b) if cur == 'A' else (b, a)
    ok = o['n'] and c['n'] and o['w'] - c['w'] >= bar and o['m'] / o['n'] > c['m'] / c['n']
    fmt = lambda s: f"{s['w']:2}/{s['n']:2} {s['m'] / max(1, s['n']):+6.0f} d{s['d'] / max(1, s['n']):4.1f}"
    print(f'{mp:22} {fmt(a):>29} {fmt(b):>29}  {cur:3}  {"YES" if ok else "no"}')
