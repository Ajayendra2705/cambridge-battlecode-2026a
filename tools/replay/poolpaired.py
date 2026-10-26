"""Pool the paired.py outputs of several panels into one weighted mean and standard error per metric.

usage: python -I tools/replay/poolpaired.py FILE[:N] [FILE[:N] ...]
FILE is a saved paired.py output (e.g. data/paired_mc2b12p.txt); N is its number of paired games, read from the file's
first line when left out or 0. Each panel's mean is weighted by its games; the pooled standard error combines the
panels' standard errors the same way. A variant runs on b11p and b12p (25 games each), judged on the 50 together.
"""
import sys, re, math
acc = {}
for arg in sys.argv[1:]:
    f, n = arg.rsplit(':', 1) if ':' in arg[2:] else (arg, '0'); n = int(n)
    text = open(f, encoding='utf-8').read()
    if n == 0: n = int(re.search(r'^(\d+) paired decoded games', text, re.M).group(1))
    for m in re.finditer(r'^\s+(\S.*?)\s+([+-]\d+\.\d+) \+-\s+(\d+\.\d+)$', text, re.M):
        k, mean, se = m.group(1), float(m.group(2)), float(m.group(3))
        a = acc.setdefault(k, [0.0, 0.0, 0])
        a[0] += mean * n; a[1] += (se * n) ** 2; a[2] += n
for k, (s, v, n) in acc.items():
    print(f'  {k:16} {s / n:+8.1f} +- {math.sqrt(v) / n:6.1f}   (n {n})')
