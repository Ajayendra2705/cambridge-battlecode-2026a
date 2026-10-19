"""Paired A/B verdict between two gate runs: python -I tools/paired.py OLD NEW

OLD and NEW are bot names logged in tools/gate.log by tools/gate.sh (latest run of each is used).
Games are paired by (panel opponent slot, map). The engine is deterministic, so a game only changes if a bot changed;
the per-game gem margin (ours - theirs) is compared with a two-sided sign test.
Verdict ACCEPT needs: total margin gain > 0, sign-test p < 0.1, and NEW deaths <= 1.05 * OLD deaths.
"""
import math, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LINE = re.compile(r'^(\S+)\s+(WIN |loss)\s+(\d+) -\s+(\d+)\s+r\s*(\d+)\s+deaths us\s+(\d+) them\s+(\d+)\s+vs (.*)$', re.M)


def run_ids(bot):
    runs = [l.split() for l in open(os.path.join(ROOT, 'tools', 'gate.log'), encoding='utf-8') if l.split()[:1] == [bot]]
    if not runs:
        sys.exit(f'no gate run for {bot} in tools/gate.log')
    return runs[-1][1:]


def games(bot):
    out = subprocess.run([sys.executable, '-I', os.path.join(ROOT, 'tools', 'group.py'), *run_ids(bot)],
                         capture_output=True, text=True, encoding='utf-8').stdout
    if re.search(r'queued|running', out):
        sys.exit(f'{bot}: run not finished')
    # Key by panel slot (group order) and map: opponents rename teams, so names do not pair reliably.
    res, slot = {}, 0
    for line in out.splitlines():
        if line.startswith('group '):
            slot += 1
            continue
        m = LINE.match(line)
        if m:
            res[(f'{slot // 2}:{m[8].strip()}', m[1])] = dict(win=m[2] == 'WIN ', margin=int(m[3]) - int(m[4]), deaths=int(m[6]))
    return res


def wilson(w, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = w / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def sign_p(pos, neg):
    n, k = pos + neg, min(pos, neg)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


old_bot, new_bot = sys.argv[1], sys.argv[2]
a, b = games(old_bot), games(new_bot)
keys = sorted(set(a) & set(b))
if len(keys) < len(set(a) | set(b)):
    print(f'warning: {len(set(a) ^ set(b))} unpaired games ignored')
pos = neg = 0
gain = 0
for k in keys:
    d = b[k]['margin'] - a[k]['margin']
    gain += d
    pos += d > 0
    neg += d < 0
    if a[k]['win'] != b[k]['win'] or abs(d) >= 300:
        print(f'{k[1]:12} {"WIN " if a[k]["win"] else "loss"} -> {"WIN " if b[k]["win"] else "loss"}'
              f'  margin {a[k]["margin"]:+5} -> {b[k]["margin"]:+5}  deaths {a[k]["deaths"]:2} -> {b[k]["deaths"]:2}  vs {k[0]}')
for name, g in ((old_bot, a), (new_bot, b)):
    w = sum(g[k]['win'] for k in keys)
    lo, hi = wilson(w, len(keys))
    print(f'{name:12} wins {w:2}/{len(keys)} (95% CI {lo:.0%}-{hi:.0%})  margin {sum(g[k]["margin"] for k in keys):+6}'
          f'  deaths {sum(g[k]["deaths"] for k in keys)}')
p = sign_p(pos, neg)
da, db = sum(a[k]['deaths'] for k in keys), sum(b[k]['deaths'] for k in keys)
print(f'paired: margin gain {gain:+d}, better {pos} worse {neg} same {len(keys) - pos - neg}, sign-test p={p:.3f}')
ok = gain > 0 and p < 0.1 and db <= 1.05 * da
print('VERDICT', 'ACCEPT' if ok else ('REJECT' if gain < 0 and p < 0.1 else 'INCONCLUSIVE'))
