"""(1+lambda) evolution strategy over the banking parameters of bots/bp (src/params.h).

usage: python -I tools/es.py [--gens 8] [--lam 6] [--pool n_d5,c_g1] [--resume]
Each generation mutates the current best into `lam` candidates (bots/es_0..), evaluates all of them plus the
incumbent on the TRAIN maps in one 12-core batch (tools/multi.py), and keeps the best by gem margin. The final
best is re-checked against the starting parameters on the held-out VALID maps. Log: tools/es.log.
"""
import argparse, json, math, os, random, re, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRAIN = '00ambush,00collision,00eight,00expanse,00interlock,01broken-curve,01corridors,01fracture,01hooks,01islands'
VALID = '00corners,00elkring,00fragment,00lanes,00monolith,01big-world,01concentrated-wealth,01elk-arena,01gold-rush,00contest'
# name: (start, lo, hi, is_int)
SPACE = {
    'P_DEADLINE_K': (2.0, 0.5, 6.0, False), 'P_RISKY_WIN': (30, 0, 120, True), 'P_RISKY_ENEMY': (500, 200, 1000, True),
    'P_FAR_D': (10, 3, 30, True), 'P_THR_FAR': (40, 10, 150, True), 'P_THR_NEAR': (20, 5, 100, True),
    'P_NEAR_ALTAR': (6, 0, 20, True), 'P_EV_H': (60.0, 10.0, 300.0, False), 'P_EV_C': (0.2, 0.01, 2.0, False),
    'P_STALL': (6, 2, 20, True), 'P_BLOCK': (40, 5, 150, True),
}
ap = argparse.ArgumentParser()
ap.add_argument('--gens', type=int, default=8)
ap.add_argument('--lam', type=int, default=6)
ap.add_argument('--pool', default='n_d5,c_g1')
ap.add_argument('--resume', action='store_true')
args = ap.parse_args()
LOG = os.path.join(ROOT, 'tools', 'es.log')


def write_bot(name, params):
    dst = os.path.join(ROOT, 'bots', name)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, 'bots', 'bp'), dst, ignore=shutil.ignore_patterns('.cambc'))
    lines = ['#pragma once']
    for k, v in params.items():
        lines.append(f'#define {k} {v}' + ('' if SPACE[k][3] else 'f'))
    open(os.path.join(dst, 'src', 'params.h'), 'w').write('\n'.join(lines) + '\n')


def evaluate(cands, maps):
    out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'multi.py'), ','.join(cands), '--pool', args.pool,
                          '--maps', maps, '--jobs', '12'], capture_output=True, text=True, cwd=ROOT).stdout
    res = {}
    for line in out.splitlines():
        f = line.split()
        if f and f[0] in cands and len(f) >= 7:
            res[f[0]] = dict(games=int(f[1]), wins=int(f[2]), margin=int(f[6]))
    return res


def mutate(p, scale):
    q = dict(p)
    for k in random.sample(list(SPACE), k=random.randint(1, 3)):
        start, lo, hi, is_int = SPACE[k]
        v = q[k] * math.exp(random.gauss(0, scale)) if q[k] > 0 else random.uniform(lo, hi) * 0.2
        v = min(hi, max(lo, v))
        q[k] = int(round(v)) if is_int else round(v, 3)
    return q


start = {k: v[0] for k, v in SPACE.items()}
best = start
if args.resume and os.path.exists(LOG):
    for line in open(LOG):
        if line.startswith('BEST '): best = json.loads(line[5:])
random.seed(len(open(LOG).readlines()) if os.path.exists(LOG) else 0)
scale = 0.35
for gen in range(args.gens):
    cands = {'es_inc': best}
    for i in range(args.lam):
        cands[f'es_{i}'] = mutate(best, scale)
    for name, p in cands.items(): write_bot(name, p)
    res = evaluate(list(cands), TRAIN)
    ranked = sorted(res, key=lambda n: res[n]['margin'], reverse=True)
    with open(LOG, 'a') as f:
        for n in ranked: f.write(f'gen {gen} {n} {json.dumps(res[n])} {json.dumps(cands[n])}\n')
        win = ranked[0]
        if win != 'es_inc' and res[win]['margin'] > res['es_inc']['margin']:
            best = cands[win]; scale = min(0.6, scale * 1.2)
        else:
            scale = max(0.1, scale * 0.8)
        f.write('BEST ' + json.dumps(best) + '\n')
    print(f'gen {gen}: incumbent {res["es_inc"]["margin"]:+}  best {ranked[0]} {res[ranked[0]]["margin"]:+}  scale {scale:.2f}', flush=True)
write_bot('es_best', best)
write_bot('es_start', start)
v = evaluate(['es_start', 'es_best'], VALID)
print('VALID held-out maps:', v)
print('best params', json.dumps(best))
with open(LOG, 'a') as f: f.write('VALID ' + json.dumps(v) + '\n')
