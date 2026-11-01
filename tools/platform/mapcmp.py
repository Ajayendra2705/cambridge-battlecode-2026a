"""One map of two platform runs, paired by opponent: python -I tools/platform/mapcmp.py BASE NEW MAP

Reads the result caches that rcmp.py writes (data/cache/res_<run>.json; run rcmp.py BASE NEW first). On MAP: each
run's wins and the paired margin difference a game with its standard error. On every other map: how many games
changed winner or margin (for a variant that should only change MAP, e.g. hym's 00monolith routing, rule_route.md).
"""
import json, math, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
base, new, mp = sys.argv[1], sys.argv[2], sys.argv[3]
load = lambda r: {tuple(k.split('|')): v for k, v in json.load(open(os.path.join(ROOT, 'data', 'cache', 'res_' + r.replace('@', '_') + '.json'))).items()}
B, N = load(base), load(new)
keys = [k for k in N if k in B]
on = [k for k in keys if k[1].rstrip('+') == mp]
off = [k for k in keys if k[1].rstrip('+') != mp]
ds = [N[k][1] - B[k][1] for k in on]
m = sum(ds) / len(ds) if ds else 0
se = math.sqrt(sum((d - m) ** 2 for d in ds) / (len(ds) - 1) / len(ds)) if len(ds) > 1 else 0
print(f'{mp}: {len(on)} paired games | wins {sum(B[k][0] for k in on)} -> {sum(N[k][0] for k in on)} | '
      f'L->W {sum(N[k][0] and not B[k][0] for k in on)} W->L {sum(B[k][0] and not N[k][0] for k in on)} | '
      f'margin {sum(B[k][1] for k in on) / max(1, len(on)):+.0f} -> {sum(N[k][1] for k in on) / max(1, len(on)):+.0f} a game, '
      f'difference {m:+.0f} +- {se:.0f}')
print(f'other maps: {len(off)} paired games, winner changed in {sum(B[k][0] != N[k][0] for k in off)}, '
      f'margin changed in {sum(B[k][1] != N[k][1] for k in off)}')
