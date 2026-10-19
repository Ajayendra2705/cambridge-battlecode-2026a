"""Black-box optimisation of farming constants: python -I tools/opt.py BASE EVALS [--resume]

Each parameter is a literal in BASE's bot.cpp. A candidate is written into bots/opt_cand (only bot.cpp changes, so
builds are incremental) and raced against the starter bot on every map, both sides. The objective is the mean
finishing round (2000 for a loss), which reproduces platform play exactly on maps without enemy pressure, so it
is only trusted for economy settings; fight settings are left out on purpose.

Search: a (1+4) evolution strategy in [0, 1]-normalised space with a step size that grows after a success and
shrinks after a failed generation (1/5th rule). Every evaluation is appended to tools/opt.log as JSON; the best
candidate so far is copied to bots/opt_best.
"""
import json, os, random, re, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG = os.environ.get('OPT_LOG', os.path.join(ROOT, 'tools', 'opt.log'))
JOBS = os.environ.get('OPT_JOBS', '12')

# name, text in the source with {} where the value goes, default, low, high, integer?
PARAMS = [
    ('gold_w', 'return round < 1400 ? {} : 0.03;', 0.1, 0.0, 0.4, False),
    ('bank_far', 'altar_d > 10 ? {} : 30', 60, 20, 150, True),
    ('bank_near_d', 'gems >= threshold || altar_d <= {} ||', 6, 0, 12, True),
    ('bank_cost_w', 'g.bank_cost * {})', 0.5, 0.0, 1.5, False),
    ('wait_pen', 'time += (n - others - 1) * {};', 4, 0, 12, True),
    ('resp_f', 'time += {} * std::max(0, g.respawn_round', 2.0, 0.5, 4.0, False),
    ('big_wait', 'big_wait < {}', 25, 0, 60, True),
    ('gather_n', 'present < std::min({}, alive_allies())', 4, 1, 6, True),
    ('retreat_m', '(steps_out + 1.0f) + {}f', 40.0, 0.0, 150.0, False),
    ('rejoin_f', 'S.hp >= hardest * {}f + 40.0f', 6.0, 2.0, 12.0, False),
    ('spawn_heal', 'if (at_spawn && S.hp < S.max_hp * {}f) {{', 0.9, 0.6, 1.0, False),
    ('home_heal', 'S.hp < S.max_hp * {}f && incoming == 0', 0.35, 0.1, 0.6, False),
    ('shop_gold', 'gold >= {} || (gold >= 150 && home <= 6)', 300, 120, 900, True),
    ('herd_full', 'full >= {}f;', 300.0, 150.0, 600.0, False),
    ('big_group', 'g.strength_left() >= {}', 200, 60, 600, True),
]
# Survival settings tuned against the passive starter bot get us killed by real teams (opt_g1t: 15/90), so they
# can be pinned at their defaults: OPT_FIX=retreat_m,rejoin_f,...
FIXED = set(filter(None, os.environ.get('OPT_FIX', '').split(',')))


def fmt(p, v):
    if p[5]:
        return str(int(round(v)))
    s = f'{v:.3f}'.rstrip('0')
    return s + '0' if s.endswith('.') else s


def render(template, values):
    src = template
    for p in PARAMS:
        src = src.replace('@' + p[0] + '@', fmt(p, values[p[0]]))
    return src


def make_template(base_src):
    src = base_src
    for p in PARAMS:
        lit = p[1].format(fmt(p, p[2]))
        n = src.count(lit)
        assert n >= 1, f'{p[0]}: {lit!r} not found'
        src = src.replace(lit, p[1].format('@' + p[0] + '@'))
    return src


def evaluate(template, values, name='opt_cand'):
    path = os.path.join(ROOT, 'bots', name, 'src', 'bot.cpp')
    open(path, 'w', encoding='utf-8', newline='\n').write(render(template, values))
    out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'batch.py'), name, 'starter-cpp', '--jobs', JOBS],
                         cwd=ROOT, capture_output=True, text=True).stdout + ''
    m = re.search(r'wins (\d+)/(\d+)\s+avg margin (-?\d+)\s+avg round \(loss=2000\) (\d+)', out)
    if not m or int(m[2]) == 0:
        return None
    return int(m[4]) - int(m[3]) / 10000.0  # ties broken by margin


def to_unit(values):
    return {p[0]: (values[p[0]] - p[3]) / (p[4] - p[3]) for p in PARAMS}


def from_unit(u):
    out = {}
    for p in PARAMS:
        x = min(1.0, max(0.0, u[p[0]]))
        v = p[3] + x * (p[4] - p[3])
        out[p[0]] = round(v) if p[5] else v
    return out


def main():
    base, evals = sys.argv[1], int(sys.argv[2])
    base_src = open(os.path.join(ROOT, 'bots', base, 'src', 'bot.cpp'), encoding='utf-8').read().replace('\r\n', '\n')
    template = make_template(base_src)
    cand = os.path.join(ROOT, 'bots', 'opt_cand')
    if not os.path.isdir(cand):
        shutil.copytree(os.path.join(ROOT, 'bots', base), cand, ignore=shutil.ignore_patterns('.cambc'))
    best_v = {p[0]: p[2] for p in PARAMS}
    if '--init' in sys.argv:
        best_v.update(json.loads(sys.argv[sys.argv.index('--init') + 1]))
    best_s = None
    if '--resume' in sys.argv and os.path.exists(LOG):
        for line in open(LOG):
            r = json.loads(line)
            if r['score'] is not None and (best_s is None or r['score'] < best_s):
                best_s, best_v = r['score'], r['values']
    if best_s is None:
        best_s = evaluate(template, best_v)
        open(LOG, 'a').write(json.dumps({'values': best_v, 'score': best_s, 'kind': 'default'}) + '\n')
    print('start', best_s, flush=True)
    sigma, rng, done = 0.15, random.Random(), 0
    while done < evals:
        u0, gen_best = to_unit(best_v), None
        for _ in range(4):
            # Change a random subset of parameters so single good moves are not drowned by noise in the others.
            k = rng.randint(1, 4)
            keys = rng.sample([p[0] for p in PARAMS if p[0] not in FIXED], k)
            u = dict(u0)
            for key in keys:
                u[key] += rng.gauss(0, sigma)
            v = from_unit(u)
            s = evaluate(template, v)
            done += 1
            open(LOG, 'a').write(json.dumps({'values': v, 'score': s, 'sigma': sigma, 'changed': keys}) + '\n')
            print(f'{done:3} score {s} sigma {sigma:.3f} changed {keys}', flush=True)
            if s is not None and (gen_best is None or s < gen_best[0]):
                gen_best = (s, v)
        if gen_best and gen_best[0] < best_s:
            best_s, best_v = gen_best
            sigma = min(0.4, sigma * 1.5)
            print('IMPROVED', best_s, json.dumps(best_v), flush=True)
            dst = os.path.join(ROOT, 'bots', 'opt_best')
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(cand, dst, ignore=shutil.ignore_patterns('.cambc'))
            open(os.path.join(dst, 'src', 'bot.cpp'), 'w', encoding='utf-8', newline='\n').write(render(template, best_v))
        else:
            sigma = max(0.03, sigma * 0.8)
    print('best', best_s, json.dumps(best_v))


if __name__ == '__main__':
    main()
