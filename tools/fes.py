"""(1+lambda) evolution strategy over the farming parameters of bots/fp (src/fparams.h).

usage: python -I tools/fes.py [--gens 10] [--lam 7] [--resume]
Objective: mean finishing round against starter-cpp (both sides; a loss counts 2000) on the TRAIN maps, all
candidates in one 16-job run-batch. The final best is compared with the start on the held-out VALID maps.
Log: tools/fes.log (one line per candidate, BEST lines, VALID line).
"""
import argparse, json, math, os, random, re, shutil, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CAMBC = os.path.expandvars(r'%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0'
                           r'\LocalCache\local-packages\Python311\Scripts\cambc.exe')
TRAIN = '00ambush 00collision 00eight 00expanse 00interlock 01broken-curve 01corridors 01fracture 01hooks 01islands 00lanes'.split()
VALID = '00corners 00elkring 00fragment 00monolith 01big-world 01concentrated-wealth 01elk-arena 01gold-rush 00contest 01boss-battle'.split()
SPACE = {  # name: (start, lo, hi, is_int)
    'F_TRIP': (6.0, 0.0, 30.0, False), 'F_GOLD': (0.25, 0.02, 1.0, False), 'F_TRAVEL': (0.7, 0.3, 1.5, False),
    'F_BANK': (0.5, 0.0, 1.5, False), 'F_WAIT': (2.0, 0.5, 5.0, False), 'F_TEAMWAIT': (4.0, 0.0, 15.0, False),
    'F_STICK': (1.05, 1.0, 1.5, False), 'F_BIGSTR': (200.0, 80.0, 500.0, False), 'F_BIGWAIT': (25, 0, 60, True),
}
ap = argparse.ArgumentParser()
ap.add_argument('--gens', type=int, default=10)
ap.add_argument('--lam', type=int, default=7)
ap.add_argument('--resume', action='store_true')
args = ap.parse_args()
LOG = os.path.join(ROOT, 'tools', 'fes.log')


def write_bot(name, params):
    dst = os.path.join(ROOT, 'bots', name)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, 'bots', 'fp'), dst, ignore=shutil.ignore_patterns('.cambc'))
    lines = ['#pragma once'] + [f'#define {k} {v}' + ('' if SPACE[k][3] else ('f' if k == 'F_BIGSTR' else '')) for k, v in params.items()]
    open(os.path.join(dst, 'src', 'fparams.h'), 'w').write('\n'.join(lines) + '\n')
    r = subprocess.run([CAMBC, 'build', name, '--release'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode: print('build failed', name, r.stdout[-800:], r.stderr[-800:]); sys.exit(1)


def evaluate(names, maps):
    out = os.path.join(ROOT, 'replays', 'fes-' + time.strftime('%H%M%S'))
    os.makedirs(out, exist_ok=True)
    rows, jobs = [], []
    for n in names:
        for m in maps:
            for a, b, us in ((n, 'starter-cpp', 'teamA'), ('starter-cpp', n, 'teamB')):
                tag = f'{n}~{m}~{us[-1]}'
                rows.append(f'"../../bots/{a}" "../../bots/{b}" "../../maps/{m}.map26a" "{tag}.repl26a" --statistics "{tag}.json" --json')
                jobs.append((n, us, tag))
    open(os.path.join(out, 'matches.txt'), 'w').write('\n'.join(rows) + '\n')
    subprocess.run([CAMBC, 'run-batch', os.path.join(out, 'matches.txt'), '--jobs', '16', '--release'], cwd=ROOT,
                   capture_output=True, text=True)
    tot = {n: [0, 0] for n in names}
    for n, us, tag in jobs:
        p = os.path.join(out, tag + '.json')
        if not os.path.exists(p): tot[n][0] += 2000; tot[n][1] += 1; continue
        d = json.load(open(p, encoding='utf-8'))
        rnd = d['match']['roundsCompleted'] if d['match']['outcome'] == us else 2000
        tot[n][0] += rnd; tot[n][1] += 1
    shutil.rmtree(out, ignore_errors=True)
    return {n: t / max(c, 1) for n, (t, c) in tot.items()}


def mutate(p, scale):
    q = dict(p)
    for k in random.sample(list(SPACE), k=random.randint(1, 3)):
        start, lo, hi, is_int = SPACE[k]
        base = q[k] if q[k] > 0 else (hi - lo) * 0.05
        v = min(hi, max(lo, base * math.exp(random.gauss(0, scale))))
        q[k] = int(round(v)) if is_int else round(v, 3)
    return q


start = {k: v[0] for k, v in SPACE.items()}
best = start
if args.resume and os.path.exists(LOG):
    for line in open(LOG):
        if line.startswith('BEST '): best = json.loads(line[5:])
random.seed(int(time.time()))
scale = 0.35
for gen in range(args.gens):
    cands = {'fe_inc': best}
    for i in range(args.lam): cands[f'fe_{i}'] = mutate(best, scale)
    for n, p in cands.items(): write_bot(n, p)
    res = evaluate(list(cands), TRAIN)
    ranked = sorted(res, key=lambda n: res[n])
    with open(LOG, 'a') as f:
        for n in ranked: f.write(f'gen {gen} {n} {res[n]:.1f} {json.dumps(cands[n])}\n')
        if ranked[0] != 'fe_inc' and res[ranked[0]] < res['fe_inc'] - 3:
            best = cands[ranked[0]]; scale = min(0.6, scale * 1.2)
        else:
            scale = max(0.1, scale * 0.8)
        f.write('BEST ' + json.dumps(best) + '\n')
    print(f'gen {gen}: incumbent {res["fe_inc"]:.1f} best {ranked[0]} {res[ranked[0]]:.1f} scale {scale:.2f}', flush=True)
write_bot('fe_best', best); write_bot('fe_start', start)
v = evaluate(['fe_start', 'fe_best'], VALID)
print('VALID held-out maps (mean round, lower is better):', v)
print('best', json.dumps(best))
with open(LOG, 'a') as f: f.write('VALID ' + json.dumps(v) + ' ' + json.dumps(best) + '\n')
